import React, { useEffect, useState } from 'react';
import { Agent } from '../types';
import { api } from '../services/api';
import { Bot, Coins, Layers, RefreshCw, Shield, Zap } from 'lucide-react';

export const Marketplace: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAgents = async () => {
    try {
      const list = await api.getAgents();
      setAgents(list);
    } catch (err) {
      console.error('Failed to load agents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span>Agent Registry ({agents.length})</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Registered autonomous agents and their specialized service toolchains.
          </p>
        </div>
        <button
          onClick={loadAgents}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500 text-xs">Loading agents...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-5 space-y-3.5"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700/60">
                    {agent.agent_type === 'buyer' ? (
                      <Bot className="w-4 h-4 text-emerald-400" />
                    ) : agent.agent_type === 'research' ? (
                      <Zap className="w-4 h-4 text-cyan-400" />
                    ) : agent.agent_type === 'analysis' ? (
                      <Coins className="w-4 h-4 text-amber-400" />
                    ) : (
                      <Shield className="w-4 h-4 text-purple-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{agent.name}</h3>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">
                      {agent.agent_type} agent
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-mono font-semibold text-emerald-400">
                    {agent.pricing_policy?.base_price
                      ? `$${agent.pricing_policy.base_price.toFixed(2)} base`
                      : 'Orchestrator'}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">{agent.description}</p>

              {agent.capabilities?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.map((cap) => (
                    <span
                      key={cap}
                      className="text-[10px] bg-slate-800/60 text-slate-400 px-2 py-0.5 rounded"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              )}

              {agent.services?.length > 0 && (
                <div className="border-t border-slate-800/60 pt-2.5 space-y-1.5">
                  {agent.services.map((srv) => (
                    <div key={srv.id} className="flex items-center justify-between text-xs py-1 text-slate-300">
                      <span className="font-medium text-[11px]">{srv.service_name}</span>
                      <span className="text-emerald-400 font-mono text-[11px]">
                        ${srv.min_price_usd.toFixed(2)} &ndash; ${srv.max_price_usd.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
