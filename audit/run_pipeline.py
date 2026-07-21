"""
Runner non-interaktif untuk audit/source/bs_tf_lstm_fix.py.

bs_tf_lstm_fix.py adalah ekspor Colab (memakai display() dan plt.show()),
sehingga tidak bisa dijalankan langsung dengan `python bs_tf_lstm_fix.py`.
Script ini TIDAK mengubah bs_tf_lstm_fix.py — hanya menyiapkan lingkungan
(shim display(), backend matplotlib non-GUI, working directory berisi CSV
input) lalu meng-eksekusi isinya apa adanya.

Semua path relatif di dalam bs_tf_lstm_fix.py (mis. "model_final",
"EBT_LSTM_Streamlit") akan dibuat di working directory ini
(audit/results/pipeline_run/), bukan di audit/source/, supaya file input
asli tetap bersih dan tidak tertimpa output.
"""
import os
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

import matplotlib
matplotlib.use("Agg")  # non-GUI backend -> plt.show() jadi no-op, tidak blocking

# Shim HANYA google.colab (bukan `google` itu sendiri, yang merupakan namespace
# package nyata dipakai TensorFlow untuk google.protobuf -- jangan ditimpa).
# Script asli memanggil `from google.colab import files` lalu
# `files.download(path_zip)` di akhir (KEGIATAN export EBT_LSTM_Streamlit),
# yang hanya berfungsi di lingkungan Colab (memicu download browser). Di luar
# Colab kita sudah punya file zip-nya langsung di disk, jadi download() dibuat
# no-op saja -- tidak mengubah bs_tf_lstm_fix.py itu sendiri. Karena sudah
# terdaftar di sys.modules, Python akan memakainya langsung tanpa mengganggu
# import google.protobuf milik TensorFlow (yang di-resolve terpisah, lazily,
# saat baris `import tensorflow as tf` di source script dieksekusi).
import types
_fake_google_colab = types.ModuleType("google.colab")
_fake_google_colab_files = types.ModuleType("google.colab.files")
_fake_google_colab_files.download = lambda path: print(f"[shim] files.download('{path}') dilewati (bukan lingkungan Colab)")
_fake_google_colab.files = _fake_google_colab_files
sys.modules["google.colab"] = _fake_google_colab
sys.modules["google.colab.files"] = _fake_google_colab_files

AUDIT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(AUDIT_DIR, "source")
RUN_DIR = os.path.join(AUDIT_DIR, "results", "pipeline_run")
SOURCE_SCRIPT = os.path.join(SOURCE_DIR, "bs_tf_lstm_fix.py")

REQUIRED_INPUT_CSVS = [
    "DATA_PHASE_3_REGIONAL_MODIFIED.csv",
    "DATA_PHASE_2_NASIONAL_FINAL.csv",
]


def prepare_run_dir():
    os.makedirs(RUN_DIR, exist_ok=True)
    for name in REQUIRED_INPUT_CSVS:
        src = os.path.join(SOURCE_DIR, name)
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
        "display": print,  # shim untuk IPython.display.display()
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
