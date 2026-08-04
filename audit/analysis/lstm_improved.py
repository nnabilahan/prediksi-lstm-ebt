"""
Eksperimen framing LSTM -- TERPISAH dari pipeline utama
(audit/source_fixed/bs_tf_lstm_fix_fixed.py), yang sengaja TIDAK diubah supaya
hasil skripsi versi asli tetap utuh sebagai pembanding.

Latar belakang (lihat audit/results/framing_findings.md): pada dataset ini,
kolom Produksi adalah fungsi deterministik dari Kapasitas dan Cuaca --

    Produksi_bulan = Kapasitas x CF x 8760 x (Cuaca_bulan / SUM Cuaca_tahun)

dengan CF tetap per jenis PLT (PLTA/PLTM 5,256 · PLTB 4,380 · PLTS/PLTS Atap
1,752 GWh per MW per tahun). Untuk PLTA/PLTM proporsinya memakai rata-rata
bergerak 3 bulan dari Cuaca, untuk PLTB/PLTS/PLTS Atap memakai Cuaca langsung.

Pipeline utama meminta model menebak Produksi di bulan t hanya dari lag
t-w..t-1, sehingga dua kolom yang menentukan jawabannya dipotong tepat sebelum
bulan target. Script ini menguji apakah memperbaiki FRAMING -- bukan arsitektur
-- membuat LSTM kompetitif.

Perbaikan yang diuji (arsitektur LSTM 64->32->Dense 1 dipertahankan sama persis
dengan pipeline utama, supaya perbandingannya soal framing):

  1. Target diganti dari GWh ke CAPACITY FACTOR (Produksi/Kapasitas) --
     menyamakan skala nasional vs regional (mengatasi dugaan negative transfer)
     sekaligus menghapus lompatan level 2025 yang sebenarnya hanya kenaikan
     kapasitas terpasang.
  2. Benchmark ditambah SEASONAL NAIVE (lag-12) dan seasonal naive x rasio
     kapasitas -- benchmark yang pantas untuk data bulanan musiman.
  3. Satu model POOLED untuk seluruh jenis PLT + category embedding, bukan satu
     model per jenis -- sample latih efektif naik berlipat.
  4. WALK-FORWARD (rolling-origin) validation untuk memilih konfigurasi, bukan
     satu split 85/15 dari belasan sequence.
  5. Empat varian penanganan Cuaca dan musiman (lihat di bawah).
  7. SEED ENSEMBLING (N_SEED run per fine-tune, prediksi dirata-rata) --
     dipakai BAIK saat walk-forward MAUPUN saat model final. Ditambahkan
     setelah terlihat bahwa selektor walk-forward berisik: PLTS dan PLTS Atap
     adalah dua seri yang identik proporsional (Cuaca sama, rasio
     P/Kapasitas sama 1,752), tapi terpilih varian berbeda, dan kombinasi
     yang menang di PLTS punya jurang besar antara skor validasi dan skor
     test. Merata-ratakan beberapa seed menurunkan varians itu di kedua sisi
     -- yang diperbaiki SELEKTORNYA, bukan pilihannya.
  6. PEMILIHAN (varian, konfigurasi) TERBAIK PER JENIS PLT memakai skor
     walk-forward jenis PLT itu sendiri -- bukan satu pemenang global.
     Ditambahkan setelah varian D memperbaiki PLTA/PLTB/PLTM tapi justru
     memperburuk PLTS: skor global adalah rata-rata RMSE dalam satuan GWh,
     jadi didominasi PLTA (ratusan GWh) dan praktis mengabaikan PLTS
     (0,1 GWh). Polanya sama dengan `model_terbaik_per_plt` di pipeline utama.

VARIAN:
  A  Lag-only. Model hanya melihat Cuaca dan CF di t-w..t-1. Ini peramalan
     murni: tidak butuh informasi apa pun tentang bulan target.
  B  A + Cuaca bulan-t di-concat di lapisan Dense terakhir.
  C  Known-future covariate (NARX). Kanal Cuaca digeser sehingga jendela
     memuat Cuaca_{t-w+1..t}, sementara kanal CF tetap CF_{t-w..t-1}. Ini
     bentuk standar peramalan EBT berbasis prakiraan cuaca.
  E  C + rasio cuaca relatif: Cuaca_t dibagi rata-rata 12 bulan terakhir
     (kausal: hanya memakai bulan t dan sebelumnya). Ditambahkan karena
     CF_bulan = CF_tahunan x Cuaca_bulan / SUM Cuaca_tahun, sehingga rasio
     "cuaca bulan ini terhadap rata-rata setahun terakhir" praktis SUDAH
     merupakan bentuk normalisasi yang menentukan CF. Fitur ini tidak
     menambah sumber informasi baru di luar yang sudah dilihat varian C --
     hanya membuat hubungannya jauh lebih mudah dipelajari.
  F  E + encoding bulan.
  D  C + encoding bulan (sin/cos dari bulan target). Ditambahkan setelah
     varian C ternyata masih kalah dari seasonal naive di PLTS/PLTS Atap --
     pemenangnya metode MUSIMAN, tanda bahwa model belum diberi informasi
     posisi bulan dalam setahun. Dengan window=3 model hanya melihat 3 bulan
     terakhir, jadi ia tidak punya cara mengetahui sedang di bulan apa.
     Encoding siklik memberikan informasi itu tanpa membuang satu baris pun
     data (berbeda dengan menambah fitur lag-12, yang akan memangkas periode
     latih regional dari 2023-2024 menjadi 2024 saja).

PERINGATAN untuk varian B dan C: keduanya melihat Cuaca di bulan target.
Karena kolom Produksi pada dataset ini DIBANGUN dari Cuaca dan Kapasitas,
sebagian keunggulannya adalah artefak konstruksi dataset, bukan bukti
kemampuan prediksi. Untuk dipakai sungguhan, Cuaca bulan target harus datang
dari PRAKIRAAN atau normal klimatologis -- bukan dari nilai aktual seperti di
eksperimen ini. Wajib diungkap di laporan.

Aturan yang dipegang script ini:
  - Data uji 2025 TIDAK PERNAH menyentuh pemilihan konfigurasi maupun fit
    scaler. Pemilihan konfigurasi murni dari skor walk-forward pada 2023-2024.
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

REGIONAL_CSV = os.path.join(SOURCE_DIR, "DATA_REGIONAL_5JENIS.csv")
NASIONAL_CSV = os.path.join(SOURCE_DIR, "DATA_NASIONAL_4JENIS.csv")

TAHUN_AKHIR_TRAIN_NASIONAL = 2021
TAHUN_VALIDASI_NASIONAL = (2022, 2023)
TAHUN_AKHIR_TRAIN_REGIONAL = 2024
TAHUN_TEST_REGIONAL = 2025

KANDIDAT_KONFIG = [
    {"window": 3, "lr": 1e-3, "dropout": 0.2},
    {"window": 3, "lr": 1e-4, "dropout": 0.2},
    {"window": 6, "lr": 1e-3, "dropout": 0.2},
    {"window": 6, "lr": 1e-4, "dropout": 0.2},
]

N_SEED = 3          # jumlah seed untuk ensembling fine-tune (lihat poin 7)
EPOCHS_PRETRAIN = 200
EPOCHS_FINETUNE = 200
BATCH_SIZE = 8

# Varian -> (daftar fitur eksogen di lapisan Dense, geser kanal cuaca)
# Fitur eksogen yang tersedia: "cuaca_t", "bulan_sin", "bulan_cos".
VARIAN = {
    "A": ([], False),
    "B": (["cuaca_t"], False),
    "C": ([], True),
    "D": (["bulan_sin", "bulan_cos"], True),
    "E": (["cuaca_rel"], True),
    "F": (["cuaca_rel", "bulan_sin", "bulan_cos"], True),
}


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def mape(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    mask = y_true != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def metrik(y_true, y_pred):
    return {"RMSE": rmse(y_true, y_pred), "MAE": mae(y_true, y_pred),
            "MAPE": mape(y_true, y_pred)}


def muat(path):
    df = pd.read_csv(path)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Tahun"] = df["Tanggal"].dt.year
    df["CF"] = df["Produksi"] / df["Kapasitas"]
    df = df.sort_values(["Jenis", "Tanggal"]).reset_index(drop=True)
    # Rasio cuaca relatif: Cuaca_t / rata-rata 12 bulan terakhir (termasuk t).
    # KAUSAL -- tidak memakai satu pun nilai dari masa depan.
    df["Cuaca_rel"] = df.groupby("Jenis")["Cuaca"].transform(
        lambda x: x / x.rolling(12, min_periods=1).mean()
    )
    return df


def buat_sequence(df, window, idx_kategori, geser_cuaca):
    """Sliding window per jenis PLT.

    Kanal CF selalu berisi CF_{t-window..t-1} (lag murni). Kalau `geser_cuaca`
    aktif, kanal Cuaca digeser satu langkah ke depan sehingga jendela memuat
    Cuaca_{t-window+1..t} -- artinya nilai cuaca di BULAN TARGET ikut terlihat
    model (varian C). Kalau tidak, kanal Cuaca sejajar dengan CF.
    """
    X, y, kat, tanggal, kapasitas, exog = [], [], [], [], [], []
    kolom_exog = ["cuaca_t", "bulan_sin", "bulan_cos", "cuaca_rel"]
    for k, s in df.groupby("Jenis"):
        if k not in idx_kategori:
            continue
        s = s.sort_values("Tanggal").reset_index(drop=True)
        cuaca, cf = s["Cuaca_s"].values, s["CF_s"].values
        cuaca_rel = s["Cuaca_rel_s"].values
        for i in range(len(s) - window):
            t = i + window
            jendela_cuaca = cuaca[i + 1:t + 1] if geser_cuaca else cuaca[i:t]
            X.append(np.stack([jendela_cuaca, cf[i:t]], axis=1))
            y.append(cf[t])
            kat.append(idx_kategori[k])
            tanggal.append(s["Tanggal"].iloc[t])
            kapasitas.append(s["Kapasitas"].iloc[t])
            bulan = s["Tanggal"].iloc[t].month
            exog.append([
                cuaca[t],
                np.sin(2 * np.pi * bulan / 12),
                np.cos(2 * np.pi * bulan / 12),
                cuaca_rel[t],
            ])
    return {
        "X": np.array(X, dtype="float32"),
        "y": np.array(y, dtype="float32"),
        "kat": np.array(kat, dtype="int32"),
        "tanggal": pd.to_datetime(pd.Series(tanggal)),
        "kapasitas": np.array(kapasitas, dtype="float64"),
        "exog": np.array(exog, dtype="float32"),
        "kolom_exog": kolom_exog,
    }


def skala(df_fit, df_apply_list, kategori):
    """Fit skala HANYA dari df_fit (periode train), terapkan ke seluruh df.

    Cuaca diskalakan per jenis PLT (satuannya beda: mm, kWh/m2, m/s). CF
    diskalakan global -- justru itu gunanya memakai capacity factor, supaya
    seluruh jenis (dan nasional vs regional) hidup di rentang yang sebanding.
    """
    par = {}
    for k in kategori:
        sub = df_fit.loc[df_fit["Jenis"] == k, "Cuaca"]
        par[k] = (sub.min(), sub.max()) if len(sub) else (0.0, 1.0)
    par_rel = {}
    for k in kategori:
        sub = df_fit.loc[df_fit["Jenis"] == k, "Cuaca_rel"]
        par_rel[k] = (sub.min(), sub.max()) if len(sub) else (0.0, 1.0)
    cf_lo, cf_hi = df_fit["CF"].min(), df_fit["CF"].max()

    hasil = []
    for df in df_apply_list:
        d = df.copy()
        lo = d["Jenis"].map(lambda k: par.get(k, (0.0, 1.0))[0])
        hi = d["Jenis"].map(lambda k: par.get(k, (0.0, 1.0))[1])
        rentang = (hi - lo).replace(0, 1)
        d["Cuaca_s"] = (d["Cuaca"] - lo) / rentang
        rlo = d["Jenis"].map(lambda k: par_rel.get(k, (0.0, 1.0))[0])
        rhi = d["Jenis"].map(lambda k: par_rel.get(k, (0.0, 1.0))[1])
        d["Cuaca_rel_s"] = (d["Cuaca_rel"] - rlo) / (rhi - rlo).replace(0, 1)
        d["CF_s"] = (d["CF"] - cf_lo) / (cf_hi - cf_lo if cf_hi > cf_lo else 1)
        hasil.append(d)
    return hasil, (cf_lo, cf_hi)


def cf_asli(cf_scaled, par):
    lo, hi = par
    return np.asarray(cf_scaled) * (hi - lo) + lo


def bangun_model(window, n_fitur, dropout, lr, n_kategori, n_exog):
    """Satu model pooled untuk seluruh jenis PLT; identitas jenis masuk lewat
    embedding. Arsitektur LSTM identik dengan pipeline utama (64 -> 32 ->
    Dense 1) supaya perbandingannya soal framing, bukan kapasitas model."""
    in_seq = Input(shape=(window, n_fitur), name="sekuens")
    in_kat = Input(shape=(1,), dtype="int32", name="kategori")

    x = LSTM(64, return_sequences=True)(in_seq)
    x = Dropout(dropout)(x)
    x = LSTM(32)(x)
    x = Dropout(dropout)(x)

    emb = Flatten()(Embedding(n_kategori, 4, name="embed_kategori")(in_kat))

    inputs, gabung = [in_seq, in_kat], [x, emb]
    if n_exog:
        in_exog = Input(shape=(n_exog,), name="eksogen")
        inputs.append(in_exog)
        gabung.append(in_exog)

    out = Dense(1)(Concatenate()(gabung))
    model = Model(inputs=inputs, outputs=out)
    model.compile(optimizer=Adam(learning_rate=lr), loss="mse", metrics=["mae"])
    return model


def masukan(seq, idx, fitur_exog):
    x = [seq["X"][idx], seq["kat"][idx]]
    if fitur_exog:
        kol = [seq["kolom_exog"].index(f) for f in fitur_exog]
        x.append(seq["exog"][idx][:, kol])
    return x


def benchmark(df_reg, kategori):
    baris = []
    for k in kategori:
        s = df_reg[df_reg["Jenis"] == k].sort_values("Tanggal").reset_index(drop=True)
        y25 = s.loc[s["Tahun"] == TAHUN_TEST_REGIONAL, "Produksi"].values
        y24 = s.loc[s["Tahun"] == 2024, "Produksi"].values
        kap24 = s.loc[s["Tahun"] == 2024, "Kapasitas"].iloc[0]
        kap25 = s.loc[s["Tahun"] == TAHUN_TEST_REGIONAL, "Kapasitas"].iloc[0]
        seri = s["Produksi"].values
        n = len(y25)
        for nama, pred in {
            "Naive_lag1": seri[-n - 1:-1],
            "SeasonalNaive_lag12": y24,
            "SeasonalNaive_x_rasio_kapasitas": y24 * kap25 / kap24,
        }.items():
            baris.append({"Kategori": k, "Model": nama, **metrik(y25, pred)})
    return pd.DataFrame(baris)


def lipatan_walk_forward(tanggal_train, n_lipat=4, ukuran_val=3):
    """Rolling-origin: latih pada awal seri, validasi pada blok berikutnya,
    lalu majukan titik potongnya. Semua blok validasi tetap di dalam periode
    2023-2024 -- data 2025 tidak pernah ikut."""
    urut = np.argsort(tanggal_train.values)
    n = len(urut)
    lipatan = []
    mulai = max(ukuran_val, n - n_lipat * ukuran_val)
    for potong in range(mulai, n, ukuran_val):
        akhir = min(potong + ukuran_val, n)
        if akhir > potong:
            lipatan.append((urut[:potong], urut[potong:akhir]))
    return lipatan


def latih(model, seq, idx, fitur_exog, epochs, validasi=None):
    cb = [EarlyStopping(monitor="val_loss" if validasi is not None else "loss",
                        patience=25, restore_best_weights=True)]
    kwargs = {}
    if validasi is not None:
        kwargs["validation_data"] = (masukan(seq, validasi, fitur_exog),
                                     seq["y"][validasi])
    model.fit(masukan(seq, idx, fitur_exog), seq["y"][idx], epochs=epochs,
              batch_size=BATCH_SIZE, callbacks=cb, verbose=0, **kwargs)
    return model


def prediksi_gwh(model, seq, idx, fitur_exog, par_cf):
    cf_pred = cf_asli(model.predict(masukan(seq, idx, fitur_exog),
                                    verbose=0).ravel(), par_cf)
    cf_true = cf_asli(seq["y"][idx], par_cf)
    kap = seq["kapasitas"][idx]
    return cf_true * kap, np.clip(cf_pred, 0, None) * kap


def latih_ensemble(seq, idx_train, fitur_exog, window, konfig, kategori,
                   bobot_awal):
    """Latih N_SEED model dengan seed berbeda dari bobot pre-training yang
    sama. Dilatih SEKALI per fold/tahap, lalu dipakai untuk seluruh jenis PLT
    -- bukan dilatih ulang per jenis."""
    model = []
    for k_seed in range(N_SEED):
        tf.keras.utils.set_random_seed(SEED + k_seed)
        m = bangun_model(window, seq["X"].shape[2], konfig["dropout"],
                         konfig["lr"], len(kategori), len(fitur_exog))
        m.set_weights(bobot_awal)
        latih(m, seq, idx_train, fitur_exog, EPOCHS_FINETUNE)
        model.append(m)
    return model


def prediksi_ensemble(model_list, seq, idx_eval, fitur_exog, par_cf):
    """Rata-ratakan prediksi seluruh model ensemble. Dipakai di walk-forward
    MAUPUN model final, supaya skor validasi dan skor test berasal dari
    prosedur yang identik."""
    kumpulan = []
    for m in model_list:
        yt, yp = prediksi_gwh(m, seq, idx_eval, fitur_exog, par_cf)
        kumpulan.append(yp)
    return yt, np.mean(kumpulan, axis=0)


def jalankan_kombinasi(nama, konfig, df_nas, df_reg, kategori, idx_kategori,
                       par_cf):
    """Latih satu kombinasi (varian, konfigurasi) dan kembalikan:
      - skor walk-forward PER JENIS PLT (dipakai untuk memilih model)
      - metrik test 2025 PER JENIS PLT (hanya dilaporkan, tidak pernah dipakai
        untuk memilih apa pun)
    """
    fitur_exog, geser = VARIAN[nama]
    w = konfig["window"]

    seq_nas = buat_sequence(df_nas, w, idx_kategori, geser)
    seq_reg = buat_sequence(df_reg, w, idx_kategori, geser)

    idx_nas_tr = np.where(seq_nas["tanggal"].dt.year <= TAHUN_AKHIR_TRAIN_NASIONAL)[0]
    idx_nas_val = np.where(seq_nas["tanggal"].dt.year.isin(TAHUN_VALIDASI_NASIONAL))[0]
    idx_reg_tr = np.where(seq_reg["tanggal"].dt.year <= TAHUN_AKHIR_TRAIN_REGIONAL)[0]

    # Pre-training nasional. Jenis PLT yang tidak ada di dataset nasional
    # (PLTS Atap) tidak ikut di sini -- baris embedding-nya baru terlatih saat
    # fine-tuning regional, setara jalur Direct Training di pipeline utama.
    tf.keras.utils.set_random_seed(SEED)
    m_pre = bangun_model(w, seq_nas["X"].shape[2], konfig["dropout"],
                         konfig["lr"], len(kategori), len(fitur_exog))
    latih(m_pre, seq_nas, idx_nas_tr, fitur_exog, EPOCHS_PRETRAIN,
          validasi=idx_nas_val)
    bobot = m_pre.get_weights()

    # --- Walk-forward: kumpulkan galat per jenis PLT lintas lipatan ---
    galat = {k: [] for k in kategori}
    for tr_lokal, val_lokal in lipatan_walk_forward(seq_reg["tanggal"].iloc[idx_reg_tr]):
        ens = latih_ensemble(seq_reg, idx_reg_tr[tr_lokal], fitur_exog, w,
                             konfig, kategori, bobot)
        idx_val = idx_reg_tr[val_lokal]
        for kat in kategori:
            sel = idx_val[seq_reg["kat"][idx_val] == idx_kategori[kat]]
            if not len(sel):
                continue
            yt, yp = prediksi_ensemble(ens, seq_reg, sel, fitur_exog, par_cf)
            galat[kat].extend(np.asarray(yt) - np.asarray(yp))
    wf = {k: (float(np.sqrt(np.mean(np.square(v)))) if len(v) else float("inf"))
          for k, v in galat.items()}

    # --- Model final: fine-tune pada seluruh 2023-2024, lalu uji pada 2025 ---
    ens_final = latih_ensemble(seq_reg, idx_reg_tr, fitur_exog, w, konfig,
                               kategori, bobot)
    idx_test = np.where(seq_reg["tanggal"].dt.year == TAHUN_TEST_REGIONAL)[0]
    test = {}
    for kat in kategori:
        sel = idx_test[seq_reg["kat"][idx_test] == idx_kategori[kat]]
        if len(sel):
            yt, yp = prediksi_ensemble(ens_final, seq_reg, sel, fitur_exog, par_cf)
            test[kat] = metrik(yt, yp)

    return wf, test


def main():
    df_nas_raw, df_reg_raw = muat(NASIONAL_CSV), muat(REGIONAL_CSV)
    kategori = sorted(df_reg_raw["Jenis"].unique())
    idx_kategori = {k: i for i, k in enumerate(kategori)}
    print(f"Jenis PLT regional : {kategori}")
    print(f"Jenis PLT nasional : {sorted(df_nas_raw['Jenis'].unique())}")

    print("\n=== Benchmark non-model (data uji 2025, satuan GWh) ===")
    df_bench = benchmark(df_reg_raw, kategori)
    print(df_bench.to_string(index=False))

    # Scaler di-fit HANYA dari periode train (nasional <=2021, regional <=2024).
    fit_src = pd.concat([
        df_nas_raw[df_nas_raw["Tahun"] <= TAHUN_AKHIR_TRAIN_NASIONAL],
        df_reg_raw[df_reg_raw["Tahun"] <= TAHUN_AKHIR_TRAIN_REGIONAL],
    ])
    (df_nas, df_reg), par_cf = skala(fit_src, [df_nas_raw, df_reg_raw], kategori)

    baris_wf, baris_test = [], []
    for nama in VARIAN:
        fitur_exog, geser = VARIAN[nama]
        garis = "=" * 74
        print(f"\n{garis}\nVARIAN {nama} "
              f"(exog: {fitur_exog or 'tidak ada'} | kanal cuaca digeser: {geser})"
              f"\n{garis}")
        for konfig in KANDIDAT_KONFIG:
            wf, test = jalankan_kombinasi(nama, konfig, df_nas, df_reg,
                                          kategori, idx_kategori, par_cf)
            tag = "window={} lr={:.0e}".format(konfig["window"], konfig["lr"])
            rincian = "  ".join("{}={:.3f}".format(k, wf[k]) for k in kategori)
            print(f"  {tag:22s} RMSE walk-forward -> {rincian}")
            for k in kategori:
                baris_wf.append({"Varian": nama, "Window": konfig["window"],
                                 "LR": konfig["lr"], "Kategori": k,
                                 "RMSE_WalkForward": wf[k]})
                if k in test:
                    baris_test.append({"Varian": nama, "Window": konfig["window"],
                                       "LR": konfig["lr"], "Kategori": k,
                                       **test[k]})

    df_wf = pd.DataFrame(baris_wf)
    df_test = pd.DataFrame(baris_test)
    df_wf.to_csv(os.path.join(OUT_DIR, "walkforward_per_kategori.csv"), index=False)
    df_test.to_csv(os.path.join(OUT_DIR, "hasil_test_semua_kombinasi.csv"), index=False)

    # --- Pemilihan model terbaik PER JENIS PLT, murni dari skor walk-forward ---
    kunci = ["Varian", "Window", "LR", "Kategori"]
    terpilih = df_wf.loc[df_wf.groupby("Kategori")["RMSE_WalkForward"].idxmin()]
    hasil = terpilih.merge(df_test, on=kunci, how="left")
    hasil = hasil[["Kategori", "Varian", "Window", "LR", "RMSE_WalkForward",
                   "RMSE", "MAE", "MAPE"]]
    hasil.to_csv(os.path.join(OUT_DIR, "model_terbaik_per_plt.csv"), index=False)

    print("\n=== Model LSTM terbaik per jenis PLT "
          "(dipilih dari skor walk-forward, TANPA melihat 2025) ===")
    print(hasil.to_string(index=False))

    lstm_terpilih = hasil.assign(
        Model=lambda d: "LSTM_terbaik(" + d["Varian"] + ")"
    )[["Kategori", "Model", "RMSE", "MAE", "MAPE"]]

    # Hasil terbaik tiap varian, untuk tabel perbandingan antar-varian.
    per_varian = (df_test.sort_values("RMSE")
                  .groupby(["Kategori", "Varian"], as_index=False).first())
    per_varian["Model"] = "LSTM_" + per_varian["Varian"]
    per_varian[["Kategori", "Model", "RMSE", "MAE", "MAPE"]].to_csv(
        os.path.join(OUT_DIR, "perbandingan_antar_varian.csv"), index=False)

    gabung = pd.concat([
        df_bench[["Kategori", "Model", "RMSE", "MAE", "MAPE"]],
        lstm_terpilih,
    ], ignore_index=True).sort_values(["Kategori", "RMSE"]).reset_index(drop=True)
    gabung.to_csv(os.path.join(OUT_DIR, "ringkasan_semua_metode.csv"), index=False)

    print("\n=== Peringkat akhir per jenis PLT (RMSE terkecil) ===")
    print(gabung.to_string(index=False))

    print("\n=== Pemenang per jenis PLT ===")
    menang = 0
    for kat, g in gabung.groupby("Kategori"):
        b = g.loc[g["RMSE"].idxmin()]
        if str(b["Model"]).startswith("LSTM"):
            menang += 1
        print(f"  {kat:11s} -> {b['Model']:26s} (RMSE={b['RMSE']:.4f})")
    print(f"\n  LSTM unggul di {menang} dari {gabung['Kategori'].nunique()} jenis PLT.")

    print(f"\nOutput ditulis ke: {OUT_DIR}")
    print(
        "\nPERINGATAN VARIAN B, C, D: ketiganya melihat Cuaca di bulan target. Karena "
        "kolom Produksi pada dataset ini DIBANGUN dari Cuaca dan Kapasitas, sebagian "
        "keunggulannya adalah artefak konstruksi dataset. Untuk dipakai sungguhan, "
        "Cuaca bulan target harus berasal dari PRAKIRAAN atau normal klimatologis, "
        "bukan nilai aktual seperti di eksperimen ini. Varian A bebas dari catatan ini "
        "-- ia tidak memakai informasi apa pun tentang bulan target."
    )


if __name__ == "__main__":
    main()
