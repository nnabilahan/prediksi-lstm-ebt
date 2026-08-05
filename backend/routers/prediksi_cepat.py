"""
Endpoint pendukung alur prediksi satu klik: GET /api/prediksi/siap.

Sebelumnya halaman Prediksi menuntut pengguna menyusun sendiri window data
(3 atau 6 baris Produksi/Kapasitas/Cuaca) lalu menebak nilai Cuaca bulan
target. Endpoint ini mengumpulkan seluruh bahan tersebut di sisi server:

  - window histori terakhir sepanjang `window_size` model jenis PLT tsb,
  - bulan target (bulan sesudah baris histori terakhir, atau yang diminta),
  - nilai Cuaca bulan target (NASA POWER kalau sudah lewat, kalau tidak
    normal klimatologis -- lihat cuaca.py).

Endpoint ini TIDAK melakukan inferensi. Hasilnya dikirim balik ke frontend,
ditampilkan supaya bisa diperiksa/disunting, lalu dikirim ke /api/predict
seperti biasa. Pemisahan ini disengaja: pengguna tetap melihat angka apa yang
masuk ke model, bukan menekan tombol yang diam-diam mengarang input.
"""
from datetime import date

import cuaca
import ml
from config import JENIS_PLT_VALID
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import DataHistoris
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/prediksi", tags=["prediksi"])


def _bulan_berikutnya(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


@router.get("/siap")
def siapkan_prediksi(
    jenis_plt: str = Query(..., description="Salah satu jenis PLT yang punya model."),
    bulan_target: date | None = Query(
        None,
        description=(
            "Bulan yang ingin ditebak (YYYY-MM-01). Kalau dikosongkan, dipakai "
            "bulan tepat setelah data historis terakhir."
        ),
    ),
    db: Session = Depends(get_db),
):
    if jenis_plt not in JENIS_PLT_VALID:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Jenis PLT '{jenis_plt}' tidak dikenali. "
                f"Pilihan: {', '.join(JENIS_PLT_VALID)}."
            ),
        )

    if not ml.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model belum termuat di server. Cek /api/health untuk detailnya.",
        )

    window_size = ml.get_window_size(jenis_plt)

    # Ambil menurun lalu dibalik: cara ini mengambil tepat `window_size` baris
    # TERAKHIR lewat satu query, tanpa menarik seluruh histori ke memori.
    baris = db.execute(
        select(DataHistoris)
        .where(DataHistoris.jenis_plt == jenis_plt)
        .order_by(DataHistoris.tanggal.desc())
        .limit(window_size)
    ).scalars().all()
    baris = list(reversed(baris))

    if len(baris) < window_size:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Model {jenis_plt} butuh {window_size} bulan berurutan, tapi di "
                f"database baru ada {len(baris)} baris untuk jenis PLT ini. "
                "Tambahkan data lewat halaman Data EBT lebih dulu."
            ),
        )

    target = (bulan_target or _bulan_berikutnya(baris[-1].tanggal)).replace(day=1)

    if target <= baris[-1].tanggal:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Bulan target ({target:%Y-%m}) tidak boleh sama atau lebih awal "
                f"dari data historis terakhir ({baris[-1].tanggal:%Y-%m}). "
                "Model menebak ke depan, bukan mengisi masa lalu."
            ),
        )

    try:
        info_cuaca = cuaca.ambil_cuaca(db, jenis_plt, target)
    except cuaca.CuacaTidakTersedia as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "jenis_plt": jenis_plt,
        "window_size": window_size,
        "bulan_target": target,
        "cuaca_target": info_cuaca["nilai"],
        "cuaca_sumber": info_cuaca["sumber"],
        "cuaca_keterangan": info_cuaca["keterangan"],
        # Kapasitas bulan target diasumsikan sama dengan bulan terakhir yang
        # tercatat -- konsisten dengan asumsi "kapasitas tetap" pada forecast
        # 2026-2028, dan diungkap ke pengguna lewat field ini.
        "kapasitas_terakhir": baris[-1].kapasitas,
        "data": [
            {
                "tanggal": b.tanggal,
                "produksi": b.produksi,
                "kapasitas": b.kapasitas,
                "cuaca": b.cuaca,
            }
            for b in baris
        ],
    }
