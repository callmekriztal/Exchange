import React from 'react';
import { LedgerEntry } from '../../types';

interface Props {
  entries: LedgerEntry[];
}

export const LedgerTable: React.FC<Props> = ({ entries }) => {
  return (
    <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/60 border-b border-slate-800/80 text-slate-400 font-mono text-[10px] uppercase">
            <tr>
              <th className="py-2.5 px-4 font-medium">Time</th>
              <th className="py-2.5 px-4 font-medium">Type</th>
              <th className="py-2.5 px-4 font-medium">Debit</th>
              <th className="py-2.5 px-4 font-medium">Credit</th>
              <th className="py-2.5 px-4 font-medium">Amount</th>
              <th className="py-2.5 px-4 font-medium">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/40">
            {entries.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No ledger entries recorded yet.
                </td>
              </tr>
            ) : (
              entries.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-4 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                    {new Date(entry.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase bg-slate-800 text-slate-300 font-medium">
                      {entry.entry_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 font-mono text-slate-300 text-[11px]">{entry.debit_account}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-300 text-[11px]">{entry.credit_account}</td>
                  <td className="py-2.5 px-4 font-mono font-semibold text-emerald-400 whitespace-nowrap">
                    ${Number(entry.amount_usd).toFixed(2)}
                  </td>
                  <td className="py-2.5 px-4 text-slate-400 text-xs max-w-sm truncate">{entry.description}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
