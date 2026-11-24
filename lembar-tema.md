# LEMBAR TEMA PROYEK

Nama            : Chiko Dhiva Pramana
NIM             : 10241017
Program studi   : Sistem Informasi
Kode peserta K  : 7

---

## Angka lingkup saya
Dokumen rujukan minimum : 5 + (K mod 4) = 5 + (7 mod 4) = 8 dokumen
Kasus uji minimum       : 12 + (K mod 6) = 12 + (7 mod 6) = 13 kasus
Tool minimum            : 2 + (K mod 2) = 2 + (7 mod 2) = 3 tool
Mode keluaran tambahan  : tidak wajib (K ganjil → satu mode bahasa Indonesia)

---

## 1. Persoalan
**Judul kerja produk :**  
AlerGizi — Asisten Penilai Keamanan Pangan Kemasan, Peringatan Alergen, dan Batas Gula-Garam-Lemak (GGL) Berbasis Regulasi Kemenkes dan BPOM RI

**Siapa yang mengalami persoalan ini (sespesifik mungkin, bukan "masyarakat") :**  
Konsumen pangan olahan kemasan di Indonesia yang memiliki kerentanan alergi makanan (misalnya alergi susu/laktosa, gandum/gluten, kedelai, kacang tanah, telur, ikan, atau krustasea) serta individu dengan pantauan diet khusus (diabetes melitus, hipertensi, atau obesitas) yang kesulitan membaca dan memahami komposisi serta tabel informasi nilai gizi pada kemasan produk yang dibeli di pasar atau minimarket.

**Bagaimana persoalan ini diselesaikan sekarang :**  
Konsumen membaca manual teks komposisi di belakang kemasan dengan tulisan berukuran sangat kecil (4–6 pt) atau menafsirkan sendiri istilah bahan baku secara manual, sering kali tanpa mengetahui padanan nama kimia industri pangan dan tanpa menghitung ambang batas gizi harian.

**Mengapa cara sekarang tidak memadai :**  
1. Huruf komposisi sangat kecil dan sering terletak di lipatan kemasan yang melengkung dan mengkilap.
2. Alergen sering tersamarkan dalam nama kimia turunan (misal: "kasein", "whey", atau "laktosa" untuk susu; "lesitin nabati" untuk kedelai; "albumin" untuk telur; "gluten" dalam tepung terigu).
3. Angka pada tabel Informasi Nilai Gizi disajikan per takaran saji (serving size) yang membingungkan konsumen untuk menghitung akumulasi terhadap batas harian Kemenkes (Gula 50g, Natrium 2000mg, Lemak 67g).

---

## 2. Mengapa AI generatif
**Mengapa persoalan ini TIDAK cukup diselesaikan dengan basis data, formulir, atau seperangkat aturan biasa :**  
Label makanan di dunia nyata bersifat data tidak terstruktur (*unstructured data*) dalam bentuk foto kemasan melengkung, mengkilap, terlipat, atau teks paragraf bahasa alami yang bervariasi susunannya antar produsen. Basis data konvensional dan aturan regex kaku (`if/else`) tidak memiliki kemampuan persepsi visi untuk mengekstrak teks dari foto fisik yang tidak sempurna, serta gagal mengenali sinonim dan variasi istilah bahan baku industri pangan yang dinamis tanpa aturan yang sangat rapuh (*brittle*).

**Apa yang membuat persoalan ini menuntut penafsiran bahasa :**  
Pengenalan semantik bahan turunan (misalnya menghubungkan bahwa *"natrium kaseinat"* adalah turunan alergen susu sapi) dan ekstraksi informasi numerik dari tata letak tabel nilai gizi yang format penyajiannya tidak seragam di berbagai produsen pangan Indonesia.

---

## 3. Ukuran keberhasilan
**Apa yang menjadi bukti bahwa produk ini berhasil :**  
Sistem mampu membaca foto maupun teks kemasan, mendeteksi 100% alergen wajib yang cocok dengan profil pengguna dengan mencantumkan pasal BPOM No. 31/2018 secara akurat, menghitung persentase batas gizi GGL harian Kemenkes secara deterministik tanpa halusinasi aritmatika, dan menolak membuat klaim jika data nutrisi tidak terbaca.

**Siapa yang dapat memeriksa keluarannya benar atau salah :**  
Dosen penguji, ahli gizi, auditor regulasi pangan BPOM, atau pengguna yang membandingkan hasil diagnosis sistem langsung dengan label fisik kemasan dan buku peraturan BPOM/Kemenkes.

**Apa yang terjadi bila keluarannya salah, dan siapa yang menanggungnya :**  
Jika salah mendeteksi alergen (*false negative*), konsumen berisiko mengalami reaksi alergi fatal seperti syok anafilaksis. Jika salah menghitung gula/garam, pasien diabetes/hipertensi berisiko mengonsumsi zat pemicu melebihi batas toleransi medis. Risiko hukum dan moral disadari sepenuhnya oleh pengembang sistem; oleh karena itu sistem dilengkapi mitigasi berupa batasan tanggung jawab hukum (*disclaimer medis*), pelarangan halusinasi (data buram wajib diberi status `TIDAK_DAPAT_DITENTUKAN`), dan persetujuan pengguna (*human-in-the-loop*).

---

