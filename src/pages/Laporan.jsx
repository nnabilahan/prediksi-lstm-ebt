import { FileText } from 'lucide-react';
import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Note from '../components/ui/Note';
import Footer from '../components/layout/Footer';
import { C } from '../lib/tokens';

const REPORTS = [
  { title: 'Laporan tren produksi EBT 2022–2025', desc: 'Analisis historis per jenis PLT' },
  { title: 'Laporan prediksi LSTM 2026–2028', desc: 'Hasil forecast dan evaluasi akurasi model' },
  { title: 'Laporan evaluasi RUED', desc: 'Konteks kebijakan dan informasi pendukung RUED' },
];

export default function Laporan() {
  return (
    <>
      <PageHead
        title="Laporan"
        desc="Ekspor dan unduh laporan produksi EBT dalam format PDF atau Excel"
      />

      <Panel
        title="Rencana pengembangan"
        subtitle="Kartu di bawah adalah usulan desain, belum terhubung ke backend"
      >
        <div className="space-y-4">
          <Note tone="warn">
            Tahap saat ini hanya berfokus pada halaman Dashboard, Prediksi EBT, Gap Analysis RUED, dan Data EBT. Fitur laporan akan dikembangkan pada tahap berikutnya.
          </Note>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-2">
            {REPORTS.map((r) => (
              <div
                key={r.title}
                className="rounded-lg border p-4 flex flex-col gap-3"
                style={{ borderColor: C.line }}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: C.greenSoft }}
                  >
                    <FileText size={15} color={C.green} />
                  </span>
                  <p className="text-sm font-semibold leading-tight" style={{ color: C.ink }}>
                    {r.title}
                  </p>
                </div>
                <p className="text-xs" style={{ color: C.muted }}>
                  {r.desc}
                </p>
                <button
                  disabled
                  className="mt-auto w-full rounded-lg py-2 text-xs font-medium"
                  style={{
                    background: C.line,
                    color: C.faint,
                    cursor: 'not-allowed',
                    border: 'none',
                    fontFamily: "'Inter', sans-serif",
                  }}
                >
                  Segera hadir
                </button>
              </div>
            ))}
          </div>
        </div>
      </Panel>

      <Footer />
    </>
  );
}
