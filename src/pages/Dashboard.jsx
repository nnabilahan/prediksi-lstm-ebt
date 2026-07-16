import { Zap, Layers, Target, Globe } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import MonthlyChart from '../components/charts/MonthlyChart';
import AnnualChart from '../components/charts/AnnualChart';
import DonutChart from '../components/charts/DonutChart';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt, buildMonthlyFromReal } from '../lib/utils';
import {
  ANNUAL_ACTUAL, ANNUAL_FORECAST, TREND_ANNUAL, PER_JENIS_2026, PLANT_META,
  MONTHLY_FORECAST_TOTAL, MONTHLY_FORECAST_PER_PLT,
} from '../lib/data';
import { useMemo } from 'react';

const REAL_DATA_PARAMS = {
  annualActual: ANNUAL_ACTUAL,
  annualForecast: ANNUAL_FORECAST,
  perJenis2026: PER_JENIS_2026,
  monthlyForecastTotal: MONTHLY_FORECAST_TOTAL,
  monthlyForecastPerPlt: MONTHLY_FORECAST_PER_PLT,
};

export default function Dashboard({ go }) {
  const allMonthly = useMemo(
    () => buildMonthlyFromReal('TOTAL', REAL_DATA_PARAMS),
    []
  );
  const forecastMonthly = useMemo(
    () => allMonthly.filter(r => r.year >= 2025),
    [allMonthly]
  );

  return (
    <>
      <PageHead
        title="Dashboard Monitoring & Prediksi EBT"
        desc="Ringkasan produksi energi baru terbarukan sektor kelistrikan Provinsi Sulawesi Selatan"
      />

      {/* Stat grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat
          label="Total produksi EBT terakhir"
          value={fmt(1320, 0)}
          unit="GWh"
          sub="+5,6% dari tahun sebelumnya"
          tone="up"
          icon={Zap}
          tip="Total seluruh jenis PLT pada tahun observasi terakhir (2025)"
        />
        <Stat
          label="Jumlah jenis PLT"
          value="7"
          unit="Jenis"
          sub="PLTA, PLTB, PLTM, PLTMH, PLTS, PLTS Atap, PLT Hybrid"
          icon={Layers}
        />
        <Stat
          label="Target RUED"
          value="20%"
          sub="Tahun 2025 — menuju 32% pada 2050"
          icon={Target}
          tip="Target bauran energi EBT terhadap total energi daerah (listrik + non-listrik), bukan target produksi GWh."
        />
        <Stat
          label="Ruang lingkup"
          value="Sektor"
          unit="Kelistrikan"
          sub="Forecast = informasi pendukung evaluasi RUED"
          icon={Globe}
        />
      </div>

      {/* Chart row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-8"
          title="Forecasting total produksi EBT (2026–2028)"
          subtitle="Hasil prediksi model LSTM, granularitas bulanan"
        >
          <MonthlyChart data={forecastMonthly} height={250} />
        </Panel>
        <Panel
          className="lg:col-span-4"
          title="Komposisi per jenis PLT"
          subtitle="Agregasi forecast tahun 2026"
        >
          <DonutChart
            data={PER_JENIS_2026}
            centerLabel="Total 2026"
            centerValue="1.636 GWh"
          />
        </Panel>
      </div>

      {/* Trend + table row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-5"
          title="Tren produksi EBT historis"
          subtitle="Total tahunan 2022–2025 + proyeksi"
        >
          <AnnualChart data={TREND_ANNUAL} height={224} />
        </Panel>
        <Panel
          className="lg:col-span-7"
          title="Produksi per jenis pembangkit (2026)"
          noPad
        >
          <DataTable
            minWidth={480}
            cols={[
              { label: 'Jenis', width: '30%' },
              { label: 'Produksi (GWh)', width: '26%', align: 'right' },
              { label: 'Persentase', width: '22%', align: 'right' },
              { label: 'vs 2025', width: '22%', align: 'right' },
            ]}
            rows={PER_JENIS_2026.map((r) => (
              <tr key={r.jenis} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td>
                  <span className="flex items-center gap-1.5">
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: PLANT_META[r.jenis]?.color, display: 'inline-block', flexShrink: 0 }} />
                    <span className="truncate">{r.jenis}</span>
                  </span>
                </Td>
                <Td align="right" mono>{fmt(r.produksi, 2)}</Td>
                <Td align="right" mono>{fmt(r.pct, 1)}%</Td>
                <Td align="right" mono color={r.yoy >= 0 ? C.ok : C.red}>
                  {r.yoy >= 0 ? '+' : ''}{fmt(r.yoy, 1)}%
                </Td>
              </tr>
            ))}
          />
        </Panel>
      </div>

      {/* Summary + notes row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-5"
          title="Ringkasan total forecast per tahun"
          right={
            <button
              onClick={() => go('gap')}
              className="px-3 py-1.5 rounded-lg text-xs font-medium"
              style={{ background: C.greenSoft, color: C.green }}
            >
              Evaluasi RUED
            </button>
          }
          noPad
        >
          <DataTable
            minWidth={320}
            cols={[
              { label: 'Tahun', width: '34%' },
              { label: 'Total (GWh)', width: '36%', align: 'right' },
              { label: 'Perubahan', width: '30%', align: 'right' },
            ]}
            rows={ANNUAL_FORECAST.map((r) => (
              <tr key={r.year} style={{ borderBottom: `1px solid ${C.line}` }}>
                <Td><span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12 }}>{r.year}</span></Td>
                <Td align="right" mono color={C.blue}>{fmt(r.total, 2)}</Td>
                <Td align="right" mono color={r.yoy == null ? C.faint : r.yoy >= 0 ? C.ok : C.red}>
                  {r.yoy == null ? '—' : `${r.yoy >= 0 ? '+' : ''}${fmt(r.yoy, 2)}%`}
                </Td>
              </tr>
            ))}
          />
        </Panel>
        <Panel className="lg:col-span-7" title="Catatan pembacaan">
          <div className="space-y-3">
            <Note tone="info">
              Forecast produksi EBT sektor kelistrikan digunakan sebagai <strong>informasi pendukung</strong> evaluasi implementasi RUED, bukan sebagai pengukuran langsung capaian target bauran energi (20% tahun 2025, 32% tahun 2050).
            </Note>
            <Note tone="warn">
              Analisis hanya mencakup <strong>sektor kelistrikan</strong>. Sektor non-listrik (biofuel, biogas, energi termal) tidak diprediksi karena dokumentasi historisnya belum konsisten.
            </Note>
            <Note tone="info">
              Nilai forecast berasal dari model LSTM yang <strong>sudah dilatih sebelumnya</strong>. Membuka halaman ini tidak menjalankan pelatihan atau inferensi baru.
            </Note>
          </div>
        </Panel>
      </div>

      <Footer />
    </>
  );
}
