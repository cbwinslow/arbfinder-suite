'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface CrewRun {
  id: number;
  crew_type: string;
  targets: string | null;
  query: string | null;
  status: string;
  started_at: number;
  completed_at: number | null;
  duration_seconds: number | null;
  items_processed: number;
  items_created: number;
  error_message: string | null;
}

interface CrewType {
  type: string;
  name: string;
  description: string;
  icon: string;
  agents: string[];
}

export default function CrewsPage() {
  const [runs, setRuns] = useState<CrewRun[]>([]);
  const [crewTypes, setCrewTypes] = useState<CrewType[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  
  // Form fields
  const [selectedType, setSelectedType] = useState('');
  const [targets, setTargets] = useState<string[]>([]);
  const [query, setQuery] = useState('');

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080';

  useEffect(() => {
    fetchRuns();
    fetchCrewTypes();
  }, []);

  const fetchRuns = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/crews/runs`);
      const data = await response.json();
      setRuns(data.runs || []);
    } catch (error) {
      console.error('Failed to fetch runs:', error);
    }
    setLoading(false);
  };

  const fetchCrewTypes = async () => {
    try {
      const response = await fetch(`${apiBase}/api/crews/types`);
      const data = await response.json();
      setCrewTypes(data.crew_types || []);
      if (data.crew_types?.length > 0) {
        setSelectedType(data.crew_types[0].type);
      }
    } catch (error) {
      console.error('Failed to fetch crew types:', error);
    }
  };

  const startCrewRun = async () => {
    if (!selectedType) {
      alert('Please select a crew type');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/crews/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crew_type: selectedType,
          targets: targets.length > 0 ? targets : null,
          query: query || null,
        }),
      });

      if (response.ok) {
        alert('Crew run started successfully!');
        setShowForm(false);
        setTargets([]);
        setQuery('');
        await fetchRuns();
      } else {
        const error = await response.json();
        alert(`Failed to start crew run: ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to start crew run:', error);
      alert('Failed to start crew run');
    }
    setLoading(false);
  };

  const cancelRun = async (runId: number) => {
    if (!confirm('Are you sure you want to cancel this run?')) {
      return;
    }

    try {
      const response = await fetch(`${apiBase}/api/crews/cancel/${runId}`, {
        method: 'POST',
      });

      if (response.ok) {
        alert('Run cancelled successfully');
        await fetchRuns();
      } else {
        const error = await response.json();
        alert(`Failed to cancel run: ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to cancel run:', error);
      alert('Failed to cancel run');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'text-yellow-400 bg-yellow-900/30 border-yellow-500/30';
      case 'running':
        return 'text-blue-400 bg-blue-900/30 border-blue-500/30';
      case 'completed':
        return 'text-green-400 bg-green-900/30 border-green-500/30';
      case 'failed':
        return 'text-red-400 bg-red-900/30 border-red-500/30';
      default:
        return 'text-gray-400 bg-gray-900/30 border-gray-500/30';
    }
  };

  const toggleTarget = (target: string) => {
    if (targets.includes(target)) {
      setTargets(targets.filter(t => t !== target));
    } else {
      setTargets([...targets, target]);
    }
  };

  const availableTargets = [
    'shopgoodwill',
    'govdeals',
    'governmentsurplus',
    'ebay',
  ];

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            🤖 AI Crew Runner
          </h1>
          <p className="text-gray-400 mt-2">Run Crawl4AI/CrewAI agents for data ingestion and processing</p>
        </div>
        
        <div className="flex gap-4">
          <Link 
            href="/" 
            className="text-blue-400 hover:text-blue-300 underline transition"
          >
            ← Back to Listings
          </Link>
          <button
            className="bg-cyan-700 hover:bg-cyan-600 px-6 py-3 rounded font-semibold transition"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ Start New Crew'}
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h3 className="text-blue-400 font-semibold mb-2">🧠 What Are AI Crews?</h3>
        <p className="text-gray-300 text-sm">
          AI crews are coordinated groups of specialized AI agents that work together to accomplish 
          complex tasks. Each crew type has multiple agents with specific roles (crawler, validator, 
          enricher, etc.) that collaborate to ingest price data, enrich metadata, generate listings, 
          or perform market research. Select a crew type, configure the targets and query, then let 
          the AI agents do the work!
        </p>
      </div>

      {/* Available Crew Types */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-cyan-400">Available Crew Types</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {crewTypes.map((crew) => (
            <div
              key={crew.type}
              className="bg-neutral-900 p-4 rounded-lg border border-gray-800 hover:border-cyan-500/50 transition"
            >
              <div className="text-3xl mb-2">{crew.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-1">{crew.name}</h3>
              <p className="text-sm text-gray-400 mb-3">{crew.description}</p>
              <div className="flex flex-wrap gap-1">
                {crew.agents.map((agent) => (
                  <span
                    key={agent}
                    className="text-xs bg-cyan-900/30 text-cyan-400 px-2 py-1 rounded"
                  >
                    {agent}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Start Crew Form */}
      {showForm && (
        <div className="bg-neutral-900 rounded-lg p-6 border border-cyan-500/20">
          <h2 className="text-xl font-semibold mb-4 text-cyan-400">Start New Crew Run</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 block mb-2">Crew Type *</label>
              <select
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-cyan-500 focus:outline-none transition"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                {crewTypes.map((crew) => (
                  <option key={crew.type} value={crew.type}>
                    {crew.icon} {crew.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="text-sm text-gray-400 block mb-2">Target Sites (optional)</label>
              <div className="flex flex-wrap gap-2">
                {availableTargets.map((target) => (
                  <button
                    key={target}
                    className={`px-4 py-2 rounded font-semibold transition ${
                      targets.includes(target)
                        ? 'bg-cyan-700 text-white'
                        : 'bg-neutral-800 text-gray-400 hover:bg-neutral-700'
                    }`}
                    onClick={() => toggleTarget(target)}
                  >
                    {target}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Leave empty to run on all available targets
              </p>
            </div>
            
            <div>
              <label className="text-sm text-gray-400 block mb-2">Search Query (optional)</label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-cyan-500 focus:outline-none transition"
                placeholder="e.g., electronics, laptops, cameras..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            
            <button
              className="w-full bg-cyan-700 hover:bg-cyan-600 px-6 py-3 rounded font-semibold transition disabled:opacity-50"
              onClick={startCrewRun}
              disabled={loading}
            >
              {loading ? 'Starting...' : 'Start Crew Run'}
            </button>
          </div>
        </div>
      )}

      {/* Crew Runs List */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-cyan-400">
          Recent Runs ({runs.length})
        </h2>
        
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
            <p className="text-gray-400 mt-4">Loading...</p>
          </div>
        )}
        
        <div className="grid grid-cols-1 gap-4">
          {runs.map((run) => {
            const crewInfo = crewTypes.find(c => c.type === run.crew_type);
            return (
              <div
                key={run.id}
                className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-cyan-500/50 transition"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`text-xs font-semibold px-2 py-1 rounded border ${getStatusColor(run.status)}`}>
                        {run.status.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        Run #{run.id}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-white mb-2">
                      {crewInfo?.icon} {crewInfo?.name || run.crew_type}
                    </h3>
                    
                    <div className="space-y-1 text-sm">
                      {run.targets && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Targets:</span>
                          <span className="text-cyan-400">
                            {JSON.parse(run.targets).join(', ')}
                          </span>
                        </div>
                      )}
                      
                      {run.query && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Query:</span>
                          <span className="text-gray-300">"{run.query}"</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Started:</span>
                        <span className="text-gray-300">
                          {new Date(run.started_at * 1000).toLocaleString()}
                        </span>
                      </div>
                      
                      {run.completed_at && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Completed:</span>
                          <span className="text-gray-300">
                            {new Date(run.completed_at * 1000).toLocaleString()}
                          </span>
                        </div>
                      )}
                      
                      {run.duration_seconds && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Duration:</span>
                          <span className="text-purple-400">
                            {run.duration_seconds.toFixed(1)}s
                          </span>
                        </div>
                      )}
                      
                      {run.status === 'completed' && (
                        <div className="flex items-center gap-4 mt-2">
                          <div className="flex items-center gap-2">
                            <span className="text-gray-400">Processed:</span>
                            <span className="text-green-400 font-semibold">
                              {run.items_processed} items
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-400">Created:</span>
                            <span className="text-blue-400 font-semibold">
                              {run.items_created} new
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {run.error_message && (
                        <div className="mt-2 p-2 bg-red-900/20 border border-red-500/30 rounded text-xs text-red-400">
                          <span className="font-semibold">Error:</span> {run.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {run.status === 'running' || run.status === 'queued' ? (
                    <button
                      className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded font-semibold transition text-sm"
                      onClick={() => cancelRun(run.id)}
                    >
                      Cancel
                    </button>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
        
        {!loading && runs.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl">No crew runs yet</p>
            <p className="text-sm mt-2">Click "Start New Crew" to begin</p>
          </div>
        )}
      </div>
    </main>
  );
}
