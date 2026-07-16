
import importlib

import streamlit as st

from utils.styling import apply_custom_css
from components.sidebar import render_sidebar
from components.header import render_header
from components.metrics_cards import render_metrics_cards
from components.chart_historis import render_chart_historis
from components.chart_forecast import render_chart_forecast
from components.chart_komposisi import render_chart_komposisi
from components.production_table import render_production_table
from components.forecast_table import render_forecast_table
from components.footer import render_footer

# Pemetaan nama menu -> nama file modul placeholder di folder pages/
# Pemetaan nama menu -> nama file modul placeholder di folder app_pages/
# CATATAN: folder ini SENGAJA diberi nama "app_pages" (bukan "pages") karena
# Streamlit secara otomatis membuat navigasi bawaan tersendiri untuk folder
# bernama literal "pages" di samping app.py -- yang akan menampilkan menu
# duplikat DAN menjalankan file halaman secara langsung (bukan lewat
# render() yang dipanggil app.py), sehingga import berat seperti TensorFlow
# ter-load lebih awal dari yang seharusnya dan bisa memicu error di beberapa
# environment (ditemukan saat pengguna menguji di Windows).
PETA_HALAMAN_PLACEHOLDER = {
    "Prediksi EBT": "app_pages.1_Prediksi_EBT",
    "Gap Analysis RUED": "app_pages.3_Gap_Analysis_RUED",
    "Data EBT": "app_pages.4_Data_EBT",
    "Laporan": "app_pages.5_Laporan",
}

# ------------------------------------------------------------------
# 1. Konfigurasi halaman
# ------------------------------------------------------------------
st.set_page_config(
    page_title="SIPREBAR - Dashboard EBT Sulsel",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# 2. CSS custom (biru - putih - hijau)
# ------------------------------------------------------------------
apply_custom_css()

# ------------------------------------------------------------------
# 3. Sidebar & menu terpilih
# ------------------------------------------------------------------
menu_terpilih = render_sidebar()

# ------------------------------------------------------------------
# 4. Routing halaman
# ------------------------------------------------------------------
if menu_terpilih == "Dashboard":
    render_header()

    render_metrics_cards()
    st.divider()

    col_kiri, col_kanan = st.columns([2, 1])
    with col_kiri:
        render_chart_forecast()
        render_chart_historis()
    with col_kanan:
        render_chart_komposisi()

    st.divider()
    render_production_table()

    st.divider()
    render_forecast_table()

    st.divider()
    render_footer()

else:
    # Menu selain Dashboard -> muat & tampilkan halaman placeholder terkait
    nama_modul = PETA_HALAMAN_PLACEHOLDER.get(menu_terpilih)
    if nama_modul:
        halaman = importlib.import_module(nama_modul)
        halaman.render()

    render_footer()
