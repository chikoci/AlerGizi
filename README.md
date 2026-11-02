# AlerGizi

**Asisten Penilai Keamanan Pangan Kemasan, Peringatan Alergen, dan Batas Gula-Garam-Lemak (GGL) untuk Konsumen Harian Berbasis Regulasi Kemenkes dan BPOM RI**

> **Mata Kuliah:** Kapita Selekta: AI Engineering (2 SKS) — Ganjil 2026/2027  
> **Program Studi:** Sistem Informasi  
> **Dosen Pengampu:** Aidil Saputra Kirsan, S.ST., M.Tr.Kom.

---

## Ringkasan Produk

**AlerGizi** adalah produk digital bertenaga AI generatif (*Google Gemini Multimodal*) yang dirancang khusus untuk melindungi konsumen Indonesia saat membeli atau mengonsumsi pangan olahan kemasan. 

Aplikasi ini membaca foto maupun teks komposisi (*ingredients*) kemasan, kemudian:
1. Mendeteksi keberadaan **Alergen Wajib BPOM** yang sering terselubung dalam istilah kimia industri pangan (seperti kasein, whey, maltodekstrin, albumin, lesitin kedelai).
2. Mengevaluasi kadar **Gula, Garam (Natrium), dan Lemak Total** terhadap ambang batas aman harian Kementerian Kesehatan RI (Pola G4-G1-L5: Permenkes No. 30/2013).
3. Mendeteksi **Bahan Tambahan Pangan Pemanis Buatan** (Sukralosa, Aspartam, Asesulfam-K, Sakarin) dan memunculkan peringatan wajib BPOM untuk anak di bawah 5 tahun dan ibu hamil.
4. Menyajikan diagnosis berformat terstruktur (*Structured Output JSON*) disertai sitasi pasal dan ayat regulasi resmi.

---

## Arsitektur "Satu Produk, Lima Lapisan"

| Lapisan | Blok Materi | Kemampuan pada Produk Ini | Status |
|:---:|---|---|:---:|
| **1** | **Fondasi (M1–M3)** | Pemahaman token, estimasi biaya pemanggilan, dan gateway Gemini API | ✅ Selesai |
| **2** | **Kendali (M4–M6)** | Instruksi sistem 6-sumbu (`v1.md`), kontrak skema Pydantic, dan tools deterministik GGL | ✅ Selesai |
| **3** | **Grounding (M7–M9)** | Korpus 8 regulasi resmi BPOM & Kemenkes RI, rancangan chunking berbasis pasal, dan arsitektur sistem UTS | ✅ Selesai |
| **4** | **Agentic (M10–M13)** | Integrasi multi-tool deterministik, penanganan kegagalan, dan orkestrasi langkah majemuk | ⏳ Sedang Berjalan (M11) |
| **5** | **Kematangan (M14–M16)** | Evaluasi kasus uji produk riil, analisis komparatif, dan mitigasi keamanan | ⏳ Tahap Berikutnya |

---

## Teknologi yang Digunakan

* **AI Engine:** Google Gemini 1.5 Flash / Gemini 2.0 Flash (Multimodal Vision & JSON Schema Mode)
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

# Salin dan isi API Key Anda di file .env
cp .env.example .env
# Edit .env dan masukkan GEMINI_API_KEY Anda

# Jalankan server
python main.py
# Backend aktif di: http://localhost:8000 (Dokumentasi Swagger di http://localhost:8000/docs)
```

### 2. Menjalankan Frontend (Svelte + Bun)
```powershell
cd frontend
# Install dependensi (jika belum)
bun install

# Jalankan dev server
bun run dev
# Frontend aktif di: http://localhost:5173
```

---

## Struktur Berkas Repositori

```text
AlerGizi/
├── backend/
│   ├── .venv/               # Virtual environment Python 3.12
│   ├── schemas.py           # Kontrak data terstruktur Pydantic (JSON Schema)
│   ├── tools.py             # Tool kalkulator matematika GGL Kemenkes & kamus alergen
│   ├── gemini_service.py    # Integrasi Google Gemini API & pemrosesan multimodal
│   ├── main.py              # Server FastAPI endpoint REST API
│   └── requirements.txt     # Daftar paket dependensi Python
├── frontend/
│   ├── src/
│   │   ├── App.svelte       # Antarmuka Scanner Dashboard modern (Glassmorphism)
│   │   └── app.css          # Styling kustom & Tailwind CSS v4
│   ├── package.json         # Konfigurasi Bun & Svelte
│   └── vite.config.ts       # Konfigurasi Vite bundler
├── instruksi/
│   ├── v1.md                # Instruksi sistem awal 6 sumbu (Minggu 4)
│   └── CATATAN.md           # Log perubahan versi instruksi & dampak pengujian
├── catatan-pemakaian.md     # Log mingguan pemakaian token dan estimasi biaya (Minggu 3-16)
└── .gitignore               # Mengamankan kunci API (.env) dari repositori Git
```

---

## Pernyataan Etis & Batasan Tanggung Jawab
Sistem ini dirancang sebagai instrumen penyaring awal (*first-line screening assistant*) untuk membantu konsumen awam memahami label kemasan makanan. Sistem **tidak dimaksudkan** sebagai alat diagnosis medis klinis, penentu resep diet penyakit berat, atau penjamin mutlak bagi penderita alergi anafilaksis fatal. Keputusan konsumsi akhir tetap berada di tangan konsumen dewasa yang bijak.
