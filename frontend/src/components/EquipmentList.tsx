interface Props {
  equipment: Array<{
    model: string;
    quantity: number;
    unit_capacity: number;
    load_factor: number;
  }>;
}

export default function EquipmentList({ equipment }: Props) {
  if (equipment.length === 0) return null;
  return (
    <div style={{ marginTop: 24 }}>
      <h3 style={{ fontSize: 16, marginBottom: 8 }}>设备选型</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12 }}>
        {equipment.map((eq, i) => (
          <div key={i} style={{
            border: '1px solid #e0e0e0', borderRadius: 8, padding: 14,
            borderLeft: eq.load_factor > 1 ? '4px solid #e53e3e' : '4px solid #38a169',
            background: 'white'
          }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: 15 }}>{eq.model}</h4>
            <div style={{ fontSize: 13, color: '#555', lineHeight: 1.7 }}>
              <div>台数: <strong>{eq.quantity}</strong></div>
              <div>单机能力: {eq.unit_capacity.toFixed(0)} t/h</div>
              <div style={{ color: eq.load_factor > 1 ? '#e53e3e' : '#38a169', fontWeight: 600 }}>
                负荷率: {(eq.load_factor * 100).toFixed(1)}%
                {eq.load_factor > 1 ? ' ⚠ 超负荷' : ''}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
