# Temuan Retraining dengan Dataset V2/V3 (rekonstruksi ulang)

Run: `audit/run_pipeline_fixed.py` → `audit/results/pipeline_run_v3/`
Log lengkap: [`run_log_dataset_v3.txt`](run_log_dataset_v3.txt)
Status: pipeline berjalan sampai akhir tanpa exception.

## 0. Apa yang berubah dari run sebelumnya

| | Run sebelumnya (`pipeline_run_fixed`) | Run ini (`pipeline_run_v3`) |
|---|---|---|
| Dataset regional | `DATA_PHASE_3_REGIONAL_MODIFIED.csv` (7 jenis PLT) | `DATA_REGIONAL_DISAGREGASI_V3.csv` (3 kategori) |
| Dataset nasional | `DATA_PHASE_2_NASIONAL_FINAL.csv` (2020–2024) | `DATA_NASIONAL_DISAGREGASI_V2.csv` (2013–2023) |
| Kolom Cuaca | proxy pola 2023 diulang tiap tahun | data riil NASA POWER |
| Split nasional | train ≤2023, val 2024 | train 2013–2021, val 2022–2023 |
| Split regional | train+val 2023–2024, test 2025 | **sama** (2025 kini data riil) |
| Kategori | 7 jenis PLT | Hydro, Solar, Wind |

**Angka di dokumen ini TIDAK sebanding dengan `eval_summary_before_*.csv`.**
Itu perbandingan antar-dataset, bukan antar-perbaikan kode. Dokumen audit lama
(`audit_findings.md`, `tugas2_findings.md`) sengaja tidak diubah — biarkan
sebagai jejak audit dataset lama.

## 1. Model terbaik per kategori (berbasis RMSE validasi)

Sumber: `pipeline_run_v3/EBT_LSTM_Streamlit/evaluation/model_terbaik_per_plt.csv`

| Kategori | Tahap menang | RMSE validasi | RMSE test 2025 (konfirmasi) |
|---|---|---|---|
| Hydro | **Baseline** | 63,22 | 206,78 |
| Solar | **Baseline** | 0,486 | 0,390 |
| Wind | **Baseline** | 6,556 | 13,90 |

**Temuan utama: Transfer Learning kalah dari Baseline di ketiga kategori.**
Baseline di sini adalah LSTM univariate (hanya Produksi) yang dilatih dari nol
pada data regional; Fine-Tuning/Iterasi 1–3 memuat bobot pre-training nasional
dan memakai input multivariat (Cuaca, Kapasitas, Produksi).

Ini kebalikan dari hasil dataset lama, di mana Fine-Tuning menang di mayoritas
jenis PLT. Kandidat penjelasan yang perlu diuji sebelum ditulis sebagai
kesimpulan di BAB IV/V:

- Pada dataset lama, kolom Cuaca regional adalah pola 2023 yang diulang identik
  tiap tahun — praktis fitur periodik bersih. Dengan cuaca riil NASA POWER,
  fitur itu jauh lebih berisik dan kontribusinya ke prediksi bisa negatif pada
  sample sekecil ini.
- Skala nasional vs regional berbeda ordo besar (mis. Hydro nasional ribuan GWh
  vs regional ratusan GWh). Bobot pre-training dimuat apa adanya ke model
  regional; makin jauh distribusinya, makin besar risiko transfer justru
  merugikan (*negative transfer*).
- Data latih regional sangat pendek: 24 titik bulanan per kategori → ~18
  sequence dengan window 6.

## 2. Metrik pada data uji 2025

Sumber: [`eval_summary.csv`](eval_summary.csv) (dibangun oleh
`audit/analysis/build_eval_summary.py`).

| Kategori | Baseline MAPE | FineTuning MAPE | Iterasi1 | Iterasi2 | Iterasi3 |
|---|---|---|---|---|---|
| Hydro | 35,88% | 21,76% | 21,58% | 22,98% | 21,60% |
| Solar | 14,05% | 18,77% | 18,76% | 41,58% | 18,62% |
| Wind | 15,97% | 36,27% | 35,53% | 40,49% | 35,51% |

**Perhatikan Hydro**: Baseline menang di validasi (RMSE 63,2 vs 71,9–117,9) tapi
justru paling buruk di test 2025 (MAPE 35,9% vs 21,6% Fine-Tuning). Ini BUKAN
alasan untuk mengganti pilihan model — memilih berdasarkan skor test justru
persis jenis leakage yang sudah diperbaiki di audit sebelumnya. Yang benar:
laporkan keduanya dan jelaskan penyebabnya.

