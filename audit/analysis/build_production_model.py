"""
Melatih dan menyimpan model final yang DIPAKAI BACKEND (production), memakai
kombinasi (varian, window, learning_rate) pemenang per jenis PLT dari
audit/analysis/lstm_improved.py -- lihat audit/results/framing_findings.md
dan audit/results/experiment_improved/model_terbaik_per_plt.csv untuk hasil
selengkapnya.

KENAPA SKRIP TERPISAH, BUKAN MENYUNTIK ke bs_tf_lstm_fix_fixed.py:
File itu sengaja disusun meniru notebook Colab asli (tahap Baseline ->
Pre-Training -> Fine-Tuning -> Iterasi 1-3 -> Model Final, ~3700 baris) untuk
menjaga alur audit-trail yang sudah didokumentasikan di
audit/results/audit_findings.md dan dataset_v3_findings.md. Menyuntikkan
arsitektur pooled+embedding+walk-forward+ensembling ke tengah file sebesar
itu berisiko tinggi (salah sambung, sulit dilacak) dan mengaburkan cerita
"pendekatan konvensional vs pendekatan yang diperbaiki" yang justru penting
untuk BAB IV. bs_tf_lstm_fix_fixed.py TETAP DIPERTAHANKAN apa adanya sebagai
bukti audit itu.

Skrip ini yang menghasilkan artefak SUNGGUHAN dipakai backend (models/,
scalers/, config/, evaluation/) -- menggantikan peran folder
pipeline_run_v4/EBT_LSTM_Streamlit/ sebelumnya.

KOMBINASI PEMENANG (dipilih murni dari skor walk-forward pada 2023-2024,
TIDAK PERNAH melihat data uji 2025 -- lihat model_terbaik_per_plt.csv):
  PLTA             -> Varian B, window=3, lr=0.001
  PLTB             -> Varian B, window=6, lr=0.001
  PLTM             -> Varian B, window=3, lr=0.0001
  PLTS, PLTS Atap  -> Varian C, window=3, lr=0.001   (kombinasi sama -> 1 model)

PLTS dan PLTS Atap KALAH dari seasonal-naive x rasio kapasitas pada data uji
2025 (lihat evaluation/evaluasi_final.csv yang ditulis skrip ini) -- ini
TETAP disimpan dan dipakai backend apa adanya, BUKAN ditukar ke kombinasi
lain yang skor test-nya kebetulan lebih bagus. Menukar berdasarkan skor test
adalah data leakage yang sama persis dengan yang sudah diperbaiki di audit
sebelumnya (lihat audit_findings.md).

PERINGATAN PRODUKSI -- WAJIB DIBACA sebelum memakai endpoint /api/predict:
Varian B dan C adalah model "known-future covariate": mereka butuh nilai
CUACA BULAN YANG DITEBAK sebagai input (bukan cuma histori). Di eksperimen
ini nilai itu diambil dari data aktual (karena mengevaluasi masa lalu), tapi
untuk prediksi produksi sungguhan, nilai itu HARUS berasal dari PRAKIRAAN
cuaca (mis. BMKG/normal klimatologis bulan tsb), bukan observasi -- observasi
bulan depan belum ada. Endpoint /api/predict & form Prediksi.jsx diperbarui
untuk meminta input ini secara eksplisit (field `cuaca_target`), disertai
keterangan bahwa ini adalah perkiraan, bukan data historis.

Output: audit/results/production_model/
  models/{combo_id}_seed{k}.keras
  scalers/scaler_params.json
  config/konfigurasi_model.json
  evaluation/evaluasi_final.csv
"""
import json
import os
import sys

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np
import pandas as pd
import tensorflow as tf

ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ANALYSIS_DIR)
import lstm_improved as li  # noqa: E402  (reuse fitur/scaler/model logic -- satu sumber kebenaran)

AUDIT_DIR = os.path.dirname(ANALYSIS_DIR)
OUT_DIR = os.path.join(AUDIT_DIR, "results", "production_model")
MODELS_DIR = os.path.join(OUT_DIR, "models")
SCALERS_DIR = os.path.join(OUT_DIR, "scalers")
CONFIG_DIR = os.path.join(OUT_DIR, "config")
EVAL_DIR = os.path.join(OUT_DIR, "evaluation")
for d in (MODELS_DIR, SCALERS_DIR, CONFIG_DIR, EVAL_DIR):
    os.makedirs(d, exist_ok=True)

