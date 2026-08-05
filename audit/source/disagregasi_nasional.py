# -*- coding: utf-8 -*-
"""
disagregasi_nasional.py
=========================
Tahap 4 Nasional (VERSI FINAL) — Disagregasi data tahunan (Produksi &
Kapasitas) menjadi bulanan per JENIS PLT INDIVIDUAL, berbasis data cuaca
riil NASA POWER.

Cakupan: 4 jenis PLT (PLTA, PLTM, PLTS, PLTB) -- bukan lagi kategori
gabungan (Hydro/Solar/Wind) seperti versi sebelumnya, dan BUKAN 5 jenis
seperti regional -- PLTS Atap TIDAK ADA padanan di data nasional (HEESI
tidak memisahkan solar rooftop dari ground-mount), lihat
DOKUMENTASI_DATASET_NASIONAL_V2.md bagian 2.

Input:
    - cuaca_riil_nasional.csv  (hasil Tahap 3, dari
      tarik_cuaca_nasa_power_nasional.py)
    - Angka tahunan terkunci per jenis PLT individual (hasil Tahap 1, dari
      HEESI Tabel 6.4.1 & 6.4.2 -- lihat DOKUMENTASI_DATASET_NASIONAL_V2.md
      bagian 3 untuk metodologi split PLTA/PLTM proporsional kapasitas)

Output:
    - DATA_NASIONAL_4JENIS.csv

Cara pakai:
    python3 disagregasi_nasional.py --cuaca cuaca_riil_nasional.csv --output DATA_NASIONAL_4JENIS.csv
"""

import argparse
from pathlib import Path

import pandas as pd

