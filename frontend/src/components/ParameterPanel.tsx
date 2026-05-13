import { useState } from 'react';
import { BalanceRequest } from '../api/client';

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

interface Props {
  onCalculate: (params: BalanceRequest) => void;
  loading: boolean;
}

export default function ParameterPanel({ onCalculate, loading }: Props) {
  const [grading, setGrading] = useState<number[]>([69, 12, 7, 7, 3, 2]);
  const [throughput, setThroughput] = useState(1500);
  const total = grading.reduce((a, b) => a + b, 0);

  return (
    <div style={{ border: '1px solid #e0e0e0', borderRadius: 8, padding: 20, background: '#fafafa' }}>
      <h3 style={{ margin: '0 0 12px 0', fontSize: 16 }}>原料参数</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12, marginBottom: 16 }}>
        {grading.map((v, i) => (
          <div key={i}>
            <label style={{ display: 'block', fontSize: 12, color: '#666', marginBottom: 4 }}>
              {SIZE_LABELS[i]} mm
            </label>
            <input type="number" value={v} min={0} max={100} step={0.1}
              onChange={e => {
                const next = [...grading];
                next[i] = Number(e.target.value);
                setGrading(next);
              }}
              style={{ width: '100%', padding: '6px 8px', border: '1px solid #ccc', borderRadius: 4, fontSize: 14 }}
            />
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginBottom: 12 }}>
        <p style={{ margin: 0, fontSize: 14, fontWeight: total === 100 ? 'normal' : 'bold',
          color: Math.abs(total - 100) > 0.1 ? '#e53e3e' : '#38a169' }}>
          合计: {total.toFixed(1)}% {Math.abs(total - 100) > 0.1 ? '(需为100%)' : '✓'}
        </p>
        <label style={{ fontSize: 14 }}>
          系统处理量:
          <input type="number" value={throughput} min={100} max={5000}
            onChange={e => setThroughput(Number(e.target.value))}
            style={{ marginLeft: 8, width: 100, padding: '6px 8px', border: '1px solid #ccc', borderRadius: 4 }}
          /> T/H
        </label>
      </div>
      <button
        disabled={loading || Math.abs(total - 100) > 0.1}
        onClick={() => onCalculate({ feed_grading: grading, system_throughput: throughput })}
        style={{
          padding: '10px 32px', fontSize: 15, fontWeight: 600,
          background: loading || Math.abs(total - 100) > 0.1 ? '#ccc' : '#3182ce',
          color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer'
        }}
      >
        {loading ? '计算中...' : '开始计算'}
      </button>
    </div>
  );
}
