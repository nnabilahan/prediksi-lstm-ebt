"""
Muat model & scaler LSTM sekali saat startup, simpan di memori, dan sediakan
fungsi inferensi. Backend TIDAK PERNAH melatih ulang model -- hanya memuat
artefak .keras/.json yang sudah ada hasil
audit/analysis/build_production_model.py.

[MODEL PRODUKSI] Arsitektur berbeda dari versi CF-fix sebelumnya (satu model
per jenis PLT, scaler pickle terpisah):
  - SATU model "pooled" dipakai bersama oleh beberapa jenis PLT (identitas
    jenis PLT masuk lewat category embedding, bukan satu model per jenis).
    PLTS dan PLTS Atap, misalnya, memakai file model yang SAMA persis.
  - Tiap kombinasi (jenis PLT -> model) sebenarnya N_SEED model (ensembling):
    prediksi akhir = rata-rata dari seluruh model dalam ensemble-nya.
  - Target model tetap CAPACITY FACTOR, TAPI definisinya BEDA dari versi
    CF-fix sebelumnya: di sini `CF = Produksi(GWh) / Kapasitas(MW)` (rasio
    sederhana, TANPA faktor jam-dalam-bulan) -- persis formula di
    audit/analysis/lstm_improved.py. JANGAN pakai formula
    "Produksi x 1000 / (Kapasitas x jam)" dari versi lama, itu skala yang
    berbeda dan akan salah kalau tercampur.
  - PALING PENTING: model butuh nilai Cuaca BULAN YANG DITEBAK sebagai input
    (`cuaca_target`), bukan cuma histori. Ini bukan cara berpikir yang aneh
    -- ini sama seperti peramalan cuaca operasional (BMKG dsb) yang memakai
    prakiraan sebagai input, bukan observasi yang belum terjadi. Endpoint
    /api/predict WAJIB meminta nilai ini dari pengguna sebagai PERKIRAAN
    cuaca (prakiraan/normal klimatologis), BUKAN observasi -- observasi
    bulan depan memang belum ada.

Lihat audit/results/framing_findings.md dan docstring
audit/analysis/build_production_model.py untuk metodologi & alasan lengkap
kenapa arsitektur ini dipilih.
"""
import os
import threading
from datetime import date

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # redam log startup TF yang berisik

import numpy as np
import pandas as pd

import config

# Lock: model.predict() Keras tidak dijamin aman dipanggil dari beberapa
# thread bersamaan pada objek model yang sama, dan FastAPI menjalankan
# endpoint sync di threadpool. Guard murah, bukan bottleneck nyata untuk
# skala pemakaian aplikasi ini.
_lock = threading.Lock()

_konfigurasi: dict = {}          # {jenis_plt: {combo_id, window_size, fitur_exog, geser_cuaca, kategori_idx, n_seed}}
_scaler_params: dict = {}        # {cf_min, cf_max, cuaca_per_kategori: {plt: {min,max}}}
_model_per_combo: dict = {}      # {combo_id: [model_seed0, model_seed1, ...]}
_mape_model: dict = {}
_rentang_training: dict = {}     # {plt: {"Produksi": (min,max), "Kapasitas": (min,max), "Cuaca": (min,max)}}

_loaded = False


def is_loaded() -> bool:
    return _loaded


def get_window_size(jenis_plt: str) -> int:
    return _konfigurasi[jenis_plt]["window_size"]


def get_mape(jenis_plt: str) -> float | None:
    return _mape_model.get(jenis_plt)


def get_rentang(jenis_plt: str) -> dict:
    return _rentang_training.get(jenis_plt, {})


def butuh_cuaca_target(jenis_plt: str) -> bool:
    """True kalau model jenis PLT ini butuh input cuaca bulan yang ditebak
    (geser_cuaca=True dan/atau "cuaca_t" ada di fitur_exog). Seluruh
    kombinasi pemenang saat ini butuh ini -- lihat PEMENANG di
    build_production_model.py -- tapi fungsi ini tetap dicek eksplisit
    supaya kalau suatu saat ada jenis PLT yang memakai varian A (murni lag,
    tidak butuh cuaca_target), endpoint tidak salah mewajibkannya."""
    cfg = _konfigurasi[jenis_plt]
    return cfg["geser_cuaca"] or "cuaca_t" in cfg["fitur_exog"]


