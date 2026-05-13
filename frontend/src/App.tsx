import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import CalculatePage from './pages/CalculatePage';
import ComparePage from './pages/ComparePage';

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav-bar">
        <span className="nav-brand">SGC</span>
        <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          {({ isActive }) => <>{isActive && <span className="nav-indicator" />}工艺计算</>}
        </NavLink>
        <NavLink to="/compare" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          {({ isActive }) => <>{isActive && <span className="nav-indicator" />}方案对比</>}
        </NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<CalculatePage />} />
        <Route path="/compare" element={<ComparePage />} />
      </Routes>
    </BrowserRouter>
  );
}
