import React, { useEffect, useState } from 'react';
import { LedgerEntry } from '../types';
import { api } from '../services/api';
import { LedgerTable } from '../components/ledger/LedgerTable';
import { BookOpen, DollarSign, Lock, RefreshCw, ShieldCheck } from 'lucide-react';

export const LedgerHistory: React.FC = () => {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const loadEntries = async () => {
    try {
      const list = await api.getLedgerEntries();
      setEntries(list);
    } catch (err) {
      console.error('Failed to load ledger', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEntries();
  }, []);

  // Compute account balances
  const escrowLocked = entries
    .filter((e) => e.entry_type === 'escrow_lock')
    .reduce((sum, e) => sum + Number(e.amount_usd), 0);

  const sellerSettled = entries
    .filter((e) => e.entry_type === 'seller_settlement')
    .reduce((sum, e) => sum + Number(e.amount_usd), 0);

  const platformFees = entries
    .filter((e) => e.entry_type === 'platform_fee')
    .reduce((sum, e) => sum + Number(e.amount_usd), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-amber-400" />
            <span>Cryptographic Double-Entry Ledger</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Internal financial source of truth distinguishing PayPal fiat movement from autonomous agent micro-credits.
          </p>
        </div>
        <button
          onClick={loadEntries}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Account Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Cumulative Escrow Deposits</span>
            <Lock className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-blue-400">${escrowLocked.toFixed(2)} USD</p>
          <span className="text-[10px] text-slate-500 font-mono">Account: ESCROW_HOLD</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Settled Seller Earnings</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-emerald-400">${sellerSettled.toFixed(2)} USD</p>
          <span className="text-[10px] text-slate-500 font-mono">Account: SELLER_AGENT_BALANCE</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Marketplace Platform Fees</span>
            <ShieldCheck className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-bold font-mono text-purple-400">${platformFees.toFixed(2)} USD</p>
          <span className="text-[10px] text-slate-500 font-mono">Account: PLATFORM_FEE_REVENUE (5%)</span>
        </div>
      </div>

      {/* Ledger Table */}
      {loading ? (
        <div className="p-16 text-center text-slate-500 text-xs">Loading double-entry ledger...</div>
      ) : (
        <LedgerTable entries={entries} />
      )}
    </div>
  );
};
