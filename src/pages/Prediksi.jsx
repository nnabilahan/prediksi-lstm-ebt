import { useState, useEffect, useMemo } from 'react';
import { Play, Cpu, Loader2, Satellite, LineChart, Pencil, RotateCcw } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Stat from '../components/ui/Stat';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import Field, { inputStyle } from '../components/ui/Field';
import DataTable, { Td } from '../components/ui/DataTable';
import { C } from '../lib/tokens';
import { fmt } from '../lib/utils';
import { apiGet, apiPost } from '../lib/api';
import { PLANT_KEYS, PLANT_META, CUACA_CONFIG, MODEL_COMPARISON } from '../lib/data';

// Metrik model produksi per jenis PLT, diambil dari MODEL_COMPARISON supaya
// angka di halaman ini tidak pernah berbeda dengan tabel di Gap Analysis.
const METRIK_MODEL = Object.fromEntries(
  MODEL_COMPARISON.map(r => [r.plt, r.lstm])
);

function bulanKeInput(iso) {
  return iso ? iso.slice(0, 7) : '';
}

function labelBulan(iso) {
  if (!iso) return '—';
  const nama = ['Januari','Februari','Maret','April','Mei','Juni',
                'Juli','Agustus','September','Oktober','November','Desember'];
  const [th, bl] = iso.slice(0, 7).split('-');
  return `${nama[Number(bl) - 1]} ${th}`;
}

