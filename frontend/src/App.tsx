import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import CalculatePage from './pages/CalculatePage';
import ComparePage from './pages/ComparePage';

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{
        background: '#0f1117', borderBottom: '1px solid #1e293b',
        padding: '0 24px', display: 'flex', gap: 24, alignItems: 'center', height: 44
      }}>
        <Link to="/" style={{ color: '#93c5fd', textDecoration: 'none', fontSize: 13, fontWeight: 500 }}>
          工艺计算
        </Link>
        <Link to="/compare" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: 13 }}>
          方案对比
        </Link>
      </nav>
      <Routes>
        <Route path="/" element={<CalculatePage />} />
        <Route path="/compare" element={<ComparePage />} />
      </Routes>
    </BrowserRouter>
  );
}
