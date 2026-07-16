"""
gap_chart_bar.py
===================
Komponen GRAFIK Forecast Produksi EBT (batang tunggal) untuk tahun
terpilih. Target RUED TIDAK ditampilkan sebagai batang kedua, melainkan
sebagai GARIS ACUAN (reference line) putus-putus — karena keduanya
berbeda basis (forecast = produksi aktual sektor kelistrikan dalam GWh;
target RUED = target bauran energi daerah dalam %, di sini ditampilkan
GWh hanya sebagai konversi acuan, lihat gap_metrics.py).
"""

import plotly.graph_objects as go
import streamlit as st

from utils.styling import COLOR_PRIMARY_BLUE, COLOR_TEXT_MUTED


def render_gap_chart_bar(baris: dict, tahun: int, label_konteks: str):
    """
    Menampilkan bar chart Forecast Produksi EBT (1 batang) untuk tahun &
    konteks yang aktif di filter, dengan Target RUED sebagai garis acuan.
    """
    st.markdown(
        f"<div class='section-title'>Forecast Produksi EBT ({tahun})</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Konteks: {label_konteks}. Garis putus-putus = acuan Target RUED (bukan pembanding langsung).")

    forecast_gwh = baris["Forecast_GWh"]
    target_gwh = baris["Target_RUED_GWh"]
    batas_atas = max(forecast_gwh, target_gwh) * 1.3

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Forecast Produksi EBT"],
            y=[forecast_gwh],
            marker_color=COLOR_PRIMARY_BLUE,
            text=[f"{forecast_gwh:,.2f} GWh"],
            textposition="outside",
            width=[0.35],
            name="Forecast Produksi EBT",
        )
    )

    # --- Target RUED sebagai garis acuan, BUKAN batang kedua ---
    fig.add_shape(
        type="line",
        xref="paper", x0=0, x1=1,
        yref="y", y0=target_gwh, y1=target_gwh,
        line=dict(color=COLOR_TEXT_MUTED, width=2, dash="dash"),
    )
    fig.add_annotation(
        xref="paper", x=1, xanchor="right",
        yref="y", y=target_gwh, yshift=12,
        text=f"Acuan Target RUED: {target_gwh:,.2f} GWh*",
        showarrow=False,
        font=dict(size=12, color=COLOR_TEXT_MUTED),
    )

    fig.update_layout(
        yaxis_title="Produksi EBT (GWh)",
        yaxis=dict(range=[0, batas_atas]),
        xaxis=dict(showticklabels=False),
        margin=dict(l=10, r=10, t=30, b=10),
        height=360,
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("*Target RUED ditampilkan dalam GWh sebagai konversi acuan dari target bauran energi (%).")