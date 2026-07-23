# Laporan Audit Tugas 1 — Pipeline LSTM EBT

Tanggal audit: 2026-07-21 (update 2026-07-23: leakage sudah diperbaiki, lihat bagian 4)
Branch: `audit/lstm-pipeline`
Sumber asli (tidak diubah): `audit/source/bs_tf_lstm_fix.py`
Sumber diperbaiki: `audit/source_fixed/bs_tf_lstm_fix_fixed.py` (+ versi `.ipynb`) — lihat bagian 4
Runner asli: `audit/run_pipeline.py` — runner diperbaiki: `audit/run_pipeline_fixed.py`
Log lengkap (versi diperbaiki, jadi acuan utama sekarang): [`run_log_fixed.txt`](run_log_fixed.txt)
Log lengkap (versi asli, sebelum fix, diarsipkan): [`run_log.txt`](run_log.txt)
Ringkasan metrik (versi diperbaiki): [`eval_summary.csv`](eval_summary.csv)
Ringkasan metrik (versi sebelum fix, diarsipkan): [`eval_summary_before_leakage_fix.csv`](eval_summary_before_leakage_fix.csv)

> **Catatan penting**: Semua angka di bagian 1-2 dokumen ini SUDAH mencerminkan
> hasil SETELAH perbaikan leakage (bagian 4). Folder `audit/results/pipeline_run/`
> sekarang berisi output dari run yang sudah diperbaiki; output run yang lama
> diarsipkan di `audit/results/pipeline_run_before_leakage_fix/`.

---

## 1. Ringkasan Eksekusi

`bs_tf_lstm_fix.py` **berhasil dijalankan end-to-end** tanpa mengubah isi filenya, melalui runner adaptasi (`audit/run_pipeline.py`) yang hanya:

1. Mengatur backend matplotlib ke `Agg` (non-GUI) — `plt.show()` di source jadi no-op, tidak mengubah kode.
2. Menyediakan shim `display = print` untuk menggantikan `IPython.display.display()` yang dipakai script (bawaan Colab, tidak ada di Python biasa).
3. Menyediakan shim modul `google.colab.files` (hanya `files.download()` di baris terakhir script, dipakai untuk memicu unduhan browser di Colab) — dibuat no-op karena file ZIP-nya sudah otomatis tersimpan di disk lokal. **Tidak** menimpa modul `google` yang asli (dipakai TensorFlow untuk `google.protobuf`), jadi tidak mengganggu TensorFlow.
4. Menjalankan script di working directory `audit/results/pipeline_run/` (berisi salinan 2 CSV input) — supaya path relatif bawaan script (`DATA_PHASE_3_REGIONAL_MODIFIED.csv`, `DATA_PHASE_2_NASIONAL_FINAL.csv`, `model_final/`, `EBT_LSTM_Streamlit/`, dst.) langsung ditemukan tanpa perlu mengedit satu pun baris di source.

**Percobaan 1 & 2 gagal** karena:
- Percobaan 1: `traceback.print_exc()` tidak menampilkan apa pun ke log karena masalah encoding stdout Windows — sudah diperbaiki (encoding UTF-8 dengan `errors="backslashreplace"`).
- Percobaan 2 (setelah fix encoding): gagal di baris `bs_tf_lstm_fix.py:2944` — `from google.colab import files` — `ModuleNotFoundError`, karena modul itu cuma tersedia di lingkungan Colab. Diperbaiki dengan shim modul (lihat poin 3 di atas).

**Percobaan 3: sukses penuh**, seluruh 3100+ baris tereksekusi sampai akhir (`=== SELESAI: pipeline berjalan sampai akhir tanpa exception ===`), menghasilkan model final untuk 7 jenis PLT, forecast 2026-2028, dan seluruh file evaluasi.

---

## 2. Hasil Numerik (RMSE/MAE/MAPE per PLT per Tahap)

Lihat [`eval_summary.csv`](eval_summary.csv) untuk tabel lengkap (35 baris = 7 PLT × 5 tahap: Baseline, Fine-Tuning, Iterasi1, Iterasi2, Iterasi3). Ringkasan:

