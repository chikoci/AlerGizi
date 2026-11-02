# RANCANGAN SISTEM — UJIAN TENGAH SEMESTER (UTS)
## AlerGizi: Asisten Cerdas Penilai Alergen & Batas Konsumsi GGL Pangan Kemasan
**Mata Kuliah:** Kapita Selekta: AI Engineering (2 SKS) | Ganjil 2026/2027  
**Program Studi:** Sistem Informasi — Institut Teknologi Kalimantan (ITK)  
**Dosen Pengampu:** Aidil Saputra Kirsan, S.ST., M.Tr.Kom.  

---

| Identitas | Keterangan |
|---|---|
| **Nama Mahasiswa** | Chiko Dhiva Pramana |
| **NIM** | 10241017 |
| **Repositori Proyek** | `AlerGizi` |
| **Tanggal Pengumpulan** | 11 Oktober 2026 |

---

## 1. Persoalan Nyata

### 1.1 Siapa yang Mengalami Persoalan
1. **Individu dengan Alergi & Intoleransi Pangan:** Konsumen yang sensitif terhadap 10 alergen pangan utama (laktosa/kasein susu, gluten gandum, kedelai, kacang tanah, kacang pohon, telur, ikan, krustasea, moluska, sulfit) serta alergen spesifik (seperti ayam). Reaksi berkisar dari ruam kulit, gangguan pencernaan akut, hingga anafilaksis fatal.
2. **Penderita Penyakit Degeneratif:** Penderita/pradiabetes yang wajib membatasi gula, serta penderita hipertensi yang wajib membatasi natrium/garam.
3. **Orang Tua Balita:** Orang tua yang harus melindungi anak <5 tahun dari bahan tambahan pangan pemanis buatan berisiko (aspartam, sukralosa, sakarin).

### 1.2 Bagaimana Persoalan Diselesaikan Sekarang
Saat ini, konsumen mengandalkan tiga pendekatan utama:
1. **Membaca Manual Label Fisik:** Konsumen membaca langsung baris komposisi (*ingredients*) dan tabel Informasi Nilai Gizi (ING) di belakang bungkus kemasan saat berada di lorong belanja minimarket/supermarket.
2. **Aplikasi Pemindai Barcode (Contoh: BPOM Mobile, Open Food Facts, Yuka):** Konsumen memindai kode batang garis (*barcode EAN-13*) untuk mencocokkan nomor identitas produk ke basis data arsip terpusat di server penyedia.
3. **Aplikasi OCR Komposisi Tradisional (Contoh: Google Lens, Text Scanner, aplikasi filter alergen berbasis kata kunci seperti Soosee/IngreCheck):** Konsumen memotret kemasan untuk menyalin teks mentah, lalu sistem mencocokkannya menggunakan algoritma pencocokan kata kunci kaku (*exact keyword/regex matching*) terhadap daftar hitam (*blacklist*) alergen.

### 1.3 Mengapa Cara Sekarang Belum Cukup
1. **Kelemahan Pemeriksaan Manual:**
   * **Cetak Mikro (*Micro-Text*):** Teks dicetak sangat kecil (font 4–6 pt) dengan kontras rendah pada lipatan kemasan fisik yang menyulitkan pembacaan cepat.
   * **Istilah Kimia Terselubung (*Hidden Synonyms*):** Konsumen awam tidak memahami istilah turunan industri seperti *whey protein concentrate* (susu), *kasein* (susu), *maltodekstrin* (turunan gula berindeks glikemik tinggi), atau *lesitin kedelai*.
   * **Ketiadaan Konteks Takaran Gizi:** Angka "Gula 18g" atau "Natrium 420mg" tidak memberi makna tanpa dikonversi ke persentase batas aman harian Kemenkes RI (Pola G4-G1-L5).
2. **Kelemahan Fatal Aplikasi Pemindai Barcode:**
   * **Ketergantungan Basis Data Terpusat (*Cold Start / Not Found*):** Barcode hanya berisi angka identitas, bukan data komposisi. Ribuan produk UMKM lokal, pangan P-IRT, jajanan pasar kemasan, dan produk impor tidak terdaftar di database server sehingga aplikasi langsung macet (*Data Not Found*).
   * **Bahaya Reformulasi Resep Senyap (*Silent Product Reformulation*):** Produsen kerap mengubah formula bahan baku (misal mengganti minyak sawit dengan kedelai) tanpa mengganti nomor barcode. Database barcode menampilkan resep lama yang usang, sementara fisik kemasan di tangan pembeli sudah memuat bahan baru berisiko.
   * **Standar Asing:** Aplikasi global menggunakan standar asing (Nutri-Score Eropa/FDA AS) dan tidak pernah mengutip dasar hukum lokal Indonesia.
