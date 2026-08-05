# -*- coding: utf-8 -*-
"""
disagregasi_regional.py
========================
Tahap 4 Regional (VERSI FINAL) — Disagregasi data tahunan (Produksi &
Kapasitas) menjadi bulanan per JENIS PLT INDIVIDUAL, berbasis data cuaca
riil NASA POWER.

Cakupan: 5 jenis PLT (PLTA, PLTM, PLTS, PLTS Atap, PLTB) -- bukan lagi
kategori gabungan (Hydro/Solar/Wind) seperti versi sebelumnya. Proporsi
cuaca bulanan tetap dihitung di level KATEGORI (karena koordinat & variabel
cuaca ditentukan per kategori di Tahap 2), lalu diterapkan ke angka tahunan
milik masing-masing jenis PLT individual secara terpisah.

PLTMH & PLT Hybrid TIDAK termasuk -- dikeluarkan dari scope penelitian
(lihat DOKUMENTASI_DATASET_REGIONAL_V2.md bagian 2).

Input:
    - cuaca_riil_regional.csv  (hasil Tahap 3, dari tarik_cuaca_nasa_power.py)
    - Angka tahunan terkunci per jenis PLT individual (hasil Tahap 1, dari
      sheet Worksheet file PERHITUNGAN_BAURAN_ENERGI_ESDM 2023/2024/2025 --
      2025 versi yang sudah diperbaiki Dinas ESDM, lihat dokumentasi bagian 3)

Output:
    - DATA_REGIONAL_5JENIS.csv

Cara pakai:
    python3 disagregasi_regional.py --cuaca cuaca_riil_regional.csv --output DATA_REGIONAL_5JENIS.csv
"""

import argparse
from pathlib import Path

import pandas as pd

# ── Angka tahunan terkunci per JENIS PLT INDIVIDUAL ─────────────────────────
# Sumber: sheet Worksheet, file PERHITUNGAN_BAURAN_ENERGI_ESDM 2023/2024/2025.
#
# CATATAN PENTING (lihat DOKUMENTASI_DATASET_REGIONAL_V2.md bagian 4):
# Kolom Produksi sumber ESDM BUKAN hasil pengukuran/metering, melainkan
# hasil kalkulasi Kapasitas x Capacity Factor asumsi x 8760 jam. Ini
# keterbatasan yang diwariskan dari sumber data primer, WAJIB diungkap di
# BAB IV/V, bukan disembunyikan.
#
# File 2025 yang dipakai di sini adalah VERSI YANG SUDAH DIPERBAIKI Dinas
# ESDM (label TAHUN benar, angka genuinely berbeda dari 2024, periode
# Januari-Desember penuh) -- bukan versi awal yang terkonfirmasi bermasalah
# (lihat dokumentasi bagian 3 untuk riwayat lengkap).
ANNUAL = {
    2023: {
        "PLTA":      {"Produksi": 3434.270400, "Kapasitas": 653.400000},
        "PLTM":      {"Produksi": 337.592880,  "Kapasitas": 64.230000},
        "PLTS":      {"Produksi": 9.005280,    "Kapasitas": 5.140000},
        "PLTS Atap": {"Produksi": 0.333756,    "Kapasitas": 0.190500},
        "PLTB":      {"Produksi": 569.400000,  "Kapasitas": 130.000000},
    },
    2024: {
        "PLTA":      {"Produksi": 3729.657600, "Kapasitas": 709.600000},
        "PLTM":      {"Produksi": 350.207280,  "Kapasitas": 66.630000},
        "PLTS":      {"Produksi": 9.005280,    "Kapasitas": 5.140000},
        "PLTS Atap": {"Produksi": 12.186036,   "Kapasitas": 6.955500},
        "PLTB":      {"Produksi": 626.340000,  "Kapasitas": 143.000000},
    },
    2025: {
        "PLTA":      {"Produksi": 4155.575468, "Kapasitas": 790.634602},
        "PLTM":      {"Produksi": 363.293017,  "Kapasitas": 69.119676},
        "PLTS":      {"Produksi": 10.975930,   "Kapasitas": 6.264800},
        "PLTS Atap": {"Produksi": 13.160919,   "Kapasitas": 7.511940},
        "PLTB":      {"Produksi": 688.974000,  "Kapasitas": 157.300000},
    },
}

# Tiap jenis PLT individual pakai data cuaca dari KATEGORI induknya (karena
# koordinat & parameter cuaca ditentukan di level kategori, Tahap 2).
PETA_KATEGORI = {
    "PLTA": "Hydro", "PLTM": "Hydro",
    "PLTS": "Solar", "PLTS Atap": "Solar",
    "PLTB": "Wind",
}

# Kategori yang perlu penyesuaian lag (efek tampungan waduk), bukan proporsi
# cuaca instan. Selain kategori ini, semua pakai proporsi langsung.
KATEGORI_PAKAI_LAG = {"Hydro"}
JENDELA_RATA_RATA_BERGERAK = 3  # bulan (bulan berjalan + 2 bulan sebelumnya)

TOLERANSI_VALIDASI = 0.01  # GWh, untuk cek SUM(bulanan) == tahunan


def hitung_basis_proporsi(sub: pd.DataFrame, kategori: str) -> pd.Series:
    """
    Hitung basis proporsi bulanan dari nilai cuaca.

    Untuk Hydro (PLTA, PLTM): rata-rata bergerak (proksi ketersediaan air
    waduk). Untuk kategori lain (Solar, Wind): nilai cuaca bulan itu
    sendiri (respons instan terhadap cuaca, tanpa penyimpanan energi).
    """
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
        description="Tahap 4 Regional: disagregasi 5 jenis PLT tahunan -> bulanan berbasis cuaca riil"
    )
    parser.add_argument("--cuaca", type=str, default="cuaca_riil_regional.csv",
                         help="Path ke CSV hasil Tahap 3 (tarik_cuaca_nasa_power.py)")
    parser.add_argument("--output", type=str, default="DATA_REGIONAL_5JENIS.csv",
                         help="Path output CSV hasil disagregasi")
    args = parser.parse_args()

    cuaca_path = Path(args.cuaca)
    if not cuaca_path.exists():
        raise FileNotFoundError(
            f"File cuaca tidak ditemukan: {cuaca_path}\n"
            f"Jalankan dulu tarik_cuaca_nasa_power.py / .ipynb untuk menghasilkan file ini."
        )

    cuaca = pd.read_csv(cuaca_path)

    print("Menjalankan disagregasi regional (5 jenis PLT)...")
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
