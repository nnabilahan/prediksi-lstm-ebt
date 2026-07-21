# Sumber Audit — Salinan Asli dari Google Colab

File di folder ini adalah **salinan tidak diubah** (unmodified) dari:
`C:\Users\LENOVO\Downloads\` (diambil 2026-07-21).

Tujuan: audit trail — versi awal pipeline LSTM sebelum diaudit/dianalisis di
`audit/results/`. File-file ini **tidak boleh diedit** — jika perlu adaptasi
agar bisa dijalankan (mis. non-Colab runner), buat salinan baru di
`audit/run_pipeline.py`, jangan ubah file di folder ini.

Isi:
- `bs_tf_lstm_fix.py` — pipeline training/evaluasi LSTM (ekspor Colab).
- `data_nasional.py` — rekonstruksi/estimasi dataset nasional (proxy cuaca
  2023 didisagregasi ke semua tahun — lihat baris 298-317).
- `data_regional.py` — rekonstruksi kolom Produksi regional Sulsel.
- `DATA_PHASE_3_REGIONAL_MODIFIED.csv` — output `data_regional.py`, dipakai
  sebagai dataset regional oleh `bs_tf_lstm_fix.py`.
- `DATA_PHASE_3_REGIONAL_FINAL.csv` — dataset regional sebelum modifikasi
  (input `data_regional.py`).
- `DATA_PHASE_2_NASIONAL_FINAL.csv` — dataset nasional dipakai untuk tahap
  pre-training di `bs_tf_lstm_fix.py`.

Catatan: data di sini adalah hasil **rekonstruksi/estimasi**, bukan data
"asli/terverifikasi" — lihat komentar kode masing-masing script untuk detail
metodologi.
