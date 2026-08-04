# Temuan: Framing Masalah, Bukan Arsitektur Model

Script: [`audit/analysis/lstm_improved.py`](../analysis/lstm_improved.py)
Hasil: [`experiment_improved/`](experiment_improved/) · Log: [`run_log_lstm_improved.txt`](run_log_lstm_improved.txt)

Eksperimen ini **terpisah** dari pipeline utama (`audit/source_fixed/bs_tf_lstm_fix_fixed.py`),
yang sengaja tidak diubah supaya hasil skripsi versi asli tetap utuh sebagai pembanding.

## 1. Akar masalahnya: target adalah fungsi deterministik dari kolom yang tidak dilihat model

Uji rasio `Produksi / Cuaca` di dalam tiap tahun pada dataset regional V3:

| Kategori | Spread rasio dalam satu tahun |
|---|---|
| Solar | ≤ 0,011% |
| Wind | ≤ 0,0003% |
| Hydro | ≈ 0% terhadap MA3(Cuaca) |

Dan `Produksi_tahunan / Kapasitas` **konstan persis di ketiga tahun**:
Solar 1,752 · Wind 4,380 · Hydro 5,256. Artinya CF asumsi sumbernya tetap, sehingga

```
Produksi_bulan = Kapasitas × CF × 8760 × ( Cuaca_bulan / ΣCuaca_tahun )
```

Rekonstruksi formula itu diuji ke 2025: **MAPE 0,00% untuk Solar dan Wind**, 4,60% untuk
Hydro (sisa error Hydro berasal dari efek batas rata-rata bergerak 3 bulan di pergantian tahun).
Bukan mirip — persis.

Sementara `create_sequences()` di pipeline utama memberi model Cuaca dan Kapasitas di bulan
**t−6…t−1** lalu meminta menebak Produksi di bulan **t**. Dua kolom yang secara aljabar
menentukan jawabannya dipotong tepat sebelum bulan target.

**Konsekuensi yang harus diakui di BAB IV/V: kolom Produksi tidak punya kandungan informasi
independen.** Ini bukan sekadar "datanya kurang akurat" — target-nya bukan observasi. Tanpa
data metering bulanan, tidak ada model yang bisa divalidasi secara jujur pada dataset ini.

Bukti pendukung: mean CF bulanan **identik** di ketiga tahun untuk setiap kategori
(Hydro 0,438 · Solar 0,146 · Wind 0,365). Jadi "lompatan level Hydro 2025" yang bikin
model utama hancur sebenarnya murni kenaikan kapasitas terpasang 776 → 860 MW, bukan
perubahan perilaku produksi.

## 2. Lima perbaikan yang diuji

1. Target diganti dari GWh ke **capacity factor** (`Produksi/Kapasitas`) — menyamakan skala
   nasional vs regional (mengatasi dugaan *negative transfer*) sekaligus menghapus lompatan
   level 2025.
2. **Input eksogen Cuaca di bulan target** → dijalankan sebagai varian terpisah (§4).
3. Benchmark ditambah **seasonal naive (lag-12)** dan seasonal naive × rasio kapasitas —
   benchmark yang pantas untuk data bulanan musiman, bukan hanya lag-1.
4. Satu model **pooled 3 kategori + category embedding**, bukan 3 model terpisah —
   sample latih efektif naik dari 24 ke 72 titik.
5. **Walk-forward (rolling-origin) validation** 4 lipatan untuk memilih konfigurasi,
   bukan satu split 85/15 dari 18 sequence.

Arsitektur LSTM (64 → 32 → Dense 1) dipertahankan sama persis dengan pipeline utama, supaya
perbandingannya soal **framing**, bukan soal kapasitas model. Data uji 2025 tidak pernah
menyentuh pemilihan konfigurasi maupun fit scaler.

Konfigurasi terpilih dari walk-forward (kedua varian): window=3, lr=1e−4, dropout=0,2.

## 3. Hasil varian A (tanpa cuaca bulan target) — hasil utama

Seluruh metrik dalam satuan GWh pada data uji 2025, sebanding langsung dengan
`eval_summary.csv` dan `baseline_comparison.csv`.

| Kategori | Metode | RMSE | MAPE |
|---|---|---|---|
| **Hydro** | **LSTM_A (framing baru)** | **76,85** | **11,89%** |
| Hydro | Naive lag-1 | 98,47 | 15,77% |
| Hydro | LSTM Fine-Tuning (pipeline utama) | 109,06 | 21,76% |
| Hydro | Seasonal naive × rasio kapasitas | 106,87 | 26,14% |
| Hydro | LSTM Baseline (model ter-deploy) | 206,78 | 35,88% |
| **Solar** | **Seasonal naive × rasio kapasitas** | **0,176** | **7,22%** |
| Solar | Naive lag-1 | 0,287 | 12,28% |
| Solar | LSTM_A (framing baru) | 0,371 | 16,54% |
| Solar | LSTM Baseline (model ter-deploy) | 0,390 | 14,05% |
| **Wind** | **Seasonal naive × rasio kapasitas** | **9,05** | **14,60%** |
| Wind | Seasonal naive lag-12 | 9,85 | 14,07% |
| Wind | Naive lag-1 | 10,42 | 13,69% |
| Wind | LSTM_A (framing baru) | 11,13 | 15,47% |
| Wind | LSTM Baseline (model ter-deploy) | 13,90 | 15,97% |

