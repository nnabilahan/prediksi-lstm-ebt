"""
dataset_manager.py
=====================
INTI pengelolaan dataset historis EBT (data/data_historis_ebt.csv):
membaca, memvalidasi, menambah, mengubah, menghapus, dan menyimpan data.

PENTING:
- File ini HANYA membaca/menulis file CSV dataset. TIDAK ADA pemanggilan
  model, training, atau forecasting di mana pun dalam file ini.
- Setiap fungsi tambah/ubah/hapus akan menulis ulang data/data_historis_ebt.csv
  secara langsung (bukan hanya mengubah data di memori), supaya perubahan
  benar-benar tersimpan dan bisa dipakai training berikutnya secara manual.
"""

import os

import pandas as pd
import streamlit as st

from utils.data_loader import BASE_DIR
from utils.plt_ui_config import DAFTAR_JENIS_PLT

PATH_DATASET = os.path.join(BASE_DIR, "data", "data_historis_ebt.csv")

KOLOM_DATASET = ["ID", "Tanggal", "Jenis_PLT", "Produksi", "Kapasitas", "Cuaca"]


def load_dataset() -> pd.DataFrame:
    """
    Membaca dataset historis dari data/data_historis_ebt.csv.
    TIDAK memakai st.cache_data (beda dengan halaman lain) karena dataset
    ini bersifat MUTABLE -- sering berubah lewat tambah/edit/hapus/impor,
    sehingga harus selalu dibaca fresh dari file setiap kali dipanggil.
    """
    if not os.path.exists(PATH_DATASET):
        # Jika file belum ada sama sekali, buat dataset kosong dengan skema yang benar
        df_kosong = pd.DataFrame(columns=KOLOM_DATASET)
        df_kosong.to_csv(PATH_DATASET, index=False)
        return df_kosong

    df = pd.read_csv(PATH_DATASET, parse_dates=["Tanggal"])
    return df


def simpan_dataset(df: pd.DataFrame) -> None:
    """
    Menyimpan (menulis ulang) dataset ke data/data_historis_ebt.csv.
    Dipanggil setelah operasi tambah/ubah/hapus/impor selesai divalidasi.
    """
    df_simpan = df.copy()
    df_simpan["Tanggal"] = pd.to_datetime(df_simpan["Tanggal"]).dt.strftime("%Y-%m-%d")
    df_simpan = df_simpan[KOLOM_DATASET].sort_values(["Tanggal", "Jenis_PLT"]).reset_index(drop=True)
    df_simpan.to_csv(PATH_DATASET, index=False)


def id_berikutnya(df: pd.DataFrame) -> int:
    """Menentukan ID baru (max ID + 1), supaya ID tidak pernah dipakai ulang meski ada penghapusan."""
    if df.empty:
        return 1
    return int(df["ID"].max()) + 1


def validasi_data_baru(df: pd.DataFrame, tanggal, jenis_plt: str, produksi: float,
                        kapasitas: float, cuaca: float, id_dikecualikan: int = None) -> list:
    """
    Memvalidasi satu baris data (dipakai untuk fitur Tambah maupun Edit).

    Parameters
    ----------
    id_dikecualikan : int, optional
        ID baris yang sedang diedit (dikecualikan dari pengecekan duplikat
        terhadap dirinya sendiri). Kosongkan (None) untuk validasi data BARU.

    Returns
    -------
    list berisi pesan error (list kosong berarti valid).
    """
    error = []

    # --- Validasi field kosong ---
    if tanggal is None:
        error.append("Tanggal wajib diisi.")
    if not jenis_plt:
        error.append("Jenis PLT wajib dipilih.")
    if produksi is None:
        error.append("Produksi wajib diisi.")
    if kapasitas is None:
        error.append("Kapasitas wajib diisi.")
    if cuaca is None:
        error.append("Variabel cuaca wajib diisi.")

    if error:
        return error  # hentikan di sini, validasi lanjutan butuh semua field terisi

    # --- Validasi nilai tidak boleh negatif ---
    if produksi < 0:
        error.append("Produksi tidak boleh bernilai negatif.")
    if kapasitas < 0:
        error.append("Kapasitas tidak boleh bernilai negatif.")
    if cuaca < 0:
        error.append("Variabel cuaca tidak boleh bernilai negatif.")

    # --- Validasi format/rentang tanggal wajar (2020-2030) ---
    try:
        tanggal_ts = pd.Timestamp(tanggal)
        if tanggal_ts.year < 2020 or tanggal_ts.year > 2030:
            error.append("Tahun pada tanggal di luar rentang wajar (2020-2030).")
    except Exception:
        error.append("Format tanggal tidak valid.")
        return error

    # --- Validasi duplikat: kombinasi Tanggal + Jenis PLT harus unik ---
    if not df.empty:
        subset = df if id_dikecualikan is None else df[df["ID"] != id_dikecualikan]
        duplikat = subset[
            (pd.to_datetime(subset["Tanggal"]).dt.date == tanggal_ts.date())
            & (subset["Jenis_PLT"] == jenis_plt)
        ]
        if not duplikat.empty:
            error.append(
                f"Data untuk {jenis_plt} pada tanggal {tanggal_ts.strftime('%d %b %Y')} sudah ada (duplikat)."
            )

    return error


