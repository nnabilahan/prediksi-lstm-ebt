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

## Dataset 4/5 jenis PLT — dataset yang DIPAKAI sekarang

> Bagian "Dataset V2/V3" di bawah ini membahas skema 3-kategori
> (Hydro/Solar/Wind) yang sudah **dikoreksi**. Skema final punya 4 jenis PLT
> nasional dan 5 jenis PLT regional (PLTA, PLTB, PLTM, PLTS, PLTS Atap —
> PLTS Atap tidak punya padanan nasional). Lihat
> `audit/results/framing_findings.md` untuk hasil terkini.

File dataset:

- `DATA_REGIONAL_5JENIS.csv` — regional Sulsel, 2023–2025, 180 baris
  (5 jenis × 3 tahun × 12 bulan).
- `DATA_NASIONAL_4JENIS.csv` — nasional, 2013–2023, 528 baris
  (4 jenis × 11 tahun × 12 bulan), basis pre-training.

Skrip pembangun:

- `disagregasi_regional.py` — Tahap 4 Regional. Mengubah angka **tahunan**
  Produksi/Kapasitas per jenis PLT individual (dikunci di dalam skrip,
  sumber: sheet Worksheet file `PERHITUNGAN_BAURAN_ENERGI_ESDM`
  2023/2024/2025 — versi 2025 yang sudah diperbaiki Dinas ESDM) menjadi
  bulanan, proporsional terhadap cuaca riil per kategori induknya
  (PLTA & PLTM → Hydro, PLTS & PLTS Atap → Solar, PLTB → Wind).
- `disagregasi_nasional.py` — sama, untuk skala nasional. Sumber angka
  tahunan: HEESI 2023 Tabel 6.4.1 & 6.4.2. Produksi PLTA vs PLTM di-*split*
  proporsional berdasar pangsa kapasitas (HEESI hanya punya satu kolom
  Produksi gabungan Hydro) — **bukan** hasil pengukuran terpisah.

Keduanya butuh file cuaca riil sebagai input (`--cuaca`), format kolom
`Kategori,Tahun,Bulan,Nilai_Cuaca`, dihasilkan oleh
`tarik_cuaca_nasa_power.py` / `tarik_cuaca_nasa_power_nasional.py`
(**skrip ini dan `DOKUMENTASI_DATASET_*_V2.md` belum ada di repo** — dua
skrip disagregasi di atas diterima terpisah dan sudah diverifikasi, tapi
langkah penarikan cuaca dari NASA POWER API belum bisa direproduksi dari
sini).

**Verifikasi yang sudah dilakukan** (bukan sekadar membaca kode): cuaca riil
per kategori direkonstruksi ulang dari kolom `Cuaca` pada kedua CSV final di
atas (sah dilakukan karena tiap jenis PLT dalam satu kategori berbagi nilai
Cuaca yang identik), lalu dipakai sebagai input kedua skrip. Hasilnya
**identik nol persis** (`|diff| = 0.000000` di kolom Produksi, Cuaca, dan
Kapasitas) dengan `DATA_REGIONAL_5JENIS.csv` / `DATA_NASIONAL_4JENIS.csv`
yang sudah dipakai pipeline. Ini membuktikan formula disagregasi
(rata-rata bergerak 3 bulan untuk Hydro, proporsi langsung untuk
Solar/Wind) dan angka `ANNUAL` di dalam kedua skrip memang persis yang
menghasilkan dataset yang sedang dipakai — bukan cuma skrip yang "terlihat
masuk akal".

**Keterbatasan yang wajib diungkap di laporan** (tetap berlaku, sekarang
dengan sumber yang lebih spesifik — lihat komentar di kedua skrip):

- Kolom `Produksi` sumber ESDM adalah hasil kalkulasi `Kapasitas × Capacity
  Factor asumsi × 8760 jam`, **bukan** observasi/metering langsung.
- Produksi PLTA & PLTM nasional adalah hasil *split proporsional* dari satu
  kolom Hydro gabungan di HEESI, berdasarkan pangsa kapasitas (asumsi CF
  sama) — bukan pengukuran terpisah.
- Data off-grid nasional baru tercatat mulai 2018; PLTB = 0 di 2013/2014/2017
  bukan data hilang — PLTB komersial pertama Indonesia (Sidrap) baru
  beroperasi 2018.
- Disagregasi tahunan → bulanan memakai rata-rata bergerak 3 bulan untuk
  Hydro (proksi efek tampungan waduk) dan proporsi langsung untuk Solar/Wind.
- Kolom `Cuaca` adalah data riil NASA POWER.

**Yang masih belum ada di repo** (gap reproducibility yang tersisa):
`tarik_cuaca_nasa_power.py` / `tarik_cuaca_nasa_power_nasional.py`, file
`cuaca_riil_regional.csv` / `cuaca_riil_nasional.csv` hasil tarikan asli
(bukan rekonstruksi), dan `DOKUMENTASI_DATASET_REGIONAL_V2.md` /
`DOKUMENTASI_DATASET_NASIONAL_V2.md`.

---

## Lampiran: Dataset V2/V3 (3 kategori, sudah dikoreksi)

Bagian di bawah ini adalah catatan historis — dipertahankan sebagai jejak
audit, angkanya **tidak berlaku** untuk hasil penelitian saat ini.

Dua file berikut sempat menggantikan dataset paling lama di atas sebagai
input pipeline, sebelum dikoreksi ke skema 4/5 jenis PLT:

- `DATA_REGIONAL_DISAGREGASI_V3.csv` — regional Sulsel, 2023–2025,
  108 baris (3 kategori × 3 tahun × 12 bulan).
- `DATA_NASIONAL_DISAGREGASI_V2.csv` — nasional, 2013–2023,
  396 baris (3 kategori × 11 tahun × 12 bulan), basis pre-training.

Skema kategori saat itu: `Hydro` (PLTA+PLTM), `Solar` (PLTS+PLTS Atap),
`Wind` (PLTB). PLTMH dan PLT Hybrid dikeluarkan dari scope penelitian —
keputusan itu **tetap berlaku** di skema 4/5 jenis PLT sekarang.
