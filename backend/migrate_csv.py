"""
Migrasi satu kali: isi tabel `data_historis` dari dataset awal hasil pipeline.

Sumber: audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv (252 baris).
PENTING: dataset ini adalah hasil REKONSTRUKSI/ESTIMASI (lihat
audit/source/README.md), BUKAN observasi terverifikasi Dinas ESDM. Karena itu
seluruh baris hasil migrasi ini diberi `sumber = "rekonstruksi"` -- status
tersebut ikut tersimpan di database, bukan hanya jadi catatan di dokumentasi.

Skrip ini menolak jalan kalau tabel sudah terisi, supaya tidak menggandakan
data kalau terlanjur dijalankan dua kali. Pakai --reset untuk sengaja
mengosongkan tabel lebih dulu.

Jalankan dari dalam folder backend/:
    python migrate_csv.py
    python migrate_csv.py --reset
"""
import argparse
import sys

import pandas as pd
from sqlalchemy import delete, func, select

import config
from database import SessionLocal, init_db
from models import DataHistoris

# Nama kolom di CSV pipeline -> nama kolom di tabel. CSV memakai "Jenis"
# (bukan "Jenis_PLT"); pemetaan ini yang menjembataninya.
KOLOM_CSV = {
    "Tanggal": "tanggal",
    "Jenis": "jenis_plt",
    "Produksi": "produksi",
    "Kapasitas": "kapasitas",
    "Cuaca": "cuaca",
}


def baca_dataset() -> pd.DataFrame:
    if not config.DATASET_AWAL_PATH.exists():
        sys.exit(f"GAGAL: dataset awal tidak ditemukan di {config.DATASET_AWAL_PATH}")

    df = pd.read_csv(config.DATASET_AWAL_PATH)

    kolom_hilang = [k for k in KOLOM_CSV if k not in df.columns]
    if kolom_hilang:
        sys.exit(
            f"GAGAL: kolom {kolom_hilang} tidak ada di CSV. "
            f"Kolom yang ditemukan: {list(df.columns)}"
        )

    df = df[list(KOLOM_CSV)].rename(columns=KOLOM_CSV)

    # Parsing tanggal dibiarkan mengikuti default pandas, sama persis dengan
    # `pd.to_datetime(df["Tanggal"])` di pipeline training -- supaya urutan
    # deret waktu di database identik dengan yang dipakai saat model dilatih.
    df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date

    jenis_asing = sorted(set(df["jenis_plt"]) - set(config.JENIS_PLT_VALID))
    if jenis_asing:
        sys.exit(
            f"GAGAL: CSV memuat jenis PLT di luar whitelist: {jenis_asing}. "
            f"Whitelist: {config.JENIS_PLT_VALID}"
        )

    baris_kosong = df[df[["produksi", "kapasitas", "cuaca"]].isna().any(axis=1)]
    if not baris_kosong.empty:
        sys.exit(
            "GAGAL: ada baris dengan nilai kosong pada Produksi/Kapasitas/Cuaca "
            f"(baris CSV ke-{[i + 2 for i in baris_kosong.index]}). "
            "Perbaiki dataset sumbernya, jangan diisi otomatis di sini."
        )

    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Kosongkan tabel data_historis lebih dulu (menghapus data input pengguna juga).",
    )
    args = parser.parse_args()

    init_db()
    df = baca_dataset()

    with SessionLocal() as db:
        jumlah_awal = db.scalar(select(func.count()).select_from(DataHistoris))

        if jumlah_awal and not args.reset:
            sys.exit(
                f"DIBATALKAN: tabel data_historis sudah berisi {jumlah_awal} baris. "
                "Migrasi ini dirancang untuk sekali jalan. Pakai --reset kalau memang "
                "ingin mengosongkan tabel dan mengisinya ulang."
            )

        if args.reset and jumlah_awal:
            db.execute(delete(DataHistoris))
            print(f"Tabel dikosongkan ({jumlah_awal} baris dihapus).")

        db.add_all([
            DataHistoris(
                tanggal=row.tanggal,
                jenis_plt=row.jenis_plt,
                produksi=float(row.produksi),
                kapasitas=float(row.kapasitas),
                cuaca=float(row.cuaca),
                sumber=config.SUMBER_REKONSTRUKSI,
            )
            for row in df.itertuples(index=False)
        ])
        db.commit()

        total = db.scalar(select(func.count()).select_from(DataHistoris))
        per_plt = db.execute(
            select(DataHistoris.jenis_plt, func.count())
            .group_by(DataHistoris.jenis_plt)
            .order_by(DataHistoris.jenis_plt)
        ).all()
        per_sumber = db.execute(
            select(DataHistoris.sumber, func.count()).group_by(DataHistoris.sumber)
        ).all()

    print(f"Sumber   : {config.DATASET_AWAL_PATH}")
    print(f"Database : {config.DATABASE_PATH}")
    print(f"Tersimpan: {total} baris")
    print("Per jenis PLT:")
    for jenis, jumlah in per_plt:
        print(f"  {jenis:<12} {jumlah}")
    print("Per sumber:")
    for sumber, jumlah in per_sumber:
        print(f"  {sumber:<16} {jumlah}")


if __name__ == "__main__":
    main()
