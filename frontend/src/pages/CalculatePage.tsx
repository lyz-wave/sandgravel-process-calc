import { useState } from 'react';
import ParameterPanel from '../components/ParameterPanel';
import FlowDiagram from '../components/FlowDiagram';
import BalanceTable from '../components/BalanceTable';
import EquipmentList from '../components/EquipmentList';
import ImportButton from '../components/ImportButton';
import { calculateBalance, exportToExcel, BalanceResponse, BalanceRequest } from '../api/client';

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
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0, fontSize: 24 }}>砂石加工系统 工艺计算平台</h1>
        <div>
          <label style={{ marginRight: 8 }}>方案:</label>
          <select value={configName} onChange={e => setConfigName(e.target.value)}
            style={{ padding: '6px 12px', fontSize: 14 }}>
            <option value="option1">方案1 (1500T/H)</option>
            <option value="option2">方案2 (1100T/H)</option>
          </select>
        </div>
      </div>

      <ParameterPanel onCalculate={handleCalculate} loading={loading} />

      {result && (
        <div style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ color: '#666', fontSize: 14 }}>
              迭代{result.iterations}次 · 收敛误差 {result.convergence_error.toExponential(3)}
            </span>
            <div style={{ display: 'flex', gap: 8 }}>
              <ImportButton onImported={setResult} />
              <button
                onClick={() => exportToExcel(result)}
                style={{
                  padding: '8px 20px', fontSize: 13, fontWeight: 600,
                  background: '#10b981', color: 'white', border: 'none',
                  borderRadius: 6, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 6,
                }}
              >
                <span style={{ fontSize: 16 }}>↓</span> 导出 Excel
              </button>
            </div>
          </div>
          <FlowDiagram streams={result.streams} products={result.products}
            recircGt40={result.recirculation_gt40} recirc20_5={result.recirculation_20_5} />
          <div style={{ marginTop: 24 }}>
            <BalanceTable streams={result.streams} />
          </div>
          <EquipmentList equipment={result.equipment} />
        </div>
      )}
    </div>
  );
}
