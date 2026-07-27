"""
Muat model & scaler LSTM sekali saat startup, simpan di memori, dan sediakan
fungsi inferensi. Backend TIDAK PERNAH melatih ulang model -- hanya memuat
artefak .keras/.pkl yang sudah ada hasil pipeline training.

Mekanisme scaling & bentuk input mengikuti PERSIS apa yang dipakai saat model
dilatih (lihat "KEGIATAN 2" & "KEGIATAN 3" fungsi forecast_autoregressive di
audit/source_fixed/bs_tf_lstm_fix_fixed.py, sekitar baris 2720-3120):

  - scaler_fitur_{PLT}.pkl di-fit HANYA pada 2 kolom [Cuaca, Kapasitas].
  - scaler_target_{PLT}.pkl di-fit HANYA pada 1 kolom [Produksi].
  - Input model = hstack([fitur_scaled, target_scaled]) -> (window_size, 3),
    urutan kolom [Cuaca, Kapasitas, Produksi] -- SAMA dengan "fitur_input" di
    konfigurasi_model.json.
  - Prediksi mentah (skala 0-1) di-inverse_transform pakai scaler_target,
    lalu di-clip minimum 0 (produksi tidak boleh negatif secara fisis) --
    perilaku yang sama dipakai pipeline untuk forecast 2026-2028.

Verifikasi bentuk input model (mis. PLTA: window=6, 3 fitur) ->
model.input_shape == (None, 6, 3) sudah dicek manual sebelum modul ini ditulis.
"""
import os
import pickle
import threading

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # redam log startup TF yang berisik

import numpy as np
import pandas as pd

import config

# Lock per PLT: model.predict() Keras tidak dijamin aman dipanggil dari
# beberapa thread bersamaan pada objek model yang sama, dan FastAPI
# menjalankan endpoint sync di threadpool. Guard murah, bukan bottleneck
# nyata untuk skala pemakaian aplikasi ini.
_lock = threading.Lock()

_models: dict = {}
_scaler_fitur: dict = {}
_scaler_target: dict = {}
_window_size: dict = {}
_mape_model: dict = {}
_rentang_training: dict = {}  # {plt: {"Produksi": (min,max), "Kapasitas": (min,max), "Cuaca": (min,max)}}

_loaded = False


def is_loaded() -> bool:
    return _loaded


def get_window_size(jenis_plt: str) -> int:
    return _window_size[jenis_plt]


def get_mape(jenis_plt: str) -> float | None:
    return _mape_model.get(jenis_plt)


def get_rentang(jenis_plt: str) -> dict:
    return _rentang_training.get(jenis_plt, {})


