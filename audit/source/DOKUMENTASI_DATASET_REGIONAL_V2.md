# Dokumentasi Perbaikan Dataset Regional — SIPREBAR

**Prediksi EBT Sulawesi Selatan (LSTM + Transfer Learning)**

- **Versi dataset:** `DATA_REGIONAL_5JENIS.csv`
- **Cakupan:** PLTA, PLTM, PLTS, PLTS Atap, PLTB — Sulawesi Selatan, 2023–2025
- **Menggantikan:** `DATA_PHASE_3_REGIONAL_MODIFIED.csv` (versi lama, sintetis) dan `DATA_REGIONAL_DISAGREGASI_V2/V3.csv` (versi kategori gabungan 3 kelas, sudah usang)
- **Dokumen terkait:** [`DOKUMENTASI_DATASET_NASIONAL_V2.md`](DOKUMENTASI_DATASET_NASIONAL_V2.md) (metodologi paralel data nasional)

---

## 1. Riwayat Revisi Skema

| Versi | Struktur Jenis | Cakupan waktu | Status |
|---|---|---|---|
| V2 (kategori gabungan) | Hydro, Solar, Wind (3 kategori) | 2023–2024 | Usang |
| V3 (kategori gabungan) | Hydro, Solar, Wind (3 kategori) | 2023–2025 | Usang |
| Final (dipakai) | PLTA, PLTM, PLTS, PLTS Atap, PLTB (5 jenis) | 2023–2025 | Aktif |

Alasan revisi ke 5 jenis: kategori gabungan (Hydro/Solar/Wind) awalnya dipilih untuk
menyelaraskan dengan variabel cuaca dan padanan data nasional. Namun jenis PLT
individual tetap diperlukan sebagai unit prediksi akhir sistem — konsolidasi ke
kategori hanya dipakai di level penentuan proporsi cuaca bulanan, bukan di level
output data.

---

## 2. Skema Final

| Jenis PLT | Kategori cuaca (Tahap 2 & 3) | Padanan nasional |
|---|---|---|
| PLTA | Hydro | Ada (lihat dokumentasi nasional) |
| PLTM | Hydro | Ada |
| PLTS | Solar | Ada |
| PLTS Atap | Solar | Tidak ada — HEESI tidak memisahkan solar rooftop dari ground-mount |
| PLTB | Wind | Ada |

PLTMH dan PLT Hybrid tetap dikeluarkan dari cakupan penelitian (keputusan dari fase
konsolidasi kategori sebelumnya, tidak berubah). Justifikasi: kontribusi kapasitas
kecil terhadap total EBT Sulsel, dan tidak ada variabel cuaca tunggal yang bisa
dijustifikasi kuat secara fisis untuk keduanya.

**PLTS Atap — konsekuensi tidak punya padanan nasional:** kembali ke desain awal
proposal — PLTS Atap hanya menjalani direct training, tidak ikut transfer learning
dari pre-training nasional (karena tidak ada bobot nasional yang relevan untuk
di-transfer).

---

## 3. Sumber Data Tahunan (Tahap 1)

Sumber: sheet **Worksheet**, file `PERHITUNGAN_BAURAN_ENERGI_ESDM` 2023, 2024, dan
2025 (versi diperbaiki).

### Angka tahunan terkunci — per jenis PLT individual

| Tahun | Jenis | Kapasitas (MW) | Produksi (GWh) |
|---|---|---|---|
| 2023 | PLTA | 653,40 | 3.434,2704 |
| 2023 | PLTM | 64,23 | 337,5929 |
| 2023 | PLTS | 5,14 | 9,0053 |
| 2023 | PLTS Atap | 0,1905 | 0,3338 |
| 2023 | PLTB | 130,00 | 569,4000 |
| 2024 | PLTA | 709,60 | 3.729,6576 |
| 2024 | PLTM | 66,63 | 350,2073 |
| 2024 | PLTS | 5,14 | 9,0053 |
| 2024 | PLTS Atap | 6,9555 | 12,1860 |
| 2024 | PLTB | 143,00 | 626,3400 |
| 2025 | PLTA | 790,6346 | 4.155,5755 |
| 2025 | PLTM | 69,1197 | 363,2930 |
| 2025 | PLTS | 6,2648 | 10,9759 |
| 2025 | PLTS Atap | 7,5119 | 13,1609 |
| 2025 | PLTB | 157,30 | 688,9740 |

