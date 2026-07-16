import pandas as pd
import streamlit as st

from utils.dataset_manager import load_dataset


def render_prediction_table(input_form: dict, df_prediksi: pd.DataFrame):
    """Menampilkan tabel detail prediksi per tahun."""

    st.markdown("<div class='section-title'>Detail Prediksi per Tahun</div>", unsafe_allow_html=True)

    jenis_plt = input_form["jenis_plt"]

    # --- Agregasi Prediksi per tahun ---
    df_prediksi_tahunan = df_prediksi.groupby("Tahun", as_index=False)["Produksi_Prediksi"].sum()
    df_prediksi_tahunan = df_prediksi_tahunan.rename(columns={"Produksi_Prediksi": "Produksi_Prediksi_GWh"})

    # --- Agregasi Aktual per tahun (jika ada data historis) ---
    df_historis = load_dataset()
    if not df_historis.empty:
        df_historis = df_historis.copy()
        df_historis["Tahun"] = pd.to_datetime(df_historis["Tanggal"]).dt.year
        if jenis_plt is not None:
            df_historis = df_historis[df_historis["Jenis_PLT"] == jenis_plt]
        df_aktual_tahunan = df_historis.groupby("Tahun", as_index=False)["Produksi"].sum()
        df_aktual_tahunan = df_aktual_tahunan.rename(columns={"Produksi": "Produksi_Aktual_GWh"})
    else:
        df_aktual_tahunan = pd.DataFrame(columns=["Tahun", "Produksi_Aktual_GWh"])

    # --- Gabungkan Aktual + Prediksi (outer join, supaya tahun historis tetap tampil) ---
    df_gabungan = pd.merge(df_aktual_tahunan, df_prediksi_tahunan, on="Tahun", how="outer").sort_values("Tahun")

    # --- Hitung perubahan year-on-year dari kolom yang tersedia (gabungan Aktual+Prediksi) ---
    df_gabungan["Produksi_Gabungan"] = df_gabungan["Produksi_Aktual_GWh"].fillna(
        df_gabungan["Produksi_Prediksi_GWh"]
    )
    df_gabungan["Perubahan_YoY"] = df_gabungan["Produksi_Gabungan"].pct_change() * 100

    df_tampil = df_gabungan[["Tahun", "Produksi_Aktual_GWh", "Produksi_Prediksi_GWh", "Perubahan_YoY"]]

    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tahun": st.column_config.NumberColumn("Tahun", format="%d"),
            "Produksi_Aktual_GWh": st.column_config.NumberColumn("Produksi Aktual (GWh)", format="%.2f"),
            "Produksi_Prediksi_GWh": st.column_config.NumberColumn("Produksi Prediksi (GWh)", format="%.2f"),
            "Perubahan_YoY": st.column_config.NumberColumn("Perubahan YoY (%)", format="%+.1f%%"),
        },
    )