def load_artefacts() -> None:
    """Muat seluruh model (per kombinasi, bukan per jenis PLT), parameter
    scaler, MAPE, dan rentang nilai training ke memori. Dipanggil sekali saat
    startup server (lihat lifespan di main.py) -- endpoint /api/predict tidak
    pernah memuat ulang file dari disk per request."""
    global _loaded

    # Import TensorFlow di sini (bukan di top-level modul lain) supaya
    # endpoint CRUD tetap bisa jalan tanpa TensorFlow terpasang kalau suatu
    # saat dipisah; startup server tetap memuatnya sekali di awal, bukan
    # lazy per request.
    from tensorflow.keras.models import load_model

    _konfigurasi.clear()
    _konfigurasi.update(config.load_konfigurasi_model())
    _scaler_params.clear()
    _scaler_params.update(config.load_scaler_params())

    for jenis_plt in config.JENIS_PLT_VALID:
        if jenis_plt not in _konfigurasi:
            raise RuntimeError(
                f"konfigurasi_model.json tidak memuat entri untuk '{jenis_plt}'."
            )
        if jenis_plt not in _scaler_params.get("cuaca_per_kategori", {}):
            raise RuntimeError(
                f"scaler_params.json tidak memuat rentang Cuaca untuk '{jenis_plt}'."
            )

    # Muat model SEKALI per combo_id, dipakai bersama oleh seluruh jenis PLT
    # yang kombinasi pemenangnya sama (mis. PLTS & PLTS Atap).
    _model_per_combo.clear()
    combo_ids = {cfg["combo_id"] for plt, cfg in _konfigurasi.items()
                if plt in config.JENIS_PLT_VALID}
    for cid in combo_ids:
        n_seed = next(c["n_seed"] for c in _konfigurasi.values() if c["combo_id"] == cid)
        model_list = []
        for k_seed in range(n_seed):
            path = config.MODELS_DIR / f"{cid}_seed{k_seed}.keras"
            if not path.exists():
                raise FileNotFoundError(
                    f"Model untuk kombinasi '{cid}' (seed {k_seed}) tidak ditemukan: {path}. "
                    "Jalankan audit/analysis/build_production_model.py lebih dulu."
                )
            model_list.append(load_model(path))
        _model_per_combo[cid] = model_list

    # MAPE per jenis PLT (evaluasi pada data uji 2025), untuk konteks
    # keandalan yang disertakan di setiap response prediksi.
    if config.EVALUASI_FINAL_PATH.exists():
        df_eval = pd.read_csv(config.EVALUASI_FINAL_PATH)
        for _, row in df_eval.iterrows():
            _mape_model[row["Jenis_PLT"]] = float(row["MAPE_Test_2025_Konfirmasi"])

    # Rentang min-max training per jenis PLT, dihitung sekali dari dataset
    # awal -- dipakai untuk peringatan out-of-range, bukan untuk menolak.
    df_dataset = pd.read_csv(config.DATASET_AWAL_PATH)
    for jenis_plt, grup in df_dataset.groupby("Jenis"):
        _rentang_training[jenis_plt] = {
            kolom: (float(grup[kolom].min()), float(grup[kolom].max()))
            for kolom in ("Produksi", "Kapasitas", "Cuaca")
        }

    _loaded = True


def cek_rentang(jenis_plt: str, baris: list[dict], cuaca_target: float | None = None) -> list[str]:
    """Bandingkan nilai input (histori + cuaca_target) terhadap rentang
    min-max data training. Tidak menolak apa pun -- hanya mengembalikan
    daftar pesan peringatan (list kosong berarti seluruh nilai dalam
    rentang)."""
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
    if cuaca_target is not None and "Cuaca" in rentang:
        lo, hi = rentang["Cuaca"]
        if cuaca_target < lo or cuaca_target > hi:
            peringatan.append(
                f"cuaca_target={cuaca_target} di luar rentang data training [{lo:g}, {hi:g}]."
            )
    return peringatan


def _skala(nilai: float, lo: float, hi: float) -> float:
    return (nilai - lo) / (hi - lo) if hi > lo else 0.0


def _skala_balik(nilai: float, lo: float, hi: float) -> float:
    return nilai * (hi - lo) + lo


