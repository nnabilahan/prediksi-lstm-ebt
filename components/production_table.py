import pandas as pd
import streamlit as st

from utils.data_loader import load_forecast_per_plt
from utils.dataset_manager import load_dataset

# Tahun acuan forecast yang ditampilkan (samakan dengan metrics_cards.py)
TAHUN_FORECAST_ACUAN = 2026


def render_production_table():
    """Menampilkan tabel Produksi per Jenis Pembangkit (forecast tahun acuan)."""

    st.markdown(
        f"<div class='section-title'>Produksi per Jenis Pembangkit ({TAHUN_FORECAST_ACUAN})</div>",
        unsafe_allow_html=True,
    )

    # --- Produksi forecast per jenis PLT tahun acuan (data sudah ada, agregasi saja) ---
    df_forecast = load_forecast_per_plt()
    df_tahun = df_forecast[df_forecast["Tahun"] == TAHUN_FORECAST_ACUAN]
    df_produksi = (
        df_tahun.groupby("Jenis_PLT", as_index=False)["Produksi_Prediksi"]
        .sum()
        .rename(columns={"Produksi_Prediksi": "Produksi_GWh"})
    )

    total_produksi = df_produksi["Produksi_GWh"].sum()
    df_produksi["Persentase"] = df_produksi["Produksi_GWh"] / total_produksi * 100

    # --- Perubahan dibanding tahun terakhir data historis (dari halaman Data EBT) ---
    df_historis = load_dataset()
    if not df_historis.empty:
        tahun_historis_terakhir = pd.to_datetime(df_historis["Tanggal"]).dt.year.max()
        df_historis_terakhir = df_historis[
            pd.to_datetime(df_historis["Tanggal"]).dt.year == tahun_historis_terakhir
        ]
        produksi_historis_per_plt = df_historis_terakhir.groupby("Jenis_PLT")["Produksi"].sum()

        def _hitung_perubahan(baris):
            nilai_lama = produksi_historis_per_plt.get(baris["Jenis_PLT"])
            if nilai_lama is None or nilai_lama == 0:
                return None
            return (baris["Produksi_GWh"] - nilai_lama) / nilai_lama * 100

        df_produksi["Perubahan_YoY"] = df_produksi.apply(_hitung_perubahan, axis=1)
        label_perubahan = f"Perubahan vs {tahun_historis_terakhir}"
    else:
        df_produksi["Perubahan_YoY"] = None
        label_perubahan = "Perubahan (data historis belum tersedia)"

    df_produksi = df_produksi.sort_values("Produksi_GWh", ascending=False).reset_index(drop=True)

    st.dataframe(
        df_produksi.rename(columns={"Jenis_PLT": "Jenis Pembangkit"}),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Jenis Pembangkit": st.column_config.TextColumn("Jenis Pembangkit"),
            "Produksi_GWh": st.column_config.NumberColumn("Produksi (GWh)", format="%.2f"),
            "Persentase": st.column_config.NumberColumn("Persentase (%)", format="%.1f%%"),
            "Perubahan_YoY": st.column_config.NumberColumn(label_perubahan, format="%+.1f%%"),
        },
    )