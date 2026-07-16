import { C } from '../../lib/tokens';

export default function Panel({ title, subtitle, right, note, noPad, className = '', children }) {
  return (
    <section
      className={`bg-white rounded-xl border flex flex-col ${className}`}
      style={{ borderColor: C.line }}
    >
      {(title || right) && (
        <div
          className="flex items-start justify-between px-4 pt-4 pb-3"
          style={{ borderBottom: `1px solid ${C.line}` }}
        >
          <div>
            {title && (
              <h2 className="text-sm font-semibold leading-tight" style={{ color: C.ink, fontFamily: "'Sora', sans-serif" }}>
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-xs mt-0.5" style={{ color: C.faint }}>
                {subtitle}
              </p>
            )}
          </div>
          {right && <div className="ml-3 flex-shrink-0">{right}</div>}
        </div>
      )}
      <div className={`flex-1 ${noPad ? '' : 'p-4'}`}>
        {children}
      </div>
      {note && (
        <div
          className="px-4 py-2 text-xs"
          style={{ color: C.faint, borderTop: `1px solid ${C.line}`, fontSize: 11 }}
        >
          {note}
        </div>
      )}
    </section>
  );
}