3. **Kelemahan Fatal Aplikasi OCR / Keyword Matching Biasa:**
   * **Kebutaan Konteks & Tata Bahasa (*Context Blindness*):** Pencocokan kata kunci gagal membedakan tanda kurung dan negasi. Teks *"minyak nabati (bebas kedelai)"* disalahartikan berbahaya karena sama-sama mengandung kata "kedelai". Aplikasi biasa juga tidak membedakan resep utama dari klausul kontaminasi silang pabrik (Pasal 44 BPOM No. 31/2018).
   * **Ketiadaan Integrasi Matematika Takaran Gizi:** OCR biasa hanya membuang teks mentah tanpa kemampuan memparsing takaran saji dan menghitung persentase ambang batas harian secara deterministik.

---

## 2. Mengapa AI Generatif (Dan Mengapa Bukan Basis Data, Formulir, atau Aturan Biasa)

Sesuai ketentuan spesifikasi perancangan, bagian ini menguraikan secara komparatif mengapa arsitektur AlerGizi tidak dapat diselesaikan dengan pendekatan komputasi konvensional:

### 2.1 Mengapa BUKAN Basis Data (Database Lookup)
1. **Masalah *Cold-Start* & Cakupan Produk Lokal:** Basis data relasional hanya dapat melakukan pencocokan data yang sudah di-input sebelumnya (*dumb lookup*). Di Indonesia, ratusan ribu produk pangan UMKM, produk industri rumah tangga (P-IRT), dan makanan impor belum terdaftar di basis data terpusat seperti BPOM Mobile atau Open Food Facts. Sistem berbasis database langsung gagal (*Data Not Found*).
2. **Bahaya Reformulasi Resep Senyap (*Silent Reformulation*):** Pabrik produsen pangan kerap mengubah formula komposisi (misalnya beralih dari minyak sawit ke minyak kedelai) tanpa mengganti kode barcode EAN-13. Pengguna yang mengandalkan database akan disajikan data resep lama yang usang dan berbahaya bagi penderita alergi, padahal label fisik kemasan di tangan pembeli sudah memuat bahan baru.
3. **Kekakuan Taksonomi Kimia Pangan:** Basis data kaku tidak mampu memetakan ribuan sinonim dan turunan industri kimia pangan yang terus berevolusi tanpa pemeliharaan manual (*manual maintenance*) yang mahal dan lambat.

### 2.2 Mengapa BUKAN Formulir (Manual Input Form)
1. **Beban Kognitif Pengguna di Lapangan (*Usability & Friction*):** Skenario penggunaan nyata terjadi di lorong belanja minimarket atau supermarket saat pengguna berdiri terburu-buru. Tidak realistis dan tidak layak (*unfeasible*) mengharapkan konsumen mengetik secara manual 20+ bahan kimia komposisi dan belasan baris angka gizi ke dalam formulir isian aplikasi.
2. **Risiko Galat Manusia (*Human Error*):** Pengetikan manual nama-nama latin/kimia pangan yang kompleks berisiko tinggi salah ketik (*typo*), yang berakibat fatal meloloskan alergen berbahaya ke dalam konsumsi.

### 2.3 Mengapa BUKAN Aturan Biasa (If-Else / Regex / Exact Keyword Matching)
1. **Kebutaan Konteks & Tata Bahasa (*Context Blindness*):** Aturan pencocokan kata kunci kaku tidak memahami hierarki tata bahasa dan cakupan tanda kurung negasi. Sebagai contoh, frasa *"minyak nabati (bebas kedelai)"* atau *"tidak menggunakan pengawet sulfit"* akan tetap memicu alarm bahaya palsu (*false positive*) pada sistem regex karena kata "kedelai" dan "sulfit" terdeteksi.
2. **Ketidakmampuan Membedakan Klausul Regulasi (Pasal 44 BPOM No. 31/2018):** Aturan if-else tidak dapat memisahkan antara komposisi bahan utama resep dengan klausul peringatan fasilitas produksi (*"Diproduksi menggunakan peralatan yang juga memproses gandum"*).

