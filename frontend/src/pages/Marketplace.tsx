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
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            <span>Agent Registry & Service Catalog</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous economic actors registered in the marketplace with distinct pricing policies and toolchains.
          </p>
        </div>
        <button
          onClick={loadAgents}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Catalog</span>
        </button>
      </div>

      {loading ? (
        <div className="p-16 text-center text-slate-500 text-xs">Loading Agent Catalog...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className={`p-2.5 rounded-xl border ${
                      agent.agent_type === 'buyer'
                        ? 'bg-emerald-950/80 border-emerald-800 text-emerald-400'
                        : agent.agent_type === 'research'
                        ? 'bg-cyan-950/80 border-cyan-800 text-cyan-400'
                        : agent.agent_type === 'analysis'
                        ? 'bg-amber-950/80 border-amber-800 text-amber-400'
                        : 'bg-purple-950/80 border-purple-800 text-purple-400'
                    }`}
                  >
                    {agent.agent_type === 'buyer' ? (
                      <Bot className="w-6 h-6" />
                    ) : agent.agent_type === 'research' ? (
                      <Zap className="w-6 h-6" />
                    ) : agent.agent_type === 'analysis' ? (
                      <Coins className="w-6 h-6" />
                    ) : (
                      <Shield className="w-6 h-6" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{agent.name}</h3>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      Type: {agent.agent_type}
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-right">
                  <span className="text-[10px] text-slate-500 uppercase block font-mono">Pricing Model</span>
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    {agent.pricing_policy?.base_price
                      ? `$${agent.pricing_policy.base_price.toFixed(2)} Base`
                      : 'Orchestrator'}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{agent.description}</p>

              <div>
                <h5 className="text-[10px] uppercase font-mono text-slate-500 font-semibold mb-2">Capabilities</h5>
                <div className="flex flex-wrap gap-1.5">
                  {agent.capabilities?.map((cap) => (
                    <span
                      key={cap}
                      className="text-[10px] font-mono bg-slate-800/80 text-slate-300 border border-slate-700/60 px-2 py-0.5 rounded"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>

              {agent.services?.length > 0 && (
                <div className="border-t border-slate-800/80 pt-3">
                  <h5 className="text-[10px] uppercase font-mono text-slate-500 font-semibold mb-2">Published Services</h5>
                  <div className="space-y-2">
                    {agent.services.map((srv) => (
                      <div key={srv.id} className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs space-y-1">
                        <div className="flex justify-between font-semibold text-white">
                          <span>{srv.service_name}</span>
                          <span className="text-emerald-400 font-mono">
                            ${srv.min_price_usd.toFixed(2)} - ${srv.max_price_usd.toFixed(2)}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">{srv.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
