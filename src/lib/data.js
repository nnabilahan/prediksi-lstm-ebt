// AUTO-GENERATED oleh audit/analysis/export_dashboard_data.py -- JANGAN EDIT MANUAL.
// Dibuat ulang: 2026-07-26 14:18
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
    "total": 1669.99,
    "yoy": null
  },
  {
    "year": 2027,
    "total": 1604.38,
    "yoy": -3.93
  },
  {
    "year": 2028,
    "total": 1610.4,
    "yoy": 0.38
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
    "prediksi": 1669.99
  },
  {
    "year": 2027,
    "aktual": null,
    "prediksi": 1604.38
  },
  {
    "year": 2028,
    "aktual": null,
    "prediksi": 1610.4
  }
];

// Forecast per jenis PLT tahun 2026 (GWh), diurutkan produksi terbesar.
export const PER_JENIS_2026 = [
  {
    "jenis": "PLTB",
    "produksi": 654.95,
    "pct": 39.2,
    "yoy": 2.2
  },
  {
    "jenis": "PLTA",
    "produksi": 402.36,
    "pct": 24.1,
    "yoy": 3.2
  },
  {
    "jenis": "PLTM",
    "produksi": 363.62,
    "pct": 21.8,
    "yoy": 1.2
  },
  {
    "jenis": "PLTMH",
    "produksi": 216.68,
    "pct": 13.0,
    "yoy": 5.7
  },
  {
    "jenis": "PLTS",
    "produksi": 15.37,
    "pct": 0.9,
    "yoy": 41.7
  },
  {
    "jenis": "PLTS Atap",
    "produksi": 14.39,
    "pct": 0.9,
    "yoy": 18.1
  },
  {
    "jenis": "PLT Hybrid",
    "produksi": 2.62,
    "pct": 0.2,
    "yoy": 0.7
  }
];

// MAPE (Mean Absolute Percentage Error, %) model LSTM tahap Fine-Tuning per
// jenis PLT -- dipakai sebagai basis "akurasi model" (100% - MAPE).
export const MODEL_RMSE = {
  "PLT Hybrid": 11.6,
  "PLTS": 11.4,
  "PLTS Atap": 28.9,
  "PLTMH": 11.3,
  "PLTM": 9.9,
  "PLTA": 9.2,
  "PLTB": 25.5,
  "TOTAL": 15.4
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
  155.72467,
  167.85654,
  159.00885,
  146.07599,
  132.0507,
  119.506,
  119.51674,
  123.574615,
  130.37508,
  136.43933,
  139.87529,
  139.99042,
  136.80493,
  133.4742,
  131.70709,
  131.67435,
  132.67764,
  133.87532,
  134.63503,
  134.60501,
  134.04398,
  133.53995,
  133.4851,
  133.85829,
  134.37329,
  134.71967,
  134.71729,
  134.38495,
  133.92471,
  133.5941,
  133.54585,
  133.76035,
  134.09337,
  134.37405,
  134.4895,
  134.42546
];

