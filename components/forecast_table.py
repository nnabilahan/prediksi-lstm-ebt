
import streamlit as st

from utils.data_loader import load_forecast_tahunan_total


def render_forecast_table():
    """Menampilkan tabel ringkasan total produksi EBT per tahun (2026-2028)."""

    st.markdown(
        "<div class='section-title'>Ringkasan Total Forecast per Tahun</div>",
        unsafe_allow_html=True,
    )
    st.caption("Total produksi EBT (GWh) hasil penjumlahan forecast bulanan per tahun.")

    df_tahunan = load_forecast_tahunan_total()

    # Hitung persentase perubahan tahun ke tahun (YoY) untuk konteks tambahan
    df_tahunan = df_tahunan.copy()
    df_tahunan["Perubahan (%)"] = df_tahunan["Total_Produksi_EBT"].pct_change() * 100

    # Format tampilan tabel agar rapi
    df_tampil = df_tahunan.rename(columns={
        "Tahun": "Tahun",
        "Total_Produksi_EBT": "Total Produksi EBT (GWh)",
    })

    st.dataframe(
        df_tampil.style.format({
            "Total Produksi EBT (GWh)": "{:,.2f}",
            "Perubahan (%)": "{:+.2f}%",
        }, na_rep="-"),
        use_container_width=True,
        hide_index=True,
    )