- **Model terbaik per PLT** (RMSE terkecil, dari `model_terbaik_per_plt.csv`, SETELAH perbaikan leakage):
  | PLT | Model Terbaik | RMSE |
  |---|---|---|
  | PLT Hybrid | Fine-Tuning | 0.0292 |
  | PLTS | Fine-Tuning | 0.1176 |
  | PLTS Atap | Baseline | 0.1833 |
  | PLTMH | Fine-Tuning | 2.0029 |
  | PLTM | Baseline | 2.7782 |
  | PLTA | Fine-Tuning | 3.3300 |
  | PLTB | Iterasi 3 | 13.1285 |
- **Rata-rata seluruh model** (dari `ringkasan_rata2_seluruh_model.csv`): Fine-Tuning masih rata-rata RMSE/MAE terendah (3.22 / 2.68), rata-rata MAPE terendah tetap Baseline (13.39%) — Iterasi2 tetap konsisten terburuk (RMSE 5.28, MAPE 20.99%). Urutan relatif antar tahap tidak banyak berubah dari sebelum perbaikan.
- **PLTB** tetap memiliki RMSE & MAPE tertinggi di semua tahap (~13-15 RMSE, ~23-26% MAPE) — jauh lebih sulit diprediksi dibanding PLT lain.
- Model final yang dipakai untuk forecasting 2026-2028 memakai kombinasi metode per PLT (`Transfer Learning` untuk PLTA/PLTB/PLTMH/PLTS, `Direct Training` untuk PLTM/PLTS Atap/PLT Hybrid) sesuai `model_terbaik_per_plt.csv`.

Forecast total 2026-2028 (SETELAH perbaikan; `pipeline_run/EBT_LSTM_Streamlit/forecast/forecast_total_2026_2028.csv`) menunjukkan proyeksi total produksi EBT regional turun dari **1.636,3 GWh (2026)** ke **~1.610-1.611 GWh (2027-2028)** — pola yang sama (datar/menurun tipis) dengan sebelum perbaikan, angka absolut sedikit berbeda (selisih <0,1%).

---

## 3. Temuan: "Cuaca" Berulang Setiap Tahun

**Status: dikonfirmasi BY DESIGN, bukan bug acak — tapi merupakan keterbatasan metodologis yang harus dilaporkan di skripsi, bukan diklaim sebagai data cuaca riil per tahun.**

- Di `DATA_PHASE_3_REGIONAL_MODIFIED.csv` (dan sumbernya, `DATA_PHASE_3_REGIONAL_FINAL.csv`), kolom `Cuaca` memiliki **12 nilai bulanan tetap per jenis PLT yang diulang identik di 2023, 2024, dan 2025**. Contoh: PLTA bulan Januari = `290` di ketiga tahun; PLT Hybrid bulan September = `5.60525` di ketiga tahun.
- `data_regional.py` (yang menghasilkan `_MODIFIED.csv` dari `_FINAL.csv`) **tidak pernah menyentuh kolom Cuaca** — hanya meregenerasi kolom `Produksi` untuk tahun-tahun yang datanya terdeteksi duplikat. Jadi pola berulang Cuaca sudah ada sejak `DATA_PHASE_3_REGIONAL_FINAL.csv`, sebelum audit ini.
- Akar penyebabnya ditemukan di `data_nasional.py:298-317` (komentar asli dari penulis kode):
  ```python
  # Ambil pola cuaca dari tahun 2023 (asumsi tahun yang tersedia)
  # Ini akan digunakan sebagai proxy untuk semua tahun EBT jika data cuaca
  # tidak tersedia untuk setiap tahun EBT secara spesifik.
  df_cuaca_proxy = df_cuaca[df_cuaca['Tahun'] == 2023].copy()
  ...
  # Gunakan data cuaca proxy (2023) untuk disagregasi
  ```
  Artinya: hanya pola cuaca tahun 2023 yang tersedia, lalu dipakai ulang (proxy) untuk mendisagregasi nilai tahunan EBT ke 12 bulan di **semua** tahun dataset.

**Implikasi untuk skripsi:**
- Ini **bukan data leakage terhadap target** — `Cuaca` tidak diturunkan dari `Produksi`, jadi tidak ada informasi masa depan yang "bocor" ke fitur.
- Tapi karena nilainya identik tiap tahun, `Cuaca` secara fungsional berperan seperti **fitur "bulan-ke-bulan" (dummy musiman)**, bukan sinyal cuaca eksogen yang benar-benar bervariasi antar tahun. Model tidak bisa belajar dampak variasi cuaca riil (mis. anomali La Niña/El Niño) terhadap produksi EBT, karena variasi itu tidak ada dalam datanya.
- **Rekomendasi penamaan di skripsi**: sebut kolom ini sebagai "proxy cuaca musiman (berbasis pola 2023)" atau "estimasi cuaca disagregasi", **jangan** "data cuaca aktual/terverifikasi per tahun".

