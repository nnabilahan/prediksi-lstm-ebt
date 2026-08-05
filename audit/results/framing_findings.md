# Temuan: Framing Masalah, Bukan Arsitektur Model

Script: [`audit/analysis/lstm_improved.py`](../analysis/lstm_improved.py) ·
Hasil: [`experiment_improved/`](experiment_improved/) ·
Log: [`run_log_lstm_improved.txt`](run_log_lstm_improved.txt)

Dataset: `DATA_NASIONAL_4JENIS.csv` (2013–2023, 4 jenis PLT) dan
`DATA_REGIONAL_5JENIS.csv` (2023–2025, 5 jenis PLT).

Eksperimen ini **terpisah** dari pipeline utama
(`audit/source_fixed/bs_tf_lstm_fix_fixed.py`), yang sengaja dipertahankan apa
adanya sebagai pembanding "pendekatan konvensional vs pendekatan yang
diperbaiki" untuk BAB IV — bukan ditinggal karena lupa.

---

## 1. Akar masalahnya: target adalah fungsi deterministik dari kolom yang tidak dilihat model

Uji rasio `Produksi / Cuaca` di dalam tiap tahun pada dataset regional:

| Jenis PLT | Spread rasio dalam satu tahun |
|---|---|
| PLTB | ≤ 0,000% |
| PLTS | ≤ 0,016% |
| PLTS Atap | ≤ 0,250% |
| PLTA, PLTM | ≈ 0% terhadap MA3(Cuaca) |

Dan `Produksi_tahunan / Kapasitas` **konstan persis di ketiga tahun**:
PLTA & PLTM 5,256 · PLTB 4,380 · PLTS & PLTS Atap 1,752. Artinya capacity
factor asumsi sumbernya tetap, sehingga:

```
Produksi_bulan = Kapasitas × CF × 8760 × ( Cuaca_bulan / ΣCuaca_tahun )
```

Untuk PLTA/PLTM proporsinya memakai rata-rata bergerak 3 bulan dari Cuaca,
untuk PLTB/PLTS/PLTS Atap memakai Cuaca langsung.

Sementara `create_sequences()` di pipeline utama memberi model Cuaca dan
Kapasitas di bulan **t−6…t−1** lalu meminta menebak Produksi di bulan **t**.
Dua kolom yang secara aljabar menentukan jawabannya dipotong tepat sebelum
bulan target.

**Konsekuensi yang harus diakui di BAB IV/V: kolom Produksi tidak punya
kandungan informasi independen.** Ini bukan sekadar "datanya kurang akurat" —
targetnya bukan observasi, melainkan hasil kalkulasi. Tanpa data metering
bulanan, tidak ada model yang bisa divalidasi secara benar-benar meyakinkan
pada dataset ini.

**Catatan tambahan:** PLTA dan PLTM punya kolom Cuaca identik (begitu juga
PLTS dan PLTS Atap), dan rasio `P/Kapasitas`-nya sama. Jadi 5 jenis PLT itu
efektifnya hanya **3 sinyal independen** yang berbeda skala.

---

## 2. Tujuh perbaikan yang diuji

Arsitektur LSTM (64 → 32 → Dense 1) dipertahankan **sama persis** dengan
pipeline utama, supaya perbandingannya soal **framing**, bukan soal kapasitas
model.

1. Target diganti dari GWh mentah ke **capacity factor** (`Produksi/Kapasitas`)
   — menyamakan skala nasional vs regional (mengatasi dugaan *negative
   transfer*) sekaligus menghapus lompatan level akibat kenaikan kapasitas
   terpasang.
2. Satu model **pooled** untuk seluruh jenis PLT + **category embedding**,
   bukan satu model per jenis — sample latih efektif naik berlipat.
3. Benchmark ditambah **seasonal naive** (lag-12 dan × rasio kapasitas) —
   pembanding yang pantas untuk data bulanan musiman, bukan hanya lag-1.
4. **Walk-forward (rolling-origin) validation** 4 lipatan untuk memilih
   konfigurasi, bukan satu split kecil.
