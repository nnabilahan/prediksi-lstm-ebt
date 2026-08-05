# Dokumentasi Perbaikan Dataset Nasional — SIPREBAR

**Prediksi EBT Sulawesi Selatan (LSTM + Transfer Learning)**

- **Versi dataset:** `DATA_NASIONAL_4JENIS.csv`
- **Cakupan:** PLTA, PLTM, PLTS, PLTB — Nasional Indonesia, 2013–2023 (11 tahun)
- **Menggantikan:** `DATA_PHASE_2_NASIONAL_FINAL.csv` (versi lama) dan
  `DATA_NASIONAL_DISAGREGASI_V2.csv` (versi kategori gabungan 3 kelas, sudah usang)
- **Dokumen terkait:** [`DOKUMENTASI_DATASET_REGIONAL_V2.md`](DOKUMENTASI_DATASET_REGIONAL_V2.md)
  (metodologi paralel data regional, 5 jenis)

---

## 1. Riwayat Revisi Skema

| Versi | Struktur Jenis | Status |
|---|---|---|
| V2 (kategori gabungan) | Hydro, Solar, Wind (3 kategori) | Usang |
| Final (dipakai) | PLTA, PLTM, PLTS, PLTB (4 jenis) | Aktif |

**Beda dari regional: nasional cuma 4 jenis, bukan 5** — lihat §2 untuk alasan PLTS
Atap tidak bisa direkonstruksi di level nasional.

---

## 2. Skema Final & Keterbatasan Padanan

| Jenis PLT | Kategori cuaca | Sumber HEESI |
|---|---|---|
| PLTA | Hydro | Hydro PP (on-grid + off-grid) |
| PLTM | Hydro | Mycro Hydro PP + Mini Hydro PP + Micro Hydro (off-grid) |
| PLTS | Solar | Solar PP (on-grid) + Solar PP+PV (off-grid) |
| PLTB | Wind | Wind PP (on-grid + off-grid) |

### ⚠️ PLTS Atap TIDAK ADA di dataset nasional