def tambah_data(tanggal, jenis_plt: str, produksi: float, kapasitas: float, cuaca: float) -> tuple:
    """
    Menambahkan satu baris data baru ke dataset, setelah validasi.

    Returns
    -------
    tuple (berhasil: bool, pesan: list[str])
    """
    df = load_dataset()
    error = validasi_data_baru(df, tanggal, jenis_plt, produksi, kapasitas, cuaca)
    if error:
        return False, error

    baris_baru = {
        "ID": id_berikutnya(df),
        "Tanggal": pd.Timestamp(tanggal).strftime("%Y-%m-%d"),
        "Jenis_PLT": jenis_plt,
        "Produksi": float(produksi),
        "Kapasitas": float(kapasitas),
        "Cuaca": float(cuaca),
    }
    df_baru = pd.concat([df, pd.DataFrame([baris_baru])], ignore_index=True)
    simpan_dataset(df_baru)
    return True, ["Data baru berhasil ditambahkan."]


def ubah_data(id_baris: int, tanggal, jenis_plt: str, produksi: float,
              kapasitas: float, cuaca: float) -> tuple:
    """
    Mengubah data yang sudah ada (dicari berdasarkan ID), setelah validasi.

    Returns
    -------
    tuple (berhasil: bool, pesan: list[str])
    """
    df = load_dataset()
    if id_baris not in df["ID"].values:
        return False, ["Data dengan ID tersebut tidak ditemukan."]

    error = validasi_data_baru(df, tanggal, jenis_plt, produksi, kapasitas, cuaca, id_dikecualikan=id_baris)
    if error:
        return False, error

    idx = df.index[df["ID"] == id_baris][0]
    df.loc[idx, "Tanggal"] = pd.Timestamp(tanggal).strftime("%Y-%m-%d")
    df.loc[idx, "Jenis_PLT"] = jenis_plt
    df.loc[idx, "Produksi"] = float(produksi)
    df.loc[idx, "Kapasitas"] = float(kapasitas)
    df.loc[idx, "Cuaca"] = float(cuaca)

    simpan_dataset(df)
    return True, ["Data berhasil diperbarui."]


def hapus_data(id_baris: int) -> tuple:
    """
    Menghapus satu baris data berdasarkan ID.
    (Konfirmasi ke pengguna ditangani di komponen UI, bukan di sini.)

    Returns
    -------
    tuple (berhasil: bool, pesan: list[str])
    """
    df = load_dataset()
    if id_baris not in df["ID"].values:
        return False, ["Data dengan ID tersebut tidak ditemukan."]

    df_baru = df[df["ID"] != id_baris].reset_index(drop=True)
    simpan_dataset(df_baru)
    return True, ["Data berhasil dihapus."]


def ringkasan_dataset(df: pd.DataFrame) -> dict:
    """Menghitung ringkasan dataset: jumlah data, jumlah jenis PLT, rentang tahun."""
    if df.empty:
        return {"jumlah_data": 0, "jumlah_jenis_plt": 0, "tahun_min": "-", "tahun_max": "-"}

    tahun = pd.to_datetime(df["Tanggal"]).dt.year
    return {
        "jumlah_data": len(df),
        "jumlah_jenis_plt": df["Jenis_PLT"].nunique(),
        "tahun_min": int(tahun.min()),
        "tahun_max": int(tahun.max()),
    }


# ------------------------------------------------------------------
# IMPOR DATASET (CSV/Excel)
# ------------------------------------------------------------------
KOLOM_WAJIB_IMPOR = ["Tanggal", "Jenis_PLT", "Produksi", "Kapasitas", "Cuaca"]


def periksa_skema_impor(df_mentah: pd.DataFrame) -> list:
    """
    Memeriksa apakah file yang diunggah memiliki kolom wajib yang benar.
    Returns list pesan error (kosong berarti skema valid).
    """
    kolom_hilang = [k for k in KOLOM_WAJIB_IMPOR if k not in df_mentah.columns]
    if kolom_hilang:
        return [
            f"Kolom wajib berikut tidak ditemukan pada file: {', '.join(kolom_hilang)}. "
            f"Skema yang dibutuhkan: {', '.join(KOLOM_WAJIB_IMPOR)} (kolom ID opsional)."
        ]
    return []


