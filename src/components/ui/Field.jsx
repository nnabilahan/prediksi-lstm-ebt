import { C } from '../../lib/tokens';

export default function Field({ label, children, className = '' }) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label className="text-xs font-medium" style={{ color: C.muted }}>
        {label}
      </label>
      {children}
    </div>
  );
}

export function inputStyle() {
  return {
    border: `1px solid ${C.line}`,
    borderRadius: 8,
    padding: '6px 10px',
    fontSize: 13,
    color: C.ink,
    background: '#fff',
    outline: 'none',
    width: '100%',
    fontFamily: "'Inter', sans-serif",
  };
}
