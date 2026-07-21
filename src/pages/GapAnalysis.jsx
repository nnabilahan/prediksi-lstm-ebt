import { useState } from 'react';
import { TrendingUp, BookOpen, AlertCircle, Globe } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import ForecastLineChart from '../components/charts/ForecastLineChart';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt } from '../lib/utils';
import { ANNUAL_FORECAST, PER_JENIS_2026, PLANT_KEYS, PLANT_META, MONTHLY_FORECAST_PER_PLT, RUED_TARGET, BASELINE_COMPARISON } from '../lib/data';

const [RUED_FROM, RUED_TO] = RUED_TARGET.anchors;

// Kelompokkan BASELINE_COMPARISON per PLT untuk panel "Pembanding Metode"
const BASELINE_BY_PLT = PLANT_KEYS.map(plt => {
  const rows = BASELINE_COMPARISON.filter(r => r.plt === plt);
  // Ranking pakai MAPE (bukan RMSE) supaya konsisten dengan angka yang ditampilkan di tabel.
  const best = rows.reduce((a, b) => (b.mape < a.mape ? b : a), rows[0]);
  return { plt, rows, best };
}).filter(g => g.rows.length > 0);

// Build per-PLT annual totals for 2027 and 2028 from monthly data
function perPltAnnual(plant, year) {
  const data = MONTHLY_FORECAST_PER_PLT[plant];
  if (!data) return null;
  const startIdx = (year - 2026) * 12;
  return data.slice(startIdx, startIdx + 12).reduce((s, v) => s + v, 0);
}

