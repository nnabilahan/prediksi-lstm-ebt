import streamlit as st

from utils.plt_ui_config import DAFTAR_JENIS_PLT

DAFTAR_TAHUN = [2026, 2027, 2028]


def render_gap_filter():
    """
    Menampilkan filter tahun & mode analisis dalam 1 baris kolom.

    Returns
    -------
    dict berisi:
        - tahun (int): tahun yang dipilih
        - mode (str): "Total Produksi EBT" atau "Per Jenis PLT"
        - jenis_plt (str | None): jenis PLT terpilih (hanya jika mode = "Per Jenis PLT")
    """
    st.markdown(
        "<div class='section-title'>Filter Analisis</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            tahun = st.selectbox("Periode / Tahun", options=DAFTAR_TAHUN, index=0)

        with col2:
            mode = st.selectbox(
                "Jenis Analisis",
                options=["Total Produksi EBT", "Per Jenis PLT"],
                index=0,
                help="Total: seluruh jenis PLT dijumlahkan. Per Jenis PLT: analisis satu jenis pembangkit.",
            )

        jenis_plt = None
        with col3:
            if mode == "Per Jenis PLT":
                jenis_plt = st.selectbox("Pilih Jenis PLT", options=DAFTAR_JENIS_PLT, index=0)
            else:
                st.selectbox(
                    "Pilih Jenis PLT",
                    options=["(seluruh jenis PLT dijumlahkan)"],
                    index=0,
                    disabled=True,
                )

    return {"tahun": tahun, "mode": mode, "jenis_plt": jenis_plt}
