# Panduan Running Project SIPREBAR dengan LocalTunnel

Dokumen ini berisi langkah lengkap untuk menjalankan aplikasi dari awal sampai akhir, termasuk:
- frontend Vite
- backend FastAPI
- localtunnel untuk mengakses URL publik
- konfigurasi `.env` agar semua URL konsisten

---

## 1. Persiapan awal

Pastikan di komputer Anda sudah tersedia:
- Node.js dan npm
- Python 3.10+
- Git (opsional)
- localtunnel (`npx localtunnel` atau `lt`)

Buka terminal di folder project:

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
```

Jika belum install dependency frontend:

```bash
npm install
```

Jika belum install dependency backend:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

Jika Anda menggunakan PowerShell:

```powershell
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

---

## 2. Setup file .env

Pastikan file `.env` ada di root project dan berisi konfigurasi seperti ini:

```env
VITE_API_BASE="https://large-buttons-count.loca.lt"
VITE_ALLOWED_HOSTS="localhost,127.0.0.1,.loca.lt,.localtunnel.me,large-buttons-count.loca.lt"
BACKEND_ALLOWED_ORIGINS_REGEX="^https?://(localhost|127\\.0\\.0\\.1|.*\\.loca\\.lt|.*\\.localtunnel\\.me|large-buttons-count\\.loca\\.lt)(?::\\d+)?$"
```

Catatan:
- `VITE_API_BASE` adalah URL publik backend yang akan dipakai frontend.
- Gunakan domain tetap agar URL tidak berubah setiap kali restart tunnel.
- `VITE_ALLOWED_HOSTS` adalah host yang diizinkan Vite saat menjalankan dev server.
- `BACKEND_ALLOWED_ORIGINS_REGEX` adalah regex CORS yang diizinkan oleh FastAPI.
- Nilai `0.0.0.0` tidak boleh dibuka di browser dan tidak boleh dipakai di `VITE_API_BASE` atau localtunnel URL.

> `0.0.0.0` artinya "bind ke semua interface" pada mesin lokal, bukan URL yang bisa diakses oleh browser atau internet. Browser harus membuka `localhost` atau URL domain tunnel, bukan `0.0.0.0`.

Jika URL tunnel tidak cocok, cukup ganti value di `.env` lalu restart server.

---

## 3. Jalankan backend

Buka terminal baru untuk backend.

### Terminal 1: activate virtual environment dan start backend

Windows PowerShell:

```powershell
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Windows Command Prompt:

```cmd
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
.venv\Scripts\activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Pastikan backend dapat berjalan di:

```text
http://localhost:8000
http://localhost:8000/docs
```

Jika ingin mengecek health:

```bash
curl http://localhost:8000/api/health
```

---

## 4. Jalankan localtunnel untuk backend dengan domain tetap

Buka terminal baru untuk tunnel backend.

### Terminal 2: tunnel backend ke URL public dengan domain statis

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npx localtunnel --port 8000 --domain large-buttons-count.loca.lt
```

atau:

```bash
lt --port 8000 --domain large-buttons-count.loca.lt
```

Dengan `--domain`, Anda mendapatkan URL yang tetap dan konsisten. Tidak perlu mengganti `.env` setiap kali menyalakan tunnel.

Setelah berhasil, pastikan nilai ini ada di `.env`:

```env
VITE_API_BASE="https://large-buttons-count.loca.lt"
```

> Gunakan domain yang benar-benar unik dan belum dipakai orang lain.
> Jangan gunakan `0.0.0.0` karena itu bukan URL publik yang valid untuk browser.

---

## 5. Jalankan frontend

Buka terminal baru untuk frontend.

### Terminal 3: start Vite dev server

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npm run dev -- --host 0.0.0.0
```

Biasanya Vite akan berjalan di:

```text
http://localhost:5173
```

Jika port 5173 terpakai, Vite akan otomatis pindah ke port lain, misalnya 5174.

---

## 6. Jalankan localtunnel untuk frontend dengan domain tetap

Buka terminal baru lagi untuk tunnel frontend.

### Terminal 4: tunnel frontend ke URL public

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npx localtunnel --port 5173 --local-host localhost --domain large-buttons-count-frontend.loca.lt
```

Jika Vite pindah ke port lain, sesuaikan dengan port yang aktif. Contoh:

```bash
npx localtunnel --port 5174 --local-host localhost --domain large-buttons-count-frontend.loca.lt
```

Setelah berhasil, URL yang akan dibuka di browser adalah:

```text
https://large-buttons-count-frontend.loca.lt
```

Kalau Anda hanya perlu akses frontend dari browser publik, cukup gunakan URL frontend localtunnel ini.

---

## 6a. Versi yang lebih stabil untuk publik: build preview + tunnel

Untuk akses public yang lebih stabil daripada `npm run dev`, gunakan build produksi dan `vite preview`.

### Terminal frontend (preview build)

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npm run build
npx vite preview --host 0.0.0.0 --port 4173
```

