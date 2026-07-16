"""
data_loader.py
================
Kumpulan fungsi untuk MEMBACA data hasil penelitian yang sudah tersedia
(forecast, evaluasi, konfigurasi model, metadata).

PENTING:
- File ini HANYA membaca data, tidak melakukan training atau forecasting ulang.
- Semua fungsi memakai @st.cache_data agar file tidak dibaca berulang kali
  setiap kali ada interaksi (klik, ganti tab, dsb) di aplikasi Streamlit.
- Path folder data merujuk ke folder hasil penelitian dari Google Colab
  (config/, evaluation/, forecast/, models/, scalers/) yang TIDAK diubah isinya.
"""

import json
import os
import pandas as pd
import streamlit as st

# CATATAN LINGKUNGAN: menonaktifkan backend string PyArrow bawaan pandas 3.x.
# Beberapa kombinasi versi pandas/pyarrow/numpy memiliki bug tingkat rendah
# saat membangun array string ber-backend PyArrow (menyebabkan crash proses).
# Menonaktifkan ini membuat pandas memakai tipe data string standar (aman,
# tidak mengubah hasil perhitungan sama sekali -- hanya cara penyimpanan
# internal kolom teks).
pd.set_option("future.infer_string", False)

# ------------------------------------------------------------------
# Konfigurasi path dasar
# ------------------------------------------------------------------
# BASE_DIR menunjuk ke folder root proyek (tempat app.py berada),
# supaya path tetap benar walau aplikasi dijalankan dari folder lain.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATH_METADATA = os.path.join(BASE_DIR, "metadata_penelitian.json")
PATH_CONFIG = os.path.join(BASE_DIR, "config", "konfigurasi_model.json")

PATH_FORECAST_TOTAL = os.path.join(BASE_DIR, "forecast", "forecast_total_2026_2028.csv")
PATH_FORECAST_PER_PLT = os.path.join(BASE_DIR, "forecast", "forecast_per_PLT_2026_2028.csv")

PATH_RINGKASAN_EVALUASI = os.path.join(BASE_DIR, "evaluation", "ringkasan_rata2_seluruh_model.csv")
PATH_MODEL_TERBAIK_PER_PLT = os.path.join(BASE_DIR, "evaluation", "model_terbaik_per_plt.csv")
PATH_PERBANDINGAN_LENGKAP = os.path.join(BASE_DIR, "evaluation", "perbandingan_lengkap_seluruh_model.csv")


# ------------------------------------------------------------------
# METADATA & KONFIGURASI
# ------------------------------------------------------------------
@st.cache_data
def load_metadata():
    """Membaca metadata_penelitian.json (judul, metodologi, model terbaik, dsb)."""
    with open(PATH_METADATA, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_konfigurasi_model():
    """Membaca config/konfigurasi_model.json (parameter model per jenis PLT)."""
    with open(PATH_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------
# DATA FORECASTING (hasil prediksi yang SUDAH ADA, bukan dihitung ulang)
# ------------------------------------------------------------------
@st.cache_data
def load_forecast_total():
    """
    Membaca total produksi EBT hasil forecast 2026-2028 (seluruh jenis PLT digabung).
    Kolom: Tanggal, Tahun, Bulan, Total_Produksi_EBT
    """
    df = pd.read_csv(PATH_FORECAST_TOTAL, parse_dates=["Tanggal"])
    return df


@st.cache_data
def load_forecast_per_plt():
    """
    Membaca hasil forecast 2026-2028 per jenis PLT.
    Kolom: Tanggal, Tahun, Bulan, Jenis_PLT, Produksi_Prediksi
    """
    df = pd.read_csv(PATH_FORECAST_PER_PLT, parse_dates=["Tanggal"])
    return df


@st.cache_data
def load_forecast_tahunan_total():
    """
    Mengagregasi forecast_total per tahun (2026, 2027, 2028) untuk kebutuhan
    tabel ringkasan forecasting di Dashboard.
    Return: DataFrame dengan kolom Tahun & Total_Produksi_EBT (GWh/tahun)
    """
    df = load_forecast_total()
    df_tahunan = df.groupby("Tahun", as_index=False)["Total_Produksi_EBT"].sum()
    return df_tahunan


# ------------------------------------------------------------------
# DATA EVALUASI MODEL (RMSE, MAE, MAPE)
# ------------------------------------------------------------------
@st.cache_data
def load_ringkasan_evaluasi():
    """
    Membaca ringkasan rata-rata RMSE/MAE/MAPE seluruh model (Baseline,
    FineTuning, Iterasi1-3) dari evaluation/ringkasan_rata2_seluruh_model.csv
    """
    df = pd.read_csv(PATH_RINGKASAN_EVALUASI)
    return df


@st.cache_data
def load_model_terbaik_per_plt():
    """
    Membaca model terbaik (beserta RMSE terbaik) untuk masing-masing jenis PLT
    dari evaluation/model_terbaik_per_plt.csv
    """
    df = pd.read_csv(PATH_MODEL_TERBAIK_PER_PLT)
    return df


@st.cache_data
def load_perbandingan_lengkap():
    """
    Membaca tabel perbandingan lengkap RMSE/MAE/MAPE seluruh model per jenis PLT.
    Berguna untuk analisis lebih detail di halaman Prediksi EBT (tahap berikutnya).
    """
    df = pd.read_csv(PATH_PERBANDINGAN_LENGKAP)
    return df


# ------------------------------------------------------------------
# DATA HISTORIS (BELUM TERSEDIA -> PLACEHOLDER)
# ------------------------------------------------------------------
@st.cache_data
def load_data_historis_placeholder():
    """
    PLACEHOLDER: Data historis produksi EBT (aktual, per tahun) BELUM tersedia
    sebagai file terpisah dari hasil penelitian (folder forecast/evaluation
    hanya berisi hasil prediksi & evaluasi, bukan data historis mentah).

    Fungsi ini mengembalikan data contoh (dummy) HANYA agar grafik historis
    di Dashboard dapat ditampilkan sementara. Nilai-nilai di sini TIDAK
    merepresentasikan data asli dan wajib diganti begitu file data historis
    resmi (misal dari folder 'data/' Dinas ESDM) tersedia.
    """
    df = pd.DataFrame({
        "Tahun": [2022, 2023, 2024, 2025],
        "Total_Produksi_EBT": [850.0, 980.0, 1250.0, 1320.0],
        "Sumber": ["placeholder"] * 4,
    })
    return df