5. **Enam varian penanganan Cuaca dan musiman** (A–F), lihat §3.
6. Pemilihan (varian, konfigurasi) **per jenis PLT** memakai skor walk-forward
   jenis itu sendiri. Ditambahkan setelah terlihat skor global didominasi PLTA
   (ratusan GWh) dan praktis mengabaikan PLTS (0,1 GWh).
7. **Seed ensembling** (N_SEED = 3, prediksi dirata-rata) di sisi walk-forward
   *maupun* model final. Ditambahkan karena selektor terbukti berisik: PLTS dan
   PLTS Atap adalah seri identik proporsional tapi sempat terpilih varian
   berbeda.

**Data uji 2025 tidak pernah menyentuh** pemilihan konfigurasi maupun fit
scaler. Seluruh pemilihan murni dari skor walk-forward pada 2023–2024.

---

## 3. Varian yang diuji

| Varian | Isi | Butuh cuaca bulan target? |
|---|---|---|
| **A** | Lag murni — hanya Cuaca & CF di t−w…t−1 | Tidak |
| **B** | A + Cuaca bulan-t di-concat di lapisan Dense | Ya |
| **C** | *Known-future covariate*: kanal Cuaca digeser jadi t−w+1…t | Ya |
| **D** | C + encoding bulan (sin/cos) | Ya |
| **E** | C + rasio cuaca relatif (Cuaca_t ÷ rata-rata 12 bulan terakhir, kausal) | Ya |
| **F** | E + encoding bulan | Ya |

Varian A adalah peramalan murni — tidak butuh informasi apa pun tentang bulan
target, jadi **bebas dari kualifikasi apa pun**. Angkanya dilaporkan terpisah
di [`experiment_improved/perbandingan_antar_varian.csv`](experiment_improved/perbandingan_antar_varian.csv).

---

## 4. Hasil akhir (data uji 2025, satuan GWh)

| Jenis PLT | Pemenang | LSTM RMSE | LSTM MAPE | Benchmark terbaik |
|---|---|---|---|---|
| PLTA | **LSTM (varian B)** | 77,06 | 10,99% | 90,98 (naive lag-1) |
| PLTB | **LSTM (varian B)** | 5,07 | 7,49% | 9,05 (seasonal × kapasitas) |
| PLTM | **LSTM (varian B)** | 5,83 | 8,90% | 7,50 (naive lag-1) |
| PLTS | seasonal × kapasitas | 0,096 | 7,90% | **0,080** |
| PLTS Atap | seasonal × kapasitas | 0,114 | 7,92% | **0,096** |

**LSTM unggul di 3 dari 5 jenis PLT**, dengan akurasi (100% − MAPE) **89–93%
di kelimanya**.

Sebagai pembanding: pipeline utama pada dataset yang sama hanya menang di
**2 dari 5** (PLTS & PLTS Atap, skala terkecil) — lihat
[`eval_summary.csv`](eval_summary.csv) dan
[`baseline_comparison.csv`](baseline_comparison.csv).

### Catatan jujur: sempat 4 dari 5, lalu turun ke 3 dari 5

Sebelum ensembling, LSTM sempat unggul di 4 dari 5 (PLTS Atap dimenangkan
varian E). Setelah ensembling, selektor walk-forward memilih varian C untuk
PLTS Atap, dan varian C kalah dari seasonal naive pada data uji.

Varian E (window = 6) sebenarnya **tetap** mengalahkan seasonal naive pada
data uji 2025 (RMSE 0,075 vs 0,096), tapi skor walk-forward-nya (0,0305) kalah
dari varian C (0,0164). **Kombinasi tidak ditukar ke E**, meskipun angka
test-nya lebih bagus — menukar berdasarkan skor test adalah data leakage yang
sama persis dengan temuan yang sudah diperbaiki di
[`audit_findings.md`](audit_findings.md).

Kesimpulan yang jujur: pada 24 titik latih per jenis PLT, pemilihan varian
untuk PLTS/PLTS Atap masih di dalam rentang ketidakpastian. Ini keterbatasan
ukuran data, bukan bukti bahwa LSTM tidak mampu.

