import React, { useEffect, useState } from 'react';
import { Contract, Deliverable, Negotiation, Objective } from '../types';
import { api } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { NegotiationTranscript } from '../components/negotiation/NegotiationTranscript';
import { PayPalCheckoutCard } from '../components/payment/PayPalCheckoutCard';
import { DeliverableCard } from '../components/deliverables/DeliverableCard';
import {
  ArrowLeft,
  Bot,
  FileCheck2,
  RefreshCw,
} from 'lucide-react';
import { formatDualCurrency } from '../utils/currency';

interface Props {
  objectiveId: string;
  onBack: () => void;
}

export const ObjectiveDetail: React.FC<Props> = ({ objectiveId, onBack }) => {
  const [objective, setObjective] = useState<Objective | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [negotiations, setNegotiations] = useState<Record<string, Negotiation>>({});
  const [deliverables, setDeliverables] = useState<Record<string, Deliverable>>({});
  const [loading, setLoading] = useState(true);

  const { messages, isConnected } = useWebSocket(objectiveId);

  const loadData = async () => {
    try {
      const obj = await api.getObjective(objectiveId);
      setObjective(obj);

      const cts = await api.getContractsForObjective(objectiveId);
      setContracts(cts);

      // Load negotiations for subtasks
      for (const st of obj.subtasks || []) {
        try {
          const neg = await api.getNegotiation(st.id);
          setNegotiations((prev) => ({ ...prev, [st.id]: neg }));
        } catch {
          // not negotiated yet
        }
      }

      // Load deliverables for contracts
      for (const c of cts) {
        try {
          const deliv = await api.getDeliverable(c.id);
          setDeliverables((prev) => ({ ...prev, [c.id]: deliv }));
        } catch {
          // not delivered yet
        }
      }
    } catch (err) {
      console.error('Failed to load objective detail', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, [objectiveId]);

  // Handle incoming live websocket messages
  useEffect(() => {
    if (messages.length > 0) {
      loadData();
    }
  }, [messages]);

  if (loading && !objective) {
    return (
      <div className="flex items-center justify-center p-20 space-x-3 text-slate-400">
        <RefreshCw className="w-5 h-5 animate-spin text-emerald-400" />
        <span>Synchronizing LangGraph Multi-Agent State...</span>
      </div>
    );
  }

  if (!objective) {
    return <div className="p-8 text-center text-rose-400">Objective not found.</div>;
  }

  const steps = [
    { label: 'Planning', key: 'planning' },
    { label: 'Negotiation', key: 'negotiating' },
    { label: 'Payment Approval', key: 'awaiting_payment' },
    { label: 'Execution', key: 'in_progress' },
    { label: 'Completed', key: 'completed' },
  ];

  const getStepStatus = (stepKey: string) => {
    const order = ['planning', 'negotiating', 'awaiting_payment', 'in_progress', 'completed'];
    const currentIdx = order.indexOf(objective.status);
    const stepIdx = order.indexOf(stepKey);

    if (objective.status === 'completed') return 'completed';
    if (currentIdx > stepIdx) return 'completed';
    if (currentIdx === stepIdx) return 'current';
    return 'upcoming';
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition py-1"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Objectives</span>
        </button>

        <span className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-slate-600'}`} />
          <span>{isConnected ? 'Live sync' : 'Offline'}</span>
        </span>
      </div>

      {/* Goal Summary Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-medium ${
                objective.status === 'completed'
                  ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-900'
                  : objective.status === 'awaiting_payment'
                  ? 'bg-amber-950/60 text-amber-400 border border-amber-900'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {objective.status.replace('_', ' ')}
            </span>
            <h2 className="text-lg font-bold text-white tracking-tight">{objective.title}</h2>
          </div>
          <span className="font-mono text-emerald-400 font-semibold text-sm">
            Budget: {formatDualCurrency(Number(objective.max_budget_usd))}
          </span>
        </div>
        <p className="text-slate-400 text-xs leading-relaxed">{objective.description}</p>
      </div>

      {/* Compact Progress Stepper */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-lg px-4 py-2.5">
        <div className="flex items-center justify-between">
          {steps.map((st, i) => {
            const status = getStepStatus(st.key);
            return (
              <React.Fragment key={st.key}>
                <div className="flex items-center space-x-1.5 text-xs">
                  <span
                    className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-medium ${
                      status === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-400 font-bold'
                        : status === 'current'
                        ? 'bg-emerald-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-500'
                    }`}
                  >
                    {status === 'completed' ? '✓' : i + 1}
                  </span>
                  <span
                    className={`hidden sm:inline text-xs ${
                      status === 'completed'
                        ? 'text-slate-300'
                        : status === 'current'
                        ? 'text-white font-medium'
                        : 'text-slate-600'
                    }`}
                  >
                    {st.label}
                  </span>
                </div>
                {i < steps.length - 1 && (
                  <div
                    className={`flex-1 mx-2 h-0.5 rounded ${
                      status === 'completed' ? 'bg-emerald-500/40' : 'bg-slate-800'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Subtasks and Bilateral Negotiations */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <Bot className="w-4 h-4 text-emerald-400" />
          <span>Subtasks ({objective.subtasks?.length || 0})</span>
        </h3>

        <div className="space-y-3">
          {objective.subtasks?.map((st, idx) => {
            const neg = negotiations[st.id];
            return (
              <div key={st.id} className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-4 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-[10px] font-mono text-slate-400 uppercase">
                        #{idx + 1} &middot; {st.service_type}
                      </span>
                      <span className="text-slate-600">&middot;</span>
                      <span className="text-[11px] text-slate-400 capitalize">{st.status}</span>
                    </div>
                    <h4 className="text-sm font-medium text-white mt-0.5">{st.title}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{st.description}</p>
                  </div>

                  <div className="flex items-center space-x-3 text-xs self-start sm:self-auto shrink-0">
                    <span className="text-slate-500 text-[11px]">
                      Allocated: <span className="font-mono text-slate-300">{formatDualCurrency(Number(st.allocated_budget_usd))}</span>
                    </span>
                    <span className="font-mono text-emerald-400 font-semibold text-xs">
                      {st.agreed_price_usd ? formatDualCurrency(Number(st.agreed_price_usd)) : 'Negotiating'}
                    </span>
                  </div>
                </div>

                {/* Collapsible Alternating-Offer Protocol Visualizer */}
                {neg && <NegotiationTranscript negotiation={neg} />}
              </div>
            );
          })}
        </div>
      </div>

      {/* Human Checkout Gate (PayPal Orders API v2) */}
      {contracts.length > 0 && (
        <PayPalCheckoutCard
          objectiveId={objective.id}
          contracts={contracts}
          onPaymentSuccess={loadData}
        />
      )}

      {/* Deliverables & Evaluation Section */}
      {Object.keys(deliverables).length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-cyan-400" />
            <span>Executed Deliverables & Quality Evaluations</span>
          </h3>

          <div className="grid grid-cols-1 gap-4">
            {contracts.map((c) => {
              const deliv = deliverables[c.id];
              if (!deliv) return null;
              return (
                <DeliverableCard
                  key={c.id}
                  deliverable={deliv}
                  subtaskTitle={c.subtask?.title || 'Contract Deliverable'}
                />
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