**Dibanding model yang ter-deploy sekarang, RMSE turun di ketiga kategori:**
Hydro −62,8% · Wind −19,9% · Solar −4,9%. Hydro yang paling dramatis (206,78 → 76,85;
MAPE 35,88% → 11,89%) — konsisten dengan diagnosis bahwa masalah terbesarnya adalah
lompatan kapasitas yang hilang begitu target diganti ke capacity factor.

**Tapi LSTM tetap hanya menang di 1 dari 3 kategori.** Di Hydro ia sekarang mengungguli
seluruh benchmark (22% lebih baik dari naive lag-1). Di Solar dan Wind masih kalah dari
seasonal naive × rasio kapasitas.

Ini masuk akal dan konsisten dengan §1: bentuk CF dalam setahun ditentukan oleh cuaca bulan
berjalan, yang tidak bisa ditebak dari lag. Yang bisa ditangkap model hanyalah pola musiman —
dan untuk itu seasonal naive sudah cukup. Hydro jadi pengecualian karena rata-rata bergerak
3 bulan pada konstruksinya memberi autokorelasi nyata yang memang bisa dipelajari LSTM.

## 4. Hasil varian B (dengan cuaca bulan target) — dan kenapa dugaan saya meleset

| Kategori | LSTM_A | LSTM_B | Selisih |
|---|---|---|---|
| Hydro | 76,85 | 81,21 | B **lebih buruk** |
| Solar | 0,371 | 0,403 | B **lebih buruk** |
| Wind | 11,13 | 10,52 | B sedikit lebih baik |

Saya memperkirakan varian B akan melonjak ke akurasi sangat tinggi dengan mengeksploitasi
rumus konstruksi dataset. **Itu tidak terjadi** — B praktis setara A, bahkan lebih buruk di
dua kategori.

Penyebabnya arsitektural: Cuaca bulan-t masuk sebagai satu skalar yang di-concat di lapisan
Dense terakhir. Untuk mengeksploitasi kebocoran, jaringan harus belajar hubungan
*perkalian* `CF_t = CF_tahunan × W_t / ΣW` — dan dengan 18 sequence latih, ia tidak sanggup.

**Jangan simpulkan dari sini bahwa kebocorannya tidak ada.** Regresi bentuk-tertutup
`P = a · Kapasitas · Cuaca` yang saya uji terpisah mendapat MAPE **3,67% (Solar)** dan
**9,44% (Wind)** — jauh di bawah varian B (17,28% dan 14,33%). Jadi kebocorannya nyata dan
bisa dieksploitasi; hanya saja arsitektur ini terlalu lemah kopelnya untuk melakukannya.

Kesimpulan jujurnya: varian B **tidak memberi nilai tambah** di setup ini, jadi hasil utama
(§3) aman dipakai tanpa kekhawatiran sirkularitas. Kalau nanti dipakai arsitektur yang
mengeksploitasi hubungan multiplikatif, kekhawatiran itu kembali dan wajib diungkap.

## 5. Implikasi untuk skripsi

Yang bisa ditulis dengan jujur setelah eksperimen ini:

- **Framing masalah lebih menentukan daripada arsitektur.** Dengan arsitektur LSTM yang
  identik, hanya dengan mengganti target ke capacity factor + pooling + walk-forward, RMSE
  turun 62,8% di Hydro. Tidak ada layer baru, tidak ada tuning hyperparameter agresif.
- **Transfer learning baru masuk akal setelah skalanya disamakan.** Kegagalan Transfer
  Learning di pipeline utama (kalah dari Baseline di ketiga kategori) konsisten dengan
  hipotesis *negative transfer* akibat beda ordo besar nasional vs regional.
- **Deep learning tetap tidak memberi nilai tambah di Solar dan Wind.** Ini temuan, bukan
  kegagalan: pada seri sependek ini dengan target yang ditentukan cuaca bulan berjalan,
  baseline musiman sederhana adalah pilihan yang benar.
- **Batas sesungguhnya ada di data, bukan model.** Selama Produksi masih hasil kalkulasi
  `Kapasitas × CF × 8760`, tidak ada model yang bisa dibuktikan lebih baik secara meyakinkan.

Rekomendasi framing BAB IV/V: jadikan §1 sebagai temuan utama penelitian, dengan §3 sebagai
bukti bahwa perbaikan metodologis memang membantu tapi ada plafon yang ditentukan kualitas
data. Itu kontribusi metodologis nyata dan jauh lebih kuat daripada memaksakan klaim
"LSTM lebih unggul".

## 6. Yang masih terbuka

- Hipotesis *negative transfer* belum diuji langsung (mis. pre-training hanya pada Wind
  nasional yang ~97% kapasitasnya memang di Sulsel).
- Belum diuji apakah arsitektur dengan kopel multiplikatif untuk cuaca bulan-t (mis. output
  dikali `Kapasitas × Cuaca_t`) mengubah kesimpulan §4 — kalau iya, sirkularitasnya harus
  diungkap eksplisit.
- Eksperimen ini hanya mengevaluasi pada 2025 (12 titik per kategori). Kesimpulannya rapuh
  terhadap satu tahun uji; idealnya diulang begitu data 2026 tersedia.
