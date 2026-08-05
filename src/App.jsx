import { useState } from 'react';
import TopNav from './components/layout/TopNav';
import Dashboard from './pages/Dashboard';
import Prediksi from './pages/Prediksi';
import GapAnalysis from './pages/GapAnalysis';
import DataEBT from './pages/DataEBT';
import { C } from './lib/tokens';

export default function App() {
  const [page, setPage] = useState('dashboard');
  return (
    <div className="min-h-screen" style={{ backgroundColor: C.bg, fontFamily: "'Inter', sans-serif" }}>
      <TopNav page={page} setPage={setPage} />
      <main className="max-w-[1320px] mx-auto px-6 py-5 space-y-4">
        {page === 'dashboard'  && <Dashboard go={setPage} />}
        {page === 'prediksi'   && <Prediksi />}
        {page === 'gap'        && <GapAnalysis />}
        {page === 'data'       && <DataEBT />}
      </main>
    </div>
  );
}
