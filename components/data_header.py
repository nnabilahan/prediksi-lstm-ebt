
import streamlit as st


def render_data_header():
    """Menampilkan header di bagian atas halaman Data EBT."""
    st.markdown(
        """
        <div class="app-header">
            <h1>Data EBT &mdash; Pengelolaan Data Historis</h1>
            <p>
                Kelola data historis produksi Energi Baru Terbarukan (EBT) sektor kelistrikan:
                tambah, ubah, hapus, impor, dan ekspor data. Data yang disimpan di halaman ini
                dapat digunakan untuk pelatihan model berikutnya secara manual (bukan otomatis).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
