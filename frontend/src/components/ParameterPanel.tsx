import { useState, useEffect } from 'react';
import { BalanceRequest, getConfigDefaults } from '../api/client';

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

interface Props {
  onCalculate: (params: BalanceRequest) => void;
  loading: boolean;
  configName: string;
}

export default function ParameterPanel({ onCalculate, loading, configName }: Props) {
  const [grading, setGrading] = useState<number[]>([69, 12, 7, 7, 3, 2]);
  const [throughput, setThroughput] = useState(1500);
  const [defaultsLoaded, setDefaultsLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getConfigDefaults(configName).then(d => {
      if (cancelled) return;
      setGrading(d.feed_grading);
      setThroughput(d.system_throughput);
      setDefaultsLoaded(true);
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [configName]);

  const total = grading.reduce((a, b) => a + b, 0);
  const valid = Math.abs(total - 100) <= 0.1;

  return (
    <div className="param-panel">
      <div className="param-section-title">原料级配参数</div>

      <div className="param-grid">
        {grading.map((v, i) => (
          <div key={i}>
            <label className="param-label">{SIZE_LABELS[i]} mm</label>
            <input
              type="number" value={v} min={0} max={100} step={0.1}
              className="input"
              onChange={e => {
                const next = [...grading];
                next[i] = Number(e.target.value);
                setGrading(next);
              }}
            />
          </div>
        ))}
      </div>

      <div className="param-row">
        <span className={`param-total ${valid ? 'valid' : 'invalid'}`}>
          Σ {total.toFixed(1)}% {valid ? '✓' : '(需为100%)'}
        </span>

        <label className="param-throughput">
          系统处理量
          <input
            type="number" value={throughput} min={100} max={5000}
            className="input"
            onChange={e => setThroughput(Number(e.target.value))}
          />
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>T/H</span>
        </label>
      </div>

      <button
        className="btn btn-amber"
        disabled={loading || !valid}
        onClick={() => onCalculate({ feed_grading: grading, system_throughput: throughput })}
      >
        {loading ? '计算中...' : '开始计算'}
      </button>
    </div>
  );
}
