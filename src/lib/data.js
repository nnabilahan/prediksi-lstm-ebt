// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: 2026-08-04 18:41
// Sumber data (semua hasil AUDIT, lihat audit/results/ & audit/analysis/):
//   - Data aktual 2023-2025 : audit/source/DATA_REGIONAL_5JENIS.csv
//     (5 jenis PLT. Produksi = hasil DISAGREGASI BULANAN dari
//     angka TAHUNAN bauran energi Dinas ESDM Sulsel; angka tahunan itu sendiri
//     adalah kalkulasi Kapasitas x Capacity Factor asumsi x 8760 jam, BUKAN
//     metering langsung. Cuaca = data riil NASA POWER.)
//   - Forecast 2026-2028    : audit/results/pipeline_run_v4/.../forecast/*.csv
//   - Metrik akurasi (MAPE) : audit/results/production_model/evaluation/evaluasi_final.csv
//     (model produksi terbaru: pooled + category embedding + ensembling
//     N_SEED=3, dipilih lewat walk-forward validation -- lihat
//     audit/results/framing_findings.md dan build_production_model.py)
//   [PENTING] Forecast 2026-2028 di bawah (ANNUAL_FORECAST,
//   MONTHLY_FORECAST_*) memakai model produksi yang SAMA dengan MAPE di
//   atas, tapi dengan DUA ASUMSI TAMBAHAN yang wajib diungkap: (1) Cuaca
//   bulan yang ditebak = NORMAL KLIMATOLOGIS per bulan kalender (rata-rata
//   2023-2025), BUKAN prakiraan cuaca operasional -- horizon 3 tahun di
//   luar jangkauan prakiraan BMKG; (2) Kapasitas = LOCF Desember 2025,
//   TIDAK memperhitungkan rencana penambahan kapasitas EBT yang mungkin ada
//   di RUED/RUPTL. Forecast juga OTOREGRESIF (prediksi bulan t jadi input
//   bulan t+1), jadi kesalahan bisa terakumulasi -- akurasinya TIDAK sama
//   dengan MAPE evaluasi 1-langkah di atas. Detail lengkap:
//   audit/analysis/build_forecast_production.py dan
//   audit/results/framing_findings.md.
//   - Target RUED           : audit/analysis/config_target_rued.csv (Perda No. 2
//     Tahun 2022 -- mencakup SELURUH SEKTOR energi, bukan spesifik kelistrikan;
//     lihat audit/results/tugas2_findings.md untuk keterbatasan cakupan ini)
//   - Pembanding metode     : audit/results/baseline_comparison.csv (LSTM vs
//     ARIMA vs Naive Persistence, split & metrik identik)
// Untuk memperbarui: jalankan ulang audit/analysis/export_dashboard_data.py
// setelah audit/results/ berubah -- JANGAN edit angka di file ini langsung.

// [DATASET 4/5 JENIS] 5 jenis PLT regional. PLTMH & PLT Hybrid tidak ada
// di dataset ini.
export const PLANT_META = {
  PLTA:        { label: 'PLTA (Tenaga Air)',   color: '#2E6F95' },
  PLTB:        { label: 'PLTB (Tenaga Angin)', color: '#2F9E7A' },
  PLTM:        { label: 'PLTM (Mini Hidro)',   color: '#7C6FAE' },
  PLTS:        { label: 'PLTS (Tenaga Surya)', color: '#DE9A2E' },
  'PLTS Atap': { label: 'PLTS Atap (Rooftop)', color: '#B8801F' },
};

export const PLANT_KEYS = Object.keys(PLANT_META);

