"""
Backend SIPREBAR -- FastAPI.

Cakupan backend ini sengaja terbatas pada dua hal:
  (a) CRUD data historis EBT,
  (b) inferensi LSTM untuk data baru yang diinput pengguna.

Forecast 2026-2028, gap analysis RUED, dan perbandingan ARIMA/Naive TETAP
statis dari src/lib/data.js -- itu hasil riset yang sudah divalidasi dan
dilaporkan di skripsi, jadi tidak boleh berubah hanya karena isi database
berubah.

Menjalankan:  uvicorn main:app --reload --port 8000   (dari dalam folder backend/)
Dokumentasi otomatis: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import config
from database import get_db, init_db
from models import DataHistoris
from routers import data as data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="SIPREBAR API",
    description=(
        "Backend sistem prediksi EBT sektor kelistrikan Provinsi Sulawesi Selatan. "
        "Melayani CRUD data historis dan inferensi model LSTM yang sudah dilatih "
        "(backend TIDAK pernah melatih ulang model)."
    ),
    version="0.1.0",
)

# Dev server Vite berjalan di origin berbeda (5173) dari backend (8000),
# jadi browser butuh izin CORS eksplisit untuk memanggil API ini.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router.router)


@app.get("/api/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    """Cek server, koneksi database, dan ketersediaan artefak model.

    Sengaja tidak pernah melempar 500: kalau ada yang bermasalah, statusnya
    dilaporkan di body supaya bisa dibaca saat testing manual.
    """
    db_status = {"terhubung": False}
    try:
        total = db.scalar(select(func.count()).select_from(DataHistoris))
        per_sumber = dict(
            db.execute(
                select(DataHistoris.sumber, func.count())
                .group_by(DataHistoris.sumber)
            ).all()
        )
        db_status = {
            "terhubung": True,
            "file": str(config.DATABASE_PATH),
            "total_baris": total,
            "per_sumber": per_sumber,
        }
    except Exception as exc:  # noqa: BLE001 -- health check melaporkan, bukan meneruskan
        db_status["error"] = f"{type(exc).__name__}: {exc}"

    artefak = config.cek_artefak()
    artefak_lengkap = all(all(v.values()) for v in artefak.values())

    konfigurasi_model_ada = config.KONFIGURASI_MODEL_PATH.exists()
    window_size = {}
    if konfigurasi_model_ada:
        window_size = {
            plt: cfg["window_size"]
            for plt, cfg in config.load_konfigurasi_model().items()
        }

    siap = db_status["terhubung"] and artefak_lengkap and konfigurasi_model_ada

    return {
        "status": "ok" if siap else "degraded",
        "database": db_status,
        "jenis_plt_valid": config.JENIS_PLT_VALID,
        "konfigurasi_model_ditemukan": konfigurasi_model_ada,
        "window_size": window_size,
        "artefak_model_lengkap": artefak_lengkap,
        "artefak_per_plt": artefak,
    }
