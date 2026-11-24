"""
AlerGizi RAG Engine (Retrieval-Augmented Generation)
Modul pencarian dan penarikan pasal hukum pangan resmi Indonesia dari 8 dokumen acuan:
- Permenkes No. 30/2013 (Batas GGL & Pesan Kesehatan)
- Permenkes No. 63/2015 (Perubahan Batas Waktu GGL)
- Peraturan BPOM No. 31/2018 (Label Alergen Pangan Olahan)
- Peraturan BPOM No. 20/2021 (Perubahan Label & Barcode 2D)
- Peraturan BPOM No. 26/2021 (Informasi Nilai Gizi & Format ING)
- Peraturan BPOM No. 11/2019 (BTP Pemanis Buatan & Peringatan Fenilketonuria)
- Peraturan BPOM No. 16/2020 (Pencantuman Gizi untuk UMKM)
- Undang-Undang No. 18/2012 (Ketentuan Label & Kejujuran Pangan)
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RegulasiChunk:
    id_chunk: str
    file_sumber: str
    nomor_regulasi: str
    judul_regulasi: str
    bab: str
    pasal: str
    topik: str
    kata_kunci: List[str] = field(default_factory=list)
    teks_lengkap: str = ""
    kutipan_resmi: str = ""


class RegulasiRAGEngine:
    """Mesin RAG in-memory berbasis chunking pasal dan pencarian semantik berbobot."""

    def __init__(self, dokumen_dir: Optional[Path] = None):
        if dokumen_dir is None:
            # Mengarah ke folder dokumen/teks AlerGizi
            dokumen_dir = Path(__file__).resolve().parent.parent / "dokumen" / "teks"
        self.dokumen_dir = Path(dokumen_dir)
        self.chunks: List[RegulasiChunk] = []
        self._load_and_chunk_all_documents()

    def _extract_regulasi_meta(self, lines: List[str], fname: str) -> Dict[str, str]:
        meta = {"lembaga": "Pemerintah RI", "nomor": "Regulasi RI", "judul": "Peraturan Pangan Olahan"}
        for line in lines[:10]:
            if line.startswith("# "):
                meta["lembaga"] = line.replace("#", "").strip()
            elif line.startswith("## "):
                meta["nomor"] = line.replace("##", "").strip()
            elif line.startswith("### TENTANG"):
                meta["judul"] = line.replace("###", "").strip()

        # Pemetaan nama resmi yang ringkas dan baku
        if "permenkes-30-2013" in fname:
            meta["singkat"] = "Permenkes No. 30/2013"
        elif "permenkes-63-2015" in fname:
            meta["singkat"] = "Permenkes No. 63/2015"
        elif "bpom-31-2018" in fname:
            meta["singkat"] = "Peraturan BPOM No. 31/2018"
        elif "bpom-20-2021" in fname:
            meta["singkat"] = "Peraturan BPOM No. 20/2021"
        elif "bpom-26-2021" in fname:
            meta["singkat"] = "Peraturan BPOM No. 26/2021"
        elif "bpom-11-2019" in fname:
            meta["singkat"] = "Peraturan BPOM No. 11/2019"
        elif "bpom-16-2020" in fname:
            meta["singkat"] = "Peraturan BPOM No. 16/2020"
        elif "uu-18-2012" in fname:
            meta["singkat"] = "UU No. 18/2012"
        else:
            meta["singkat"] = meta["nomor"]

        return meta

    def _load_and_chunk_all_documents(self):
        """Membaca 8 dokumen markdown di folder teks dan membaginya per Bab/Pasal."""
        if not self.dokumen_dir.exists():
            return

        md_files = sorted(list(self.dokumen_dir.glob("*.md")))
        for fpath in md_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.splitlines()
            meta = self._extract_regulasi_meta(lines, fpath.name)

            # Pola pemisah bab dan pasal
            cur_bab = "Ketentuan Umum"
            cur_pasal = "Umum"
            cur_chunk_lines: List[str] = []
            chunk_idx = 1

            for line in lines:
                if line.startswith("### BAB"):
                    if cur_chunk_lines:
                        self._save_chunk(fpath.name, meta, cur_bab, cur_pasal, cur_chunk_lines, chunk_idx)
                        chunk_idx += 1
                        cur_chunk_lines = []
                    cur_bab = line.replace("###", "").strip()
                elif line.startswith("#### "):
                    if cur_chunk_lines:
                        self._save_chunk(fpath.name, meta, cur_bab, cur_pasal, cur_chunk_lines, chunk_idx)
                        chunk_idx += 1
                        cur_chunk_lines = []
                    cur_pasal = line.replace("####", "").strip()
                else:
                    cur_chunk_lines.append(line)

            if cur_chunk_lines:
                self._save_chunk(fpath.name, meta, cur_bab, cur_pasal, cur_chunk_lines, chunk_idx)

    def _save_chunk(self, fname: str, meta: Dict[str, str], bab: str, pasal: str, lines: List[str], idx: int):
        teks = "\n".join(lines).strip()
        if not teks or len(teks) < 20:
            return

        id_clean = re.sub(r"[^A-Za-z0-9]+", "-", f"{fname.replace('.md','')}-{pasal}-{idx}").strip("-").upper()
        
        # Ekstrak kata kunci dan topik otomatis
        topik, kata_kunci = self._analyze_topics_and_keywords(teks, bab, pasal)
        
        # Buat kutipan resmi standar
        kutipan = f"{meta.get('singkat', meta['nomor'])}, {pasal}"

        chunk = RegulasiChunk(
            id_chunk=id_clean,
            file_sumber=fname,
            nomor_regulasi=meta.get("nomor", "Regulasi RI"),
            judul_regulasi=meta.get("judul", "Peraturan Pangan"),
            bab=bab,
            pasal=pasal,
            topik=topik,
            kata_kunci=kata_kunci,
            teks_lengkap=teks,
            kutipan_resmi=kutipan
        )
        self.chunks.append(chunk)

    def _analyze_topics_and_keywords(self, teks: str, bab: str, pasal: str) -> (str, List[str]):
        teks_low = (teks + " " + bab + " " + pasal).lower()
        keywords = set()
        topik = "Regulasi Pangan"

        # Deteksi Topik & Alergen
        if any(w in teks_low for w in ["alergen", "susu", "gluten", "kedelai", "kacang", "telur", "ikan", "krustasea", "udang", "sulfit"]):
            topik = "Alergen Pangan Wajib BPOM"
            for w in ["alergen", "susu", "laktosa", "kasein", "whey", "gluten", "gandum", "terigu", "kedelai", "soya", "lesitin", "kacang", "telur", "ikan", "udang", "kepiting", "krustasea", "sulfit"]:
                if w in teks_low:
                    keywords.add(w)

        # Deteksi Batas GGL & Nutrisi
        if any(w in teks_low for w in ["gula", "garam", "lemak", "natrium", "g4-g1-l5", "50 g", "2000 mg", "67 g", "pesan kesehatan"]):
            topik = "Batas Konsumsi GGL & Pesan Kesehatan"
            for w in ["gula", "garam", "lemak", "natrium", "50g", "2000mg", "67g", "diabetes", "hipertensi", "stroke", "jantung", "pesan kesehatan"]:
                if w in teks_low:
                    keywords.add(w)

        # Deteksi Pemanis Buatan
        if any(w in teks_low for w in ["pemanis", "aspartam", "sukralosa", "asesulfam", "sakarin", "siklamat", "fenilketonuria"]):
            topik = "BTP Pemanis Buatan & Peringatan Wajib"
            for w in ["pemanis", "pemanis buatan", "aspartam", "sukralosa", "asesulfam", "sakarin", "siklamat", "fenilketonuria", "ibu hamil"]:
                if w in teks_low:
                    keywords.add(w)

        # Deteksi UMKM & ING
        if any(w in teks_low for w in ["umkm", "usaha mikro", "usaha kecil"]):
            topik = "Kemudahan Gizi UMKM"
            keywords.update(["umkm", "usaha mikro", "usaha kecil", "format ringkas"])

        if any(w in teks_low for w in ["takaran saji", "serving size", "informasi nilai gizi", "akg"]):
            topik = "Format Informasi Nilai Gizi"
            keywords.update(["takaran saji", "serving size", "ing", "nilai gizi", "akg"])

        if any(w in teks_low for w in ["kontaminasi silang", "dapat mengandung", "diproduksi menggunakan"]):
            keywords.update(["kontaminasi silang", "dapat mengandung"])

        return topik, list(keywords)

    def cari_pasal(self, kata_kunci: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Pencarian berbasis relevansi teks regulasi (RAG Retrieval).
        Mengembalikan dokumen teratas lengkap dengan kutipan pasal dan teks hukum asli.
        """
        if not kata_kunci or not kata_kunci.strip():
            return {
                "status": "KOSONG",
                "query": kata_kunci,
                "total_ditemukan": 0,
                "hasil": [],
                "pesan": "Kata kunci pencarian kosong."
            }

        query = kata_kunci.lower().strip()
        all_tokens = re.findall(r"\w+", query)
        
        # Filter stopwords dan kata institusional umum
        stopwords = {
            "dan", "yang", "di", "ke", "dari", "pada", "untuk", "dengan", "adalah", 
            "tentang", "atas", "badan", "pengawas", "obat", "makanan", "menteri", 
            "kesehatan", "republik", "indonesia", "nomor", "tahun", "peraturan", "uu"
        }
        query_tokens = [t for t in all_tokens if t not in stopwords and len(t) > 2]
        if not query_tokens:
            query_tokens = all_tokens

        scored_results = []

        for chunk in self.chunks:
            score = 0
            chunk_text_low = chunk.teks_lengkap.lower()
            chunk_pasal_low = chunk.pasal.lower()
            chunk_topik_low = chunk.topik.lower()

            # 1. Exact phrase match (+15)
            if query in chunk_text_low and len(query) > 3 and query not in stopwords:
                score += 15

            # 2. Token matches in keywords (+6)
            for token in query_tokens:
                if token in chunk.kata_kunci:
                    score += 8
                if token in chunk_pasal_low:
                    score += 5
                if token in chunk_topik_low:
                    score += 4
                # Frekuensi kemunculan kata di teks (+1 per match, max 5)
                occurrences = chunk_text_low.count(token)
                score += min(occurrences, 5)

            if score >= 3:  # Minimal threshold score
                scored_results.append((score, chunk))

        # Sort descending by score
        scored_results.sort(key=lambda x: x[0], reverse=True)

        if not scored_results:
            return {
                "status": "TIDAK_DITEMUKAN",
                "query": kata_kunci,
                "total_ditemukan": 0,
                "hasil": [],
                "pesan": (
                    f"Bahan atau kata kunci '{kata_kunci}' tidak tercantum secara spesifik dalam 8 regulasi resmi pangan BPOM/Kemenkes. "
                    "Mengacu pada Peraturan BPOM No. 31/2018 Pasal 41 ayat (2), hanya 9 kelompok bahan yang diwajibkan sebagai alergen resmi di Indonesia."
                )
            }

        top_results = []
        for score, chunk in scored_results[:top_k]:
            top_results.append({
                "id_chunk": chunk.id_chunk,
                "nomor_regulasi": chunk.nomor_regulasi,
                "pasal": chunk.pasal,
                "topik": chunk.topik,
                "kutipan_resmi": chunk.kutipan_resmi,
                "ringkasan_isi": chunk.teks_lengkap[:260].replace("\n", " ") + "...",
                "teks_lengkap": chunk.teks_lengkap,
                "skor_relevansi": score
            })

        return {
            "status": "SUKSES",
            "query": kata_kunci,
            "total_ditemukan": len(scored_results),
            "hasil": top_results,
            "kutipan_utama": top_results[0]["kutipan_resmi"] if top_results else None
        }


# Inisialisasi singleton RAG Engine untuk digunakan oleh tools dan gemini_service
rag_engine = RegulasiRAGEngine()


def cari_regulasi_bpom(kata_kunci: str, top_k: int = 3) -> Dict[str, Any]:
    """Tool ke-3 AlerGizi: Mengakses pipeline RAG fisik untuk meneliti pasal resmi BPOM/Kemenkes"""
    return rag_engine.cari_pasal(kata_kunci=kata_kunci, top_k=top_k)
