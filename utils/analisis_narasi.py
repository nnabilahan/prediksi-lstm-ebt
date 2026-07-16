"""
analisis_narasi.py
====================
Util MURNI untuk keperluan penyajian (UI) & interpretasi naratif pada
halaman "Analisis Kesesuaian terhadap Target RUED".

PENTING (batasan lingkup):
- File ini TIDAK mengubah data penelitian, model LSTM, atau hasil
  forecasting apa pun. Fungsi di sini hanya MEMETAKAN status numerik
  yang sudah dihitung oleh utils/rued_loader.py (Tercapai/Mendekati/
  Defisit, berdasarkan Persentase_Capaian) menjadi label & catatan
  naratif yang sesuai ruang lingkup penelitian skripsi (evaluasi
  kesesuaian arah kebijakan, BUKAN penilaian resmi capaian RUED).
"""

# Status teknis (dari rued_loader.klasifikasi_status) -> label naratif
STATUS_ANALISIS = {
    "Tercapai": "Sesuai Tren",
    "Mendekati": "Mendekati Target",
    "Defisit": "Perlu Evaluasi",
}

# Status teknis -> catatan singkat per baris tabel
CATATAN_ANALISIS = {
    "Tercapai": "Relatif Stabil",
    "Mendekati": "Mendekati Target",
    "Defisit": "Perlu Peningkatan Produksi",
}

# Status teknis -> ikon (konsisten di kartu, tabel, & panel ringkasan)
IKON_STATUS_ANALISIS = {
    "Tercapai": "🟢",
    "Mendekati": "🟡",
    "Defisit": "🔴",
}

# Status teknis -> kalimat penjelasan singkat untuk kartu "Status Analisis"
PENJELASAN_STATUS = {
    "Tercapai": "Forecast produksi EBT sektor kelistrikan sudah sejalan dengan arah target RUED.",
    "Mendekati": "Forecast produksi EBT mendekati acuan target RUED, namun belum sepenuhnya sejalan.",
    "Defisit": "Forecast produksi EBT masih perlu dievaluasi lebih lanjut terhadap arah target RUED.",
}


def get_status_analisis(status_teknis: str) -> str:
    """Label naratif (Sesuai Tren / Mendekati Target / Perlu Evaluasi)."""
    return STATUS_ANALISIS.get(status_teknis, "Perlu Evaluasi")


def get_catatan_analisis(status_teknis: str) -> str:
    """Catatan singkat per baris tabel."""
    return CATATAN_ANALISIS.get(status_teknis, "-")


def get_ikon_status_analisis(status_teknis: str) -> str:
    return IKON_STATUS_ANALISIS.get(status_teknis, "⚪")


def get_penjelasan_status(status_teknis: str) -> str:
    """Kalimat penjelasan singkat untuk kartu Status Analisis."""
    return PENJELASAN_STATUS.get(status_teknis, "")