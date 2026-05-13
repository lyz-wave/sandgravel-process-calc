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
    <div className="eq-grid">
      {equipment.map((eq, i) => {
        const overloaded = eq.load_factor > 1;
        return (
          <div key={i} className={`eq-card ${overloaded ? 'warn' : 'ok'}`}>
            <div className="eq-model">{eq.model}</div>
            <div className="eq-stats">
              <div className="eq-stat">
                <span className="eq-stat-label">台数</span>
                <span className="eq-stat-value">{eq.quantity}</span>
              </div>
              <div className="eq-stat">
                <span className="eq-stat-label">单机能力</span>
                <span className="eq-stat-value">{eq.unit_capacity.toFixed(0)} t/h</span>
              </div>
            </div>
            <div className="eq-load-pct">
              <span className={`eq-load ${overloaded ? 'over' : 'good'}`}>
                负荷率 {(eq.load_factor * 100).toFixed(1)}%
              </span>
              {overloaded && <span style={{ marginLeft: 8, fontSize: '0.7rem', color: 'var(--red)' }}>超负荷</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
