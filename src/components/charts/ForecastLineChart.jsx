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
      style={{ background: C.ink, color: '#fff' }}
    >
      <p className="font-semibold mb-1" style={{ color: C.faint }}>{label}</p>
      <p style={{ color: C.sky }}>Forecast: {fmt(payload[0]?.value, 2)} GWh</p>
    </div>
  );
}

export default function ForecastLineChart({ data, height = 234 }) {
  const vals = data.map(d => d.total);
  const min = Math.min(...vals) - 15;
  const max = Math.max(...vals) + 15;

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={C.line} vertical={false} />
          <XAxis
            dataKey="year"
            tick={{ fontSize: 11, fill: C.faint }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[min, max]}
            tick={{ fontSize: 11, fill: C.faint }}
            axisLine={false}
            tickLine={false}
            width={52}
            tickFormatter={(v) => fmt(v, 0)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="total"
            stroke={C.blue}
            strokeWidth={2.5}
            dot={{ r: 4, fill: C.blue, strokeWidth: 0 }}
            name="total"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