def validasi_baris_impor(df_mentah: pd.DataFrame) -> tuple:
    """
    Memvalidasi setiap baris pada file yang diimpor (format, field kosong,
    nilai negatif, jenis PLT dikenal, dan duplikat DI DALAM file itu sendiri).

    Returns
    -------
    tuple (df_valid, daftar_pesan_dilewati)
        df_valid: DataFrame hanya berisi baris yang lolos validasi
        daftar_pesan_dilewati: list string, penjelasan baris yang dilewati
    """
    baris_valid = []
    pesan_dilewati = []
    kombinasi_terpakai = set()

    for i, baris in df_mentah.iterrows():
        nomor_baris = i + 2  # perkiraan nomor baris di file (memperhitungkan header)

        try:
            tanggal = pd.Timestamp(baris["Tanggal"])
        except Exception:
            pesan_dilewati.append(f"Baris {nomor_baris}: format Tanggal tidak valid.")
            continue

        jenis_plt = str(baris["Jenis_PLT"]).strip()
        if jenis_plt not in DAFTAR_JENIS_PLT:
            pesan_dilewati.append(f"Baris {nomor_baris}: Jenis PLT '{jenis_plt}' tidak dikenal.")
            continue

        try:
            produksi = float(baris["Produksi"])
            kapasitas = float(baris["Kapasitas"])
            cuaca = float(baris["Cuaca"])
        except Exception:
            pesan_dilewati.append(f"Baris {nomor_baris}: Produksi/Kapasitas/Cuaca bukan angka.")
            continue

        if pd.isna(produksi) or pd.isna(kapasitas) or pd.isna(cuaca):
            pesan_dilewati.append(f"Baris {nomor_baris}: ada nilai kosong pada Produksi/Kapasitas/Cuaca.")
            continue

        if produksi < 0 or kapasitas < 0 or cuaca < 0:
            pesan_dilewati.append(f"Baris {nomor_baris}: ada nilai negatif (tidak wajar).")
            continue

        kunci = (tanggal.date(), jenis_plt)
        if kunci in kombinasi_terpakai:
            pesan_dilewati.append(f"Baris {nomor_baris}: duplikat dengan baris lain di file yang sama.")
            continue
        kombinasi_terpakai.add(kunci)

        baris_valid.append({
            "Tanggal": tanggal.strftime("%Y-%m-%d"),
            "Jenis_PLT": jenis_plt,
            "Produksi": produksi,
            "Kapasitas": kapasitas,
            "Cuaca": cuaca,
        })

    df_valid = pd.DataFrame(baris_valid) if baris_valid else pd.DataFrame(columns=KOLOM_WAJIB_IMPOR)
    return df_valid, pesan_dilewati


def proses_impor(df_valid: pd.DataFrame, mode: str) -> dict:
    """
    Memproses hasil impor yang sudah divalidasi ke dataset utama.

    Parameters
    ----------
    df_valid : DataFrame hasil dari validasi_baris_impor()
    mode : "Gabung dengan data yang ada" atau "Ganti seluruh dataset"

    Returns
    -------
    dict ringkasan: jumlah_ditambahkan, jumlah_dilewati_duplikat
    """
    if mode == "Ganti seluruh dataset":
        df_final = df_valid.copy()
        df_final.insert(0, "ID", range(1, len(df_final) + 1))
        simpan_dataset(df_final)
        return {"jumlah_ditambahkan": len(df_final), "jumlah_dilewati_duplikat": 0}

    # --- Mode gabung: cek duplikat terhadap dataset yang SUDAH ADA ---
    df_ada = load_dataset()
    kombinasi_ada = set(
        zip(pd.to_datetime(df_ada["Tanggal"]).dt.date, df_ada["Jenis_PLT"])
    ) if not df_ada.empty else set()

    baris_ditambahkan = []
    jumlah_dilewati = 0
    id_berjalan = id_berikutnya(df_ada)

    for _, baris in df_valid.iterrows():
        kunci = (pd.Timestamp(baris["Tanggal"]).date(), baris["Jenis_PLT"])
        if kunci in kombinasi_ada:
            jumlah_dilewati += 1
            continue
        baris_baru = baris.to_dict()
        baris_baru["ID"] = id_berjalan
        baris_ditambahkan.append(baris_baru)
        kombinasi_ada.add(kunci)
        id_berjalan += 1

    if baris_ditambahkan:
        df_final = pd.concat([df_ada, pd.DataFrame(baris_ditambahkan)], ignore_index=True)
        simpan_dataset(df_final)

    return {"jumlah_ditambahkan": len(baris_ditambahkan), "jumlah_dilewati_duplikat": jumlah_dilewati}
