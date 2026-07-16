import streamlit as st

from utils.plt_ui_config import DAFTAR_JENIS_PLT

OPSI_TOTAL = "Seluruh Jenis PLT (Total)"
TAHUN_TERSEDIA = [2026, 2027, 2028]  # cakupan forecast yang sudah ada


def render_prediction_form():
    """
    Menampilkan form pemilihan Jenis Pembangkit & periode prediksi.

    Returns
    -------
    dict berisi (jenis_plt, tahun_awal, tahun_akhir) HANYA jika tombol
    submit ditekan & valid. Selain itu mengembalikan None.
    jenis_plt bernilai None jika user memilih "Seluruh Jenis PLT (Total)".
    """
    st.markdown("<div class='section-title'>Form Input Prediksi</div>", unsafe_allow_html=True)

    with st.container(border=True):
        jenis_plt_pilihan = st.selectbox(
            "Jenis Pembangkit",
            options=[OPSI_TOTAL] + DAFTAR_JENIS_PLT,
            index=0,
            help="Pilih satu jenis PLT, atau 'Total' untuk seluruh jenis PLT digabung.",
        )

        mode_periode = st.radio(
            "Mode Periode",
            options=["Rentang Tahun (Awal - Akhir)", "Tahun Tertentu"],
            index=0,
            horizontal=True,
        )

        if mode_periode == "Rentang Tahun (Awal - Akhir)":
            col1, col2 = st.columns(2)
            with col1:
                tahun_awal = st.selectbox("Tahun Awal Prediksi", options=TAHUN_TERSEDIA, index=0)
            with col2:
                tahun_akhir = st.selectbox(
                    "Tahun Akhir Prediksi", options=TAHUN_TERSEDIA, index=len(TAHUN_TERSEDIA) - 1
                )
        else:
            tahun_tunggal = st.selectbox("Pilih Tahun", options=TAHUN_TERSEDIA, index=0)
            tahun_awal = tahun_akhir = tahun_tunggal

        submit = st.button("🔍 Prediksi Produksi EBT", use_container_width=True)

    if submit:
        if tahun_awal > tahun_akhir:
            st.warning("⚠️ Tahun Awal tidak boleh lebih besar dari Tahun Akhir.")
            return None

        return {
            "jenis_plt": None if jenis_plt_pilihan == OPSI_TOTAL else jenis_plt_pilihan,
            "tahun_awal": tahun_awal,
            "tahun_akhir": tahun_akhir,
        }

    return None