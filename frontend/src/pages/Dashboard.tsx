import React, { useEffect, useState } from 'react';
import { Objective } from '../types';
import { api } from '../services/api';
import { ArrowRight, Plus, RefreshCw, Sparkles, TrendingUp } from 'lucide-react';

interface Props {
  onSelectObjective: (id: string) => void;
}

export const Dashboard: React.FC<Props> = ({ onSelectObjective }) => {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [budget, setBudget] = useState('25.00');

  const loadObjectives = async () => {
    try {
      await api.loginOrRegisterDemo();
      await api.seedAgents();
      const list = await api.getObjectives();
      setObjectives(list);
    } catch (err) {
      console.error('Failed to load objectives', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadObjectives();
  }, []);

  const handleCreateObjective = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description || !budget) return;
    setCreating(true);
    try {
      const obj = await api.createObjective(title, description, parseFloat(budget));
      onSelectObjective(obj.id);
    } catch (err) {
      console.error('Failed to create objective', err);
    } finally {
      setCreating(false);
    }
  };

  const handlePreset = (presetTitle: string, presetDesc: string, presetBudget: string) => {
    setTitle(presetTitle);
    setDescription(presetDesc);
    setBudget(presetBudget);
  };

  return (
    <div className="space-y-8">
      {/* Hero & Objective Submission */}
      <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-cyan-950/40 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="max-w-3xl mb-6">
          <span className="inline-flex items-center gap-1.5 text-xs font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full mb-3">
            <Sparkles className="w-3.5 h-3.5" /> Autonomous Marketplace Engine
          </span>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Deploy an Objective. Let AI Agents Trade & Deliver.
          </h2>
          <p className="text-slate-300 text-xs leading-relaxed mt-2">
            Set strategic goals and a budget ceiling. The Buyer Agent decomposes the work into specialized subtasks, queries the marketplace registry, negotiates bilateral prices, and seeks your PayPal approval before executing.
          </p>
        </div>

        <form onSubmit={handleCreateObjective} className="space-y-4 max-w-3xl bg-slate-950/60 p-6 rounded-xl border border-slate-800/80">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase font-mono mb-1.5">
              Strategic Objective Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Next-Gen Solid State Battery Market Brief"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase font-mono mb-1.5">
              Detailed Scope & Requirements
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="e.g. Research current manufacturing cathode chemistry breakthroughs, perform 5-year commercial cost CAGR modeling, and synthesize an executive roadmap."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              required
            />
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <div className="w-full sm:w-64">
              <label className="block text-xs font-semibold text-slate-300 uppercase font-mono mb-1.5">
                Maximum Budget Limit (USD)
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 text-xs font-mono">$</span>
                <input
                  type="number"
                  step="0.50"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-7 pr-3 py-2 text-xs font-mono font-bold text-emerald-400 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={creating}
                className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 px-6 rounded-lg text-xs transition flex items-center justify-center space-x-2 shadow-lg shadow-emerald-950/60 disabled:opacity-50"
              >
                <Plus className="w-4 h-4" />
                <span>{creating ? 'Decomposing Tasks...' : 'Launch Autonomous Trade'}</span>
              </button>
            </div>
          </div>

          {/* Quick presets */}
          <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-[11px] text-slate-500 font-mono">Sample Presets:</span>
            <button
              type="button"
              onClick={() =>
                handlePreset(
                  'Global Solar & Wind Energy Forecast 2026',
                  'Research grid-scale storage advancements, compute levelized cost of energy (LCOE) variance, and generate an executive report.',
                  '25.00'
                )
              }
              className="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded border border-slate-700 transition"
            >
              Solar & Wind Forecast ($25)
            </button>
            <button
              type="button"
              onClick={() =>
                handlePreset(
                  'AI Semiconductor Silicon Economics',
                  'Analyze wafer fabrication capacity, compute 3nm chip yield CAGRs, and compile strategic procurement findings.',
                  '30.00'
                )
              }
              className="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded border border-slate-700 transition"
            >
              AI Silicon Economics ($30)
            </button>
          </div>
        </form>
      </div>

      {/* Active Objectives List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">Active Market Objectives & Trades</h3>
          </div>
          <button
            onClick={loadObjectives}
            className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs">Loading marketplace objectives...</div>
        ) : objectives.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400 text-xs">
            No objectives created yet. Submit an objective above to watch AI agents negotiate and trade!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {objectives.map((obj) => (
              <div
                key={obj.id}
                onClick={() => onSelectObjective(obj.id)}
                className="bg-slate-900/90 hover:bg-slate-800/80 border border-slate-800 hover:border-emerald-600/50 rounded-xl p-5 cursor-pointer transition shadow-lg space-y-3 group"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-0.5 rounded font-mono text-[10px] uppercase font-bold ${
                      obj.status === 'completed'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : obj.status === 'awaiting_payment'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800 animate-pulse'
                        : 'bg-cyan-950 text-cyan-400 border border-cyan-800'
                    }`}
                  >
                    {obj.status}
                  </span>
                  <span className="font-mono text-emerald-400 font-bold text-sm">
                    ${Number(obj.max_budget_usd).toFixed(2)} USD
                  </span>
                </div>

                <div>
                  <h4 className="text-base font-bold text-white group-hover:text-emerald-300 transition">
                    {obj.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{obj.description}</p>
                </div>

                <div className="border-t border-slate-800/80 pt-3 flex items-center justify-between text-xs text-slate-400">
                  <span>{obj.subtasks?.length || 0} Subtasks Decomposed</span>
                  <span className="flex items-center gap-1 text-emerald-400 font-medium group-hover:translate-x-1 transition">
                    <span>View Live Trading</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
