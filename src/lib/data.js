// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: 2026-07-21 19:20
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

export const PLANT_META = {
  PLTA:        { label: 'PLTA (Tenaga Air)',    color: '#2E6F95' },
  PLTB:        { label: 'PLTB (Tenaga Angin)',  color: '#2F9E7A' },
  PLTM:        { label: 'PLTM (Mini Hidro)',    color: '#7C6FAE' },
  PLTMH:       { label: 'PLTMH (Mikro Hidro)',  color: '#5FA8D3' },
  PLTS:        { label: 'PLTS (Tenaga Surya)',  color: '#DE9A2E' },
  'PLTS Atap': { label: 'PLTS Atap (Rooftop)', color: '#B8801F' },
  'PLT Hybrid':{ label: 'PLT Hybrid',          color: '#6B7A70' },
};

export const PLANT_KEYS = Object.keys(PLANT_META);

export const CUACA_CONFIG = {
  PLTA:        { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' },
  PLTB:        { label: 'Kecepatan Angin',  satuan: 'm/s',    help: 'Kecepatan angin rata-rata bulanan di lokasi pembangkit.' },
  PLTM:        { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' },
  PLTMH:       { label: 'Curah Hujan',      satuan: 'mm',     help: 'Curah hujan rata-rata bulanan di area DAS pembangkit.' },
  PLTS:        { label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan.' },
  'PLTS Atap': { label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Rata-rata radiasi matahari harian dalam sebulan.' },
  'PLT Hybrid':{ label: 'Radiasi Matahari', satuan: 'kWh/m²', help: 'Kombinasi sumber energi; radiasi matahari sebagai indikator cuaca utama.' },
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
      "year": 2030,
      "persen": 32.0
    }
  ],
  "sumber": "Perda Provinsi Sulawesi Selatan No. 2 Tahun 2022 (RUED)",
  "cakupan": "Bauran energi seluruh sektor (nasional/daerah) -- BUKAN spesifik sektor kelistrikan"
};

// Total produksi EBT sektor kelistrikan per tahun (GWh) -- data aktual
// hasil rekonstruksi (2023-2025) dari DATA_PHASE_3_REGIONAL_MODIFIED.csv.
export const ANNUAL_ACTUAL = [
  {
    "year": 2023,
    "total": 1470.56
  },
  {
    "year": 2024,
    "total": 1583.62
  },
  {
    "year": 2025,
    "total": 1620.87
  }
];

// Forecast total produksi EBT per tahun (GWh), 2026-2028, model LSTM Fine-Tuning.
export const ANNUAL_FORECAST = [
  {
    "year": 2026,
    "total": 1628.49,
    "yoy": null
  },
  {
    "year": 2027,
    "total": 1604.53,
    "yoy": -1.47
  },
  {
    "year": 2028,
    "total": 1603.32,
    "yoy": -0.08
  }
];

// Gabungan aktual (2023-2025) + forecast (2026-2028) untuk chart tren tahunan.
export const TREND_ANNUAL = [
  {
    "year": 2023,
    "aktual": 1470.56,
    "prediksi": null
  },
  {
    "year": 2024,
    "aktual": 1583.62,
    "prediksi": null
  },
  {
    "year": 2025,
    "aktual": 1620.87,
    "prediksi": 1620.87
  },
  {
    "year": 2026,
    "aktual": null,
    "prediksi": 1628.49
  },
  {
    "year": 2027,
    "aktual": null,
    "prediksi": 1604.53
  },
  {
    "year": 2028,
    "aktual": null,
    "prediksi": 1603.32
  }
];

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = [
  {
    "jenis": "PLTB",
    "produksi": 639.61,
    "pct": 39.3,
    "yoy": -0.2
  },
  {
    "jenis": "PLTA",
    "produksi": 400.62,
    "pct": 24.6,
    "yoy": 2.7
  },
  {
    "jenis": "PLTM",
    "produksi": 350.99,
    "pct": 21.6,
    "yoy": -2.3
  },
  {
    "jenis": "PLTMH",
    "produksi": 208.99,
    "pct": 12.8,
    "yoy": 1.9
  },
  {
    "jenis": "PLTS Atap",
    "produksi": 13.15,
    "pct": 0.8,
    "yoy": 7.9
  },
  {
    "jenis": "PLTS",
    "produksi": 12.59,
    "pct": 0.8,
    "yoy": 16.1
  },
  {
    "jenis": "PLT Hybrid",
    "produksi": 2.53,
    "pct": 0.2,
    "yoy": -2.7
  }
];

// MAPE (Mean Absolute Percentage Error, %) model LSTM tahap Fine-Tuning per
// jenis PLT -- dipakai sebagai basis "akurasi model" (100% - MAPE).
export const MODEL_RMSE = {
  "PLT Hybrid": 11.3,
  "PLTA": 9.2,
  "PLTB": 21.1,
  "PLTM": 11.0,
  "PLTMH": 11.5,
  "PLTS": 12.2,
  "PLTS Atap": 26.4,
  "TOTAL": 14.7
};

// Data BULANAN AKTUAL 2023-2025 (real, hasil rekonstruksi -- BUKAN aproksimasi
// sinusoidal). 36 nilai: Jan 2023 (idx 0) -> Des 2025 (idx 35).
export const MONTHLY_ACTUAL_TOTAL = [
  152.581248,
  141.502842,
  127.977101,
  120.085364,
  124.781692,
  112.364115,
  112.801243,
  113.475637,
  114.362989,
  112.001119,
  117.18459,
  121.44206,
  163.55942,
  151.373978,
  135.597708,
  130.762838,
  137.797865,
  117.801823,
  125.093506,
  116.663804,
  123.981924,
  122.618365,
  126.402194,
  131.97122,
  167.410638,
  155.221207,
  140.463729,
  132.220871,
  132.26111,
  120.164472,
  123.644866,
  128.77125,
  128.645358,
  127.300402,
  128.722238,
  136.044322
];

export const MONTHLY_ACTUAL_PER_PLT = {
  "PLTA": [
    37.593769,
    31.500986,
    35.130729,
    31.760253,
    29.815748,
    26.834173,
    22.426628,
    19.185786,
    19.833954,
    25.148935,
    31.371352,
    32.667689,
    42.693563,
    35.840955,
    39.999228,
    38.594394,
    32.830055,
    29.419907,
    24.284892,
    22.003644,
    23.202549,
    28.020745,
    33.933716,
    35.358862,
    43.428926,
    36.107585,
    38.362702,
    35.961532,
    33.605303,
    30.367601,
    26.036593,
    21.716326,
    22.855236,
    28.289923,
    35.60137,
    37.574103
  ],
  "PLTB": [
    54.325408,
    59.118827,
    36.023265,
    36.894796,
    46.626888,
    41.978724,
    53.744388,
    62.604949,
    61.733418,
    45.610102,
    34.861224,
    35.87801,
    58.075881,
    62.617586,
    37.758224,
    39.549348,
    55.379062,
    43.377464,
    61.981502,
    61.345881,
    65.933899,
    50.197843,
    39.333205,
    40.77372,
    60.606092,
    65.494433,
    43.159873,
    41.557364,
    49.062607,
    44.580312,
    57.860845,
    73.463348,
    70.943482,
    54.123693,
    38.70445,
    41.270208
  ],
  "PLTM": [
    36.971714,
    30.979747,
    34.54943,
    31.234724,
    29.322394,
    26.390155,
    22.05554,
    18.868323,
    19.505767,
    24.732802,
    30.852258,
    32.127145,
    38.353814,
    32.137851,
    35.840978,
    32.40236,
    30.418542,
    27.376688,
    22.880034,
    19.573671,
    20.234943,
    25.657379,
    32.005597,
    33.328142,
    38.992267,
    33.68663,
    35.917277,
    32.870088,
    30.834232,
    26.833117,
    24.011111,
    19.770504,
    20.839934,
    26.919177,
    33.534502,
    35.220558
  ],
  "PLTMH": [
    22.826548,
    19.127073,
    21.331016,
    19.284498,
    18.103814,
    16.293433,
    13.617217,
    11.649411,
    12.042972,
    15.270174,
    19.048361,
    19.835483,
    22.631301,
    19.228577,
    20.060842,
    18.323067,
    17.292108,
    15.776815,
    13.952881,
    11.323168,
    11.96189,
    16.200658,
    18.936942,
    20.594682,
    22.548319,
    18.326548,
    20.957482,
    19.852879,
    16.785487,
    16.510186,
    13.691663,
    11.327012,
    11.300945,
    15.252909,
    18.570263,
    19.939927
  ],
  "PLTS": [
    0.630543,
    0.547089,
    0.732154,
    0.7037,
    0.68676,
    0.65717,
    0.711169,
    0.872434,
    0.941762,
    0.965697,
    0.826675,
    0.724848,
    0.705267,
    0.550253,
    0.701237,
    0.725806,
    0.710046,
    0.725289,
    0.762065,
    0.909326,
    1.045384,
    0.915146,
    0.811189,
    0.69854,
    0.760154,
    0.659546,
    0.882652,
    0.848349,
    0.827928,
    0.792255,
    0.857353,
    1.051767,
    1.135346,
    1.164201,
    0.996603,
    0.873844
  ],
  "PLTS Atap": [
    0.02312,
    0.02006,
    0.026846,
    0.025802,
    0.025181,
    0.024096,
    0.026076,
    0.031989,
    0.034531,
    0.035409,
    0.030311,
    0.026578,
    0.897473,
    0.77869,
    1.042099,
    1.0016,
    0.977489,
    0.935372,
    1.01223,
    1.241764,
    1.340441,
    1.374508,
    1.176634,
    1.0317,
    0.854035,
    0.741002,
    0.991662,
    0.953123,
    0.930179,
    0.8901,
    0.963238,
    1.181663,
    1.275564,
    1.307983,
    1.119685,
    0.981766
  ],
  "PLT Hybrid": [
    0.210145,
    0.20906,
    0.183662,
    0.181591,
    0.200907,
    0.186364,
    0.220226,
    0.262745,
    0.270584,
    0.238,
    0.194408,
    0.182307,
    0.20212,
    0.220065,
    0.195101,
    0.166264,
    0.190563,
    0.190288,
    0.219902,
    0.26635,
    0.262818,
    0.252085,
    0.204911,
    0.185574,
    0.220844,
    0.205462,
    0.192081,
    0.177537,
    0.215375,
    0.190901,
    0.224062,
    0.260629,
    0.294851,
    0.242516,
    0.195364,
    0.183916
  ]
};

// Forecast bulanan total (GWh), 36 nilai: Jan 2026 (idx 0) -> Des 2028 (idx 35).
export const MONTHLY_FORECAST_TOTAL = [
  149.2169,
  150.05289,
  144.15602,
  134.78249,
  128.28915,
  127.63182,
  129.48373,
  129.92336,
  131.68468,
  133.62418,
  134.73314,
  134.91397,
  134.71252,
  134.42952,
  133.94038,
  133.5193,
  133.30847,
  133.27686,
  133.33276,
  133.43184,
  133.55469,
  133.64546,
  133.68634,
  133.68884,
  133.67009,
  133.6412,
  133.6121,
  133.593,
  133.58559,
  133.58675,
  133.59271,
  133.60036,
  133.60698,
  133.61086,
  133.612,
  133.61124
];

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {
  "PLTA": [
    41.71794,
    42.3093,
    39.01185,
    33.612953,
    29.445553,
    28.554722,
    29.195137,
    29.35792,
    30.454058,
    31.726229,
    32.51642,
    32.72044,
    32.66989,
    32.537907,
    32.243065,
    31.964237,
    31.800106,
    31.745161,
    31.75167,
    31.797417,
    31.870098,
    31.932531,
    31.969385,
    31.98293,
    31.98041,
    31.967289,
    31.94991,
    31.93564,
    31.927132,
    31.924038,
    31.925005,
    31.928461,
    31.932594,
    31.935913,
    31.937883,
    31.93855
  ],
  "PLTB": [
    53.96569,
    53.89774,
    53.384552,
    52.747528,
    52.611572,
    52.964924,
    53.349094,
    53.345627,
    53.338863,
    53.33373,
    53.33375,
    53.336884,
    53.33916,
    53.339104,
    53.33903,
    53.338997,
    53.33901,
    53.33903,
    53.339046,
    53.339046,
    53.33904,
    53.33904,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046,
    53.339046
  ],
  "PLTM": [
    30.105368,
    30.088722,
    29.625147,
    29.028635,
    28.699896,
    28.800358,
    29.063406,
    29.082245,
    29.109512,
    29.128845,
    29.132513,
    29.125238,
    29.118246,
    29.116978,
    29.115883,
    29.115421,
    29.115528,
    29.115845,
    29.116047,
    29.116108,
    29.116142,
    29.116148,
    29.116138,
    29.116125,
    29.116121,
    29.116116,
    29.116116,
    29.116116,
    29.116116,
    29.11612,
    29.11612,
    29.11612,
    29.11612,
    29.11612,
    29.11612,
    29.11612
  ],
  "PLTMH": [
    21.044067,
    21.363468,
    19.75211,
    17.032383,
    15.194344,
    14.975994,
    15.526358,
    15.789235,
    16.4351,
    17.08885,
    17.403738,
    17.38392,
    17.237053,
    17.087261,
    16.893959,
    16.751999,
    16.704994,
    16.727823,
    16.776897,
    16.830091,
    16.880152,
    16.908432,
    16.912418,
    16.901346,
    16.885086,
    16.869318,
    16.85757,
    16.852718,
    16.853798,
    16.85805,
    16.86303,
    16.867212,
    16.869705,
    16.870262,
    16.869434,
    16.868004
  ],
  "PLTS": [
    1.049232,
    1.049323,
    1.044426,
    1.039967,
    1.037746,
    1.043474,
    1.054134,
    1.053936,
    1.053943,
    1.054436,
    1.055342,
    1.056473,
    1.057275,
    1.057413,
    1.057604,
    1.057824,
    1.058032,
    1.058196,
    1.058296,
    1.058353,
    1.058409,
    1.058457,
    1.058495,
    1.058523,
    1.058542,
    1.058556,
    1.058568,
    1.058577,
    1.058585,
    1.05859,
    1.058594,
    1.058597,
    1.058599,
    1.058601,
    1.058602,
    1.058604
  ],
  "PLTS Atap": [
    1.12901,
    1.142857,
    1.132823,
    1.111668,
    1.08556,
    1.077557,
    1.083499,
    1.081797,
    1.079583,
    1.07772,
    1.076583,
    1.076301,
    1.076253,
    1.075995,
    1.075792,
    1.075661,
    1.075592,
    1.075558,
    1.075532,
    1.075506,
    1.07549,
    1.075479,
    1.075473,
    1.075469,
    1.075466,
    1.075463,
    1.075462,
    1.075461,
    1.07546,
    1.07546,
    1.07546,
    1.075459,
    1.075459,
    1.075459,
    1.075459,
    1.075459
  ],
  "PLT Hybrid": [
    0.20559,
    0.201478,
    0.205109,
    0.209346,
    0.21448,
    0.214795,
    0.212115,
    0.212602,
    0.213612,
    0.214373,
    0.214787,
    0.214724,
    0.214643,
    0.214854,
    0.215047,
    0.21516,
    0.215212,
    0.215232,
    0.215267,
    0.215317,
    0.215353,
    0.215375,
    0.21539,
    0.215402,
    0.215414,
    0.215426,
    0.215434,
    0.215439,
    0.215444,
    0.215448,
    0.215451,
    0.215454,
    0.215456,
    0.215458,
    0.215459,
    0.21546
  ]
};

// Pembanding metode: LSTM Fine-Tuning vs ARIMA(1,1,1) vs Naive Persistence,
// evaluasi pada data uji tahun 2025 (split identik untuk ketiganya).
export const BASELINE_COMPARISON = [
  {
    "plt": "PLT Hybrid",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 0.042,
    "mae": 0.029,
    "mape": 11.92
  },
  {
    "plt": "PLT Hybrid",
    "model": "LSTM_FineTuning",
    "rmse": 0.029,
    "mae": 0.024,
    "mape": 11.26
  },
  {
    "plt": "PLT Hybrid",
    "model": "Naive_Persistence",
    "rmse": 0.032,
    "mae": 0.03,
    "mape": 13.45
  },
  {
    "plt": "PLTA",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 7.669,
    "mae": 5.759,
    "mape": 21.57
  },
  {
    "plt": "PLTA",
    "model": "LSTM_FineTuning",
    "rmse": 3.426,
    "mae": 2.679,
    "mape": 9.23
  },
  {
    "plt": "PLTA",
    "model": "Naive_Persistence",
    "rmse": 4.754,
    "mae": 4.179,
    "mape": 12.97
  },
  {
    "plt": "PLTB",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 12.71,
    "mae": 10.638,
    "mape": 18.89
  },
  {
    "plt": "PLTB",
    "model": "LSTM_FineTuning",
    "rmse": 12.019,
    "mae": 10.606,
    "mape": 21.14
  },
  {
    "plt": "PLTB",
    "model": "Naive_Persistence",
    "rmse": 12.742,
    "mae": 10.571,
    "mape": 20.5
  },
  {
    "plt": "PLTM",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 7.608,
    "mae": 5.769,
    "mape": 23.77
  },
  {
    "plt": "PLTM",
    "model": "LSTM_FineTuning",
    "rmse": 3.575,
    "mae": 2.799,
    "mape": 10.99
  },
  {
    "plt": "PLTM",
    "model": "Naive_Persistence",
    "rmse": 4.136,
    "mae": 3.733,
    "mape": 12.73
  },
  {
    "plt": "PLTMH",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 5.868,
    "mae": 4.858,
    "mape": 34.45
  },
  {
    "plt": "PLTMH",
    "model": "LSTM_FineTuning",
    "rmse": 2.063,
    "mae": 1.868,
    "mape": 11.52
  },
  {
    "plt": "PLTMH",
    "model": "Naive_Persistence",
    "rmse": 2.603,
    "mae": 2.258,
    "mape": 13.51
  },
  {
    "plt": "PLTS",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 0.264,
    "mae": 0.223,
    "mape": 22.9
  },
  {
    "plt": "PLTS",
    "model": "LSTM_FineTuning",
    "rmse": 0.123,
    "mae": 0.104,
    "mape": 12.17
  },
  {
    "plt": "PLTS",
    "model": "Naive_Persistence",
    "rmse": 0.115,
    "mae": 0.095,
    "mape": 10.54
  },
  {
    "plt": "PLTS Atap",
    "model": "ARIMA(1, 1, 1)",
    "rmse": 0.165,
    "mae": 0.143,
    "mape": 14.45
  },
  {
    "plt": "PLTS Atap",
    "model": "LSTM_FineTuning",
    "rmse": 0.283,
    "mae": 0.241,
    "mape": 26.38
  },
  {
    "plt": "PLTS Atap",
    "model": "Naive_Persistence",
    "rmse": 0.138,
    "mae": 0.116,
    "mape": 11.59
  }
];

// Contoh baris data historis (real, hasil rekonstruksi) untuk halaman Data EBT
// -- diambil dari audit/source/DATA_PHASE_3_REGIONAL_MODIFIED.csv, BUKAN
// "data asli/terverifikasi" Dinas ESDM (lihat audit/source/README.md).
export const SAMPLE_MONTHLY_ROWS = [
  {
    "id": 1,
    "tanggal": "01 Jan 2023",
    "jenis": "PLT Hybrid",
    "produksi": 0.21,
    "kapasitas": 1.704,
    "cuaca": 4.2
  },
  {
    "id": 2,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTA",
    "produksi": 37.594,
    "kapasitas": 653.4,
    "cuaca": 290.0
  },
  {
    "id": 3,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTB",
    "produksi": 54.325,
    "kapasitas": 130.0,
    "cuaca": 3.74
  },
  {
    "id": 4,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTM",
    "produksi": 36.972,
    "kapasitas": 64.23,
    "cuaca": 290.0
  },
  {
    "id": 5,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTMH",
    "produksi": 22.827,
    "kapasitas": 39.66,
    "cuaca": 290.0
  },
  {
    "id": 6,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTS",
    "produksi": 0.631,
    "kapasitas": 5.14,
    "cuaca": 4.66
  },
  {
    "id": 7,
    "tanggal": "01 Jan 2023",
    "jenis": "PLTS Atap",
    "produksi": 0.023,
    "kapasitas": 0.19,
    "cuaca": 4.66
  },
  {
    "id": 8,
    "tanggal": "01 Feb 2023",
    "jenis": "PLT Hybrid",
    "produksi": 0.209,
    "kapasitas": 1.704,
    "cuaca": 4.057
  }
];