export default function Prediksi() {
  const [plant, setPlant] = useState(PLANT_KEYS[0]);
  const [bulanTarget, setBulanTarget] = useState('');

  // `siap` = paket bahan inferensi dari GET /api/prediksi/siap (window histori
  // + nilai cuaca bulan target). Disimpan utuh supaya bisa ditampilkan ke
  // pengguna sebelum dikirim ke model.
  const [siap, setSiap] = useState(null);
  const [siapLoading, setSiapLoading] = useState(false);
  const [hasil, setHasil] = useState(null);
  const [predictLoading, setPredictLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modeLanjutan, setModeLanjutan] = useState(false);

  const cuacaMeta = CUACA_CONFIG[plant] || { label: 'Cuaca', satuan: '—', help: '' };
  const metrik = METRIK_MODEL[plant];

  // Ganti jenis PLT = konteks lama tidak berlaku lagi. Dikosongkan supaya
  // tidak ada hasil PLTA yang masih terpampang saat PLTB sudah dipilih.
  useEffect(() => {
    setSiap(null);
    setHasil(null);
    setError(null);
    setBulanTarget('');
  }, [plant]);

  async function muatBahan(bulan) {
    setSiapLoading(true);
    setError(null);
    setHasil(null);
    try {
      const q = new URLSearchParams({ jenis_plt: plant });
      if (bulan) q.set('bulan_target', `${bulan}-01`);
      const data = await apiGet(`/api/prediksi/siap?${q}`);
      setSiap(data);
      setBulanTarget(bulanKeInput(data.bulan_target));
      return data;
    } catch (err) {
      setError(err.message);
      setSiap(null);
      return null;
    } finally {
      setSiapLoading(false);
    }
  }

  useEffect(() => { muatBahan(null); /* eslint-disable-next-line */ }, [plant]);

  async function handlePrediksi() {
    const bahan = siap ?? await muatBahan(bulanTarget || null);
    if (!bahan) return;

    setPredictLoading(true);
    setError(null);
    try {
      const hasilPrediksi = await apiPost('/api/predict', {
        jenis_plt: bahan.jenis_plt,
        data: bahan.data.map(r => ({
          tanggal: r.tanggal,
          produksi: r.produksi,
          kapasitas: r.kapasitas,
          cuaca: r.cuaca,
        })),
        cuaca_target: bahan.cuaca_target,
      });
      setHasil({ ...hasilPrediksi, bulan_target: bahan.bulan_target });
    } catch (err) {
      setError(err.message);
    } finally {
      setPredictLoading(false);
    }
  }

  function ubahBaris(index, field, value) {
    setSiap(prev => ({
      ...prev,
      data: prev.data.map((r, i) => (i === index ? { ...r, [field]: value === '' ? null : parseFloat(value) } : r)),
    }));
    setHasil(null);
  }

  const dariNasa = siap?.cuaca_sumber === 'nasa_power';

  const rentangHistori = useMemo(() => {
    if (!siap?.data?.length) return '—';
    return `${labelBulan(siap.data[0].tanggal)} – ${labelBulan(siap.data[siap.data.length - 1].tanggal)}`;
  }, [siap]);

  return (
    <>
      <PageHead
        title="Prediksi Produksi EBT"
        desc="Pilih jenis pembangkit dan bulan yang ingin ditebak — sistem menyiapkan sendiri data historis dan nilai cuaca yang dibutuhkan model, lalu menjalankan inferensi LSTM."
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat label="Jenis pembangkit" value={plant} sub={PLANT_META[plant]?.label} icon={Cpu} />
        <Stat
          label="RMSE model"
          value={metrik ? fmt(metrik.rmse, metrik.rmse < 1 ? 4 : 2) : '—'}
          unit="GWh"
          icon={LineChart}
          tip="Root Mean Squared Error pada data uji 2025 — metrik evaluasi utama, dalam satuan produksi (GWh). Semakin kecil semakin baik."
        />
        <Stat
          label="MAPE model"
          value={metrik ? fmt(metrik.mape, 2) : '—'}
          unit="%"
          tip="Mean Absolute Percentage Error — kesalahan relatif, berguna untuk membandingkan antar jenis PLT yang skalanya jauh berbeda."
        />
        <Stat
          label="Kebutuhan input"
          value={siap ? String(siap.window_size) : '—'}
          unit="bulan"
          tip="Panjang window model. Berbeda per jenis PLT karena tiap kategori punya konfigurasi pemenang sendiri dari walk-forward validation — PLTB butuh 6 bulan, sisanya 3 bulan."
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        <Panel className="lg:col-span-4" title="Jalankan prediksi" subtitle="Dua isian, satu klik">
          <div className="space-y-3">
            <Field label="Jenis pembangkit">
              <select style={inputStyle()} value={plant} onChange={e => setPlant(e.target.value)}>
                {PLANT_KEYS.map(k => (
                  <option key={k} value={k}>{k} — {PLANT_META[k]?.label}</option>
                ))}
              </select>
            </Field>

            <Field label="Bulan yang ingin ditebak">
              <input
                type="month"
                style={inputStyle()}
                value={bulanTarget}
                onChange={e => setBulanTarget(e.target.value)}
                onBlur={e => e.target.value && muatBahan(e.target.value)}
              />
            </Field>

            <button
              onClick={handlePrediksi}
              disabled={!siap || siapLoading || predictLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium"
              style={{
                background: C.green, color: '#fff', border: 'none',
                cursor: (!siap || siapLoading || predictLoading) ? 'default' : 'pointer',
                opacity: (!siap || siapLoading || predictLoading) ? 0.6 : 1,
                fontFamily: "'Inter', sans-serif",
              }}
            >
              {(siapLoading || predictLoading)
                ? <Loader2 size={15} className="animate-spin" />
                : <Play size={15} />}
              {siapLoading ? 'Menyiapkan data…' : predictLoading ? 'Menjalankan model…' : 'Jalankan prediksi'}
            </button>

            {error && (
              <div className="rounded-lg px-3 py-2 text-xs" style={{ background: '#FEF2F2', color: C.red }}>
                {error}
              </div>
            )}

            {hasil && (
              <div className="rounded-lg p-4 text-center" style={{ background: C.greenSoft }}>
                <p className="text-xs mb-1" style={{ color: C.muted }}>
                  Prediksi {hasil.jenis_plt} — {labelBulan(hasil.bulan_target)}
                </p>
                <p className="text-2xl font-semibold" style={{ color: C.green }}>
                  {fmt(hasil.prediksi, 3)}
                  <span className="text-sm font-normal ml-1">GWh</span>
                </p>
                {hasil.peringatan && (
                  <p className="text-[11px] mt-2 text-left" style={{ color: C.gold }}>
                    {hasil.peringatan}
                  </p>
                )}
              </div>
            )}
          </div>
        </Panel>

        <div className="lg:col-span-8 flex flex-col gap-4">
          <Panel
            title={`Nilai ${cuacaMeta.label.toLowerCase()} untuk bulan target`}
            subtitle="Diisi otomatis — tidak perlu menebak sendiri"
          >
            {siap ? (
              <div className="flex flex-wrap items-center gap-4">
                <div>
                  <p className="text-2xl font-semibold" style={{ color: C.ink }}>
                    {fmt(siap.cuaca_target, 3)}
                    <span className="text-sm font-normal ml-1" style={{ color: C.muted }}>
                      {cuacaMeta.satuan}
                    </span>
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: C.muted }}>
                    {cuacaMeta.label} · {labelBulan(siap.bulan_target)}
                  </p>
                </div>
                <span
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium"
                  style={dariNasa
                    ? { background: C.greenSoft, color: C.green }
                    : { background: C.goldSoft, color: C.gold }}
                >
                  {dariNasa ? <Satellite size={12} /> : <RotateCcw size={12} />}
                  {dariNasa ? 'Observasi NASA POWER' : 'Normal klimatologis'}
                </span>
                <p className="text-xs flex-1 min-w-[220px]" style={{ color: C.muted }}>
                  {siap.cuaca_keterangan}
                </p>
              </div>
            ) : (
              <p className="text-xs" style={{ color: C.muted }}>
                {siapLoading ? 'Menyiapkan…' : 'Belum ada data.'}
              </p>
            )}
          </Panel>

          <Panel
            title="Data historis yang dipakai model"
            subtitle={siap ? `${siap.window_size} bulan terakhir · ${rentangHistori}` : '—'}
            noPad
            right={
              <button
                onClick={() => setModeLanjutan(v => !v)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium"
                style={{ background: modeLanjutan ? C.greenSoft : C.line, color: modeLanjutan ? C.green : C.muted, border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}
              >
                <Pencil size={12} />
                {modeLanjutan ? 'Selesai menyunting' : 'Sunting manual'}
              </button>
            }
          >
            {siap ? (
              <DataTable
                minWidth={520}
                cols={[
                  { label: 'Bulan', width: '28%' },
                  { label: 'Produksi (GWh)', width: '24%', align: 'right' },
                  { label: 'Kapasitas (MW)', width: '24%', align: 'right' },
                  { label: cuacaMeta.label, width: '24%', align: 'right' },
                ]}
                rows={siap.data.map((r, i) => (
                  <tr key={r.tanggal} style={{ borderBottom: `1px solid ${C.line}` }}>
                    <Td>{labelBulan(r.tanggal)}</Td>
                    {['produksi', 'kapasitas', 'cuaca'].map(kolom => (
                      <Td key={kolom} align="right" mono>
                        {modeLanjutan ? (
                          <input
                            type="number" step="0.001"
                            value={r[kolom] ?? ''}
                            onChange={e => ubahBaris(i, kolom, e.target.value)}
                            style={{ ...inputStyle(), textAlign: 'right', padding: '3px 6px', width: '100%' }}
                          />
                        ) : fmt(r[kolom], 3)}
                      </Td>
                    ))}
                  </tr>
                ))}
              />
            ) : (
              <p className="text-xs p-4" style={{ color: C.muted }}>
                {siapLoading ? 'Memuat data historis…' : 'Belum ada data.'}
              </p>
            )}
          </Panel>
        </div>
      </div>

      <Note tone="info">
        Halaman ini menjalankan <strong>inferensi sungguhan</strong> ke model LSTM di backend untuk satu bulan ke depan.
        Untuk proyeksi jangka panjang <strong>2026–2028</strong>, lihat halaman <strong>Dashboard</strong> dan <strong>Gap Analysis RUED</strong> — angka di sana dihitung sekali lewat pipeline riset dan tidak dihitung ulang saat halaman dibuka.
        Kapasitas bulan target diasumsikan sama dengan bulan terakhir yang tercatat ({siap ? `${fmt(siap.kapasitas_terakhir, 2)} MW` : '—'}), mengikuti asumsi kapasitas tetap yang juga dipakai forecast jangka panjang.
      </Note>

      <Footer />
    </>
  );
}