export default function GapAnalysis() {
  const [tahun, setTahun] = useState(2026);
  const [jenis, setJenis] = useState('total');
  const [plt, setPlt] = useState('PLTA');

  const forecastVal = jenis === 'total'
    ? ANNUAL_FORECAST.find(r => r.year === tahun)?.total
    : (tahun === 2026
        ? PER_JENIS_2026.find(r => r.jenis === plt)?.produksi
        : perPltAnnual(plt, tahun));

  const prevYear = tahun > 2026 ? tahun - 1 : null;
  const prevVal = prevYear
    ? (jenis === 'total'
        ? ANNUAL_FORECAST.find(r => r.year === prevYear)?.total
        : (prevYear === 2026
            ? PER_JENIS_2026.find(r => r.jenis === plt)?.produksi
            : perPltAnnual(plt, prevYear)))
    : null;

  const yoyPct = (forecastVal != null && prevVal != null && prevVal !== 0)
    ? ((forecastVal - prevVal) / prevVal) * 100
    : null;
  const yoyDir = yoyPct !== null ? (yoyPct >= 0 ? 'meningkat' : 'menurun') : null;

  const rowLabel = jenis === 'total' ? 'Seluruh Jenis PLT (Total EBT)' : plt;
  const konteks = jenis === 'total' ? 'seluruh jenis PLT' : plt;

  return (
    <>
      <PageHead
        title="Analisis Kesesuaian terhadap Target RUED"
        desc="Konteks kebijakan Perda Sulsel No. 2 Tahun 2022 — Rencana Umum Energi Daerah"
      />

      {/* Filter */}
      <Panel title="Filter analisis">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Field label="Periode / tahun">
            <select style={inputStyle()} value={tahun} onChange={e => setTahun(Number(e.target.value))}>
              <option value={2026}>2026</option>
              <option value={2027}>2027</option>
              <option value={2028}>2028</option>
            </select>
          </Field>
          <Field label="Jenis analisis">
            <select style={inputStyle()} value={jenis} onChange={e => setJenis(e.target.value)}>
              <option value="total">Total produksi EBT</option>
              <option value="per_jenis">Per jenis PLT</option>
            </select>
          </Field>
          <Field label="Pilih jenis PLT">
            <select
              style={{ ...inputStyle(), opacity: jenis === 'total' ? 0.5 : 1 }}
              value={plt}
              onChange={e => setPlt(e.target.value)}
              disabled={jenis === 'total'}
            >
              {PLANT_KEYS.map(k => (
                <option key={k} value={k}>{PLANT_META[k].label}</option>
              ))}
            </select>
          </Field>
        </div>
      </Panel>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat
          label="Forecast produksi EBT"
          value={fmt(forecastVal, 2)}
          unit="GWh"
          sub="Hasil prediksi model LSTM"
          icon={TrendingUp}
        />
        <Stat
          label="Target RUED"
          value={`${RUED_FROM.persen}%`}
          sub={`Tahun ${RUED_FROM.year} — menuju ${RUED_TO.persen}% pada ${RUED_TO.year}`}
          icon={BookOpen}
          tip="Target bauran energi terhadap total energi daerah. Satuannya persen, bukan GWh — tidak dapat dibandingkan langsung dengan forecast."
        />
        <Stat
          label="Peran forecast"
          value="Pendukung"
          sub="Bukan pengukuran langsung capaian target"
          icon={AlertCircle}
        />
        <Stat
          label="Ruang lingkup"
          value="Kelistrikan"
          sub="Tidak mencakup biofuel, biogas, energi termal"
          icon={Globe}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-7"
          title={`Tren forecast (2026–2028) — ${rowLabel}`}
          note="Forecast dalam satuan GWh, bukan persen bauran energi. Tidak dapat langsung dibandingkan dengan target RUED."
        >
          <ForecastLineChart data={ANNUAL_FORECAST} height={234} />
        </Panel>

        <div className="lg:col-span-5 flex flex-col gap-4">
          <Panel title="Tabel forecast produksi EBT" noPad>
            <DataTable
              minWidth={280}
              cols={[
                { label: 'Tahun', width: '40%' },
                { label: 'Forecast (GWh)', width: '60%', align: 'right' },
              ]}
              rows={ANNUAL_FORECAST.map((r) => (
                <tr key={r.year} style={{ borderBottom: `1px solid ${C.line}` }}>
                  <Td mono>{r.year}</Td>
                  <Td align="right" mono color={C.blue}>{fmt(r.total, 2)}</Td>
                </tr>
              ))}
            />
          </Panel>

          <Panel title="Ringkasan analisis">
            <div className="space-y-3">
              <Note tone="info">
                Forecast produksi EBT sektor kelistrikan untuk <strong>{konteks}</strong> pada tahun <strong>{tahun}</strong> adalah <strong>{fmt(forecastVal, 2)} GWh</strong>, hasil prediksi model LSTM.
                {yoyPct !== null && (
                  <> Dibanding tahun {prevYear}, forecast produksi EBT <strong>{yoyDir}</strong> sebesar <strong>{fmt(Math.abs(yoyPct), 1)}%</strong> ({fmt(prevVal, 2)} GWh → {fmt(forecastVal, 2)} GWh).</>
                )}
              </Note>
              <Note tone="warn">
                <strong>Perbedaan satuan kritis:</strong> Target RUED diukur dalam <strong>persen bauran energi daerah</strong>, sedangkan output model LSTM adalah <strong>GWh produksi kelistrikan</strong>. Keduanya tidak dapat dibandingkan secara langsung tanpa data total energi daerah (listrik + non-listrik).
              </Note>
              <p className="text-xs" style={{ color: '#8E9C91' }}>
                Hasil prediksi ini digunakan sebagai informasi pendukung evaluasi implementasi RUED, bukan sebagai pengukuran langsung terhadap capaian target bauran energi RUED ({RUED_FROM.persen}% tahun {RUED_FROM.year}, {RUED_TO.persen}% tahun {RUED_TO.year}).
              </p>
            </div>
          </Panel>
        </div>
      </div>

      <Panel
        title="Pembanding metode: LSTM vs metode tradisional"
        note="Evaluasi pada data uji tahun 2025, split & metrik identik untuk ketiga metode (lihat audit/results/tugas2_findings.md)."
        noPad
      >
        <DataTable
          minWidth={560}
          cols={[
            { label: 'Jenis PLT', width: '22%' },
            { label: 'LSTM (Fine-Tuning)', width: '20%', align: 'right' },
            { label: 'ARIMA(1,1,1)', width: '20%', align: 'right' },
            { label: 'Naive Persistence', width: '20%', align: 'right' },
            { label: 'Metode Terbaik', width: '18%', align: 'right' },
          ]}
          rows={BASELINE_BY_PLT.map(({ plt, rows, best }) => {
            const byModel = Object.fromEntries(rows.map(r => [r.model, r]));
            const lstm = byModel['LSTM_FineTuning'];
            const arima = byModel['ARIMA(1, 1, 1)'];
            const naive = byModel['Naive_Persistence'];
            const bestLabel = best?.model === 'LSTM_FineTuning' ? 'LSTM'
              : best?.model === 'Naive_Persistence' ? 'Naive'
              : best?.model?.startsWith('ARIMA') ? 'ARIMA' : '—';
            return (
              <tr key={plt} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td>{plt}</Td>
                <Td align="right" mono color={best?.model === 'LSTM_FineTuning' ? C.ok : undefined}>
                  {lstm ? `${fmt(lstm.mape, 1)}%` : '—'}
                </Td>
                <Td align="right" mono color={best?.model?.startsWith('ARIMA') ? C.ok : undefined}>
                  {arima ? `${fmt(arima.mape, 1)}%` : '—'}
                </Td>
                <Td align="right" mono color={best?.model === 'Naive_Persistence' ? C.ok : undefined}>
                  {naive ? `${fmt(naive.mape, 1)}%` : '—'}
                </Td>
                <Td align="right" mono color={bestLabel === 'LSTM' ? C.blue : C.red}>{bestLabel}</Td>
              </tr>
            );
          })}
        />
      </Panel>
      <Note tone="warn">
        MAPE (semakin kecil semakin baik). LSTM unggul di PLT skala besar/menengah, tapi <strong>naive persistence lebih akurat</strong> untuk PLTS dan PLTS Atap (skala produksi kecil) — klaim "LSTM lebih unggul" perlu dikualifikasi per jenis PLT, bukan digeneralisasi.
      </Note>

      <Footer />
    </>
  );
}
