"""
Endpoint CRUD + ekspor/impor tabel `data_historis`.

Catatan lingkup: endpoint di sini hanya mengelola data historis mentah di
database. Forecast 2026-2028, gap analysis RUED, dan perbandingan
ARIMA/Naive TIDAK ada di sini -- itu tetap statis dari src/lib/data.js.
"""
import io

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import config
from database import get_db
from models import DataHistoris
from schemas import (
    DataHistorisCreate,
    DataHistorisList,
    DataHistorisOut,
    DataHistorisUpdate,
    ImportResult,
)

router = APIRouter(prefix="/api/data", tags=["data"])

# Kolom wajib saat impor. "Jenis_PLT" adalah nama yang dipakai kontrak API
# (dan tombol Ekspor di frontend); "Jenis" diterima sebagai alias karena itu
# nama kolom asli di audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv.
KOLOM_WAJIB = ["Tanggal", "Produksi", "Kapasitas", "Cuaca"]
ALIAS_JENIS = ["Jenis_PLT", "Jenis"]


def _pesan_whitelist() -> str:
    return f"Jenis PLT tidak dikenali. Jenis PLT yang valid: {', '.join(config.JENIS_PLT_VALID)}."


def _cek_whitelist(jenis_plt: str) -> None:
    if jenis_plt not in config.JENIS_PLT_VALID:
        raise HTTPException(status_code=400, detail=_pesan_whitelist())


