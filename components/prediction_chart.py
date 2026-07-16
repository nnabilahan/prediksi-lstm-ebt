"""
prediction_chart.py
=====================
Komponen GRAFIK Aktual vs Prediksi (revisi): garis Aktual dari dataset
historis (data/data_historis_ebt.csv, dikelola di halaman Data EBT) dan
garis Prediksi dari data forecast yang sudah tersedia, sesuai filter
Jenis Pembangkit & periode yang dipilih.

Garis Aktual & Prediksi disambung di satu titik peralihan (titik akhir
data aktual) agar transisi terlihat kontinu, tidak terputus.
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from utils.dataset_manager import load_dataset
from utils.styling import WARNA_PLT, COLOR_PRIMARY_BLUE


def render_prediction_chart(input_form: dict, df_prediksi: pd.DataFrame):
    """Menampilkan line chart Aktual (historis) vs Prediksi (forecast)."""

    jenis_plt = input_form["jenis_plt"]
    label_konteks = jenis_plt if jenis_plt else "Seluruh Jenis PLT (Total)"

    st.markdown(
        f"<div class='section-title'>Grafik Aktual vs Prediksi &mdash; {label_konteks}</div>",
        unsafe_allow_html=True,
    )

    # --- Data Aktual (historis) ---
    df_historis = load_dataset()
    if not df_historis.empty:
        df_historis = df_historis.copy()
        df_historis["Tanggal"] = pd.to_datetime(df_historis["Tanggal"])
        if jenis_plt is not None:
            df_historis = df_historis[df_historis["Jenis_PLT"] == jenis_plt]
        df_historis_bulanan = (
            df_historis.groupby("Tanggal", as_index=False)["Produksi"].sum().sort_values("Tanggal")
        )
    else:
        df_historis_bulanan = pd.DataFrame(columns=["Tanggal", "Produksi"])

    warna = WARNA_PLT.get(jenis_plt, "#1B5E20") if jenis_plt else "#1B5E20"

    # --- Sambungkan Aktual & Prediksi agar garis tidak terputus ---
    # Titik terakhir data aktual dipakai juga sebagai titik AWAL garis
    # Prediksi, supaya kedua garis bertemu persis di titik peralihan.
    if not df_historis_bulanan.empty:
        titik_sambung = pd.DataFrame({
            "Tanggal": [df_historis_bulanan["Tanggal"].iloc[-1]],
            "Produksi_Prediksi": [df_historis_bulanan["Produksi"].iloc[-1]],
        })
        df_prediksi_plot = pd.concat([titik_sambung, df_prediksi], ignore_index=True)
    else:
        df_prediksi_plot = df_prediksi

    fig = go.Figure()

    if not df_historis_bulanan.empty:
        fig.add_trace(
            go.Scatter(
                x=df_historis_bulanan["Tanggal"],
                y=df_historis_bulanan["Produksi"],
                mode="lines",
                name="Aktual (Historis)",
                line=dict(color=warna, width=2.5),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df_prediksi_plot["Tanggal"],
            y=df_prediksi_plot["Produksi_Prediksi"],
            mode="lines",
            name="Prediksi (Forecast)",
            line=dict(color=COLOR_PRIMARY_BLUE, width=2.5, dash="dot"),
        )
    )

    fig.update_layout(
        xaxis_title="Periode",
        yaxis_title="Produksi (GWh)",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        height=400,
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)