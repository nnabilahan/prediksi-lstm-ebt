"""
Runner non-interaktif untuk audit/source_fixed/bs_tf_lstm_fix_fixed.py
(versi yang sudah diperbaiki dari temuan data leakage -- lihat komentar
"[FIX LEAKAGE #N]" di file itu dan audit/results/audit_findings.md).

Sama seperti audit/run_pipeline.py, hanya beda source & output directory
supaya hasil run "before" (audit/results/pipeline_run/) dan "after" tidak
saling menimpa sebelum dibandingkan.
"""
import os
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

import matplotlib
matplotlib.use("Agg")

import types
_fake_google_colab = types.ModuleType("google.colab")
_fake_google_colab_files = types.ModuleType("google.colab.files")
_fake_google_colab_files.download = lambda path: print(f"[shim] files.download('{path}') dilewati (bukan lingkungan Colab)")
_fake_google_colab.files = _fake_google_colab_files
sys.modules["google.colab"] = _fake_google_colab
sys.modules["google.colab.files"] = _fake_google_colab_files

AUDIT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(AUDIT_DIR, "source_fixed")
# Nama folder output bisa dioverride lewat env var RUN_DIR_NAME supaya hasil
# run dataset lama (pipeline_run_fixed/) tidak tertimpa oleh run dataset baru.
RUN_DIR = os.path.join(
    AUDIT_DIR, "results", os.environ.get("RUN_DIR_NAME", "pipeline_run_v3")
)
SOURCE_SCRIPT = os.path.join(SOURCE_DIR, "bs_tf_lstm_fix_fixed.py")

REQUIRED_INPUT_CSVS = [
    "DATA_REGIONAL_DISAGREGASI_V3.csv",
    "DATA_NASIONAL_DISAGREGASI_V2.csv",
]


def prepare_run_dir():
    os.makedirs(RUN_DIR, exist_ok=True)
    source_csv_dir = os.path.join(AUDIT_DIR, "source")
    for name in REQUIRED_INPUT_CSVS:
        src = os.path.join(source_csv_dir, name)
        dst = os.path.join(RUN_DIR, name)
        if not os.path.exists(dst):
            with open(src, "rb") as f_in, open(dst, "wb") as f_out:
                f_out.write(f_in.read())


def main():
    prepare_run_dir()
    os.chdir(RUN_DIR)

    with open(SOURCE_SCRIPT, "r", encoding="utf-8") as f:
        source_code = f.read()

    exec_globals = {
        "__name__": "__main__",
        "__file__": SOURCE_SCRIPT,
        "display": print,
    }

    print(f"=== Menjalankan {SOURCE_SCRIPT} ===")
    print(f"=== Working directory: {RUN_DIR} ===\n")

    try:
        exec(compile(source_code, SOURCE_SCRIPT, "exec"), exec_globals)
        print("\n=== SELESAI: pipeline berjalan sampai akhir tanpa exception ===")
    except Exception as exc:
        sys.stdout.flush()
        print("\n=== BERHENTI KARENA EXCEPTION ===", flush=True)
        try:
            tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        except Exception as fmt_exc:
            tb_text = f"(gagal memformat traceback: {fmt_exc!r})"
        print(tb_text, flush=True)
        print(f"Exception type: {type(exc).__name__}", flush=True)
        print(f"Exception str (repr): {str(exc)!r}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
