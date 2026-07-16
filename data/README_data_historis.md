# Catatan: data/data_historis_ebt.csv

**STATUS: DATA SINTETIS (PLACEHOLDER)** — bukan data historis resmi Dinas
ESDM Provinsi Sulawesi Selatan. Nilainya dibangkitkan secara terprogram
(seed=42) agar berada pada rentang yang sama dengan data yang dipakai saat
melatih model LSTM (lihat `scalers/scaler_fitur_*.pkl` &
`scalers/scaler_target_*.pkl`), supaya fitur Data Management (tambah/edit/
hapus/impor/ekspor/filter) bisa langsung diuji dengan data yang realistis
secara skala.

## Skema kolom

| Kolom      | Tipe   | Keterangan                                          |
|------------|--------|------------------------------------------------------|
| ID         | int    | ID unik baris, dibuat otomatis oleh aplikasi         |
| Tanggal    | date   | Format YYYY-MM-DD (awal bulan)                        |
| Jenis_PLT  | text   | PLTA/PLTB/PLTM/PLTMH/PLTS/PLTS Atap/PLT Hybrid       |
| Produksi   | float  | Produksi EBT (GWh, asumsi)                            |
| Kapasitas  | float  | Kapasitas pembangkit (MW, asumsi)                     |
| Cuaca      | float  | Curah hujan/kecepatan angin/radiasi matahari (sesuai jenis PLT) |

## Cara mengganti dengan data resmi

Gunakan fitur **Impor Dataset (CSV/Excel)** di halaman Data EBT pada
aplikasi Streamlit — unggah file dengan skema kolom yang sama (boleh tanpa
kolom `ID`, akan dibuat otomatis), lalu pilih mode "Gabung" atau "Ganti
Seluruh Data". Tidak perlu mengubah kode maupun file ini secara manual.

## Catatan penting

- File ini adalah dataset yang DIKELOLA (dibaca & ditulis ulang) oleh
  halaman Data EBT. Setiap tambah/edit/hapus/impor akan langsung menulis
  ulang file ini.
- Perubahan pada file ini TIDAK memicu pelatihan ulang model secara
  otomatis. Untuk melatih ulang model dengan data terbaru, unduh dataset
  ini (fitur Ekspor) lalu gunakan secara manual di pipeline Google Colab.
