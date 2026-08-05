"""
Penyedia nilai Cuaca untuk halaman Prediksi.

Model produksi adalah model *known-future covariate*: untuk menebak produksi
bulan X, ia butuh nilai Cuaca bulan X itu sendiri. Sebelumnya nilai tersebut
harus diketik manual oleh pengguna -- padahal untuk bulan yang belum lewat,
angka itu tidak mungkin diketahui siapa pun. Modul ini menghilangkan tebakan
manual tersebut dengan dua strategi, sesuai posisi bulan target:

  1. Bulan yang SUDAH LEWAT  -> tarik observasi riil dari NASA POWER.
  2. Bulan yang BELUM LEWAT  -> normal klimatologis, yaitu rata-rata bulan
     kalender yang sama dari seluruh data historis di database.

Strategi (2) adalah asumsi yang sama persis dengan yang dipakai forecast
2026-2028 di halaman Dashboard, jadi angka antar halaman tetap sebanding.

Koordinat & parameter di bawah DISALIN dari
audit/source/tarik_cuaca_nasa_power.py -- skrip yang menghasilkan kolom Cuaca
pada dataset latih. Nilainya dipakai apa adanya tanpa konversi satuan, dan itu
sudah diverifikasi cocok 1:1 dengan isi database (mis. Hydro Januari 2023 =
7,79 = kolom cuaca PLTA/PLTM pada tanggal tersebut). Menggeser koordinat atau
mengganti parameter di sini akan membuat input inferensi tidak lagi sebanding
dengan data latih.
"""
import logging
from datetime import date

import requests
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import DataHistoris

logger = logging.getLogger("siprebar.cuaca")

BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# Jenis PLT -> titik pengukuran cuaca yang mewakilinya. PLTA & PLTM berbagi
# titik Hydro, PLTS & PLTS Atap berbagi titik Solar -- persis seperti saat
# dataset latih dibentuk.
LOKASI_PLT = {
    "PLTA":      {"lat": -2.86, "lon": 120.79, "parameter": "PRECTOTCORR"},
    "PLTM":      {"lat": -2.86, "lon": 120.79, "parameter": "PRECTOTCORR"},
    "PLTB":      {"lat": -4.64, "lon": 119.82, "parameter": "WS10M"},
    "PLTS":      {"lat": -5.10, "lon": 119.60, "parameter": "ALLSKY_SFC_SW_DWN"},
    "PLTS Atap": {"lat": -5.10, "lon": 119.60, "parameter": "ALLSKY_SFC_SW_DWN"},
}

MISSING_VALUE = -999.0  # kode data hilang standar NASA POWER
TIMEOUT_DETIK = 15


class CuacaTidakTersedia(Exception):
    """Tidak ada nilai yang bisa diberikan, baik dari NASA POWER maupun histori."""


def _ambil_nasa_power(jenis_plt: str, target: date) -> float | None:
    """Observasi riil NASA POWER untuk satu bulan, atau None kalau belum ada.

    Mengembalikan None (bukan melempar exception) untuk semua kegagalan yang
    wajar terjadi -- bulan belum terbit, jaringan mati, API sedang down --
    supaya pemanggil bisa jatuh ke normal klimatologis tanpa menganggapnya
    error. Kegagalan tetap dicatat di log agar bisa ditelusuri.
    """
    lokasi = LOKASI_PLT[jenis_plt]
    parameter = lokasi["parameter"]
    try:
        resp = requests.get(
            BASE_URL,
            params={
                "parameters": parameter,
                "community": "RE",
                "longitude": lokasi["lon"],
                "latitude": lokasi["lat"],
                "format": "JSON",
                "start": target.year,
                "end": target.year,
            },
            timeout=TIMEOUT_DETIK,
        )
        resp.raise_for_status()
        bulanan = resp.json()["properties"]["parameter"][parameter]
    except (requests.RequestException, KeyError, ValueError) as exc:
        logger.info("NASA POWER tidak dapat dipakai untuk %s %s: %s", jenis_plt, target, exc)
        return None

    nilai = bulanan.get(f"{target.year}{target.month:02d}")
    if nilai is None or nilai == MISSING_VALUE:
        return None
    return float(nilai)


def _normal_klimatologis(db: Session, jenis_plt: str, bulan: int) -> float | None:
    """Rata-rata bulan kalender yang sama dari seluruh histori di database."""
    return db.scalar(
        select(func.avg(DataHistoris.cuaca))
        .where(DataHistoris.jenis_plt == jenis_plt)
        # strftime dipakai supaya query tetap satu perjalanan ke database dan
        # tidak perlu menarik seluruh baris ke Python hanya untuk dirata-rata.
        .where(func.strftime("%m", DataHistoris.tanggal) == f"{bulan:02d}")
    )


def ambil_cuaca(db: Session, jenis_plt: str, target: date) -> dict:
    """Nilai Cuaca terbaik yang tersedia untuk `jenis_plt` pada bulan `target`.

    Selalu melaporkan ASAL angkanya lewat field `sumber`, karena observasi dan
    asumsi tidak boleh terlihat sama di antarmuka -- pengguna harus tahu mana
    yang fakta dan mana yang perkiraan.
    """
    bulan_ini = date.today().replace(day=1)
    target = target.replace(day=1)

    if target < bulan_ini:
        nilai = _ambil_nasa_power(jenis_plt, target)
        if nilai is not None:
            return {
                "nilai": round(nilai, 4),
                "sumber": "nasa_power",
                "keterangan": (
                    "Observasi riil NASA POWER untuk bulan tersebut -- sumber "
                    "yang sama dengan kolom Cuaca pada dataset latih."
                ),
            }

    rata = _normal_klimatologis(db, jenis_plt, target.month)
    if rata is None:
        raise CuacaTidakTersedia(
            f"Tidak ada data historis {jenis_plt} untuk bulan ke-{target.month}, "
            "sehingga normal klimatologis tidak bisa dihitung. Isi nilai Cuaca "
            "secara manual."
        )

    if target < bulan_ini:
        keterangan = (
            "NASA POWER belum menerbitkan angka bulan ini, jadi dipakai normal "
            "klimatologis (rata-rata bulan kalender yang sama dari data historis)."
        )
    else:
        keterangan = (
            "Bulan target belum lewat sehingga observasinya belum ada di mana pun. "
            "Dipakai normal klimatologis -- asumsi yang sama dengan forecast "
            "2026-2028 di halaman Dashboard."
        )

    return {"nilai": round(float(rata), 4), "sumber": "klimatologi", "keterangan": keterangan}
