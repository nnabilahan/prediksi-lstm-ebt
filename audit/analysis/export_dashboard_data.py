"""
Generator src/lib/data.js dari hasil audit (Tugas 1 & 2), menggantikan
data dummy/placeholder yang tadinya ditulis tangan.

Sumber data (semua dari folder audit/, bukan Downloads langsung):
- audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv   -> data aktual 2023-2025
  (hasil rekonstruksi, lihat audit/source/README.md)
- audit/results/pipeline_run/EBT_LSTM_Streamlit/forecast/*.csv -> forecast 2026-2028
- audit/results/eval_summary.csv (Stage == FineTuning)          -> metrik akurasi (MAPE)
- audit/analysis/config_target_rued.csv                          -> target RUED terkoreksi
- audit/results/baseline_comparison.csv                          -> LSTM vs ARIMA vs Naive

PENTING: script ini MENIMPA src/lib/data.js sepenuhnya kecuali PLANT_META
dan CUACA_CONFIG (konstanta statis, bukan hasil data/model). Jalankan ulang
script ini setiap kali audit/results/ diperbarui, jangan edit data.js manual.
"""
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_DIR = os.path.join(REPO_ROOT, "audit")
SOURCE_DIR = os.path.join(AUDIT_DIR, "source")
RESULTS_DIR = os.path.join(AUDIT_DIR, "results")
ANALYSIS_DIR = os.path.join(AUDIT_DIR, "analysis")
FORECAST_DIR = os.path.join(RESULTS_DIR, "pipeline_run", "EBT_LSTM_Streamlit", "forecast")

DATA_JS_PATH = os.path.join(REPO_ROOT, "src", "lib", "data.js")

PLANT_ORDER = ["PLTA", "PLTB", "PLTM", "PLTMH", "PLTS", "PLTS Atap", "PLT Hybrid"]


def load_actual():
    df = pd.read_csv(os.path.join(SOURCE_DIR, "DATA_PHASE_3_REGIONAL_MODIFIED.csv"))
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df = df.sort_values(["Jenis", "Tanggal"]).reset_index(drop=True)
    return df


def load_forecast_total():
    df = pd.read_csv(os.path.join(FORECAST_DIR, "forecast_total_2026_2028.csv"))
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    return df.sort_values("Tanggal").reset_index(drop=True)


def load_forecast_per_plt():
    df = pd.read_csv(os.path.join(FORECAST_DIR, "forecast_per_PLT_2026_2028.csv"))
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    return df.sort_values(["Jenis_PLT", "Tanggal"]).reset_index(drop=True)


def build_annual_actual(actual_df):
    annual = actual_df.groupby(actual_df["Tanggal"].dt.year)["Produksi"].sum()
    return [{"year": int(y), "total": round(float(v), 2)} for y, v in annual.items()]


def build_monthly_actual_total(actual_df):
    monthly = actual_df.groupby("Tanggal")["Produksi"].sum().sort_index()
    return [round(float(v), 6) for v in monthly.values]


def build_monthly_actual_per_plt(actual_df):
    result = {}
    for plt in PLANT_ORDER:
        sub = actual_df[actual_df["Jenis"] == plt].sort_values("Tanggal")
        result[plt] = [round(float(v), 6) for v in sub["Produksi"].values]
    return result


def build_annual_forecast(forecast_total_df):
    annual = forecast_total_df.groupby(forecast_total_df["Tanggal"].dt.year)["Total_Produksi_EBT"].sum()
    years = sorted(annual.index)
    rows = []
    prev = None
    for y in years:
        total = float(annual[y])
        yoy = None if prev is None else round((total - prev) / prev * 100, 2)
        rows.append({"year": int(y), "total": round(total, 2), "yoy": yoy})
        prev = total
    return rows


def build_monthly_forecast_total(forecast_total_df):
    return [round(float(v), 6) for v in forecast_total_df.sort_values("Tanggal")["Total_Produksi_EBT"].values]


