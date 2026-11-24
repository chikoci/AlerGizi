import os
import json
import base64
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

logging.getLogger('google_genai.models').setLevel(logging.ERROR)

from schemas import ScanResponse, AllergenInfo, GGLNutrisi, PemanisBuatanInfo
from tools import hitung_persentase_ggl, deteksi_pemanis_buatan, cari_regulasi_bpom, KAMUS_ALERGEN_BPOM

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = [MODEL_NAME, "gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]

SYSTEM_PROMPT = """
Kamu adalah Asisten Auditor Keamanan Pangan Kemasan, Spesialis Deteksi Alergen, dan Evaluator Gizi Harian (GGL) independen untuk konsumen Indonesia.
Kamu bekerja berlandaskan 8 dokumen regulasi resmi:
1. Peraturan BPOM No. 31/2018 (Label Alergen Pangan Olahan) & No. 20/2021 (Perubahan Label)
2. Permenkes No. 30/2013 & No. 63/2015 (Pencantuman Informasi GGL & Pola G4-G1-L5)
3. Peraturan BPOM No. 26/2021 (Informasi Nilai Gizi pada Label Pangan Olahan)
4. Peraturan BPOM No. 11/2019 (BTP Pemanis Buatan & Peringatan Wajib)
5. Peraturan BPOM No. 16/2020 (Pencantuman Gizi untuk UMKM)
6. Undang-Undang No. 18/2012 tentang Pangan (Pasal 97 tentang Kejujuran Label Pangan)

TUGAS UTAMA:
1. Ekstrak nama produk pangan dari teks atau gambar label kemasan.
2. Identifikasi seluruh bahan yang termasuk ALERGEN WAJIB BPOM (Susu/Laktosa/Kasein/Whey, Gluten/Gandum/Terigu, Kedelai/Lesitin, Kacang Tanah, Kacang Pohon, Telur/Albumin, Ikan, Krustasea, Moluska, Sulfit), SERTA identifikasi bahan apapun yang cocok dengan Alergi Spesifik Pengguna (seperti Daging Ayam/Ekstrak Ayam, Daging Sapi, Wijen, Jagung, dll).
3. Ekstrak data kuantitatif takaran saji (gram/ml), Gula (gram), Natrium/Garam (mg), dan Lemak Total (gram). Jika tidak ada di label kemasan fisik, isi dengan null (dilarang menebak/mengasumsikan 0).
4. Identifikasi Bahan Tambahan Pangan pemanis buatan (Aspartam, Sukralosa, Asesulfam-K, Sakarin, Siklamat, Neotam).
5. Tentukan status keamanan umum:
   - "AMAN": Tidak ada alergen berisiko tinggi bagi profil pengguna, dan kadar gula/garam/lemak berada pada batas wajar.
   - "PERINGATAN": Ditemukan alergen yang cocok dengan profil risiko pengguna, ATAU gula/natrium melebihi 20% batas harian dalam satu sajian, ATAU mengandung pemanis buatan.
   - "BAHAYA": Mengandung alergen fatal bagi profil pengguna, atau gula/natrium melebihi 40% batas harian dalam satu sajian.
   - "DITOLAK": Jika masukan jelas-jelas BUKAN label komposisi atau pangan olahan.

ATURAN KETAT:
- Wajib mengembalikan respon HANYA dalam format JSON valid yang mematuhi skema yang diminta.
- Jangan menambahkan teks pembuka seperti 'Tentu, ini hasilnya' atau tanda kutip markdown ```json.
"""


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY belum disetel di file .env")
    return genai.Client(api_key=GEMINI_API_KEY)


def _generate_json_resilient(client: genai.Client, contents: Any) -> Dict[str, Any]:
    """Eksekusi pemanggilan Gemini dengan model fallback jika versi tertentu dinonaktifkan"""
    last_err = None
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        temperature=0.2,
    )

    for model_candidate in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_candidate,
                contents=contents,
                config=config
            )
            raw_text = response.text.strip()
            # Bersihkan jika ada bungkus markdown ```json
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            # Lanjutkan ke fallback jika model 404 / deprecated / unavailable
            if "404" in err_str or "no longer available" in err_str or "503" in err_str:
                continue
            raise e

    if last_err:
        raise last_err
    raise RuntimeError("Gagal memanggil model Gemini.")