### 2.4 Mengapa AI Generatif (LLM Multimodal) Tepat
1. **Ekstraksi Citra Multimodal:** Model visi multimodal membaca langsung citra kemasan fisik yang melengkung, mengkilap, terlipat, atau bising langsung dari kamera ponsel seketika di tempat belanja.
2. **Penalaran Semantik Bahasa Alami (*Semantic Reasoning*):** Model memahami cakupan tanda kurung, klaim non-alergen, sinonim bahan kimia industri, dan secara fleksibel mencocokkannya ke profil risiko khusus pengguna (seperti alergi daging ayam).

### 2.5 Batasan Sistem: Bagian yang TIDAK Menggunakan AI
Penghitungan persentase matematis gizi (gula, natrium, lemak) terhadap batas harian Kemenkes RI (rumus G4-G1-L5) **sama sekali tidak diserahkan ke AI**. Operasi aritmatika didelegasikan 100% ke **Tool Deterministik Python** guna menjamin akurasi mutlak dan mengeliminasi risiko halusinasi numerik.


---

## 3. Arsitektur Rancangan Sistem

### 3.1 Diagram Alur Sistem (End-to-End)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PENGGUNA (FRONTEND SVELTE)                      │
│   [Foto Label Kemasan / Input Teks] + [Profil Risiko: Alergi, GGL]    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP POST (Multipart/JSON)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        BACKEND ENGINE (FASTAPI)                        │
│                                                                        │
│  1. PANGGILAN MODEL GATEWAY (Gemini 2.5 Flash / Flash Lite)            │
│     • Suhu Rendah (0.2) + Instruksi Sistem 6-Sumbu                     │
│     • Strict JSON Schema Mode                                          │
│     • Ekstraksi: Bahan Baku, Angka Nutrisi (g/mg), Pemanis Buatan      │
│                                                                        │
│  2. EKSEKUSI TOOL DETERMINISTIK (Python Pure Functions)                │
│     • hitung_persentase_ggl(gula, natrium, lemak)                      │
│       ➔ Rumus: (nilai / batas_kemenkes) * 100%                         │
│     • deteksi_pemanis_buatan(teks) ➔ Kamus BPOM No. 11/2019            │
│                                                                        │
│  3. GROUNDING REGULASI (BPOM No. 31/2018 & Permenkes No. 30/2013)      │
│     • Penegakan Sitasi Pasal 41-43 (10 Alergen Wajib)                  │
│     • Penegakan Label Status Tertutup: AMAN | PERINGATAN | BAHAYA      │
│                                                                        │
│  4. VALIDASI KONTRAK DATA (Pydantic v2 Schema Validation)              │
│     • Valid ➔ ScanResponse JSON                                        │
│     • Tidak Valid ➔ Fallback Terkendali (TIDAK_DAPAT_DITENTUKAN)       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ JSON Structured Contract
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      HASIL AUDIT DI DASHBOARD SVELTE                   │
│   • Badge Status Keamanan ([AMAN] / [PERINGATAN] / [BAHAYA])           │
│   • Kartu Alergen Terdeteksi + Sitasi Pasal BPOM                       │
│   • Bar Progres Persentase Gula, Natrium, Lemak Kemenkes (G4-G1-L5)    │
│   • Peringatan Pemanis Buatan untuk Anak & Ibu Hamil                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Kendali Output (Structured Output & Contract)

### 4.1 Skema Kontrak Pydantic (`schemas.py`)
Model memaksa keluaran model bahasa masuk ke dalam skema tertutup:
* `ScanResponse`:
  * `nama_produk: str`
  * `status_keamanan_umum: Enum["AMAN", "PERINGATAN", "BAHAYA", "DITOLAK"]`
  * `ringkasan_eksekutif: str` (1–2 kalimat fakta audit)
  * `alergen_terdeteksi: List[AllergenInfo]` (bahan, kategori resmi BPOM, status, kutipan pasal)
  * `analisis_ggl: GGLNutrisi` (gram/mg, persentase terhadap batas harian, status GGL)
  * `pemanis_buatan: PemanisBuatanInfo` (status deteksi, jenis bahan, kalimat peringatan wajib BPOM)
  * `rekomendasi_konsumen: str`
  * `disclaimer_etis: str` (Batas tanggung jawab hukum)

### 4.2 Nilai Valid dan Nilai untuk Kasus "Tidak Dapat Ditentukan"
* Status Keamanan Umum: `AMAN`, `PERINGATAN`, `BAHAYA`, `DITOLAK`.
* Status Gizi (Gula/Natrium/Lemak): `AMAN`, `WASPADA`, `BERLEBIH`, `TIDAK_DAPAT_DITENTUKAN`.
* **Penanganan Kasus Tak Tertentukan:** Jika takaran saji atau angka gram gizi terpotong/buram pada kemasan, sistem **dilarang mengasumsikan angka 0**. Sistem mengisi nilai `null` dan menandai status `TIDAK_DAPAT_DITENTUKAN`.

