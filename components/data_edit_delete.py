
import datetime

import pandas as pd
import streamlit as st

from utils.dataset_manager import ubah_data, hapus_data
from utils.plt_ui_config import DAFTAR_JENIS_PLT, SATUAN_KAPASITAS, SATUAN_PRODUKSI, get_konfigurasi_ui


def _label_baris(baris: pd.Series) -> str:
    """Format label baris untuk selectbox pemilihan data."""
    tanggal = pd.Timestamp(baris["Tanggal"]).strftime("%d %b %Y")
    return f"#{int(baris['ID'])} - {tanggal} - {baris['Jenis_PLT']} - {baris['Produksi']:.2f} GWh"


def render_data_edit_delete(df: pd.DataFrame):
    """Menampilkan panel edit & hapus data berdasarkan pemilihan ID."""

    with st.expander(" Edit / Hapus Data", expanded=False):
        if df.empty:
            st.info("Belum ada data untuk diedit/dihapus.")
            return

        df_urut = df.sort_values("Tanggal", ascending=False).reset_index(drop=True)
        opsi_label = [_label_baris(baris) for _, baris in df_urut.iterrows()]

        label_terpilih = st.selectbox("Pilih Data (berdasarkan ID)", options=opsi_label, key="edit_pilih_baris")
        id_terpilih = int(label_terpilih.split(" - ")[0].replace("#", ""))
        baris_data = df_urut[df_urut["ID"] == id_terpilih].iloc[0]

        konfigurasi_ui = get_konfigurasi_ui(baris_data["Jenis_PLT"])

        # --- Form edit, terisi otomatis dari data terpilih ---
        with st.form("form_edit_data"):
            col1, col2 = st.columns(2)
            with col1:
                tanggal_baru = st.date_input(
                    "Tanggal",
                    value=pd.Timestamp(baris_data["Tanggal"]).date(),
                    min_value=datetime.date(2020, 1, 1),
                    max_value=datetime.date(2030, 12, 31),
                )
                jenis_plt_baru = st.selectbox(
                    "Jenis PLT",
                    options=DAFTAR_JENIS_PLT,
                    index=DAFTAR_JENIS_PLT.index(baris_data["Jenis_PLT"]),
                )
                produksi_baru = st.number_input(
                    f"Produksi ({SATUAN_PRODUKSI})", min_value=0.0, value=float(baris_data["Produksi"]), step=0.1
                )
            with col2:
                kapasitas_baru = st.number_input(
                    f"Kapasitas ({SATUAN_KAPASITAS})", min_value=0.0, value=float(baris_data["Kapasitas"]), step=0.1
                )
                cuaca_baru = st.number_input(
                    f"{konfigurasi_ui['label_cuaca']} ({konfigurasi_ui['satuan_cuaca']})",
                    min_value=0.0, value=float(baris_data["Cuaca"]), step=0.1,
                )

            simpan = st.form_submit_button("Simpan Perubahan", use_container_width=True)

        if simpan:
            berhasil, pesan = ubah_data(
                id_terpilih, tanggal_baru, jenis_plt_baru, produksi_baru, kapasitas_baru, cuaca_baru
            )
            if berhasil:
                st.success(f"✅ {pesan[0]}")
                st.rerun()
            else:
                for p in pesan:
                    st.error(f"❌ {p}")

        st.divider()

        # --- Hapus data: konfirmasi 2 langkah ---
        st.markdown("**Hapus Data Terpilih**")

        kunci_konfirmasi = "id_konfirmasi_hapus"

        if st.session_state.get(kunci_konfirmasi) != id_terpilih:
            if st.button("🗑️ Hapus Data Ini", key="tombol_hapus_awal"):
                st.session_state[kunci_konfirmasi] = id_terpilih
                st.rerun()
        else:
            st.warning(
                f"Yakin ingin menghapus data **#{id_terpilih} - {baris_data['Jenis_PLT']} - "
                f"{pd.Timestamp(baris_data['Tanggal']).strftime('%d %b %Y')}**? Tindakan ini tidak dapat dibatalkan."
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Ya, Hapus Data", key="tombol_konfirmasi_hapus", use_container_width=True):
                    berhasil, pesan = hapus_data(id_terpilih)
                    del st.session_state[kunci_konfirmasi]
                    if berhasil:
                        st.success(f"✅ {pesan[0]}")
                    else:
                        st.error(f"❌ {pesan[0]}")
                    st.rerun()
            with col_b:
                if st.button("↩️ Batal", key="tombol_batal_hapus", use_container_width=True):
                    del st.session_state[kunci_konfirmasi]
                    st.rerun()
