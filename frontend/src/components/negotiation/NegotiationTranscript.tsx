import React from 'react';
import { Negotiation } from '../../types';
import { Bot, CheckCircle2, MessageSquare } from 'lucide-react';

interface Props {
  negotiation: Negotiation;
}

export const NegotiationTranscript: React.FC<Props> = ({ negotiation }) => {
  return (
    <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-emerald-400" />
          <h4 className="text-sm font-semibold text-white">Multi-Agent Alternating-Offer Protocol</h4>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="text-slate-400">
            Rounds: <strong className="text-slate-200">{negotiation.current_round} / {negotiation.max_rounds}</strong>
          </span>
          <span
            className={`px-2 py-0.5 rounded-full font-medium uppercase text-[10px] ${
              negotiation.status === 'agreed'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}
          >
            {negotiation.status}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {negotiation.rounds.map((round) => {
          const isBuyer = round.action === 'offer' || (round.action === 'accept' && round.round_number === 3);

          return (
            <div
              key={round.id || round.round_number}
              className={`p-3.5 rounded-lg border text-xs leading-relaxed transition ${
                isBuyer
                  ? 'bg-slate-900/80 border-slate-700/80 ml-0 mr-8'
                  : 'bg-slate-900/40 border-cyan-900/40 ml-8 mr-0'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                  <Bot className={`w-3.5 h-3.5 ${isBuyer ? 'text-emerald-400' : 'text-cyan-400'}`} />
                  {isBuyer ? 'Apex Buyer Agent' : 'Candidate Seller Agent'} (Round {round.round_number})
                </span>
                <span className="font-mono text-emerald-400 font-semibold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900">
                  ${round.proposed_price_usd.toFixed(2)} USD
                </span>
              </div>
              <p className="text-slate-300 italic">{round.rationale}</p>
              <div className="mt-2 flex items-center text-[10px] uppercase font-mono text-slate-500">
                Action: <span className="text-slate-300 font-semibold ml-1">{round.action}</span>
              </div>
            </div>
          );
        })}
      </div>

      {negotiation.final_agreed_price_usd && (
        <div className="bg-emerald-950/30 border border-emerald-700/40 rounded-lg p-3 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-emerald-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Consensus Reached & Signed at Reservation Floor</span>
          </div>
          <span className="text-sm font-bold font-mono text-emerald-400">
            ${negotiation.final_agreed_price_usd.toFixed(2)} USD
          </span>
        </div>
      )}
    </div>
  );
};
