import React, { useState } from 'react';
import { Navbar } from './components/common/Navbar';
import { Dashboard } from './pages/Dashboard';
import { ObjectiveDetail } from './pages/ObjectiveDetail';
import { Marketplace } from './pages/Marketplace';
import { LedgerHistory } from './pages/LedgerHistory';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'marketplace' | 'ledger'>('dashboard');
  const [selectedObjectiveId, setSelectedObjectiveId] = useState<string | null>(null);

  const handleSelectObjective = (id: string) => {
    setSelectedObjectiveId(id);
    setCurrentTab('dashboard');
  };

  const handleBackToDashboard = () => {
    setSelectedObjectiveId(null);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setCurrentTab(tab);
          if (tab !== 'dashboard') {
            setSelectedObjectiveId(null);
          }
        }}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {currentTab === 'marketplace' && <Marketplace />}
        {currentTab === 'ledger' && <LedgerHistory />}
        {currentTab === 'dashboard' && (
          selectedObjectiveId ? (
            <ObjectiveDetail
              objectiveId={selectedObjectiveId}
              onBack={handleBackToDashboard}
            />
          ) : (
            <Dashboard onSelectObjective={handleSelectObjective} />
          )
        )}
      </main>

      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 bg-slate-950/60">
        The AI Economy MVP &copy; 2026. Built with FastAPI, LangGraph, React, PostgreSQL & PayPal Orders API v2.
      </footer>
    </div>
  );
};

export default App;
