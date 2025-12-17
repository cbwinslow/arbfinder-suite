'use client';

import { useState, useEffect } from 'react';
import RetroWindow from '@/components/RetroWindow';
import CrawlerMonitor from '@/components/CrawlerMonitor';
import AgentStatus from '@/components/AgentStatus';
import LiveUpdates from '@/components/LiveUpdates';

export default function DashboardPage() {
  const [crawlerData, setCrawlerData] = useState<any[]>([]);
  const [agentJobs, setAgentJobs] = useState<any[]>([]);
  const [liveUpdates, setLiveUpdates] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch initial data
    fetchDashboardData();
    
    // Set up polling for live updates
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080';
      
      // Fetch crawler results
      const crawlerResponse = await fetch(`${apiBase}/api/crawler/status`);
      if (crawlerResponse.ok) {
        const data = await crawlerResponse.json();
        setCrawlerData(data.results || []);
      }
      
      // Fetch agent jobs
      const agentResponse = await fetch(`${apiBase}/api/agents/jobs?limit=20`);
      if (agentResponse.ok) {
        const data = await agentResponse.json();
        setAgentJobs(data.jobs || []);
      }
      
      // Fetch live updates
      const updatesResponse = await fetch(`${apiBase}/api/live-updates?limit=50`);
      if (updatesResponse.ok) {
        const data = await updatesResponse.json();
        setLiveUpdates(data.updates || []);
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#008080] p-4">
      <div className="max-w-[1400px] mx-auto">
        {/* Header */}
        <RetroWindow
          title="ArbFinder Dashboard - Control Panel"
          className="mb-4"
        >
          <div className="p-4 bg-[#c0c0c0]">
            <h1 className="text-2xl font-bold text-black mb-2">
              Web Crawler & AI Agent Dashboard
            </h1>
            <p className="text-sm text-gray-700">
              Real-time monitoring of web crawlers, AI agents, and price data ingestion
            </p>
          </div>
        </RetroWindow>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Crawler Monitor - Takes 2 columns */}
          <div className="lg:col-span-2">
            <RetroWindow title="Web Crawler Monitor" icon="🕷️">
              <CrawlerMonitor data={crawlerData} isLoading={isLoading} />
            </RetroWindow>
          </div>

          {/* Agent Status - Takes 1 column */}
          <div>
            <RetroWindow title="AI Agent Status" icon="🤖">
              <AgentStatus jobs={agentJobs} isLoading={isLoading} />
            </RetroWindow>
          </div>
        </div>

        {/* Live Updates Section */}
        <div className="mt-4">
          <RetroWindow title="Live Updates" icon="📡">
            <LiveUpdates updates={liveUpdates} isLoading={isLoading} />
          </RetroWindow>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          <RetroWindow title="Total Items" icon="📦">
            <div className="p-4 text-center">
              <div className="text-3xl font-bold text-blue-600">
                {crawlerData.reduce((sum, crawler) => sum + (crawler.items_found || 0), 0)}
              </div>
              <div className="text-sm text-gray-600 mt-1">Items Crawled</div>
            </div>
          </RetroWindow>

          <RetroWindow title="Active Agents" icon="⚡">
            <div className="p-4 text-center">
              <div className="text-3xl font-bold text-green-600">
                {agentJobs.filter(job => job.status === 'running').length}
              </div>
              <div className="text-sm text-gray-600 mt-1">Running Now</div>
            </div>
          </RetroWindow>

          <RetroWindow title="Success Rate" icon="✅">
            <div className="p-4 text-center">
              <div className="text-3xl font-bold text-purple-600">
                {crawlerData.length > 0
                  ? Math.round(
                      (crawlerData.filter(c => c.status === 'success').length /
                        crawlerData.length) *
                        100
                    )
                  : 0}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Crawler Success</div>
            </div>
          </RetroWindow>

          <RetroWindow title="Queue Size" icon="📋">
            <div className="p-4 text-center">
              <div className="text-3xl font-bold text-orange-600">
                {agentJobs.filter(job => job.status === 'queued').length}
              </div>
              <div className="text-sm text-gray-600 mt-1">Pending Jobs</div>
            </div>
          </RetroWindow>
        </div>
      </div>
    </div>
  );
}
