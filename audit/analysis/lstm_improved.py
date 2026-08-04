"""
Eksperimen framing LSTM yang diperbaiki -- TERPISAH dari pipeline utama
(audit/source_fixed/bs_tf_lstm_fix_fixed.py), yang sengaja TIDAK diubah supaya
hasil skripsi versi asli tetap utuh sebagai pembanding.

Latar belakang (lihat audit/results/dataset_v3_findings.md dan
audit/results/framing_findings.md): pada dataset V3, kolom Produksi adalah
fungsi deterministik dari Kapasitas dan Cuaca --

    Produksi_bulan = Kapasitas x CF x 8760 x (Cuaca_bulan / SUM Cuaca_tahun)

dengan CF tetap per kategori. Pipeline utama meminta model menebak Produksi di
bulan t hanya dari lag t-6..t-1, sehingga dua kolom yang menentukan jawabannya
justru dipotong tepat sebelum bulan target.

Script ini menguji lima perbaikan yang sah secara metodologis:

  1. Target diganti dari GWh ke CAPACITY FACTOR (Produksi/Kapasitas). Ini
     membuat skala nasional dan regional sebanding (mengatasi dugaan negative
     transfer) sekaligus menghapus lompatan level 2025 yang sebenarnya hanya
     kenaikan kapasitas terpasang.
  3. Benchmark diganti ke SEASONAL NAIVE (lag-12), bukan lag-1 -- benchmark
     yang pantas untuk data bulanan musiman.
  4. Satu model POOLED untuk 3 kategori + category embedding, bukan 3 model
     terpisah -- sample latih efektif naik dari 24 ke 72 titik.
  5. WALK-FORWARD (rolling-origin) validation untuk memilih konfigurasi,
     bukan satu split 85/15 dari 18 sequence.

Perbaikan (2) -- memberi model Cuaca di bulan target sebagai input eksogen --
dijalankan sebagai VARIAN TERPISAH dan sengaja tidak dicampur ke hasil utama.
Lihat peringatan di bagian VARIAN B di bawah: sebagian besar performanya adalah
artefak konstruksi dataset, bukan kemampuan prediksi.

Aturan yang dipegang script ini:
  - Data uji 2025 TIDAK PERNAH menyentuh pemilihan konfigurasi maupun fit
    scaler. Pemilihan model murni dari skor walk-forward pada 2023-2024.
  - Seluruh metrik dilaporkan kembali dalam satuan GWh (CF x Kapasitas) supaya
    sebanding langsung dengan eval_summary.csv dan baseline_comparison.csv.

Output: audit/results/experiment_improved/
"""
import os
import warnings

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import tensorflow as tf
from tensorflow.keras.layers import (
    LSTM, Dense, Dropout, Input, Embedding, Flatten, Concatenate,
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

AUDIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(AUDIT_DIR, "source")
OUT_DIR = os.path.join(AUDIT_DIR, "results", "experiment_improved")
os.makedirs(OUT_DIR, exist_ok=True)

REGIONAL_CSV = os.path.join(SOURCE_DIR, "DATA_REGIONAL_DISAGREGASI_V3.csv")
NASIONAL_CSV = os.path.join(SOURCE_DIR, "DATA_NASIONAL_DISAGREGASI_V2.csv")

KATEGORI = ["Hydro", "Solar", "Wind"]
IDX_KATEGORI = {k: i for i, k in enumerate(KATEGORI)}

# Batas periode -- identik dengan pipeline utama supaya hasilnya sebanding.
TAHUN_AKHIR_TRAIN_NASIONAL = 2021
TAHUN_VALIDASI_NASIONAL = (2022, 2023)
TAHUN_AKHIR_TRAIN_REGIONAL = 2024
TAHUN_TEST_REGIONAL = 2025

# Kandidat konfigurasi untuk walk-forward. Sengaja sedikit: data latih regional
# hanya 24 titik, grid besar justru mengundang overfit pada skor validasi.
KANDIDAT_KONFIG = [
    {"window": 3, "lr": 1e-3, "dropout": 0.2},
    {"window": 3, "lr": 1e-4, "dropout": 0.2},
    {"window": 6, "lr": 1e-3, "dropout": 0.2},
    {"window": 6, "lr": 1e-4, "dropout": 0.2},
]

EPOCHS_PRETRAIN = 200
EPOCHS_FINETUNE = 200
BATCH_SIZE = 8


# ----------------------------------------------------------------------------
# Metrik -- formula identik dengan hitung_mape() di pipeline utama.
# ----------------------------------------------------------------------------
def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def mape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def metrik(y_true, y_pred):
    return {"RMSE": rmse(y_true, y_pred), "MAE": mae(y_true, y_pred),
            "MAPE": mape(y_true, y_pred)}


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def muat(path):
    df = pd.read_csv(path)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df = df[df["Jenis"].isin(KATEGORI)].copy()
    df["Tahun"] = df["Tanggal"].dt.year
    # [PERBAIKAN 1] Target = capacity factor, bukan GWh mentah.
    df["CF"] = df["Produksi"] / df["Kapasitas"]
    return df.sort_values(["Jenis", "Tanggal"]).reset_index(drop=True)


def buat_sequence(df, window, kolom_fitur=("Cuaca_s", "CF_s")):
    """Sliding window per kategori.

    Mengembalikan dict of arrays. `exog` adalah nilai fitur di BULAN TARGET
    (t), dipakai hanya oleh varian B; varian A mengabaikannya sepenuhnya.
    """
    X, y, kat, tanggal, kapasitas, exog = [], [], [], [], [], []
    for k in KATEGORI:
        s = df[df["Jenis"] == k].reset_index(drop=True)
        arr = s[list(kolom_fitur)].values
        for i in range(len(s) - window):
            X.append(arr[i:i + window])
            y.append(s["CF_s"].iloc[i + window])
            kat.append(IDX_KATEGORI[k])
            tanggal.append(s["Tanggal"].iloc[i + window])
            kapasitas.append(s["Kapasitas"].iloc[i + window])
            exog.append([s["Cuaca_s"].iloc[i + window]])
    return {
        "X": np.array(X, dtype="float32"),
        "y": np.array(y, dtype="float32"),
        "kat": np.array(kat, dtype="int32"),
        "tanggal": pd.to_datetime(pd.Series(tanggal)),
        "kapasitas": np.array(kapasitas, dtype="float64"),
        "exog": np.array(exog, dtype="float32"),
    }


def skala(df_fit, df_apply_list):
    """Fit skala HANYA dari df_fit, terapkan ke seluruh df di df_apply_list.

    Cuaca diskalakan per kategori (satuannya beda-beda: mm, kWh/m2, m/s).
    CF diskalakan global -- justru itu gunanya memakai capacity factor, supaya
    ketiga kategori (dan nasional vs regional) hidup di rentang yang sebanding.
    """
    par_cuaca = {
        k: (df_fit.loc[df_fit["Jenis"] == k, "Cuaca"].min(),
            df_fit.loc[df_fit["Jenis"] == k, "Cuaca"].max())
        for k in KATEGORI
    }
    cf_lo, cf_hi = df_fit["CF"].min(), df_fit["CF"].max()

    hasil = []
    for df in df_apply_list:
        d = df.copy()
        lo = d["Jenis"].map(lambda k: par_cuaca[k][0])
        hi = d["Jenis"].map(lambda k: par_cuaca[k][1])
        d["Cuaca_s"] = (d["Cuaca"] - lo) / (hi - lo).replace(0, 1)
        d["CF_s"] = (d["CF"] - cf_lo) / (cf_hi - cf_lo if cf_hi > cf_lo else 1)
        hasil.append(d)
    return hasil, (cf_lo, cf_hi)


def cf_asli(cf_scaled, par):
    lo, hi = par
    return np.asarray(cf_scaled) * (hi - lo) + lo


# ----------------------------------------------------------------------------
# Model: LSTM pooled + category embedding
# ----------------------------------------------------------------------------
def bangun_model(window, n_fitur, dropout, lr, pakai_exog, n_exog=1):
    """[PERBAIKAN 4] Satu model untuk 3 kategori. Identitas kategori masuk
    lewat embedding, bukan lewat model terpisah -- sample latih efektif 3x
    lebih banyak, dan pola musiman yang sama-sama dimiliki ketiga kategori
    bisa saling meminjam kekuatan.

    Arsitektur LSTM (64 -> 32 -> Dense 1) dipertahankan sama dengan pipeline
    utama supaya perbandingannya soal FRAMING, bukan soal kapasitas model.
    """
    in_seq = Input(shape=(window, n_fitur), name="sekuens")
    in_kat = Input(shape=(1,), dtype="int32", name="kategori")

    x = LSTM(64, return_sequences=True)(in_seq)
    x = Dropout(dropout)(x)
    x = LSTM(32)(x)
    x = Dropout(dropout)(x)

    emb = Flatten()(Embedding(len(KATEGORI), 4, name="embed_kategori")(in_kat))

    inputs = [in_seq, in_kat]
    gabung = [x, emb]
    if pakai_exog:
        in_exog = Input(shape=(n_exog,), name="eksogen")
        inputs.append(in_exog)
        gabung.append(in_exog)

    h = Concatenate()(gabung)
    out = Dense(1)(h)

    model = Model(inputs=inputs, outputs=out)
    model.compile(optimizer=Adam(learning_rate=lr), loss="mse", metrics=["mae"])
    return model


def masukan(seq, idx, pakai_exog):
    x = [seq["X"][idx], seq["kat"][idx]]
    if pakai_exog:
        x.append(seq["exog"][idx])
    return x


# ----------------------------------------------------------------------------
# Benchmark [PERBAIKAN 3]
# ----------------------------------------------------------------------------
def benchmark(df_reg):
    """Baseline non-model pada data uji 2025, satuan GWh."""
    baris = []
    for k in KATEGORI:
        s = df_reg[df_reg["Jenis"] == k].sort_values("Tanggal").reset_index(drop=True)
        y25 = s.loc[s["Tahun"] == TAHUN_TEST_REGIONAL, "Produksi"].values
        y24 = s.loc[s["Tahun"] == 2024, "Produksi"].values
        kap24 = s.loc[s["Tahun"] == 2024, "Kapasitas"].iloc[0]
        kap25 = s.loc[s["Tahun"] == TAHUN_TEST_REGIONAL, "Kapasitas"].iloc[0]

        # Naive lag-1: prediksi bulan t = aktual bulan t-1 (menyeberangi batas tahun).
        seri = s.sort_values("Tanggal")["Produksi"].values
        n = len(y25)
        y_lag1 = seri[-n - 1:-1]

        kandidat = {
            "Naive_lag1": y_lag1,
            "SeasonalNaive_lag12": y24,
            "SeasonalNaive_x_rasio_kapasitas": y24 * kap25 / kap24,
        }
        for nama, pred in kandidat.items():
            baris.append({"Kategori": k, "Model": nama, **metrik(y25, pred)})
    return pd.DataFrame(baris)


# ----------------------------------------------------------------------------
# Walk-forward [PERBAIKAN 5]
# ----------------------------------------------------------------------------
def lipatan_walk_forward(tanggal_train, n_lipat=4, ukuran_val=3):
    """Rolling-origin: latih pada awal seri, validasi pada blok berikutnya,
    lalu majukan titik potongnya. Semua blok validasi tetap di dalam periode
    2023-2024 -- data 2025 tidak pernah ikut.

    Mengembalikan list (idx_train, idx_val) dalam urutan waktu.
    """
    urut = np.argsort(tanggal_train.values)
    n = len(urut)
    lipatan = []
    # Sisakan minimal setengah seri sebagai train pada lipatan pertama.
    mulai = max(ukuran_val, n - n_lipat * ukuran_val)
    for potong in range(mulai, n, ukuran_val):
        akhir = min(potong + ukuran_val, n)
        if akhir <= potong:
            break
        lipatan.append((urut[:potong], urut[potong:akhir]))
    return lipatan


def latih(model, seq, idx, pakai_exog, epochs, validasi=None, verbose=0):
    cb = [EarlyStopping(monitor="val_loss" if validasi is not None else "loss",
                        patience=25, restore_best_weights=True)]
    kwargs = {}
    if validasi is not None:
        kwargs["validation_data"] = (
            masukan(seq, validasi, pakai_exog), seq["y"][validasi]
        )
    model.fit(masukan(seq, idx, pakai_exog), seq["y"][idx],
              epochs=epochs, batch_size=BATCH_SIZE, callbacks=cb,
              verbose=verbose, **kwargs)
    return model


def prediksi_gwh(model, seq, idx, pakai_exog, par_cf):
    cf_pred = cf_asli(model.predict(masukan(seq, idx, pakai_exog), verbose=0).ravel(), par_cf)
    cf_true = cf_asli(seq["y"][idx], par_cf)
    kap = seq["kapasitas"][idx]
    return cf_true * kap, np.clip(cf_pred, 0, None) * kap


# ----------------------------------------------------------------------------
# Satu varian penuh (pretrain nasional -> walk-forward -> fine-tune -> test)
# ----------------------------------------------------------------------------
def jalankan_varian(nama_varian, pakai_exog, df_nas_raw, df_reg_raw):
    print(f"\n{'='*70}\nVARIAN {nama_varian} (input eksogen bulan-t: "
          f"{'YA' if pakai_exog else 'TIDAK'})\n{'='*70}")

    # Scaler di-fit HANYA dari periode train (nasional <=2021, regional <=2024).
    fit_src = pd.concat([
        df_nas_raw[df_nas_raw["Tahun"] <= TAHUN_AKHIR_TRAIN_NASIONAL],
        df_reg_raw[df_reg_raw["Tahun"] <= TAHUN_AKHIR_TRAIN_REGIONAL],
    ])
    (df_nas, df_reg), par_cf = skala(fit_src, [df_nas_raw, df_reg_raw])

    hasil_konfig, hasil_test = [], []
    model_terbaik = None

    for konfig in KANDIDAT_KONFIG:
        w = konfig["window"]
        seq_nas = buat_sequence(df_nas, w)
        seq_reg = buat_sequence(df_reg, w)

        m_nas_tr = seq_nas["tanggal"].dt.year <= TAHUN_AKHIR_TRAIN_NASIONAL
        m_nas_val = seq_nas["tanggal"].dt.year.isin(TAHUN_VALIDASI_NASIONAL)
        m_reg_tr = seq_reg["tanggal"].dt.year <= TAHUN_AKHIR_TRAIN_REGIONAL

        idx_nas_tr = np.where(m_nas_tr)[0]
        idx_nas_val = np.where(m_nas_val)[0]
        idx_reg_tr = np.where(m_reg_tr)[0]

        # --- Pre-training nasional (transfer learning tetap dipertahankan) ---
        tf.keras.utils.set_random_seed(SEED)
        m_pre = bangun_model(w, seq_nas["X"].shape[2], konfig["dropout"],
                             konfig["lr"], pakai_exog)
        latih(m_pre, seq_nas, idx_nas_tr, pakai_exog, EPOCHS_PRETRAIN,
              validasi=idx_nas_val)
        bobot_pretrain = m_pre.get_weights()

        # --- Walk-forward pada regional 2023-2024 ---
        tanggal_tr = seq_reg["tanggal"].iloc[idx_reg_tr]
        skor = []
        for f, (tr_lokal, val_lokal) in enumerate(lipatan_walk_forward(tanggal_tr)):
            idx_tr = idx_reg_tr[tr_lokal]
            idx_val = idx_reg_tr[val_lokal]
            tf.keras.utils.set_random_seed(SEED)
            m = bangun_model(w, seq_reg["X"].shape[2], konfig["dropout"],
                             konfig["lr"], pakai_exog)
            m.set_weights(bobot_pretrain)
            latih(m, seq_reg, idx_tr, pakai_exog, EPOCHS_FINETUNE)
            yt, yp = prediksi_gwh(m, seq_reg, idx_val, pakai_exog, par_cf)
            skor.append(rmse(yt, yp))
        rmse_wf = float(np.mean(skor))
        hasil_konfig.append({
            "Varian": nama_varian, "Window": w, "LR": konfig["lr"],
            "Dropout": konfig["dropout"], "RMSE_WalkForward": rmse_wf,
            "Jumlah_Lipatan": len(skor),
        })
        print(f"  window={w} lr={konfig['lr']:.0e} -> RMSE walk-forward = {rmse_wf:.3f} "
              f"({len(skor)} lipatan)")

        if model_terbaik is None or rmse_wf < model_terbaik["rmse_wf"]:
            model_terbaik = {"konfig": konfig, "rmse_wf": rmse_wf,
                             "bobot": bobot_pretrain, "seq": seq_reg,
                             "idx_tr": idx_reg_tr, "w": w}

    # --- Fine-tune final dengan konfigurasi pemenang, lalu uji 2025 ---
    k = model_terbaik["konfig"]
    seq_reg = model_terbaik["seq"]
    print(f"\n  Konfigurasi terpilih (murni dari walk-forward, tanpa melihat 2025): "
          f"window={k['window']} lr={k['lr']:.0e} dropout={k['dropout']}")

    tf.keras.utils.set_random_seed(SEED)
    m_final = bangun_model(model_terbaik["w"], seq_reg["X"].shape[2],
                           k["dropout"], k["lr"], pakai_exog)
    m_final.set_weights(model_terbaik["bobot"])
    latih(m_final, seq_reg, model_terbaik["idx_tr"], pakai_exog, EPOCHS_FINETUNE)

    idx_test = np.where(seq_reg["tanggal"].dt.year == TAHUN_TEST_REGIONAL)[0]
    for kat in KATEGORI:
        sel = idx_test[seq_reg["kat"][idx_test] == IDX_KATEGORI[kat]]
        yt, yp = prediksi_gwh(m_final, seq_reg, sel, pakai_exog, par_cf)
        hasil_test.append({"Varian": nama_varian, "Kategori": kat,
                           "Model": f"LSTM_{nama_varian}", **metrik(yt, yp)})

    return pd.DataFrame(hasil_konfig), pd.DataFrame(hasil_test)


def main():
    df_nas = muat(NASIONAL_CSV)
    df_reg = muat(REGIONAL_CSV)

    print("=== Benchmark non-model (data uji 2025, satuan GWh) ===")
    df_bench = benchmark(df_reg)
    print(df_bench.to_string(index=False))

    konfig_a, test_a = jalankan_varian("A", False, df_nas, df_reg)
    konfig_b, test_b = jalankan_varian("B", True, df_nas, df_reg)

    df_konfig = pd.concat([konfig_a, konfig_b], ignore_index=True)
    df_test = pd.concat([test_a, test_b], ignore_index=True)

    df_bench.to_csv(os.path.join(OUT_DIR, "benchmark_2025.csv"), index=False)
    df_konfig.to_csv(os.path.join(OUT_DIR, "walkforward_konfig.csv"), index=False)
    df_test.to_csv(os.path.join(OUT_DIR, "hasil_test_2025.csv"), index=False)

    print("\n=== Hasil pada data uji 2025 (satuan GWh) ===")
    print(df_test.to_string(index=False))

    gabung = pd.concat([
        df_bench.assign(Varian="benchmark"),
        df_test,
    ], ignore_index=True)[["Kategori", "Model", "RMSE", "MAE", "MAPE"]]
    gabung = gabung.sort_values(["Kategori", "RMSE"]).reset_index(drop=True)
    gabung.to_csv(os.path.join(OUT_DIR, "ringkasan_semua_metode.csv"), index=False)

    print("\n=== Peringkat per kategori (RMSE terkecil) ===")
    print(gabung.to_string(index=False))

    print(f"\nOutput ditulis ke: {OUT_DIR}")
    print(
        "\nPERINGATAN VARIAN B: varian ini melihat Cuaca di bulan target. Karena "
        "kolom Produksi pada dataset ini DIBANGUN dari Cuaca dan Kapasitas, "
        "sebagian besar keunggulan varian B adalah artefak konstruksi dataset "
        "-- bukan bukti kemampuan prediksi. Jangan laporkan angkanya sebagai "
        "akurasi peramalan tanpa pengungkapan ini."
    )


if __name__ == "__main__":
    main()
