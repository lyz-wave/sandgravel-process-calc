import { useState, useEffect } from 'react';
import { calculateBalance, BalanceResponse } from '../api/client';

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];
const PRODUCT_LABELS = ['80-40mm', '40-20mm', '20-5mm', '<5mm 机制砂'];

function fmtPct(v: number): string { return v.toFixed(2) + '%'; }
function fmtTph(v: number): string { return v.toFixed(1); }

export default function ComparePage() {
  const [opt1, setOpt1] = useState<BalanceResponse | null>(null);
  const [opt2, setOpt2] = useState<BalanceResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [r1, r2] = await Promise.all([
          calculateBalance({ config_name: 'option1' }),
          calculateBalance({ config_name: 'option2' }),
        ]);
        setOpt1(r1);
        setOpt2(r2);
      } catch (e: any) {
        alert('加载失败: ' + (e.response?.data?.detail || e.message));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <span>加载两方案数据</span>
        <span className="loading-dot" />
        <span className="loading-dot" />
        <span className="loading-dot" />
      </div>
    );
  }

  const getProducts = (r: BalanceResponse | null) => {
    if (!r?.products) return [0, 0, 0, 0];
    const p = r.products;
    return [p['40-80mm'] || 0, p['40-20mm'] || 0, p['20-5mm'] || 0, p['<5mm'] || 0];
  };
  const p1 = getProducts(opt1);
  const p2 = getProducts(opt2);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">方案对比</h1>
          <p className="page-subtitle">Option 1 (1500 T/H 爆破毛料) vs Option 2 (1100 T/H 天然砂石料)</p>
        </div>
      </div>

      {/* Key metrics grid */}
      <div className="metric-grid">
        {PRODUCT_LABELS.map((label, i) => {
          const v1 = p1[i] || 0;
          const v2 = p2[i] || 0;
          const diff = v2 - v1;
          const dir = diff > 0.01 ? 'up' : diff < -0.01 ? 'down' : 'neutral';
          return (
            <div key={i} className={`metric-card ${dir}`}>
              <div className="metric-label">{label}</div>
              <div className="metric-values">
                <div className="metric-val-group">
                  <span className="metric-val-label">方案1</span>
                  <span className="metric-val">{fmtPct(v1)}</span>
                </div>
                <div className="metric-val-group">
                  <span className="metric-val-label">方案2</span>
                  <span className="metric-val">{fmtPct(v2)}</span>
                </div>
              </div>
              <div className={`metric-diff ${diff > 0.01 ? 'pos' : diff < -0.01 ? 'neg' : 'zero'}`}>
                {diff > 0.01 ? '↑' : diff < -0.01 ? '↓' : '='} {Math.abs(diff).toFixed(2)}% vs 方案1
              </div>
            </div>
          );
        })}
      </div>

      {/* Detailed comparison */}
      <div className="option-panel">
        {[
          { name: '方案1 · 1500 T/H 爆破毛料', data: opt1, color: '#3b82f6' },
          { name: '方案2 · 1100 T/H 天然砂石料', data: opt2, color: '#ef4444' },
        ].map((opt, idx) => (
          <div key={idx} className="option-col">
            <div className="option-col-header" style={{ background: opt.color }}>
              <span>{opt.name}</span>
              <span className="meta">
                迭代{opt.data?.iterations}次 · 误差{opt.data?.convergence_error.toExponential(2)}
              </span>
            </div>
            <div className="option-col-body">
              {/* Streams table */}
              <table className="data-table">
                <thead>
                  <tr>
                    <th>物料流</th>
                    <th>t/h</th>
                    {SIZE_LABELS.map(l => <th key={l}>{l}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {opt.data && Object.entries(opt.data.streams).slice(0, 12).map(([name, s]) => (
                    <tr key={name}>
                      <td>{name}</td>
                      <td className="col-tonnage">{fmtTph(s.tonnage)}</td>
                      {s.grading.map((v, gi) => (
                        <td key={gi}>{v.toFixed(1)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Equipment chips */}
              {opt.data && opt.data.equipment.length > 0 && (
                <div style={{ marginTop: 14 }}>
                  <div style={{
                    fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)',
                    textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8,
                  }}>
                    设备配置
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {opt.data.equipment.map((eq, ei) => {
                      const over = eq.load_factor > 1;
                      return (
                        <span key={ei} style={{
                          padding: '3px 10px', borderRadius: 3, fontSize: '0.72rem',
                          fontFamily: 'var(--font-mono)',
                          background: over ? 'var(--red-glow)' : 'var(--green-glow)',
                          color: over ? 'var(--red)' : 'var(--green)',
                          border: `1px solid ${over ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}`,
                        }}>
                          {eq.model} × {eq.quantity} ({(eq.load_factor * 100).toFixed(0)}%)
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Design recommendation */}
      <div className="rec-box">
        <h3>设计建议</h3>
        <ul>
          <li><strong>高粗骨料需求</strong>（大坝混凝土）→ 选 <strong>方案1</strong>：爆破毛料经颚破+圆锥破产出更多 40-80mm、40-20mm 粗骨料</li>
          <li><strong>高机制砂需求</strong>（喷射混凝土/砂浆）→ 选 <strong>方案2</strong>：天然砂石料直接制砂，&lt;5mm 产率 49.54%，循环负荷更低</li>
          <li>方案1 循环负荷率更高（碎石 1.20×, 制砂 2.79×），设备配置更重</li>
          <li>方案2 无粗碎环节，流程更短，能耗更低</li>
        </ul>
      </div>
    </div>
  );
}