def audit_label_teks(teks_komposisi: str, profil_alergi: List[str] = None, fokus_diabetes: bool = False, fokus_hipertensi: bool = False, fokus_lemak: bool = False) -> ScanResponse:
    """Audit label makanan berbasis teks komposisi"""
    client = _get_client()

    prompt_user = f"""
    Analisis teks label makanan berikut:
    \"\"\"{teks_komposisi}\"\"\"

    Profil Risiko Pengguna:
    - Alergi yang dihindari: {profil_alergi if profil_alergi else 'Tidak ada alergi spesifik'}
    - Fokus Batasi Gula (Diabetes): {'Ya' if fokus_diabetes else 'Tidak'}
    - Fokus Batasi Garam (Hipertensi): {'Ya' if fokus_hipertensi else 'Tidak'}
    - Fokus Batasi Lemak (Kolesterol/Jantung): {'Ya' if fokus_lemak else 'Tidak'}

    Berikan hasil audit dalam skema JSON persis:
    {{
        "nama_produk": "string",
        "status_keamanan_umum": "AMAN" | "PERINGATAN" | "BAHAYA" | "DITOLAK",
        "ringkasan_eksekutif": "string",
        "takaran_saji_gram": float or null,
        "gula_gram": float or null,
        "natrium_mg": float or null,
        "lemak_total_gram": float or null,
        "alergen_ditemukan": [
            {{"bahan": "string", "kategori_alergen": "string", "status_bahaya": "WASPADA" | "BAHAYA", "kutipan_pasal": "Peraturan BPOM No. 31/2018"}}
        ],
        "pemanis_buatan_ditemukan": ["string"],
        "rekomendasi_konsumen": "string"
    }}
    """

    data = _generate_json_resilient(client, prompt_user)
    return _post_process_audit(data, teks_komposisi, profil_alergi, fokus_diabetes, fokus_hipertensi, fokus_lemak)


def audit_label_gambar(image_bytes: bytes, mime_type: str = "image/jpeg", profil_alergi: List[str] = None, fokus_diabetes: bool = False, fokus_hipertensi: bool = False, fokus_lemak: bool = False) -> ScanResponse:
    """Audit label makanan dari citra kemasan"""
    client = _get_client()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    prompt_user = f"""
    Baca foto kemasan makanan ini (ekstrak komposisi bahan dan tabel Informasi Nilai Gizi).
    
    Profil Risiko Pengguna:
    - Alergi yang dihindari: {profil_alergi if profil_alergi else 'Tidak ada alergi spesifik'}
    - Fokus Batasi Gula (Diabetes): {'Ya' if fokus_diabetes else 'Tidak'}
    - Fokus Batasi Garam (Hipertensi): {'Ya' if fokus_hipertensi else 'Tidak'}
    - Fokus Batasi Lemak (Kolesterol/Jantung): {'Ya' if fokus_lemak else 'Tidak'}

    Berikan hasil audit dalam skema JSON persis:
    {{
        "nama_produk": "string",
        "status_keamanan_umum": "AMAN" | "PERINGATAN" | "BAHAYA" | "DITOLAK",
        "ringkasan_eksekutif": "string",
        "takaran_saji_gram": float or null,
        "gula_gram": float or null,
        "natrium_mg": float or null,
        "lemak_total_gram": float or null,
        "alergen_ditemukan": [
            {{"bahan": "string", "kategori_alergen": "string", "status_bahaya": "WASPADA" | "BAHAYA", "kutipan_pasal": "Peraturan BPOM No. 31/2018"}}
        ],
        "pemanis_buatan_ditemukan": ["string"],
        "rekomendasi_konsumen": "string"
    }}
    """

    data = _generate_json_resilient(client, [prompt_user, image_part])
    return _post_process_audit(data, "", profil_alergi, fokus_diabetes, fokus_hipertensi, fokus_lemak)