def build_monthly_forecast_per_plt(forecast_per_plt_df):
    result = {}
    for plt in PLANT_ORDER:
        sub = forecast_per_plt_df[forecast_per_plt_df["Jenis_PLT"] == plt].sort_values("Tanggal")
        result[plt] = [round(float(v), 6) for v in sub["Produksi_Prediksi"].values]
    return result


def build_per_jenis_2026(monthly_forecast_per_plt, actual_2025_per_plt):
    rows = []
    total_2026 = sum(sum(v[:12]) for v in monthly_forecast_per_plt.values())
    for plt in PLANT_ORDER:
        produksi = sum(monthly_forecast_per_plt[plt][:12])
        pct = produksi / total_2026 * 100 if total_2026 else 0
        prev = actual_2025_per_plt.get(plt)
        yoy = round((produksi - prev) / prev * 100, 1) if prev else None
        rows.append({
            "jenis": plt,
            "produksi": round(produksi, 2),
            "pct": round(pct, 1),
            "yoy": yoy,
        })
    rows.sort(key=lambda r: -r["produksi"])
    return rows


def build_model_mape(eval_summary_path):
    df = pd.read_csv(eval_summary_path)
    ft = df[df["Stage"] == "FineTuning"]
    result = {row["PLT"]: round(float(row["MAPE"]), 1) for _, row in ft.iterrows()}
    result["TOTAL"] = round(float(ft["MAPE"].mean()), 1)
    return result


def build_ru_target(config_path):
    df = pd.read_csv(config_path)
    row0, row1 = df.iloc[0], df.iloc[1]
    return {
        "anchors": [
            {"year": int(row0["Tahun"]), "persen": float(row0["Target_Bauran_EBT_Persen"])},
            {"year": int(row1["Tahun"]), "persen": float(row1["Target_Bauran_EBT_Persen"])},
        ],
        "sumber": str(row0["Sumber"]),
        "cakupan": str(row0["Cakupan"]),
    }


def build_baseline_comparison(path):
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "plt": r["PLT"], "model": r["Model"],
            "rmse": round(float(r["RMSE"]), 3), "mae": round(float(r["MAE"]), 3),
            "mape": round(float(r["MAPE"]), 2),
        })
    return rows


def build_sample_monthly_rows(actual_df, n=8):
    sub = actual_df.sort_values(["Tanggal", "Jenis"]).head(n).reset_index(drop=True)
    rows = []
    for i, r in sub.iterrows():
        rows.append({
            "id": i + 1,
            "tanggal": r["Tanggal"].strftime("%d %b %Y"),
            "jenis": r["Jenis"],
            "produksi": round(float(r["Produksi"]), 3),
            "kapasitas": round(float(r["Kapasitas"]), 3),
            "cuaca": round(float(r["Cuaca"]), 3),
        })
    return rows


def js_num(v):
    if v is None:
        return "null"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return json.dumps(v)


