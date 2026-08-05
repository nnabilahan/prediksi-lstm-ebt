"""
Konfigurasi terpusat backend SIPREBAR: path artefak, whitelist jenis PLT, dan
pembacaan konfigurasi model hasil pipeline.

[MODEL PRODUKSI] Artefak sekarang berasal dari
audit/analysis/build_production_model.py (model pooled + category embedding
+ ensembling, dipilih lewat walk-forward validation), BUKAN lagi dari
audit/results/pipeline_run_v4/EBT_LSTM_Streamlit/ (pipeline notebook-style
lama, satu model per jenis PLT). Lihat audit/results/framing_findings.md dan
docstring build_production_model.py untuk alasan & metodologi lengkap.

Prinsip: SATU SUMBER KEBENARAN. Nilai seperti `window_size`, `fitur_exog`,
dan `combo_id` per jenis PLT TIDAK di-hardcode di sini -- semuanya dibaca
langsung dari `konfigurasi_model.json` yang ditulis
build_production_model.py. Kalau skrip itu dijalankan ulang dengan kombinasi
pemenang berbeda, backend ikut menyesuaikan tanpa perlu diedit.
"""
import json
from pathlib import Path

# backend/config.py -> backend/ -> root repo
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"

PRODUCTION_DIR = BASE_DIR / "audit" / "results" / "production_model"
KONFIGURASI_MODEL_PATH = PRODUCTION_DIR / "config" / "konfigurasi_model.json"
MODELS_DIR = PRODUCTION_DIR / "models"
SCALER_PARAMS_PATH = PRODUCTION_DIR / "scalers" / "scaler_params.json"
EVALUASI_FINAL_PATH = PRODUCTION_DIR / "evaluation" / "evaluasi_final.csv"

DATASET_AWAL_PATH = BASE_DIR / "audit" / "source" / "DATA_REGIONAL_5JENIS.csv"

DATABASE_PATH = BACKEND_DIR / "siprebar.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Whitelist kategori pembangkit yang punya model terlatih. Menambah jenis di
# luar daftar ini TIDAK cukup dengan mengedit konstanta -- butuh model &
# scaler baru dari pipeline training.
#
# [DATASET 4/5 JENIS] Dataset regional memuat 5 jenis PLT. PLTMH dan
# PLT Hybrid tidak ada di dataset ini.
JENIS_PLT_VALID = [
    "PLTA",
    "PLTB",
    "PLTM",
    "PLTS",
    "PLTS Atap",
]

# Nilai `sumber` pada tabel data_historis -- membedakan data bawaan hasil
# rekonstruksi dari data yang benar-benar diinput pengguna.
SUMBER_REKONSTRUKSI = "rekonstruksi"
SUMBER_INPUT_PENGGUNA = "input_pengguna"

# Dipakai endpoint GET /api/data untuk memvalidasi query `sumber`, supaya nilai
# yang tidak dikenal ditolak alih-alih mengembalikan tabel kosong.
SUMBER_VALID = (SUMBER_REKONSTRUKSI, SUMBER_INPUT_PENGGUNA)


def load_konfigurasi_model() -> dict:
    """Baca konfigurasi_model.json (per jenis PLT: combo_id, window_size,
    fitur_exog, geser_cuaca, kategori_idx, n_seed).

    Raise FileNotFoundError kalau build_production_model.py belum pernah
    dijalankan di mesin ini, dengan pesan yang menunjuk ke akar masalahnya
    (bukan KeyError misterius beberapa lapis kemudian).
    """
    if not KONFIGURASI_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"konfigurasi_model.json tidak ditemukan di {KONFIGURASI_MODEL_PATH}. "
            "Jalankan audit/analysis/build_production_model.py lebih dulu "
            "(butuh audit/analysis/lstm_improved.py sudah pernah dijalankan "
            "sampai selesai untuk tahu kombinasi pemenang)."
        )
    with open(KONFIGURASI_MODEL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scaler_params() -> dict:
    """Baca scaler_params.json (rentang min-max CF global & Cuaca per jenis PLT,
    dipakai ml.py untuk normalisasi/denormalisasi manual -- bukan objek
    MinMaxScaler pickle, karena hanya perlu 2 angka per rentang)."""
    if not SCALER_PARAMS_PATH.exists():
        raise FileNotFoundError(
            f"scaler_params.json tidak ditemukan di {SCALER_PARAMS_PATH}. "
            "Jalankan audit/analysis/build_production_model.py lebih dulu."
        )
    with open(SCALER_PARAMS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def cek_artefak() -> dict:
    """Status keberadaan model per jenis PLT (dicek lewat combo_id di
    konfigurasi_model.json, karena satu file model bisa dipakai bersama oleh
    beberapa jenis PLT yang kombinasi pemenangnya sama).

    Dipakai oleh /api/health supaya masalah 'model belum ada di mesin ini'
    ketahuan sebelum request inferensi pertama, bukan saat pengguna sudah
    menekan tombol Prediksi.
    """
    hasil = {}
    try:
        konfigurasi = load_konfigurasi_model()
    except FileNotFoundError:
        return {plt: {"model": False, "config": False} for plt in JENIS_PLT_VALID}

    for plt in JENIS_PLT_VALID:
        cfg = konfigurasi.get(plt)
        if cfg is None:
            hasil[plt] = {"model": False, "config": False}
            continue
        n_seed = cfg["n_seed"]
        model_ada = all(
            (MODELS_DIR / f"{cfg['combo_id']}_seed{k}.keras").exists()
            for k in range(n_seed)
        )
        hasil[plt] = {"model": model_ada, "config": True}
    return hasil
