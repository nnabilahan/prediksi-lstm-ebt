"""
Konverter generik: file .py hasil ekspor Google Colab -> .ipynb.

Format ekspor Colab menandai cell dengan baris string literal berdiri
sendiri di awal file/section (judul diapit tiga tanda kutip ganda) menjadi
1 markdown cell (isinya = teks di dalam string itu), dan kode Python di
antara dua marker tersebut menjadi 1 code cell.

Dipakai untuk membuat audit/source_fixed/bs_tf_lstm_fix_fixed.ipynb dari
audit/source_fixed/bs_tf_lstm_fix_fixed.py, supaya bisa dibuka lagi di
Google Colab. Tidak bergantung pada library `nbformat` -- notebook v4
JSON dibangun manual (strukturnya sederhana).

Usage: python py_to_ipynb.py <input.py> <output.ipynb>
"""
import ast
import json
import re
import sys

# Banner komentar 3-baris yang dipakai di file ini sebagai penanda sub-section
# (bukan markdown cell asli Colab, tapi cukup konsisten untuk dipakai sebagai
# titik pemisah cell tambahan supaya notebook lebih mudah dibaca daripada
# 1 code cell raksasa).
BANNER_RE = re.compile(r"(?m)^# ={5,}\n(?:# .*\n)+# ={5,}\n")


def split_cells(source_text):
    """Pecah source Colab-exported jadi list (cell_type, content)."""
    tree = ast.parse(source_text)
    lines = source_text.splitlines(keepends=True)

    # Ambil rentang baris (1-indexed, inclusive) tiap top-level statement,
    # supaya markdown-marker (bare string expr) dan kode di sekitarnya
    # bisa dipisah persis sesuai batas baris aslinya.
    boundaries = []
    for node in tree.body:
        start = node.lineno
        end = getattr(node, "end_lineno", node.lineno)
        is_markdown = (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        boundaries.append((start, end, is_markdown, node.value.value if is_markdown else None))

    cells = []
    code_buffer_start = 1

    def flush_code(end_line_exclusive):
        nonlocal code_buffer_start
        if code_buffer_start < end_line_exclusive:
            chunk = "".join(lines[code_buffer_start - 1: end_line_exclusive - 1])
            if chunk.strip():
                cells.append(("code", chunk.rstrip("\n")))
        code_buffer_start = end_line_exclusive

    for start, end, is_markdown, text in boundaries:
        if is_markdown:
            flush_code(start)
            cells.append(("markdown", text.strip()))
            code_buffer_start = end + 1
        # else: leave in the code buffer, flushed at the next markdown
        # marker or at the end of file.

    flush_code(len(lines) + 1)
    return split_code_cells_on_banners(cells)


def split_code_cells_on_banners(cells):
    """Pecah lagi cell code yang panjang di setiap banner komentar 3-baris
    (# ====.../# Judul/# ====...), supaya notebook tidak berujung 1 cell
    raksasa untuk section yang tidak memakai markdown-marker Colab asli."""
    result = []
    for cell_type, content in cells:
        if cell_type != "code":
            result.append((cell_type, content))
            continue

        split_points = [m.start() for m in BANNER_RE.finditer(content + "\n")]
        if not split_points or split_points[0] != 0:
            split_points = [0] + split_points
        split_points.append(len(content) + 1)

        for i in range(len(split_points) - 1):
            chunk = content[split_points[i]:split_points[i + 1]].strip("\n")
            if chunk.strip():
                result.append(("code", chunk))
    return result


def build_notebook(cells):
    nb_cells = []
    for cell_type, content in cells:
        if cell_type == "markdown":
            nb_cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [content],
            })
        else:
            source_lines = content.splitlines(keepends=True)
            nb_cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": source_lines,
            })
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "cells": nb_cells,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python py_to_ipynb.py <input.py> <output.ipynb>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]
    with open(in_path, "r", encoding="utf-8") as f:
        source_text = f.read()

    cells = split_cells(source_text)
    notebook = build_notebook(cells)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    # Validasi: pastikan hasil tulis bisa di-parse ulang sebagai JSON valid.
    with open(out_path, "r", encoding="utf-8") as f:
        json.load(f)

    print(f"Ditulis: {out_path} ({len(notebook['cells'])} cells, valid JSON).")


if __name__ == "__main__":
    main()
