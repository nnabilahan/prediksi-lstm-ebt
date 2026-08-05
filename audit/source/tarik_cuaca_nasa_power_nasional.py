# -*- coding: utf-8 -*-
"""
tarik_cuaca_nasa_power_nasional.py
====================================
Tahap 3 Nasional — Menarik data cuaca bulanan RIIL dari NASA POWER untuk
3 kategori nasional (Hydro, Solar, Wind), 2013-2023 (11 tahun).

Versi nasional dari tarik_cuaca_nasa_power.py (regional). Struktur & logika
identik, cuma beda koordinat dan rentang tahun -- lihat DOKUMENTASI_DATASET
untuk justifikasi pemilihan koordinat masing-masing kategori.

CATATAN: skrip ini butuh koneksi internet aktif ke power.larc.nasa.gov.
Tidak bisa dijalankan di sandbox Claude (jaringan dibatasi) -- jalankan di
Google Colab atau lingkungan lokal/Cowork yang punya akses internet penuh.

Cara pakai:
    pip install requests pandas
    python3 tarik_cuaca_nasa_power_nasional.py

Output: cuaca_riil_nasional.csv
"""

import requests
import pandas as pd
from pathlib import Path

# ── Konfigurasi 3 titik koordinat kategori NASIONAL (hasil Tahap 2 Nasional) ─
# Hydro  : centroid tertimbang 3 klaster PLTA besar (Jawa Barat/Tengah --
#          Cirata, Saguling, Jatiluhur, Mrica; Sulawesi Tengah -- Poso;
#          Sumatera Utara -- Sigura-gura, Asahan, Tangga). Simplifikasi dari
#          pembangkit terbesar yang terdokumentasi publik, BUKAN registry
#          lengkap nasional (beda dari regional yang punya daftar lengkap
#          dari sheet Data Energi ESDM Sulsel).
# Solar  : titik representatif Jawa Barat (area Cirata, lokasi PLTS
#          Terapung Cirata 192 MWp) -- simplifikasi.
# Wind   : SAMA PERSIS dengan koordinat regional Sulsel -- karena PLTB
#          Sidrap (75 MW) + Tolo/Jeneponto (72 MW) mencakup ~97% dari total
#          kapasitas Wind nasional 2023 (152,30 MW). Ini bukan simplifikasi
#          longgar, tapi representasi yang akurat secara empiris.
LOKASI = {
    "Hydro": {"lat": -4.40, "lon": 107.95, "parameter": "PRECTOTCORR"},
    "Solar": {"lat": -6.85, "lon": 107.40, "parameter": "ALLSKY_SFC_SW_DWN"},
    "Wind":  {"lat": -4.64, "lon": 119.82, "parameter": "WS10M"},
}

START_YEAR = 2013
END_YEAR = 2023  # 11 tahun, sesuai cakupan HEESI Tahap 1 Nasional

BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

BARIS_PER_KATEGORI_EKSPEKTASI = (END_YEAR - START_YEAR + 1) * 12  # 132 untuk 2013-2023


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
        # Format key: "YYYYMM", contoh "201301". Bulan "13" = rata-rata
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
    print(f"Menarik data cuaca NASA POWER (NASIONAL), {START_YEAR}-{END_YEAR}...\n")

    for kategori, info in LOKASI.items():
        hasil = tarik_data(kategori, info["lat"], info["lon"], info["parameter"])
        semua_data.extend(hasil)
        print(f"    -> {len(hasil)} baris berhasil ditarik\n")

    df = pd.DataFrame(semua_data)
    df = df.sort_values(["Kategori", "Tahun", "Bulan"]).reset_index(drop=True)

    out_path = Path("cuaca_riil_nasional.csv")
    df.to_csv(out_path, index=False)

    print(f"{'=' * 60}")
    print(f"SELESAI. Total {len(df)} baris disimpan ke {out_path}")
    print(f"{'=' * 60}")
    print("\nPratinjau:")
    print(df.head(15).to_string(index=False))

    print(f"\nValidasi jumlah baris (harus {BARIS_PER_KATEGORI_EKSPEKTASI} per kategori "
          f"untuk {START_YEAR}-{END_YEAR}):")
    for kategori in LOKASI:
        jumlah = len(df[df["Kategori"] == kategori])
        status = "OK" if jumlah == BARIS_PER_KATEGORI_EKSPEKTASI else \
            f"KURANG ({jumlah}/{BARIS_PER_KATEGORI_EKSPEKTASI}) -- cek peringatan di atas"
        print(f"  {kategori}: {status}")


if __name__ == "__main__":
    main()
