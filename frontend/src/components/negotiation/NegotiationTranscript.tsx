import React, { useState } from 'react';
import { Negotiation } from '../../types';
import { Bot, ChevronDown, ChevronUp, MessageSquare } from 'lucide-react';
import { formatDualCurrency } from '../../utils/currency';

interface Props {
  negotiation: Negotiation;
}

export const NegotiationTranscript: React.FC<Props> = ({ negotiation }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-slate-950/40 border border-slate-800/80 rounded-lg text-xs overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3.5 py-2 flex items-center justify-between text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 transition"
      >
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-medium text-slate-300">
            Price Negotiation ({negotiation.rounds?.length || 0} rounds)
          </span>
          <span
            className={`px-1.5 py-0.2 rounded text-[10px] font-mono uppercase ${
              negotiation.status === 'agreed'
                ? 'text-emerald-400'
                : 'text-amber-400'
            }`}
          >
            &middot; {negotiation.status}
          </span>
        </div>

        <div className="flex items-center space-x-2 text-[11px] text-slate-500">
          <span>{expanded ? 'Hide transcript' : 'View rounds'}</span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {expanded && (
        <div className="p-3.5 border-t border-slate-800/80 space-y-2.5 bg-slate-950/60">
          {negotiation.rounds.map((round) => {
            const isBuyer = round.action === 'offer' || (round.action === 'accept' && round.round_number === 3);

            return (
              <div
                key={round.id || round.round_number}
                className={`p-2.5 rounded-lg border text-xs leading-relaxed ${
                  isBuyer
                    ? 'bg-slate-900/60 border-slate-800'
                    : 'bg-slate-900/30 border-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-slate-300 flex items-center gap-1.5 text-[11px]">
                    <Bot className={`w-3 h-3 ${isBuyer ? 'text-emerald-400' : 'text-cyan-400'}`} />
                    {isBuyer ? 'Apex Buyer' : 'Seller Agent'} &middot; R{round.round_number}
                  </span>
                  <span className="font-mono text-emerald-400 font-semibold text-xs">
                    {formatDualCurrency(round.proposed_price_usd)}
                  </span>
                </div>
                <p className="text-slate-400 text-[11px]">{round.rationale}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
