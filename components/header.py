
import streamlit as st

def render_header():
    """Menampilkan header utama di bagian atas halaman Dashboard."""
    st.markdown(
        """
        <div class="app-header">
            <h1>Dashboard Monitoring &amp; Prediksi EBT</h1>
            <p>
                Sistem Pendukung Pemantauan dan Prediksi Produksi Energi Baru Terbarukan (EBT)
                Sektor Kelistrikan &mdash; Dinas Energi dan Sumber Daya Mineral
                Provinsi Sulawesi Selatan, berbasis model Deep Learning LSTM.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
