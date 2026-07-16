"""
forecast_ringkasan.py
========================
Fungsi RINGAN untuk membaca & meringkas (agregasi bulanan -> tahunan)
hasil forecast produksi EBT yang SUDAH ADA (forecast/forecast_per_PLT_2026_2028.csv
dan forecast/forecast_total_2026_2028.csv), TANPA menggabungkannya dengan
target RUED apa pun.

Dipakai khusus oleh halaman "Analisis Kesesuaian terhadap Target RUED"
setelah revisi ruang lingkup: forecast HANYA ditampilkan sebagai informasi
pendukung evaluasi RUED, bukan dibandingkan langsung (dalam GWh) dengan
target RUED (yang sebenarnya berbentuk target bauran energi %, bukan
GWh per jenis PLT per tahun).

TIDAK ADA forecasting ulang di file ini -- murni membaca & agregasi data
forecast yang sudah tersedia.
"""

import pandas as pd

from utils.data_loader import load_forecast_per_plt, load_forecast_total


def get_forecast_tahunan(mode: str, jenis_plt: str = None) -> pd.DataFrame:
    """
    Mengambil forecast tahunan (2026-2028) sesuai mode yang dipilih pengguna.

    Parameters
    ----------
    mode : str
        "Total Produksi EBT" atau "Per Jenis PLT"
    jenis_plt : str, optional
        Wajib diisi jika mode == "Per Jenis PLT"

    Returns
    -------
    DataFrame dengan kolom: Tahun, [Jenis_PLT], Forecast_GWh
    """
    if mode == "Per Jenis PLT":
        df = load_forecast_per_plt()
        df = df[df["Jenis_PLT"] == jenis_plt]
        df_tahunan = (
            df.groupby(["Tahun", "Jenis_PLT"], as_index=False)["Produksi_Prediksi"]
            .sum()
            .rename(columns={"Produksi_Prediksi": "Forecast_GWh"})
        )
    else:
        df = load_forecast_total()
        df_tahunan = (
            df.groupby("Tahun", as_index=False)["Total_Produksi_EBT"]
            .sum()
            .rename(columns={"Total_Produksi_EBT": "Forecast_GWh"})
        )

    return df_tahunan.sort_values("Tahun").reset_index(drop=True)