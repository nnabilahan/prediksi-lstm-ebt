// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: 2026-08-03 23:51
// Sumber data (semua hasil AUDIT, lihat audit/results/ & audit/analysis/):
//   - Data aktual 2023-2025 : audit/source/DATA_REGIONAL_DISAGREGASI_V3.csv
//     (3 kategori Hydro/Solar/Wind. Produksi = hasil DISAGREGASI BULANAN dari
//     angka TAHUNAN bauran energi Dinas ESDM Sulsel; angka tahunan itu sendiri
//     adalah kalkulasi Kapasitas x Capacity Factor asumsi x 8760 jam, BUKAN
//     metering langsung. Cuaca = data riil NASA POWER.)
//   - Forecast 2026-2028    : audit/results/pipeline_run_v3/.../forecast/*.csv
//   - Metrik akurasi (MAPE) : evaluation/evaluasi_final.csv (metode terpilih
//     per kategori, dikonfirmasi pada data uji 2025)
//   - Target RUED           : audit/analysis/config_target_rued.csv (Perda No. 2
//     Tahun 2022 -- mencakup SELURUH SEKTOR energi, bukan spesifik kelistrikan;
//     lihat audit/results/tugas2_findings.md untuk keterbatasan cakupan ini)
//   - Pembanding metode     : audit/results/baseline_comparison.csv (LSTM vs
//     ARIMA vs Naive Persistence, split & metrik identik)
// Untuk memperbarui: jalankan ulang audit/analysis/export_dashboard_data.py
// setelah audit/results/ berubah -- JANGAN edit angka di file ini langsung.

// [DATASET V3] 3 kategori inti: Hydro (PLTA+PLTM), Solar (PLTS+PLTS Atap),
// Wind (PLTB). PLTMH & PLT Hybrid di luar scope penelitian.
export const PLANT_META = {
  Hydro: { label: 'Hydro (PLTA + PLTM)',   color: '#2E6F95' },
  Solar: { label: 'Solar (PLTS + Atap)',   color: '#DE9A2E' },
  Wind:  { label: 'Wind (PLTB)',           color: '#2F9E7A' },
};

export const PLANT_KEYS = Object.keys(PLANT_META);