### 4.3 Mengapa Field Bukti Berupa Kutipan Langsung
Field `bahan` dan `kutipan_pasal` wajib berupa kutipan teks langsung dari kemasan dan teks undang-undang (bukan ringkasan buatan model). Hal ini memungkinkan verifikasi instan (*auditability*) oleh mata manusia dan mengeliminasi halusinasi tafsir.

### 4.4 Penanganan Output Tak Valid
Jika keluaran LLM rusak atau melanggar skema, Pydantic `ValidationError` menangkapnya, menolak respons tersebut, dan secara aman mengembalikan pesan galat terstruktur ke UI tanpa membuat backend *crash*.

---

## 5. Tool Deterministik dan Batas Kewenangan

### 5.1 Daftar Tool
1. **`hitung_persentase_ggl(gula, natrium, lemak)`:**
   * Menghitung rasio terhadap ambang anjuran Kemenkes RI per orang per hari:
     * Gula: $\text{Batas} = 50.0\text{ g}$ (4 sdm)
     * Natrium: $\text{Batas} = 2000.0\text{ mg}$ (1 sdt garam)
     * Lemak: $\text{Batas} = 67.0\text{ g}$ (5 sdm minyak)
   * Logika Status: `AMAN` ($<20\%$), `WASPADA` ($20\% - 40\%$), `BERLEBIH` ($>40\%$).
2. **`deteksi_pemanis_buatan(teks)`:**
   * Memvalidasi keberadaan BTP pemanis buatan (Sukralosa, Aspartam, Sakarin, Asesulfam-K, Neotam, Siklamat) berdasarkan Peraturan BPOM No. 11/2019 dan membubuhkan kalimat peringatan wajib bagi anak di bawah 5 tahun dan ibu hamil.

### 5.2 Batas Akses dan Sifat Tool
* **Pure Functional & Read-Only:** Seluruh tool bersifat deterministik matematika lokal murni. Tool tidak memiliki akses jaringan luar, tidak menulis ke basis data, dan tidak dapat mengubah *state* sistem.
* **Kapan Tool TIDAK Boleh Dipakai:** Jika parameter masukan bernilai negatif atau bernilai `None` (data kemasan hilang), tool tidak boleh mengarang angka pengganti.

### 5.3 Titik Persetujuan Manusia (*Human-in-the-Loop*)
Peringatan alergen berkategori `BAHAYA` (reaksi anafilaksis fatal) secara etis mewajibkan konfirmasi manual oleh konsumen pada label fisik kemasan sebelum makanan dikonsumsi. Sistem bertindak sebagai *screening assistant*, bukan pengganti pertimbangan medis.

---

## 6. Grounding (RAG) & Dokumen Rujukan

### 6.1 Korpus Dokumen Rujukan Resmi (8 Dokumen Sah Indonesia)
1. **Permenkes No. 30 Tahun 2013:** Pencantuman Informasi Kandungan GGL serta Pesan Kesehatan (24 hlm).
2. **Peraturan BPOM No. 31 Tahun 2018:** Label Pangan Olahan — Pasal 41–44 tentang Alergen (72 hlm).
3. **Peraturan BPOM No. 26 Tahun 2021:** Informasi Nilai Gizi pada Label Pangan Olahan (48 hlm).
4. **Peraturan BPOM No. 11 Tahun 2019:** Bahan Tambahan Pangan Pemanis Buatan (58 hlm).
5. **Permenkes No. 28 Tahun 2019:** Angka Kecukupan Gizi (AKG) Masyarakat Indonesia (34 hlm).
6. **Pedoman Gizi Seimbang (PGS) Kemenkes RI 2014:** Anjuran Porsi Aman Konsumsi Sehat (96 hlm).
7. **Pedoman Pelabelan Pangan Berisiko Alergi BPOM 2020:** Panduan Teknis Identifikasi Alergen (36 hlm).
8. **Peraturan BPOM No. 1 Tahun 2022:** Pengawasan Klaim pada Label dan Iklan Pangan Olahan (64 hlm).

