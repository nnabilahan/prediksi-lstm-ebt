"""
model_loader.py
=================
Fungsi untuk MEMUAT model LSTM (.keras) dan scaler (.pkl) yang SUDAH DILATIH
sebelumnya di Google Colab, sesuai jenis PLT yang dipilih pengguna.

PENTING:
- File ini HANYA memuat (load) model & scaler yang sudah ada di folder
  models/ dan scalers/. TIDAK ADA proses training/fit() di sini.
- Memakai st.cache_resource (bukan cache_data) karena objek yang di-cache
  adalah model TensorFlow & scaler scikit-learn, bukan data biasa -
  ini membuat model hanya dimuat sekali ke memori meski dipakai berkali-kali.
- Path model & scaler diambil dari config/konfigurasi_model.json (bukan
  ditulis manual/hardcode), supaya konsisten dengan hasil penelitian asli.
"""

import os
import joblib
import streamlit as st
import tensorflow as tf

from utils.data_loader import load_konfigurasi_model, BASE_DIR


@st.cache_resource(show_spinner="Memuat model LSTM...")
def load_model_untuk_plt(jenis_plt: str):
    """
    Memuat model .keras yang sesuai dengan jenis PLT terpilih.

    Parameters
    ----------
    jenis_plt : str
        Nama jenis PLT, harus sama persis dengan key di konfigurasi_model.json
        (contoh: "PLTA", "PLTS Atap", "PLT Hybrid")

    Returns
    -------
    tf.keras.Model
    """
    konfigurasi = load_konfigurasi_model()
    info_plt = konfigurasi[jenis_plt]
    path_model = os.path.join(BASE_DIR, "models", info_plt["nama_file_model"])
    model = tf.keras.models.load_model(path_model, compile=False)
    return model


@st.cache_resource(show_spinner="Memuat scaler...")
def load_scaler_untuk_plt(jenis_plt: str):
    """
    Memuat sepasang scaler (fitur & target) yang sesuai dengan jenis PLT terpilih.

    Parameters
    ----------
    jenis_plt : str
        Nama jenis PLT, sama persis dengan key di konfigurasi_model.json

    Returns
    -------
    tuple (scaler_fitur, scaler_target)
        scaler_fitur  : MinMaxScaler untuk kolom [Cuaca, Kapasitas]
        scaler_target : MinMaxScaler untuk kolom [Produksi]
    """
    konfigurasi = load_konfigurasi_model()
    info_plt = konfigurasi[jenis_plt]

    path_scaler_fitur = os.path.join(BASE_DIR, "scalers", info_plt["nama_file_scaler_fitur"])
    path_scaler_target = os.path.join(BASE_DIR, "scalers", info_plt["nama_file_scaler_target"])

    scaler_fitur = joblib.load(path_scaler_fitur)
    scaler_target = joblib.load(path_scaler_target)

    return scaler_fitur, scaler_target


def get_info_konfigurasi_plt(jenis_plt: str) -> dict:
    """
    Mengambil detail konfigurasi (window_size, metode, dsb) untuk satu jenis PLT
    dari config/konfigurasi_model.json. Dipakai untuk menampilkan info metode
    model (Transfer Learning / Direct Training) di halaman Prediksi EBT.
    """
    konfigurasi = load_konfigurasi_model()
    return konfigurasi[jenis_plt]
