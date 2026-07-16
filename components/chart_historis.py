
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data_historis_placeholder
from utils.styling import COLOR_PRIMARY_GREEN


def render_chart_historis():
    """Menampilkan grafik line chart tren produksi EBT historis per tahun."""

    st.markdown(
        "<div class='section-title'>Tren Produksi EBT Historis (GWh)</div>",
        unsafe_allow_html=True,
    )
    

    df = load_data_historis_placeholder()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Tahun"],
            y=df["Total_Produksi_EBT"],
            mode="lines+markers+text",
            name="Produksi Aktual",
            line=dict(color=COLOR_PRIMARY_GREEN, width=3),
            marker=dict(size=9),
            text=[f"{v:,.0f}" for v in df["Total_Produksi_EBT"]],
            textposition="top center",
        )
    )

    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Produksi EBT (GWh)",
        xaxis=dict(type="category"),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
