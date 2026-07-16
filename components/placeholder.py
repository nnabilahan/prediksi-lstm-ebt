import streamlit as st


def render_placeholder(nama_halaman: str, deskripsi: str, ikon: str = "🚧"):
    """
    Menampilkan halaman placeholder yang rapi untuk menu yang belum aktif.

    Parameters
    ----------
    nama_halaman : str
        Nama halaman, contoh: "Prediksi EBT"
    deskripsi : str
        Penjelasan singkat apa yang akan ada di halaman ini nanti
    ikon : str
        Emoji ikon halaman
    """
    st.markdown(f"## {ikon} {nama_halaman}")
    st.info(
        f"Halaman **{nama_halaman}** akan dikembangkan pada tahap berikutnya.\n\n"
        f"{deskripsi}"
    )
    st.caption("Tahap saat ini hanya berfokus pada halaman Dashboard.")
