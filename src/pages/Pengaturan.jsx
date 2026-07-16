import PageHead from '../components/ui/PageHead';
import Panel from '../components/ui/Panel';
import Note from '../components/ui/Note';
import Field, { inputStyle } from '../components/ui/Field';
import Footer from '../components/layout/Footer';
import { C } from '../lib/tokens';

export default function Pengaturan() {
  return (
    <>
      <PageHead
        title="Pengaturan"
        desc="Konfigurasi profil pengguna dan parameter sistem SIPREBAR"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-stretch">
        <Panel title="Profil pengguna" subtitle="Identitas yang tampil pada laporan">
          <div className="space-y-3">
            <Field label="Nama">
              <input
                type="text"
                defaultValue="Admin Dinas ESDM"
                style={inputStyle()}
              />
            </Field>
            <Field label="Instansi">
              <input
                type="text"
                defaultValue="Dinas Energi dan Sumber Daya Mineral Prov. Sulsel"
                style={inputStyle()}
              />
            </Field>
            <button
              className="mt-2 px-4 py-2 rounded-lg text-sm font-medium"
              style={{ background: C.green, color: '#fff', border: 'none', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}
            >
              Simpan perubahan
            </button>
          </div>
        </Panel>

        <Panel title="Parameter model" subtitle="Ambang batas dan mode pelatihan">
          <div className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm" style={{ color: C.ink }}>
                Ambang batas RMSE peringatan
              </span>
              <input
                type="text"
                defaultValue="5.0%"
                style={{ ...inputStyle(), width: 80, textAlign: 'right' }}
              />
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm" style={{ color: C.ink }}>
                Retraining model
              </span>
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-medium"
                style={{ background: C.goldSoft, color: C.gold }}
              >
                Manual (via Colab)
              </span>
            </div>
            <Note tone="info">
              Pelatihan ulang dijalankan di luar aplikasi menggunakan pipeline Google Colab, lalu artefak model (.h5) dan scaler (.pkl) diunggah kembali ke sistem.
            </Note>
          </div>
        </Panel>
      </div>

      <Footer />
    </>
  );
}
