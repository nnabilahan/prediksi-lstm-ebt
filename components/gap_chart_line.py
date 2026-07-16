"""
gap_chart_line.py
====================
Komponen GRAFIK "Tren Forecast Produksi EBT Sektor Kelistrikan
(2026-2028)": menampilkan HANYA tren forecast produksi EBT hasil model
LSTM, TANPA garis Target RUED -- karena target RUED yang sesungguhnya
berbentuk target bauran energi (%) untuk seluruh sumber energi provinsi
(20% tahun 2025, 32% tahun 2050), bukan angka produksi tahunan (GWh)
yang bisa diplot pada sumbu yang sama dengan forecast produksi.
"""

import plotly.graph_objects as go
import streamlit as st

from utils.forecast_ringkasan import get_forecast_tahunan
from utils.styling import COLOR_PRIMARY_BLUE


def render_gap_chart_line(filter_input: dict):
    """Menampilkan tren Forecast Produksi EBT 2026-2028 (tanpa garis Target RUED)."""

    label_konteks = (
        filter_input["jenis_plt"] if filter_input["mode"] == "Per Jenis PLT" else "Seluruh Jenis PLT"
    )

    st.markdown(
        f"<div class='section-title'>Tren Forecast Produksi EBT Sektor Kelistrikan (2026-2028) &mdash; {label_konteks}</div>",
        unsafe_allow_html=True,
    )

    df = get_forecast_tahunan(filter_input["mode"], filter_input["jenis_plt"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Tahun"],
            y=df["Forecast_GWh"],
            mode="lines+markers+text",
            name="Forecast Produksi EBT",
            line=dict(color=COLOR_PRIMARY_BLUE, width=3),
            marker=dict(size=9),
            text=[f"{v:,.1f}" for v in df["Forecast_GWh"]],
            textposition="top center",
        )
    )

    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Forecast Produksi EBT (GWh)",
        xaxis=dict(type="category"),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Grafik ini menampilkan tren forecast produksi EBT sektor kelistrikan sebagai "
        "informasi pendukung evaluasi RUED, bukan perbandingan langsung dengan target "
        "bauran energi RUED."
    )