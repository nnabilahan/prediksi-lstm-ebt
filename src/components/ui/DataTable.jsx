import { C } from '../../lib/tokens';

export default function DataTable({ cols, rows, minWidth = 500 }) {
  return (
    <div className="overflow-x-auto" style={{ minWidth: 0 }}>
      <table
        style={{
          tableLayout: 'fixed',
          width: '100%',
          minWidth,
          borderCollapse: 'collapse',
          fontSize: 12.5,
        }}
      >
        <colgroup>
          {cols.map((c, i) => (
            <col key={i} style={{ width: c.width }} />
          ))}
        </colgroup>
        <thead>
          <tr style={{ borderBottom: `1px solid ${C.line}` }}>
            {cols.map((c, i) => (
              <th
                key={i}
                className="px-3 py-2 text-left font-semibold"
                style={{
                  color: C.muted,
                  fontSize: 11,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  textAlign: c.align || 'left',
                  whiteSpace: 'nowrap',
                }}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  );
}

export function Td({ children, align = 'left', mono = false, color }) {
  return (
    <td
      className="px-3 py-2"
      style={{
        textAlign: align,
        color: color || C.ink,
        fontFamily: mono ? "'IBM Plex Mono', monospace" : "'Inter', sans-serif",
        fontSize: mono ? 12 : 12.5,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      }}
    >
      {children}
    </td>
  );
}
