"""
gap_table.py
==============
Komponen TABEL FORECAST: menampilkan Tahun, (Jenis PLT jika relevan),
dan Forecast Produksi EBT untuk seluruh periode 2026-2028. Disederhanakan
-- tidak lagi menampilkan Target RUED, Status, atau Catatan capaian,
karena forecast produksi EBT sektor kelistrikan (GWh) tidak sepadan
untuk dibandingkan langsung dengan target bauran energi RUED (%).
"""

import streamlit as st

from utils.forecast_ringkasan import get_forecast_tahunan


def render_gap_table(filter_input: dict):
    """Menampilkan tabel forecast produksi EBT untuk seluruh periode 2026-2028."""

    st.markdown(
        "<div class='section-title'>Tabel Forecast Produksi EBT</div>",
        unsafe_allow_html=True,
    )

    df = get_forecast_tahunan(filter_input["mode"], filter_input["jenis_plt"])

    kolom_tampil = ["Tahun"]
    if "Jenis_PLT" in df.columns:
        kolom_tampil.append("Jenis_PLT")
    kolom_tampil.append("Forecast_GWh")

    df_tampil = df[kolom_tampil].rename(columns={"Jenis_PLT": "Jenis PLT"})

    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tahun": st.column_config.NumberColumn("Tahun", format="%d"),
            "Forecast_GWh": st.column_config.NumberColumn("Forecast Produksi EBT (GWh)", format="%.2f"),
        },
    )
    st.caption(
        "Tabel ini menampilkan data forecast produksi EBT sektor kelistrikan sebagai "
        "informasi pendukung evaluasi RUED, bukan pengukuran langsung terhadap capaian "
        "target bauran energi RUED."
    )