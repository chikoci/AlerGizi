from typing import List, Optional
from pydantic import BaseModel, Field


class AllergenInfo(BaseModel):
    bahan: str = Field(description="Nama bahan dalam komposisi yang menjadi sumber alergen")
    kategori_alergen: str = Field(description="Kategori alergen resmi BPOM (misal: Susu, Gluten, Kedelai, Kacang, Telur, Ikan)")
    status_bahaya: str = Field(description="Tingkat risiko alergi: WASPADA atau BAHAYA")
    kutipan_pasal: str = Field(default="Peraturan BPOM No. 31/2018 Pasal 41-43", description="Dasar regulasi rujukan")


class GGLNutrisi(BaseModel):
    takaran_saji_gram: Optional[float] = Field(default=None, description="Takaran saji dalam gram/ml jika tertera")
    gula_gram: Optional[float] = Field(default=None, description="Kandungan gula per sajian (gram)")
    natrium_mg: Optional[float] = Field(default=None, description="Kandungan natrium per sajian (miligram)")
    lemak_total_gram: Optional[float] = Field(default=None, description="Kandungan lemak total per sajian (gram)")
    persen_gula_harian: Optional[float] = Field(default=None, description="Persentase terhadap batas harian Kemenkes (50g)")
    persen_natrium_harian: Optional[float] = Field(default=None, description="Persentase terhadap batas harian Kemenkes (2000mg)")
    persen_lemak_harian: Optional[float] = Field(default=None, description="Persentase terhadap batas harian Kemenkes (67g)")
    status_gula: str = Field(description="Kategori status: AMAN | WASPADA | BERLEBIH | TIDAK_DAPAT_DITENTUKAN")
    status_natrium: str = Field(description="Kategori status: AMAN | WASPADA | BERLEBIH | TIDAK_DAPAT_DITENTUKAN")
    status_lemak: str = Field(description="Kategori status: AMAN | WASPADA | BERLEBIH | TIDAK_DAPAT_DITENTUKAN")


class PemanisBuatanInfo(BaseModel):
    terdeteksi: bool = Field(description="Apakah terdapat bahan pemanis buatan")
    jenis_pemanis: List[str] = Field(default_factory=list, description="Daftar nama pemanis buatan yang ditemukan")
    peringatan_wajib: Optional[str] = Field(default=None, description="Kalimat peringatan wajib BPOM jika menggunakan pemanis buatan")


class ScanResponse(BaseModel):
    nama_produk: str = Field(description="Nama produk makanan atau estimasi kategori produk")
    status_keamanan_umum: str = Field(description="Status akhir: AMAN, PERINGATAN, BAHAYA, atau DITOLAK")
    ringkasan_eksekutif: str = Field(description="Penjelasan ringkas hasil audit dalam 1-2 kalimat bahasa manusia")
    alergen_terdeteksi: List[AllergenInfo] = Field(default_factory=list, description="Daftar seluruh alergen yang teridentifikasi")
    analisis_ggl: GGLNutrisi = Field(description="Analisis batas konsumsi Gula Garam Lemak Kemenkes")
    pemanis_buatan: PemanisBuatanInfo = Field(description="Analisis Bahan Tambahan Pangan pemanis buatan")
    rekomendasi_konsumen: str = Field(description="Anjuran porsi aman atau alternatif tindakan untuk konsumen")
    disclaimer_etis: str = Field(
        default="Sistem ini adalah asisten penilai label pangan awal, bukan pengganti diagnosis medis klinis atau jaminan ketiadaan reaksi anafilaksis berat.",
        description="Pernyataan batas tanggung jawab sistem"
    )


class ScanTextRequest(BaseModel):
    komposisi_teks: str = Field(description="Teks komposisi bahan dan nilai gizi makanan")
    profil_alergi: List[str] = Field(default_factory=list, description="Profil alergi pengguna (opsional, misal: ['Susu', 'Gluten'])")
    fokus_diabetes: bool = Field(default=False, description="Apakah pengguna sedang membatasi gula")
    fokus_hipertensi: bool = Field(default=False, description="Apakah pengguna sedang membatasi garam/natrium")
    fokus_lemak: bool = Field(default=False, description="Apakah pengguna sedang membatasi lemak/kolesterol")
