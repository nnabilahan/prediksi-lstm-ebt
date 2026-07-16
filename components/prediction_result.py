import streamlit as st

from utils.data_loader import load_forecast_per_plt


def render_prediction_result(input_form: dict):
    """
    Menampilkan kartu ringkasan hasil prediksi untuk filter yang dipilih.

    Returns
    -------
    DataFrame hasil filter (dipakai ulang oleh chart & tabel), atau None jika kosong.
    """
    jenis_plt = input_form["jenis_plt"]
    tahun_awal = input_form["tahun_awal"]
    tahun_akhir = input_form["tahun_akhir"]

    df = load_forecast_per_plt()
    df = df[(df["Tahun"] >= tahun_awal) & (df["Tahun"] <= tahun_akhir)]

    if jenis_plt is not None:
        df = df[df["Jenis_PLT"] == jenis_plt]
    else:
        # Total: jumlahkan seluruh jenis PLT per bulan
        df = df.groupby(["Tanggal", "Tahun", "Bulan"], as_index=False)["Produksi_Prediksi"].sum()

    if df.empty:
        st.warning("Tidak ada data forecast untuk filter ini.")
        return None

    label_konteks = jenis_plt if jenis_plt else "Seluruh Jenis PLT (Total)"

    st.markdown("<div class='section-title'>Hasil Prediksi</div>", unsafe_allow_html=True)

    total_prediksi = df["Produksi_Prediksi"].sum()
    jumlah_tahun = tahun_akhir - tahun_awal + 1
    rata_rata_tahunan = total_prediksi / jumlah_tahun
    prediksi_tahun_akhir = df[df["Tahun"] == tahun_akhir]["Produksi_Prediksi"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jenis Pembangkit", label_konteks)
    col2.metric(f"Total Prediksi {tahun_awal}-{tahun_akhir}", f"{total_prediksi:,.2f} GWh")
    col3.metric("Rata-rata per Tahun", f"{rata_rata_tahunan:,.2f} GWh")
    col4.metric(f"Prediksi Tahun {tahun_akhir}", f"{prediksi_tahun_akhir:,.2f} GWh")

    st.info(
        "ℹ️ Nilai di atas berasal dari hasil forecast model LSTM yang sudah dihitung "
        "sebelumnya (bukan inferensi/forecasting baru saat ini)."
    )

    return df