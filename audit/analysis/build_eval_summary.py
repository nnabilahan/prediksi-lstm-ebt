"""
Menyusun audit/results/eval_summary.csv dari file evaluasi per tahap yang
ditulis pipeline (EBT_LSTM_Streamlit/evaluation/evaluasi_*.csv).

Sebelumnya eval_summary.csv dirakit manual, jadi tidak reproducible dan mudah
tertinggal saat pipeline dijalankan ulang. Script ini menggantikan langkah
manual itu -- jalankan setelah audit/run_pipeline_fixed.py selesai.

Folder run bisa dioverride lewat env var RUN_DIR_NAME (default: pipeline_run_v3),
sama seperti audit/run_pipeline_fixed.py.

Catatan metrik: seluruh angka RMSE/MAE/MAPE di sini adalah metrik pada DATA UJI
2025 (data yang tidak pernah dilihat model pada tahap-tahap tersebut). Pemilihan
model terbaik TIDAK memakai angka ini -- itu memakai RMSE validasi
(perbandingan_model_VALIDASI.csv), lihat audit/results/audit_findings.md.
"""
import os

import pandas as pd

AUDIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_DIR_NAME = os.environ.get("RUN_DIR_NAME", "pipeline_run_v3")
EVAL_DIR = os.path.join(
    AUDIT_DIR, "results", RUN_DIR_NAME, "EBT_LSTM_Streamlit", "evaluation"
)
OUT_PATH = os.path.join(AUDIT_DIR, "results", "eval_summary.csv")

# (nama Stage di output, nama file evaluasi, metode default kalau file itu
# tidak punya kolom "Metode")
STAGES = [
    ("Baseline", "evaluasi_baseline.csv", "Direct Training (Baseline)"),
    ("FineTuning", "evaluasi_finetuning.csv", None),
    ("Iterasi1", "evaluasi_iterasi1.csv", None),
    ("Iterasi2", "evaluasi_iterasi2.csv", None),
    ("Iterasi3", "evaluasi_iterasi3.csv", None),
]


def main():
    frames = []
    for stage, filename, metode_default in STAGES:
        path = os.path.join(EVAL_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} tidak ditemukan. Jalankan audit/run_pipeline_fixed.py "
                f"lebih dulu (atau set RUN_DIR_NAME ke folder run yang benar)."
            )
        df = pd.read_csv(path)
        df["Stage"] = stage
        if "Metode" not in df.columns:
            df["Metode"] = metode_default
        frames.append(df.rename(columns={"Jenis_PLT": "PLT"}))

    summary = pd.concat(frames, ignore_index=True)
    summary = summary[["Stage", "PLT", "Metode", "RMSE", "MAE", "MAPE"]]

    # Urutkan per PLT lalu per tahap (mengikuti urutan STAGES), supaya tabelnya
    # enak dibaca berpasangan saat membandingkan antar tahap untuk satu PLT.
    urutan_stage = {s[0]: i for i, s in enumerate(STAGES)}
    summary = (
        summary.assign(_urut=summary["Stage"].map(urutan_stage))
        .sort_values(["PLT", "_urut"])
        .drop(columns="_urut")
        .reset_index(drop=True)
    )

    summary.to_csv(OUT_PATH, index=False)
    print(f"Ditulis: {OUT_PATH} ({len(summary)} baris, sumber: {EVAL_DIR})")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
