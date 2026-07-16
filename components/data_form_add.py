
import datetime

import streamlit as st

from utils.dataset_manager import tambah_data
from utils.plt_ui_config import DAFTAR_JENIS_PLT, SATUAN_KAPASITAS, SATUAN_PRODUKSI, get_konfigurasi_ui

PLACEHOLDER_PLT = "-- Pilih Jenis PLT --"


def render_data_form_add():
    """Menampilkan form untuk menambahkan satu baris data baru ke dataset."""

    with st.expander("➕ Tambah Data Baru", expanded=False):
        # Jenis PLT di luar form supaya label Cuaca langsung menyesuaikan
        jenis_plt = st.selectbox(
            "Jenis PLT", options=[PLACEHOLDER_PLT] + DAFTAR_JENIS_PLT, index=0, key="tambah_jenis_plt"
        )
        plt_terpilih = jenis_plt != PLACEHOLDER_PLT
        konfigurasi_ui = get_konfigurasi_ui(jenis_plt) if plt_terpilih else {
            "label_cuaca": "Variabel Cuaca", "satuan_cuaca": "",
        }

        with st.form("form_tambah_data", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tanggal = st.date_input(
                    "Tanggal",
                    value=None,
                    min_value=datetime.date(2020, 1, 1),
                    max_value=datetime.date(2030, 12, 31),
                )
                produksi = st.number_input(
                    f"Produksi ({SATUAN_PRODUKSI})", min_value=0.0, value=None, step=0.1
                )
            with col2:
                kapasitas = st.number_input(
                    f"Kapasitas ({SATUAN_KAPASITAS})", min_value=0.0, value=None, step=0.1
                )
                label_cuaca = f"{konfigurasi_ui['label_cuaca']} ({konfigurasi_ui['satuan_cuaca']})"
                cuaca = st.number_input(label_cuaca, min_value=0.0, value=None, step=0.1)

            submit = st.form_submit_button(" Simpan Data Baru", use_container_width=True)

        if submit:
            if not plt_terpilih:
                st.warning(" Silakan pilih Jenis PLT terlebih dahulu.")
                return

            berhasil, pesan = tambah_data(tanggal, jenis_plt, produksi, kapasitas, cuaca)
            if berhasil:
                st.success(f"✅ {pesan[0]}")
                st.rerun()
            else:
                for p in pesan:
                    st.error(f"❌ {p}")
