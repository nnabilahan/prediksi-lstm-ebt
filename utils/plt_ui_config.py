"""
plt_ui_config.py
==================
Konfigurasi TAMPILAN (label & satuan) untuk tiap jenis PLT pada form
Prediksi EBT. Dipisah dari config/konfigurasi_model.json (yang berisi
parameter MODEL) karena file ini murni untuk kebutuhan UI/UX -
supaya field "Cuaca" yang generik di model bisa ditampilkan dengan
label yang kontekstual bagi pengguna (radiasi matahari, curah hujan,
atau kecepatan angin) sesuai karakteristik masing-masing jenis PLT.

CATATAN: metadata_penelitian.json / konfigurasi_model.json menyimpan
variabel cuaca dengan nama generik "Cuaca" untuk semua jenis PLT.
Pemetaan label kontekstual di bawah ini didasarkan pada karakteristik
umum tiap jenis pembangkit (PLTS/PLTS Atap/PLT Hybrid -> radiasi matahari,
PLTA/PLTM/PLTMH -> curah hujan, PLTB -> kecepatan angin).
"""

# Daftar jenis PLT sesuai key di config/konfigurasi_model.json
DAFTAR_JENIS_PLT = [
    "PLTA",
    "PLTB",
    "PLTM",
    "PLTMH",
    "PLTS",
    "PLTS Atap",
    "PLT Hybrid",
]

# Label & satuan variabel cuaca per jenis PLT
KONFIGURASI_UI_PLT = {
    "PLTA": {
        "label_cuaca": "Curah Hujan",
        "satuan_cuaca": "mm",
        "help_cuaca": "Curah hujan rata-rata bulanan di area DAS pembangkit.",
    },
    "PLTB": {
        "label_cuaca": "Kecepatan Angin",
        "satuan_cuaca": "m/s",
        "help_cuaca": "Kecepatan angin rata-rata bulanan di lokasi pembangkit.",
    },
    "PLTM": {
        "label_cuaca": "Curah Hujan",
        "satuan_cuaca": "mm",
        "help_cuaca": "Curah hujan rata-rata bulanan di area DAS pembangkit.",
    },
    "PLTMH": {
        "label_cuaca": "Curah Hujan",
        "satuan_cuaca": "mm",
        "help_cuaca": "Curah hujan rata-rata bulanan di area DAS pembangkit.",
    },
    "PLTS": {
        "label_cuaca": "Radiasi Matahari",
        "satuan_cuaca": "kWh/m²",
        "help_cuaca": "Rata-rata radiasi matahari harian dalam sebulan.",
    },
    "PLTS Atap": {
        "label_cuaca": "Radiasi Matahari",
        "satuan_cuaca": "kWh/m²",
        "help_cuaca": "Rata-rata radiasi matahari harian dalam sebulan.",
    },
    "PLT Hybrid": {
        "label_cuaca": "Radiasi Matahari",
        "satuan_cuaca": "kWh/m²",
        "help_cuaca": "Kombinasi sumber energi; radiasi matahari sebagai indikator cuaca utama.",
    },
}

# Satuan produksi & kapasitas.
# CATATAN: metadata_penelitian.json & konfigurasi_model.json TIDAK menyebutkan
# satuan secara eksplisit. GWh (produksi) & MW (kapasitas) dipakai sebagai
# asumsi satuan yang lazim dipakai Dinas ESDM, konsisten dengan satuan yang
# sudah dipakai di halaman Dashboard. Sesuaikan di sini jika satuan asli
# data penelitian berbeda.
SATUAN_PRODUKSI = "GWh"
SATUAN_KAPASITAS = "MW"


def get_konfigurasi_ui(jenis_plt: str) -> dict:
    """Mengambil label & satuan variabel cuaca untuk satu jenis PLT."""
    return KONFIGURASI_UI_PLT[jenis_plt]
