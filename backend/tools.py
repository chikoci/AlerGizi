"""
Tools deterministik kalkulasi nutrisi GGL dan deteksi bahan tambahan pangan
Berdasarkan Permenkes No. 30/2013 dan Peraturan BPOM No. 31/2018
"""

from typing import Dict, Any, Optional

# Batas konsumsi harian Kemenkes RI (Permenkes No. 30/2013)
BATAS_HARIAN_GULA_GRAM = 50.0       # 50g
BATAS_HARIAN_NATRIUM_MG = 2000.0    # 2000mg
BATAS_HARIAN_LEMAK_GRAM = 67.0      # 67g

# Daftar alergen wajib BPOM No. 31/2018 (Pasal 41-43)
KAMUS_ALERGEN_BPOM = {
    "Susu & Olahannya (Laktosa/Kasein/Whey)": [
        "susu", "laktosa", "kasein", "casein", "whey", "keju", "mentega", "butter", 
        "krim", "krimer", "skimm", "skim", "dadih", "yogurt", "buttermilk"
    ],
    "Gluten & Serealia (Gandum/Oat/Barley/Rye)": [
        "gandum", "terigu", "tepung terigu", "gluten", "barley", "rye", "oat", 
        "havermut", "malt", "ekstrak malt", "semolina", "spelt"
    ],
    "Kedelai & Olahannya": [
        "kedelai", "soya", "soy", "lesitin kedelai", "soy lecithin", "protein kedelai", 
        "tahu", "tempe", "kecap", "edamame"
    ],
    "Kacang Tanah (Peanut)": [
        "kacang tanah", "peanut", "kacang tuban", "selai kacang"
    ],
    "Kacang Pohon (Tree Nuts)": [
        "almond", "kenari", "walnut", "mete", "cashew", "kacang mede", 
        "pistachio", "hazelnut", "kacang hazel", "pecan", "macadamia", "kemiri"
    ],
    "Telur & Olahannya": [
        "telur", "egg", "albumin", "albumen", "kuning telur", "putih telur", "ovalbumin", "mayones"
    ],
    "Ikan & Olahannya": [
        "ikan", "fish", "gelatin ikan", "minyak ikan", "surimi", "tuna", "salmon", "teri"
    ],
    "Krustasea (Udang/Kepiting/Lobster)": [
        "udang", "shrimp", "prawn", "kepiting", "crab", "lobster", "ebi", "terasi"
    ],
    "Moluska (Cumi/Kerang/Tiram/Gurita)": [
        "cumi", "cumi-cumi", "kerang", "tiram", "gurita", "octopus", "squid", "oyster", "clam"
    ],
    "Sulfit (Belerang Dioksida)": [
        "sulfit", "sulfite", "belerang dioksida", "sulfur dioksida", "natrium bisulfit", 
        "kalium metabisulfit", "natrium metabisulfit"
    ]
}

# Bahan Tambahan Pangan pemanis buatan (BPOM No. 11/2019)
DAFTAR_PEMANIS_BUATAN = [
    "aspartam", "aspartame", "sukralosa", "sucralose", "asesulfam", "acesulfame", 
    "sakarin", "saccharin", "siklamat", "cyclamate", "neotam", "neotame", "sorbitol", "maltitol"
]


def hitung_persentase_ggl(
    gula: Optional[float] = None, 
    natrium: Optional[float] = None, 
    lemak: Optional[float] = None
) -> Dict[str, Any]:
    """Hitung rasio kandungan gizi per sajian terhadap batas harian Kemenkes"""
    hasil = {}

    if gula is not None and gula >= 0:
        pct = round((gula / BATAS_HARIAN_GULA_GRAM) * 100, 1)
        status = "BERLEBIH" if pct > 40 else ("WASPADA" if pct >= 20 else "AMAN")
        hasil["gula"] = {"gram": gula, "persen": pct, "status": status}
    else:
        hasil["gula"] = {"gram": None, "persen": None, "status": "TIDAK_DAPAT_DITENTUKAN"}

    if natrium is not None and natrium >= 0:
        pct = round((natrium / BATAS_HARIAN_NATRIUM_MG) * 100, 1)
        status = "BERLEBIH" if pct > 40 else ("WASPADA" if pct >= 20 else "AMAN")
        hasil["natrium"] = {"mg": natrium, "persen": pct, "status": status}
    else:
        hasil["natrium"] = {"mg": None, "persen": None, "status": "TIDAK_DAPAT_DITENTUKAN"}

    if lemak is not None and lemak >= 0:
        pct = round((lemak / BATAS_HARIAN_LEMAK_GRAM) * 100, 1)
        status = "BERLEBIH" if pct > 40 else ("WASPADA" if pct >= 20 else "AMAN")
        hasil["lemak"] = {"gram": lemak, "persen": pct, "status": status}
    else:
        hasil["lemak"] = {"gram": None, "persen": None, "status": "TIDAK_DAPAT_DITENTUKAN"}

    return hasil


def deteksi_pemanis_buatan(teks: str) -> Dict[str, Any]:
    """Mendeteksi bahan pemanis buatan berdasarkan kamus BPOM"""
    teks_lower = teks.lower()
    ditemukan = []
    for p in DAFTAR_PEMANIS_BUATAN:
        if p in teks_lower:
            ditemukan.append(p.capitalize())
    
    warning = None
    if ditemukan:
        warning = "Mengandung pemanis buatan (" + ", ".join(ditemukan) + "). Konsumsi berlebih dapat mempunyai efek laksatif dan tidak disarankan untuk anak di bawah 5 tahun serta ibu hamil."

    return {
        "terdeteksi": len(ditemukan) > 0,
        "jenis_pemanis": ditemukan,
        "peringatan_wajib": warning
    }
