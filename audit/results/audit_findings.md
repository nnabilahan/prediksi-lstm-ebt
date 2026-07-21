# Laporan Audit Tugas 1 — Pipeline LSTM EBT

Tanggal audit: 2026-07-21
Branch: `audit/lstm-pipeline`
Sumber: `audit/source/bs_tf_lstm_fix.py` (salinan tidak diubah dari Colab)
Runner: `audit/run_pipeline.py` (adaptasi non-interaktif, lihat bagian "Cara Menjalankan" di bawah)
Log lengkap: [`run_log.txt`](run_log.txt) (808+ baris, seluruh output stdout end-to-end)
Ringkasan metrik: [`eval_summary.csv`](eval_summary.csv)

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

- **Model terbaik per PLT** (RMSE terkecil, dari `model_terbaik_per_plt.csv`):
  | PLT | Model Terbaik | RMSE |
  |---|---|---|
  | PLT Hybrid | Fine-Tuning | 0.0290 |
  | PLTS | Fine-Tuning | 0.1233 |
  | PLTS Atap | Baseline | 0.1770 |
  | PLTMH | Baseline | 2.0110 |
  | PLTM | Baseline | 2.7945 |
  | PLTA | Baseline | 3.2995 |
  | PLTB | Iterasi 3 | 11.9845 |
- **Rata-rata seluruh model** (dari `ringkasan_rata2_seluruh_model.csv`): Fine-Tuning punya rata-rata RMSE/MAE terendah (3.07 / 2.62), tapi rata-rata MAPE terendah justru Baseline (13.37%) — Iterasi2 konsisten terburuk di semua metrik (RMSE 5.46, MAPE 22.28%).
- **PLTB** memiliki RMSE & MAPE tertinggi di semua tahap (~12-15 RMSE, ~21-24% MAPE) — jauh lebih sulit diprediksi dibanding PLT lain, kemungkinan karena skala produksi PLTB lebih besar dan/atau variasi datanya lebih tinggi.
- Model final yang dipakai untuk forecasting 2026-2028 memakai kombinasi metode per PLT (`Transfer Learning` untuk PLTA/PLTB/PLTMH/PLTS, `Direct Training` untuk PLTM/PLTS Atap/PLT Hybrid) sesuai `model_terbaik_per_plt.csv` — bukan selalu tahap "Final" tersendiri, karena tahap "MODEL FINAL" di source melatih ulang dengan seluruh data (lihat poin 4 di bawah), tidak menghasilkan RMSE/MAE/MAPE baru (tidak ada data uji tersisa).

Forecast total 2026-2028 (`pipeline_run/EBT_LSTM_Streamlit/forecast/forecast_total_2026_2028.csv`) menunjukkan proyeksi total produksi EBT regional turun dari **1.636,6 GWh (2026)** ke **~1.608-1.610 GWh (2027-2028)** — relatif datar/menurun tipis, bukan tren naik tajam.

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

## 4. Temuan: Data Leakage (Scaler Fit-Before-Split)

**Status: dikonfirmasi — leakage sistemik skala kecil di seluruh tahap pipeline yang punya train/test split.**

Pola yang berulang di 4 tahap (Baseline, Pre-Training Nasional, Fine-Tuning, Iterasi 1-3): `MinMaxScaler().fit_transform()` dipanggil pada **seluruh deret waktu per-PLT** SEBELUM data displit menjadi train/test:

| Tahap | Baris fit scaler | Baris split |
|---|---|---|
| Baseline (regional, univariate) | `bs_tf_lstm_fix.py:117` | `bs_tf_lstm_fix.py:167` |
| Pre-Training (nasional, multivariate) | `bs_tf_lstm_fix.py:493-494` | `bs_tf_lstm_fix.py:555-556` (mask tahun) |
| Fine-Tuning (regional, multivariate) | `bs_tf_lstm_fix.py:802-803` | `bs_tf_lstm_fix.py:859-872` (mask tahun, test=2025) |
| Iterasi 1-3 | pola serupa (scaler baru per iterasi, fit sebelum split) | — |

**Akibatnya:** rentang min-max yang dipakai untuk menormalisasi data (termasuk yang nanti jadi "data uji"/test) ikut dihitung dari nilai test itu sendiri — nilai ekstrem di test set memengaruhi skala normalisasi data train. ­Ini leakage ringan (bukan leakage label langsung seperti target bocor ke fitur), tapi tetap melanggar prinsip "test set tidak boleh memengaruhi proses training apa pun, termasuk preprocessing".

**Dampak terhadap validitas hasil skripsi:** metrik RMSE/MAE/MAPE yang dilaporkan kemungkinan **sedikit optimis (bias rendah)** dibanding jika scaler di-fit hanya pada train lalu di-transform ke test. Mengingat ukuran dataset regional sangat kecil (253 baris total, ~36 baris per PLT), efek ini bisa cukup terasa secara relatif meskipun kecil secara absolut.

**Rekomendasi perbaikan (BELUM diterapkan di audit ini, sesuai instruksi "jangan ubah kode sebelum direview")**: untuk setiap tahap, urutan seharusnya dibalik — split dulu (kronologis) baru `scaler.fit(train)` lalu `scaler.transform(train)` dan `scaler.transform(test)` (bukan `fit_transform` pada gabungan). Ini perlu keputusan pengguna dulu sebelum diimplementasikan, karena akan mengubah semua angka evaluasi yang sudah ada di `eval_summary.csv`.

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

## Cara Menjalankan Ulang

```bash
cd C:\prediksi-lstm-ebt-react-app
python audit/run_pipeline.py > audit/results/run_log.txt 2>&1
```

Output akan muncul di `audit/results/pipeline_run/` (model, scaler, forecast, evaluation — tidak di-commit ke git karena besar, lihat `.gitignore`) dan `audit/results/pipeline_run/EBT_LSTM_Streamlit/` (struktur folder deliverable sesuai desain asli script, termasuk `EBT_LSTM_Streamlit.zip`).