### Terminal tunnel preview

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npx localtunnel --port 4173 --local-host localhost --domain siprebar-preview.loca.lt
```

Selain lebih stabil, cara ini minim error WebSocket dan asset 502 karena Vite HMR tidak dipakai untuk akses publik. Gunakan URL berikut untuk browser publik:

```text
https://siprebar-preview.loca.lt
```

---

## 7. Pastikan frontend bisa terhubung ke backend

Frontend saat ini menggunakan nilai dari:

```js
import.meta.env.VITE_API_BASE
```

Maka semua request API akan menuju ke URL backend yang ada di `.env`.

Contoh:

```env
VITE_API_BASE="https://your-subdomain.loca.lt"
```

Jadi aplikasi akan fetch ke:

```text
https://your-subdomain.loca.lt/api/health
```

dan bukan ke `localhost:8000` secara hardcode.

---

## 8. Alur run lengkap (versi ringkas)

Berikut urutan paling umum yang digunakan:

### Terminal 1
```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2
```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npx localtunnel --port 8000
```

### Terminal 3
```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npm run dev -- --host 0.0.0.0
```

### Terminal 4
```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
npx localtunnel --port 5173
```

Setelah itu:
- pastikan `.env` berisi URL backend tunnel permanen sebagai `VITE_API_BASE`
- buka URL frontend tunnel di browser
- backend tetap jalan di `localhost:8000`
- frontend tetap jalan di `localhost:5173`
- jangan buka `http://0.0.0.0:8000` atau `http://0.0.0.0:5173` di browser, karena itu bukan URL valid untuk browser/public access

---

## 9. Troubleshooting

### Error CORS
Jika browser menampilkan error CORS, cek:
- backend sedang berjalan
- `.env` `VITE_API_BASE` sudah benar
- `BACKEND_ALLOWED_ORIGINS_REGEX` mencakup URL localtunnel
- URL yang dibuka di browser bukan `0.0.0.0`, melainkan domain tunnel atau localhost

### Blank putih saat membuka URL public
Blank putih biasanya terjadi karena:
- frontend mengarah ke backend yang salah (`localhost`/`0.0.0.0` yang tidak valid untuk public)
- CORS backend belum mengizinkan domain tunnel
- URL backend di `.env` tidak sesuai dengan domain hasil `--domain`
- Vite dev server tidak benar-benar hidup, atau tunnel diarahkan ke port yang salah

Pastikan semua komponen berjalan dengan domain tetap yang sama di `.env`, backend, dan tunnel.

### Error 503 saat klik `Jalankan prediksi`
Error 503 pada fitur prediksi biasanya berarti backend masih hidup, tetapi model LSTM belum termuat yang membuat endpoint `/api/predict` menolak request.

Penyebab umum:
- TensorFlow belum terinstal di environment backend
- model `.keras` belum dibuat
- `uvicorn` belum dimulai ulang setelah dependency baru terpasang

Cek terlebih dahulu di terminal backend:

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
.
\.venv\Scripts\Activate.ps1
cd backend
python -c "import tensorflow; print(tensorflow.__version__)"
```

Jika error `ModuleNotFoundError: No module named 'tensorflow'`, install dependency backend:

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt"
.
\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Lalu restart backend:

```bash
cd "c:/belajarku/Semester 8/prediksi-lstm-ebt/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> Jika backend sudah terinstall TensorFlow tetapi tetap 503, cek `/api/health` terlebih dahulu. Endpoint prediksi hanya akan berjalan kalau model benar-benar termuat saat startup.

### URL localtunnel berubah
LocalTunnel biasanya menghasilkan subdomain baru setiap kali server dimulai ulang. Jika URL berubah:
1. update `.env`
2. restart frontend
3. refresh browser

### Frontend tidak terhubung backend
Coba cek langsung:

```bash
curl https://your-subdomain.loca.lt/api/health
```

Jika berhasil, backend sudah bisa diakses publik.

---

## 10. Kesimpulan

Cara paling aman adalah:
- Backend jalan di localhost:8000
- Frontend jalan di localhost:5173
- URL publik dibuat via localtunnel
- Semua URL dikelola dari `.env`

Dengan cara ini, setiap kali localtunnel memberikan subdomain baru, Anda tinggal update satu file saja, yaitu `.env`.

---

Jika Anda mau, saya juga bisa buatkan versi yang lebih ringkas dalam bentuk:
1. `run_localtunnel.md` (versi ini), dan
2. `README` ringkas untuk tim yang hanya butuh langkah cepat.
