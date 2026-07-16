"""
predictor.py
=============
INTI proses prediksi produksi EBT menggunakan model LSTM yang SUDAH DILATIH.

Tahapan di file ini (sesuai alur yang sudah dijelaskan ke pengguna):
1. Bentuk sequence 6 bulan (window_size model) dari 1 titik input pengguna
   -> Cuaca & Kapasitas diasumsikan konstan 6 bulan (LOCF)
   -> Produksi (fitur lag) memakai nilai tengah rentang historis (referensi netral)
2. Scaling input memakai scaler yang SUDAH tersimpan (bukan scaler baru)
3. Inferensi: model.predict() -- TIDAK ADA model.fit() / training di sini
4. Inverse transform hasil prediksi ke satuan produksi asli

Semua fungsi di sini murni pemrosesan (tidak ada tampilan/UI Streamlit),
supaya bisa diuji terpisah dari komponen tampilan.
"""

import numpy as np

from utils.model_loader import (
    load_model_untuk_plt,
    load_scaler_untuk_plt,
    get_info_konfigurasi_plt,
)

WINDOW_SIZE = 6  # jumlah timestep yang dibutuhkan model (lihat config/konfigurasi_model.json)


def bangun_sequence_input(cuaca: float, kapasitas: float, scaler_fitur, scaler_target):
    """
    Membentuk sequence input berbentuk (1, 6, 3) yang dibutuhkan model LSTM,
    dari SATU titik input pengguna (cuaca & kapasitas saat ini).

    Asumsi yang dipakai (didokumentasikan & ditampilkan ke pengguna di UI):
    - Cuaca & Kapasitas: diasumsikan KONSTAN selama 6 bulan ke belakang (LOCF),
      pendekatan yang sama seperti dipakai pada forecasting jangka panjang
      di pipeline Colab (lihat metadata_penelitian.json).
    - Produksi (fitur lag ke-3): karena tidak ada data produksi real-time
      sebagai konteks, dipakai nilai tengah rentang produksi historis PLT
      tersebut (rata-rata data_min_ & data_max_ pada scaler_target) sebagai
      referensi netral.

    Returns
    -------
    tuple (sequence, produksi_referensi)
        sequence : np.ndarray shape (1, 6, 3), sudah dalam skala 0-1
        produksi_referensi : float, nilai asli (belum discaling) yang dipakai sebagai lag
    """
    # --- Scaling Cuaca & Kapasitas (2 kolom) ---
    fitur_mentah = np.array([[cuaca, kapasitas]])            # shape (1, 2)
    fitur_scaled = scaler_fitur.transform(fitur_mentah)[0]    # shape (2,)

    # --- Nilai referensi netral untuk lag Produksi ---
    produksi_min = scaler_target.data_min_[0]
    produksi_max = scaler_target.data_max_[0]
    produksi_referensi = (produksi_min + produksi_max) / 2
    produksi_scaled = scaler_target.transform([[produksi_referensi]])[0][0]

    # --- Susun 1 baris fitur: [Cuaca_scaled, Kapasitas_scaled, Produksi_scaled] ---
    satu_baris = np.array([fitur_scaled[0], fitur_scaled[1], produksi_scaled])

    # --- Ulangi baris ini sebanyak window_size (6 bulan), sesuai asumsi LOCF ---
    sequence = np.tile(satu_baris, (WINDOW_SIZE, 1))   # shape (6, 3)
    sequence = np.expand_dims(sequence, axis=0)         # shape (1, 6, 3)

    return sequence, produksi_referensi


def jalankan_prediksi(jenis_plt: str, cuaca: float, kapasitas: float) -> dict:
    """
    Fungsi utama: memuat model & scaler sesuai jenis PLT, menjalankan inferensi,
    dan mengembalikan hasil prediksi dalam satuan produksi asli.

    TIDAK melakukan training ulang maupun forecasting berantai -- hanya
    satu kali inferensi (single-point) dari model yang sudah jadi.

    Returns
    -------
    dict berisi:
        - hasil_produksi (float): prediksi produksi dalam satuan asli
        - metode (str): "Transfer Learning" atau "Direct Training"
        - produksi_referensi (float): nilai tengah yang dipakai sebagai lag Produksi
    """
    # 1. Muat model & scaler (sudah dilatih sebelumnya, hanya di-load)
    model = load_model_untuk_plt(jenis_plt)
    scaler_fitur, scaler_target = load_scaler_untuk_plt(jenis_plt)
    info_konfigurasi = get_info_konfigurasi_plt(jenis_plt)

    # 2. Bentuk sequence input (preprocessing)
    sequence_input, produksi_referensi = bangun_sequence_input(
        cuaca, kapasitas, scaler_fitur, scaler_target
    )

    # 3. Inferensi model (bukan training)
    hasil_scaled = model.predict(sequence_input, verbose=0)  # shape (1, 1)

    # 4. Inverse transform ke satuan produksi asli
    hasil_produksi = scaler_target.inverse_transform(hasil_scaled)[0][0]

    return {
        "hasil_produksi": float(hasil_produksi),
        "metode": info_konfigurasi.get("metode", "-"),
        "produksi_referensi": float(produksi_referensi),
    }
