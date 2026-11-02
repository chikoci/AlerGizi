import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import ScanResponse, ScanTextRequest
from gemini_service import audit_label_teks, audit_label_gambar

app = FastAPI(
    title="AlerGizi API",
    description="API audit keamanan pangan, deteksi alergen, dan analisis GGL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AlerGizi",
        "version": "1.0.0",
        "supported_models": ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
    }


@app.post("/api/scan-text", response_model=ScanResponse)
async def scan_text_endpoint(payload: ScanTextRequest):
    try:
        return audit_label_teks(
            teks_komposisi=payload.komposisi_teks,
            profil_alergi=payload.profil_alergi,
            fokus_diabetes=payload.fokus_diabetes,
            fokus_hipertensi=payload.fokus_hipertensi,
            fokus_lemak=payload.fokus_lemak
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses teks: {str(e)}")


@app.post("/api/scan-image", response_model=ScanResponse)
async def scan_image_endpoint(
    file: UploadFile = File(...),
    profil_alergi: Optional[str] = Form(default="[]"),
    fokus_diabetes: bool = Form(default=False),
    fokus_hipertensi: bool = Form(default=False),
    fokus_lemak: bool = Form(default=False)
):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Format file harus berupa gambar.")

        image_bytes = await file.read()
        
        try:
            alergi_list = json.loads(profil_alergi) if profil_alergi else []
        except Exception:
            alergi_list = []

        return audit_label_gambar(
            image_bytes=image_bytes,
            mime_type=file.content_type,
            profil_alergi=alergi_list,
            fokus_diabetes=fokus_diabetes,
            fokus_hipertensi=fokus_hipertensi,
            fokus_lemak=fokus_lemak
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses gambar: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
