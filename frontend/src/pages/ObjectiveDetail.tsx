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
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-xs text-slate-400 hover:text-white transition bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/60"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Objectives</span>
        </button>

        <div className="flex items-center space-x-3">
          <span
            className={`inline-flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded-full border ${
              isConnected
                ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
            {isConnected ? 'Real-time WebSocket Live' : 'Polling Sync'}
          </span>
        </div>
      </div>

      {/* Goal Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <span className="text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded">
              Status: {objective.status.toUpperCase()}
            </span>
            <h2 className="text-2xl font-bold text-white mt-2">{objective.title}</h2>
          </div>
          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 text-right">
            <span className="text-[11px] text-slate-400">Authorized Human Budget</span>
            <p className="text-xl font-bold font-mono text-emerald-400">${Number(objective.max_budget_usd).toFixed(2)} USD</p>
          </div>
        </div>
        <p className="text-slate-300 text-xs leading-relaxed max-w-4xl">{objective.description}</p>
      </div>

      {/* Progress Stepper */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {steps.map((st, i) => {
            const status = getStepStatus(st.key);
            return (
              <div
                key={st.key}
                className={`flex items-center space-x-2 p-2.5 rounded-lg border text-xs font-medium transition ${
                  status === 'completed'
                    ? 'bg-emerald-950/30 border-emerald-800/80 text-emerald-300'
                    : status === 'current'
                    ? 'bg-cyan-950/40 border-cyan-600 text-cyan-200 animate-pulse'
                    : 'bg-slate-900/40 border-slate-800 text-slate-500'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    status === 'completed'
                      ? 'bg-emerald-500 text-slate-950'
                      : status === 'current'
                      ? 'bg-cyan-400 text-slate-950'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {status === 'completed' ? '✓' : i + 1}
                </div>
                <span>{st.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Subtasks and Bilateral Negotiations */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Bot className="w-5 h-5 text-emerald-400" />
          <span>Decomposed Subtasks & Bilateral Negotiations</span>
        </h3>

        <div className="space-y-4">
          {objective.subtasks?.map((st, idx) => {
            const neg = negotiations[st.id];
            return (
              <div key={st.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        Task #{idx + 1}: {st.service_type}
                      </span>
                      <span className="text-xs font-medium text-slate-400 capitalize">
                        Status: <strong className="text-white">{st.status}</strong>
                      </span>
                    </div>
                    <h4 className="text-base font-semibold text-white mt-1.5">{st.title}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{st.description}</p>
                  </div>

                  <div className="flex items-center space-x-4 bg-slate-950/80 border border-slate-800/80 px-4 py-2.5 rounded-lg text-xs">
                    <div>
                      <span className="text-[10px] text-slate-500 block">Budget Allocated</span>
                      <span className="font-mono text-slate-300 font-semibold">${Number(st.allocated_budget_usd).toFixed(2)}</span>
                    </div>
                    <div className="border-l border-slate-800 pl-4">
                      <span className="text-[10px] text-slate-500 block">Agreed Price</span>
                      <span className="font-mono text-emerald-400 font-bold">
                        {st.agreed_price_usd ? `$${Number(st.agreed_price_usd).toFixed(2)}` : 'In Negotiation...'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Alternating-Offer Protocol Visualizer */}
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
