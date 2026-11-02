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
from tools import hitung_persentase_ggl, deteksi_pemanis_buatan, KAMUS_ALERGEN_BPOM

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """
Kamu adalah Asisten Auditor Keamanan Pangan Kemasan dan Spesialis Deteksi Alergen independen untuk konsumen Indonesia, berlandaskan Permenkes No. 30/2013 dan Peraturan BPOM No. 31/2018.

TUGAS UTAMA:
1. Ekstrak nama produk pangan dari teks atau gambar label kemasan.
2. Identifikasi seluruh bahan yang termasuk ALERGEN WAJIB BPOM (Susu/Laktosa/Kasein, Gluten/Gandum/Terigu, Kedelai/Lesitin, Kacang, Telur/Albumin, Ikan/Krustasea, dll), SERTA identifikasi bahan apapun yang cocok dengan Alergi Spesifik Pengguna (seperti Daging Ayam/Ekstrak Ayam, Daging Sapi, Wijen, Jagung, dll).
3. Ekstrak data kuantitatif takaran saji (gram/ml), Gula (gram), Natrium/Garam (mg), dan Lemak Total (gram). Jika tidak ada di label, isi dengan null.
4. Identifikasi Bahan Tambahan Pangan pemanis buatan (Aspartam, Sukralosa, Asesulfam-K, Sakarin, dll).
5. Tentukan status keamanan umum:
   - "AMAN": Tidak ada alergen berisiko tinggi bagi profil pengguna, dan kadar gula/garam/lemak berada pada batas wajar.
   - "PERINGATAN": Ditemukan alergen yang cocok dengan profil risiko pengguna, ATAU gula/natrium melebihi 20% batas harian dalam satu sajian.
   - "BAHAYA": Mengandung alergen fatal bagi profil pengguna, atau gula/natrium melebihi 40% batas harian.
   - "DITOLAK": Jika masukan jelas-jelas BUKAN label komposisi atau pangan olahan.

ATURAN KETAT:
- Wajib mengembalikan respon HANYA dalam format JSON valid yang mematuhi skema yang diminta.
- Jangan menambahkan teks pembuka seperti 'Tentu, ini hasilnya' atau tanda kutip markdown ```json.
"""


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY belum disetel di file .env")
    return genai.Client(api_key=GEMINI_API_KEY)


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

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_user,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    raw_text = response.text.strip()
    data = json.loads(raw_text)

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

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt_user, image_part],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    raw_text = response.text.strip()
    data = json.loads(raw_text)

    return _post_process_audit(data, raw_text, profil_alergi, fokus_diabetes, fokus_hipertensi, fokus_lemak)



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
    for item in data.get("alergen_ditemukan", []):
        alergen_list.append(AllergenInfo(
            bahan=item.get("bahan", "Bahan tidak spesifik"),
            kategori_alergen=item.get("kategori_alergen", "Alergen Pangan"),
            status_bahaya=item.get("status_bahaya", "WASPADA"),
            kutipan_pasal=item.get("kutipan_pasal", "Peraturan BPOM No. 31/2018 Pasal 41")
        ))

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
        rekomendasi_konsumen=data.get("rekomendasi_konsumen", "Periksa porsi saji sebelum mengonsumsi.")
    )
