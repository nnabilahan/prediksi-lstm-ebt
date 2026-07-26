import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine, Cell,
} from 'recharts';
import { C } from '../../lib/tokens';
import { fmt } from '../../lib/utils';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const v = payload[0]?.value;
  return (
    <div
      className="rounded-lg px-3 py-2 text-xs shadow-lg"
      style={{ background: C.ink, color: '#fff' }}
    >
      <p className="font-semibold mb-1" style={{ color: C.faint }}>{label}</p>
      <p style={{ color: v >= 0 ? C.ok : C.red }}>Growth: {v >= 0 ? '+' : ''}{fmt(v, 1)}%</p>
    </div>
  );
}

// data: [{ year, yoy }] — yoy in percent, null entries are skipped by recharts.
export default function GrowthRateChart({ data, height = 180 }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
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
            width={44}
            tickFormatter={(v) => `${fmt(v, 0)}%`}
          />
          <ReferenceLine y={0} stroke={C.line} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="yoy" radius={[4, 4, 4, 4]} maxBarSize={48}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.yoy >= 0 ? C.ok : C.red} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
