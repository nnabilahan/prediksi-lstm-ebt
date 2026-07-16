"""
rued_loader.py
================
Fungsi untuk MEMBACA target RUED dari file CSV yang dapat diperbarui
pengguna (config/target_rued.csv) TANPA mengubah kode, menggabungkannya
dengan data forecast yang sudah tersedia, dan MENGHITUNG gap/persentase
capaian.

PENTING:
- Tidak ada angka target yang ditulis langsung (hardcode) di file .py manapun.
- Tidak ada forecasting ulang -- data forecast dibaca apa adanya dari
  utils/data_loader.load_forecast_per_plt().
"""

import os

import pandas as pd
import streamlit as st

from utils.data_loader import BASE_DIR, load_forecast_per_plt

PATH_TARGET_RUED = os.path.join(BASE_DIR, "config", "target_rued.csv")

# Ambang batas klasifikasi status capaian (mudah disesuaikan di satu tempat)
AMBANG_TERCAPAI = 100.0    # persen capaian >= ini -> "Tercapai/Surplus"
AMBANG_MENDEKATI = 85.0    # persen capaian >= ini (tapi < AMBANG_TERCAPAI) -> "Mendekati"
# di bawah AMBANG_MENDEKATI -> "Defisit"


@st.cache_data
def load_target_rued() -> pd.DataFrame:
    """
    Membaca target RUED dari config/target_rued.csv.
    Kolom: Tahun, Jenis_PLT, Target_RUED_GWh
    """
    df = pd.read_csv(PATH_TARGET_RUED)
    return df


def klasifikasi_status(persentase_capaian: float) -> str:
    """Mengklasifikasikan status capaian menjadi Tercapai / Mendekati / Defisit."""
    if persentase_capaian >= AMBANG_TERCAPAI:
        return "Tercapai"
    elif persentase_capaian >= AMBANG_MENDEKATI:
        return "Mendekati"
    else:
        return "Defisit"


@st.cache_data
def hitung_gap_per_plt_tahunan() -> pd.DataFrame:
    """
    Menggabungkan forecast tahunan per jenis PLT dengan target RUED,
    lalu menghitung Gap dan Persentase Capaian untuk SETIAP kombinasi
    Tahun x Jenis PLT.

    Returns
    -------
    DataFrame dengan kolom:
        Tahun, Jenis_PLT, Forecast_GWh, Target_RUED_GWh, Gap_GWh,
        Persentase_Capaian, Status
    """
    # 1. Agregasi forecast bulanan -> tahunan, per jenis PLT
    df_forecast = load_forecast_per_plt()
    df_forecast_tahunan = (
        df_forecast.groupby(["Tahun", "Jenis_PLT"], as_index=False)["Produksi_Prediksi"]
        .sum()
        .rename(columns={"Produksi_Prediksi": "Forecast_GWh"})
    )

    # 2. Baca target RUED
    df_target = load_target_rued()

    # 3. Gabungkan (join) berdasarkan Tahun & Jenis_PLT
    df_gap = pd.merge(
        df_forecast_tahunan, df_target, on=["Tahun", "Jenis_PLT"], how="inner"
    )

    # 4. Hitung Gap & Persentase Capaian
    df_gap["Gap_GWh"] = df_gap["Forecast_GWh"] - df_gap["Target_RUED_GWh"]
    df_gap["Persentase_Capaian"] = (df_gap["Forecast_GWh"] / df_gap["Target_RUED_GWh"]) * 100

    # 5. Klasifikasi status capaian
    df_gap["Status"] = df_gap["Persentase_Capaian"].apply(klasifikasi_status)

    return df_gap


def hitung_gap_total_tahunan() -> pd.DataFrame:
    """
    Menghitung Gap untuk TOTAL seluruh jenis PLT (mode analisis "Total
    Produksi EBT"), dengan MENJUMLAHKAN forecast & target semua PLT per
    tahun -- bukan angka Total yang terpisah, supaya selalu konsisten
    dengan rincian per PLT.

    Returns
    -------
    DataFrame dengan kolom:
        Tahun, Forecast_GWh, Target_RUED_GWh, Gap_GWh, Persentase_Capaian, Status
    """
    df_per_plt = hitung_gap_per_plt_tahunan()
    df_total = (
        df_per_plt.groupby("Tahun", as_index=False)[["Forecast_GWh", "Target_RUED_GWh"]]
        .sum()
    )
    df_total["Gap_GWh"] = df_total["Forecast_GWh"] - df_total["Target_RUED_GWh"]
    df_total["Persentase_Capaian"] = (df_total["Forecast_GWh"] / df_total["Target_RUED_GWh"]) * 100
    df_total["Status"] = df_total["Persentase_Capaian"].apply(klasifikasi_status)
    return df_total


def get_data_analisis(mode: str, jenis_plt: str = None) -> pd.DataFrame:
    """
    Titik masuk TUNGGAL untuk mengambil data gap analysis sesuai mode yang
    dipilih pengguna, dipakai bersama oleh seluruh komponen (metric cards,
    bar chart, line chart, tabel) supaya logika filter tidak terduplikasi.

    Parameters
    ----------
    mode : str
        "Total Produksi EBT" atau "Per Jenis PLT"
    jenis_plt : str, optional
        Wajib diisi jika mode == "Per Jenis PLT"

    Returns
    -------
    DataFrame berisi SELURUH periode (2026-2028) untuk mode/jenis PLT terpilih,
    dengan kolom: Tahun, [Jenis_PLT], Forecast_GWh, Target_RUED_GWh, Gap_GWh,
    Persentase_Capaian, Status
    """
    if mode == "Per Jenis PLT":
        df = hitung_gap_per_plt_tahunan()
        df = df[df["Jenis_PLT"] == jenis_plt].reset_index(drop=True)
    else:
        df = hitung_gap_total_tahunan()

    return df
