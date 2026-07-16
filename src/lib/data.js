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

export const TARGET_RUED_PER_PLT = {
  2026: { PLTA: 430, PLTB: 600, PLTM: 380, PLTMH: 210, PLTS: 14, 'PLTS Atap': 12,   'PLT Hybrid': 3 },
  2027: { PLTA: 450, PLTB: 620, PLTM: 390, PLTMH: 215, PLTS: 15, 'PLTS Atap': 12.5, 'PLT Hybrid': 3 },
  2028: { PLTA: 470, PLTB: 640, PLTM: 400, PLTMH: 220, PLTS: 16, 'PLTS Atap': 13,   'PLT Hybrid': 3 },
};

export const ANNUAL_ACTUAL = [
  { year: 2022, total: 850 },
  { year: 2023, total: 980 },
  { year: 2024, total: 1250 },
  { year: 2025, total: 1320 },
];

export const ANNUAL_FORECAST = [
  { year: 2026, total: 1635.96, yoy: null },
  { year: 2027, total: 1609.86, yoy: -1.60 },
  { year: 2028, total: 1608.91, yoy: -0.06 },
];

export const TREND_ANNUAL = [
  { year: 2022, aktual: 850,    prediksi: null },
  { year: 2023, aktual: 980,    prediksi: null },
  { year: 2024, aktual: 1250,   prediksi: null },
  { year: 2025, aktual: 1320,   prediksi: 1320 },
  { year: 2026, aktual: null,   prediksi: 1635.96 },
  { year: 2027, aktual: null,   prediksi: 1609.86 },
  { year: 2028, aktual: null,   prediksi: 1608.91 },
];

export const PER_JENIS_2026 = [
  { jenis: 'PLTB',        produksi: 640.70, pct: 39.2, yoy: -3.8 },
  { jenis: 'PLTA',        produksi: 399.27, pct: 24.4, yoy:  7.8 },
  { jenis: 'PLTM',        produksi: 355.25, pct: 21.7, yoy: -0.5 },
  { jenis: 'PLTMH',       produksi: 212.16, pct: 13.0, yoy:  2.9 },
  { jenis: 'PLTS Atap',   produksi:  13.48, pct:  0.8, yoy: 58.6 },
  { jenis: 'PLTS',        produksi:  12.56, pct:  0.8, yoy: 24.7 },
  { jenis: 'PLT Hybrid',  produksi:   2.56, pct:  0.2, yoy: -7.4 },
];

export const MODEL_RMSE = {
  TOTAL:        2.2,
  PLTA:         2.9,
  PLTB:         4.6,
  PLTM:         3.1,
  PLTMH:        2.5,
  PLTS:         3.8,
  'PLTS Atap':  5.2,
  'PLT Hybrid': 6.1,
};

// Actual monthly forecast data from forecast/forecast_total_2026_2028.csv
// 36 values: Jan 2026 (idx 0) → Dec 2028 (idx 35)
export const MONTHLY_FORECAST_TOTAL = [
  // 2026
  150.23863, 151.16641, 145.12059, 135.27922, 128.34311, 127.88644,
  130.24901, 130.77135, 132.42534, 134.16420, 135.11577, 135.20090,
  // 2027
  134.95865, 134.70476, 134.30800, 133.98312, 133.83362, 133.82720,
  133.88170, 133.95767, 134.04431, 134.10458, 134.12872, 134.12683,
  // 2028
  134.11235, 134.09329, 134.07542, 134.06447, 134.06088, 134.06229,
  134.06613, 134.07057, 134.07416, 134.07613, 134.07658, 134.07603,
];

