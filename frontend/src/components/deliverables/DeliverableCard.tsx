import React, { useState } from 'react';
import { Deliverable } from '../../types';
import { ChevronDown, ChevronRight, Clock, Hash, ShieldCheck, Star } from 'lucide-react';

interface Props {
  deliverable: Deliverable;
  subtaskTitle: string;
}

export const DeliverableCard: React.FC<Props> = ({ deliverable, subtaskTitle }) => {
  const [expanded, setExpanded] = useState(false);
  const evaluation = deliverable.evaluation;

  return (
    <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
            {deliverable.artifact_type} deliverable
          </span>
          <h4 className="text-sm font-semibold text-white mt-1.5">{subtaskTitle}</h4>
        </div>

        {evaluation && (
          <div className="text-right">
            <span
              className={`inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full border ${
                evaluation.is_accepted
                  ? 'bg-emerald-950/80 text-emerald-400 border-emerald-800'
                  : 'bg-rose-950/80 text-rose-400 border-rose-800'
              }`}
            >
              <Star className="w-3.5 h-3.5 fill-current" />
              <span>Score: {evaluation.score}/100</span>
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 font-mono bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80">
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          Runtime: {deliverable.execution_duration_ms}ms
        </span>
        <span className="flex items-center gap-1 truncate max-w-xs">
          <Hash className="w-3.5 h-3.5 text-emerald-400" />
          SHA256: {deliverable.checksum.slice(0, 16)}...
        </span>
      </div>

      {evaluation && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 space-y-1.5">
          <div className="flex items-center space-x-1.5 text-emerald-400 font-semibold text-[11px]">
            <ShieldCheck className="w-4 h-4" />
            <span>Apex Buyer Agent Quality Audit</span>
          </div>
          <p className="italic text-slate-300">{evaluation.feedback}</p>
        </div>
      )}

      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium transition"
        >
          {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          <span>{expanded ? 'Hide Artifact Content' : 'Inspect Produced Deliverable'}</span>
        </button>

        {expanded && (
          <div className="mt-3 bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs font-mono text-slate-200 overflow-x-auto max-h-96">
            {deliverable.artifact_type === 'markdown' && deliverable.content.markdown_report ? (
              <pre className="whitespace-pre-wrap font-sans text-xs text-slate-200">
                {deliverable.content.markdown_report}
              </pre>
            ) : (
              <pre className="whitespace-pre-wrap">{JSON.stringify(deliverable.content, null, 2)}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
