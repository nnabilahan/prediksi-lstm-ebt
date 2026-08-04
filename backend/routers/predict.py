"""
Endpoint inferensi LSTM: POST /api/predict.

Model & scaler dimuat sekali saat startup server (lihat ml.load_artefacts(),
dipanggil dari lifespan di main.py) -- endpoint ini hanya memakainya dari
memori, tidak pernah membaca ulang file .keras/.pkl per request dan tidak
pernah melatih ulang apa pun.

Empat lapis validasi, berurutan, BERHENTI di lapis pertama yang gagal:
  1. Whitelist jenis PLT
  2. Kelengkapan fitur (Produksi/Kapasitas/Cuaca tidak boleh kosong)
  3. Panjang data >= window_size PLT tersebut
  4. Rentang nilai vs data training -- TIDAK menolak, hanya mengisi field
     `peringatan` di response.
"""
import ml
from fastapi import APIRouter, HTTPException
from config import JENIS_PLT_VALID
from schemas import PredictRequest, PredictResponse

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("", response_model=PredictResponse)
def predict(payload: PredictRequest):
    if not ml.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model belum termuat di server. Cek /api/health untuk detail artefak yang hilang.",
        )

    jenis_plt = payload.jenis_plt

    # Lapis 1: whitelist.
    if jenis_plt not in JENIS_PLT_VALID:
        raise HTTPException(
            status_code=400,
            detail="Jenis PLT tidak dikenali, model belum tersedia untuk kategori ini.",
        )

    # Lapis 2: kelengkapan fitur -- cek SEMUA baris yang dikirim (sebelum
    # dipangkas ke window_size), supaya pesan error menunjuk baris asli
    # sesuai urutan yang dikirim pengguna.
    baris_kurang = [
        i for i, titik in enumerate(payload.data, start=1)
        if titik.produksi is None or titik.kapasitas is None or titik.cuaca is None
    ]
    if baris_kurang:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ada baris dengan Produksi/Kapasitas/Cuaca kosong: "
                f"baris ke-{baris_kurang} (dari data yang dikirim). "
                "Lengkapi nilainya -- endpoint ini tidak mengisi otomatis."
            ),
        )

    # Lapis 3: panjang data.
    window_size = ml.get_window_size(jenis_plt)
    if len(payload.data) < window_size:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Data tidak cukup panjang untuk {jenis_plt}: dibutuhkan "
                f"{window_size} bulan berurutan, hanya diberikan {len(payload.data)}."
            ),
        )

    # Urutkan kronologis, ambil window_size baris TERAKHIR sebagai input
    # model (kalau pengguna mengirim lebih dari window_size baris).
    titik_terurut = sorted(payload.data, key=lambda t: t.tanggal)
    jendela = titik_terurut[-window_size:]
    baris = [
        {"produksi": t.produksi, "kapasitas": t.kapasitas, "cuaca": t.cuaca, "tanggal": t.tanggal}
        for t in jendela
    ]

    # Lapis 4: rentang nilai -- peringatan saja, tidak menolak.
    daftar_peringatan = ml.cek_rentang(jenis_plt, baris, payload.cuaca_target)
    peringatan = "; ".join(daftar_peringatan) if daftar_peringatan else None

    prediksi = ml.predict(
        jenis_plt, baris, payload.cuaca_target, payload.kapasitas_target
    )

    return PredictResponse(
        jenis_plt=jenis_plt,
        prediksi=round(prediksi, 3),
        mape_model=ml.get_mape(jenis_plt),
        peringatan=peringatan,
    )
