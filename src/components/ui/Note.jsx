import { Info, AlertTriangle } from 'lucide-react';
import { C } from '../../lib/tokens';

export default function Note({ children, tone = 'info' }) {
  const isWarn = tone === 'warn';
  const bg = isWarn ? C.goldSoft : C.blueSoft;
  const iconColor = isWarn ? C.warn : C.blue;
  const Icon = isWarn ? AlertTriangle : Info;
  return (
    <div
      className="flex gap-2.5 rounded-lg px-3 py-2.5"
      style={{ background: bg }}
    >
      <Icon size={14} color={iconColor} className="flex-shrink-0 mt-0.5" />
      <p className="text-xs leading-relaxed" style={{ color: C.ink }}>
        {children}
      </p>
    </div>
  );
}
