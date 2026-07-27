"""
Konfigurasi terpusat backend SIPREBAR: path artefak, whitelist jenis PLT, dan
pembacaan konfigurasi model hasil pipeline.

Prinsip: SATU SUMBER KEBENARAN. Nilai seperti `window_size` dan urutan fitur
input TIDAK di-hardcode di sini -- semuanya dibaca langsung dari
`konfigurasi_model.json` yang ditulis oleh pipeline training. Kalau pipeline
dijalankan ulang dengan window_size berbeda, backend ikut menyesuaikan tanpa
perlu diedit.
"""
import json
from pathlib import Path

# backend/config.py -> backend/ -> root repo
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"

PIPELINE_DIR = BASE_DIR / "audit" / "results" / "pipeline_run" / "EBT_LSTM_Streamlit"
KONFIGURASI_MODEL_PATH = PIPELINE_DIR / "config" / "konfigurasi_model.json"
MODELS_DIR = PIPELINE_DIR / "models"
SCALERS_DIR = PIPELINE_DIR / "scalers"
EVALUASI_FINAL_PATH = PIPELINE_DIR / "evaluation" / "evaluasi_final.csv"

DATASET_AWAL_PATH = BASE_DIR / "audit" / "source" / "DATA_PHASE_3_REGIONAL_MODIFIED.csv"

DATABASE_PATH = BACKEND_DIR / "siprebar.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Whitelist 7 jenis PLT yang punya model terlatih. Menambah jenis di luar
# daftar ini TIDAK cukup dengan mengedit konstanta -- butuh model & scaler
# baru dari pipeline training.
JENIS_PLT_VALID = [
    "PLTA",
    "PLTB",
    "PLTM",
    "PLTMH",
    "PLTS",
    "PLT Hybrid",
    "PLTS Atap",
]

# Nilai `sumber` pada tabel data_historis -- membedakan data bawaan hasil
# rekonstruksi dari data yang benar-benar diinput pengguna.
SUMBER_REKONSTRUKSI = "rekonstruksi"
SUMBER_INPUT_PENGGUNA = "input_pengguna"


def slug_plt(jenis_plt: str) -> str:
    """Nama jenis PLT -> potongan nama file artefak ('PLT Hybrid' -> 'PLT_Hybrid')."""
    return jenis_plt.replace(" ", "_")


def load_konfigurasi_model() -> dict:
    """Baca konfigurasi_model.json (window_size, fitur_input, nama file artefak).

    Raise FileNotFoundError kalau pipeline belum pernah dijalankan di mesin ini,
    dengan pesan yang menunjuk ke akar masalahnya (bukan KeyError misterius
    beberapa lapis kemudian).
    """
    if not KONFIGURASI_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"konfigurasi_model.json tidak ditemukan di {KONFIGURASI_MODEL_PATH}. "
            "Jalankan pipeline training lebih dulu (audit/run_pipeline*.py) atau "
            "salin folder audit/results/pipeline_run/ dari hasil run sebelumnya."
        )
    with open(KONFIGURASI_MODEL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def cek_artefak() -> dict:
    """Status keberadaan artefak model & scaler per jenis PLT.

    Dipakai oleh /api/health supaya masalah 'model belum ada di mesin ini'
    ketahuan sebelum request inferensi pertama, bukan saat pengguna sudah
    menekan tombol Prediksi.
    """
    hasil = {}
    for plt in JENIS_PLT_VALID:
        slug = slug_plt(plt)
        hasil[plt] = {
            "model": (MODELS_DIR / f"model_final_{slug}.keras").exists(),
            "scaler_fitur": (SCALERS_DIR / f"scaler_fitur_{slug}.pkl").exists(),
            "scaler_target": (SCALERS_DIR / f"scaler_target_{slug}.pkl").exists(),
        }
    return hasil
