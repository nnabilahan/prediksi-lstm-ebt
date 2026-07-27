"""Skema Pydantic untuk request/response endpoint data historis."""
from datetime import date

from pydantic import BaseModel, ConfigDict


class DataHistorisBase(BaseModel):
    tanggal: date
    jenis_plt: str
    produksi: float
    kapasitas: float
    cuaca: float


class DataHistorisCreate(DataHistorisBase):
    """Payload POST /api/data. `sumber` tidak diterima dari klien -- server
    selalu memaksanya jadi "input_pengguna" (lihat routers/data.py)."""


class DataHistorisUpdate(DataHistorisBase):
    """Payload PUT /api/data/{id}. Full replace -- `sumber` baris yang sudah
    ada tetap dipertahankan, tidak bisa diubah lewat endpoint ini."""


class DataHistorisOut(DataHistorisBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sumber: str


class DataHistorisList(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DataHistorisOut]


class ImportResult(BaseModel):
    baris_diterima: int
    baris_ditolak: int
    pesan: str


class TitikDataPrediksi(BaseModel):
    """Satu baris deret waktu untuk /api/predict.

    Produksi/Kapasitas/Cuaca sengaja Optional (bukan wajib di level skema):
    baris yang kosong tetap harus LOLOS parsing supaya lapis validasi
    "kelengkapan fitur" di endpoint bisa menyebutkan baris mana yang kurang,
    bukan berhenti dengan error 422 generik dari Pydantic.
    """
    tanggal: date
    produksi: float | None = None
    kapasitas: float | None = None
    cuaca: float | None = None


class PredictRequest(BaseModel):
    jenis_plt: str
    data: list[TitikDataPrediksi]


class PredictResponse(BaseModel):
    jenis_plt: str
    prediksi: float
    mape_model: float | None
    peringatan: str | None
