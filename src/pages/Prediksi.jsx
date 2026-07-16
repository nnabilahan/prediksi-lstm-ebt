import { useState, useMemo } from 'react';
import { Play, Cpu, BarChart2, TrendingUp, Percent } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Gauge from '../components/ui/Gauge';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import MonthlyChart from '../components/charts/MonthlyChart';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt, buildMonthlyFromReal } from '../lib/utils';
import {
  ANNUAL_ACTUAL, ANNUAL_FORECAST, PER_JENIS_2026,
  PLANT_KEYS, PLANT_META, MODEL_RMSE,
  MONTHLY_FORECAST_TOTAL, MONTHLY_FORECAST_PER_PLT,
} from '../lib/data';

const REAL_DATA_PARAMS = {
  annualActual: ANNUAL_ACTUAL,
  annualForecast: ANNUAL_FORECAST,
  perJenis2026: PER_JENIS_2026,
  monthlyForecastTotal: MONTHLY_FORECAST_TOTAL,
  monthlyForecastPerPlt: MONTHLY_FORECAST_PER_PLT,
};

export default function Prediksi() {
  const [plant, setPlant] = useState('TOTAL');
  const [mode, setMode] = useState('rentang');
  const [y0, setY0] = useState(2026);
  const [y1, setY1] = useState(2028);

  const monthly = useMemo(
    () => buildMonthlyFromReal(plant, REAL_DATA_PARAMS),
    [plant]
  );

  const yearly = useMemo(() => {
    const map = {};
    monthly.forEach(r => {
      if (!map[r.year]) map[r.year] = { year: r.year, aktualSum: 0, prediksiSum: 0, hasAktual: false, hasPrediksi: false };
      if (r.aktual != null) { map[r.year].aktualSum += r.aktual; map[r.year].hasAktual = true; }
      if (r.prediksi != null) { map[r.year].prediksiSum += r.prediksi; map[r.year].hasPrediksi = true; }
    });
    return Object.values(map).sort((a, b) => a.year - b.year);
  }, [monthly]);

  const selectedRows = useMemo(() => {
    if (mode === 'tunggal') return yearly.filter(r => r.year === y1);
    return yearly.filter(r => r.year >= y0 && r.year <= y1);
  }, [yearly, mode, y0, y1]);

  const totalPred = useMemo(
    () => selectedRows.reduce((s, r) => s + (r.hasPrediksi ? r.prediksiSum : r.aktualSum), 0),
    [selectedRows]
  );
  const avgPred = selectedRows.length > 0 ? totalPred / selectedRows.length : 0;
  const endRow = selectedRows[selectedRows.length - 1];
  const endPred = endRow ? (endRow.hasPrediksi ? endRow.prediksiSum : endRow.aktualSum) : 0;
  const rmse = MODEL_RMSE[plant] ?? MODEL_RMSE.TOTAL;
  const accuracy = 100 - rmse;

  const plantLabel = plant === 'TOTAL' ? 'Semua Jenis PLT' : (PLANT_META[plant]?.label ?? plant);
  const periodLabel = mode === 'rentang' ? `${y0}–${y1}` : String(y1);

  // Table rows with YoY
  const tableRows = useMemo(() => {
    return yearly.map((r, i) => {
      const prev = yearly[i - 1];
      const curVal = r.hasPrediksi ? r.prediksiSum : (r.hasAktual ? r.aktualSum : null);
      const prevVal = prev ? (prev.hasPrediksi ? prev.prediksiSum : prev.aktualSum) : null;
      const yoy = (curVal != null && prevVal != null && prevVal !== 0)
        ? ((curVal - prevVal) / prevVal) * 100
        : null;
      return { ...r, curVal, yoy, isPred: r.hasPrediksi };
    });
  }, [yearly]);

  return (
    <>
      <PageHead
        title="Prediksi Energi Baru Terbarukan"
        desc="Jalankan inferensi model LSTM yang sudah dilatih untuk memperkirakan produksi EBT per jenis pembangkit. Halaman ini tidak melakukan pelatihan ulang — lihat Gap Analysis untuk evaluasi terhadap RUED."
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        {/* Form panel */}
        <Panel className="lg:col-span-4" title="Form input prediksi">
          <div className="flex flex-col gap-3 h-full">
            <Field label="Jenis pembangkit">
              <select
                style={inputStyle()}
                value={plant}
                onChange={e => setPlant(e.target.value)}
              >
                <option value="TOTAL">Seluruh jenis PLT (total)</option>
                {PLANT_KEYS.map(k => (
                  <option key={k} value={k}>{PLANT_META[k].label}</option>
                ))}
              </select>
            </Field>

            <Field label="Mode periode">
              <div className="flex gap-3">
                {['rentang', 'tunggal'].map(m => (
                  <label key={m} className="flex items-center gap-1.5 cursor-pointer text-xs" style={{ color: C.ink }}>
                    <input
                      type="radio"
                      name="mode"
                      value={m}
                      checked={mode === m}
                      onChange={() => setMode(m)}
                      style={{ accentColor: C.green }}
                    />
                    {m === 'rentang' ? 'Rentang tahun' : 'Tahun tertentu'}
                  </label>
                ))}
              </div>
            </Field>

            {mode === 'rentang' ? (
              <div className="grid grid-cols-2 gap-3">
                <Field label="Tahun awal">
                  <select style={inputStyle()} value={y0} onChange={e => setY0(Number(e.target.value))}>
                    <option value={2026}>2026</option>
                    <option value={2027}>2027</option>
                  </select>
                </Field>
                <Field label="Tahun akhir">
                  <select style={inputStyle()} value={y1} onChange={e => setY1(Number(e.target.value))}>
                    <option value={2026}>2026</option>
                    <option value={2027}>2027</option>
                    <option value={2028}>2028</option>
                  </select>
                </Field>
              </div>
            ) : (
              <Field label="Pilih tahun">
                <select style={inputStyle()} value={y1} onChange={e => setY1(Number(e.target.value))}>
                  <option value={2026}>2026</option>
                  <option value={2027}>2027</option>
                  <option value={2028}>2028</option>
                </select>
              </Field>
            )}

            <button
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium mt-1"
              style={{ background: C.green, color: '#fff', fontFamily: "'Inter', sans-serif" }}
            >
              <Play size={14} fill="#fff" />
              Prediksi produksi EBT
            </button>

            <div className="mt-auto pt-3 border-t" style={{ borderColor: C.line }}>
              <Gauge value={accuracy} size={168} label={`Akurasi model — RMSE ${fmt(rmse, 1)}%`} />
            </div>
          </div>
        </Panel>

        {/* Right column */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Stat label="Jenis pembangkit" value={plant === 'TOTAL' ? 'Semua' : plant} icon={Cpu} />
            <Stat
              label={`Total ${periodLabel}`}
              value={fmt(totalPred, 2)}
              unit="GWh"
              sub={`Rata-rata ${fmt(avgPred, 2)} GWh/tahun`}
              icon={BarChart2}
            />
            <Stat
              label={`Prediksi ${y1}`}
              value={fmt(endPred, 2)}
              unit="GWh"
              icon={TrendingUp}
            />
            <Stat
              label="RMSE model"
              value={fmt(rmse, 1)}
              unit="%"
              icon={Percent}
              tip="Root Mean Square Error — semakin kecil, prediksi semakin mendekati nilai aktual."
            />
          </div>
          <Panel
            title={`Grafik aktual vs prediksi — ${plantLabel}`}
            subtitle="Satuan GWh, granularitas bulanan 2023–2028"
          >
            <MonthlyChart data={monthly} height={252} />
          </Panel>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel className="lg:col-span-7" title="Detail prediksi per tahun" noPad>
          <DataTable
            minWidth={440}
            cols={[
              { label: 'Tahun', width: '18%' },
              { label: 'Aktual (GWh)', width: '28%', align: 'right' },
              { label: 'Prediksi (GWh)', width: '28%', align: 'right' },
              { label: 'Perubahan YoY', width: '26%', align: 'right' },
            ]}
            rows={tableRows.map((r) => (
              <tr key={r.year} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td mono>{r.year}</Td>
                <Td align="right" mono>
                  {r.hasAktual ? fmt(r.aktualSum, 2) : '—'}
                </Td>
                <Td align="right" mono color={r.hasPrediksi ? C.blue : undefined}>
                  {r.hasPrediksi ? fmt(r.prediksiSum, 2) : '—'}
                </Td>
                <Td align="right" mono color={r.yoy == null ? C.faint : r.yoy >= 0 ? C.ok : C.red}>
                  {r.yoy == null ? '—' : `${r.yoy >= 0 ? '+' : ''}${fmt(r.yoy, 2)}%`}
                </Td>
              </tr>
            ))}
          />
        </Panel>

        <Panel className="lg:col-span-5" title="Insight otomatis">
          <div className="space-y-3">
            <Note tone="info">
              Model LSTM memprediksi total produksi EBT sebesar <strong>{fmt(totalPred, 2)} GWh</strong> untuk periode {periodLabel}. Rata-rata tahunan {fmt(avgPred, 2)} GWh.
            </Note>
            <Note tone="info">
              Jenis pembangkit yang dipilih: <strong>{plantLabel}</strong>. RMSE model {fmt(rmse, 1)}% menunjukkan tingkat kesalahan prediksi relatif terhadap nilai aktual.
            </Note>
            <Note tone="warn">
              Nilai prediksi bersifat informatif dan dapat berubah jika data historis diperbarui atau model dilatih ulang dengan parameter berbeda.
            </Note>
          </div>
        </Panel>
      </div>

      <Footer />
    </>
  );
}
