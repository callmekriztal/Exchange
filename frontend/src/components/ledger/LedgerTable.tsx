import React from 'react';
import { LedgerEntry } from '../../types';
import { BookOpen } from 'lucide-react';

interface Props {
  entries: LedgerEntry[];
}

export const LedgerTable: React.FC<Props> = ({ entries }) => {
  return (
    <div className="bg-slate-950/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-amber-400" />
          <h3 className="font-bold text-white text-base">Internal Double-Entry Ledger</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Total Entries: {entries.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase font-mono text-[10px]">
            <tr>
              <th className="py-3 px-4">Date / Time</th>
              <th className="py-3 px-4">Entry Type</th>
              <th className="py-3 px-4">Debit Account</th>
              <th className="py-3 px-4">Credit Account</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {entries.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No ledger entries recorded yet.
                </td>
              </tr>
            ) : (
              entries.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3 px-4 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                    {new Date(entry.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded font-mono text-[10px] uppercase font-semibold ${
                        entry.entry_type === 'escrow_lock'
                          ? 'bg-blue-950 text-blue-400 border border-blue-800'
                          : entry.entry_type === 'seller_settlement'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-purple-950 text-purple-400 border border-purple-800'
                      }`}
                    >
                      {entry.entry_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-rose-400 font-medium">{entry.debit_account}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400 font-medium">{entry.credit_account}</td>
                  <td className="py-3 px-4 font-mono font-bold text-white whitespace-nowrap">
                    ${Number(entry.amount_usd).toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-sm truncate">{entry.description}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
