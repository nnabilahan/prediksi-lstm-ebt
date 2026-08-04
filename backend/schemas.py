"""Skema Pydantic untuk request/response endpoint data historis."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


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
    """Payload POST /api/predict.

    `cuaca_target` WAJIB: perkiraan/prakiraan Cuaca untuk bulan yang ditebak
    -- BUKAN observasi (observasi bulan itu memang belum ada). Model produksi
    memakai arsitektur "known-future covariate": prediksi CF bulan target
    bergantung pada nilai Cuaca bulan itu sendiri, jadi wajib diisi dengan
    estimasi (mis. prakiraan BMKG atau normal klimatologis bulan tsb), bukan
    dikosongkan atau ditebak asal. Lihat backend/ml.py untuk detail
    metodologis.
    """
    jenis_plt: str
    data: list[TitikDataPrediksi]
    cuaca_target: float = Field(
        description=(
            "Perkiraan/prakiraan Cuaca untuk bulan yang ditebak (bukan "
            "observasi -- observasi bulan itu belum ada)."
        )
    )
    kapasitas_target: float | None = Field(
        default=None,
        description=(
            "Kapasitas bulan yang ditebak. Opsional -- kalau tidak diisi, "
            "memakai kapasitas baris histori terakhir (asumsi LOCF)."
        ),
    )


class PredictResponse(BaseModel):
    jenis_plt: str
    prediksi: float
    mape_model: float | None
    peringatan: str | None
