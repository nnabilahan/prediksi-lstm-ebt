
import pandas as pd
import streamlit as st

from utils.plt_ui_config import DAFTAR_JENIS_PLT

NAMA_BULAN = [
    "Semua Bulan", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def render_data_filter_search(df: pd.DataFrame):
   
    st.markdown(
        "<div class='section-title'>Filter &amp; Pencarian</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1, 1, 1.4, 1.6])

        daftar_tahun = ["Semua Tahun"]
        if not df.empty:
            daftar_tahun += sorted(pd.to_datetime(df["Tanggal"]).dt.year.unique().tolist())

        with col1:
            tahun_terpilih = st.selectbox("Tahun", options=daftar_tahun, index=0)
        with col2:
            bulan_terpilih = st.selectbox("Bulan", options=NAMA_BULAN, index=0)
        with col3:
            jenis_plt_terpilih = st.selectbox(
                "Jenis PLT", options=["Semua Jenis PLT"] + DAFTAR_JENIS_PLT, index=0
            )
        with col4:
            kata_kunci = st.text_input(
                "Cari",
                placeholder="Cari berdasarkan kata kunci...",
                help="Mencari di seluruh kolom (Tanggal, Jenis PLT, Produksi, Kapasitas, Cuaca).",
            )

    # --- Terapkan filter ---
    df_hasil = df.copy()

    if not df_hasil.empty:
        if tahun_terpilih != "Semua Tahun":
            df_hasil = df_hasil[pd.to_datetime(df_hasil["Tanggal"]).dt.year == tahun_terpilih]

        if bulan_terpilih != "Semua Bulan":
            nomor_bulan = NAMA_BULAN.index(bulan_terpilih)  # index sudah pas 1-12 (0 = "Semua Bulan")
            df_hasil = df_hasil[pd.to_datetime(df_hasil["Tanggal"]).dt.month == nomor_bulan]

        if jenis_plt_terpilih != "Semua Jenis PLT":
            df_hasil = df_hasil[df_hasil["Jenis_PLT"] == jenis_plt_terpilih]

        if kata_kunci:
            mask = df_hasil.astype(str).apply(
                lambda kolom: kolom.str.contains(kata_kunci, case=False, na=False)
            ).any(axis=1)
            df_hasil = df_hasil[mask]

    st.caption(f"Menampilkan **{len(df_hasil)}** dari **{len(df)}** total data.")

    return df_hasil.reset_index(drop=True)
