"""
gap_metrics.py
=================
Komponen 4 KARTU RINGKASAN halaman Analisis Kesesuaian terhadap Target
RUED (revisi ruang lingkup):
1. Forecast Produksi EBT (GWh) -- hasil model LSTM, tahun terpilih
2. Target RUED -- target bauran energi EBT menurut dokumen RUED
   Provinsi Sulawesi Selatan (20% tahun 2025, 32% tahun 2050), TIDAK
   dikonversi ke GWh dan TIDAK dibandingkan langsung dengan forecast
3. Peran Forecast -- penegasan bahwa forecast adalah informasi
   PENDUKUNG evaluasi RUED, bukan pengukuran langsung capaian target
4. Ruang Lingkup Analisis -- EBT Sektor Kelistrikan

PENTING: Tidak ada lagi Gap/Persentase Capaian/Status Capaian di sini --
target RUED sesungguhnya berbentuk target bauran energi (%) untuk
SELURUH sumber energi provinsi, bukan target produksi tahunan (GWh)
per jenis PLT, sehingga tidak relevan dibandingkan langsung dengan
forecast produksi EBT sektor kelistrikan pada penelitian ini.
"""

import streamlit as st

from utils.forecast_ringkasan import get_forecast_tahunan

TARGET_RUED_2025 = "20%"
TARGET_RUED_2050 = "32%"


def render_gap_metrics(filter_input: dict):
    """
    Menampilkan 4 kartu ringkasan untuk tahun & konteks (Total/jenis PLT)
    yang dipilih di filter.

    Returns
    -------
    dict berisi Tahun & Forecast_GWh (tahun terpilih) -- dipakai ulang
    oleh komponen grafik & panel ringkasan analisis.
    """
    df = get_forecast_tahunan(filter_input["mode"], filter_input["jenis_plt"])
    baris = df[df["Tahun"] == filter_input["tahun"]].iloc[0]

    label_konteks = (
        filter_input["jenis_plt"] if filter_input["mode"] == "Per Jenis PLT" else "Seluruh Jenis PLT"
    )

    st.markdown(
        f"<div class='section-title'>Ringkasan Analisis {filter_input['tahun']} &mdash; {label_konteks}</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Forecast Produksi EBT", value=f"{baris['Forecast_GWh']:,.2f} GWh")
        st.caption("Hasil prediksi model LSTM.")

    with col2:
        st.metric(label="Target RUED", value=f"{TARGET_RUED_2025} (2025)")
        st.caption(f"Target bauran energi EBT Provinsi Sulawesi Selatan, menuju {TARGET_RUED_2050} pada 2050.")

    with col3:
        st.metric(label="Peran Forecast", value="Informasi Pendukung")
        st.caption("Bukan pengukuran langsung capaian target RUED.")

    with col4:
        st.metric(label="Ruang Lingkup Analisis", value="EBT Sektor Kelistrikan")
        st.caption("Analisis hanya mencakup sektor kelistrikan, bukan keseluruhan bauran energi daerah.")

    return baris.to_dict()