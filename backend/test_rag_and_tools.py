"""
Uji Validasi Otomatis AlerGizi:
1. Verifikasi 3 Tools Resmi (Kode Peserta K=7 -> 2 + (7 mod 2) = 3 tools)
2. Verifikasi RAG Engine (36 Chunks dari 8 Dokumen Regulasi Pangan)
3. Verifikasi Fallback Handling untuk Bahan Non-Regulasi
4. Verifikasi Integrasi Output Schemas (ScanResponse + referensi_regulasi)
"""

import sys
from pathlib import Path

# Set output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools import (
    hitung_persentase_ggl,
    deteksi_pemanis_buatan,
    cari_regulasi_bpom,
    DAFTAR_TOOLS_ALERGIZI,
    rag_engine
)
from schemas import ScanResponse
from gemini_service import _post_process_audit


def test_tool_count():
    print("[TEST 1] Memeriksa Jumlah Tools Terdaftar...")
    total_tools = len(DAFTAR_TOOLS_ALERGIZI)
    assert total_tools == 3, f"Jumlah tool harus tepat 3, ditemukan: {total_tools}"
    names = [t["nama"] for t in DAFTAR_TOOLS_ALERGIZI]
    print(f"  ✓ Terdaftar {total_tools} tools resmi:")
    for t in DAFTAR_TOOLS_ALERGIZI:
        print(f"    - {t['nama']} ({t['tipe']})")
    assert "hitung_persentase_ggl" in names
    assert "deteksi_pemanis_buatan" in names
    assert "cari_regulasi_bpom" in names
    print("  ✓ PASS\n")


def test_tool_1_ggl():
    print("[TEST 2] Menguji Tool 1: hitung_persentase_ggl...")
    res = hitung_persentase_ggl(gula=25.0, natrium=800.0, lemak=20.0)
    assert res["gula"]["persen"] == 50.0
    assert res["gula"]["status"] == "BERLEBIH"
    assert res["natrium"]["persen"] == 40.0
    assert res["natrium"]["status"] == "WASPADA"
    print(f"  ✓ Gula: {res['gula']['persen']}% ({res['gula']['status']})")
    print(f"  ✓ Natrium: {res['natrium']['persen']}% ({res['natrium']['status']})")
    print("  ✓ PASS\n")


def test_tool_2_pemanis():
    print("[TEST 3] Menguji Tool 2: deteksi_pemanis_buatan...")
    teks = "Komposisi: Air, gula, pemanis buatan sukralosa dan asesulfam-K."
    res = deteksi_pemanis_buatan(teks)
    assert res["terdeteksi"] is True
    assert "Sukralosa" in res["jenis_pemanis"]
    assert "Asesulfam" in res["jenis_pemanis"]
    assert "laksatif" in res["peringatan_wajib"]
    print(f"  ✓ Terdeteksi pemanis: {res['jenis_pemanis']}")
    print("  ✓ PASS\n")


def test_tool_3_rag_retrieval():
    print("[TEST 4] Menguji Tool 3: cari_regulasi_bpom (RAG Engine)...")
    print(f"  ✓ Total Chunks Pasals terindeks: {len(rag_engine.chunks)}")
    assert len(rag_engine.chunks) > 20

    # Uji query Alergen (Susu / Terigu)
    res_susu = cari_regulasi_bpom("susu laktosa")
    assert res_susu["status"] == "SUKSES"
    assert "BPOM No. 31/2018" in res_susu["kutipan_utama"]
    print(f"  ✓ Query 'susu laktosa' -> {res_susu['kutipan_utama']}")

    # Uji query Batas GGL
    res_ggl = cari_regulasi_bpom("gula garam lemak 50g")
    assert res_ggl["status"] == "SUKSES"
    assert "Permenkes" in res_ggl["kutipan_utama"]
    print(f"  ✓ Query 'gula garam lemak 50g' -> {res_ggl['kutipan_utama']}")

    # Uji query Pemanis
    res_pemanis = cari_regulasi_bpom("aspartam fenilketonuria")
    assert res_pemanis["status"] == "SUKSES"
    assert "BPOM No. 11/2019" in res_pemanis["kutipan_utama"]
    print(f"  ✓ Query 'aspartam fenilketonuria' -> {res_pemanis['kutipan_utama']}")

    # Uji query UMKM
    res_umkm = cari_regulasi_bpom("gizi pangan umkm mikro kecil")
    assert res_umkm["status"] == "SUKSES"
    assert "BPOM No. 16/2020" in res_umkm["kutipan_utama"]
    print(f"  ✓ Query 'gizi UMKM' -> {res_umkm['kutipan_utama']}")

    # Uji fallback non-regulasi
    res_fallback = cari_regulasi_bpom("parasetamol tablet obat flu")
    assert res_fallback["status"] == "TIDAK_DITEMUKAN"
    print(f"  ✓ Query obat non-pangan -> Status: {res_fallback['status']} (Fallback Aman)")
    print("  ✓ PASS\n")


def test_end_to_end_post_process():
    print("[TEST 5] Menguji Integrasi End-to-End Output (ScanResponse + RAG)...")
    mock_llm_output = {
        "nama_produk": "Biskuit Gandum Cokelat",
        "status_keamanan_umum": "PERINGATAN",
        "ringkasan_eksekutif": "Produk mengandung alergen gandum dan susu.",
        "takaran_saji_gram": 30.0,
        "gula_gram": 12.0,
        "natrium_mg": 130.0,
        "lemak_total_gram": 6.0,
        "alergen_ditemukan": [
            {"bahan": "Tepung terigu", "kategori_alergen": "Gluten / Gandum", "status_bahaya": "WASPADA"},
            {"bahan": "Susu bubuk skim", "kategori_alergen": "Susu & Olahannya", "status_bahaya": "WASPADA"}
        ],
        "pemanis_buatan_ditemukan": [],
        "rekomendasi_konsumen": "Konsumsi dalam batas wajar."
    }

    resp = _post_process_audit(
        data=mock_llm_output,
        raw_context="Tepung terigu, gula, susu bubuk skim.",
        profil_alergi=["Susu"],
        fokus_diabetes=False,
        fokus_hipertensi=False
    )

    assert isinstance(resp, ScanResponse)
    assert resp.status_keamanan_umum == "BAHAYA"  # Karena profil pengguna alergi susu
    assert len(resp.alergen_terdeteksi) == 2
    
    # Pastikan kutipan pasal ditarik dinamis dari RAG
    for a in resp.alergen_terdeteksi:
        print(f"  ✓ Alergen: {a.bahan} -> Dasar Hukum RAG: {a.kutipan_pasal}")
        assert "BPOM No. 31/2018" in a.kutipan_pasal

    print(f"  ✓ Total Referensi Regulasi RAG yang Disertakan: {resp.referensi_regulasi}")
    assert len(resp.referensi_regulasi) >= 2
    print("  ✓ PASS\n")


if __name__ == "__main__":
    print("================================================================")
    print("MEMULAI SUITE PENGUJIAN FASE 2: RAG ENGINE & 3 TOOLS ALERGIZI")
    print("================================================================\n")
    try:
        test_tool_count()
        test_tool_1_ggl()
        test_tool_2_pemanis()
        test_tool_3_rag_retrieval()
        test_end_to_end_post_process()
        print("================================================================")
        print("SELURUH 5 PENGUJIAN FASE 2 BERHASIL 100% TANPA KESALAHAN!")
        print("================================================================")
    except AssertionError as e:
        print(f"\n[GAGAL] Assertion Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[GAGAL] Error Tak Terduga: {e}")
        sys.exit(1)
