# Laporan Tugas 2 — Gap Analysis RUED & Baseline Non-DL

**Update 2026-07-23**: seluruh angka di dokumen ini sudah dijalankan ulang
memakai model hasil perbaikan data leakage (lihat
[`audit_findings.md`](audit_findings.md) bagian 4) — angka sebelumnya
diarsipkan di `baseline_comparison_before_leakage_fix.csv`.

Branch: `audit/lstm-pipeline`
Script: [`audit/analysis/gap_rued.py`](../analysis/gap_rued.py), [`audit/analysis/baseline_compare.py`](../analysis/baseline_compare.py)
Output: [`gap_analysis_2026_2028.csv`](gap_analysis_2026_2028.csv), [`gap_analysis_2026_2028.png`](gap_analysis_2026_2028.png), [`baseline_comparison.csv`](baseline_comparison.csv)

---

## 1. Gap Analysis vs Target RUED

**Koreksi angka target** (sesuai konfirmasi pengguna, menggantikan `config/target_rued.csv` di repo `prediksi-lstm-ebt` yang statusnya sudah eksplisit ditandai **PLACEHOLDER/fabrikasi** oleh README-nya sendiri):
- Target RUED Sulsel (Perda No. 2 Tahun 2022): **20% pada 2025**, **32% pada 2030** (bukan 2050).
- Satuan: **persen bauran energi**, mencakup **seluruh sektor energi** (listrik, transportasi, industri, dst) — bukan spesifik sektor kelistrikan.

**Keterbatasan metodologis yang disengaja (bukan diabaikan begitu saja):**
Forecast model ini hanya mencakup **produksi EBT sektor kelistrikan** (GWh) — subset dari cakupan target RUED. Repo ini **tidak memiliki data total bauran energi Sulsel seluruh sektor** (listrik + transportasi + industri, dst, dalam satuan yang sama) untuk dijadikan penyebut yang valid saat mengonversi GWh kelistrikan menjadi "% terhadap target RUED". Memaksakan konversi tanpa penyebut yang benar akan menghasilkan angka gap yang menyesatkan — sama seperti masalah placeholder yang sudah ditemukan di `target_rued.csv` lama.

**Pendekatan yang dipakai**: kedua rangkaian data disajikan **berdampingan** (bukan digabung jadi satu angka gap), dengan catatan cakupan eksplisit di setiap baris:

| Tahun | Target Bauran EBT RUED (%, seluruh sektor) | Forecast EBT Kelistrikan (GWh/tahun) |
|---|---|---|
| 2026 | 22.4 (interpolasi linear 20%→32%) | 1.636,32 |
| 2027 | 24.8 | 1.611,23 |
| 2028 | 27.2 | 1.609,93 |

Trennya: target RUED terus naik (+2,4 poin persen/tahun), sementara forecast EBT kelistrikan justru **turun/stagnan** dari 2026 ke 2028. Ini konsisten dengan temuan RMSE PLTB yang tinggi di Tugas 1 (LSTM kesulitan menangkap tren PLTB, kontributor produksi terbesar) — layak dibahas di Bab IV/V sebagai catatan bahwa proyeksi kelistrikan saja (tanpa data sektor lain) tidak bisa dipakai untuk menyimpulkan pencapaian/kegagalan target RUED secara keseluruhan.

**Rekomendasi untuk skripsi**: sebut bagian ini sebagai "gap kontekstual" atau "referensi tren", bukan "gap resmi terhadap RUED" — dan cantumkan keterbatasan cakupan (kelistrikan vs seluruh sektor) secara eksplisit di teks maupun judul chart/tabel.

---

## 2. Baseline Non-Deep-Learning (ARIMA & Naive Persistence)

Metodologi split **identik** dengan tahap Fine-Tuning LSTM (train=2023-2024, test=2025, dataset regional `DATA_PHASE_3_REGIONAL_MODIFIED.csv`), metrik RMSE/MAE/MAPE dihitung dengan formula yang sama persis dengan `hitung_mape()` di `bs_tf_lstm_fix.py`. ARIMA order tetap (1,1,1) untuk semua PLT (bukan auto-tuned — data terlalu pendek untuk tuning yang andal, lihat catatan di script).

**Hasil (siapa menang per PLT, RMSE terkecil) — SETELAH perbaikan leakage:**

| PLT | Model Terbaik | RMSE |
|---|---|---|
| PLT Hybrid | **LSTM Fine-Tuning** | 0,029 |
| PLTA | **LSTM Fine-Tuning** | 3,330 |
| PLTB | ARIMA(1,1,1) | 12,710 |
| PLTM | **LSTM Fine-Tuning** | 3,505 |
| PLTMH | **LSTM Fine-Tuning** | 2,003 |
| PLTS | Naive Persistence | 0,115 |
| PLTS Atap | Naive Persistence | 0,138 |

**Perubahan dari temuan sebelum perbaikan leakage**: sebelumnya LSTM menang tipis di PLTB (RMSE 12,02 vs ARIMA 12,71); setelah scaler diperbaiki agar tidak "mengintip" data uji 2025, RMSE LSTM PLTB naik jadi 13,23 — sekarang **ARIMA yang menang di PLTB**. PLTS dan PLTS Atap tetap dimenangkan naive persistence seperti sebelumnya.

**Temuan jujur — bukan "LSTM selalu menang"**: LSTM unggul di **4 dari 7** jenis PLT (PLT Hybrid, PLTA, PLTM, PLTMH — semua skala menengah), **kalah dari ARIMA** di PLTB (skala produksi terbesar), dan **kalah dari naive persistence** di PLTS & PLTS Atap (skala produksi terkecil).

**Implikasi untuk klaim Bab I ("LSTM lebih unggul dari metode tradisional")**: klaim ini **didukung secara empiris hanya untuk PLT skala menengah** (PLTA, PLTM, PLTMH, PLT Hybrid) — **tidak lagi bisa digeneralisasi ke PLTB** seperti temuan awal (sebelum leakage diperbaiki). Ini justru memperkuat pentingnya audit data leakage: kesimpulan "LSTM menang di PLT besar" yang sempat muncul di analisis awal ternyata sebagian dipengaruhi oleh bias metrik akibat leakage, bukan murni kemampuan model. Temuan yang lebih jujur (dan lebih kredibel untuk Bab IV): LSTM unggul di PLT skala menengah, tapi metode tradisional (ARIMA/naive) kompetitif atau lebih baik di kedua ujung ekstrem (PLT terbesar dan PLT terkecil).

---

## 3. File Output

- `audit/results/gap_analysis_2026_2028.csv` — tabel target vs forecast per tahun.
- `audit/results/gap_analysis_2026_2028.png` — chart dua sumbu-y (persen vs GWh, eksplisit dipisah).
- `audit/results/baseline_comparison.csv` — RMSE/MAE/MAPE LSTM vs ARIMA vs Naive per PLT.
