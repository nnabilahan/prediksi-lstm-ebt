import { Zap, ChevronDown, LayoutDashboard, TrendingUp, Target, Database } from 'lucide-react';
import { C } from '../../lib/tokens';

const TABS = [
  { key: 'dashboard',   label: 'Dashboard',          icon: LayoutDashboard },
  { key: 'prediksi',    label: 'Prediksi EBT',        icon: TrendingUp },
  { key: 'gap',         label: 'Gap Analysis RUED',   icon: Target },
  { key: 'data',        label: 'Data EBT',            icon: Database },
];

function getTodayID() {
  const now = new Date();
  const months = ['Januari','Februari','Maret','April','Mei','Juni',
                  'Juli','Agustus','September','Oktober','November','Desember'];
  return `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
}

export default function TopNav({ page, setPage }) {
  return (
    <div className="sticky top-0 z-50" style={{ boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}>
      {/* Brand bar */}
      <div style={{ background: C.greenDark, height: 56 }}>
        <div className="max-w-[1320px] mx-auto px-6 h-full flex items-center justify-between">
          {/* Left: brand */}
          <div className="flex items-center gap-2.5">
            <div
              className="flex items-center justify-center rounded-full flex-shrink-0"
              style={{ width: 32, height: 32, background: C.gold }}
            >
              <Zap size={16} color="#fff" fill="#fff" />
            </div>
            <div>
              <p
                className="leading-none font-bold"
                style={{ color: '#fff', fontSize: 14, fontFamily: "'Sora', sans-serif" }}
              >
                SIPREBAR
              </p>
              <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10.5, marginTop: 1 }}>
                Dinas ESDM Provinsi Sulawesi Selatan
              </p>
            </div>
          </div>
          {/* Right: date + user */}
          <div className="flex items-center gap-3">
            <span style={{ color: 'rgba(255,255,255,0.65)', fontSize: 12 }}>{getTodayID()}</span>
            <div className="flex items-center gap-1.5">
              <div
                className="flex items-center justify-center rounded-full text-xs font-bold"
                style={{ width: 30, height: 30, background: C.gold, color: '#fff', fontFamily: "'Sora', sans-serif" }}
              >
                AN
              </div>
              <span style={{ color: 'rgba(255,255,255,0.85)', fontSize: 12 }}>Admin</span>
              <ChevronDown size={14} color="rgba(255,255,255,0.65)" />
            </div>
          </div>
        </div>
      </div>
      {/* Tab bar */}
      <div style={{ background: '#fff', borderBottom: `1px solid ${C.line}` }}>
        <div className="max-w-[1320px] mx-auto px-6 flex overflow-x-auto" style={{ scrollbarWidth: 'none' }}>
          {TABS.map(({ key, label, icon: Icon }) => {
            const active = page === key;
            return (
              <button
                key={key}
                onClick={() => setPage(key)}
                className="flex items-center gap-1.5 px-3 text-sm font-medium flex-shrink-0 transition-colors border-0 bg-transparent cursor-pointer"
                style={{
                  color: active ? C.green : C.muted,
                  borderBottom: active ? `2px solid ${C.gold}` : '2px solid transparent',
                  fontSize: 13,
                  fontFamily: "'Inter', sans-serif",
                  paddingBottom: 10,
                  paddingTop: 10,
                  whiteSpace: 'nowrap',
                }}
              >
                <Icon size={14} />
                {label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
