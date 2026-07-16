"""
4_Data_EBT.py
===============
Halaman DATA EBT: merangkai (orchestrate) komponen header, ringkasan,
filter/pencarian, tabel, tambah data, edit/hapus data, dan impor/ekspor.
Sama seperti halaman lain, file ini HANYA merangkai -- seluruh logika
baca/tulis dataset ada di utils/dataset_manager.py.

Alur:
1. Tampilkan header halaman
2. Baca dataset TERKINI (selalu fresh dari file, bukan cache)
3. Tampilkan ringkasan (jumlah data, jumlah jenis PLT, rentang tahun)
4. Tampilkan filter & pencarian -> dataset terfilter
5. Tampilkan tabel dataset terfilter
6. Tampilkan form tambah data baru
7. Tampilkan panel edit/hapus data
8. Tampilkan panel impor & ekspor dataset
"""

import streamlit as st

from components.data_header import render_data_header
from components.data_summary import render_data_summary
from components.data_filter_search import render_data_filter_search
from components.data_table import render_data_table
from components.data_form_add import render_data_form_add
from components.data_edit_delete import render_data_edit_delete
from components.data_import_export import render_data_import, render_data_export
from utils.dataset_manager import load_dataset


def render():
    render_data_header()

    # Dataset selalu dibaca ulang dari file (bukan cache) karena bersifat mutable
    df = load_dataset()

    render_data_summary(df)
    st.divider()

    df_filtered = render_data_filter_search(df)
    render_data_table(df_filtered)

    st.divider()
    st.markdown(
        "<div class='section-title'>Kelola Data</div>",
        unsafe_allow_html=True,
    )
    render_data_form_add()
    render_data_edit_delete(df)
    render_data_import(df)

    st.divider()
    render_data_export(df_filtered)

    st.divider()
    st.info(
        "ℹ️ Perubahan pada data (tambah/ubah/hapus/impor) langsung tersimpan ke "
        "`data/data_historis_ebt.csv`, namun **tidak memicu pelatihan ulang model** "
        "secara otomatis. Untuk melatih ulang model dengan data terbaru, unduh "
        "dataset ini (fitur Ekspor) lalu gunakan secara manual di pipeline Google Colab."
    )
