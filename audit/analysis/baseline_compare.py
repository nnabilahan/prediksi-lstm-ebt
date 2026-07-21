"""
Baseline non-deep-learning (ARIMA & naive persistence) sebagai pembanding
klaim "LSTM lebih unggul dari metode tradisional" (Bab I skripsi).

Metodologi split & metrik dibuat SAMA PERSIS dengan tahap Fine-Tuning LSTM
di bs_tf_lstm_fix.py (baris 843-883, 1040-1055): dataset regional
(DATA_PHASE_3_REGIONAL_MODIFIED.csv), per PLT, target = Produksi,
train = 2023-2024, test = 2025 (tidak disentuh sampai evaluasi akhir),
metrik RMSE/MAE/MAPE dihitung dengan formula identik ke
`hitung_mape()` pada source pipeline (mask y_true != 0).

Model ARIMA order dipilih sederhana & tetap (1,1,1) per PLT -- bukan
auto-ARIMA/grid-search, karena data sangat pendek (test 2025 = 12 titik,
train 2023-2024 = 24 titik) sehingga tuning order berisiko overfit pada
data sekecil ini. Dicatat sebagai keterbatasan di laporan.

Output: audit/results/baseline_comparison.csv (LSTM Fine-Tuning vs ARIMA vs Naive)
"""
import os
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

AUDIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(AUDIT_DIR, "source", "DATA_PHASE_3_REGIONAL_MODIFIED.csv")
EVAL_SUMMARY_PATH = os.path.join(AUDIT_DIR, "results", "eval_summary.csv")
OUT_PATH = os.path.join(AUDIT_DIR, "results", "baseline_comparison.csv")

ARIMA_ORDER = (1, 1, 1)


def hitung_mape(y_true, y_pred):
    """Identik dengan hitung_mape() di bs_tf_lstm_fix.py."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2)))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))


def naive_forecast(train_series, test_series):
    """Naive persistence: prediksi bulan t = nilai aktual bulan t-1 (lag-1)."""
    combined = pd.concat([train_series, test_series])
    preds = combined.shift(1).iloc[-len(test_series):]
    return preds.values


def arima_forecast(train_series, n_periods):
    model = ARIMA(train_series.values, order=ARIMA_ORDER)
    fitted = model.fit()
    return fitted.forecast(steps=n_periods)


def main():
    df = pd.read_csv(DATA_PATH)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df = df.sort_values(["Jenis", "Tanggal"]).reset_index(drop=True)

    results = []
    for plt_name in df["Jenis"].unique():
        sub = df[df["Jenis"] == plt_name].sort_values("Tanggal").reset_index(drop=True)
        train = sub[sub["Tanggal"].dt.year <= 2024]["Produksi"].reset_index(drop=True)
        test = sub[sub["Tanggal"].dt.year == 2025]["Produksi"].reset_index(drop=True)

        if len(test) == 0 or len(train) < 4:
            print(f"[skip] {plt_name}: data tidak cukup (train={len(train)}, test={len(test)})")
            continue

        # --- Naive persistence ---
        y_pred_naive = naive_forecast(train, test)
        results.append({
            "PLT": plt_name, "Model": "Naive_Persistence",
            "RMSE": rmse(test, y_pred_naive), "MAE": mae(test, y_pred_naive),
            "MAPE": hitung_mape(test, y_pred_naive),
        })

        # --- ARIMA(1,1,1) ---
        try:
            y_pred_arima = arima_forecast(train, len(test))
            results.append({
                "PLT": plt_name, "Model": f"ARIMA{ARIMA_ORDER}",
                "RMSE": rmse(test, y_pred_arima), "MAE": mae(test, y_pred_arima),
                "MAPE": hitung_mape(test, y_pred_arima),
            })
        except Exception as exc:
            print(f"[gagal] ARIMA {plt_name}: {exc!r}")

        print(f"{plt_name:12s} -> train={len(train):2d} test={len(test):2d} selesai")

    baseline_df = pd.DataFrame(results)

    # --- Gabungkan dengan metrik LSTM Fine-Tuning yang sudah ada (eval_summary.csv) ---
    eval_summary = pd.read_csv(EVAL_SUMMARY_PATH)
    lstm_ft = eval_summary[eval_summary["Stage"] == "FineTuning"].copy()
    lstm_ft = lstm_ft.rename(columns={"PLT": "PLT"})[["PLT", "RMSE", "MAE", "MAPE"]]
    lstm_ft["Model"] = "LSTM_FineTuning"

    combined = pd.concat([
        lstm_ft[["PLT", "Model", "RMSE", "MAE", "MAPE"]],
        baseline_df[["PLT", "Model", "RMSE", "MAE", "MAPE"]],
    ], ignore_index=True)
    combined = combined.sort_values(["PLT", "Model"]).reset_index(drop=True)
    combined.to_csv(OUT_PATH, index=False)

    print("\n=== Perbandingan LSTM vs ARIMA vs Naive (test = tahun 2025) ===")
    print(combined.to_string(index=False))

    print("\n=== Ringkasan: siapa yang menang per PLT (RMSE terkecil) ===")
    for plt_name, grp in combined.groupby("PLT"):
        best = grp.loc[grp["RMSE"].idxmin()]
        print(f"{plt_name:12s} -> terbaik: {best['Model']:20s} (RMSE={best['RMSE']:.3f})")


if __name__ == "__main__":
    main()
