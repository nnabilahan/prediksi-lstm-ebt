"""
Gap analysis: forecast EBT sektor kelistrikan (2026-2028) vs target RUED
Provinsi Sulawesi Selatan (Perda No. 2 Tahun 2022).

PENTING -- keterbatasan metodologis yang disengaja, bukan bug:
Target RUED (20% @ 2025, 32% @ 2030) adalah target BAURAN ENERGI untuk
SELURUH SEKTOR (listrik, transportasi, industri, rumah tangga, dst), dalam
satuan PERSEN dari total konsumsi/pasokan energi daerah. Forecast model ini
HANYA mencakup produksi EBT SEKTOR KELISTRIKAN (GWh), yang merupakan
subset dari cakupan target RUED.

Karena repo ini tidak memiliki data total bauran energi Sulsel (seluruh
sektor, seluruh sumber, dalam satuan yang sama) untuk dijadikan penyebut
(denominator) yang valid, script ini TIDAK memaksakan konversi GWh EBT
kelistrikan menjadi "% terhadap target RUED" -- itu akan jadi angka yang
menyesatkan (apples-to-oranges). Sebagai gantinya, script ini menyajikan
KEDUA rangkaian data (target % RUED dan forecast GWh kelistrikan) secara
berdampingan sebagai referensi, dengan catatan cakupan yang eksplisit,
supaya siapa pun yang membaca tidak salah mengira ini adalah gap yang
langsung sepadan.

Output:
- audit/results/gap_analysis_2026_2028.csv
- audit/results/gap_analysis_2026_2028.png
"""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AUDIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_RUED_PATH = os.path.join(AUDIT_DIR, "analysis", "config_target_rued.csv")
FORECAST_TOTAL_PATH = os.path.join(
    AUDIT_DIR, "results", "pipeline_run", "EBT_LSTM_Streamlit", "forecast",
    "forecast_total_2026_2028.csv",
)
OUT_CSV = os.path.join(AUDIT_DIR, "results", "gap_analysis_2026_2028.csv")
OUT_PNG = os.path.join(AUDIT_DIR, "results", "gap_analysis_2026_2028.png")

FORECAST_YEARS = [2026, 2027, 2028]


def interpolate_target(target_df, years):
    """Interpolasi linear target % RUED antar titik jangkar (2025->20%, 2030->32%)."""
    anchor_years = target_df["Tahun"].values.astype(float)
    anchor_values = target_df["Target_Bauran_EBT_Persen"].values.astype(float)
    slope = (anchor_values[1] - anchor_values[0]) / (anchor_years[1] - anchor_years[0])
    result = {}
    for y in years:
        result[y] = anchor_values[0] + slope * (y - anchor_years[0])
    return result, slope


def main():
    target_df = pd.read_csv(TARGET_RUED_PATH)
    forecast_df = pd.read_csv(FORECAST_TOTAL_PATH)
    forecast_df["Tahun"] = pd.to_datetime(forecast_df["Tanggal"]).dt.year

    forecast_annual = (
        forecast_df.groupby("Tahun")["Total_Produksi_EBT"].sum().reindex(FORECAST_YEARS)
    )

    target_interp, slope = interpolate_target(target_df, FORECAST_YEARS)

    rows = []
    for year in FORECAST_YEARS:
        rows.append({
            "Tahun": year,
            "Target_Bauran_EBT_Persen_RUED": round(target_interp[year], 3),
            "Forecast_Produksi_EBT_Kelistrikan_GWh": round(float(forecast_annual[year]), 3),
            "Catatan_Cakupan": (
                "Target % mencakup seluruh sektor energi (RUED); "
                "forecast GWh hanya sektor kelistrikan. Tidak dikonversi "
                "menjadi satu satuan gap karena tidak ada data total "
                "bauran energi Sulsel (seluruh sektor) sebagai penyebut yang valid."
            ),
        })

    gap_df = pd.DataFrame(rows)
    gap_df.to_csv(OUT_CSV, index=False)

    print("=== Gap Analysis vs Target RUED (Perda No. 2 Tahun 2022) ===")
    print(f"Target: {target_df.loc[0,'Target_Bauran_EBT_Persen']}% @ {int(target_df.loc[0,'Tahun'])} "
          f"-> {target_df.loc[1,'Target_Bauran_EBT_Persen']}% @ {int(target_df.loc[1,'Tahun'])} "
          f"(interpolasi linear, slope {slope:.2f} persen/tahun)")
    print(gap_df.to_string(index=False))
    print()
    print("CATATAN METODOLOGIS: target RUED di atas mencakup seluruh sektor energi, "
          "forecast hanya EBT sektor kelistrikan. Angka % dan GWh TIDAK sepadan "
          "secara langsung -- lihat kolom Catatan_Cakupan / README audit.")

    # --- Visualisasi: dua sumbu-y (persen vs GWh), jelas dipisahkan ---
    fig, ax1 = plt.subplots(figsize=(8, 5))

    ax1.plot(FORECAST_YEARS, [target_interp[y] for y in FORECAST_YEARS],
              color="tab:red", marker="o", label="Target Bauran EBT RUED (%, seluruh sektor)")
    ax1.set_xlabel("Tahun")
    ax1.set_ylabel("Target RUED (%)", color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.set_xticks(FORECAST_YEARS)

    ax2 = ax1.twinx()
    ax2.plot(FORECAST_YEARS, [forecast_annual[y] for y in FORECAST_YEARS],
              color="tab:blue", marker="s", label="Forecast Produksi EBT Kelistrikan (GWh)")
    ax2.set_ylabel("Forecast EBT Kelistrikan (GWh/tahun)", color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    plt.title("Target RUED (seluruh sektor) vs Forecast EBT Kelistrikan\n"
              "(dua sumbu-y berbeda satuan -- BUKAN perbandingan langsung)")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=150)
    print(f"\nChart disimpan: {OUT_PNG}")


if __name__ == "__main__":
    main()
