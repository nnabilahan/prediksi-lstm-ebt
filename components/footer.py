import streamlit as st

from utils.data_loader import load_metadata


def render_footer():
    """Menampilkan footer di bagian paling bawah halaman Dashboard."""

    metadata = load_metadata()
    judul_penelitian = metadata.get("judul_penelitian", "-")
    metodologi = metadata.get("metodologi", "-")

    st.markdown(
        f"""
        <div class="app-footer">
            <b>{judul_penelitian}</b><br>
            <br>&copy; 2026 &mdash; Penelitian Prediksi EBT Provinsi Sulawesi Selatan
        </div>
        """,
        unsafe_allow_html=True,
    )
