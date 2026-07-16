import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip,
} from 'recharts';
import { C } from '../../lib/tokens';
import { fmt } from '../../lib/utils';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg"
      style={{ background: C.ink, color: '#fff', minWidth: 130 }}
    >
      <p className="font-semibold mb-1" style={{ color: C.faint }}>{label}</p>
      {payload.map((p, i) => p.value != null && (
        <p key={i} style={{ color: p.color }}>
          {p.name === 'aktual' ? 'Aktual' : 'Prediksi'}: {fmt(p.value, 0)} GWh
        </p>
      ))}
    </div>
  );
}

export default function AnnualChart({ data, height = 224 }) {
  return (
    <div>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={C.line} vertical={false} />
            <XAxis
              dataKey="year"
              tick={{ fontSize: 11, fill: C.faint }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: C.faint }}
              axisLine={false}
              tickLine={false}
              width={48}
              tickFormatter={(v) => fmt(v, 0)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="aktual"
              stroke={C.green}
              strokeWidth={2}
              dot={{ r: 3, fill: C.green, strokeWidth: 0 }}
              connectNulls={false}
              name="aktual"
            />
            <Line
              type="monotone"
              dataKey="prediksi"
              stroke={C.gold}
              strokeWidth={2}
              strokeDasharray="5 3"
              dot={{ r: 3, fill: C.gold, strokeWidth: 0 }}
              connectNulls={false}
              name="prediksi"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-4 mt-2 justify-center">
        <span className="flex items-center gap-1.5 text-xs" style={{ color: C.muted }}>
          <span style={{ display: 'inline-block', width: 20, height: 2, background: C.green, borderRadius: 1 }} />
          Aktual
        </span>
        <span className="flex items-center gap-1.5 text-xs" style={{ color: C.muted }}>
          <span style={{ display: 'inline-block', width: 20, height: 2, background: C.gold, borderRadius: 1 }} />
          Prediksi
        </span>
      </div>
    </div>
  );
}
