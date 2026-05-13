interface Props {
  streams: Record<string, { tonnage: number; grading: number[] }>;
}

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

export default function BalanceTable({ streams }: Props) {
  const entries = Object.entries(streams);
  return (
    <div style={{ marginTop: 20 }}>
      <h3 style={{ fontSize: 16, marginBottom: 8 }}>物料平衡表</h3>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#edf2f7' }}>
              <th style={{ padding: '8px 12px', textAlign: 'left', borderBottom: '2px solid #cbd5e0' }}>名称</th>
              <th style={{ padding: '8px 12px', textAlign: 'right', borderBottom: '2px solid #cbd5e0' }}>吨位 (t/h)</th>
              {SIZE_LABELS.map(l => <th key={l} style={{ padding: '8px 6px', textAlign: 'right', borderBottom: '2px solid #cbd5e0' }}>{l}</th>)}
            </tr>
          </thead>
          <tbody>
            {entries.map(([name, stream], idx) => (
              <tr key={name} style={{ background: idx % 2 === 0 ? 'white' : '#f7fafc' }}>
                <td style={{ padding: '6px 12px', borderBottom: '1px solid #e2e8f0', fontWeight: 500 }}>{name}</td>
                <td style={{ padding: '6px 12px', textAlign: 'right', borderBottom: '1px solid #e2e8f0' }}>
                  {stream.tonnage.toFixed(1)}
                </td>
                {stream.grading.map((v, i) => (
                  <td key={i} style={{ padding: '6px 6px', textAlign: 'right', borderBottom: '1px solid #e2e8f0' }}>
                    {v.toFixed(2)}%
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