Penyebab yang paling mungkin: produksi Hydro 2025 melompat naik tajam
(Jan 2025 = 606 GWh vs Jan 2024 = 373 GWh, Jan 2023 = 338 GWh), sejalan dengan
kenaikan kapasitas 776 → 860 MW. Model yang hanya melihat 2023–2024 tidak punya
dasar untuk mengantisipasi lompatan level ini. Baseline yang univariate bahkan
tidak melihat kolom Kapasitas sama sekali — konsisten dengan mengapa ia paling
terpukul.

## 3. LSTM vs metode tradisional

Sumber: [`baseline_comparison.csv`](baseline_comparison.csv), uji = 2025, split
& metrik identik untuk ketiga metode.

| Kategori | LSTM (Fine-Tuning) RMSE | ARIMA(1,1,1) RMSE | Naive persistence RMSE | Menang |
|---|---|---|---|---|
| Hydro | 109,06 | 127,73 | **98,47** | Naive |
| Solar | 0,409 | 1,187 | **0,287** | Naive |
| Wind | 22,76 | 11,87 | **10,42** | Naive |

Dengan MAPE: Hydro naive 15,8%; Solar naive 12,3%; Wind ARIMA 13,65% vs naive
13,69% (praktis seri), keduanya jauh di atas LSTM (36,3%).

**Klaim "LSTM lebih unggul dari metode tradisional" (BAB I) tidak didukung oleh
hasil ini.** Pada dataset lama LSTM menang di 4 dari 7 jenis PLT; pada dataset
riil ini LSTM tidak menang di satu kategori pun. Ini perlu ditulis apa adanya,
bukan disembunyikan — dan bisa dibingkai sebagai kontribusi (menunjukkan batas
kelayakan deep learning pada seri sependek ini), bukan kegagalan.

### Catatan metodologis yang perlu keputusan

`baseline_compare.py` membandingkan ARIMA/naive terhadap **tahap Fine-Tuning**,
mengikuti desain awal. Tapi model yang benar-benar di-deploy sekarang adalah
tahap **Baseline** di ketiga kategori. Kalau perbandingan memakai model yang
di-deploy, angkanya berubah cukup banyak (Wind: 15,97% bukan 36,27%; Solar:
14,05% bukan 18,77%; Hydro: 35,88% bukan 21,76%) — LSTM jadi jauh lebih dekat
di Wind & Solar, tapi makin jauh tertinggal di Hydro. Kesimpulan "naive menang"
tidak berubah. Perlu diputuskan mana yang dipakai di BAB IV, lalu konsisten.

## 4. Forecast 2026–2028

Sumber: `pipeline_run_v3/EBT_LSTM_Streamlit/forecast/`

| Tahun | Total forecast (GWh) | YoY |
|---|---|---|
| 2026 | 4.927,96 | — |
| 2027 | 4.910,61 | −0,35% |
| 2028 | 4.896,95 | −0,28% |

Aktual: 2023 = 4.350,6 · 2024 = 4.727,4 · 2025 = 5.231,98 GWh.

Forecast **turun** dari aktual 2025 lalu stagnan, padahal aktual 2023–2025 naik
konsisten (+8,7%, +10,7%). Ini konsekuensi langsung dari model autoregresif yang
dilatih pada 24–36 titik: ia menarik seri kembali ke rata-rata historis alih-alih
melanjutkan tren. Jangan dibaca sebagai proyeksi penurunan produksi EBT Sulsel —
ini keterbatasan model, dan wajib dinyatakan begitu di BAB IV/V.

## 5. Yang masih terbuka

- Skrip pembangun dataset (`disagregasi_regional.py`, `disagregasi_nasional.py`,
  `tarik_cuaca_nasa_power*.py`) dan `DOKUMENTASI_DATASET_*.md` belum ada di repo
  → dataset belum reproducible dari sumber.
- `DOKUMENTASI_DATASET_REGIONAL_V2.md` masih menyebut 2025 dikecualikan; perlu
  diupdate ke V3.
- Bagian batubara/fosil pada file bauran energi 2025 versi baru belum dicek
  (pengecekan kemarin baru bagian EBT).
- Audit `app.py` / `app_pages/` (Streamlit) belum pernah disentuh.
- Hipotesis *negative transfer* di §1 belum diuji — kalau mau dijadikan
  kesimpulan, perlu eksperimen terpisah (mis. fine-tuning dengan target yang
  dinormalisasi per-kategori, atau pre-training hanya pada Wind nasional yang
  ~97% memang kapasitas Sulsel).
