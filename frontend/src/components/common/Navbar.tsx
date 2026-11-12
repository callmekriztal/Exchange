import React from 'react';
import { Coins, BookOpen, Layers, ShieldCheck, Activity } from 'lucide-react';

interface NavbarProps {
  currentTab: 'dashboard' | 'marketplace' | 'ledger';
  onSelectTab: (tab: 'dashboard' | 'marketplace' | 'ledger') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onSelectTab }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
        <div className="bg-emerald-500/20 text-emerald-400 p-2 rounded-lg border border-emerald-500/30">
          <Coins className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            The AI Economy
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Autonomous MVP
            </span>
          </h1>
          <p className="text-xs text-slate-400">Where AI Agents Discover, Negotiate & Trade</p>
        </div>
      </div>

      <nav className="flex items-center space-x-2">
        <button
          onClick={() => onSelectTab('dashboard')}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            currentTab === 'dashboard'
              ? 'bg-slate-800 text-white border border-slate-700'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>Objectives & Trades</span>
        </button>

        <button
          onClick={() => onSelectTab('marketplace')}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            currentTab === 'marketplace'
              ? 'bg-slate-800 text-white border border-slate-700'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>Agent Registry</span>
        </button>

        <button
          onClick={() => onSelectTab('ledger')}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            currentTab === 'ledger'
              ? 'bg-slate-800 text-white border border-slate-700'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
          }`}
        >
          <BookOpen className="w-4 h-4 text-amber-400" />
          <span>Accounting Ledger</span>
        </button>
      </nav>

      <div className="flex items-center space-x-3">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800">
          <ShieldCheck className="w-3.5 h-3.5 mr-1.5" /> PayPal Sandbox Active
        </span>
      </div>
    </header>
  );
};
