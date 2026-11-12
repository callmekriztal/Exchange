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
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-amber-400" />
            <span>Accounting Ledger ({entries.length} entries)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Double-entry financial journal tracking escrow locks and agent settlements.
          </p>
        </div>
        <button
          onClick={loadEntries}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Account Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Escrow Deposits</span>
            <Lock className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <p className="text-xl font-bold font-mono text-white">${escrowLocked.toFixed(2)}</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Seller Settlements</span>
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <p className="text-xl font-bold font-mono text-white">${sellerSettled.toFixed(2)}</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Platform Fees (5%)</span>
            <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <p className="text-xl font-bold font-mono text-white">${platformFees.toFixed(2)}</p>
        </div>
      </div>

      {/* Ledger Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-500 text-xs">Loading ledger...</div>
      ) : (
        <LedgerTable entries={entries} />
      )}
    </div>
  );
};