# ── Angka tahunan terkunci per JENIS PLT INDIVIDUAL -- NASIONAL ────────────
# Sumber: HEESI 2023, Tabel 6.4.1 (Kapasitas) & 6.4.2 (Produksi).
#
# CATATAN PENTING (lihat DOKUMENTASI_DATASET_NASIONAL_V2.md bagian 3):
# HEESI memisahkan KAPASITAS PLTA (Hydro PP) vs PLTM (Mycro+Mini Hydro PP),
# tapi PRODUKSI Hydro cuma satu kolom gabungan. Produksi PLTA & PLTM di
# bawah ini adalah hasil SPLIT PROPORSIONAL berdasarkan pangsa kapasitas
# (asumsi CF sama untuk keduanya) -- BUKAN hasil pengukuran terpisah.
# Wajib diungkap sebagai keterbatasan di BAB III/IV.
#
# Data off-grid baru tercatat mulai 2018 -- 2013-2017 hanya on-grid.
# Wind = 0 pada 2013, 2014, 2017 BUKAN data hilang -- PLTB komersial
# pertama Indonesia (Sidrap) baru beroperasi 2018.
ANNUAL = {
    2013: {"PLTA": {"Produksi": 16573.3102, "Kapasitas": 5058.87},
           "PLTM": {"Produksi": 349.6898,   "Kapasitas": 106.74},
           "PLTS": {"Produksi": 5.5,        "Kapasitas": 9.02},
           "PLTB": {"Produksi": 0,          "Kapasitas": 0.63}},
    2014: {"PLTA": {"Produksi": 14668.1482, "Kapasitas": 5059.06},
           "PLTM": {"Produksi": 493.8518,   "Kapasitas": 170.33},
           "PLTS": {"Produksi": 6.81,       "Kapasitas": 9.02},
           "PLTB": {"Produksi": 0,          "Kapasitas": 1.12}},
    2015: {"PLTA": {"Produksi": 13122.5909, "Kapasitas": 5068.59},
           "PLTM": {"Produksi": 618.4091,   "Kapasitas": 238.86},
           "PLTS": {"Produksi": 5.28,       "Kapasitas": 36.94},
           "PLTB": {"Produksi": 4,          "Kapasitas": 1.46}},
    2016: {"PLTA": {"Produksi": 17661.4233, "Kapasitas": 5343.59},
           "PLTM": {"Produksi": 1015.5767,  "Kapasitas": 307.27},
           "PLTS": {"Produksi": 21.09,      "Kapasitas": 46.7},
           "PLTB": {"Produksi": 6,          "Kapasitas": 1.46}},
    2017: {"PLTA": {"Produksi": 17504.1349, "Kapasitas": 5343.59},
           "PLTM": {"Produksi": 1127.8651,  "Kapasitas": 344.31},
           "PLTS": {"Produksi": 29.05,      "Kapasitas": 54.48},
           "PLTB": {"Produksi": 0,          "Kapasitas": 1.46}},
    2018: {"PLTA": {"Produksi": 20218.0017, "Kapasitas": 5399.59},
           "PLTM": {"Produksi": 1394.9983,  "Kapasitas": 372.56},
           "PLTS": {"Produksi": 75.27,      "Kapasitas": 52.61},
           "PLTB": {"Produksi": 190,        "Kapasitas": 143.51}},
    2019: {"PLTA": {"Produksi": 19649.1207, "Kapasitas": 5558.52},
           "PLTM": {"Produksi": 1475.8793,  "Kapasitas": 417.51},
           "PLTS": {"Produksi": 98.28,      "Kapasitas": 134.91},
           "PLTB": {"Produksi": 484,        "Kapasitas": 154.31}},
    2020: {"PLTA": {"Produksi": 22375.4845, "Kapasitas": 5638.67},
           "PLTM": {"Produksi": 1913.5155,  "Kapasitas": 482.21},
           "PLTS": {"Produksi": 148.97,     "Kapasitas": 136.39},
           "PLTB": {"Produksi": 475,        "Kapasitas": 154.31}},
    2021: {"PLTA": {"Produksi": 22295.5324, "Kapasitas": 5988.67},
           "PLTM": {"Produksi": 2282.4676,  "Kapasitas": 613.08},
           "PLTS": {"Produksi": 167.62,     "Kapasitas": 190.15},
           "PLTB": {"Produksi": 437,        "Kapasitas": 154.31}},
    2022: {"PLTA": {"Produksi": 24317.2043, "Kapasitas": 5988.67},
           "PLTM": {"Produksi": 2843.7957,  "Kapasitas": 700.35},
           "PLTS": {"Produksi": 361.73,     "Kapasitas": 272.22},
           "PLTB": {"Produksi": 356,        "Kapasitas": 154.31}},
    2023: {"PLTA": {"Produksi": 20998.3532, "Kapasitas": 5610.07},
           "PLTM": {"Produksi": 3591.6468,  "Kapasitas": 959.57},
           "PLTS": {"Produksi": 642.87,     "Kapasitas": 589.05},
           "PLTB": {"Produksi": 481,        "Kapasitas": 152.3}},
}

PETA_KATEGORI = {"PLTA": "Hydro", "PLTM": "Hydro", "PLTS": "Solar", "PLTB": "Wind"}
KATEGORI_PAKAI_LAG = {"Hydro"}
JENDELA_RATA_RATA_BERGERAK = 3

# Toleransi lebih besar dari versi regional karena skala nasional jauh lebih
# besar (ribuan GWh) -- pembulatan absolut wajar lebih besar.
TOLERANSI_VALIDASI = 0.5  # GWh


def hitung_basis_proporsi(sub: pd.DataFrame, kategori: str) -> pd.Series:
    """Sama seperti versi regional -- rata-rata bergerak untuk Hydro, langsung untuk lainnya."""
    if kategori in KATEGORI_PAKAI_LAG:
        return sub["Nilai_Cuaca"].rolling(
            window=JENDELA_RATA_RATA_BERGERAK, min_periods=1
        ).mean()
    return sub["Nilai_Cuaca"]


