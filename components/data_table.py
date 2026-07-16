import streamlit as st


def render_data_table(df):
    """Menampilkan tabel dataset (hasil filter) sebagai st.dataframe."""

    st.markdown(
        "<div class='section-title'>Tabel Data Historis EBT</div>",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Tidak ada data yang cocok dengan filter/pencarian saat ini.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "Tanggal": st.column_config.DateColumn("Tanggal", format="DD MMM YYYY"),
            "Jenis_PLT": st.column_config.TextColumn("Jenis PLT"),
            "Produksi": st.column_config.NumberColumn("Produksi (GWh)", format="%.3f"),
            "Kapasitas": st.column_config.NumberColumn("Kapasitas (MW)", format="%.3f"),
            "Cuaca": st.column_config.NumberColumn("Cuaca", format="%.3f"),
        },
        height=380,
    )
