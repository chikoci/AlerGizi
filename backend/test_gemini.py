"""
Uji konektivitas gateway Google Gemini API
"""

import os
import sys
import logging
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
logging.getLogger('google_genai.models').setLevel(logging.ERROR)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "MASUKKAN_GEMINI_API_KEY_ANDA_DISINI":
    print("[ERROR] GEMINI_API_KEY belum disetel di .env")
    sys.exit(1)

try:
    from google import genai

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"
    
    print(f"[INFO] Menguji pemanggilan model ({model_name})...")
    response = client.models.generate_content(
        model=model_name,
        contents="Jelaskan dalam 1 kalimat batas konsumsi gula harian menurut Permenkes RI."
    )

    print("\n[OK] Koneksi berhasil:")
    print(response.text.strip())

except Exception as e:
    print(f"\n[ERROR] Gagal memanggil API: {e}")
    sys.exit(1)
