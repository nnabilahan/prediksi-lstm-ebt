# SIPREBAR
**Sistem Prediksi Energi Baru Terbarukan**

Aplikasi web untuk memantau produksi EBT sektor kelistrikan, menampilkan hasil prediksi model LSTM, dan mendukung evaluasi pencapaian Rencana Umum Energi Daerah (RUED) Provinsi Sulawesi Selatan.

> Dikembangkan sebagai bagian dari penelitian skripsi:
> *"Prediksi Konsumsi Energi Baru Terbarukan Sektor Kelistrikan Menggunakan Deep Learning: Implementasi Long Short-Term Memory pada Data Dinas ESDM Provinsi Sulawesi Selatan"*
> UIN Alauddin Makassar — Teknik Informatika, 2026

---

## Prasyarat

Pastikan perangkat sudah terinstal:

| Perangkat | Versi minimum | Cek versi |
|-----------|---------------|-----------|
| Node.js   | 18.x          | `node -v` |
| npm       | 9.x           | `npm -v`  |

---

## Cara Menjalankan (Development)

### 1. Clone atau salin folder proyek

```bash
# Jika menggunakan Git
git clone <url-repositori>
cd siprebar

# Atau langsung masuk ke folder proyek
cd siprebar
```

### 2. Install dependensi

```bash
npm install
```

Perintah ini akan mengunduh semua package yang dibutuhkan ke folder `node_modules/`.

### 3. Jalankan server development

```bash
npm run dev
```

Setelah berhasil, terminal akan menampilkan:

```
VITE v6.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### 4. Buka di browser

Buka **http://localhost:5173** di browser (Chrome / Edge / Firefox).

> Jika port 5173 sudah dipakai, Vite otomatis memilih port berikutnya (5174, 5175, dst). Perhatikan output terminal untuk URL yang benar.

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
├── src/
│   ├── lib/
│   │   ├── tokens.js        # Design tokens (semua warna)
│   │   ├── data.js          # Data dummy / placeholder API
│   │   └── utils.js         # Helper fmt() dan buildMonthly()
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TopNav.jsx   # Navigasi atas (2 lapisan)
│   │   │   └── Footer.jsx   # Footer sitasi
│   │   ├── ui/              # Komponen UI (Panel, Stat, Note, Gauge, dll.)
│   │   └── charts/          # Komponen chart (MonthlyChart, DonutChart, dll.)
│   ├── pages/               # 6 halaman utama
│   │   ├── Dashboard.jsx
│   │   ├── Prediksi.jsx
│   │   ├── GapAnalysis.jsx
│   │   ├── DataEBT.jsx
│   │   ├── Laporan.jsx
│   │   └── Pengaturan.jsx
│   ├── App.jsx
│   └── main.jsx
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

---

## Mengganti Data dengan Data Nyata

Saat ini aplikasi menggunakan **data dummy** di `src/lib/data.js`. Saat model LSTM dan backend API siap, ganti bagian berikut:

| File | Konstanta | Ganti dengan |
|------|-----------|-------------|
| `src/lib/data.js` | `ANNUAL_FORECAST` | Fetch dari `GET /api/forecast/annual` |
| `src/lib/data.js` | `MODEL_RMSE` | Fetch dari `GET /api/model/metrics` |
| `src/lib/data.js` | `SAMPLE_MONTHLY_ROWS` | Fetch dari `GET /api/data/historical` |
| `src/lib/utils.js` | `buildMonthly()` | Fetch dari `GET /api/forecast/monthly?plant=X` |

Arsitektur komponen tidak perlu diubah — cukup ganti sumber datanya.

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

---

## Lisensi

Dikembangkan untuk keperluan penelitian akademik. Hak cipta © 2026 — UIN Alauddin Makassar.
