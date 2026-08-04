"""
Forecast 2026-2028 memakai MODEL PRODUKSI (pooled + category embedding +
ensembling, lihat audit/analysis/build_production_model.py) -- menggantikan
forecast_total_2026_2028.csv / forecast_per_PLT_2026_2028.csv lama yang
berasal dari pipeline_run_v4 (satu model per jenis PLT, tanpa ensembling).

ASUMSI YANG WAJIB DIUNGKAP DI LAPORAN (dua asumsi, keduanya baru dibanding
forecast lama):

1. CUACA = NORMAL KLIMATOLOGIS PER BULAN KALENDER, bukan prakiraan
   operasional. Model produksi butuh nilai Cuaca BULAN YANG DITEBAK sebagai
   input (lihat build_production_model.py, backend/ml.py). Untuk horizon 3
   tahun ke depan, prakiraan cuaca operasional (BMKG dsb) tidak tersedia --
   horizonnya jauh di luar jangkauan prakiraan musiman. Sebagai gantinya,
   dipakai RATA-RATA Cuaca per bulan kalender dari histori 2023-2025 (mis.
   Cuaca Januari = rata-rata Cuaca Januari 2023, 2024, 2025). Ini estimasi
   "cuaca normal", BUKAN prediksi cuaca sungguhan -- variabilitas antar-tahun
   (mis. anomali El Nino/La Nina) TIDAK tertangkap.
2. KAPASITAS = LOCF dari titik data terakhir (Desember 2025), dipertahankan
   tetap sampai Desember 2028. TIDAK memperhitungkan rencana penambahan
   kapasitas EBT Sulsel yang mungkin sudah ada di RUED/RUPTL -- kalau ada
   rencana penambahan kapasitas terverifikasi, forecast ini akan meremehkan
   produksi ke depan. Asumsi yang SAMA dipakai forecast_autoregressive() di
   pipeline lama (bs_tf_lstm_fix_fixed.py).

Forecast bersifat AUTOREGRESIF: prediksi bulan t dipakai sebagai bagian dari
input (CF lag) untuk memprediksi bulan t+1, dst. -- kesalahan bisa
terakumulasi sepanjang 36 bulan. Ini sebabnya akurasi forecast jangka panjang
TIDAK bisa disamakan dengan MAPE evaluasi 1-langkah (data uji 2025) yang
dilaporkan di evaluation/evaluasi_final.csv.

Output (schema identik dengan forecast lama, supaya export_dashboard_data.py
tidak perlu berubah selain path):
  audit/results/production_model/forecast/forecast_total_2026_2028.csv
  audit/results/production_model/forecast/forecast_per_PLT_2026_2028.csv
"""
import json
import os
import sys
from datetime import date

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np
import pandas as pd

ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ANALYSIS_DIR)
import lstm_improved as li  # noqa: E402  (reuse REGIONAL_CSV path & konstanta)

AUDIT_DIR = os.path.dirname(ANALYSIS_DIR)
PROD_DIR = os.path.join(AUDIT_DIR, "results", "production_model")
FORECAST_DIR = os.path.join(PROD_DIR, "forecast")
os.makedirs(FORECAST_DIR, exist_ok=True)

FORECAST_MULAI = date(2026, 1, 1)
FORECAST_AKHIR = date(2028, 12, 1)


