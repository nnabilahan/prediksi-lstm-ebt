import io

import pandas as pd
import streamlit as st

from utils.dataset_manager import (
    periksa_skema_impor,
    validasi_baris_impor,
    proses_impor,
)


def _baca_file_upload(file_upload) -> pd.DataFrame:
    """Membaca file upload (CSV atau Excel) menjadi DataFrame."""
    nama = file_upload.name.lower()
    if nama.endswith(".csv"):
        return pd.read_csv(file_upload)
    return pd.read_excel(file_upload)


def render_data_import(df_saat_ini: pd.DataFrame):
    """Menampilkan panel impor dataset dari file CSV/Excel."""

    with st.expander("Impor Dataset (CSV/Excel)", expanded=False):
        st.caption(
            f"Skema kolom yang dibutuhkan: **Tanggal, Jenis_PLT, Produksi, Kapasitas, Cuaca** "
            f"(kolom ID opsional, akan dibuat otomatis)."
        )

        file_upload = st.file_uploader("Pilih file CSV atau Excel", type=["csv", "xlsx", "xls"])

        if file_upload is None:
            return

        try:
            df_mentah = _baca_file_upload(file_upload)
        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
            return

        error_skema = periksa_skema_impor(df_mentah)
        if error_skema:
            for e in error_skema:
                st.error(f"❌ {e}")
            return

        df_valid, pesan_dilewati = validasi_baris_impor(df_mentah)

        col1, col2 = st.columns(2)
        col1.metric("Baris Valid", len(df_valid))
        col2.metric("Baris Dilewati", len(pesan_dilewati))

        if pesan_dilewati:
            with st.expander(f"⚠️ Lihat {len(pesan_dilewati)} baris yang dilewati"):
                for p in pesan_dilewati[:50]:
                    st.caption(f"- {p}")
                if len(pesan_dilewati) > 50:
                    st.caption(f"... dan {len(pesan_dilewati) - 50} baris lainnya.")

        if df_valid.empty:
            st.warning("⚠️ Tidak ada baris valid untuk diimpor.")
            return

        st.markdown("**Pratinjau data valid:**")
        st.dataframe(df_valid.head(10), use_container_width=True, hide_index=True)

        mode = st.radio(
            "Mode Impor",
            options=["Gabung dengan data yang ada", "Ganti seluruh dataset"],
            index=0,
            help=(
                "Gabung: baris baru ditambahkan, baris duplikat (Tanggal+Jenis PLT sama "
                "dengan data yang sudah ada) otomatis dilewati. "
                "Ganti: SELURUH dataset saat ini akan digantikan oleh isi file ini."
            ),
        )

        if mode == "Ganti seluruh dataset":
            st.warning(f"⚠️ Mode ini akan MENGHAPUS seluruh {len(df_saat_ini)} data saat ini dan menggantinya.")

        if st.button("✅ Proses Impor", type="primary"):
            hasil = proses_impor(df_valid, mode)
            st.success(
                f"✅ Impor selesai: {hasil['jumlah_ditambahkan']} data ditambahkan, "
                f"{hasil['jumlah_dilewati_duplikat']} data dilewati (duplikat dengan data yang sudah ada)."
            )
            st.info("ℹ️ Data tersimpan ke dataset. Tidak ada pelatihan model yang dipicu secara otomatis.")
            st.rerun()


def render_data_export(df_terfilter: pd.DataFrame):
    """Menampilkan tombol ekspor dataset (hasil filter aktif) ke CSV/Excel."""

    with st.expander("📥 Ekspor Dataset", expanded=False):
        st.caption(f"Akan mengekspor **{len(df_terfilter)}** baris data sesuai filter yang sedang aktif.")

        col1, col2 = st.columns(2)

        with col1:
            csv_bytes = df_terfilter.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Unduh sebagai CSV",
                data=csv_bytes,
                file_name="data_historis_ebt_export.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_terfilter.to_excel(writer, index=False, sheet_name="Data EBT")
            st.download_button(
                "⬇️ Unduh sebagai Excel",
                data=buffer.getvalue(),
                file_name="data_historis_ebt_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
