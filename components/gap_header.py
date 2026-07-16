"""
gap_header.py
================
Komponen HEADER untuk halaman "Analisis Kesesuaian terhadap Target RUED":
judul halaman serta penjelasan singkat bahwa halaman ini adalah alat
evaluasi arah kebijakan, bukan penilaian resmi capaian RUED.
"""

import streamlit as st


def render_gap_header():
    """Menampilkan header di bagian atas halaman Analisis Kesesuaian RUED."""
    st.markdown(
        """
        <div class="app-header">
            <h1>🎯 Analisis Kesesuaian terhadap Target RUED</h1>
            <p>
                Evaluasi hasil forecasting produksi EBT sektor kelistrikan sebagai
                acuan terhadap target RUED Provinsi Sulawesi Selatan.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )