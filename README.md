# SIPREBAR
**Sistem Prediksi Energi Baru Terbarukan**

Aplikasi web untuk memantau produksi EBT sektor kelistrikan, menampilkan hasil prediksi model LSTM, dan mendukung evaluasi pencapaian Rencana Umum Energi Daerah (RUED) Provinsi Sulawesi Selatan.

> Dikembangkan sebagai bagian dari penelitian skripsi:
> *"Prediksi Konsumsi Energi Baru Terbarukan Sektor Kelistrikan Menggunakan Deep Learning: Implementasi Long Short-Term Memory pada Data Dinas ESDM Provinsi Sulawesi Selatan"*
> UIN Alauddin Makassar — Teknik Informatika, 2026

---

## Prasyarat

Pastikan perangkat sudah terinstal:

| Perangkat | Versi minimum | Cek versi   |
|-----------|---------------|-------------|
| Node.js   | 18.x          | `node -v`   |
| npm       | 9.x           | `npm -v`    |
| Python    | 3.10–3.12     | `python --version` |

Python dibutuhkan untuk menjalankan **backend** (lihat [Menjalankan Backend](#menjalankan-backend)) — Dashboard dan Gap Analysis RUED tetap statis dan tidak butuh backend untuk ditampilkan; backend dipakai untuk mengelola data historis (CRUD) dan menjalankan inferensi LSTM di halaman **Data EBT** dan **Prediksi**.

Backend juga butuh artefak model produksi (`audit/results/production_model/models/*.keras` beserta `config/konfigurasi_model.json` dan `scalers/scaler_params.json`) sudah ada di mesin lokal. File `.keras` tidak ikut di-commit ke git — reproduksi dalam hitungan menit dengan:

```bash
python audit/analysis/build_production_model.py
```

---

## Cara Menjalankan (Development)

Aplikasi terdiri dari dua proses terpisah yang perlu dijalankan **bersamaan** di dua terminal: **frontend** (React + Vite, port 5173) dan **backend** (FastAPI, port 8000).

### 1. Clone atau salin folder proyek

```bash
# Jika menggunakan Git
git clone <url-repositori>
cd siprebar

# Atau langsung masuk ke folder proyek
cd siprebar
```

### 2. Jalankan frontend

```bash
npm install
npm run dev
```

Perintah `npm install` mengunduh semua package ke folder `node_modules/`. Setelah `npm run dev` berhasil, terminal akan menampilkan:

```
VITE v6.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

Buka **http://localhost:5173** di browser (Chrome / Edge / Firefox).

> Jika port 5173 sudah dipakai, Vite otomatis memilih port berikutnya (5174, 5175, dst). Perhatikan output terminal untuk URL yang benar.

### 3. Jalankan backend (terminal terpisah)

Lihat [Menjalankan Backend](#menjalankan-backend) di bawah untuk langkah lengkap (install dependensi, migrasi data awal, start server). Backend harus berjalan di **http://localhost:8000** — CORS di backend menerima permintaan dari origin `localhost` port berapa pun, jadi tetap jalan kalau Vite pindah ke 5174/5175.

Tanpa backend berjalan, halaman **Data EBT** dan **Prediksi** akan menampilkan pesan error yang jelas ("Tidak dapat terhubung ke backend...") alih-alih data — Dashboard dan Gap Analysis RUED tetap berfungsi normal karena datanya statis dari `src/lib/data.js`.

---

## Menjalankan Backend

Backend melayani tiga hal: **CRUD data historis EBT** (dipakai halaman Data EBT), **penyiapan bahan inferensi** (`GET /api/prediksi/siap` — window historis + nilai cuaca otomatis), dan **inferensi model LSTM** (`POST /api/predict`). Backend **tidak pernah melatih ulang model** — hanya memuat artefak `.keras` yang sudah ada.

### 1. Install dependensi Python

Dari root folder proyek:

```bash
pip install -r backend/requirements.txt
```

Dependensi ini terpisah dari kebutuhan pipeline training (`audit/`) — mencakup FastAPI, SQLAlchemy, TensorFlow, dan scikit-learn (untuk memuat model & scaler).

### 2. Migrasi data awal ke database (sekali saja)

```bash
cd backend
python migrate_csv.py
```

Mengisi database SQLite lokal (`backend/siprebar.db`, dibuat otomatis, tidak ikut di-commit) dengan **180 baris** dari `audit/source/DATA_REGIONAL_5JENIS.csv` (5 jenis PLT × 3 tahun × 12 bulan, **regional Sulawesi Selatan**), ditandai `sumber = "rekonstruksi"` di setiap baris. Skrip menolak jalan ulang kalau database sudah terisi (supaya tidak menggandakan data); pakai `python migrate_csv.py --reset` kalau sengaja ingin mengosongkan dan mengisi ulang.

> **Penting — jangan mengimpor dataset nasional ke database ini.** Aplikasi menampilkan data **regional Sulsel**. Dataset nasional (`DATA_NASIONAL_*.csv`) memakai skala kapasitas yang jauh berbeda (PLTA ±5.000–6.000 MW vs ±650–790 MW regional) dan hanya memuat 4 jenis PLT. Mencampurnya lewat fitur Impor akan membuat tabel menampilkan dua versi untuk tahun yang sama dan statistik menjadi salah. Filter **Asal data** di halaman Data EBT bisa dipakai untuk memeriksa baris mana yang berasal dari dataset awal dan mana yang ditambahkan sendiri.

### 3. Jalankan server backend

```bash
python -m uvicorn main:app --reload --port 8000
```

(Perintah di atas dijalankan dari dalam folder `backend/`.) Buka **http://localhost:8000/docs** untuk dokumentasi API interaktif (Swagger, dibuat otomatis oleh FastAPI), atau **http://localhost:8000/api/health** untuk cek cepat status server, database, dan ketersediaan artefak model per jenis PLT.

> Di Windows, flag `--reload` uvicorn kadang memicu galat reload bawaan `asyncio` saat menyimpan file berulang kali. Kalau itu terjadi, jalankan tanpa `--reload` (`python -m uvicorn main:app --port 8000`) dan restart manual setiap kali mengubah kode backend.

---

## Perintah yang Tersedia

| Perintah | Fungsi |
|----------|--------|
| `npm run dev` | Jalankan server development dengan hot-reload |
| `npm run build` | Build aplikasi untuk produksi (output di folder `dist/`) |
| `npm run preview` | Preview hasil build produksi secara lokal |

---

## Build untuk Produksi

```bash
# 1. Build
npm run build

# 2. Preview hasil build
npm run preview
```

Folder `dist/` yang dihasilkan berisi file statis (HTML, CSS, JS) yang bisa di-deploy ke web server mana pun (Nginx, Apache, Vercel, Netlify, dll.).

### Deploy ke Nginx (contoh)

```nginx
server {
    listen 80;
    server_name siprebar.esdm.sulsel.go.id;
    root /var/www/siprebar/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Struktur Proyek

```
siprebar/
├── backend/
│   ├── main.py               # App FastAPI, CORS, GET /api/health
│   ├── config.py             # Path artefak, whitelist jenis PLT, baca konfigurasi_model.json
│   ├── database.py           # Engine & session SQLAlchemy (SQLite)
│   ├── models.py             # Model ORM tabel data_historis
│   ├── schemas.py            # Skema Pydantic request/response
│   ├── ml.py                 # Muat model/scaler LSTM sekali saat startup, fungsi inferensi
│   ├── migrate_csv.py        # Migrasi data awal CSV -> database (sekali jalan)
│   ├── cuaca.py              # Ambil nilai Cuaca: NASA POWER (bulan lampau) / klimatologi
│   ├── routers/
│   │   ├── data.py           # GET/POST/PUT/DELETE /api/data, export, import
│   │   ├── predict.py        # POST /api/predict (4 lapis validasi)
│   │   └── prediksi_cepat.py # GET /api/prediksi/siap (window histori + cuaca otomatis)
│   ├── requirements.txt
│   └── siprebar.db           # Database SQLite lokal (dibuat migrate_csv.py, tidak di-commit)
├── src/
│   ├── lib/
│   │   ├── tokens.js        # Design tokens (semua warna)
│   │   ├── data.js          # AUTO-GENERATED: forecast 2026-2028, gap RUED, dll. -- statis, hasil riset
│   │   ├── api.js           # Klien fetch ke backend (dipakai DataEBT.jsx & Prediksi.jsx)
│   │   └── utils.js         # Helper fmt() dan buildMonthly()
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TopNav.jsx   # Navigasi atas (2 lapisan)
│   │   │   └── Footer.jsx   # Footer sitasi
│   │   ├── ui/              # Komponen UI (Panel, Stat, Note, Gauge, dll.)
│   │   └── charts/          # Komponen chart (MonthlyChart, DonutChart, dll.)
│   ├── pages/               # 4 halaman utama
│   │   ├── Dashboard.jsx    # Statis (data.js)
│   │   ├── Prediksi.jsx     # Live: inferensi LSTM 1 bulan ke depan lewat backend
│   │   ├── GapAnalysis.jsx  # Statis (data.js)
│   │   └── DataEBT.jsx      # Live dari backend (GET/POST/PUT/DELETE/import/export /api/data)
│   ├── App.jsx
│   └── main.jsx
├── audit/                    # Pipeline training, hasil audit, dan artefak model (lihat audit/*/README*)
├── index.html
├── tailwind.config.js
├── vite.config.js
└── package.json
```

---

## Tech Stack

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| React | 18 | Framework UI |
| Vite | 6 | Build tool & dev server |
| Tailwind CSS | 3 | Utility-first styling |
| recharts | 2 | Visualisasi data / grafik |
| lucide-react | latest | Icon set |
| FastAPI | 0.115 | Backend REST API |
| SQLAlchemy | 2.0 | ORM (SQLite lokal, siap pindah ke PostgreSQL) |
| TensorFlow / Keras | 2.19 | Memuat model LSTM terlatih untuk inferensi |
| scikit-learn | 1.6 | Memuat scaler (`MinMaxScaler`) hasil training |

---

## Data Statis vs Data Live (Backend)

Bagian tertentu dari aplikasi **sengaja tetap statis** dari `src/lib/data.js` (hasil riset skripsi yang sudah divalidasi — angka forecast, MAPE, dan perbandingan metode tidak berubah hanya karena data historis di database berubah):

| Halaman / bagian | Sumber | Live via backend? |
|---|---|---|
| Dashboard — seluruh isi | `data.js` | Tidak |
| Gap Analysis — forecast & gap RUED | `data.js` | Tidak |
| Gap Analysis — tabel pembanding metode | `data.js` (`MODEL_COMPARISON`) | Tidak |
| Prediksi — penyiapan data & cuaca | `GET /api/prediksi/siap` | **Ya** |
| Prediksi — inferensi LSTM | `POST /api/predict` | **Ya** |
| Data EBT — tabel, tambah/ubah/hapus/impor/ekspor | `GET/POST/PUT/DELETE /api/data`, `/export`, `/import` | **Ya** |

Alasan bagian statis tetap statis: angka forecast 2026–2028 dan hasil evaluasi model adalah **keluaran pipeline riset yang sudah difinalisasi**. Menjadikannya live berarti angka di skripsi bisa berubah hanya karena seseorang menambah satu baris di database.

**Perbedaan grafik Dashboard vs halaman Prediksi** — keduanya bukan hal yang sama:

| | Dashboard | Prediksi |
|---|---|---|
| Horizon | 36 bulan (2026–2028) | 1 bulan ke depan |
| Dihitung kapan | sekali, saat pipeline riset dijalankan | saat tombol ditekan |
| Sifat | otoregresif (prediksi jadi input bulan berikutnya) | satu langkah, dari data historis nyata |
| Cuaca | asumsi normal klimatologis sepanjang horizon | NASA POWER kalau tersedia, kalau tidak klimatologis |

---

## Metodologi & Catatan Data

Bagian ini memuat catatan yang sebelumnya ditempelkan sebagai card di antarmuka. Dipindahkan ke sini supaya halaman tetap ringkas, tanpa menghilangkan kualifikasi yang wajib diungkap di laporan.

### Asal-usul dataset

Cakupan: **sektor kelistrikan Provinsi Sulawesi Selatan**, 5 jenis PLT (PLTA, PLTB, PLTM, PLTS, PLTS Atap), Januari 2023 – Desember 2025 (180 baris bulanan).

| Kolom | Asal | Status |
|---|---|---|
| Produksi (GWh) | disagregasi bulanan dari angka **tahunan** Dinas ESDM Sulsel | **rekonstruksi**, bukan metering langsung |
| Kapasitas (MW) | data kapasitas terpasang Dinas ESDM Sulsel | tercatat |
| Cuaca | NASA POWER (`power.larc.nasa.gov`) | observasi riil |

Angka tahunan Dinas ESDM sendiri merupakan kalkulasi **Kapasitas × Capacity Factor asumsi × 8760 jam**, bukan hasil pengukuran meter. Konsekuensinya: kolom Produksi mewarisi pola dari Kapasitas dan asumsi CF. Ini di luar kendali penelitian — dataset tersebut yang tersedia dan disetujui sebagai sumber resmi. Skrip disagregasi ada di `audit/source/disagregasi_regional.py`, dokumentasi lengkap di `audit/source/DOKUMENTASI_DATASET_REGIONAL_V2.md`.

Parameter cuaca per kategori (titik koordinat di `backend/cuaca.py`, disalin dari `audit/source/tarik_cuaca_nasa_power.py`):

| Jenis PLT | Parameter NASA POWER | Satuan |
|---|---|---|
| PLTA, PLTM | `PRECTOTCORR` (curah hujan) | mm/hari |
| PLTB | `WS10M` (kecepatan angin 10 m) | m/s |
| PLTS, PLTS Atap | `ALLSKY_SFC_SW_DWN` (radiasi) | kWh/m² |

### Model produksi

Dibangun oleh `audit/analysis/build_production_model.py` → `audit/results/production_model/`. Arsitektur: **pooled LSTM + category embedding + ensembling 3 seed**, kombinasi per jenis PLT dipilih lewat **walk-forward validation** (bukan skor data uji).

| Jenis PLT | Kombinasi | Window |
|---|---|---|
| PLTA | Varian B, lr 1e−3 | 3 bulan |
| PLTB | Varian B, lr 1e−3 | **6 bulan** |
| PLTM | Varian B, lr 1e−4 | 3 bulan |
| PLTS, PLTS Atap | Varian C, lr 1e−3 (berbagi 1 model) | 3 bulan |

Window berbeda per jenis PLT karena tiap kategori punya konfigurasi pemenang sendiri — itulah sebabnya form Prediksi meminta 6 bulan untuk PLTB dan 3 bulan untuk sisanya.

PLTS dan PLTS Atap memakai **file model yang sama**, dibedakan lewat category embedding. Jadi PLTS Atap tetap punya representasi di tabel evaluasi meskipun tidak menjalani fine-tuning terpisah.

### Hasil evaluasi (data uji 2025, RMSE dalam GWh)

| Jenis PLT | LSTM | ARIMA(1,1,1) | Naive lag-1 | Seasonal × Kapasitas | Terbaik |
|---|---|---|---|---|---|
| PLTA | **77,06** | 117,66 | 90,98 | 98,28 | LSTM |
| PLTB | **5,07** | 11,87 | 10,42 | 9,05 | LSTM |
| PLTM | **5,83** | 10,31 | 7,50 | 8,59 | LSTM |
| PLTS | 0,0958 | 0,5480 | 0,1363 | **0,0801** | Seasonal |
| PLTS Atap | 0,1138 | 0,5668 | 0,1509 | **0,0960** | Seasonal |

**LSTM unggul di 3 dari 5 jenis PLT**, dengan akurasi (100 − MAPE) 89–93% di kelimanya.

> **Catatan integritas.** PLTS & PLTS Atap kalah tipis dari seasonal naive, dan itu dilaporkan apa adanya. Kombinasi model **tidak ditukar** ke varian yang skor data ujinya kebetulan lebih bagus — memilih berdasarkan data uji adalah kebocoran data (*test-set leakage*) yang membuat angka evaluasi tidak lagi sah. Sebelum ensembling LSTM sempat unggul 4 dari 5, tapi selektor walk-forward memilih varian C untuk PLTS Atap dan itu dipertahankan. Uraian lengkap: `audit/results/framing_findings.md` bagian *"Catatan jujur"*.

### Keterbatasan yang wajib diungkap

- **Forecast bukan pengukuran capaian RUED.** Target RUED diukur dalam **persen bauran energi daerah**, sedangkan keluaran model adalah **GWh produksi kelistrikan**. Keduanya tidak bisa dibandingkan langsung tanpa data total energi daerah (listrik + non-listrik) sebagai penyebut. Forecast berperan sebagai *informasi pendukung* evaluasi RUED.
- **Hanya sektor kelistrikan.** Biofuel, biogas, dan energi termal tidak diprediksi karena dokumentasi historisnya belum konsisten.
- **Forecast 2026–2028 memakai asumsi**: Cuaca = normal klimatologis per bulan kalender (rata-rata 2023–2025), bukan prakiraan operasional — horizon 3 tahun di luar jangkauan prakiraan BMKG. Kapasitas diasumsikan **tetap** di level Desember 2025, tidak memperhitungkan rencana penambahan kapasitas di RUED/RUPTL.
- **Akumulasi galat.** Forecast jangka panjang bersifat otoregresif — prediksi satu bulan menjadi input bulan berikutnya, sehingga kesalahan menumpuk sepanjang periode.
- **Model butuh cuaca bulan yang ditebak.** Seluruh kombinasi pemenang adalah model *known-future covariate*. Untuk bulan yang sudah lewat, sistem menarik observasi riil dari NASA POWER; untuk bulan yang belum lewat, dipakai normal klimatologis — dan asal angkanya selalu ditandai di antarmuka.
- **NASA POWER punya jeda terbit.** Data bulanan biasanya tertinggal beberapa bulan dari tanggal hari ini. Kalau bulan yang diminta belum terbit, sistem otomatis jatuh ke normal klimatologis dan menyatakannya, bukan diam-diam.
- **Menambah data tidak melatih ulang model.** Pelatihan ulang dijalankan terpisah lewat `audit/analysis/build_production_model.py`.

---

## Troubleshooting

**`npm install` gagal / error ENOENT**
Pastikan Anda berada di dalam folder `siprebar/` (yang berisi `package.json`), bukan di folder induknya.

```bash
# Cek lokasi saat ini
pwd   # Linux/Mac
cd    # Windows

# Pastikan ada package.json
ls package.json
```

**Port sudah dipakai**
Jalankan dengan port kustom:
```bash
npm run dev -- --port 3000
```

**Halaman kosong / error di browser**
Buka DevTools (F12) → tab Console, perhatikan pesan error. Pastikan `npm install` sudah dijalankan sebelum `npm run dev`.

**Halaman Data EBT / Prediksi menampilkan "Tidak dapat terhubung ke backend"**
Backend belum berjalan, atau berjalan di port selain 8000. Cek `http://localhost:8000/api/health` bisa diakses langsung dari browser; kalau tidak, jalankan backend (lihat [Menjalankan Backend](#menjalankan-backend)).

**`/api/health` menunjukkan `"status": "degraded"` atau `"artefak_model_lengkap": false`**
Artinya model (`.keras`) atau scaler (`.pkl`) untuk salah satu jenis PLT tidak ditemukan di mesin ini — periksa `artefak_per_plt` di response untuk tahu PLT mana yang bermasalah. File ini besar dan tidak ikut di-commit ke git (lihat catatan di [Prasyarat](#prasyarat)); bangun ulang dengan `python audit/analysis/build_production_model.py` (butuh beberapa menit). Endpoint CRUD (`/api/data`) tetap berfungsi normal walau artefak model belum ada — hanya `/api/predict` yang akan menolak dengan `503`.

**Migrasi (`python migrate_csv.py`) gagal dengan pesan "tabel sudah berisi N baris"**
Migrasi ini dirancang sekali jalan supaya tidak menggandakan data. Kalau memang ingin mengosongkan dan mengisi ulang dari CSV sumber, pakai `python migrate_csv.py --reset` (ini akan menghapus juga data yang sudah diinput/diimpor pengguna).

---

## Lisensi

Dikembangkan untuk keperluan penelitian akademik. Hak cipta © 2026 — UIN Alauddin Makassar.