---

## 4. Temuan: Data Leakage (Scaler Fit-Before-Split) — SUDAH DIPERBAIKI (2026-07-23)

**Status: dikonfirmasi 2026-07-21, DIPERBAIKI 2026-07-23 atas konfirmasi pengguna.**

Pola yang ditemukan: `MinMaxScaler().fit_transform()` dipanggil pada **seluruh deret waktu per-PLT** SEBELUM data displit menjadi train/test, di **3 lokasi fit scaler** (bukan 4 seperti dugaan awal — Fine-Tuning dan Iterasi 1/2/3 ternyata memakai ULANG satu scaler yang sama, `data_scaled_regional_per_plt`, bukan fit scaler baru per iterasi):

| # | Tahap | Baris fit scaler (asli) | Baris split |
|---|---|---|---|
| 1 | Baseline (regional, univariate) | `bs_tf_lstm_fix.py:117` | `bs_tf_lstm_fix.py:167` (index, `TRAIN_RATIO`) |
| 2 | Pre-Training (nasional, multivariate) | `bs_tf_lstm_fix.py:493-494` | `bs_tf_lstm_fix.py:555-556` (mask tahun ≤2023/2024) |
| 3 | Regional (dipakai bersama Fine-Tuning **+ Iterasi 1/2/3**) | `bs_tf_lstm_fix.py:802-803` | `bs_tf_lstm_fix.py:859-872` (mask tahun 2023-2024/test=2025) |

Tahap "MODEL FINAL" (baris ~2360-2378) **tetap TIDAK diubah** — dia sengaja memakai seluruh data 2023-2025 tanpa held-out test (baris 2351: "TANPA menyisakan data uji"), jadi tidak ada split yang bisa bocor di situ.

### Perbaikan yang diterapkan
File baru `audit/source_fixed/bs_tf_lstm_fix_fixed.py` (+ `bs_tf_lstm_fix_fixed.ipynb`, lihat di bawah) — **file asli `audit/source/bs_tf_lstm_fix.py` TIDAK diubah**, tetap sebagai arsip versi awal. Di ketiga lokasi di atas, polanya diganti dari `scaler.fit_transform(seluruh_data)` menjadi `scaler.fit(hanya_porsi_train)` lalu `scaler.transform(seluruh_data)` — detail & alasan tiap perubahan ada di komentar `[FIX LEAKAGE #1/#2/#3]` langsung di kodenya.

### Dampak empiris (before vs after, MAPE %)
Perbandingan lengkap ada di `eval_summary_before_leakage_fix.csv` vs `eval_summary.csv`. Ringkasan tahap Baseline & Fine-Tuning:

| Tahap | PLT | MAPE Sebelum | MAPE Sesudah | Selisih |
|---|---|---|---|---|
| Fine-Tuning | PLTB | 21,14% | 23,62% | **+2,48** |
| Fine-Tuning | PLTS Atap | 26,38% | 27,96% | +1,57 |
| Fine-Tuning | PLTS | 12,17% | 11,52% | −0,65 |
| Fine-Tuning | PLTMH | 11,52% | 10,88% | −0,64 |
| Fine-Tuning | PLTM | 10,99% | 10,59% | −0,40 |
| Fine-Tuning | PLTA | 9,23% | 8,94% | −0,29 |
| Fine-Tuning | PLT Hybrid | 11,26% | 11,32% | +0,05 |
| Baseline | rata-rata 7 PLT | — | — | umumnya <0,5 poin, arah campuran |

**Kesimpulan dampak**: seperti diduga di laporan awal, leakage-nya **skala kecil** (mayoritas pergeseran MAPE <1 poin persentase, arah campuran — tidak selalu membuat model "lebih bagus"). Tapi **PLTB terdampak paling besar** (+2,48 poin MAPE setelah diperbaiki) — konsisten dengan temuan bahwa PLTB memang PLT paling sulit diprediksi di pipeline ini. Perbaikan ini juga **mengubah hasil "model terbaik per PLT"**: PLTMH dan PLTA yang sebelumnya menang di tahap Baseline, sekarang menang di Fine-Tuning (lihat tabel bagian 2).