def _post_process_audit(data: Dict[str, Any], raw_context: str, profil_alergi: List[str], fokus_diabetes: bool, fokus_hipertensi: bool, fokus_lemak: bool = False) -> ScanResponse:
    """Integrasi output LLM dengan tools deterministik"""
    gula = data.get("gula_gram")
    natrium = data.get("natrium_mg")
    lemak = data.get("lemak_total_gram")

    ggl_calc = hitung_persentase_ggl(gula=gula, natrium=natrium, lemak=lemak)

    ggl_model = GGLNutrisi(
        takaran_saji_gram=data.get("takaran_saji_gram"),
        gula_gram=gula,
        natrium_mg=natrium,
        lemak_total_gram=lemak,
        persen_gula_harian=ggl_calc["gula"]["persen"],
        persen_natrium_harian=ggl_calc["natrium"]["persen"],
        persen_lemak_harian=ggl_calc["lemak"]["persen"],
        status_gula=ggl_calc["gula"]["status"],
        status_natrium=ggl_calc["natrium"]["status"],
        status_lemak=ggl_calc["lemak"]["status"],
    )

    pemanis_raw = data.get("pemanis_buatan_ditemukan", [])
    pemanis_dict = deteksi_pemanis_buatan(raw_context)
    semua_pemanis = list(set(pemanis_raw + pemanis_dict["jenis_pemanis"]))
    pemanis_info = PemanisBuatanInfo(
        terdeteksi=len(semua_pemanis) > 0,
        jenis_pemanis=semua_pemanis,
        peringatan_wajib=pemanis_dict["peringatan_wajib"] if len(semua_pemanis) > 0 else None
    )

    alergen_list = []
    referensi_regulasi = []

    for item in data.get("alergen_ditemukan", []):
        bahan = item.get("bahan", "Bahan tidak spesifik")
        kategori = item.get("kategori_alergen", "Alergen Pangan")
        
        # Eksekusi Tool 3 (RAG Retrieval) untuk menarik dasar hukum resmi
        rag_query = f"{bahan} {kategori}"
        rag_res = cari_regulasi_bpom(rag_query)
        if rag_res["status"] == "SUKSES" and rag_res.get("kutipan_utama"):
            kutipan_pasal = rag_res["kutipan_utama"]
            referensi_regulasi.append(kutipan_pasal)
        else:
            kutipan_pasal = item.get("kutipan_pasal") or "Alergi Spesifik Konsumen (Di luar 9 Alergen Wajib BPOM)"
            referensi_regulasi.append("Peraturan BPOM No. 31/2018, Pasal 41")

        alergen_list.append(AllergenInfo(
            bahan=bahan,
            kategori_alergen=kategori,
            status_bahaya=item.get("status_bahaya", "WASPADA"),
            kutipan_pasal=kutipan_pasal
        ))

    # Tambahkan rujukan regulasi pemanis jika terdeteksi
    if pemanis_info.terdeteksi:
        rag_pemanis = cari_regulasi_bpom("pemanis buatan")
        if rag_pemanis["status"] == "SUKSES" and rag_pemanis.get("kutipan_utama"):
            referensi_regulasi.append(rag_pemanis["kutipan_utama"])
        else:
            referensi_regulasi.append("Peraturan BPOM No. 11/2019, Pasal 22")

    # Tambahkan rujukan regulasi batas konsumsi harian GGL
    if ggl_model.gula_gram is not None or ggl_model.natrium_mg is not None or ggl_model.lemak_total_gram is not None:
        referensi_regulasi.append("Permenkes No. 30/2013, Pasal 5 (Pola G4-G1-L5)")

    # Hapus duplikasi rujukan regulasi
    referensi_unik = list(dict.fromkeys(referensi_regulasi))

    status_final = data.get("status_keamanan_umum", "AMAN")
    if profil_alergi:
        for al in alergen_list:
            for pa in profil_alergi:
                if pa.lower() in al.kategori_alergen.lower() or pa.lower() in al.bahan.lower():
                    status_final = "BAHAYA"
                    break

    if fokus_diabetes and ggl_model.status_gula in ["WASPADA", "BERLEBIH"]:
        status_final = "BAHAYA" if ggl_model.status_gula == "BERLEBIH" else "PERINGATAN"

    if fokus_hipertensi and ggl_model.status_natrium in ["WASPADA", "BERLEBIH"]:
        status_final = "BAHAYA" if ggl_model.status_natrium == "BERLEBIH" else "PERINGATAN"

    if fokus_lemak and ggl_model.status_lemak in ["WASPADA", "BERLEBIH"]:
        status_final = "BAHAYA" if ggl_model.status_lemak == "BERLEBIH" else "PERINGATAN"

    return ScanResponse(
        nama_produk=data.get("nama_produk", "Produk Pangan Olahan"),
        status_keamanan_umum=status_final,
        ringkasan_eksekutif=data.get("ringkasan_eksekutif", "Analisis label berhasil diselesaikan."),
        alergen_terdeteksi=alergen_list,
        analisis_ggl=ggl_model,
        pemanis_buatan=pemanis_info,
        referensi_regulasi=referensi_unik,
        rekomendasi_konsumen=data.get("rekomendasi_konsumen", "Periksa porsi saji sebelum mengonsumsi.")
    )
