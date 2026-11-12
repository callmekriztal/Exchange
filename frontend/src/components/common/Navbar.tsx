import React from 'react';
import { Coins, BookOpen, Layers, Activity } from 'lucide-react';

interface NavbarProps {
  currentTab: 'dashboard' | 'marketplace' | 'ledger';
  onSelectTab: (tab: 'dashboard' | 'marketplace' | 'ledger') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onSelectTab }) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-2.5 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
        <div className="bg-emerald-500/10 text-emerald-400 p-1.5 rounded-lg border border-emerald-500/20">
          <Coins className="w-5 h-5" />
        </div>
        <span className="text-base font-bold tracking-tight text-white">
          The AI Economy
        </span>
      </div>

      <nav className="flex items-center space-x-1 sm:space-x-2">
        <button
          onClick={() => onSelectTab('dashboard')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            currentTab === 'dashboard'
              ? 'bg-slate-800 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
          }`}
        >
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span>Objectives & Trades</span>
        </button>

        <button
          onClick={() => onSelectTab('marketplace')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            currentTab === 'marketplace'
              ? 'bg-slate-800 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
          }`}
        >
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>Agent Registry</span>
        </button>

        <button
          onClick={() => onSelectTab('ledger')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            currentTab === 'ledger'
              ? 'bg-slate-800 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5 text-amber-400" />
          <span>Ledger</span>
        </button>
      </nav>

      <div className="flex items-center space-x-2">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium text-slate-400 bg-slate-900 border border-slate-800">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span>PayPal Sandbox</span>
        </span>
      </div>
    </header>
  );
};
