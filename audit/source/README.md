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

---

## Dataset V2/V3 (rekonstruksi ulang) — dataset yang DIPAKAI sekarang

Dua file berikut menggantikan dataset lama di atas sebagai input pipeline.
Dataset lama **sengaja tidak dihapus** supaya hasil run sebelumnya di
`audit/results/` tetap bisa ditelusuri sebagai pembanding.

- `DATA_REGIONAL_DISAGREGASI_V3.csv` — regional Sulsel, 2023–2025,
  108 baris (3 kategori × 3 tahun × 12 bulan).
- `DATA_NASIONAL_DISAGREGASI_V2.csv` — nasional, 2013–2023,
  396 baris (3 kategori × 11 tahun × 12 bulan), basis pre-training.

**Skema kategori** disederhanakan dari 7 jenis PLT menjadi 3 kategori inti:
`Hydro` (PLTA+PLTM), `Solar` (PLTS+PLTS Atap), `Wind` (PLTB). PLTMH dan
PLT Hybrid dikeluarkan dari scope penelitian — keputusan sadar, bukan
penghapusan diam-diam.

**Keterbatasan yang wajib diungkap di laporan:**

- Kolom `Produksi` pada sumber tahunan regional (file bauran energi Dinas
  ESDM Sulsel) adalah hasil kalkulasi `Kapasitas × Capacity Factor asumsi ×
  8760 jam`, **bukan** observasi/metering langsung. Keterbatasan ini
  diwariskan dari sumber primer.
- Angka tahunan nasional berasal dari HEESI 2023 (Tabel 6.4.1 & 6.4.2).
  Data off-grid baru tercatat mulai 2018 → ada diskontinuitas struktural
  pada seri nasional, bukan bug.
- Disagregasi tahunan → bulanan memakai proporsi langsung untuk Solar/Wind
  dan rata-rata bergerak 3 bulan untuk Hydro (proksi efek tampungan waduk).
- Kolom `Cuaca` adalah data riil NASA POWER (bukan lagi proxy pola 2023 yang
  diulang seperti dataset lama).

Skrip pembangun (`disagregasi_regional.py`, `disagregasi_nasional.py`,
`tarik_cuaca_nasa_power*.py`) dan dokumentasi lengkapnya
(`DOKUMENTASI_DATASET_REGIONAL_*.md`, `DOKUMENTASI_DATASET_NASIONAL_V2.md`)
**belum dipindahkan ke repo ini** — masih di folder output percakapan
Claude.ai. Perlu di-commit ke sini agar dataset di atas reproducible.