### 6.2 Strategi Chunking Dokumen
* **Aturan Pemotongan:** *Semantic section / pasal-based chunking* (memotong menurut batas Bab, Pasal, dan Ayat hukum).
* **Alasan:** Peraturan perundang-undangan memiliki struktur hierarki hukum yang ketat. Pemotongan sembarangan berdasarkan jumlah huruf (misal per 500 huruf) akan memenggal ayat di tengah kalimat dan merusak konteks subjek hukumnya.
* **Metadata Wajib Chunk:** Nama Peraturan, Nomor Pasal, Ayat, Topik Bahan, dan Tahun Pengesahan.

### 6.3 Perilaku Jika Informasi Tidak Ditemukan
Jika bahan tidak tercantum dalam daftar 10 alergen BPOM atau korpus rujukan, sistem **wajib menolak membuat klaim hukum** dan menyatakan: *"Bahan tidak tercantum dalam daftar regulasi rujukan resmi"*. Sistem dilarang diam-diam beralih ke pengetahuan umum tanpa memberitahu pengguna. Ini adalah **keputusan etis**, bukan sekadar teknis.

---

## 7. Bukti Sejauh Ini (Keberhasilan & Kegagalan Nyata)

### 7.1 Keberhasilan yang Terbukti
Pada pengujian masukan kemasan biskuit cokelat dengan komposisi:
> *"Tepung terigu, gula, krimer nabati (mengandung kasein 2%), lesitin kedelai, perisa artifisial, garam (natrium 180mg), gula 14g per sajian 30g."*

Sistem sukses 100%:
1. Mengurai tanda kurung bersarang dan mendeteksi 3 alergen wajib: Gluten (gandum/terigu), Susu (kasein dalam krimer), dan Kedelai (lesitin).
2. Mengeksekusi tool numerik secara presisi: Gula 14g = $28\%$ batas Kemenkes (`WASPADA`), Natrium 180mg = $9\%$ (`AMAN`).
3. Menghasilkan JSON valid yang langsung ter-render rapi di dashboard antarmuka.

### 7.2 Kegagalan yang Ditemukan Sendiri (Analisis Akar Masalah)
* **Gejala:** Pada pengujian produk minuman sari buah dengan klaim *"Gula: 0g"*, sistem versi v1 memberikan status `AMAN` bagi penderita diabetes. Namun pada baris komposisi sebenarnya tertera *"Maltodekstrin"* dan *"Sukralosa"*.
* **Akar Masalah:** Instruksi awal v1 hanya berpatokan sempit pada angka numerik di tabel gizi tanpa mengevaluasi indeks glikemik bahan pengisi (*maltodekstrin*) dan ketiadaan deteksi BTP pemanis buatan.
* **Tindakan Perbaikan:** 
  1. Memperbarui instruksi ke versi v2 (mewajibkan audit silang antara angka gizi dan daftar komposisi kimia).
  2. Menambahkan modul tool deterministik khusus `deteksi_pemanis_buatan()`.

---

## 8. Analisis Risiko & Rencana Kerja (Minggu 9–16)

### 8.1 Risiko Utama dan Mitigasi
1. **Risiko Kualitas Citra Buruk (Foto Blur / Melengkung):**
   * *Mitigasi:* Menambahkan *pre-validation* pada modul visi: jika teks pada gambar tidak terbaca $\ge 50\%$, sistem mengembalikan status `DITOLAK` dengan instruksi agar pengguna memotret ulang dengan pencahayaan cukup.
2. **Risiko Halusinasi pada Istilah Kimia Baru:**
   * *Mitigasi:* Pembatasan skema ketat dan kewajiban mengutip teks bahan asli tanpa interpretasi bebas.
3. **Risiko Prompt Injection (Teks Label Berisi Perintah Merusak):**
   * *Mitigasi:* Pemisahan tegas antara blok instruksi sistem (*System Role*) dan blok teks masukan (*User Context*).

### 8.2 Rencana Pengembangan Kumulatif (Blok C, D, E)
* **Minggu 9 (Grounding RAG Penuh):** Mengintegrasikan korpus 8 dokumen hukum ke dalam vector database (ChromaDB / FAISS) dengan pencarian embedding berbasis pasal.
* **Minggu 10–13 (Agentic Workflow & Guardrails):** Membangun alur multi-langkah otonom (Penyaringan Masukan $\rightarrow$ Audit Alergen $\rightarrow$ Evaluasi GGL $\rightarrow$ Rekomendasi Porsi) yang dilengkapi pagar pembatas (*Guardrails*) dan verifikasi manusia.
* **Minggu 14–16 (Kematangan & Pertanggungjawaban UAS):** Menguji sistem pada 13+ produk pangan kemasan riil, mengukur evaluasi biaya token, menyusun laporan evaluasi resmi, dan audit etika profesi.
