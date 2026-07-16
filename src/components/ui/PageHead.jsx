import { C } from '../../lib/tokens';

export default function PageHead({ title, desc }) {
  return (
    <div
      className="rounded-xl px-5 py-4"
      style={{ background: C.green }}
    >
      <h1
        className="font-bold leading-tight"
        style={{ color: '#fff', fontSize: 16.5, fontFamily: "'Sora', sans-serif" }}
      >
        {title}
      </h1>
      {desc && (
        <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.85)' }}>
          {desc}
        </p>
      )}
    </div>
  );
}