def load_artefacts() -> None:
    """Muat seluruh model, scaler, window_size, MAPE, dan rentang nilai
    training ke memori. Dipanggil sekali saat startup server (lihat
    lifespan di main.py) -- endpoint /api/predict tidak pernah memuat
    ulang file dari disk per request."""
    global _loaded

    # Import TensorFlow di sini (bukan di top-level modul lain) supaya
    # endpoint CRUD (Task Group 6) tetap bisa jalan tanpa TensorFlow
    # terpasang kalau suatu saat dipisah; startup server tetap memuatnya
    # sekali di awal, bukan lazy per request.
    from tensorflow.keras.models import load_model

    konfigurasi = config.load_konfigurasi_model()

    for jenis_plt in config.JENIS_PLT_VALID:
        if jenis_plt not in konfigurasi:
            raise RuntimeError(
                f"konfigurasi_model.json tidak memuat entri untuk '{jenis_plt}'."
            )
        cfg = konfigurasi[jenis_plt]
        slug = config.slug_plt(jenis_plt)

        path_model = config.MODELS_DIR / f"model_final_{slug}.keras"
        path_scaler_fitur = config.SCALERS_DIR / f"scaler_fitur_{slug}.pkl"
        path_scaler_target = config.SCALERS_DIR / f"scaler_target_{slug}.pkl"

        for path in (path_model, path_scaler_fitur, path_scaler_target):
            if not path.exists():
                raise FileNotFoundError(
                    f"Artefak untuk {jenis_plt} tidak ditemukan: {path}. "
                    "Salin folder audit/results/pipeline_run/EBT_LSTM_Streamlit/ "
                    "dari hasil run pipeline sebelumnya."
                )

        _models[jenis_plt] = load_model(path_model)
        with open(path_scaler_fitur, "rb") as f:
            _scaler_fitur[jenis_plt] = pickle.load(f)
        with open(path_scaler_target, "rb") as f:
            _scaler_target[jenis_plt] = pickle.load(f)
        _window_size[jenis_plt] = cfg["window_size"]

    # MAPE per PLT (tahap yang dipakai untuk Model Final), untuk konteks
    # keandalan yang disertakan di setiap response prediksi.
    if config.EVALUASI_FINAL_PATH.exists():
        df_eval = pd.read_csv(config.EVALUASI_FINAL_PATH)
        for _, row in df_eval.iterrows():
            _mape_model[row["Jenis_PLT"]] = float(row["MAPE_Test_2025_Konfirmasi"])

    # Rentang min-max training per PLT, dihitung sekali dari dataset awal
    # dan disimpan di memori -- dipakai untuk peringatan out-of-range,
    # bukan untuk menolak request.
    df_dataset = pd.read_csv(config.DATASET_AWAL_PATH)
    for jenis_plt, grup in df_dataset.groupby("Jenis"):
        _rentang_training[jenis_plt] = {
            kolom: (float(grup[kolom].min()), float(grup[kolom].max()))
            for kolom in ("Produksi", "Kapasitas", "Cuaca")
        }

    _loaded = True


def cek_rentang(jenis_plt: str, baris: list[dict]) -> list[str]:
    """Bandingkan nilai input terhadap rentang min-max data training.
    Tidak menolak apa pun -- hanya mengembalikan daftar pesan peringatan
    (list kosong berarti seluruh nilai dalam rentang)."""
    rentang = _rentang_training.get(jenis_plt, {})
    peringatan = []
    for i, row in enumerate(baris, start=1):
        for kolom, field in (("Produksi", "produksi"), ("Kapasitas", "kapasitas"), ("Cuaca", "cuaca")):
            if kolom not in rentang:
                continue
            nilai = row[field]
            lo, hi = rentang[kolom]
            if nilai < lo or nilai > hi:
                peringatan.append(
                    f"Baris {i}: {kolom}={nilai} di luar rentang data training "
                    f"[{lo:g}, {hi:g}]."
                )
    return peringatan


def predict(jenis_plt: str, baris: list[dict]) -> float:
    """Jalankan satu langkah inferensi. `baris` adalah window_size baris
    terakhir (sudah diurutkan & dipangkas oleh caller), tiap baris dict
    berisi key 'produksi', 'kapasitas', 'cuaca' (float, sudah divalidasi
    lengkap oleh caller)."""
    model = _models[jenis_plt]
    scaler_fitur = _scaler_fitur[jenis_plt]
    scaler_target = _scaler_target[jenis_plt]
    window_size = _window_size[jenis_plt]

    fitur = np.array([[r["cuaca"], r["kapasitas"]] for r in baris], dtype=float)
    produksi = np.array([[r["produksi"]] for r in baris], dtype=float)

    fitur_scaled = scaler_fitur.transform(fitur)
    target_scaled = scaler_target.transform(produksi)
    sequence = np.hstack([fitur_scaled, target_scaled]).reshape(1, window_size, 3)

    with _lock:
        pred_scaled = model.predict(sequence, verbose=0)[0, 0]

    pred_asli = scaler_target.inverse_transform([[pred_scaled]])[0, 0]
    return max(0.0, float(pred_asli))  # produksi tidak boleh negatif (sama seperti pipeline)