def bulan_berikutnya(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def daftar_bulan_forecast():
    hasil, d = [], FORECAST_MULAI
    while d <= FORECAST_AKHIR:
        hasil.append(d)
        d = bulan_berikutnya(d)
    return hasil


def main():
    with open(os.path.join(PROD_DIR, "config", "konfigurasi_model.json"), encoding="utf-8") as f:
        konfigurasi = json.load(f)
    with open(os.path.join(PROD_DIR, "scalers", "scaler_params.json"), encoding="utf-8") as f:
        scaler_params = json.load(f)

    from tensorflow.keras.models import load_model
    model_per_combo = {}
    for cfg in konfigurasi.values():
        cid = cfg["combo_id"]
        if cid in model_per_combo:
            continue
        model_per_combo[cid] = [
            load_model(os.path.join(PROD_DIR, "models", f"{cid}_seed{k}.keras"))
            for k in range(cfg["n_seed"])
        ]

    df_reg = pd.read_csv(li.REGIONAL_CSV)
    df_reg["Tanggal"] = pd.to_datetime(df_reg["Tanggal"])

    # Normal klimatologis: rata-rata Cuaca per (jenis PLT, bulan kalender)
    # dari SELURUH histori regional (2023-2025) -- lihat CATATAN ASUMSI di atas.
    normal_cuaca = (
        df_reg.groupby(["Jenis", df_reg["Tanggal"].dt.month])["Cuaca"]
        .mean().to_dict()
    )  # {(jenis, bulan): rata2_cuaca}

    cf_lo, cf_hi = scaler_params["cf_min"], scaler_params["cf_max"]
    bulan_forecast = daftar_bulan_forecast()

    baris_per_plt = []
    for jenis_plt, cfg in konfigurasi.items():
        window = cfg["window_size"]
        cuaca_lo = scaler_params["cuaca_per_kategori"][jenis_plt]["min"]
        cuaca_hi = scaler_params["cuaca_per_kategori"][jenis_plt]["max"]
        model_list = model_per_combo[cfg["combo_id"]]

        s = df_reg[df_reg["Jenis"] == jenis_plt].sort_values("Tanggal").reset_index(drop=True)
        kapasitas_locf = float(s["Kapasitas"].iloc[-1])  # LOCF dari Des 2025 -- lihat CATATAN ASUMSI.

        # Riwayat awal: window_size bulan TERAKHIR data riil (berakhir Des 2025).
        hist = s.tail(window)
        cuaca_lag = [_skala(c, cuaca_lo, cuaca_hi) for c in hist["Cuaca"]]
        cf_lag = [_skala(p / k, cf_lo, cf_hi) for p, k in zip(hist["Produksi"], hist["Kapasitas"])]

        for tgl in bulan_forecast:
            cuaca_target = normal_cuaca[(jenis_plt, tgl.month)]
            cuaca_target_scaled = _skala(cuaca_target, cuaca_lo, cuaca_hi)

            if cfg["geser_cuaca"]:
                cuaca_channel = cuaca_lag[1:] + [cuaca_target_scaled]
            else:
                cuaca_channel = cuaca_lag

            X = np.array([[cuaca_channel[i], cf_lag[i]] for i in range(window)],
                         dtype="float32").reshape(1, window, 2)
            kat = np.array([[cfg["kategori_idx"]]], dtype="int32")
            inputs = [X, kat]
            if cfg["fitur_exog"]:
                nilai_exog = {
                    "cuaca_t": cuaca_target_scaled,
                    "bulan_sin": np.sin(2 * np.pi * tgl.month / 12),
                    "bulan_cos": np.cos(2 * np.pi * tgl.month / 12),
                }
                inputs.append(np.array(
                    [[nilai_exog[n] for n in cfg["fitur_exog"]]], dtype="float32"
                ))

            cf_pred_scaled = float(np.mean([
                float(m.predict(inputs, verbose=0)[0, 0]) for m in model_list
            ]))
            cf_pred = max(0.0, _skala_balik(cf_pred_scaled, cf_lo, cf_hi))
            produksi_pred = cf_pred * kapasitas_locf

            baris_per_plt.append({
                "Tanggal": tgl.isoformat(), "Tahun": tgl.year, "Bulan": tgl.month,
                "Jenis_PLT": jenis_plt, "Produksi_Prediksi": round(produksi_pred, 4),
            })

            # Geser jendela: prediksi bulan ini jadi bagian histori bulan berikutnya
            # (autoregresif) -- CF dari HASIL PREDIKSI, Cuaca dari normal klimatologis
            # bulan yang baru saja diproses.
            cuaca_lag = cuaca_lag[1:] + [cuaca_target_scaled]
            cf_lag = cf_lag[1:] + [cf_pred_scaled]

        print(f"{jenis_plt:10s} -> forecast 36 bulan selesai "
              f"(kapasitas LOCF={kapasitas_locf:.2f} MW)")

    df_per_plt = pd.DataFrame(baris_per_plt)
    df_per_plt.to_csv(os.path.join(FORECAST_DIR, "forecast_per_PLT_2026_2028.csv"), index=False)

    df_total = (
        df_per_plt.groupby(["Tanggal", "Tahun", "Bulan"], as_index=False)["Produksi_Prediksi"]
        .sum().rename(columns={"Produksi_Prediksi": "Total_Produksi_EBT"})
        .sort_values("Tanggal")
    )
    df_total.to_csv(os.path.join(FORECAST_DIR, "forecast_total_2026_2028.csv"), index=False)

    print(f"\nOutput ditulis ke: {FORECAST_DIR}")
    print("\nRingkasan total per tahun (GWh):")
    print(df_total.groupby("Tahun")["Total_Produksi_EBT"].sum().round(2).to_string())
    print(
        "\nCATATAN: forecast ini memakai Cuaca = normal klimatologis per bulan "
        "kalender (rata-rata 2023-2025) dan Kapasitas = LOCF Desember 2025 -- "
        "BUKAN prakiraan cuaca operasional maupun rencana penambahan kapasitas. "
        "Lihat docstring skrip ini untuk detail & keterbatasan."
    )


def _skala(nilai, lo, hi):
    return (nilai - lo) / (hi - lo) if hi > lo else 0.0


def _skala_balik(nilai, lo, hi):
    return nilai * (hi - lo) + lo


if __name__ == "__main__":
    main()