// Forecast bulanan per jenis PLT (GWh), 36 nilai per PLT: Jan 2026 -> Des 2028.
export const MONTHLY_FORECAST_PER_PLT = {
  "PLTA": [
    41.790478,
    42.07588,
    38.64454,
    33.221516,
    29.276285,
    28.973768,
    30.374788,
    30.546318,
    31.20703,
    31.864702,
    32.188145,
    32.19219,
    32.105488,
    32.048927,
    31.957035,
    31.886843,
    31.857073,
    31.855139,
    31.86243,
    31.871967,
    31.883167,
    31.890669,
    31.893793,
    31.894156,
    31.893297,
    31.891973,
    31.890673,
    31.889845,
    31.8895,
    31.889452,
    31.889565,
    31.889732,
    31.889883,
    31.889977,
    31.890018,
    31.890018
  ],
  "PLTB": [
    52.78005,
    63.990734,
    62.669186,
    61.82567,
    56.911865,
    46.00775,
    44.069916,
    47.408398,
    51.680973,
    54.97123,
    56.589447,
    56.04106,
    52.92651,
    50.183735,
    49.393795,
    50.276974,
    51.86907,
    53.26569,
    53.88471,
    53.470425,
    52.425556,
    51.49842,
    51.176643,
    51.468494,
    52.065865,
    52.599163,
    52.80898,
    52.64666,
    52.275433,
    51.94442,
    51.823578,
    51.92671,
    52.146946,
    52.343147,
    52.417885,
    52.357437
  ],
  "PLTM": [
    37.20395,
    37.52354,
    34.532642,
    30.147919,
    26.82216,
    25.568268,
    25.40635,
    26.073074,
    27.832458,
    29.740984,
    31.087074,
    31.677998,
    31.633257,
    31.047556,
    30.135857,
    29.275604,
    28.698109,
    28.477299,
    28.587616,
    28.942415,
    29.394808,
    29.790184,
    30.034693,
    30.097795,
    30.000992,
    29.803337,
    29.581469,
    29.402296,
    29.304537,
    29.296803,
    29.362038,
    29.466843,
    29.573805,
    29.653196,
    29.689482,
    29.68212
  ],
  "PLTMH": [
    21.481005,
    21.741743,
    20.565998,
    18.25597,
    16.377491,
    16.250713,
    16.906755,
    16.746798,
    16.848993,
    17.061663,
    17.209824,
    17.237846,
    17.232706,
    17.258226,
    17.256147,
    17.243633,
    17.234789,
    17.232052,
    17.230108,
    17.227304,
    17.22683,
    17.22724,
    17.22756,
    17.227705,
    17.227919,
    17.228155,
    17.228231,
    17.228243,
    17.228252,
    17.228254,
    17.228241,
    17.228226,
    17.22822,
    17.228214,
    17.228212,
    17.22821
  ],
  "PLTS": [
    1.12479,
    1.146151,
    1.176854,
    1.19389,
    1.218556,
    1.250015,
    1.289179,
    1.328488,
    1.359383,
    1.390079,
    1.423931,
    1.472424,
    1.530065,
    1.558256,
    1.586719,
    1.614228,
    1.642267,
    1.669737,
    1.695799,
    1.719699,
    1.741529,
    1.762093,
    1.781364,
    1.799046,
    1.814069,
    1.825965,
    1.836964,
    1.847035,
    1.856224,
    1.864474,
    1.871801,
    1.878267,
    1.883972,
    1.888999,
    1.893385,
    1.897165
  ],
  "PLTS Atap": [
    1.129965,
    1.163098,
    1.202515,
    1.211595,
    1.222087,
    1.232492,
    1.244624,
    1.247007,
    1.22577,
    1.195794,
    1.164592,
    1.155295,
    1.16077,
    1.161255,
    1.161268,
    1.160833,
    1.160249,
    1.15955,
    1.158773,
    1.157935,
    1.157131,
    1.156545,
    1.156228,
    1.156167,
    1.156172,
    1.156127,
    1.156076,
    1.156025,
    1.155977,
    1.155936,
    1.155903,
    1.155877,
    1.155859,
    1.155848,
    1.155842,
    1.155838
  ],
  "PLT Hybrid": [
    0.21443,
    0.215386,
    0.21711,
    0.219426,
    0.222255,
    0.222991,
    0.22513,
    0.224532,
    0.220474,
    0.214877,
    0.212281,
    0.213606,
    0.216135,
    0.216234,
    0.21627,
    0.216224,
    0.216087,
    0.215848,
    0.215586,
    0.215258,
    0.214958,
    0.214799,
    0.214825,
    0.214928,
    0.214978,
    0.214938,
    0.214893,
    0.214846,
    0.214799,
    0.214756,
    0.214721,
    0.214695,
    0.214679,
    0.214673,
    0.21467,
    0.214666
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
    "rmse": 0.03,
    "mae": 0.025,
    "mape": 11.57
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
    "rmse": 3.411,
    "mae": 2.746,
    "mape": 9.24
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
    "rmse": 13.87,
    "mae": 11.996,
    "mape": 25.5
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
    "rmse": 3.345,
    "mae": 2.551,
    "mape": 9.94
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
    "rmse": 2.038,
    "mae": 1.857,
    "mape": 11.32
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
    "rmse": 0.119,
    "mae": 0.1,
    "mape": 11.43
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
    "rmse": 0.313,
    "mae": 0.262,
    "mape": 28.94
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