## 4. Dokumen rujukan
| # | Judul | Penerbit / asal | Tahun | Halaman | Status kelayakan |
|---|---|---|---|---|---|
| 1 | Permenkes No. 30 Tahun 2013 tentang Pencantuman Informasi Kandungan Gula, Garam, Lemak serta Pesan Kesehatan untuk Pangan Olahan dan Pangan Siap Saji | Kementerian Kesehatan RI | 2013 | 24 | Sah, dokumen publik resmi JDIH |
| 2 | Permenkes No. 63 Tahun 2015 tentang Perubahan atas Permenkes No. 30 Tahun 2013 | Kementerian Kesehatan RI | 2015 | 8 | Sah, dokumen publik resmi JDIH |
| 3 | Peraturan BPOM No. 31 Tahun 2018 tentang Label Pangan Olahan (Pasal 41–44 Alergen) | Badan Pengawas Obat dan Makanan RI | 2018 | 72 | Sah, dokumen publik resmi JDIH |
| 4 | Peraturan BPOM No. 20 Tahun 2021 tentang Perubahan atas Peraturan BPOM No. 31 Tahun 2018 | Badan Pengawas Obat dan Makanan RI | 2021 | 18 | Sah, dokumen publik resmi JDIH |
| 5 | Peraturan BPOM No. 26 Tahun 2021 tentang Informasi Nilai Gizi pada Label Pangan Olahan | Badan Pengawas Obat dan Makanan RI | 2021 | 48 | Sah, dokumen publik resmi JDIH |
| 6 | Peraturan BPOM No. 11 Tahun 2019 tentang Bahan Tambahan Pangan Pemanis | Badan Pengawas Obat dan Makanan RI | 2019 | 36 | Sah, dokumen publik resmi JDIH |
| 7 | Peraturan BPOM No. 16 Tahun 2020 tentang Pencantuman Informasi Nilai Gizi untuk Pangan Olahan yang Diproduksi oleh Usaha Mikro dan Usaha Kecil | Badan Pengawas Obat dan Makanan RI | 2020 | 14 | Sah, dokumen publik resmi JDIH |
| 8 | Undang-Undang No. 18 Tahun 2012 tentang Pangan (Bab VIII Label dan Iklan Pangan, Pasal 97–103) | Republik Indonesia | 2012 | 68 | Sah, Lembaran Negara RI |

Konfirmasi:
- [x] Seluruh dokumen sah saya pakai
- [x] Tidak ada data pribadi orang sungguhan di dalamnya
- [x] Sedikitnya enam pertanyaan uji saya terjawab oleh kumpulan ini

---

## 5. Uji lima kriteria penolakan
1. **AI tidak dipaksakan pada persoalan deterministik :** LOLOS. Penghitungan matematika persentase gizi 100% diserahkan ke fungsi Python deterministik (`tools.py`), AI hanya dipakai untuk pemahaman semantik teks label yang tidak terstruktur.
2. **Keluaran dapat dibuktikan benar atau salah :** LOLOS. Kebenaran hasil deteksi alergen dan angka gizi dapat dibuktikan langsung dengan mencocokkan kemasan produk fisik terhadap teks regulasi BPOM/Permenkes.
3. **Sumber pengetahuan tersedia dan sah :** LOLOS. Menggunakan 8 korpus peraturan perundang-undangan resmi publik dari portal JDIH BPOM dan JDIH Kemenkes RI.
4. **Tidak bergantung pada data pribadi nyata :** LOLOS. Masukan hanya berupa foto atau teks label kemasan produk komersial terbuka yang dijual di pasaran tanpa data rekam medis pasien sungguhan.
5. **Lingkupnya muat dikerjakan seorang diri 12 minggu :** LOLOS. Lingkup dibatasi secara spesifik pada 10 alergen wajib BPOM dan ambang batas harian G4-G1-L5 Kemenkes.

---

## 6. Batas yang saya tetapkan sendiri
* **Produk ini TIDAK dimaksudkan untuk :** Menjadi pengganti diagnosis klinis oleh dokter spesialis alergi, dan tidak melayani pangan olahan racikan non-kemasan tanpa izin edar resmi.
* **Keputusan apa yang TIDAK boleh diserahkan kepada produk ini :** Penentuan batas toleransi darurat pasien anafilaksis dan keputusan pengesahan izin edar produk pangan.

---

## 7. Rencana lapisan
| Blok | Yang akan saya tambahkan | Risiko terbesar |
|---|---|---|
| **B — Kendali (Mgg 4–6)** | Ekstraksi terstruktur Pydantic dan pemanggilan tool deterministik GGL | Halusinasi nilai gizi saat label foto kemasan terpotong |
| **C — Grounding (Mgg 7–9)** | 8 korpus regulasi resmi BPOM/Kemenkes dan perancangan pasal-based chunking | Kegagalan retrieval pasal karena nama bahan pangan di kemasan memakai istilah gaul/daerah |
| **D — Agentic (Mgg 10–13)** | Integrasi 3 tool (GGL, Pemanis, RAG Regulasi) dan pengamanan 5 lapis guardrails | Serangan prompt injection yang diselipkan pada teks deskripsi kemasan makanan |
| **E — Kematangan (Mgg 14–16)** | Uji 13 produk minimarket riil, laporan evaluasi akurasi, dan kajian risiko etika | Penilaian akurasi bias jika produk uji tidak mewakili variasi pasar kemasan Indonesia |

---

Tanda tangan mahasiswa : **Chiko Dhiva Pramana**  
Tanggal : 2026-09-28  
NIM : 10241017  
Catatan dosen : -  
Vonis : **DITERIMA**
