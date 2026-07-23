// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: 2026-07-23 22:30
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
    "total": 1636.32,
    "yoy": null
  },
  {
    "year": 2027,
    "total": 1611.23,
    "yoy": -1.53
  },
  {
    "year": 2028,
    "total": 1609.93,
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
    "prediksi": 1636.32
  },
  {
    "year": 2027,
    "aktual": null,
    "prediksi": 1611.23
  },
  {
    "year": 2028,
    "aktual": null,
    "prediksi": 1609.93
  }
];

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = [
  {
    "jenis": "PLTB",
    "produksi": 639.6,
    "pct": 39.1,
    "yoy": -0.2
  },
  {
    "jenis": "PLTA",
    "produksi": 402.86,
    "pct": 24.6,
    "yoy": 3.3
  },
  {
    "jenis": "PLTM",
    "produksi": 352.78,
    "pct": 21.6,
    "yoy": -1.8
  },
  {
    "jenis": "PLTMH",
    "produksi": 212.36,
    "pct": 13.0,
    "yoy": 3.6
  },
  {
    "jenis": "PLTS Atap",
    "produksi": 13.63,
    "pct": 0.8,
    "yoy": 11.8
  },
  {
    "jenis": "PLTS",
    "produksi": 12.6,
    "pct": 0.8,
    "yoy": 16.1
  },
  {
    "jenis": "PLT Hybrid",
    "produksi": 2.49,
    "pct": 0.2,
    "yoy": -4.5
  }
];

// MAPE (Mean Absolute Percentage Error, %) model LSTM tahap Fine-Tuning per
// jenis PLT -- dipakai sebagai basis "akurasi model" (100% - MAPE).
export const MODEL_RMSE = {
  "PLT Hybrid": 11.3,
  "PLTA": 8.9,
  "PLTB": 23.6,
  "PLTM": 10.6,
  "PLTMH": 10.9,
  "PLTS": 11.5,
  "PLTS Atap": 28.0,
  "TOTAL": 15.0
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
  150.52223,
  151.28438,
  144.96239,
  135.36958,
  128.93884,
  128.4216,
  130.18735,
  130.44212,
  132.0245,
  133.84991,
  134.99727,
  135.3211,
  135.25095,
  135.01898,
  134.56241,
  134.14404,
  133.90286,
  133.82896,
  133.85526,
  133.94508,
  134.06992,
  134.17244,
  134.2299,
  134.24632,
  134.23416,
  134.20486,
  134.17123,
  134.14554,
  134.13193,
  134.12927,
  134.1344,
  134.14352,
  134.1528,
  134.15948,
  134.16277,
  134.16302
];

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {
  "PLTA": [
    42.142418,
    42.667297,
    39.175247,
    33.72158,
    29.548769,
    28.518747,
    28.956116,
    29.271679,
    30.59483,
    32.062435,
    32.973137,
    33.22615,
    33.154892,
    32.924755,
    32.51293,
    32.141884,
    31.927265,
    31.862038,
    31.890728,
    31.979837,
    32.09818,
    32.194065,
    32.247242,
    32.2614,
    32.24809,
    32.218597,
    32.18557,
    32.160557,
    32.147415,
    32.145035,
    32.150265,
    32.15934,
    32.168472,
    32.17501,
    32.17817,
    32.178333
  ],
  "PLTB": [
    54.607395,
    54.486343,
    53.467865,
    52.287125,
    52.056866,
    52.72471,
    53.391243,
    53.351254,
    53.306595,
    53.287045,
    53.302986,
    53.33142,
    53.346302,
    53.344345,
    53.343323,
    53.343647,
    53.344772,
    53.345726,
    53.346043,
    53.34599,
    53.345993,
    53.34604,
    53.34609,
    53.34612,
    53.346123,
    53.346123,
    53.346127,
    53.346127,
    53.34613,
    53.34613,
    53.34613,
    53.34613,
    53.34613,
    53.34613,
    53.34613,
    53.34613
  ],
  "PLTM": [
    30.065632,
    30.044811,
    29.69511,
    29.253025,
    29.00719,
    29.067343,
    29.250393,
    29.259977,
    29.275589,
    29.28752,
    29.290705,
    29.28734,
    29.283678,
    29.283161,
    29.282648,
    29.28238,
    29.282372,
    29.282482,
    29.28256,
    29.28258,
    29.282597,
    29.282602,
    29.282602,
    29.282597,
    29.282595,
    29.282595,
    29.282595,
    29.282595,
    29.282593,
    29.282593,
    29.282595,
    29.282595,
    29.282595,
    29.282595,
    29.282595,
    29.282595
  ],
  "PLTMH": [
    21.304663,
    21.66031,
    20.201126,
    17.705467,
    15.953506,
    15.744136,
    16.20712,
    16.175606,
    16.461763,
    16.825094,
    17.04063,
    17.084738,
    17.073185,
    17.07263,
    17.028177,
    16.979809,
    16.951397,
    16.941116,
    16.937817,
    16.938076,
    16.944122,
    16.950384,
    16.954372,
    16.956404,
    16.957338,
    16.957357,
    16.956614,
    16.955814,
    16.955238,
    16.954882,
    16.954702,
    16.95468,
    16.954763,
    16.954865,
    16.954948,
    16.955006
  ],
  "PLTS": [
    1.043514,
    1.040736,
    1.036025,
    1.034099,
    1.036031,
    1.04499,
    1.058245,
    1.058348,
    1.059141,
    1.060732,
    1.062804,
    1.064945,
    1.066468,
    1.066948,
    1.067543,
    1.068169,
    1.068734,
    1.069179,
    1.069482,
    1.069691,
    1.069892,
    1.070066,
    1.070207,
    1.070314,
    1.070395,
    1.070461,
    1.070518,
    1.070564,
    1.0706,
    1.070629,
    1.070652,
    1.07067,
    1.070686,
    1.070698,
    1.070708,
    1.070716
  ],
  "PLTS Atap": [
    1.16046,
    1.193167,
    1.189282,
    1.163278,
    1.123061,
    1.108652,
    1.116926,
    1.116761,
    1.115632,
    1.114299,
    1.113326,
    1.113149,
    1.113283,
    1.113232,
    1.113172,
    1.113126,
    1.113104,
    1.113101,
    1.113102,
    1.113099,
    1.113096,
    1.113095,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094,
    1.113094
  ],
  "PLT Hybrid": [
    0.198146,
    0.191719,
    0.197737,
    0.20501,
    0.213423,
    0.213027,
    0.207307,
    0.208496,
    0.210961,
    0.212784,
    0.213681,
    0.213356,
    0.213138,
    0.213909,
    0.214613,
    0.215026,
    0.215221,
    0.215327,
    0.215531,
    0.215821,
    0.216038,
    0.216183,
    0.216295,
    0.216405,
    0.216523,
    0.216634,
    0.216721,
    0.216791,
    0.216855,
    0.216914,
    0.21697,
    0.217018,
    0.217058,
    0.217093,
    0.217126,
    0.217155
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
    "mae": 0.025,
    "mape": 11.32
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
    "rmse": 3.33,
    "mae": 2.65,
    "mape": 8.94
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
    "rmse": 13.232,
    "mae": 11.252,
    "mape": 23.62
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
    "rmse": 3.505,
    "mae": 2.702,
    "mape": 10.59
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
    "rmse": 2.003,
    "mae": 1.773,
    "mape": 10.88
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
    "rmse": 0.118,
    "mae": 0.101,
    "mape": 11.52
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
    "rmse": 0.304,
    "mae": 0.255,
    "mape": 27.96
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
