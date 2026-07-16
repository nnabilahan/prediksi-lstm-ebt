import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { C } from '../../lib/tokens';
import { PLANT_META } from '../../lib/data';

export default function DonutChart({ data, centerLabel, centerValue }) {
  return (
    <div>
      <div style={{ height: 180, position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="produksi"
              nameKey="jenis"
              innerRadius={48}
              outerRadius={72}
              strokeWidth={0}
            >
              {data.map((entry, i) => (
                <Cell
                  key={entry.jenis}
                  fill={PLANT_META[entry.jenis]?.color || C.faint}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        {/* Center label overlay */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            pointerEvents: 'none',
          }}
        >
          <p style={{ fontSize: 10, color: C.faint, marginBottom: 2 }}>{centerLabel}</p>
          <p style={{ fontSize: 13, fontWeight: 700, color: C.ink, fontFamily: "'Sora', sans-serif" }}>
            {centerValue}
          </p>
        </div>
      </div>
      {/* Legend */}
      <div className="mt-2 space-y-1.5">
        {data.map((d) => (
          <div key={d.jenis} className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 min-w-0">
              <span
                className="flex-shrink-0"
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: PLANT_META[d.jenis]?.color || C.faint,
                  display: 'inline-block',
                }}
              />
              <span className="text-xs truncate" style={{ color: C.muted }}>
                {d.jenis}
              </span>
            </div>
            <span className="text-xs flex-shrink-0" style={{ color: C.faint, fontFamily: "'IBM Plex Mono', monospace" }}>
              {d.pct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
