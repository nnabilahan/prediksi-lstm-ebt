import { useState, useMemo, useEffect } from 'react';
import { Play, Cpu, BarChart2, TrendingUp, Percent, Loader2, RefreshCw } from 'lucide-react';
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
import { apiGet, apiPost } from '../lib/api';
import {
  ANNUAL_ACTUAL, ANNUAL_FORECAST, PER_JENIS_2026,
  PLANT_KEYS, PLANT_META, MODEL_RMSE, CUACA_CONFIG,
  MONTHLY_FORECAST_TOTAL, MONTHLY_FORECAST_PER_PLT,
  MONTHLY_ACTUAL_TOTAL, MONTHLY_ACTUAL_PER_PLT,
} from '../lib/data';

function emptyPredictRow() {
  return { tanggal: '', produksi: '', kapasitas: '', cuaca: '' };
}

const REAL_DATA_PARAMS = {
  annualActual: ANNUAL_ACTUAL,
  annualForecast: ANNUAL_FORECAST,
  perJenis2026: PER_JENIS_2026,
  monthlyForecastTotal: MONTHLY_FORECAST_TOTAL,
  monthlyForecastPerPlt: MONTHLY_FORECAST_PER_PLT,
  monthlyActualTotal: MONTHLY_ACTUAL_TOTAL,
  monthlyActualPerPlt: MONTHLY_ACTUAL_PER_PLT,
};