---

## 5. Model yang dipakai aplikasi (produksi)

Dibangun oleh [`audit/analysis/build_production_model.py`](../analysis/build_production_model.py)
→ `audit/results/production_model/`. Backend (`backend/config.py`,
`backend/ml.py`) membaca dari sini, **bukan** lagi dari
`pipeline_run_v4/EBT_LSTM_Streamlit/`.

| Jenis PLT | Kombinasi | File model |
|---|---|---|
| PLTA | Varian B, window = 3, lr = 1e−3 | `B_w3_lr1e-3_seed{0,1,2}.keras` |
| PLTB | Varian B, window = 6, lr = 1e−3 | `B_w6_lr1e-3_seed{0,1,2}.keras` |
| PLTM | Varian B, window = 3, lr = 1e−4 | `B_w3_lr1e-4_seed{0,1,2}.keras` |
| PLTS, PLTS Atap | Varian C, window = 3, lr = 1e−3 | `C_w3_lr1e-3_seed{0,1,2}.keras` (berbagi) |

PLTS dan PLTS Atap memakai file model yang **sama** — dibedakan lewat category
embedding, dan terbukti menghasilkan angka berbeda sesuai skalanya saat diuji
lewat endpoint.

File `.keras` **tidak dikomit** (direproduksi dalam hitungan menit lewat
`build_production_model.py`), konsisten dengan kebijakan `.gitignore` yang
sudah ada untuk binari model pipeline audit.

---

## 6. Konsekuensi operasional yang WAJIB diungkap di laporan

Seluruh kombinasi pemenang (varian B dan C) adalah model **known-future
covariate**: mereka butuh nilai Cuaca **bulan yang ditebak** sebagai input.

- Di evaluasi ini nilai tersebut diambil dari data aktual, karena yang
  dievaluasi adalah masa lalu (2025).
- Untuk prediksi sungguhan, nilai itu **harus** berasal dari **prakiraan**
  cuaca (BMKG) atau **normal klimatologis** bulan tersebut — observasi bulan
  depan memang belum ada.
- Endpoint `/api/predict` dan form `Prediksi.jsx` sudah meminta ini secara
  eksplisit sebagai field `cuaca_target`, dengan keterangan bahwa isinya
  perkiraan, bukan observasi.

Karena Produksi pada dataset ini **dibangun** dari Cuaca dan Kapasitas,
sebagian keunggulan varian B/C adalah artefak konstruksi dataset. Varian A
(murni lag) dilaporkan terpisah sebagai angka yang bebas dari kualifikasi ini.

---

## 7. Forecast 2026–2028

Diregenerasi oleh
[`audit/analysis/build_forecast_production.py`](../analysis/build_forecast_production.py)
memakai model produksi secara **otoregresif** (prediksi bulan t menjadi input
bulan t+1).

| Tahun | Forecast |
|---|---|
| 2026 | 5.204,36 GWh |
| 2027 | 5.176,72 GWh |
| 2028 | 5.177,85 GWh |

Aktual sebagai pembanding: 2023 = 4.350,60 · 2024 = 4.727,40 · 2025 = 5.231,98 GWh.

**Dua asumsi yang wajib diungkap** (sudah ditampilkan di UI Dashboard dan Gap
Analysis, bukan hanya di komentar kode):

1. **Cuaca = normal klimatologis** per bulan kalender (rata-rata 2023–2025),
   bukan prakiraan operasional — horizon 3 tahun di luar jangkauan prakiraan
   musiman BMKG. Variabilitas antar-tahun (El Niño/La Niña) **tidak**
   tertangkap.
2. **Kapasitas = LOCF** Desember 2025, dipertahankan tetap sampai Desember
   2028. Kalau ada rencana penambahan kapasitas terverifikasi di RUED/RUPTL,
   forecast ini akan **meremehkan** produksi ke depan.

Karena sifatnya otoregresif, akurasi forecast 36 bulan ke depan **tidak** bisa
disamakan dengan MAPE evaluasi 1 langkah di §4.

---

## 8. Implikasi untuk skripsi