def _bangun_exog(cfg: dict, cuaca_target_scaled: float, tanggal_target: date) -> np.ndarray:
    """Susun vektor fitur eksogen sesuai `fitur_exog` di config, dengan
    urutan nilai mengikuti urutan nama di `fitur_exog` -- itu urutan yang
    model pelajari saat training (lihat masukan() di lstm_improved.py)."""
    nilai_per_nama = {
        "cuaca_t": cuaca_target_scaled,
        "bulan_sin": np.sin(2 * np.pi * tanggal_target.month / 12),
        "bulan_cos": np.cos(2 * np.pi * tanggal_target.month / 12),
    }
    hasil = []
    for nama in cfg["fitur_exog"]:
        if nama == "cuaca_rel":
            # [KETERBATASAN] "cuaca_rel" butuh rata-rata Cuaca 12 bulan
            # terakhir (termasuk bulan target), yang tidak tersedia dari
            # window histori sependek window_size (3 atau 6 bulan) yang
            # diminta endpoint ini. Tidak ada kombinasi pemenang saat ini
            # yang memakai fitur ini (lihat PEMENANG di
            # build_production_model.py) -- error eksplisit ini adalah
            # pengaman kalau suatu saat konfigurasi berubah tanpa ml.py
            # ikut diperbarui, supaya gagalnya jelas & cepat ketahuan,
            # bukan diam-diam salah hitung.
            raise NotImplementedError(
                "Fitur eksogen 'cuaca_rel' belum didukung endpoint /api/predict "
                "(butuh histori 12 bulan, di luar cakupan window_size saat ini)."
            )
        if nama not in nilai_per_nama:
            raise NotImplementedError(f"Fitur eksogen '{nama}' belum didukung ml.py.")
        hasil.append(nilai_per_nama[nama])
    return np.array([hasil], dtype="float32")  # shape (1, n_exog)


def predict(jenis_plt: str, baris: list[dict], cuaca_target: float,
           kapasitas_target: float | None = None) -> float:
    """Jalankan satu langkah inferensi (rata-rata ensemble N_SEED model).

    `baris` adalah window_size baris terakhir (sudah diurutkan & dipangkas
    oleh caller), tiap baris dict berisi key 'produksi', 'kapasitas',
    'cuaca', 'tanggal' (float/float/float/date, sudah divalidasi lengkap
    oleh caller).

    `cuaca_target` WAJIB: perkiraan/prakiraan Cuaca untuk bulan yang ditebak
    (BUKAN observasi -- observasi bulan itu belum ada). Model butuh nilai ini
    karena arsitekturnya "known-future covariate" -- lihat docstring modul.

    `kapasitas_target`: kapasitas bulan yang ditebak, dipakai mengonversi CF
    hasil prediksi balik ke GWh. Kalau tidak diberikan, memakai kapasitas
    baris histori terakhir (asumsi LOCF -- konsisten dengan asumsi yang sama
    dipakai forecast_autoregressive() di pipeline utama)."""
    cfg = _konfigurasi[jenis_plt]
    window = cfg["window_size"]
    cuaca_lo = _scaler_params["cuaca_per_kategori"][jenis_plt]["min"]
    cuaca_hi = _scaler_params["cuaca_per_kategori"][jenis_plt]["max"]
    cf_lo, cf_hi = _scaler_params["cf_min"], _scaler_params["cf_max"]

    if kapasitas_target is None:
        kapasitas_target = baris[-1]["kapasitas"]

    cuaca_lag_scaled = [_skala(r["cuaca"], cuaca_lo, cuaca_hi) for r in baris]
    cf_lag_scaled = [_skala(r["produksi"] / r["kapasitas"], cf_lo, cf_hi) for r in baris]
    cuaca_target_scaled = _skala(cuaca_target, cuaca_lo, cuaca_hi)

    if cfg["geser_cuaca"]:
        # Jendela cuaca digeser satu langkah: buang titik terlama, tambahkan
        # cuaca_target di ujung -- identik dengan buat_sequence(geser_cuaca=True)
        # di lstm_improved.py.
        cuaca_channel = cuaca_lag_scaled[1:] + [cuaca_target_scaled]
    else:
        cuaca_channel = cuaca_lag_scaled

    X = np.array([[cuaca_channel[i], cf_lag_scaled[i]] for i in range(window)],
                 dtype="float32").reshape(1, window, 2)
    kat = np.array([[cfg["kategori_idx"]]], dtype="int32")

    tanggal_terakhir = baris[-1]["tanggal"]
    tahun, bulan = tanggal_terakhir.year, tanggal_terakhir.month
    bulan_target, tahun_target = (bulan % 12) + 1, tahun + (1 if bulan == 12 else 0)
    tanggal_target = date(tahun_target, bulan_target, 1)

    inputs = [X, kat]
    if cfg["fitur_exog"]:
        inputs.append(_bangun_exog(cfg, cuaca_target_scaled, tanggal_target))

    model_list = _model_per_combo[cfg["combo_id"]]
    with _lock:
        prediksi_cf_scaled = [
            float(m.predict(inputs, verbose=0)[0, 0]) for m in model_list
        ]
    cf_pred_scaled = float(np.mean(prediksi_cf_scaled))

    cf_pred = _skala_balik(cf_pred_scaled, cf_lo, cf_hi)
    produksi_pred = max(0.0, cf_pred) * kapasitas_target
    return max(0.0, float(produksi_pred))  # produksi tidak boleh negatif secara fisis
