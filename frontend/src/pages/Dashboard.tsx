import React, { useEffect, useState } from 'react';
import { Objective } from '../types';
import { api } from '../services/api';
import { ArrowRight, Plus, RefreshCw, TrendingUp } from 'lucide-react';

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
      {/* Objective Creation Form */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="mb-5">
          <h2 className="text-xl font-bold text-white tracking-tight">New Objective</h2>
          <p className="text-xs text-slate-400 mt-1">
            Specify your goal and budget ceiling. Agents will autonomously decompose, negotiate, and fulfill the tasks.
          </p>
        </div>

        <form onSubmit={handleCreateObjective} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Objective Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Solid State Battery Market Analysis"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/80 transition"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Scope & Deliverables
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="e.g. Research cathode chemistry breakthroughs, model 5-year cost CAGRs, and compile an executive summary."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/80 transition"
              required
            />
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
            <div className="flex items-center gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Max Budget</label>
                <div className="relative w-32">
                  <span className="absolute inset-y-0 left-0 pl-2.5 flex items-center text-slate-400 text-xs">$</span>
                  <input
                    type="number"
                    step="0.50"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-6 pr-2.5 py-1.5 text-xs font-mono font-semibold text-emerald-400 focus:outline-none focus:border-emerald-500/80"
                    required
                  />
                </div>
              </div>

              <div className="hidden md:flex items-center gap-1.5 pt-4">
                <span className="text-[11px] text-slate-500">Presets:</span>
                <button
                  type="button"
                  onClick={() =>
                    handlePreset(
                      'Global Solar & Wind Energy Forecast 2026',
                      'Research grid-scale storage advancements, compute LCOE variance, and synthesize an executive report.',
                      '25.00'
                    )
                  }
                  className="text-[11px] text-slate-400 hover:text-slate-200 bg-slate-800/50 hover:bg-slate-800 px-2 py-1 rounded transition"
                >
                  Energy Forecast ($25)
                </button>
                <button
                  type="button"
                  onClick={() =>
                    handlePreset(
                      'AI Semiconductor Silicon Economics',
                      'Analyze wafer fabrication capacity, compute 3nm chip yield CAGRs, and compile procurement findings.',
                      '30.00'
                    )
                  }
                  className="text-[11px] text-slate-400 hover:text-slate-200 bg-slate-800/50 hover:bg-slate-800 px-2 py-1 rounded transition"
                >
                  AI Silicon ($30)
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={creating}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 px-5 rounded-lg text-xs transition flex items-center justify-center space-x-1.5 disabled:opacity-50 shadow-sm self-end"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{creating ? 'Creating...' : 'Launch Objective'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Active Objectives List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Active Objectives ({objectives.length})</h3>
          </div>
          <button
            onClick={loadObjectives}
            className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 transition"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Refresh</span>
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-xs">Loading objectives...</div>
        ) : objectives.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-8 text-center text-slate-500 text-xs">
            No active objectives. Create one above to begin.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {objectives.map((obj) => (
              <div
                key={obj.id}
                onClick={() => onSelectObjective(obj.id)}
                className="bg-slate-900/50 hover:bg-slate-800/50 border border-slate-800/80 hover:border-slate-700 rounded-xl p-4 cursor-pointer transition space-y-2.5 group"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-medium ${
                      obj.status === 'completed'
                        ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-900'
                        : obj.status === 'awaiting_payment'
                        ? 'bg-amber-950/60 text-amber-400 border border-amber-900'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {obj.status.replace('_', ' ')}
                  </span>
                  <span className="font-mono text-emerald-400 font-semibold text-xs">
                    ${Number(obj.max_budget_usd).toFixed(2)}
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-white group-hover:text-emerald-300 transition line-clamp-1">
                    {obj.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{obj.description}</p>
                </div>

                <div className="border-t border-slate-800/60 pt-2 flex items-center justify-between text-[11px] text-slate-500">
                  <span>{obj.subtasks?.length || 0} subtasks</span>
                  <span className="flex items-center gap-1 text-slate-400 group-hover:text-emerald-400 transition">
                    <span>View</span>
                    <ArrowRight className="w-3 h-3" />
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
