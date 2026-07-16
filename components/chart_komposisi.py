
import plotly.express as px
import streamlit as st

from utils.data_loader import load_forecast_per_plt
from utils.styling import WARNA_PLT


def render_chart_komposisi():
    """Menampilkan pie chart komposisi produksi EBT per jenis PLT (tahun 2026)."""

    st.markdown(
        "<div class='section-title'>Komposisi Produksi EBT per Jenis PLT (2026)</div>",
        unsafe_allow_html=True,
    )
    st.caption("Agregasi dari hasil forecast tahun 2026 ")

    df = load_forecast_per_plt()

    # Agregasi: total produksi prediksi per jenis PLT untuk tahun 2026 saja
    df_2026 = df[df["Tahun"] == 2026]
    df_komposisi = (
        df_2026.groupby("Jenis_PLT", as_index=False)["Produksi_Prediksi"]
        .sum()
        .sort_values("Produksi_Prediksi", ascending=False)
    )

    fig = px.pie(
        df_komposisi,
        names="Jenis_PLT",
        values="Produksi_Prediksi",
        hole=0.45,
        color="Jenis_PLT",
        color_discrete_map=WARNA_PLT,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        pull=[0.02] * len(df_komposisi),
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5),
    )

    st.plotly_chart(fig, use_container_width=True)
