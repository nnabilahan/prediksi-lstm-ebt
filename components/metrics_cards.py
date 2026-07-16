"""
metrics_cards.py
=================
Komponen 4 KARTU INFORMASI (st.metric) di bagian atas Dashboard:
1. Total Produksi EBT Terakhir (data historis)
2. Jumlah Jenis PLT
3. Target RUED (target bauran energi RUED Provinsi Sulawesi Selatan)
4. Peran Forecast (penegasan bahwa forecast adalah informasi pendukung
   evaluasi RUED, bukan pengukuran langsung capaian target)

PENTING (revisi ruang lingkup): Kartu ini TIDAK LAGI menampilkan
Persentase Pencapaian atau Status Capaian terhadap target RUED dalam
satuan GWh, karena target RUED yang sesungguhnya (dokumen RUED Provinsi
Sulawesi Selatan) berbentuk target bauran energi 20% (2025) dan 32%
(2050) untuk SELURUH sumber energi provinsi -- bukan target produksi
EBT tahunan per jenis PLT dalam GWh yang bisa dibandingkan langsung
dengan hasil forecast model LSTM pada penelitian ini.
"""

import streamlit as st

from utils.data_loader import load_metadata, load_data_historis_placeholder

TARGET_RUED_2025 = "20%"
TARGET_RUED_2050 = "32%"


def render_metrics_cards():
    """Menampilkan 4 kartu st.metric dalam 4 kolom sejajar."""

    metadata = load_metadata()
    df_historis = load_data_historis_placeholder()

    # --- Kartu 1: Total produksi EBT terakhir + tren YoY ---
    df_historis_urut = df_historis.sort_values("Tahun").reset_index(drop=True)
    baris_terakhir = df_historis_urut.iloc[-1]
    total_produksi_terakhir = baris_terakhir["Total_Produksi_EBT"]
    tahun_terakhir = int(baris_terakhir["Tahun"])

    delta_yoy = None
    if len(df_historis_urut) >= 2:
        produksi_tahun_lalu = df_historis_urut.iloc[-2]["Total_Produksi_EBT"]
        if produksi_tahun_lalu:
            delta_yoy = (
                (total_produksi_terakhir - produksi_tahun_lalu) / produksi_tahun_lalu * 100
            )

    # --- Kartu 2: Jumlah jenis PLT ---
    jumlah_jenis_plt = len(metadata.get("jenis_plt", []))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Produksi EBT Terakhir",
            value=f"{total_produksi_terakhir:,.0f} GWh",
            delta=f"{delta_yoy:+.1f}%" if delta_yoy is not None else None,
            help=f"Data tahun {tahun_terakhir} (*placeholder*, menunggu data historis resmi)",
        )
        if delta_yoy is not None:
            arah = "meningkat" if delta_yoy >= 0 else "menurun"
            st.caption(f"Produksi {arah} dibanding tahun sebelumnya sebesar {abs(delta_yoy):,.1f}%.")

    with col2:
        st.metric(
            label="Jumlah Jenis PLT",
            value=f"{jumlah_jenis_plt} Jenis",
            help=", ".join(metadata.get("jenis_plt", [])),
        )
        st.caption(", ".join(metadata.get("jenis_plt", [])))

    with col3:
        st.metric(
            label="Target RUED",
            value=f"{TARGET_RUED_2025} (2025)",
            help=f"Target bauran energi RUED Provinsi Sulawesi Selatan: {TARGET_RUED_2025} pada 2025, meningkat menjadi {TARGET_RUED_2050} pada 2050.",
        )
        st.caption(f"Target bauran energi EBT, menuju {TARGET_RUED_2050} pada tahun 2050.")

    # with col4:
    #     st.metric(
    #         label="Peran Forecast",
    #         value="Informasi Pendukung",
    #         help="Forecast produksi EBT sektor kelistrikan berperan sebagai informasi pendukung evaluasi RUED, bukan pengukuran langsung capaian target.",
    #     )
    #     st.caption("Bukan pengukuran langsung capaian RUED — lihat halaman Analisis Kesesuaian RUED.")

    st.caption(
        "ℹ️ Ruang lingkup: analisis EBT **sektor kelistrikan**. Hasil forecast digunakan sebagai "
        "informasi pendukung evaluasi implementasi RUED, bukan sebagai pengukuran langsung "
        "terhadap capaian target bauran energi RUED."
    )