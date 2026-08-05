# -*- coding: utf-8 -*-
"""
tarik_cuaca_nasa_power.py
==========================
Tahap 3 — Menarik data cuaca bulanan RIIL dari NASA POWER untuk 3 kategori
regional Sulsel (Opsi A: hasil Tahap 1 & 2).

CATATAN: skrip ini butuh koneksi internet aktif ke power.larc.nasa.gov.
Tidak bisa dijalankan di sandbox Claude (jaringan dibatasi) — jalankan di
Google Colab atau lingkungan lokal/Cowork yang punya akses internet penuh.

Cara pakai:
    pip install requests pandas
    python3 tarik_cuaca_nasa_power.py

Output: cuaca_riil_regional.csv
"""

import requests
import pandas as pd
from pathlib import Path

# ── Konfigurasi 3 titik koordinat kategori (hasil Tahap 2, Opsi A) ──────────
# Hydro  : centroid tertimbang kapasitas dari 7 PLTA besar (Luwu Timur/Luwu)
# Solar  : titik representatif provinsi (Makassar/Maros) — disagregasi
#          simplifikasi karena PLTS+PLTS Atap tersebar di >45 lokasi kecil
# Wind   : centroid tertimbang PLTB Sidrap + PLTB Jeneponto
LOKASI = {
    "Hydro": {"lat": -2.86, "lon": 120.79, "parameter": "PRECTOTCORR"},
    "Solar": {"lat": -5.10, "lon": 119.60, "parameter": "ALLSKY_SFC_SW_DWN"},
    "Wind":  {"lat": -4.64, "lon": 119.82, "parameter": "WS10M"},
}

START_YEAR = 2023
END_YEAR = 2025  # ganti ke 2026 kalau butuh data untuk validasi forecast

BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"


def tarik_data(nama_kategori: str, lat: float, lon: float, parameter: str) -> list[dict]:
    """Tarik satu parameter cuaca bulanan untuk satu titik koordinat."""
    params = {
        "parameters": parameter,
        "community": "RE",  # Renewable Energy — komunitas paling relevan
        "longitude": lon,
        "latitude": lat,
        "format": "JSON",
        "start": START_YEAR,
        "end": END_YEAR,
    }

    print(f"  Menarik {nama_kategori} ({parameter}) di ({lat}, {lon})...")
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    try:
        monthly = data["properties"]["parameter"][parameter]
    except KeyError:
        raise RuntimeError(
            f"Struktur respons tidak sesuai ekspektasi untuk {nama_kategori}. "
            f"Cek manual: {resp.url}"
        )

    rows = []
    for key, value in monthly.items():
        # Format key: "YYYYMM", contoh "202301". Bulan "13" = rata-rata
        # tahunan, bukan bulan sungguhan — dilewati.
        tahun, bulan = key[:4], key[4:6]
        if bulan == "13":
            continue
        if value == -999.0:  # kode missing value standar NASA POWER
            print(f"    [PERINGATAN] Data hilang untuk {tahun}-{bulan}, dilewati")
            continue
        rows.append({
            "Tahun": int(tahun),
            "Bulan": int(bulan),
            "Kategori": nama_kategori,
            "Parameter_Cuaca": parameter,
            "Nilai_Cuaca": value,
            "Lat": lat,
            "Lon": lon,
        })
    return rows


def main():
    semua_data = []
    print(f"Menarik data cuaca NASA POWER, {START_YEAR}-{END_YEAR}...\n")

    for kategori, info in LOKASI.items():
        hasil = tarik_data(kategori, info["lat"], info["lon"], info["parameter"])
        semua_data.extend(hasil)
        print(f"    -> {len(hasil)} baris berhasil ditarik\n")

    df = pd.DataFrame(semua_data)
    df = df.sort_values(["Kategori", "Tahun", "Bulan"]).reset_index(drop=True)

    out_path = Path("cuaca_riil_regional.csv")
    df.to_csv(out_path, index=False)

    print(f"{'=' * 60}")
    print(f"SELESAI. Total {len(df)} baris disimpan ke {out_path}")
    print(f"{'=' * 60}")
    print("\nPratinjau:")
    print(df.head(15).to_string(index=False))

    print("\nValidasi jumlah baris (harus 36 per kategori untuk 2023-2025):")
    print(df.groupby("Kategori").size())


if __name__ == "__main__":
    main()
