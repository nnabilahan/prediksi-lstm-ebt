import { useState } from 'react';
import { HelpCircle } from 'lucide-react';
import { C } from '../../lib/tokens';

export default function Tip({ text }) {
  const [show, setShow] = useState(false);
  if (!text) return null;
  return (
    <span className="relative inline-flex items-center ml-1">
      <button
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="focus:outline-none"
        style={{ color: C.faint }}
        tabIndex={-1}
      >
        <HelpCircle size={13} />
      </button>
      {show && (
        <span
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 z-50 w-56 rounded-lg px-3 py-2 text-xs shadow-lg pointer-events-none"
          style={{ background: C.ink, color: '#fff', lineHeight: 1.5 }}
        >
          {text}
          <span
            className="absolute top-full left-1/2 -translate-x-1/2"
            style={{
              borderLeft: '5px solid transparent',
              borderRight: '5px solid transparent',
              borderTop: `5px solid ${C.ink}`,
              width: 0,
              height: 0,
              display: 'block',
            }}
          />
        </span>
      )}
    </span>
  );
}
