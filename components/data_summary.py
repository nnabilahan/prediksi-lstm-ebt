import streamlit as st

from utils.dataset_manager import ringkasan_dataset


def render_data_summary(df):
    """Menampilkan 3 kartu ringkasan dataset."""
    st.markdown(
        "<div class='section-title'>Ringkasan Dataset</div>",
        unsafe_allow_html=True,
    )

    ringkasan = ringkasan_dataset(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Data", f"{ringkasan['jumlah_data']:,}")
    col2.metric("Jumlah Jenis PLT", ringkasan["jumlah_jenis_plt"])
    if ringkasan["tahun_min"] == ringkasan["tahun_max"]:
        rentang = f"{ringkasan['tahun_min']}"
    else:
        rentang = f"{ringkasan['tahun_min']} - {ringkasan['tahun_max']}"
    col3.metric("Rentang Tahun", rentang)