### Riwayat masalah file 2025 (penting untuk BAB IV — dokumentasi transparansi proses)

File `PERHITUNGAN_BAURAN_ENERGI_2025.xlsx` versi awal yang diterima terindikasi
bermasalah:

- Sel TAHUN internal masih tertulis "2024"
- Nilai Kapasitas & Produksi PLTA, PLTM, PLTS Atap, PLTB identik persis dengan file
  2024 (hanya PLTS off-grid yang berbeda)
- Pola duplikasi yang sama juga ditemukan di luar bagian EBT: kapasitas & konsumsi 3
  PLTU utama (Barru OMU, Punagayya, Jeneponto Bosowa) serta data co-firing —
  mengonfirmasi kemungkinan besar seluruh file adalah salinan file 2024 yang belum
  diupdate

Setelah dikonfirmasi & diperbaiki oleh Dinas ESDM: file versi baru menunjukkan label
TAHUN benar ("2025"), seluruh angka Kapasitas & Produksi genuinely berbeda dari 2024
(pola pertumbuhan wajar), dan periode data Januari–Desember 2025 penuh (bukan
parsial, tidak perlu anualisasi). Versi inilah yang dipakai di tabel §3 di atas.

---

## 4. ⚠️ Keterbatasan Kritis: Kolom Produksi Bukan Observasi

Kolom "Total Produksi Listrik" pada sumber data ESDM bukan hasil pengukuran/metering,
melainkan hasil kalkulasi:

```
Produksi (GWh) = Kapasitas (MW) × Capacity Factor asumsi × 8760 jam
```

Diverifikasi cocok persis di seluruh jenis PLT dan seluruh tahun (termasuk file 2025
yang sudah diperbaiki — CF tetap konstan per jenis: PLTA/PLTM = 0,6; PLTS/PLTS Atap =
0,2; PLTB = 0,5). Variasi bulanan dalam dataset final murni berasal dari proporsi
cuaca riil (§6), tapi total tahunannya tetap angka hasil formula CF, bukan observasi
lapangan. **Wajib diungkap eksplisit di BAB IV/V.**

---

## 5. Koordinat Representatif per Kategori Cuaca (Tahap 2)

Koordinat ditentukan di level kategori (Hydro/Solar/Wind), dipakai bersama oleh jenis
PLT individual di dalamnya (PLTA & PLTM sama-sama pakai koordinat Hydro; PLTS & PLTS
Atap sama-sama pakai koordinat Solar).

| Kategori cuaca | Latitude | Longitude | Metode penentuan |
|---|---|---|---|
| Hydro (untuk PLTA, PLTM) | -2,86 | 120,79 | Centroid tertimbang kapasitas dari 7 PLTA besar (Larona, Karebbe, Bakaru 1, Balambano, Malea, Bili-Bili, Ranteballa) |
| Solar (untuk PLTS, PLTS Atap) | -5,10 | 119,60 | Titik representatif provinsi (area Makassar/Maros) — simplifikasi |
| Wind (untuk PLTB) | -4,64 | 119,82 | Centroid tertimbang PLTB Sidrap + PLTB Jeneponto |

**Keterbatasan:** PLTA dan PLTM dianggap merespons pola cuaca yang sama (satu titik
koordinat gabungan), padahal lokasi fisiknya bisa tersebar di kabupaten berbeda. Sama
untuk PLTS vs PLTS Atap. Ini simplifikasi yang diakui, bukan presisi penuh per unit
pembangkit.

---

## 6. Sumber & Metodologi Data Cuaca (Tahap 3)

Sumber: NASA POWER API (`power.larc.nasa.gov`), community "Renewable Energy (RE)",
endpoint monthly, periode 2023–2025.

| Kategori | Parameter | Satuan asli |
|---|---|---|
| Hydro | `PRECTOTCORR` | mm/hari (rata-rata harian dalam bulan, BUKAN total bulanan) |
| Solar | `ALLSKY_SFC_SW_DWN` | kWh/m²/hari (rata-rata harian dalam bulan) |
| Wind | `WS10M` | m/s |

---

## 7. Metodologi Disagregasi Tahunan → Bulanan (Tahap 4)