export const CUACA_CONFIG = {
  Hydro: { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan (NASA POWER) di centroid kapasitas PLTA/PLTM Sulsel.' },
  Solar: { label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan (NASA POWER).' },
  Wind:  { label: 'Kecepatan Angin',  satuan: 'm/s',    help: 'Kecepatan angin rata-rata bulanan (NASA POWER) di centroid kapasitas PLTB Sulsel.' },
};

// Target RUED Provinsi Sulawesi Selatan (Perda No. 2 Tahun 2022).
// PENTING: target ini mencakup BAURAN ENERGI SELURUH SEKTOR (listrik +
// transportasi + industri, dst), BUKAN spesifik sektor kelistrikan --
// lihat audit/results/tugas2_findings.md. Jangan dibandingkan langsung
// dengan forecast GWh (satuan & cakupan berbeda) tanpa data total bauran
// energi Sulsel sebagai penyebut yang valid.
export const RUED_TARGET = {
  "anchors": [
    {
      "year": 2025,
      "persen": 20.0
    },
    {
      "year": 2050,
      "persen": 32.0
    }
  ],
  "sumber": "Perda Provinsi Sulawesi Selatan No. 2 Tahun 2022 (RUED)",
  "cakupan": "Bauran energi seluruh sektor (nasional/daerah) -- BUKAN spesifik sektor kelistrikan"
};

// Total produksi EBT sektor kelistrikan per tahun (GWh) -- 2023-2025 dari
// DATA_REGIONAL_DISAGREGASI_V3.csv (disagregasi bulanan dari angka tahunan
// Dinas ESDM Sulsel).
export const ANNUAL_ACTUAL = [
  {
    "year": 2023,
    "total": 4350.6
  },
  {
    "year": 2024,
    "total": 4727.4
  },
  {
    "year": 2025,
    "total": 5231.98
  }
];

// Forecast total produksi EBT per tahun (GWh), 2026-2028, model LSTM Fine-Tuning.
export const ANNUAL_FORECAST = [
  {
    "year": 2026,
    "total": 4927.96,
    "yoy": null
  },
  {
    "year": 2027,
    "total": 4910.61,
    "yoy": -0.35
  },
  {
    "year": 2028,
    "total": 4896.95,
    "yoy": -0.28
  }
];

// Gabungan aktual (2023-2025) + forecast (2026-2028) untuk chart tren tahunan.
export const TREND_ANNUAL = [
  {
    "year": 2023,
    "aktual": 4350.6,
    "prediksi": null
  },
  {
    "year": 2024,
    "aktual": 4727.4,
    "prediksi": null
  },
  {
    "year": 2025,
    "aktual": 5231.98,
    "prediksi": 5231.98
  },
  {
    "year": 2026,
    "aktual": null,
    "prediksi": 4927.96
  },
  {
    "year": 2027,
    "aktual": null,
    "prediksi": 4910.61
  },
  {
    "year": 2028,
    "aktual": null,
    "prediksi": 4896.95
  }
];

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = [
  {
    "jenis": "Hydro",
    "produksi": 4187.39,
    "pct": 85.0,
    "yoy": -7.3
  },
  {
    "jenis": "Wind",
    "produksi": 714.87,
    "pct": 14.5,
    "yoy": 3.8
  },
  {
    "jenis": "Solar",
    "produksi": 25.69,
    "pct": 0.5,
    "yoy": 6.4
  }
];

// MAPE (Mean Absolute Percentage Error, %) dari model yang BENAR-BENAR
// dipakai untuk forecast per kategori -- dipakai sebagai basis "akurasi
// model" (100% - MAPE).
export const MODEL_RMSE = {
  "Solar": 14.0,
  "Wind": 16.0,
  "Hydro": 35.9,
  "TOTAL": 22.0
};

// Data BULANAN AKTUAL 2023-2025 hasil disagregasi angka tahunan resmi.
// 36 nilai: Jan 2023 (idx 0) -> Des 2025 (idx 35).
export const MONTHLY_ACTUAL_TOTAL = [
  390.0665,
  359.4619,
  389.012,
  443.6766,
  516.6487,
  491.0968,
  396.5191,
  325.4328,
  266.5228,
  221.3469,
  250.3768,
  300.4414,
  425.2376,
  471.1543,
  416.4849,
  413.8142,
  450.0829,
  444.7527,
  509.4398,
  421.596,
  347.6806,
  221.23,
  242.5095,
  363.414,
  665.3723,
  617.1177,
  582.2869,
  480.6304,
  455.7481,
  395.8661,
  366.2768,
  320.2925,
  309.2663,
  307.4808,
  339.9133,
  391.7283
];

export const MONTHLY_ACTUAL_PER_PLT = {
  "Hydro": [
    338.4792,
    305.2396,
    352.0937,
    407.5655,
    474.3343,
    446.0915,
    345.4313,
    258.82,
    197.6997,
    161.6358,
    217.8317,
    266.6411,
    373.1393,
    426.1528,
    377.8637,
    378.6814,
    389.4022,
    386.2223,
    443.0063,
    344.5201,
    286.555,
    169.2619,
    199.2438,
    305.8161,
    605.9965,
    558.4673,
    528.5816,
    436.0438,
    405.618,
    335.2244,
    302.8182,
    243.4068,
    229.7242,
    256.5493,
    283.5545,
    332.884
  ],
  "Solar": [
    0.6543,
    0.5677,
    0.7597,
    0.7302,
    0.7126,
    0.6819,
    0.738,
    0.9053,
    0.9772,
    1.0021,
    0.8578,
    0.7522,
    1.4132,
    1.6554,
    1.6967,
    1.6485,
    1.7391,
    1.6529,
    1.7583,
    2.0802,
    2.184,
    2.2003,
    1.9837,
    1.1791,
    1.7368,
    1.8195,
    1.9918,
    2.0307,
    1.9181,
    1.656,
    2.0489,
    2.2783,
    2.5106,
    2.4501,
    1.9519,
    1.744
  ],
  "Wind": [
    50.933,
    53.6546,
    36.1586,
    35.3809,
    41.6018,
    44.3234,
    50.3498,
    65.7075,
    67.8459,
    58.709,
    31.6873,
    33.0481,
    50.6851,
    43.3461,
    36.9245,
    33.4843,
    58.9416,
    56.8775,
    64.6752,
    74.9957,
    58.9416,
    49.7678,
    41.282,
    56.4188,
    57.639,
    56.8309,
    51.7135,
    42.5559,
    48.212,
    58.9857,
    61.4097,
    74.6074,
    77.0315,
    48.4814,
    54.4069,
    57.1003
  ]
};

// Forecast bulanan total (GWh), 36 nilai: Jan 2026 (idx 0) -> Des 2028 (idx 35).
export const MONTHLY_FORECAST_TOTAL = [
  392.8796,
  420.82712,
  432.21454,
  439.47003,
  423.39078,
  409.73444,
  400.842,
  393.42,
  394.15485,
  399.38113,
  407.9145,
  413.72726,
  416.18546,
  415.6679,
  412.23932,
  408.11017,
  404.80756,
  403.62463,
  404.30844,
  406.1894,
  408.44815,
  410.10785,
  410.70245,
  410.22083,
  409.11386,
  407.90997,
  407.0515,
  406.79022,
  407.08926,
  407.71945,
  408.37445,
  408.81458,
  408.92776,
  408.7406,
  408.3869,
  408.03156
];

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {
  "Hydro": [
    335.99362,
    363.00824,
    370.17325,
    372.24008,
    358.72516,
    346.38666,
    338.2592,
    331.99014,
    333.5939,
    338.8504,
    346.467,
    351.70236,
    353.80984,
    353.12994,
    349.79434,
    345.94525,
    342.93698,
    341.88257,
    342.57315,
    344.37863,
    346.52142,
    348.07953,
    348.62708,
    348.1585,
    347.09512,
    345.93994,
    345.1165,
    344.86676,
    345.15582,
    345.765,
    346.40024,
    346.82883,
    346.9405,
    346.7595,
    346.41498,
    346.06723
  ],
  "Solar": [
    2.137631,
    2.205527,
    2.229694,
    2.182153,
    2.102869,
    2.088976,
    2.121709,
    2.122933,
    2.124613,
    2.12564,
    2.125686,
    2.12531,
    2.125095,
    2.125054,
    2.125039,
    2.125041,
    2.12505,
    2.125055,
    2.125057,
    2.125057,
    2.125057,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056,
    2.125056
  ],
  "Wind": [
    54.74836,
    55.61335,
    59.811596,
    65.0478,
    62.56276,
    61.258812,
    60.46112,
    59.306927,
    58.43634,
    58.405087,
    59.32178,
    59.899597,
    60.25051,
    60.412907,
    60.319923,
    60.03989,
    59.745525,
    59.616997,
    59.61022,
    59.68572,
    59.801674,
    59.90328,
    59.950333,
    59.93726,
    59.89368,
    59.844986,
    59.80998,
    59.798405,
    59.80838,
    59.82937,
    59.849155,
    59.860703,
    59.862206,
    59.856037,
    59.84688,
    59.839283
  ]
};

// Pembanding metode: LSTM Fine-Tuning vs ARIMA(1,1,1) vs Naive Persistence,
// evaluasi pada data uji tahun 2025 (split identik untuk ketiganya).
export const BASELINE_COMPARISON = [
  {
    "plt": "Hydro",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 127.734,
    "mae": 108.57,
    "mape": 29.59
  },
  {
    "plt": "Hydro",
    "model": "LSTM_FineTuning",
    "rmse": 109.061,
    "mae": 80.654,
    "mape": 21.76
  },
  {
    "plt": "Hydro",
    "model": "Naive_Persistence",
    "rmse": 98.469,
    "mae": 64.968,
    "mape": 15.77
  },
  {
    "plt": "Solar",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 1.187,
    "mae": 1.157,
    "mape": 56.84
  },
  {
    "plt": "Solar",
    "model": "LSTM_FineTuning",
    "rmse": 0.409,
    "mae": 0.347,
    "mape": 18.77
  },
  {
    "plt": "Solar",
    "model": "Naive_Persistence",
    "rmse": 0.287,
    "mae": 0.237,
    "mape": 12.28
  },
  {
    "plt": "Wind",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 11.866,
    "mae": 8.618,
    "mape": 13.65
  },
  {
    "plt": "Wind",
    "model": "LSTM_FineTuning",
    "rmse": 22.763,
    "mae": 19.441,
    "mape": 36.27
  },
  {
    "plt": "Wind",
    "model": "Naive_Persistence",
    "rmse": 10.423,
    "mae": 7.329,
    "mape": 13.69
  }
];

// Contoh baris data historis untuk halaman Data EBT -- diambil dari
// audit/source/DATA_REGIONAL_DISAGREGASI_V3.csv.
export const SAMPLE_MONTHLY_ROWS = [
  {
    "id": 1,
    "tanggal": "01 Jan 2023",
    "jenis": "Hydro",
    "produksi": 338.479,
    "kapasitas": 717.63,
    "cuaca": 7.79
  },
  {
    "id": 2,
    "tanggal": "01 Jan 2023",
    "jenis": "Solar",
    "produksi": 0.654,
    "kapasitas": 5.33,
    "cuaca": 4.66
  },
  {
    "id": 3,
    "tanggal": "01 Jan 2023",
    "jenis": "Wind",
    "produksi": 50.933,
    "kapasitas": 130.0,
    "cuaca": 2.62
  },
  {
    "id": 4,
    "tanggal": "01 Feb 2023",
    "jenis": "Hydro",
    "produksi": 305.24,
    "kapasitas": 717.63,
    "cuaca": 6.26
  },
  {
    "id": 5,
    "tanggal": "01 Feb 2023",
    "jenis": "Solar",
    "produksi": 0.568,
    "kapasitas": 5.33,
    "cuaca": 4.043
  },
  {
    "id": 6,
    "tanggal": "01 Feb 2023",
    "jenis": "Wind",
    "produksi": 53.655,
    "kapasitas": 130.0,
    "cuaca": 2.76
  },
  {
    "id": 7,
    "tanggal": "01 Mar 2023",
    "jenis": "Hydro",
    "produksi": 352.094,
    "kapasitas": 717.63,
    "cuaca": 10.26
  },
  {
    "id": 8,
    "tanggal": "01 Mar 2023",
    "jenis": "Solar",
    "produksi": 0.76,
    "kapasitas": 5.33,
    "cuaca": 5.411
  }
];