export const CUACA_CONFIG = {
  PLTA:        { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan (NASA POWER) di area DAS pembangkit.' },
  PLTB:        { label: 'Kecepatan Angin',  satuan: 'm/s',    help: 'Kecepatan angin rata-rata bulanan (NASA POWER) di lokasi pembangkit.' },
  PLTM:        { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan (NASA POWER) di area DAS pembangkit.' },
  PLTS:        { label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan (NASA POWER).' },
  'PLTS Atap': { label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan (NASA POWER).' },
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
// DATA_REGIONAL_5JENIS.csv (disagregasi bulanan dari angka tahunan
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
    "total": 5204.36,
    "yoy": null
  },
  {
    "year": 2027,
    "total": 5176.72,
    "yoy": -0.53
  },
  {
    "year": 2028,
    "total": 5177.85,
    "yoy": 0.02
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
    "prediksi": 5204.36
  },
  {
    "year": 2027,
    "aktual": null,
    "prediksi": 5176.72
  },
  {
    "year": 2028,
    "aktual": null,
    "prediksi": 5177.85
  }
];

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = [
  {
    "jenis": "PLTA",
    "produksi": 4133.37,
    "pct": 79.4,
    "yoy": -0.5
  },
  {
    "jenis": "PLTB",
    "produksi": 702.43,
    "pct": 13.5,
    "yoy": 2.0
  },
  {
    "jenis": "PLTM",
    "produksi": 345.48,
    "pct": 6.6,
    "yoy": -4.9
  },
  {
    "jenis": "PLTS Atap",
    "produksi": 12.67,
    "pct": 0.2,
    "yoy": -3.7
  },
  {
    "jenis": "PLTS",
    "produksi": 10.41,
    "pct": 0.2,
    "yoy": -5.2
  }
];

// MAPE (Mean Absolute Percentage Error, %) dari model yang BENAR-BENAR
// dipakai untuk forecast per kategori -- dipakai sebagai basis "akurasi
// model" (100% - MAPE).
export const MODEL_RMSE = {
  "PLTA": 11.0,
  "PLTB": 7.5,
  "PLTM": 8.9,
  "PLTS": 7.9,
  "PLTS Atap": 7.9,
  "TOTAL": 8.6
};

// Data BULANAN AKTUAL 2023-2025 hasil disagregasi angka tahunan resmi.
// 36 nilai: Jan 2023 (idx 0) -> Des 2025 (idx 35).
export const MONTHLY_ACTUAL_TOTAL = [
  390.0665,
  359.4618,
  389.0121,
  443.6765,
  516.6488,
  491.0969,
  396.5191,
  325.4328,
  266.5228,
  221.3469,
  250.3769,
  300.4414,
  425.2375,
  471.1544,
  416.4848,
  413.8141,
  450.0828,
  444.7527,
  509.4399,
  421.596,
  347.6806,
  221.23,
  242.5095,
  363.414,
  665.3723,
  617.1177,
  582.2868,
  480.6304,
  455.748,
  395.8663,
  366.2768,
  320.2925,
  309.2663,
  307.4807,
  339.9133,
  391.7283
];

export const MONTHLY_ACTUAL_PER_PLT = {
  "PLTA": [
    308.1843,
    277.9197,
    320.5803,
    371.0871,
    431.88,
    406.165,
    314.5142,
    235.6548,
    180.005,
    147.1689,
    198.3351,
    242.7759,
    341.1097,
    389.5727,
    345.4286,
    346.1761,
    355.9767,
    353.0698,
    404.9796,
    314.9472,
    261.9577,
    154.7328,
    182.1411,
    279.5655,
    557.2776,
    513.5695,
    486.0864,
    400.9882,
    373.0084,
    308.2742,
    278.4732,
    223.8382,
    211.2555,
    235.9241,
    260.7582,
    306.1219
  ],
  "PLTB": [
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
  ],
  "PLTM": [
    30.2949,
    27.3198,
    31.5134,
    36.4783,
    42.4543,
    39.9265,
    30.9171,
    23.1652,
    17.6947,
    14.4669,
    19.4966,
    23.8652,
    32.0295,
    36.5801,
    32.435,
    32.5052,
    33.4255,
    33.1525,
    38.0268,
    29.5729,
    24.5973,
    14.5291,
    17.1027,
    26.2506,
    48.7189,
    44.8978,
    42.4952,
    35.0556,
    32.6095,
    26.9503,
    24.345,
    19.5686,
    18.4686,
    20.6252,
    22.7963,
    26.7621
  ],
  "PLTS": [
    0.6309,
    0.5474,
    0.7326,
    0.7041,
    0.6872,
    0.6576,
    0.7116,
    0.8729,
    0.9423,
    0.9663,
    0.8272,
    0.7253,
    0.6005,
    0.7035,
    0.721,
    0.7005,
    0.739,
    0.7024,
    0.7472,
    0.884,
    0.9281,
    0.935,
    0.843,
    0.5011,
    0.7898,
    0.8274,
    0.9057,
    0.9234,
    0.8722,
    0.7531,
    0.9317,
    1.036,
    1.1417,
    1.1141,
    0.8876,
    0.7931
  ],
  "PLTS Atap": [
    0.0234,
    0.0203,
    0.0272,
    0.0261,
    0.0255,
    0.0244,
    0.0264,
    0.0324,
    0.0349,
    0.0358,
    0.0307,
    0.0269,
    0.8127,
    0.952,
    0.9757,
    0.948,
    1.0,
    0.9505,
    1.0111,
    1.1962,
    1.2559,
    1.2653,
    1.1407,
    0.678,
    0.947,
    0.9921,
    1.086,
    1.1073,
    1.0459,
    0.903,
    1.1172,
    1.2423,
    1.369,
    1.3359,
    1.0643,
    0.9509
  ]
};

// Forecast bulanan total (GWh), 36 nilai: Jan 2026 (idx 0) -> Des 2028 (idx 35).
export const MONTHLY_FORECAST_TOTAL = [
  449.6307,
  481.0876,
  480.1823,
  462.8022,
  463.3666,
  431.5365,
  439.1217,
  406.5319,
  385.7364,
  369.4998,
  395.998,
  438.8648,
  476.1211,
  483.2755,
  460.8513,
  443.4965,
  452.4109,
  425.9943,
  437.0138,
  406.0752,
  385.9069,
  369.923,
  396.409,
  439.2379,
  476.5014,
  483.6196,
  461.0698,
  443.5983,
  452.4419,
  426.0006,
  437.0217,
  406.0906,
  385.9237,
  369.9337,
  396.4127,
  439.237
];

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {
  "PLTA": [
    362.6229,
    391.4731,
    394.3115,
    381.2539,
    377.6233,
    342.2183,
    343.5988,
    301.124,
    283.1594,
    279.7123,
    316.8895,
    359.3852,
    394.5109,
    400.0683,
    380.044,
    365.4756,
    367.6714,
    337.2079,
    342.0352,
    301.4246,
    284.0522,
    280.5404,
    317.4418,
    359.7552,
    394.7957,
    400.2772,
    380.1716,
    365.5277,
    367.6768,
    337.2009,
    342.029,
    301.421,
    284.0511,
    280.5408,
    317.4427,
    359.756
  ],
  "PLTB": [
    56.7939,
    56.6532,
    52.114,
    48.1759,
    51.9963,
    56.7893,
    64.5276,
    75.6257,
    74.9552,
    63.3803,
    51.5464,
    49.8693,
    50.1397,
    50.591,
    47.951,
    45.6378,
    51.8023,
    56.8373,
    64.3182,
    75.052,
    74.3155,
    63.0136,
    51.4203,
    49.8758,
    50.233,
    50.7221,
    48.0386,
    45.6856,
    51.8272,
    56.8505,
    64.3328,
    75.0714,
    74.3336,
    63.0241,
    51.4232,
    49.8742
  ],
  "PLTM": [
    28.7632,
    31.6081,
    32.1348,
    31.6492,
    31.9596,
    30.8808,
    29.132,
    27.4178,
    24.9563,
    23.7333,
    25.2962,
    27.9464,
    30.1316,
    31.4173,
    31.3752,
    30.7865,
    31.2543,
    30.3798,
    28.8602,
    27.2883,
    24.9199,
    23.7323,
    25.3066,
    27.9579,
    30.1418,
    31.4252,
    31.3806,
    30.7895,
    31.2556,
    30.3802,
    28.86,
    27.288,
    24.9196,
    23.7321,
    25.3065,
    27.9578
  ],
  "PLTS": [
    0.6581,
    0.6124,
    0.7331,
    0.7779,
    0.806,
    0.7422,
    0.8393,
    1.066,
    1.2017,
    1.2048,
    1.0198,
    0.7475,
    0.6007,
    0.5377,
    0.6655,
    0.7176,
    0.7563,
    0.7047,
    0.8092,
    1.0401,
    1.1795,
    1.1868,
    1.0073,
    0.7402,
    0.5967,
    0.5357,
    0.6643,
    0.7169,
    0.7559,
    0.7045,
    0.809,
    1.04,
    1.1795,
    1.1868,
    1.0073,
    0.7401
  ],
  "PLTS Atap": [
    0.7926,
    0.7408,
    0.8889,
    0.9453,
    0.9814,
    0.9059,
    1.024,
    1.2984,
    1.4638,
    1.4691,
    1.2461,
    0.9164,
    0.7382,
    0.6612,
    0.8156,
    0.879,
    0.9266,
    0.8646,
    0.991,
    1.2702,
    1.4398,
    1.4499,
    1.233,
    0.9088,
    0.7342,
    0.6594,
    0.8147,
    0.8786,
    0.9264,
    0.8645,
    0.9909,
    1.2702,
    1.4399,
    1.4499,
    1.233,
    0.9089
  ]
};

// Pembanding metode: LSTM Fine-Tuning vs ARIMA(1,1,1) vs Naive Persistence,
// evaluasi pada data uji tahun 2025 (split identik untuk ketiganya).
export const BASELINE_COMPARISON = [
  {
    "plt": "PLTA",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 117.66,
    "mae": 99.465,
    "mape": 29.29
  },
  {
    "plt": "PLTA",
    "model": "LSTM_FineTuning",
    "rmse": 90.648,
    "mae": 72.538,
    "mape": 20.62
  },
  {
    "plt": "PLTA",
    "model": "Naive_Persistence",
    "rmse": 90.976,
    "mae": 59.883,
    "mape": 15.8
  },
  {
    "plt": "PLTB",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 11.866,
    "mae": 8.618,
    "mape": 13.65
  },
  {
    "plt": "PLTB",
    "model": "LSTM_FineTuning",
    "rmse": 12.679,
    "mae": 10.727,
    "mape": 20.42
  },
  {
    "plt": "PLTB",
    "model": "Naive_Persistence",
    "rmse": 10.423,
    "mae": 7.329,
    "mape": 13.69
  },
  {
    "plt": "PLTM",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 10.309,
    "mae": 9.103,
    "mape": 32.96
  },
  {
    "plt": "PLTM",
    "model": "LSTM_FineTuning",
    "rmse": 10.122,
    "mae": 7.873,
    "mape": 28.88
  },
  {
    "plt": "PLTM",
    "model": "Naive_Persistence",
    "rmse": 7.497,
    "mae": 5.084,
    "mape": 15.49
  },
  {
    "plt": "PLTS",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 0.548,
    "mae": 0.534,
    "mape": 57.7
  },
  {
    "plt": "PLTS",
    "model": "LSTM_FineTuning",
    "rmse": 0.119,
    "mae": 0.095,
    "mape": 10.5
  },
  {
    "plt": "PLTS",
    "model": "Naive_Persistence",
    "rmse": 0.136,
    "mae": 0.111,
    "mape": 12.65
  },
  {
    "plt": "PLTS Atap",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 0.567,
    "mae": 0.548,
    "mape": 49.1
  },
  {
    "plt": "PLTS Atap",
    "model": "LSTM_FineTuning",
    "rmse": 0.155,
    "mae": 0.116,
    "mape": 10.15
  },
  {
    "plt": "PLTS Atap",
    "model": "Naive_Persistence",
    "rmse": 0.151,
    "mae": 0.126,
    "mape": 11.97
  }
];

// Contoh baris data historis untuk halaman Data EBT -- diambil dari
// audit/source/DATA_REGIONAL_5JENIS.csv.
export const SAMPLE_MONTHLY_ROWS = [
  {
    "id": 1,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTA",
    "produksi": 308.184,
    "kapasitas": 653.4,
    "cuaca": 7.79
  },
  {
    "id": 2,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTB",
    "produksi": 50.933,
    "kapasitas": 130.0,
    "cuaca": 2.62
  },
  {
    "id": 3,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTM",
    "produksi": 30.295,
    "kapasitas": 64.23,
    "cuaca": 7.79
  },
  {
    "id": 4,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTS",
    "produksi": 0.631,
    "kapasitas": 5.14,
    "cuaca": 4.66
  },
  {
    "id": 5,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTS Atap",
    "produksi": 0.023,
    "kapasitas": 0.191,
    "cuaca": 4.66
  },
  {
    "id": 6,
    "tanggal": "01 Feb 2023",
    "jenis": "PLTA",
    "produksi": 277.92,
    "kapasitas": 653.4,
    "cuaca": 6.26
  },
  {
    "id": 7,
    "tanggal": "01 Feb 2023",
    "jenis": "PLTB",
    "produksi": 53.655,
    "kapasitas": 130.0,
    "cuaca": 2.76
  },
  {
    "id": 8,
    "tanggal": "01 Feb 2023",
    "jenis": "PLTM",
    "produksi": 27.32,
    "kapasitas": 64.23,
    "cuaca": 6.26
  }
];