export default function Prediksi() {
  const [plant, setPlant] = useState('TOTAL');
  const [mode, setMode] = useState('rentang');
  const [y0, setY0] = useState(2026);
  const [y1, setY1] = useState(2028);

  // ── Inferensi langsung (Task Group 7/8): jenis PLT & window_size di sini
  // TERPISAH dari `plant`/mode/tahun di atas -- bagian di atas hanya
  // mengendalikan tampilan forecast statis 2026-2028 dari data.js, tidak
  // pernah memanggil backend.
  const [inferPlant, setInferPlant] = useState(PLANT_KEYS[0]);
  const [windowSizeMap, setWindowSizeMap] = useState({});
  const [healthError, setHealthError] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [predictRows, setPredictRows] = useState([]);
  const [autofillLoading, setAutofillLoading] = useState(false);
  const [predictLoading, setPredictLoading] = useState(false);
  const [predictError, setPredictError] = useState(null);
  const [predictResult, setPredictResult] = useState(null);

  async function fetchHealth() {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const health = await apiGet('/api/health');
      setWindowSizeMap(health.window_size || {});
    } catch (err) {
      setHealthError(err.message);
    } finally {
      setHealthLoading(false);
    }
  }

  useEffect(() => { fetchHealth(); }, []);

  const inferWindowSize = windowSizeMap[inferPlant] ?? null;

  // Ukuran ulang daftar baris input tiap kali PLT (atau window_size-nya)
  // berubah -- window PLTA=6 vs PLT Hybrid=12, misalnya.
  useEffect(() => {
    if (!inferWindowSize) return;
    setPredictRows(Array.from({ length: inferWindowSize }, emptyPredictRow));
    setPredictResult(null);
    setPredictError(null);
  }, [inferPlant, inferWindowSize]);

  function updatePredictRow(index, field, value) {
    setPredictRows(prev => prev.map((r, i) => i === index ? { ...r, [field]: value } : r));
  }

  async function handleAutofill() {
    if (!inferWindowSize) return;
    setAutofillLoading(true);
    setPredictError(null);
    try {
      const first = await apiGet(`/api/data?jenis_plt=${encodeURIComponent(inferPlant)}&limit=1&offset=0`);
      const offset = Math.max(0, first.total - inferWindowSize);
      const page = await apiGet(`/api/data?jenis_plt=${encodeURIComponent(inferPlant)}&limit=${inferWindowSize}&offset=${offset}`);
      if (page.items.length < inferWindowSize) {
        setPredictError(
          `Data historis ${inferPlant} di database cuma ${page.items.length} baris, ` +
          `butuh ${inferWindowSize} untuk mengisi otomatis.`
        );
        return;
      }
      setPredictRows(page.items.map(r => ({
        tanggal: r.tanggal,
        produksi: String(r.produksi),
        kapasitas: String(r.kapasitas),
        cuaca: String(r.cuaca),
      })));
      setPredictResult(null);
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setAutofillLoading(false);
    }
  }

  async function handlePredictSubmit() {
    setPredictLoading(true);
    setPredictError(null);
    setPredictResult(null);
    try {
      const payload = {
        jenis_plt: inferPlant,
        data: predictRows.map(r => ({
          tanggal: r.tanggal || null,
          produksi: r.produksi === '' ? null : parseFloat(r.produksi),
          kapasitas: r.kapasitas === '' ? null : parseFloat(r.kapasitas),
          cuaca: r.cuaca === '' ? null : parseFloat(r.cuaca),
        })),
      };
      const result = await apiPost('/api/predict', payload);
      setPredictResult(result);
    } catch (err) {
      setPredictError(err.message);
    } finally {
      setPredictLoading(false);
    }
  }

  const cuacaInfer = CUACA_CONFIG[inferPlant] || { label: 'Cuaca', satuan: '—' };

  const monthly = useMemo(
    () => buildMonthlyFromReal(plant, REAL_DATA_PARAMS),
    [plant]
  );

  const yearly = useMemo(() => {
    const map = {};
    monthly.forEach(r => {
      if (!map[r.year]) map[r.year] = { year: r.year, aktualSum: 0, prediksiSum: 0, hasAktual: false, hasPrediksi: false };
      if (r.aktual != null) { map[r.year].aktualSum += r.aktual; map[r.year].hasAktual = true; }
      // Titik "bridge" (bulan terakhir tahun aktual, dipakai supaya garis chart
      // aktual->prediksi tersambung) punya aktual DAN prediksi terisi nilai
      // yang sama -- jangan dihitung sebagai prediksi bulanan sungguhan, atau
      // total prediksi tahun itu jadi cuma 1 bulan (bukan proyeksi 12 bulan).
      if (r.prediksi != null && r.aktual == null) { map[r.year].prediksiSum += r.prediksi; map[r.year].hasPrediksi = true; }
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

            <p className="text-xs mt-1" style={{ color: C.faint }}>
              Grafik &amp; tabel di halaman ini menampilkan forecast 2026–2028 yang sudah dihitung sebelumnya (hasil riset, tidak berubah di sini). Untuk menjalankan inferensi model secara langsung dengan data baru, gunakan panel <strong>"Inferensi langsung"</strong> di bawah.
            </p>

            <div className="mt-auto pt-3 border-t" style={{ borderColor: C.line }}>
              <Gauge value={accuracy} size={168} label={`Akurasi model — MAPE ${fmt(rmse, 1)}%`} />
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
              label="MAPE model"
              value={fmt(rmse, 1)}
              unit="%"
              icon={Percent}
              tip="Mean Absolute Percentage Error (tahap Fine-Tuning) — semakin kecil, prediksi semakin mendekati nilai aktual."
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
              Jenis pembangkit yang dipilih: <strong>{plantLabel}</strong>. MAPE model {fmt(rmse, 1)}% menunjukkan tingkat kesalahan prediksi relatif terhadap nilai aktual (tahap Fine-Tuning).
            </Note>
            <Note tone="warn">
              Nilai prediksi bersifat informatif dan dapat berubah jika data historis diperbarui atau model dilatih ulang dengan parameter berbeda.
            </Note>
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
        <Panel
          className="lg:col-span-4"
          title="Inferensi langsung"
          subtitle="Jalankan model LSTM dengan data baru (bukan forecast statis di atas)"
        >
          <div className="flex flex-col gap-3 h-full">
            {healthError && (
              <Note tone="warn">
                Tidak dapat memuat konfigurasi model dari backend: {healthError}{' '}
                <button onClick={fetchHealth} className="underline font-medium"
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: 0 }}>
                  Coba lagi
                </button>
              </Note>
            )}

            <Field label="Jenis PLT">
              <select style={inputStyle()} value={inferPlant} onChange={e => setInferPlant(e.target.value)}>
                {PLANT_KEYS.map(k => (
                  <option key={k} value={k}>{PLANT_META[k].label}</option>
                ))}
              </select>
            </Field>

            <p className="text-xs" style={{ color: C.muted }}>
              {healthLoading
                ? 'Memuat window_size dari backend…'
                : inferWindowSize
                  ? <>Model {inferPlant} butuh <strong>{inferWindowSize} bulan berurutan</strong> ({cuacaInfer.label}, Kapasitas, Produksi) sebagai input.</>
                  : 'Window_size untuk PLT ini belum diketahui (cek /api/health).'}
            </p>

            <button
              type="button"
              onClick={handleAutofill}
              disabled={!inferWindowSize || autofillLoading}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium"
              style={{ background: C.greenSoft, color: C.green, border: 'none', cursor: (!inferWindowSize || autofillLoading) ? 'default' : 'pointer', opacity: (!inferWindowSize || autofillLoading) ? 0.6 : 1, fontFamily: "'Inter', sans-serif" }}
            >
              {autofillLoading ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
              {autofillLoading ? 'Mengambil data…' : `Ambil ${inferWindowSize ?? '…'} bulan terakhir dari data historis`}
            </button>

            <button
              type="button"
              onClick={handlePredictSubmit}
              disabled={!inferWindowSize || predictLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium mt-auto"
              style={{ background: C.green, color: '#fff', border: 'none', cursor: (!inferWindowSize || predictLoading) ? 'default' : 'pointer', opacity: (!inferWindowSize || predictLoading) ? 0.7 : 1, fontFamily: "'Inter', sans-serif" }}
            >
              {predictLoading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} fill="#fff" />}
              {predictLoading ? 'Memproses inferensi…' : 'Prediksi produksi EBT'}
            </button>

            {predictError && (
              <Note tone="warn"><strong>Gagal:</strong> {predictError}</Note>
            )}

            {predictResult && (
              <div className="space-y-2">
                <Note tone="info">
                  Prediksi produksi <strong>{predictResult.jenis_plt}</strong> bulan berikutnya: <strong>{fmt(predictResult.prediksi, 3)} GWh</strong>
                  {predictResult.mape_model != null && <> (MAPE model: {fmt(predictResult.mape_model, 2)}%)</>}.
                </Note>
                {predictResult.peringatan && (
                  <Note tone="warn"><strong>Peringatan:</strong> {predictResult.peringatan}</Note>
                )}
              </div>
            )}
          </div>
        </Panel>

        <Panel className="lg:col-span-8" title={`Input data ${inferWindowSize ?? ''} bulan terakhir — ${inferPlant}`} noPad>
          <div className="p-3 max-h-96 overflow-y-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr style={{ borderBottom: `1px solid ${C.line}` }}>
                  <th className="text-left py-1.5 px-1" style={{ color: C.muted }}>#</th>
                  <th className="text-left py-1.5 px-1" style={{ color: C.muted }}>Tanggal</th>
                  <th className="text-right py-1.5 px-1" style={{ color: C.muted }}>Produksi (GWh)</th>
                  <th className="text-right py-1.5 px-1" style={{ color: C.muted }}>Kapasitas (MW)</th>
                  <th className="text-right py-1.5 px-1" style={{ color: C.muted }}>{cuacaInfer.label}</th>
                </tr>
              </thead>
              <tbody>
                {predictRows.map((row, i) => (
                  <tr key={i} style={{ borderBottom: `1px solid ${C.line}` }}>
                    <td className="py-1 px-1" style={{ color: C.faint }}>{i + 1}</td>
                    <td className="py-1 px-1">
                      <input type="date" required value={row.tanggal}
                        onChange={e => updatePredictRow(i, 'tanggal', e.target.value)}
                        style={{ ...inputStyle(), padding: '4px 6px', fontSize: 11 }} />
                    </td>
                    <td className="py-1 px-1">
                      <input type="number" step="0.001" value={row.produksi}
                        onChange={e => updatePredictRow(i, 'produksi', e.target.value)}
                        style={{ ...inputStyle(), padding: '4px 6px', fontSize: 11, textAlign: 'right' }} />
                    </td>
                    <td className="py-1 px-1">
                      <input type="number" step="0.001" value={row.kapasitas}
                        onChange={e => updatePredictRow(i, 'kapasitas', e.target.value)}
                        style={{ ...inputStyle(), padding: '4px 6px', fontSize: 11, textAlign: 'right' }} />
                    </td>
                    <td className="py-1 px-1">
                      <input type="number" step="0.001" value={row.cuaca}
                        onChange={e => updatePredictRow(i, 'cuaca', e.target.value)}
                        style={{ ...inputStyle(), padding: '4px 6px', fontSize: 11, textAlign: 'right' }} />
                    </td>
                  </tr>
                ))}
                {predictRows.length === 0 && (
                  <tr><td colSpan={5} className="text-center py-6" style={{ color: C.faint }}>
                    {healthLoading ? 'Memuat…' : 'Pilih jenis PLT untuk menampilkan baris input.'}
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="px-4 pb-4">
            <Note tone="info">
              Kosongkan Produksi/Kapasitas/Cuaca pada baris mana pun untuk menguji validasi kelengkapan data backend, atau isi nilai jauh di luar kebiasaan untuk melihat <strong>peringatan rentang nilai</strong>.
            </Note>
          </div>
        </Panel>
      </div>

      <Footer />
    </>
  );
}