Proporsi bulanan dihitung di level kategori cuaca, lalu diterapkan ke masing-masing
jenis PLT individual dalam kategori itu menggunakan angka tahunan miliknya sendiri
(bukan angka gabungan kategori).

**PLTS & PLTB (kategori Solar/Wind) — proporsi langsung:**

```
proporsi_bulan = cuaca_bulan / total_cuaca_tahun
produksi_bulan[jenis] = produksi_tahunan[jenis] × proporsi_bulan
```

**PLTA & PLTM (kategori Hydro) — rata-rata bergerak 3 bulan sebagai proksi
ketersediaan air waduk:**

```
basis_proporsi_bulan = rata-rata(curah_hujan[bulan-2 : bulan])
proporsi_bulan = basis_proporsi_bulan / total_basis_proporsi_tahun
produksi_bulan[jenis] = produksi_tahunan[jenis] × proporsi_bulan
```

PLTS Atap ikut pola proporsi yang sama dengan PLTS (sama-sama kategori Solar), tapi
dihitung dari angka tahunan PLTS Atap sendiri.

### Validasi

Seluruh 15 kombinasi jenis×tahun (5 jenis × 3 tahun) lolos validasi — SUM(produksi
bulanan) == produksi tahunan terkunci, selisih di bawah 0,01 GWh.

---

## 8. Struktur Dataset Final

File: `DATA_REGIONAL_5JENIS.csv`

| Kolom | Tipe | Keterangan |
|---|---|---|
| Tanggal | Date (YYYY-MM-01) | Bulan observasi |
| Produksi | Float (GWh) | Hasil disagregasi Tahap 4 |
| Kapasitas | Float (MW) | Snapshot tahunan (konstan per tahun per jenis) |
| Cuaca | Float | Nilai NASA POWER sesuai kategori cuaca jenis tersebut (§6) |
| Jenis | String | PLTA / PLTM / PLTS / PLTS Atap / PLTB |

Total baris: 180 (5 jenis × 3 tahun × 12 bulan)
Cakupan waktu: Januari 2023 – Desember 2025

---

## 9. Ringkasan Keterbatasan yang Harus Diungkap di BAB IV/V

1. Kolom Produksi bersumber dari formula Kapasitas × CF asumsi × 8760 jam, bukan
   observasi/metering langsung (§4)
2. File sumber 2025 sempat bermasalah (label salah, banyak baris duplikat dari 2024)
   sebelum diperbaiki Dinas ESDM — riwayat ini didokumentasikan sebagai bagian
   proses verifikasi data (§3)
3. Koordinat cuaca ditentukan di level kategori (Hydro/Solar/Wind), bukan per jenis
   PLT individual — PLTA & PLTM dianggap merespons cuaca yang sama, demikian juga
   PLTS & PLTS Atap (§5)
4. Koordinat Solar adalah simplifikasi satu titik representatif provinsi, bukan
   rata-rata tertimbang presisi (§5)
5. Disagregasi PLTA/PLTM pakai simplifikasi rata-rata bergerak 3 bulan, bukan model
   hidrologi waduk yang sesungguhnya (§7)
6. PLTS Atap tidak punya padanan data nasional — hanya menjalani direct training,
   tidak ikut transfer learning (§2)
7. PLTMH dan PLT Hybrid dikeluarkan dari scope penelitian (§2)
8. Sample size tetap kecil: 36 titik bulanan per jenis sebelum windowing (3 tahun ×
   12 bulan)

---

## 10. Provenance Ringkas

| Data | Sumber | Berkas |
|---|---|---|
| Kapasitas & Produksi tahunan 2023, 2024, 2025 | Dinas ESDM Sulsel — Perhitungan Bauran Energi | `PERHITUNGAN_BAURAN_ENERGI_2023/2024/2025.xlsx`, sheet Worksheet |
| Cuaca bulanan 2023–2025 | NASA POWER API, community RE | `cuaca_riil_regional.csv` |
| Koordinat pembangkit individual (untuk penentuan centroid) | Dinas ESDM Sulsel | `PERHITUNGAN_BAURAN_ENERGI_2023.xlsx`, sheet Data Energi |

---

*Dokumen ini adalah lampiran metodologis untuk BAB III/IV skripsi. Redaksi akhir
untuk dokumen skripsi (format formal, Times New Roman) perlu disesuaikan terpisah.*