**Dampak lanjutan ke Tugas 2 (baseline comparison)**: dengan angka yang sudah diperbaiki, **PLTB sekarang kalah dari ARIMA** (LSTM MAPE 23,62% vs ARIMA 18,89%) — sebelumnya LSTM menang tipis di PLTB. Jadi setelah perbaikan, LSTM menang di **4 dari 7 PLT** (PLT Hybrid, PLTA, PLTM, PLTMH), bukan 5 dari 7 seperti temuan awal — lihat `tugas2_findings.md` untuk detail lengkap.

---

## 5. File yang Tidak Ditemukan / Perlu Klarifikasi

- `data_nasional.py` (baris 26/53/81) mereferensikan `dataset_ebt_bulanan_cuaca.csv` sebagai input utama — file ini **tidak ditemukan** di `C:\Users\LENOVO\Downloads\` dengan nama persis itu. Kandidat terdekat: `dataset_ebt_bulanan_weather_driven.csv` (nama berbeda, isi belum diverifikasi sama). **`data_nasional.py` tidak dijalankan** dalam audit ini (di luar cakupan `bs_tf_lstm_fix.py`) — perlu klarifikasi dari pengguna sebelum script ini bisa dijalankan ulang.
- Data leakage/keterbatasan lain yang perlu direview manual sebelum Tugas 2: apakah split 85/15 internal-val pada Fine-Tuning (`VAL_INTERNAL_RATIO`) dan pemilihan test=2025-only konsisten dipakai kembali untuk baseline ARIMA di Tugas 2 (supaya perbandingan adil/apple-to-apple).

---

## 6. Istilah Data (Audit Trail)

Sesuai batasan yang diminta: seluruh data pada pipeline ini adalah hasil **rekonstruksi/estimasi/proxy**, bukan data "asli/terverifikasi":
- `Produksi` regional 2023-2025: sebagian direkonstruksi oleh `data_regional.py` (deteksi duplikat tahun → digenerate ulang dengan model noise sintetis, `RANDOM_SEED=42`).
- `Cuaca`: proxy musiman dari pola 2023 (lihat bagian 3).
- Model & forecast 2026-2028: hasil pelatihan LSTM pada data yang sudah melalui rekonstruksi di atas — bukan prediksi yang divalidasi terhadap observasi cuaca/produksi riil di luar dataset ini.

---

## 7. Versi .ipynb (untuk dibuka lagi di Google Colab)

`audit/source_fixed/bs_tf_lstm_fix_fixed.ipynb` dibuat dari `bs_tf_lstm_fix_fixed.py` memakai converter generik `audit/analysis/py_to_ipynb.py`. Konverter ini memecah kode jadi cell berdasarkan (a) marker markdown asli Colab (`"""Judul"""` berdiri sendiri — hanya ada 3 di file ini) dan (b) banner komentar `# ====.../# Judul/# ====...` yang dipakai sebagai penanda sub-section di sisa file, menghasilkan 114 cell (bukan 1 cell raksasa). **Keterbatasan yang perlu diketahui**: file `.py` hasil "download" Colab tidak menyimpan batas cell asli untuk kode yang TIDAK dipisah markdown cell di notebook aslinya — jadi granularitas cell di `.ipynb` hasil konversi ini adalah rekonstruksi terbaik dari sisa informasi yang ada (banner komentar), bukan replika 100% persis dari cell-per-cell notebook Colab yang asli. Notebook sudah divalidasi valid (JSON ter-parse, kode gabungan seluruh cell ter-compile tanpa error sintaks).

## Cara Menjalankan Ulang

```bash
cd C:\prediksi-lstm-ebt-react-app
# Versi sudah diperbaiki (dipakai sebagai acuan utama sekarang):
python audit/run_pipeline_fixed.py > audit/results/run_log_fixed.txt 2>&1

# Versi asli/sebelum-fix (arsip, untuk pembanding):
python audit/run_pipeline.py > audit/results/run_log_before_leakage_fix.txt 2>&1
```

Output versi diperbaiki: `audit/results/pipeline_run/` (folder ini sekarang berisi hasil SETELAH fix — hasil sebelum fix diarsipkan di `pipeline_run_before_leakage_fix/`). Isi tiap folder: model, scaler, forecast, evaluation (tidak di-commit ke git karena besar, lihat `.gitignore`) dan `EBT_LSTM_Streamlit/` (struktur folder deliverable sesuai desain asli script, termasuk `EBT_LSTM_Streamlit.zip`).