HEESI **tidak pernah memisahkan solar rooftop dari ground-mount** — hanya ada satu
angka "Solar PP" gabungan di kedua tabel (kapasitas & produksi). Sempat dicoba
pendekatan proxy (memakai data lampu jalan tenaga surya sebagai pengganti "PLTS
Atap"), tapi **pendekatan ini dibuang** karena analoginya terlalu dipaksakan — lampu
jalan bukan representasi solar rooftop, dan menyajikan angka yang kelihatan presisi
padahal sebenarnya tidak reliable justru berisiko lebih besar daripada mengakui
keterbatasannya secara terbuka.

**Konsekuensi:** PLTS Atap regional **hanya menjalani direct training**, tidak ikut
transfer learning dari pre-training nasional. Ini konsisten dengan desain awal
proposal sebelum skema kategori gabungan diperkenalkan.

---

## 3. Sumber Data Tahunan (Tahap 1)

**Sumber:** Handbook of Energy & Economic Statistics of Indonesia (HEESI) 2023,
Kementerian ESDM — Tabel 6.4.1 (Kapasitas Terpasang) dan Tabel 6.4.2 (Produksi).

### ⚠️ Keterbatasan: PLTA & PLTM — produksi displit proporsional, bukan diukur terpisah

Tabel 6.4.1 (Kapasitas) HEESI memisahkan "Hydro PP" (skala besar) dari "Mycro Hydro
PP" + "Mini Hydro PP" (skala kecil) — ini dipetakan ke PLTA vs PLTM. Tapi **Tabel
6.4.2 (Produksi) HEESI hanya punya satu kolom "Hydro" gabungan**, tidak dipecah per
skala.

**Solusi yang dipakai:** produksi Hydro total displit ke PLTA dan PLTM secara
proporsional berdasarkan pangsa kapasitas:

```
produksi_PLTA = produksi_Hydro_total × (kapasitas_PLTA / (kapasitas_PLTA + kapasitas_PLTM))
produksi_PLTM = produksi_Hydro_total × (kapasitas_PLTM / (kapasitas_PLTA + kapasitas_PLTM))
```

Ini **bukan hasil pengukuran terpisah**, melainkan pendekatan pragmatis karena
sumber data tidak menyediakan breakdown produksi. Asumsi implisit: PLTA dan PLTM
punya capacity factor yang sama — asumsi yang wajar tapi tidak tervalidasi secara
empiris. **Wajib diungkap sebagai keterbatasan di BAB III/IV.**

### Angka tahunan terkunci (2013–2023)

| Tahun | PLTA Kap (MW) | PLTA Prod (GWh) | PLTM Kap (MW) | PLTM Prod (GWh) | PLTS Kap (MW) | PLTS Prod (GWh) | PLTB Kap (MW) | PLTB Prod (GWh) |
|---|---|---|---|---|---|---|---|---|
| 2013 | 5.058,87 | 16.573,31 | 106,74 | 349,69 | 9,02 | 5,50 | 0,63 | 0 |
| 2014 | 5.059,06 | 14.668,15 | 170,33 | 493,85 | 9,02 | 6,81 | 1,12 | 0 |
| 2015 | 5.068,59 | 13.122,59 | 238,86 | 618,41 | 36,94 | 5,28 | 1,46 | 4 |
| 2016 | 5.343,59 | 17.661,42 | 307,27 | 1.015,58 | 46,70 | 21,09 | 1,46 | 6 |
| 2017 | 5.343,59 | 17.504,13 | 344,31 | 1.127,87 | 54,48 | 29,05 | 1,46 | 0 |
| 2018 | 5.399,59 | 20.218,00 | 372,56 | 1.394,10 | 52,61 | 75,27 | 143,51 | 190 |
| 2019 | 5.558,52 | 19.649,12 | 417,51 | 1.475,88 | 134,91 | 98,28 | 154,31 | 484 |
| 2020 | 5.638,67 | 22.375,48 | 482,21 | 1.913,52 | 136,39 | 148,97 | 154,31 | 475 |
| 2021 | 5.988,67 | 22.295,53 | 613,08 | 2.282,47 | 190,15 | 167,62 | 154,31 | 437 |
| 2022 | 5.988,67 | 24.317,20 | 700,35 | 2.843,80 | 272,22 | 361,73 | 154,31 | 356 |
| 2023 | 5.610,07 | 20.998,35 | 959,57 | 3.591,65 | 589,05 | 642,87 | 152,30 | 481 |

### Validasi silang

Total Hydro (PLTA+PLTM) 2023 = 20.998,35 + 3.591,65 = **24.590 GWh** — cocok dengan
angka ringkasan resmi HEESI ("Hydro Power: 24.589,40 GWh").

### ⚠️ Keterbatasan lain (diwarisi dari versi kategori gabungan sebelumnya)

- **Data off-grid baru tercatat mulai 2018** — 2013-2017 hanya mencakup on-grid
- **Wind = 0 pada 2013, 2014, 2017** — bukan data hilang, PLTB komersial pertama
  Indonesia (Sidrap) baru beroperasi 2018

---

## 4. Koordinat Representatif per Kategori (Tahap 2)

| Kategori cuaca | Latitude | Longitude | Dipakai untuk jenis | Metode |
|---|---|---|---|---|
| Hydro | -4,40 | 107,95 | PLTA, PLTM | Centroid tertimbang 3 klaster PLTA besar (Jawa Barat/Tengah, Sulawesi Tengah, Sumatera Utara) |
| Solar | -6,85 | 107,40 | PLTS | Titik representatif Jawa Barat (area Cirata) |
| Wind | -4,64 | 119,82 | PLTB | Identik dengan koordinat Wind regional — ~97% kapasitas Wind nasional ada di Sulsel |

⚠️ Sama seperti regional, PLTA & PLTM memakai satu koordinat cuaca gabungan (asumsi
merespons pola hujan yang sama), meskipun lokasi fisiknya bisa tersebar di klaster
berbeda.

---

## 5. Sumber & Metodologi Data Cuaca (Tahap 3)

Sumber: NASA POWER API, community RE, periode 2013–2023. Parameter sama seperti
regional (§6 dokumentasi regional): `PRECTOTCORR` (Hydro), `ALLSKY_SFC_SW_DWN`
(Solar), `WS10M` (Wind) — semua rata-rata harian dalam bulan, bukan total bulanan.

Hasil penarikan: 396 baris (3 kategori × 11 tahun × 12 bulan), tanpa data hilang.

---

## 6. Metodologi Disagregasi Tahunan → Bulanan (Tahap 4)

Sama seperti regional: proporsi dihitung di level kategori cuaca, diterapkan ke
masing-masing jenis PLT (PLTA & PLTM pakai proporsi Hydro dengan rata-rata bergerak
3 bulan; PLTS & PLTB pakai proporsi langsung).

### Validasi

Seluruh 44 kombinasi jenis×tahun (4 jenis × 11 tahun) lolos validasi — selisih
SUM(bulanan) vs target tahunan di bawah 0,5 GWh (toleransi lebih besar dari regional
karena skala nasional jauh lebih besar).

---

## 7. Struktur Dataset Final

File: `DATA_NASIONAL_4JENIS.csv`

| Kolom | Tipe | Keterangan |
|---|---|---|
| Tanggal | Date (YYYY-MM-01) | Bulan observasi |
| Produksi | Float (GWh) | Hasil disagregasi Tahap 4 |
| Kapasitas | Float (MW) | Snapshot tahunan |
| Cuaca | Float | Nilai NASA POWER sesuai kategori cuaca jenis tersebut |
| Jenis | String | PLTA / PLTM / PLTS / PLTB (tidak ada PLTS Atap, lihat §2) |

Total baris: 528 (4 jenis × 11 tahun × 12 bulan)
Cakupan waktu: Januari 2013 – Desember 2023

---

## 8. Ringkasan Keterbatasan yang Harus Diungkap di BAB IV/V

1. PLTS Atap tidak punya padanan nasional — regional PLTS Atap hanya direct
   training, bukan transfer learning (§2)
2. Produksi PLTA vs PLTM displit proporsional berdasarkan kapasitas, bukan hasil
   pengukuran terpisah — asumsi CF sama untuk keduanya belum tervalidasi (§3)
3. Data off-grid nasional baru tercatat mulai 2018 (§3)
4. Wind = 0 di beberapa tahun awal adalah realita historis, bukan data hilang (§3)
5. Koordinat Hydro & Solar nasional adalah simplifikasi dari beberapa pembangkit
   terbesar yang terdokumentasi publik, bukan registry lengkap (§4)
6. PLTA & PLTM memakai satu koordinat cuaca gabungan, sama seperti keterbatasan di
   data regional (§4)

---

## 9. Provenance Ringkas

| Data | Sumber | Berkas/Link |
|---|---|---|
| Kapasitas & Produksi tahunan 2013-2023 | Kementerian ESDM — HEESI 2023 | Tabel 6.4.1 & 6.4.2, esdm.go.id |
| Cuaca bulanan 2013-2023 | NASA POWER API, community RE | `cuaca_riil_nasional.csv` |
| Lokasi klaster PLTA besar & PLTB | Pencarian web, dikonfirmasi terpisah dari HEESI | Lihat §4 dokumentasi regional untuk detail koordinat Wind |

---

*Dokumen ini adalah lampiran metodologis untuk BAB III/IV skripsi. Redaksi akhir
untuk dokumen skripsi (format formal, Times New Roman) perlu disesuaikan terpisah.*
