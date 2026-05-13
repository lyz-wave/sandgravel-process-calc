import { useState } from 'react';
import ParameterPanel from '../components/ParameterPanel';
import FlowDiagram from '../components/FlowDiagram';
import BalanceTable from '../components/BalanceTable';
import EquipmentList from '../components/EquipmentList';
import ImportButton from '../components/ImportButton';
import { calculateBalance, exportToExcel, exportToPdf, BalanceResponse, BalanceRequest } from '../api/client';

export default function CalculatePage() {
  const [result, setResult] = useState<BalanceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [configName, setConfigName] = useState('option1');

  const handleCalculate = async (params: BalanceRequest) => {
    setLoading(true);
    try {
      const data = await calculateBalance({ ...params, config_name: configName });
      setResult(data);
    } catch (err: any) {
      alert('计算失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">砂石加工系统 工艺计算平台</h1>
          <p className="page-subtitle">Material Balance · Equipment Sizing · Process Flow</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            方案
          </span>
          <select className="select" value={configName} onChange={e => { setConfigName(e.target.value); setResult(null); }}>
            <option value="option1">Option 1 · 1500 T/H 爆破毛料</option>
            <option value="option2">Option 2 · 1100 T/H 天然砂石料</option>
          </select>
        </div>
      </div>

      <ParameterPanel onCalculate={handleCalculate} loading={loading} configName={configName} />

      {result && (
        <div className="anim-fade-in" style={{ marginTop: 'var(--space-lg)' }}>
          <div className="meta-bar">
            <span className="meta-stat">
              迭代 <strong>{result.iterations}</strong> 次
              <span style={{ margin: '0 12px', color: 'var(--border-default)' }}>|</span>
              收敛误差 <strong>{result.convergence_error.toExponential(3)}</strong>
            </span>
            <div className="meta-actions">
              <ImportButton onImported={setResult} />
              <button className="btn btn-green" onClick={() => exportToExcel(result)}>
                <span className="btn-icon">↓</span> Excel
              </button>
              <button className="btn btn-primary" onClick={() => exportToPdf({ ...result, config_name: configName }, 'full')}>
                <span className="btn-icon">↓</span> 计算报告 PDF
              </button>
              <button className="btn btn-ghost" onClick={() => exportToPdf({ ...result, config_name: configName }, 'equipment')}>
                <span className="btn-icon">↓</span> 选型报告 PDF
              </button>
            </div>
          </div>

          <FlowDiagram
            streams={result.streams}
            products={result.products}
            recircGt40={result.recirculation_gt40}
            recirc20_5={result.recirculation_20_5}
            flowStructure={result.flow_structure}
          />

          <div className="card" style={{ marginTop: 'var(--space-lg)' }}>
            <div className="card-header">物料平衡表</div>
            <div className="card-body" style={{ padding: 0, overflow: 'auto' }}>
              <BalanceTable streams={result.streams} />
            </div>
          </div>

          <div className="card" style={{ marginTop: 'var(--space-lg)' }}>
            <div className="card-header">设备选型</div>
            <div className="card-body">
              <EquipmentList equipment={result.equipment} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
