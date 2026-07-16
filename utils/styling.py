"""
styling.py
===========
Konstanta warna tema aplikasi (biru - putih - hijau, khas instansi pemerintahan)
dan CSS custom MINIMAL untuk mempercantik tampilan (card, header, sidebar).

PENTING:
- CSS di sini hanya bersifat "polesan" (warna, bayangan, jarak antar elemen).
- Komponen utama tetap memakai elemen bawaan Streamlit (st.metric, st.columns,
  st.container, dsb) sesuai instruksi, CSS TIDAK menggantikan komponen tersebut.
"""

import streamlit as st

# ------------------------------------------------------------------
# Palet warna tema (biru - putih - hijau)
# ------------------------------------------------------------------
COLOR_PRIMARY_GREEN = "#1B5E20"      # Hijau tua - identitas Dinas ESDM (header, sidebar aktif)
COLOR_SECONDARY_GREEN = "#2E7D32"    # Hijau menengah - aksen, tombol
COLOR_PRIMARY_BLUE = "#1565C0"       # Biru - grafik, elemen interaktif
COLOR_LIGHT_BLUE = "#E3F2FD"         # Biru muda - background card/section
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_GRAY = "#F5F7FA"         # Background halaman
COLOR_TEXT_DARK = "#1A1A1A"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_WARNING = "#F59E0B"            # Oranye - status "hampir mencapai target"
COLOR_DANGER = "#DC2626"             # Merah - status defisit

# Palet warna untuk grafik per jenis PLT (dipakai konsisten di semua chart)
WARNA_PLT = {
    "PLTA": "#1565C0",
    "PLTB": "#2E7D32",
    "PLTMH": "#0097A7",
    "PLTS": "#F9A825",
    "PLTM": "#7B1FA2",
    "PLTS Atap": "#EF6C00",
    "PLT Hybrid": "#00897B",
}


def apply_custom_css():
    """
    Menyuntikkan CSS minimal ke halaman Streamlit.
    Dipanggil sekali di awal app.py (dan tiap file pages/ placeholder).
    """
    st.markdown(
        f"""
        <style>
        /* Background utama halaman */
        .main {{
            background-color: {COLOR_LIGHT_GRAY};
        }}

        /* Mempercantik kotak st.metric jadi terlihat seperti kartu info */
        div[data-testid="stMetric"] {{
            background-color: {COLOR_WHITE};
            border: 1px solid #E5E7EB;
            border-left: 5px solid {COLOR_PRIMARY_GREEN};
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}

        /* Header aplikasi (dipakai lewat st.markdown di components/header.py) */
        .app-header {{
            background: linear-gradient(90deg, {COLOR_PRIMARY_GREEN} 0%, {COLOR_SECONDARY_GREEN} 100%);
            color: {COLOR_WHITE};
            padding: 22px 28px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .app-header h1 {{
            color: {COLOR_WHITE};
            margin-bottom: 4px;
            font-size: 26px;
        }}
        .app-header p {{
            color: {COLOR_LIGHT_BLUE};
            margin: 0;
            font-size: 14px;
        }}

        /* Footer */
        .app-footer {{
            text-align: center;
            padding: 16px 0 8px 0;
            margin-top: 30px;
            border-top: 1px solid #E5E7EB;
            color: {COLOR_TEXT_MUTED};
            font-size: 13px;
        }}

        /* Judul section (dipakai sebelum tiap grafik) */
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: {COLOR_TEXT_DARK};
            margin-top: 10px;
            margin-bottom: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