def render_js(ctx):
    def plant_block(title, obj, quote_keys=True):
        lines = [f"export const {title} = {{"]
        for k, v in obj.items():
            key = json.dumps(k) if quote_keys else k
            lines.append(f"  {key}: {json.dumps(v)},")
        lines.append("};")
        return "\n".join(lines)

    gen_time = ctx["generated_at"]

    js = f"""// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: {gen_time}
// Sumber data (semua hasil AUDIT, lihat audit/results/ & audit/analysis/):
//   - Data aktual 2023-2025 : audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv
//     (data REKONSTRUKSI/ESTIMASI -- lihat audit/source/README.md, BUKAN data
//     "asli/terverifikasi" Dinas ESDM; Cuaca adalah proxy pola 2023 yang
//     diulang tiap tahun, lihat audit/results/audit_findings.md)
//   - Forecast 2026-2028    : audit/results/pipeline_run/.../forecast/*.csv
//   - Metrik akurasi (MAPE) : audit/results/eval_summary.csv (stage FineTuning)
//   - Target RUED           : audit/analysis/config_target_rued.csv (Perda No. 2
//     Tahun 2022 -- mencakup SELURUH SEKTOR energi, bukan spesifik kelistrikan;
//     lihat audit/results/tugas2_findings.md untuk keterbatasan cakupan ini)
//   - Pembanding metode     : audit/results/baseline_comparison.csv (LSTM vs
//     ARIMA vs Naive Persistence, split & metrik identik)
// Untuk memperbarui: jalankan ulang audit/analysis/export_dashboard_data.py
// setelah audit/results/ berubah -- JANGAN edit angka di file ini langsung.

export const PLANT_META = {{
  PLTA:        {{ label: 'PLTA (Tenaga Air)',    color: '#2E6F95' }},
  PLTB:        {{ label: 'PLTB (Tenaga Angin)',  color: '#2F9E7A' }},
  PLTM:        {{ label: 'PLTM (Mini Hidro)',    color: '#7C6FAE' }},
  PLTMH:       {{ label: 'PLTMH (Mikro Hidro)',  color: '#5FA8D3' }},
  PLTS:        {{ label: 'PLTS (Tenaga Surya)',  color: '#DE9A2E' }},
  'PLTS Atap': {{ label: 'PLTS Atap (Rooftop)', color: '#B8801F' }},
  'PLT Hybrid':{{ label: 'PLT Hybrid',          color: '#6B7A70' }},
}};

export const PLANT_KEYS = Object.keys(PLANT_META);

export const CUACA_CONFIG = {{
  PLTA:        {{ label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' }},
  PLTB:        {{ label: 'Kecepatan Angin',  satuan: 'm/s',    help: 'Kecepatan angin rata-rata bulanan di lokasi pembangkit.' }},
  PLTM:        {{ label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' }},
  PLTMH:       {{ label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' }},
  PLTS:        {{ label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan.' }},
  'PLTS Atap': {{ label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan.' }},
  'PLT Hybrid':{{ label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Kombinasi sumber energi; radiasi matahari sebagai indikator cuaca utama.' }},
}};

// Target RUED Provinsi Sulawesi Selatan (Perda No. 2 Tahun 2022).
// PENTING: target ini mencakup BAURAN ENERGI SELURUH SEKTOR (listrik +
// transportasi + industri, dst), BUKAN spesifik sektor kelistrikan --
// lihat audit/results/tugas2_findings.md. Jangan dibandingkan langsung
// dengan forecast GWh (satuan & cakupan berbeda) tanpa data total bauran
// energi Sulsel sebagai penyebut yang valid.
export const RUED_TARGET = {json.dumps(ctx["ru_target"], indent=2, ensure_ascii=False)};

// Total produksi EBT sektor kelistrikan per tahun (GWh) -- data aktual
// hasil rekonstruksi (2023-2025) dari DATA_PHASE_3_REGIONAL_MODIFIED.csv.
export const ANNUAL_ACTUAL = {json.dumps(ctx["annual_actual"], indent=2)};

// Forecast total produksi EBT per tahun (GWh), 2026-2028, model LSTM Fine-Tuning.
export const ANNUAL_FORECAST = {json.dumps(ctx["annual_forecast"], indent=2)};

// Gabungan aktual (2023-2025) + forecast (2026-2028) untuk chart tren tahunan.
export const TREND_ANNUAL = {json.dumps(ctx["trend_annual"], indent=2)};

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = {json.dumps(ctx["per_jenis_2026"], indent=2, ensure_ascii=False)};

// MAPE (Mean Absolute Percentage Error, %) model LSTM tahap Fine-Tuning per
// jenis PLT -- dipakai sebagai basis "akurasi model" (100% - MAPE).
export const MODEL_RMSE = {json.dumps(ctx["model_mape"], indent=2)};

// Data BULANAN AKTUAL 2023-2025 (real, hasil rekonstruksi -- BUKAN aproksimasi
// sinusoidal). 36 nilai: Jan 2023 (idx 0) -> Des 2025 (idx 35).
export const MONTHLY_ACTUAL_TOTAL = {json.dumps(ctx["monthly_actual_total"], indent=2)};

export const MONTHLY_ACTUAL_PER_PLT = {json.dumps(ctx["monthly_actual_per_plt"], indent=2, ensure_ascii=False)};

// Forecast bulanan total (GWh), 36 nilai: Jan 2026 (idx 0) -> Des 2028 (idx 35).
export const MONTHLY_FORECAST_TOTAL = {json.dumps(ctx["monthly_forecast_total"], indent=2)};

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {json.dumps(ctx["monthly_forecast_per_plt"], indent=2, ensure_ascii=False)};

// Pembanding metode: LSTM Fine-Tuning vs ARIMA(1,1,1) vs Naive Persistence,
// evaluasi pada data uji tahun 2025 (split identik untuk ketiganya).
export const BASELINE_COMPARISON = {json.dumps(ctx["baseline_comparison"], indent=2, ensure_ascii=False)};

// Contoh baris data historis (real, hasil rekonstruksi) untuk halaman Data EBT
// -- diambil dari audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv, BUKAN
// "data asli/terverifikasi" Dinas ESDM (lihat audit/source/README.md).
export const SAMPLE_MONTHLY_ROWS = {json.dumps(ctx["sample_monthly_rows"], indent=2, ensure_ascii=False)};
"""
    return js


