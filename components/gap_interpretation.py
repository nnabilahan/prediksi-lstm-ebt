"""
gap_interpretation.py
========================
Komponen panel "Ringkasan Analisis": menyusun ringkasan otomatis
forecast produksi EBT untuk tahun & konteks terpilih, DISERTAI catatan
tegas bahwa hasil ini adalah informasi pendukung evaluasi RUED -- bukan
pengukuran langsung capaian target RUED (yang berbentuk % bauran
energi, bukan GWh).
"""

import streamlit as st

from utils.forecast_ringkasan import get_forecast_tahunan


def render_gap_interpretation(filter_input: dict, baris: dict):
    """Menampilkan panel Ringkasan Analisis untuk tahun & konteks yang aktif di filter."""

    st.markdown("<div class='section-title'>Ringkasan Analisis</div>", unsafe_allow_html=True)

    label_konteks = (
        filter_input["jenis_plt"] if filter_input["mode"] == "Per Jenis PLT" else "seluruh jenis PLT (Total EBT)"
    )
    tahun = filter_input["tahun"]
    forecast = baris["Forecast_GWh"]

    df = get_forecast_tahunan(filter_input["mode"], filter_input["jenis_plt"])
    tahun_sebelumnya = tahun - 1
    baris_sebelumnya = df[df["Tahun"] == tahun_sebelumnya]

    kalimat_tren = ""
    if not baris_sebelumnya.empty:
        forecast_sebelumnya = baris_sebelumnya.iloc[0]["Forecast_GWh"]
        if forecast_sebelumnya:
            selisih_persen = (forecast - forecast_sebelumnya) / forecast_sebelumnya * 100
            arah = "meningkat" if selisih_persen >= 0 else "menurun"
            kalimat_tren = (
                f" Dibanding tahun {tahun_sebelumnya}, forecast produksi EBT **{arah}** "
                f"sebesar **{abs(selisih_persen):,.1f}%** ({forecast_sebelumnya:,.2f} GWh &rarr; {forecast:,.2f} GWh)."
            )

    st.info(
        f"Forecast produksi EBT sektor kelistrikan untuk **{label_konteks}** pada tahun "
        f"**{tahun}** adalah **{forecast:,.2f} GWh**, hasil prediksi model LSTM."
        + kalimat_tren,
        icon="📊",
    )

    st.caption(
        "Hasil prediksi ini digunakan sebagai **informasi pendukung** evaluasi implementasi RUED, "
        "**bukan sebagai pengukuran langsung** terhadap capaian target bauran energi RUED "
        "(20% tahun 2025, 32% tahun 2050)."
    )