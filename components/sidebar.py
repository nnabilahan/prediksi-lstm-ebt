import streamlit as st

# Daftar menu navigasi beserta ikonnya (konsisten)
DAFTAR_MENU = [
    ("Dashboard", "🏠"),
    ("Prediksi EBT", "⚡"),
    ("Gap Analysis RUED", "📈"),
    ("Data EBT", "🗃️"),
    ("Laporan", "📝"),
]



def render_sidebar():
    # Aset logo (sesuai folder assets/)
    logo_path = "assets/Logo_Sulsel.png"

    # Styling khusus sidebar (tanpa mengubah logika navigasi)
    st.markdown(
        """
        <style>
        /* Sidebar container */
        section[data-testid="stSidebar"] {
            background: #ffffff;
        }

        /* Radio menu: teks abu-abu */
        div[data-testid="stRadio"] label {
            color: #6B7280;
            font-weight: 600;
            border-radius: 10px;
        }
   
        /* Hover halus */
        div[data-testid="stRadio"] label:hover {
            background: #F3F4F6;
            transition: background 120ms ease-in-out;
        }

        /* Indikator aktif: garis hijau di kiri + teks hijau tua */
        div[data-testid="stRadio"] input:checked + div {
            border-left: 4px solid #1B5E20;
            padding-left: 12px;
        }

        div[data-testid="stRadio"] input:checked + div span {
            color: #1B5E20;
        }

        /* Caption kecil */
        .siprebar-caption {
            color: #6B7280;
            font-size: 12px;
        }

        /* Logo: taruh di tengah + agak dekat ke atas */
        .siprebar-logo-wrap {
            display: flex;
            justify-content: center;
            margin-top: -6px; /* "agak kenaan" */
        }
        .siprebar-logo {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # --- Identitas aplikasi ---
        st.markdown(
            f"""
            <div class='siprebar-logo-wrap'>
                <img class='siprebar-logo' src='{logo_path}' width='110' />
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style='text-align:center; margin-top: 6px;'>
                <div style='font-size:20px; font-weight:900; color:#111827; letter-spacing:0.2px;'>SIPREBAR</div>
                <div style='font-size:12px; color:#1B5E20; font-weight:700; margin-top:2px;'>Sistem Prediksi Energi Baru Terbarukan</div>
                <div class='siprebar-caption' style='margin-top:6px; line-height:1.2;'>
                    Dinas Energi dan Sumber Daya Mineral<br/>Provinsi Sulawesi Selatan
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # --- Menu navigasi ---
        label_menu = [f"{ikon}  {nama}" for (nama, ikon) in DAFTAR_MENU]
        pilihan = st.radio(
            "Menu Navigasi",
            options=label_menu,
            index=0,
            label_visibility="collapsed",
        )

        # Ambil nama menu tanpa ikon (lebih robust dari split berbasis spasi)
        # pilihan format: "{ikon}  {nama}"
        _, _, menu_terpilih = pilihan.partition("  ")



        st.divider()

        # --- Footer sidebar ---
        st.caption("Versi 1.0")
        st.caption("Penelitian Skripsi UIN Alauddin Makassar")

        return menu_terpilih

