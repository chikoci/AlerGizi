# AlerGizi

**Asisten Penilai Keamanan Pangan Kemasan, Peringatan Alergen, dan Batas Gula-Garam-Lemak (GGL) untuk Konsumen Harian Berbasis Regulasi Kemenkes dan BPOM RI**

> **Mata Kuliah:** Kapita Selekta: AI Engineering (2 SKS) — Ganjil 2026/2027  
> **Program Studi:** Sistem Informasi — Institut Teknologi Kalimantan (ITK)  
> **Mahasiswa:** Chiko Dhiva Pramana (NIM: 10241017) | **Kode Peserta K:** 7  
> **Dosen Pengampu:** Aidil Saputra Kirsan, S.ST., M.Tr.Kom.  
> **Repositori GitHub:** [chikoci/AlerGizi](https://github.com/chikoci/AlerGizi)

---

## Ringkasan Produk

**AlerGizi** adalah produk digital bertenaga AI generatif (*Google Gemini Multimodal Vision*) yang dirancang khusus untuk melindungi konsumen Indonesia saat membeli atau mengonsumsi pangan olahan kemasan. 

Aplikasi ini membaca foto langsung maupun teks komposisi (*ingredients*) kemasan, kemudian:
1. **Deteksi 10 Alergen Wajib BPOM:** Mengidentifikasi bahan alergen tersembunyi yang terselubung dalam istilah kimia industri pangan (seperti kasein, whey, albumin, lesitin kedelai, gluten).
2. **Kalkulasi Deterministik Batas GGL Kemenkes:** Menghitung akumulasi kadar Gula, Garam (Natrium), dan Lemak Total per sajian terhadap batas aman harian Kemenkes RI (Pola G4-G1-L5: Permenkes No. 30/2013) menggunakan fungsi Python eksak tanpa halusinasi aritmatika AI.
3. **Audit Pemanis Buatan BPOM No. 11/2019:** Mendeteksi bahan pemanis sintetis (Sukralosa, Aspartam, Asesulfam-K, Sakarin) dan memunculkan peringatan wajib untuk anak di bawah 5 tahun serta ibu hamil.
4. **Sitasi Pasal Regulasi Otentik:** Menyajikan diagnosis berformat terstruktur (*Structured Output JSON / Pydantic*) disertai rujukan pasal dan ayat hukum resmi.

---

## Arsitektur "Satu Produk, Lima Lapisan"

| Lapisan | Blok Materi | Kemampuan pada Produk Ini | Status |
|:---:|---|---|:---:|
| **1** | **Fondasi (M1–M3)** | Pemahaman token, estimasi biaya pemanggilan, dan gateway Gemini API via Google GenAI SDK | ✅ Selesai |
| **2** | **Kendali (M4–M6)** | Pustaka instruksi berversi ([`v1.md`](instruksi/v1.md), [`v2.md`](instruksi/v2.md)), kontrak skema Pydantic, dan tools deterministik GGL | ✅ Selesai |
| **3** | **Grounding (M7–M9)** | Korpus 8 regulasi resmi BPOM & Kemenkes RI ([`dokumen/`](dokumen/README.md)), perancangan chunking berbasis pasal, dan arsitektur sistem UTS | ✅ Selesai |
| **4** | **Agentic (M10–M13)** | Integrasi 3 tool deterministik (GGL, Pemanis, RAG Regulasi), penanganan kegagalan, dan orkestrasi langkah majemuk | ⏳ Sedang Berjalan (M11–M12) |
| **5** | **Kematangan (M14–M16)** | Evaluasi 13 kasus uji produk pangan minimarket riil, laporan evaluasi akurasi, dan mitigasi risiko etika | ⏳ Tahap Berikutnya (M14) |

---

## Korpus 8 Dokumen Acuan Resmi (Kode Peserta K = 7)

Sesuai formula penurunan lingkup **Lampiran B RPS** ($5 + (K \bmod 4) = 5 + (7 \bmod 4) = \mathbf{8\text{ dokumen}}$), seluruh penalaran audit sistem AlerGizi di-grounding pada 8 regulasi sah pemerintah Republik Indonesia:

| # | Nomor Regulasi | Judul Dokumen | Instansi Penerbit | Tahun | Berkas Teks & PDF Asli | Portal Pemerintah |
|:---:|---|---|---|:---:|:---:|:---:|
| **1** | Permenkes No. 30/2013 | Informasi Kandungan Gula, Garam, Lemak serta Pesan Kesehatan | Kemenkes RI | 2013 | [`Teks`](dokumen/teks/01-permenkes-30-2013-ggl.md) · [`PDF`](dokumen/pdf/01-permenkes-30-2013-ggl.pdf) | [JDIH BPK](https://peraturan.bpk.go.id/Details/172111/permenkes-no-30-tahun-2013) |
| **2** | Permenkes No. 63/2015 | Perubahan atas Permenkes No. 30/2013 tentang GGL | Kemenkes RI | 2015 | [`Teks`](dokumen/teks/02-permenkes-63-2015-perubahan-ggl.md) · [`PDF`](dokumen/pdf/02-permenkes-63-2015-perubahan-ggl.pdf) | [JDIH BPK](https://peraturan.bpk.go.id/Details/172110/permenkes-no-63-tahun-2015) |
| **3** | Peraturan BPOM No. 31/2018 | Label Pangan Olahan (Pasal 41–44 Alergen Wajib) | BPOM RI | 2018 | [`Teks`](dokumen/teks/03-bpom-31-2018-label-alergen.md) · [`PDF`](dokumen/pdf/03-bpom-31-2018-label-alergen.pdf) | [JDIH BPK](https://peraturan.bpk.go.id/Details/219910/peraturan-bpom-no-31-tahun-2018) |
| **4** | Peraturan BPOM No. 20/2021 | Perubahan Peraturan BPOM No. 31/2018 tentang Label Pangan | BPOM RI | 2021 | [`Teks`](dokumen/teks/04-bpom-20-2021-perubahan-label.md) · [`PDF`](dokumen/pdf/04-bpom-20-2021-perubahan-label.pdf) | [JDIH BPK](https://peraturan.bpk.go.id/Details/175158/peraturan-bpom-no-20-tahun-2021) |
| **5** | Peraturan BPOM No. 26/2021 | Informasi Nilai Gizi pada Label Pangan Olahan | BPOM RI | 2021 | [`Teks`](dokumen/teks/05-bpom-26-2021-informasi-nilai-gizi.md) · [`PDF`](dokumen/pdf/05-bpom-26-2021-informasi-nilai-gizi.pdf) | [Peraturan.go.id](https://peraturan.go.id/id/peraturan-bpom-no-26-tahun-2021) |
| **6** | Peraturan BPOM No. 11/2019 | Bahan Tambahan Pangan Pemanis (BTP Pemanis) | BPOM RI | 2019 | [`Teks`](dokumen/teks/06-bpom-11-2019-pemanis-buatan.md) · [`PDF`](dokumen/pdf/06-bpom-11-2019-pemanis-buatan.pdf) | [Peraturan.go.id](https://peraturan.go.id/id/peraturan-bpom-no-11-tahun-2019) |
| **7** | Peraturan BPOM No. 16/2020 | Informasi Nilai Gizi untuk Pangan Olahan Produksi UMKM | BPOM RI | 2020 | [`Teks`](dokumen/teks/07-bpom-16-2020-gizi-umkm.md) · [`PDF`](dokumen/pdf/07-bpom-16-2020-gizi-umkm.pdf) | [Peraturan.go.id](https://peraturan.go.id/id/peraturan-bpom-no-16-tahun-2020) |
| **8** | UU No. 18 Tahun 2012 | Undang-Undang tentang Pangan (Bab VIII: Label dan Iklan) | Republik Indonesia | 2012 | [`Teks`](dokumen/teks/08-uu-18-2012-pangan-label.md) · [`PDF`](dokumen/pdf/08-uu-18-2012-pangan-label.pdf) | [JDIH BPK](https://peraturan.bpk.go.id/Details/39100/uu-no-18-tahun-2012) |

*Katalog metadata lengkap, pasal-based chunking, dan link portal resmi JDIH tersedia di: [`dokumen/README.md`](dokumen/README.md).*

---

## Berkas Kelengkapan Administratif & Rekayasa AI

* 📑 **Kontrak Tema Resmi (Lampiran B):** [`lembar-tema.md`](lembar-tema.md)
* 📊 **Log Konsumsi Token & Biaya Mingguan (Lampiran F):** [`catatan-pemakaian.md`](catatan-pemakaian.md)
* 📐 **Dokumen Perancangan Arsitektur Sistem (UTS):** [`rancangan-sistem.md`](rancangan-sistem.md)
* 📝 **Pustaka Instruksi Sistem Berversi:** [`instruksi/v1.md`](instruksi/v1.md) · [`instruksi/v2.md`](instruksi/v2.md) · [`instruksi/CATATAN.md`](instruksi/CATATAN.md)
* 📚 **Korpus Dokumen Rujukan & Chunking RAG:** [`dokumen/README.md`](dokumen/README.md)

---

## Teknologi yang Digunakan

* **AI Engine:** Google Gemini (Gemini 3.5 Flash Lite / Gemini 2.5 Flash) via Google GenAI SDK (Multimodal Vision & JSON Schema Mode)
* **Backend:** Python 3.12, FastAPI, Pydantic v2, Uvicorn
* **Frontend:** Svelte 5, Bun, Tailwind CSS v4, Lucide Icons
* **Deployment Target:** Vercel (Frontend & Serverless Functions)

---

## Panduan Menjalankan Proyek Secara Lokal

### 1. Menjalankan Backend (FastAPI)
```powershell
cd backend
# Aktifkan virtual environment
.\.venv\Scripts\Activate.ps1

# Salin dan isi API Key Anda di file .env (jika belum)
# GEMINI_API_KEY=AIzaSy...

# Jalankan server FastAPI
uvicorn main:app --reload --port 8000
# Backend aktif di: http://127.0.0.1:8000 (Dokumentasi Swagger di http://127.0.0.1:8000/docs)
```

### 2. Menjalankan Frontend (Svelte + Bun)
```powershell
cd frontend
# Install dependensi (jika baru pertama kali)
bun install

# Jalankan dev server
bun run dev
# Frontend aktif di: http://localhost:5173
```
