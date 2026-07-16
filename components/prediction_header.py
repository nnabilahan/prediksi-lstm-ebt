import streamlit as st


def render_prediction_header():
    """Menampilkan header di bagian atas halaman Prediksi EBT."""
    st.markdown(
        """
        <div class="app-header">
            <h1>🔎 Prediksi Energi Baru Terbarukan</h1>
            <p>
                Jalankan inferensi model LSTM yang sudah dilatih untuk memperkirakan
                produksi EBT satu jenis pembangkit berdasarkan kapasitas dan kondisi cuaca
                yang Anda masukkan. Halaman ini tidak melakukan pelatihan ulang maupun
                forecasting jangka panjang &mdash; lihat menu <b>Forecasting</b> untuk itu.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
