import { useState } from 'react';
import { TrendingUp, BookOpen, AlertCircle, Globe } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import ForecastLineChart from '../components/charts/ForecastLineChart';
import GrowthRateChart from '../components/charts/GrowthRateChart';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt } from '../lib/utils';
import { ANNUAL_FORECAST, PER_JENIS_2026, PLANT_KEYS, PLANT_META, MONTHLY_FORECAST_PER_PLT, RUED_TARGET, MODEL_COMPARISON, LSTM_MENANG, MODEL_TOTAL_PLT } from '../lib/data';

const [RUED_FROM, RUED_TO] = RUED_TARGET.anchors;

// Label kolom sekaligus urutan tampil pada tabel pembanding metode.
const METODE = [
  { key: 'lstm', label: 'LSTM (produksi)' },
  { key: 'arima', label: 'ARIMA(1,1,1)' },
  { key: 'naive', label: 'Naive lag-1' },
  { key: 'seasonal', label: 'Seasonal × Kapasitas' },
];

const LABEL_SINGKAT = {
  lstm: 'LSTM',
  arima: 'ARIMA',
  naive: 'Naive',
  seasonal: 'Seasonal',
};

// Build per-PLT annual totals for 2027 and 2028 from monthly data
function perPltAnnual(plant, year) {
  const data = MONTHLY_FORECAST_PER_PLT[plant];
  if (!data) return null;
  const startIdx = (year - 2026) * 12;
  return data.slice(startIdx, startIdx + 12).reduce((s, v) => s + v, 0);
}

// Tren pertumbuhan (growth rate) forecast 2026-2028 untuk konteks terpilih
// (total atau per jenis PLT) -- 2026 tidak punya YoY karena tidak ada
// tahun forecast sebelumnya untuk dibandingkan (konsisten dengan field
// `yoy` di ANNUAL_FORECAST, yang juga null untuk 2026).
function buildGrowthSeries(jenis, plt) {
  const years = [2026, 2027, 2028];
  const totals = years.map((year) => (
    jenis === 'total'
      ? ANNUAL_FORECAST.find(r => r.year === year)?.total ?? null
      : (year === 2026 ? PER_JENIS_2026.find(r => r.jenis === plt)?.produksi ?? null : perPltAnnual(plt, year))
  ));
  return years.map((year, i) => {
    const total = totals[i];
    const prev = i > 0 ? totals[i - 1] : null;
    const yoy = (total != null && prev != null && prev !== 0) ? ((total - prev) / prev) * 100 : null;
    return { year, total, yoy };
  });
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

  const growthSeries = buildGrowthSeries(jenis, plt);
  const growthChartData = growthSeries.filter(r => r.yoy != null).map(r => ({ year: r.year, yoy: r.yoy }));

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
            </div>
          </Panel>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-7"
          title={`Tren pertumbuhan (growth rate) forecast 2026–2028 — ${rowLabel}`}
          note="Persentase perubahan forecast tahun berjalan terhadap tahun sebelumnya. 2026 tidak punya nilai growth karena tidak ada tahun forecast sebelumnya untuk dibandingkan."
        >
          {growthChartData.length > 0 ? (
            <GrowthRateChart data={growthChartData} height={180} />
          ) : (
            <p className="text-xs" style={{ color: '#8E9C91' }}>Data growth rate tidak tersedia untuk konteks ini.</p>
          )}
        </Panel>

        <Panel className="lg:col-span-5" title="Tabel growth rate per tahun" noPad>
          <DataTable
            minWidth={320}
            cols={[
              { label: 'Tahun', width: '25%' },
              { label: 'Forecast (GWh)', width: '40%', align: 'right' },
              { label: 'Growth YoY', width: '35%', align: 'right' },
            ]}
            rows={growthSeries.map((r) => (
              <tr key={r.year} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td mono>{r.year}</Td>
                <Td align="right" mono color={C.blue}>{fmt(r.total, 2)}</Td>
                <Td align="right" mono color={r.yoy == null ? undefined : (r.yoy >= 0 ? C.ok : C.red)}>
                  {r.yoy == null ? '—' : `${r.yoy >= 0 ? '+' : ''}${fmt(r.yoy, 1)}%`}
                </Td>
              </tr>
            ))}
          />
        </Panel>
      </div>

      <Panel
        title="Pembanding metode: LSTM vs metode tradisional"
        subtitle={`RMSE pada data uji 2025 (GWh, makin kecil makin baik) — LSTM unggul di ${LSTM_MENANG} dari ${MODEL_TOTAL_PLT} jenis PLT`}
        noPad
      >
        <DataTable
          minWidth={640}
          cols={[
            { label: 'Jenis PLT', width: '20%' },
            ...METODE.map(m => ({ label: m.label, width: '17%', align: 'right' })),
            { label: 'Terbaik', width: '12%', align: 'right' },
          ]}
          rows={MODEL_COMPARISON.map(({ plt, best, ...metrik }) => {
            // Angka kecil (PLTS/PLTS Atap) butuh lebih banyak desimal supaya
            // selisih antar metode tidak hilang oleh pembulatan.
            const desimal = metrik.lstm.rmse < 1 ? 4 : 2;
            return (
              <tr key={plt} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td>{plt}</Td>
                {METODE.map(m => (
                  <Td
                    key={m.key}
                    align="right"
                    mono
                    color={best === m.key ? C.ok : undefined}
                  >
                    {fmt(metrik[m.key].rmse, desimal)}
                  </Td>
                ))}
                <Td align="right" mono color={best === 'lstm' ? C.blue : C.red}>
                  {LABEL_SINGKAT[best]}
                </Td>
              </tr>
            );
          })}
        />
      </Panel>
      <Note tone={LSTM_MENANG > MODEL_TOTAL_PLT / 2 ? 'info' : 'warn'}>
        Tabel ini memakai <strong>model produksi</strong> (pooled + category embedding + ensembling) — model yang sama persis yang melayani halaman Prediksi EBT.{' '}
        <strong>LSTM unggul di {LSTM_MENANG} dari {MODEL_TOTAL_PLT} jenis PLT</strong> (PLTA, PLTB, PLTM), dengan akurasi 89–93% di kelimanya.{' '}
        PLTS &amp; PLTS Atap masih kalah tipis dari <em>seasonal naive × rasio kapasitas</em>; keduanya adalah kategori berskala terkecil, dan pada 24 titik latih per jenis PLT selisih ini masih berada di dalam rentang ketidakpastian.{' '}
        Kombinasi model <strong>tidak ditukar</strong> untuk mengejar skor test yang lebih bagus, karena pemilihan berdasarkan data uji adalah bentuk kebocoran data.
      </Note>

      <Footer />
    </>
  );
}
