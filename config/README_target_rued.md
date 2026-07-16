# Catatan: config/target_rued.csv

**STATUS: PLACEHOLDER** — angka di file ini BUKAN angka resmi RUED Provinsi
Sulawesi Selatan. Angka ini disusun agar besarannya sepadan dengan skala
hasil forecast model (supaya gap analysis bisa diuji & didemokan), BUKAN
hasil kutipan dari dokumen RUED resmi.

## Cara memperbarui dengan angka resmi

1. Buka `config/target_rued.csv` dengan Excel/text editor.
2. Kolom yang ada: `Tahun`, `Jenis_PLT`, `Target_RUED_GWh`.
3. Ganti nilai `Target_RUED_GWh` sesuai target resmi per jenis PLT & tahun
   dari dokumen RUED / Perda Provinsi Sulawesi Selatan.
4. Simpan file (format & nama kolom harus tetap sama).
5. Jalankan ulang aplikasi Streamlit (`streamlit run app.py`) — halaman
   Gap Analysis RUED akan otomatis membaca nilai baru TANPA perlu
   mengubah kode program sama sekali.

## Catatan tambahan

- "Total Produksi EBT" pada halaman Gap Analysis dihitung otomatis dengan
  MENJUMLAHKAN forecast & target seluruh jenis PLT pada baris di atas -
  bukan angka Total yang terpisah - supaya selalu konsisten.
- Jika RUED resmi memiliki target dalam bentuk "bauran energi (%)" bukan
  GWh, konversi ke GWh terlebih dahulu (target % dikali proyeksi total
  kebutuhan listrik provinsi pada tahun terkait) sebelum diisi ke file ini.
