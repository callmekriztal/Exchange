import React, { useState } from 'react';
import { Deliverable } from '../../types';
import { ChevronDown, ChevronRight, Star } from 'lucide-react';

interface Props {
  deliverable: Deliverable;
  subtaskTitle: string;
}

export const DeliverableCard: React.FC<Props> = ({ deliverable, subtaskTitle }) => {
  const [expanded, setExpanded] = useState(false);
  const evaluation = deliverable.evaluation;

  return (
    <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-[10px] font-mono text-slate-500 uppercase">
            {deliverable.artifact_type} deliverable &middot; {deliverable.execution_duration_ms}ms
          </span>
          <h4 className="text-sm font-semibold text-white mt-0.5">{subtaskTitle}</h4>
        </div>

        {evaluation && (
          <span
            className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
              evaluation.is_accepted
                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-900'
                : 'bg-rose-950/60 text-rose-400 border-rose-900'
            }`}
          >
            <Star className="w-3 h-3 fill-current" />
            <span>{evaluation.score}/100</span>
          </span>
        )}
      </div>

      {evaluation?.feedback && (
        <p className="text-xs text-slate-400 italic bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/50">
          "{evaluation.feedback}"
        </p>
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
