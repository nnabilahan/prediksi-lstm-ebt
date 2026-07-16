export function fmt(n, d = 1) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—';
  return n.toLocaleString('id-ID', {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });
}

// Legacy sinusoidal builder — kept for reference, not used in pages anymore
export function buildMonthly(plant, annualActual, annualForecast, perJenis2026) {
  const allYears = [...annualActual, ...annualForecast];
  const anchors = Object.fromEntries(allYears.map(r => [r.year, r.total]));
  const totalForecast2026 = annualForecast.find(r => r.year === 2026)?.total ?? 1635.96;
  const shareMap = {
    TOTAL: 1,
    ...Object.fromEntries(perJenis2026.map(r => [r.jenis, r.produksi / totalForecast2026])),
  };
  const share = shareMap[plant] ?? 1;
  const rows = [];
  [2023, 2024, 2025, 2026, 2027, 2028].forEach(year => {
    const meanMonthly = (anchors[year] * share) / 12;
    const amplitude = year <= 2025
      ? meanMonthly * 0.18
      : year === 2026 ? meanMonthly * 0.12
      : meanMonthly * 0.04;
    for (let m = 0; m < 12; m++) {
      const v = meanMonthly + amplitude * Math.sin((2 * Math.PI * (m - 2)) / 12);
      const isActual = year <= 2025;
      const isBridge = year === 2025 && m === 11;
      rows.push({
        label: `${year}-${String(m + 1).padStart(2, '0')}`,
        year, month: m + 1,
        aktual: isActual ? v : null,
        prediksi: !isActual || isBridge ? v : null,
      });
    }
  });
  return rows;
}

// Builds monthly series using real forecast data for 2026–2028,
// and sinusoidal approximation for historical years 2023–2025.
export function buildMonthlyFromReal(plant, {
  annualActual,
  annualForecast,
  perJenis2026,
  monthlyForecastTotal,
  monthlyForecastPerPlt,
}) {
  const totalForecast2026 = annualForecast.find(r => r.year === 2026)?.total ?? 1635.96;
  const shareMap = {
    TOTAL: 1,
    ...Object.fromEntries(perJenis2026.map(r => [r.jenis, r.produksi / totalForecast2026])),
  };
  const share = shareMap[plant] ?? 1;
  const anchors = Object.fromEntries(annualActual.map(r => [r.year, r.total]));

  const rows = [];

  // Historical years: sinusoidal approximation
  [2023, 2024, 2025].forEach(year => {
    const meanMonthly = ((anchors[year] ?? 0) * share) / 12;
    const amplitude = meanMonthly * 0.18;
    for (let m = 0; m < 12; m++) {
      const v = meanMonthly + amplitude * Math.sin((2 * Math.PI * (m - 2)) / 12);
      const isBridge = year === 2025 && m === 11;
      rows.push({
        label: `${year}-${String(m + 1).padStart(2, '0')}`,
        year, month: m + 1,
        aktual: v,
        prediksi: isBridge ? v : null,
      });
    }
  });

  // Forecast years: real data
  const monthlyData = plant === 'TOTAL' ? monthlyForecastTotal : monthlyForecastPerPlt[plant];

  [2026, 2027, 2028].forEach((year, yi) => {
    for (let m = 0; m < 12; m++) {
      const idx = yi * 12 + m;
      rows.push({
        label: `${year}-${String(m + 1).padStart(2, '0')}`,
        year, month: m + 1,
        aktual: null,
        prediksi: monthlyData ? (monthlyData[idx] ?? null) : null,
      });
    }
  });

  return rows;
}