- **Framing masalah lebih menentukan daripada arsitektur.** Dengan arsitektur
  LSTM yang identik, hanya dengan mengganti target ke capacity factor +
  pooling + walk-forward + ensembling, LSTM naik dari menang 2/5 menjadi 3/5.
  Tidak ada layer baru, tidak ada tuning hyperparameter agresif.
- **Transfer learning baru masuk akal setelah skalanya disamakan.** Kegagalan
  Transfer Learning di pipeline utama konsisten dengan hipotesis *negative
  transfer* akibat beda ordo besar nasional vs regional.
- **Deep learning tetap tidak memberi nilai tambah di PLTS & PLTS Atap.** Ini
  temuan, bukan kegagalan: pada seri sependek ini dengan target yang
  ditentukan cuaca bulan berjalan, baseline musiman sederhana adalah pilihan
  yang benar.
- **Batas sesungguhnya ada di data, bukan model.** Selama Produksi masih hasil
  kalkulasi `Kapasitas × CF × 8760`, tidak ada model yang bisa dibuktikan
  lebih baik secara meyakinkan.

Rekomendasi framing BAB IV/V: jadikan §1 sebagai temuan utama penelitian,
dengan §4 sebagai bukti bahwa perbaikan metodologis memang membantu tapi ada
plafon yang ditentukan kualitas data. Itu kontribusi metodologis nyata dan
jauh lebih kuat daripada memaksakan klaim "LSTM lebih unggul".

---

## 9. Yang masih terbuka

- Hipotesis *negative transfer* belum diuji langsung (mis. pre-training hanya
  pada PLTB nasional yang ~97% kapasitasnya memang di Sulsel).
- Belum diuji apakah arsitektur dengan kopel **multiplikatif** untuk cuaca
  bulan-t (mis. output dikali `Kapasitas × Cuaca_t`) mengubah kesimpulan —
  kalau iya, sirkularitasnya harus diungkap lebih tegas lagi.
- Eksperimen ini hanya mengevaluasi pada 2025 (12 titik per jenis PLT).
  Kesimpulannya rapuh terhadap satu tahun uji; idealnya diulang begitu data
  2026 tersedia.
- ~~Skrip pembangun dataset belum ada di repo~~ — **sudah beres**: seluruh
  rantai (`tarik_cuaca_nasa_power*.py` → `disagregasi_*.py`) ada di
  `audit/source/` dan diverifikasi ujung-ke-ujung memakai data NASA POWER
  API live, hasilnya identik nol persis dengan dataset yang dipakai
  pipeline. Lihat `audit/source/README.md` dan
  `DOKUMENTASI_DATASET_{REGIONAL,NASIONAL}_V2.md`.

---

## Lampiran: catatan historis dataset 3 kategori

Versi awal dokumen ini ditulis saat dataset masih 3 kategori (Hydro = PLTA+PLTM,
Solar = PLTS+PLTS Atap, Wind = PLTB) — dataset itu kemudian **dikoreksi** ke
4 jenis nasional / 5 jenis regional yang dipakai sekarang.

Temuan pada dataset lama, untuk jejak audit:

- Struktur konstruksinya **sama persis** (`Produksi_tahunan / Kapasitas`
  konstan lintas tahun), jadi diagnosis §1 berlaku di kedua dataset.
- Dengan framing lama, LSTM kalah di **seluruh** kategori melawan naive
  persistence. Setelah perbaikan target capacity factor + pooling +
  walk-forward, LSTM menang di 1 dari 3 (Hydro).
- Varian B saat itu **tidak** lebih baik dari varian A — arsitekturnya terlalu
  lemah kopelnya untuk mengeksploitasi hubungan multiplikatif pada 18 sequence
  latih. Regresi bentuk-tertutup `P = a · Kapasitas · Cuaca` mendapat MAPE
  3,67% (Solar) dan 9,44% (Wind), jauh di bawah varian B — bukti bahwa
  kebocorannya nyata dan bisa dieksploitasi arsitektur lain.

Angka lengkap versi itu ada di riwayat Git (commit `0cb04c8`).
