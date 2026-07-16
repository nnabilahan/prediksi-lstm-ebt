
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_forecast_total
from utils.styling import COLOR_PRIMARY_BLUE


def render_chart_forecast():
    """Menampilkan grafik line chart forecasting total produksi EBT per bulan (2026-2028)."""

    st.markdown(
        "<div class='section-title'>Forecasting Total Produksi EBT (2026 - 2028)</div>",
        unsafe_allow_html=True,
    )
    st.caption("Hasil prediksi model LSTM (Transfer Learning + Fine-Tuning), data bulanan.")

    df = load_forecast_total()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Tanggal"],
            y=df["Total_Produksi_EBT"],
            mode="lines",
            name="Prediksi Total EBT",
            line=dict(color=COLOR_PRIMARY_BLUE, width=3, dash="dot"),
            fill="tozeroy",
            fillcolor="rgba(21, 101, 192, 0.08)",
        )
    )

    fig.update_layout(
        xaxis_title="Periode",
        yaxis_title="Total Produksi EBT (GWh)",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        plot_bgcolor="white",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