// Actual monthly forecast per PLT type from forecast/forecast_per_PLT_2026_2028.csv
// Each array: 36 values Jan 2026 (idx 0) → Dec 2028 (idx 35)
export const MONTHLY_FORECAST_PER_PLT = {
  PLTA: [
    41.746777, 42.16982,  38.609924, 32.92266,  28.625366, 28.011961,
    29.163103, 29.640081, 30.857939, 32.06877,  32.709324, 32.74393,
    32.543423, 32.32275,  32.021095, 31.789244, 31.690418, 31.696619,
    31.748152, 31.814007, 31.881327, 31.924662, 31.93937,  31.934185,
    31.919815, 31.903103, 31.888922, 31.881035, 31.879213, 31.881323,
    31.885147, 31.889053, 31.891935, 31.893305, 31.893393, 31.892706,
  ],
  PLTB: [
    54.131683, 54.202103, 53.65461,  52.87772,  52.64881,  52.982967,
    53.380333, 53.375984, 53.366444, 53.35917,  53.359188, 53.363388,
    53.36637,  53.36627,  53.36615,  53.36609,  53.36611,  53.366154,
    53.366177, 53.366177, 53.366173, 53.366173, 53.366173, 53.366173,
    53.366177, 53.366177, 53.366177, 53.366177, 53.366177, 53.366173,
    53.366173, 53.366173, 53.366173, 53.366177, 53.366177, 53.366177,
  ],
  PLTM: [
    30.60784,  30.619453, 30.10638,  29.412928, 29.005022, 29.087791,
    29.362167, 29.373634, 29.399107, 29.420818, 29.428158, 29.423542,
    29.417826, 29.417088, 29.416136, 29.415543, 29.415438, 29.41559,
    29.41572,  29.415754, 29.415783, 29.415798, 29.415798, 29.415794,
    29.415792, 29.415789, 29.415789, 29.415789, 29.415789, 29.415789,
    29.415789, 29.415789, 29.415789, 29.415789, 29.415789, 29.415789,
  ],
  PLTMH: [
    21.35376,  21.758392, 20.341667, 17.679981, 15.703908, 15.444764,
    15.966024, 16.00523,  16.426395, 16.94019,  17.242973, 17.292244,
    17.251884, 17.219332, 17.124985, 17.032228, 16.98124,  16.968082,
    16.970692, 16.980652, 16.999823, 17.016619, 17.025965, 17.029186,
    17.029026, 17.02664,  17.022924, 17.019829, 17.018026, 17.017311,
    17.017332, 17.017843, 17.01855,  17.019135, 17.01949,  17.019636,
  ],
  PLTS: [
    1.0424463, 1.0422477, 1.0373201, 1.0333842, 1.0325042, 1.0400866,
    1.0534304, 1.0532736, 1.0533935, 1.0542383, 1.0557287, 1.0575666,
    1.0589129, 1.059152,  1.0594964, 1.0599145, 1.0603288, 1.0606657,
    1.0608776, 1.0609972, 1.061121,  1.0612351, 1.0613288, 1.0613981,
    1.0614471, 1.0614849, 1.0615185, 1.0615463, 1.0615678, 1.0615841,
    1.0615968, 1.0616069, 1.0616152, 1.061622,  1.0616271, 1.0616312,
  ],
  'PLTS Atap': [
    1.1460159, 1.1662351, 1.1605599, 1.140884,  1.113216,  1.1041163,
    1.110216,  1.1092381, 1.107766,  1.1064563, 1.1056365, 1.1054673,
    1.1054969, 1.1053761, 1.1052793, 1.1052184, 1.1051887, 1.1051779,
    1.1051705, 1.1051625, 1.1051571, 1.105154,  1.1051526, 1.1051517,
    1.1051509, 1.1051505, 1.1051502, 1.10515,   1.1051499, 1.1051497,
    1.1051497, 1.1051497, 1.1051497, 1.1051497, 1.1051497, 1.1051497,
  ],
  'PLT Hybrid': [
    0.21010977, 0.20816225, 0.21012254, 0.21166757, 0.21427666, 0.21474531,
    0.21373607, 0.2139074,  0.21428594, 0.21456285, 0.21475534, 0.21476087,
    0.21473417, 0.21479386, 0.21485049, 0.21488522, 0.21490307, 0.21490858,
    0.2149155,  0.21492644, 0.21493442, 0.21493916, 0.21494198, 0.21494393,
    0.21494588, 0.21494766, 0.21494886, 0.21494967, 0.21495022, 0.21495067,
    0.21495104, 0.21495134, 0.21495155, 0.21495168, 0.2149518,  0.21495189,
  ],
};

// Real data historis (first 8 rows from data/data_historis_ebt.csv)
export const SAMPLE_MONTHLY_ROWS = [
  { id: 1, tanggal: '01 Jan 2023', jenis: 'PLT Hybrid',  produksi: 0.258,  kapasitas: 1.704,    cuaca: 4.943 },
  { id: 2, tanggal: '01 Jan 2023', jenis: 'PLTA',        produksi: 35.484, kapasitas: 681.345,  cuaca: 238.866 },
  { id: 3, tanggal: '01 Jan 2023', jenis: 'PLTB',        produksi: 55.582, kapasitas: 136.481,  cuaca: 3.609 },
  { id: 4, tanggal: '01 Jan 2023', jenis: 'PLTM',        produksi: 30.491, kapasitas: 65.419,   cuaca: 233.458 },
  { id: 5, tanggal: '01 Jan 2023', jenis: 'PLTMH',       produksi: 18.824, kapasitas: 39.66,    cuaca: 232.464 },
  { id: 6, tanggal: '01 Jan 2023', jenis: 'PLTS',        produksi: 0.974,  kapasitas: 5.68,     cuaca: 5.952 },
  { id: 7, tanggal: '01 Jan 2023', jenis: 'PLTS Atap',   produksi: 0.936,  kapasitas: 3.422,    cuaca: 6.055 },
  { id: 8, tanggal: '01 Feb 2023', jenis: 'PLT Hybrid',  produksi: 0.256,  kapasitas: 1.704,    cuaca: 5.172 },
];