# Kombinasi pemenang per jenis PLT -- disalin dari
# audit/results/experiment_improved/model_terbaik_per_plt.csv (hasil setelah
# ensembling N_SEED=3, lihat header file ini).
PEMENANG = {
    "PLTA": {"varian": "B", "window": 3, "lr": 0.001},
    "PLTB": {"varian": "B", "window": 6, "lr": 0.001},
    "PLTM": {"varian": "B", "window": 3, "lr": 0.0001},
    "PLTS": {"varian": "C", "window": 3, "lr": 0.001},
    "PLTS Atap": {"varian": "C", "window": 3, "lr": 0.001},
}

DROPOUT = 0.2  # sama untuk seluruh KANDIDAT_KONFIG di lstm_improved.py


def combo_id(v):
    return f"{v['varian']}_w{v['window']}_lr{v['lr']:.0e}".replace("+", "").replace("-0", "-")


def main():
    df_nas_raw, df_reg_raw = li.muat(li.NASIONAL_CSV), li.muat(li.REGIONAL_CSV)
    kategori = sorted(df_reg_raw["Jenis"].unique())
    idx_kategori = {k: i for i, k in enumerate(kategori)}
    print(f"Jenis PLT regional : {kategori}")

    fit_src = pd.concat([
        df_nas_raw[df_nas_raw["Tahun"] <= li.TAHUN_AKHIR_TRAIN_NASIONAL],
        df_reg_raw[df_reg_raw["Tahun"] <= li.TAHUN_AKHIR_TRAIN_REGIONAL],
    ])
    (df_nas, df_reg), par_cf = li.skala(fit_src, [df_nas_raw, df_reg_raw], kategori)

    # --- Kelompokkan jenis PLT berdasarkan kombinasi yang sama (hemat model) ---
    combo_ke_kategori = {}
    for plt, v in PEMENANG.items():
        cid = combo_id(v)
        combo_ke_kategori.setdefault(cid, {"info": v, "kategori": []})
        combo_ke_kategori[cid]["kategori"].append(plt)

    print(f"\n{len(combo_ke_kategori)} kombinasi unik untuk {len(PEMENANG)} jenis PLT:")
    for cid, g in combo_ke_kategori.items():
        print(f"  {cid:16s} -> {g['kategori']}")

    scaler_params = {
        "cf_min": float(par_cf[0]), "cf_max": float(par_cf[1]),
        "cuaca_per_kategori": {},
    }
    konfigurasi = {}
    baris_eval = []

    for cid, g in combo_ke_kategori.items():
        v = g["info"]
        konfig = {"window": v["window"], "lr": v["lr"], "dropout": DROPOUT}
        fitur_exog, geser = li.VARIAN[v["varian"]]
        w = konfig["window"]
        print(f"\n{'='*72}\nMelatih kombinasi {cid} untuk: {g['kategori']}\n{'='*72}")

        seq_nas = li.buat_sequence(df_nas, w, idx_kategori, geser)
        seq_reg = li.buat_sequence(df_reg, w, idx_kategori, geser)
        idx_nas_tr = np.where(seq_nas["tanggal"].dt.year <= li.TAHUN_AKHIR_TRAIN_NASIONAL)[0]
        idx_nas_val = np.where(seq_nas["tanggal"].dt.year.isin(li.TAHUN_VALIDASI_NASIONAL))[0]
        idx_reg_tr = np.where(seq_reg["tanggal"].dt.year <= li.TAHUN_AKHIR_TRAIN_REGIONAL)[0]
        idx_test = np.where(seq_reg["tanggal"].dt.year == li.TAHUN_TEST_REGIONAL)[0]

        # Pre-training nasional (sekali per kombinasi, dipakai sebagai bobot awal
        # ensembling -- identik dengan alur jalankan_kombinasi() di lstm_improved.py).
        tf.keras.utils.set_random_seed(li.SEED)
        m_pre = li.bangun_model(w, seq_nas["X"].shape[2], konfig["dropout"],
                                konfig["lr"], len(kategori), len(fitur_exog))
        li.latih(m_pre, seq_nas, idx_nas_tr, fitur_exog, li.EPOCHS_PRETRAIN,
                validasi=idx_nas_val)
        bobot = m_pre.get_weights()

        # Ensemble final: fine-tune pada SELURUH 2023-2024 (regional), N_SEED model.
        ensemble = li.latih_ensemble(seq_reg, idx_reg_tr, fitur_exog, w, konfig,
                                     kategori, bobot)

        for k_seed, m in enumerate(ensemble):
            path = os.path.join(MODELS_DIR, f"{cid}_seed{k_seed}.keras")
            m.save(path)
        print(f"  {len(ensemble)} model disimpan untuk kombinasi {cid}.")

        # Evaluasi pada data uji 2025 -- PER JENIS PLT dalam kombinasi ini.
        for plt in g["kategori"]:
            sel = idx_test[seq_reg["kat"][idx_test] == idx_kategori[plt]]
            yt, yp = li.prediksi_ensemble(ensemble, seq_reg, sel, fitur_exog, par_cf)
            m_ = li.metrik(yt, yp)
            baris_eval.append({
                "Jenis_PLT": plt, "Metode_Terpilih": f"Pooled+Ensemble({v['varian']})",
                "RMSE_Test_2025_Konfirmasi": m_["RMSE"],
                "MAE_Test_2025_Konfirmasi": m_["MAE"],
                "MAPE_Test_2025_Konfirmasi": m_["MAPE"],
            })
            print(f"  {plt:10s} -> RMSE={m_['RMSE']:.3f}  MAPE={m_['MAPE']:.2f}%")

            konfigurasi[plt] = {
                "combo_id": cid,
                "varian": v["varian"],
                "window_size": w,
                "fitur_exog": fitur_exog,
                "geser_cuaca": geser,
                "kategori_idx": idx_kategori[plt],
                "n_seed": len(ensemble),
                "fitur_input": ["Cuaca", "CF"],
                "target_prediksi": "Produksi",
            }

        # Rentang Cuaca per jenis PLT dalam kombinasi ini (dari fit_src, sama
        # dengan yang dipakai li.skala() -- disalin ulang di sini karena
        # li.skala() tidak mengembalikan par per-kategori secara terpisah).
        for plt in g["kategori"]:
            sub = fit_src.loc[fit_src["Jenis"] == plt, "Cuaca"]
            scaler_params["cuaca_per_kategori"][plt] = {
                "min": float(sub.min()), "max": float(sub.max()),
            }

    # --- Simpan scaler & konfigurasi ---
    with open(os.path.join(SCALERS_DIR, "scaler_params.json"), "w", encoding="utf-8") as f:
        json.dump(scaler_params, f, indent=2, ensure_ascii=False)

    with open(os.path.join(CONFIG_DIR, "konfigurasi_model.json"), "w", encoding="utf-8") as f:
        json.dump(konfigurasi, f, indent=2, ensure_ascii=False)

    df_eval = pd.DataFrame(baris_eval)
    df_eval.to_csv(os.path.join(EVAL_DIR, "evaluasi_final.csv"), index=False)

    print(f"\n=== Ringkasan evaluasi model produksi (data uji 2025) ===")
    print(df_eval.to_string(index=False))
    print(f"\nOutput ditulis ke: {OUT_DIR}")
    print(
        "\nPERINGATAN PRODUKSI: model PLTA/PLTB/PLTM/PLTS/PLTS Atap semuanya "
        "butuh input Cuaca BULAN YANG DITEBAK (bukan cuma histori). Backend "
        "(ml.py) dan form Prediksi.jsx WAJIB meminta nilai ini sebagai "
        "perkiraan/prakiraan, bukan observasi -- observasi bulan depan belum ada."
    )
    print(
        "\nCATATAN: PLTS dan PLTS Atap kalah dari seasonal-naive x rasio "
        "kapasitas pada data uji 2025 (lihat framing_findings.md). Model "
        "tetap disimpan & dipakai backend apa adanya -- TIDAK ditukar "
        "berdasarkan skor test."
    )


if __name__ == "__main__":
    main()
