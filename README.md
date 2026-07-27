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

Python dibutuhkan untuk menjalankan **backend** (lihat [Menjalankan Backend](#menjalankan-backend)) — dashboard, gap analysis RUED, dan perbandingan ARIMA/Naive tetap statis dan tidak butuh backend untuk ditampilkan; backend hanya dipakai untuk mengelola data historis (CRUD) dan menjalankan inferensi LSTM langsung dari halaman **Data EBT** dan **Prediksi**.

Backend juga butuh artefak model & scaler hasil pipeline training (`audit/results/pipeline_run/EBT_LSTM_Streamlit/models/*.keras` dan `.../scalers/*.pkl`) sudah ada di mesin lokal — file ini besar dan tidak ikut di-commit ke git (lihat `.gitignore`), jadi harus tersedia dari hasil run pipeline sebelumnya.

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

Lihat [Menjalankan Backend](#menjalankan-backend) di bawah untuk langkah lengkap (install dependensi, migrasi data awal, start server). Backend harus berjalan di **http://localhost:8000** — CORS di backend sudah dikonfigurasi untuk menerima permintaan dari `localhost:5173`.

Tanpa backend berjalan, halaman **Data EBT** dan panel **"Inferensi langsung"** di halaman **Prediksi** akan menampilkan pesan error yang jelas ("Tidak dapat terhubung ke backend...") alih-alih data — sisa aplikasi (Dashboard, Gap Analysis RUED, forecast statis 2026–2028) tetap berfungsi normal karena datanya statis dari `src/lib/data.js`.

---

## Menjalankan Backend

Backend melayani dua hal: **CRUD data historis EBT** (tambah/ubah/hapus/impor/ekspor, dipakai halaman Data EBT) dan **inferensi model LSTM langsung** (dipakai panel "Inferensi langsung" di halaman Prediksi). Backend **tidak pernah melatih ulang model** — hanya memuat model `.keras` dan scaler `.pkl` yang sudah ada hasil pipeline training.

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

Mengisi database SQLite lokal (`backend/siprebar.db`, dibuat otomatis, tidak ikut di-commit) dengan 252 baris dari `audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv` — data hasil **rekonstruksi/estimasi** (lihat `audit/source/README.md`), ditandai `sumber = "rekonstruksi"` di setiap baris. Skrip menolak jalan ulang kalau database sudah terisi (supaya tidak menggandakan data); pakai `python migrate_csv.py --reset` kalau sengaja ingin mengosongkan dan mengisi ulang.

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
│   ├── routers/
│   │   ├── data.py           # GET/POST/PUT/DELETE /api/data, export, import
│   │   └── predict.py        # POST /api/predict (4 lapis validasi)
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
│   ├── pages/               # 6 halaman utama
│   │   ├── Dashboard.jsx    # Statis (data.js)
│   │   ├── Prediksi.jsx     # Forecast statis (data.js) + panel "Inferensi langsung" (backend)
│   │   ├── GapAnalysis.jsx  # Statis (data.js)
│   │   ├── DataEBT.jsx      # Live dari backend (GET/POST/PUT/DELETE/import/export /api/data)
│   │   ├── Laporan.jsx
│   │   └── Pengaturan.jsx
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
| Dashboard — tren & ringkasan | `data.js` | Tidak |
| Gap Analysis RUED | `data.js` | Tidak |
| Prediksi — grafik & tabel forecast 2026–2028 | `data.js` | Tidak |
| Prediksi — perbandingan LSTM vs ARIMA/Naive | `data.js` | Tidak |
| Prediksi — panel **"Inferensi langsung"** | `POST /api/predict` | **Ya** |
| Data EBT — tabel, tambah/ubah/hapus/impor/ekspor | `GET/POST/PUT/DELETE /api/data`, `/export`, `/import` | **Ya** |

`data.js` dibuat ulang oleh `audit/analysis/export_dashboard_data.py` — jangan diedit manual, dan jangan diganti jadi fetch ke backend untuk bagian-bagian di atas yang statis.

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

**Halaman Data EBT / panel "Inferensi langsung" menampilkan "Tidak dapat terhubung ke backend"**
Backend belum berjalan, atau berjalan di port selain 8000. Cek `http://localhost:8000/api/health` bisa diakses langsung dari browser; kalau tidak, jalankan backend (lihat [Menjalankan Backend](#menjalankan-backend)).

**`/api/health` menunjukkan `"status": "degraded"` atau `"artefak_model_lengkap": false`**
Artinya model (`.keras`) atau scaler (`.pkl`) untuk salah satu jenis PLT tidak ditemukan di mesin ini — periksa `artefak_per_plt` di response untuk tahu PLT mana yang bermasalah. File ini besar dan tidak ikut di-commit ke git (lihat catatan di [Prasyarat](#prasyarat)); salin folder `audit/results/pipeline_run/EBT_LSTM_Streamlit/models/` dan `.../scalers/` dari hasil run pipeline sebelumnya. Endpoint CRUD (`/api/data`) tetap berfungsi normal walau artefak model belum ada — hanya `/api/predict` yang akan menolak dengan `503`.

**Migrasi (`python migrate_csv.py`) gagal dengan pesan "tabel sudah berisi N baris"**
Migrasi ini dirancang sekali jalan supaya tidak menggandakan data. Kalau memang ingin mengosongkan dan mengisi ulang dari CSV sumber, pakai `python migrate_csv.py --reset` (ini akan menghapus juga data yang sudah diinput/diimpor pengguna).

---

## Lisensi

Dikembangkan untuk keperluan penelitian akademik. Hak cipta © 2026 — UIN Alauddin Makassar.
