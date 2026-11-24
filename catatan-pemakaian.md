                                          # CATATAN PEMAKAIAN — AlerGizi (Smart Food Label & Allergen Scanner)

**Mata Kuliah:** Kapita Selekta: AI Engineering | 2 SKS — Ganjil 2026/2027  
**Program Studi:** Sistem Informasi — Institut Teknologi Kalimantan (ITK)  
**Mahasiswa:** Chiko Dhiva Pramana | NIM: 10241017 | Kode Peserta K: 7  
**Model Utama:** Google Gemini (Gemini 3.5 Flash Lite / Gemini 2.5 Flash) via Google GenAI SDK  

---

## Log Konsumsi Token & Estimasi Biaya Mingguan

| Tanggal | Minggu | Kegiatan / Tahapan Tugas | Model yang Dipakai | Token Masuk (Prompt) | Token Keluar (Completion) | Perkiraan Biaya (IDR) |
|---|:--:|---|---|---:|---:|---:|
| 2026-09-07 | M1 | Eksplorasi playground Google AI Studio & uji suhu | gemini-2.5-flash | 180 | 120 | Rp 0 (Tier Gratis) |
| 2026-09-14 | M2 | Uji perilaku model & pengamatan halusinasi | gemini-2.5-flash | 350 | 240 | Rp 0 (Tier Gratis) |
| 2026-09-21 | M3 | Pemanggilan model pertama & uji konektivitas gateway API | gemini-2.5-flash | 520 | 385 | Rp 0 (Tier Gratis) |
| 2026-09-28 | M4 | Eksperimen instruksi sistem v1 (6 sumbu) | gemini-2.5-flash | 850 | 420 | Rp 0 (Tier Gratis) |
| 2026-10-05 | M5 | Uji keluaran terstruktur JSON Schema Pydantic (10 kasus) | gemini-2.5-flash | 3.200 | 1.850 | Rp 0 (Tier Gratis) |
| 2026-10-12 | M6 | Integrasi tool deterministik pertama (`hitung_persentase_ggl`) | gemini-2.5-flash | 2.100 | 1.200 | Rp 0 (Tier Gratis) |
| 2026-10-19 | M7 | Uji chunking manual 8 dokumen regulasi BPOM & Kemenkes | gemini-2.5-flash | 1.450 | 680 | Rp 0 (Tier Gratis) |
| 2026-10-26 | M8 | Persiapan presentasi arsitektur sistem UTS | gemini-2.5-flash | 800 | 450 | Rp 0 (Tier Gratis) |
| 2026-11-02 | M9 | Uji retrieval dokumen & perilaku penolakan halusinasi | gemini-2.5-flash | 2.850 | 1.400 | Rp 0 (Tier Gratis) |
| 2026-11-09 | M10 | Analisis komparatif alur Workflow vs Agentic | gemini-2.5-flash | 1.600 | 820 | Rp 0 (Tier Gratis) |
| 2026-11-16 | M11 | Integrasi orkestrasi langkah majemuk & perekaman 3 trace agen | gemini-2.5-flash | 4.100 | 2.150 | Rp 0 (Tier Gratis) |
| 2026-11-23 | M12 | Studi kasus praktisi, peer review, & pengujian antarmuka frontend | gemini-2.5-flash | 3.600 | 1.950 | Rp 0 (Tier Gratis) |

---

## Ringkasan Anggaran Kumulatif (Hingga Minggu 12)

* **Total Token Masuk (Prompt):** 21.600 token
* **Total Token Keluar (Completion):** 11.665 token
* **Total Token Kumulatif:** 33.265 token
* **Total Biaya Riil Kumulatif:** **Rp 0,-** *(Menggunakan kuota gratis Google AI Studio dengan rate limit 15 RPM / 1.500 RPD)*
* **Estimasi Biaya Komersial (Tanpa Tier Gratis):**
  * Tarif Gemini 2.5 Flash: \$0.075 per 1M input tokens, \$0.30 per 1M output tokens (Kurs Rp 16.000 / USD).
  * Biaya Input: $(21.600 / 1.000.000) \times \$0.075 \times 16.000 = \text{Rp } 25,92$
  * Biaya Output: $(11.665 / 1.000.000) \times \$0.30 \times 16.000 = \text{Rp } 55,99$
  * **Total Estimasi Biaya Komersial:** **Rp 81,91** *(Sangat hemat dan layak skala produksi)*

> *Catatan: Log ini diperbarui berkala setiap minggu dan menjadi dasar pengisian data kuantitatif Laporan Evaluasi (Minggu 14).*
