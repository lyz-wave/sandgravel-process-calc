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
      } catch (e: any) { alert('加载失败: ' + (e.response?.data?.detail || e.message)); }
      finally { setLoading(false); }
    }
    load();
  }, []);

  if (loading) return <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>加载两方案数据中...</div>;

  const getProducts = (r: BalanceResponse | null) => {
    if (!r?.products) return [0, 0, 0, 0];
    const p = r.products;
    return [p['40-80mm'] || 0, p['40-20mm'] || 0, p['20-5mm'] || 0, p['<5mm'] || 0];
  };
  const p1 = getProducts(opt1);
  const p2 = getProducts(opt2);

  return (
    <div style={{ maxWidth: 1300, margin: '0 auto', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: 22, marginBottom: 4 }}>方案对比</h1>
      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 24 }}>
        Option1 (1500T/H, 爆破毛料) vs Option2 (1100T/H, 天然砂石料)
      </p>

      {/* Key metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        {PRODUCT_LABELS.map((label, i) => {
          const v1 = p1[i] || 0;
          const v2 = p2[i] || 0;
          const diff = v2 - v1;
          return (
            <div key={i} style={{
              border: '1px solid #e2e8f0', borderRadius: 8, padding: 16, background: 'white',
              borderLeft: `4px solid ${diff > 0 ? '#38a169' : diff < 0 ? '#e53e3e' : '#cbd5e0'}`
            }}>
              <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>{label}</div>
              <div style={{ display: 'flex', gap: 16, marginBottom: 4 }}>
                <div><span style={{ fontSize: 11, color: '#94a3b8' }}>方案1 </span>
                  <strong style={{ fontSize: 16 }}>{fmtPct(v1)}</strong></div>
                <div><span style={{ fontSize: 11, color: '#94a3b8' }}>方案2 </span>
                  <strong style={{ fontSize: 16 }}>{fmtPct(v2)}</strong></div>
              </div>
              <div style={{ fontSize: 12, color: diff > 0 ? '#38a169' : diff < 0 ? '#e53e3e' : '#718096' }}>
                {diff > 0 ? '↑' : diff < 0 ? '↓' : '='} {Math.abs(diff).toFixed(2)}%
              </div>
            </div>
          );
        })}
      </div>

      {/* Detailed comparison table */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {[
          { name: '方案1 (1500T/H 爆破毛料)', data: opt1, color: '#3182ce' },
          { name: '方案2 (1100T/H 天然砂石料)', data: opt2, color: '#e53e3e' },
        ].map((opt, idx) => (
          <div key={idx} style={{
            border: '1px solid #e2e8f0', borderRadius: 8, overflow: 'hidden'
          }}>
            <div style={{
              background: opt.color, color: 'white', padding: '10px 16px',
              fontSize: 14, fontWeight: 600
            }}>
              {opt.name}
              <span style={{ marginLeft: 8, fontSize: 12, opacity: 0.8 }}>
                迭代{opt.data?.iterations}次 · 误差{opt.data?.convergence_error.toExponential(2)}
              </span>
            </div>
            <div style={{ padding: 12, overflow: 'auto' }}>
              <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f7fafc' }}>
                    <th style={{ padding: '6px 8px', textAlign: 'left', borderBottom: '2px solid #e2e8f0' }}>物料流</th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', borderBottom: '2px solid #e2e8f0' }}>t/h</th>
                    {SIZE_LABELS.map(l => (
                      <th key={l} style={{ padding: '4px 4px', textAlign: 'right', borderBottom: '2px solid #e2e8f0', fontSize: 10 }}>{l}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {opt.data && Object.entries(opt.data.streams).slice(0, 12).map(([name, s], ri) => (
                    <tr key={name} style={{ background: ri % 2 === 0 ? 'white' : '#f7fafc' }}>
                      <td style={{ padding: '4px 8px', borderBottom: '1px solid #edf2f7', fontSize: 11 }}>{name}</td>
                      <td style={{ padding: '4px 8px', textAlign: 'right', borderBottom: '1px solid #edf2f7' }}>{fmtTph(s.tonnage)}</td>
                      {s.grading.map((v, gi) => (
                        <td key={gi} style={{ padding: '2px 4px', textAlign: 'right', borderBottom: '1px solid #edf2f7', fontSize: 11 }}>{v.toFixed(1)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Equipment summary */}
            {opt.data && opt.data.equipment.length > 0 && (
              <div style={{ padding: '0 12px 12px' }}>
                <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6, color: '#4a5568' }}>设备配置</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {opt.data.equipment.map((eq, ei) => (
                    <span key={ei} style={{
                      padding: '3px 8px', borderRadius: 4, fontSize: 11,
                      background: eq.load_factor > 1 ? '#fed7d7' : '#c6f6d5',
                      color: eq.load_factor > 1 ? '#9b2c2c' : '#276749',
                    }}>
                      {eq.model}×{eq.quantity} ({(eq.load_factor * 100).toFixed(0)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Design recommendation */}
      <div style={{
        marginTop: 24, padding: 16, borderRadius: 8,
        background: '#ebf8ff', border: '1px solid #bee3f8'
      }}>
        <h3 style={{ margin: '0 0 8px', fontSize: 14, color: '#2b6cb0' }}>设计建议</h3>
        <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: '#2d3748', lineHeight: 1.7 }}>
          <li><strong>高粗骨料需求</strong>（大坝混凝土）→ 选 <strong>方案1</strong>：爆破毛料经颚破+圆锥破产出更多 40-80mm、40-20mm 粗骨料</li>
          <li><strong>高机制砂需求</strong>（喷射混凝土/砂浆）→ 选 <strong>方案2</strong>：天然砂石料直接制砂，{'<5mm'} 产率 49.54%，循环负荷更低</li>
          <li>方案1 循环负荷率更高（碎石 1.20×, 制砂 2.79×），设备配置更重</li>
          <li>方案2 无粗碎环节，流程更短，能耗更低</li>
        </ul>
      </div>
    </div>
  );
}