def _ambil_atau_404(db: Session, item_id: int) -> DataHistoris:
    item = db.get(DataHistoris, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Data dengan id={item_id} tidak ditemukan.")
    return item


@router.get("", response_model=DataHistorisList)
def list_data(
    jenis_plt: str | None = Query(None, description="Filter jenis PLT (harus salah satu whitelist)."),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if jenis_plt is not None:
        _cek_whitelist(jenis_plt)

    stmt = select(DataHistoris)
    count_stmt = select(func.count()).select_from(DataHistoris)
    if jenis_plt is not None:
        stmt = stmt.where(DataHistoris.jenis_plt == jenis_plt)
        count_stmt = count_stmt.where(DataHistoris.jenis_plt == jenis_plt)

    total = db.scalar(count_stmt)
    items = db.execute(
        stmt.order_by(DataHistoris.tanggal, DataHistoris.jenis_plt)
        .limit(limit)
        .offset(offset)
    ).scalars().all()

    return DataHistorisList(total=total, limit=limit, offset=offset, items=items)


@router.post("", response_model=DataHistorisOut, status_code=201)
def create_data(payload: DataHistorisCreate, db: Session = Depends(get_db)):
    _cek_whitelist(payload.jenis_plt)

    item = DataHistoris(
        tanggal=payload.tanggal,
        jenis_plt=payload.jenis_plt,
        produksi=payload.produksi,
        kapasitas=payload.kapasitas,
        cuaca=payload.cuaca,
        sumber=config.SUMBER_INPUT_PENGGUNA,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DataHistorisOut)
def update_data(item_id: int, payload: DataHistorisUpdate, db: Session = Depends(get_db)):
    _cek_whitelist(payload.jenis_plt)
    item = _ambil_atau_404(db, item_id)

    item.tanggal = payload.tanggal
    item.jenis_plt = payload.jenis_plt
    item.produksi = payload.produksi
    item.kapasitas = payload.kapasitas
    item.cuaca = payload.cuaca
    # `sumber` sengaja tidak diubah -- status asal data (rekonstruksi vs
    # input pengguna) tetap terlacak walau isinya diedit.

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_data(item_id: int, db: Session = Depends(get_db)):
    item = _ambil_atau_404(db, item_id)
    db.delete(item)
    db.commit()
    return {"pesan": f"Data id={item_id} berhasil dihapus."}


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    items = db.execute(
        select(DataHistoris).order_by(DataHistoris.jenis_plt, DataHistoris.tanggal)
    ).scalars().all()

    df = pd.DataFrame([
        {
            "ID": r.id,
            "Tanggal": r.tanggal.isoformat(),
            "Jenis_PLT": r.jenis_plt,
            "Produksi": r.produksi,
            "Kapasitas": r.kapasitas,
            "Cuaca": r.cuaca,
            "Sumber": r.sumber,
        }
        for r in items
    ])
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data_historis_ebt.csv"},
    )


def _baca_upload(file: UploadFile, content: bytes) -> pd.DataFrame:
    nama = (file.filename or "").lower()
    try:
        if nama.endswith(".csv"):
            return pd.read_csv(io.BytesIO(content))
        if nama.endswith(".xlsx") or nama.endswith(".xls"):
            return pd.read_excel(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Gagal membaca file '{file.filename}': {exc}",
        ) from exc

    raise HTTPException(
        status_code=400,
        detail=f"Format file '{file.filename}' tidak didukung. Gunakan .csv, .xlsx, atau .xls.",
    )


@router.post("/import", response_model=ImportResult)
async def import_data(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' kosong.")

    df = _baca_upload(file, content)

    # Kolom Jenis_PLT/Jenis: terima salah satu, normalisasi ke "Jenis_PLT".
    kolom_jenis_ditemukan = next((k for k in ALIAS_JENIS if k in df.columns), None)
    if kolom_jenis_ditemukan is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Kolom jenis PLT tidak ditemukan. Sertakan salah satu kolom "
                f"berikut: {ALIAS_JENIS}."
            ),
        )
    if kolom_jenis_ditemukan != "Jenis_PLT":
        df = df.rename(columns={kolom_jenis_ditemukan: "Jenis_PLT"})

    kolom_diperlukan = KOLOM_WAJIB + ["Jenis_PLT"]
    kolom_hilang = [k for k in kolom_diperlukan if k not in df.columns]
    if kolom_hilang:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Kolom wajib tidak lengkap: {kolom_hilang}. "
                f"Kolom yang dibutuhkan: {kolom_diperlukan} "
                f"(kolom jenis PLT juga bisa memakai nama 'Jenis'). "
                f"Kolom yang ditemukan di file: {list(df.columns)}."
            ),
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="File tidak memuat baris data.")

    # Baris kosong pada kolom wajib -- tolak seluruh file, sebutkan baris mana.
    subset = df[["Tanggal", "Jenis_PLT", "Produksi", "Kapasitas", "Cuaca"]]
    baris_kosong = subset[subset.isna().any(axis=1)]
    if not baris_kosong.empty:
        nomor_baris = [i + 2 for i in baris_kosong.index]  # +2: header + index 0-based
        raise HTTPException(
            status_code=400,
            detail=(
                "Ada baris dengan nilai kosong pada Tanggal/Jenis_PLT/Produksi/"
                f"Kapasitas/Cuaca di baris file (termasuk header): {nomor_baris}. "
                "Perbaiki file lalu unggah ulang -- tidak ada pengisian otomatis."
            ),
        )

    # Jenis PLT harus masuk whitelist.
    jenis_asing = sorted(set(df["Jenis_PLT"]) - set(config.JENIS_PLT_VALID))
    if jenis_asing:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ditemukan jenis PLT di luar whitelist: {jenis_asing}. "
                f"Jenis PLT yang valid: {config.JENIS_PLT_VALID}."
            ),
        )

    # Tanggal harus bisa diparse; numerik (Produksi/Kapasitas/Cuaca) harus valid.
    try:
        tanggal_parsed = pd.to_datetime(df["Tanggal"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Kolom Tanggal tidak bisa diparse sebagai tanggal: {exc}",
        ) from exc

    kolom_numerik = ["Produksi", "Kapasitas", "Cuaca"]
    for kolom in kolom_numerik:
        if not pd.api.types.is_numeric_dtype(df[kolom]):
            non_numerik = pd.to_numeric(df[kolom], errors="coerce")
            baris_invalid = [i + 2 for i in df.index[non_numerik.isna()]]
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Kolom {kolom} memuat nilai non-numerik di baris (termasuk header): "
                    f"{baris_invalid}."
                ),
            )

    items = [
        DataHistoris(
            tanggal=tanggal_parsed.iloc[i].date(),
            jenis_plt=str(row["Jenis_PLT"]),
            produksi=float(row["Produksi"]),
            kapasitas=float(row["Kapasitas"]),
            cuaca=float(row["Cuaca"]),
            sumber=config.SUMBER_INPUT_PENGGUNA,
        )
        for i, (_, row) in enumerate(df.iterrows())
    ]
    db.add_all(items)
    db.commit()

    return ImportResult(
        baris_diterima=len(items),
        baris_ditolak=0,
        pesan=f"{len(items)} baris berhasil diimpor dengan sumber='{config.SUMBER_INPUT_PENGGUNA}'.",
    )
