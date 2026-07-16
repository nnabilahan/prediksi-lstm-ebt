"""
gap_info_box.py
==================
Komponen INFO BOX di bagian paling bawah halaman Analisis Kesesuaian
terhadap Target RUED: menegaskan batasan ruang lingkup penelitian &
peran forecast sebagai informasi pendukung, bukan pengukuran langsung.
"""

import streamlit as st


def render_gap_info_box():
    """Menampilkan info box catatan batasan ruang lingkup penelitian."""
    st.info(
        "**Catatan:** Berdasarkan dokumen RUED Provinsi Sulawesi Selatan, target yang "
        "ditetapkan adalah target bauran energi sebesar **20% pada tahun 2025** dan "
        "**32% pada tahun 2050** -- bukan target produksi EBT tahunan dalam satuan GWh. "
        "Penelitian ini hanya memprediksi produksi Energi Baru Terbarukan **sektor "
        "kelistrikan** menggunakan model LSTM, sehingga hasil forecast yang ditampilkan "
        "berfungsi sebagai **informasi pendukung** evaluasi implementasi RUED, **bukan "
        "sebagai pengukuran langsung** terhadap capaian target bauran energi RUED "
        "secara keseluruhan.",
        icon="ℹ️",
    )