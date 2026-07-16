"""
3_Gap_Analysis_RUED.py
=========================
Halaman "Analisis Kesesuaian terhadap Target RUED" (revisi ruang lingkup):
merangkai header, filter, kartu ringkasan, grafik tren forecast, tabel
forecast, panel ringkasan, dan info box.

PENTING: Sejak revisi ini, halaman TIDAK LAGI menghitung atau menampilkan
Gap (GWh), Persentase Capaian, Status Capaian, maupun Target RUED dalam
satuan GWh -- karena target RUED yang sesungguhnya (dokumen RUED
Provinsi Sulawesi Selatan) berbentuk target bauran energi 20% (2025) dan
32% (2050), BUKAN target produksi EBT tahunan per jenis PLT dalam GWh.
Forecast produksi EBT sektor kelistrikan (hasil model LSTM) ditampilkan
sebagai informasi PENDUKUNG evaluasi RUED, bukan pengukuran langsung.

Alur:
1. Header halaman
2. Filter (tahun, mode analisis, jenis PLT) -> filter_input
3. 4 kartu ringkasan -> baris (1 baris data forecast)
4. Grafik tren forecast produksi EBT (2026-2028), tanpa garis target
5. Tabel forecast (disederhanakan)
6. Panel Ringkasan Analisis
7. Info box batasan ruang lingkup
"""

import streamlit as st

from components.gap_header import render_gap_header
from components.gap_filter import render_gap_filter
from components.gap_metrics import render_gap_metrics
from components.gap_chart_line import render_gap_chart_line
from components.gap_table import render_gap_table
from components.gap_interpretation import render_gap_interpretation
from components.gap_info_box import render_gap_info_box


def render():
    render_gap_header()

    filter_input = render_gap_filter()
    st.divider()

    baris_terpilih = render_gap_metrics(filter_input)
    st.divider()

    render_gap_chart_line(filter_input)

    st.divider()
    render_gap_table(filter_input)

    st.divider()
    render_gap_interpretation(filter_input, baris_terpilih)

    st.divider()
    with st.expander("ℹ️ Tentang analisis ini"):
        st.markdown(
            "- **Forecast** dibaca langsung dari `forecast/forecast_per_PLT_2026_2028.csv` "
            "dan `forecast/forecast_total_2026_2028.csv` (hasil model LSTM yang sudah ada, "
            "tidak dihitung ulang).\n"
            "- **Target RUED** yang ditampilkan (20% tahun 2025, 32% tahun 2050) adalah "
            "target bauran energi sesuai dokumen RUED Provinsi Sulawesi Selatan -- tidak "
            "dikonversi ke GWh dan tidak dibandingkan langsung dengan forecast produksi.\n"
            "- Halaman ini tidak lagi menghitung Gap atau Persentase Capaian, karena satuan "
            "target RUED (%) dan forecast produksi (GWh) tidak sepadan untuk dibandingkan "
            "langsung.\n"
            "- Tidak ada training model maupun forecasting ulang di halaman ini."
        )

    st.divider()
    render_gap_info_box()