import { C } from '../../lib/tokens';
import { fmt } from '../../lib/utils';

function polarToCartesian(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx, cy, r, startAngle, endAngle) {
  const s = polarToCartesian(cx, cy, r, startAngle);
  const e = polarToCartesian(cx, cy, r, endAngle);
  const large = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
}

export default function Gauge({ value = 0, size = 168, label = 'Akurasi Model' }) {
  const cx = size / 2;
  const cy = size / 2 + 8;
  const r = size * 0.38;
  const strokeW = size * 0.072;

  // Arc spans from 180° to 360° (bottom half of circle = half arc)
  const startAngle = 180;
  const endAngle = 360;
  const totalSpan = endAngle - startAngle;

  const progressAngle = startAngle + (Math.min(Math.max(value, 0), 100) / 100) * totalSpan;

  const trackColor = value < 75 ? '#E5E7EB' : '#E5E7EB';
  const progressColor = value >= 90 ? C.ok : value >= 75 ? C.gold : C.red;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size * 0.62} viewBox={`0 0 ${size} ${size * 0.62}`}>
        {/* Track segments */}
        <path
          d={arcPath(cx, cy, r, 180, 270)}
          fill="none"
          stroke="#E9ECEF"
          strokeWidth={strokeW}
          strokeLinecap="round"
        />
        <path
          d={arcPath(cx, cy, r, 270, 315)}
          fill="none"
          stroke="#DEE2E6"
          strokeWidth={strokeW}
          strokeLinecap="round"
        />
        <path
          d={arcPath(cx, cy, r, 315, 360)}
          fill="none"
          stroke="#CED4DA"
          strokeWidth={strokeW}
          strokeLinecap="round"
        />
        {/* Progress */}
        {value > 0 && (
          <path
            d={arcPath(cx, cy, r, startAngle, progressAngle)}
            fill="none"
            stroke={progressColor}
            strokeWidth={strokeW}
            strokeLinecap="round"
          />
        )}
        {/* Center text */}
        <text
          x={cx}
          y={cy - r * 0.05}
          textAnchor="middle"
          dominantBaseline="middle"
          style={{
            fontFamily: "'Sora', sans-serif",
            fontWeight: 700,
            fontSize: size * 0.155,
            fill: C.ink,
          }}
        >
          {fmt(value, 1)}%
        </text>
      </svg>
      <p className="text-xs text-center" style={{ color: C.muted, marginTop: -4 }}>
        {label}
      </p>
    </div>
  );
}