def disagregasi(cuaca: pd.DataFrame, annual: dict) -> pd.DataFrame:
    """Jalankan disagregasi tahunan -> bulanan untuk semua jenis PLT & tahun."""
    hasil_rows = []

    for tahun, jenis_dict in annual.items():
        for jenis, angka in jenis_dict.items():
            kategori = PETA_KATEGORI[jenis]
            sub = cuaca[
                (cuaca["Kategori"] == kategori) & (cuaca["Tahun"] == tahun)
            ].copy()

            if sub.empty:
                print(f"  [PERINGATAN] Tidak ada data cuaca untuk {jenis} "
                      f"({kategori}) {tahun}, dilewati")
                continue

            sub = sub.sort_values("Bulan").reset_index(drop=True)
            sub["Basis_Proporsi"] = hitung_basis_proporsi(sub, kategori)

            total_basis = sub["Basis_Proporsi"].sum()
            sub["Proporsi"] = sub["Basis_Proporsi"] / total_basis
            sub["Produksi_Bulanan"] = sub["Proporsi"] * angka["Produksi"]

            for _, row in sub.iterrows():
                hasil_rows.append({
                    "Tanggal": f"{tahun}-{int(row['Bulan']):02d}-01",
                    "Produksi": round(row["Produksi_Bulanan"], 4),
                    "Kapasitas": angka["Kapasitas"],
                    "Cuaca": row["Nilai_Cuaca"],
                    "Jenis": jenis,
                })

    df = pd.DataFrame(hasil_rows)
    return df.sort_values(["Jenis", "Tanggal"]).reset_index(drop=True)


def validasi(df_final: pd.DataFrame, annual: dict) -> bool:
    """Cek SUM(Produksi bulanan) == Produksi tahunan terkunci untuk tiap jenis/tahun."""
    semua_lolos = True
    print("\n" + "=" * 70)
    print("VALIDASI: SUM(Produksi bulanan) harus == Produksi tahunan terkunci")
    print("=" * 70)

    for tahun, jenis_dict in annual.items():
        for jenis, angka in jenis_dict.items():
            subset = df_final[
                (df_final["Jenis"] == jenis)
                & (df_final["Tanggal"].str.startswith(str(tahun)))
            ]
            if subset.empty:
                continue

            total_hasil = subset["Produksi"].sum()
            target = angka["Produksi"]
            selisih = abs(total_hasil - target)
            lolos = selisih < TOLERANSI_VALIDASI
            semua_lolos = semua_lolos and lolos

            status = "OK" if lolos else "SELISIH TERLALU BESAR -- CEK ULANG"
            print(f"{tahun} {jenis}: hasil={total_hasil:.4f}  target={target:.4f}  "
                  f"selisih={selisih:.6f}  -> {status}")

    return semua_lolos


def main():
    parser = argparse.ArgumentParser(
        description="Tahap 4 Nasional: disagregasi 4 jenis PLT tahunan -> bulanan berbasis cuaca riil"
    )
    parser.add_argument("--cuaca", type=str, default="cuaca_riil_nasional.csv",
                         help="Path ke CSV hasil Tahap 3 (tarik_cuaca_nasa_power_nasional.py)")
    parser.add_argument("--output", type=str, default="DATA_NASIONAL_4JENIS.csv",
                         help="Path output CSV hasil disagregasi")
    args = parser.parse_args()

    cuaca_path = Path(args.cuaca)
    if not cuaca_path.exists():
        raise FileNotFoundError(
            f"File cuaca tidak ditemukan: {cuaca_path}\n"
            f"Jalankan dulu tarik_cuaca_nasa_power_nasional.py / .ipynb untuk menghasilkan file ini."
        )

    cuaca = pd.read_csv(cuaca_path)

    print("Menjalankan disagregasi nasional (4 jenis PLT)...")
    df_final = disagregasi(cuaca, ANNUAL)

    lolos = validasi(df_final, ANNUAL)
    if not lolos:
        print("\n[PERINGATAN] Ada jenis/tahun yang gagal validasi. "
              "Cek data cuaca atau angka ANNUAL sebelum dipakai lebih lanjut.")

    df_final.to_csv(args.output, index=False)
    print(f"\n{'=' * 70}")
    print(f"SELESAI. {len(df_final)} baris disimpan ke {args.output}")
    print(f"{'=' * 70}")
    print("\nPratinjau:")
    print(df_final.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
