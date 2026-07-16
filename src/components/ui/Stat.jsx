import { C } from '../../lib/tokens';
import Tip from './Tip';

export default function Stat({ label, value, unit, sub, tone, icon: Icon, tip }) {
  const subColor = tone === 'up' ? C.ok : tone === 'down' ? C.red : C.faint;
  return (
    <div
      className="bg-white rounded-xl border p-4 flex flex-col gap-1"
      style={{ borderColor: C.line }}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium" style={{ color: C.muted }}>
          {label}
          {tip && <Tip text={tip} />}
        </span>
        {Icon && (
          <span className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: C.greenSoft }}>
            <Icon size={14} color={C.green} />
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span
          className="font-bold leading-none"
          style={{ fontSize: 22, color: C.ink, fontFamily: "'Sora', sans-serif" }}
        >
          {value}
        </span>
        {unit && (
          <span className="text-xs font-medium" style={{ color: C.muted }}>
            {unit}
          </span>
        )}
      </div>
      {sub && (
        <p className="text-xs leading-tight" style={{ color: subColor }}>
          {sub}
        </p>
      )}
    </div>
  );
}