def main():
    actual_df = load_actual()
    forecast_total_df = load_forecast_total()
    forecast_per_plt_df = load_forecast_per_plt()

    annual_actual = build_annual_actual(actual_df)
    monthly_actual_total = build_monthly_actual_total(actual_df)
    monthly_actual_per_plt = build_monthly_actual_per_plt(actual_df)

    annual_forecast = build_annual_forecast(forecast_total_df)
    monthly_forecast_total = build_monthly_forecast_total(forecast_total_df)
    monthly_forecast_per_plt = build_monthly_forecast_per_plt(forecast_per_plt_df)

    actual_2025_per_plt = {
        plt: actual_df[(actual_df["Jenis"] == plt) & (actual_df["Tanggal"].dt.year == 2025)]["Produksi"].sum()
        for plt in PLANT_ORDER
    }
    per_jenis_2026 = build_per_jenis_2026(monthly_forecast_per_plt, actual_2025_per_plt)

    model_mape = build_model_mape(os.path.join(RESULTS_DIR, "eval_summary.csv"))
    ru_target = build_ru_target(os.path.join(ANALYSIS_DIR, "config_target_rued.csv"))
    baseline_comparison = build_baseline_comparison(os.path.join(RESULTS_DIR, "baseline_comparison.csv"))
    sample_monthly_rows = build_sample_monthly_rows(actual_df)

    trend_annual = []
    for r in annual_actual:
        trend_annual.append({"year": r["year"], "aktual": r["total"], "prediksi": None})
    # Bridge point: tahun terakhir aktual juga jadi titik awal garis prediksi
    if annual_actual:
        trend_annual[-1]["prediksi"] = trend_annual[-1]["aktual"]
    for r in annual_forecast:
        trend_annual.append({"year": r["year"], "aktual": None, "prediksi": r["total"]})

    ctx = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "annual_actual": annual_actual,
        "annual_forecast": annual_forecast,
        "trend_annual": trend_annual,
        "per_jenis_2026": per_jenis_2026,
        "model_mape": model_mape,
        "monthly_actual_total": monthly_actual_total,
        "monthly_actual_per_plt": monthly_actual_per_plt,
        "monthly_forecast_total": monthly_forecast_total,
        "monthly_forecast_per_plt": monthly_forecast_per_plt,
        "baseline_comparison": baseline_comparison,
        "sample_monthly_rows": sample_monthly_rows,
        "ru_target": ru_target,
    }

    js_content = render_js(ctx)
    with open(DATA_JS_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(js_content)

    print(f"Ditulis: {DATA_JS_PATH}")
    print(f"ANNUAL_ACTUAL: {annual_actual}")
    print(f"ANNUAL_FORECAST: {annual_forecast}")
    print(f"MODEL_RMSE (MAPE %): {model_mape}")
    print(f"RUED_TARGET: {ru_target}")


if __name__ == "__main__":
    main()
