'use client';

interface AgentJob {
  id: number;
  agentType: string;
  status: string;
  startedAt: string;
  completedAt?: string;
  duration?: number;
  errorMsg?: string;
}

interface AgentStatusProps {
  jobs: AgentJob[];
  isLoading: boolean;
}

export default function AgentStatus({ jobs, isLoading }: AgentStatusProps) {
  const getAgentIcon = (agentType: string) => {
    const icons: Record<string, string> = {
      web_crawler: '🕷️',
      data_validator: '✅',
      market_researcher: '📊',
      price_specialist: '💰',
      listing_writer: '✍️',
      image_processor: '🖼️',
      metadata_enricher: '🔍',
      title_enhancer: '📝',
      crosslister: '📤',
      quality_monitor: '👁️',
    };
    return icons[agentType] || '🤖';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'running':
        return 'bg-blue-500 animate-pulse';
      case 'failed':
        return 'bg-red-500';
      case 'queued':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 text-center">
        <div className="inline-block animate-spin text-2xl">⟳</div>
        <div className="mt-2 text-sm text-gray-600">Loading agents...</div>
      </div>
    );
  }

  return (
    <div className="p-3 h-[600px] overflow-y-auto">
      <div className="space-y-2">
        {jobs.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <div className="text-3xl mb-2">🤖</div>
            <div>No agent jobs</div>
          </div>
        ) : (
          jobs.map((job) => (
            <div
              key={job.id}
              className="
                border-2 
                border-t-white 
                border-l-white 
                border-r-[#808080] 
                border-b-[#808080]
                p-2
                bg-white
              "
            >
              <div className="flex items-start gap-2">
                <span className="text-xl">{getAgentIcon(job.agentType)}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-xs text-black truncate">
                    {job.agentType.replace(/_/g, ' ').toUpperCase()}
                  </div>
                  <div className="text-[10px] text-gray-500">
                    ID: {job.id}
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <div
                      className={`
                        w-2 h-2 rounded-full
                        ${getStatusColor(job.status)}
                      `}
                    />
                    <span className="text-[10px] font-bold">
                      {job.status.toUpperCase()}
                    </span>
                  </div>
                  {job.duration && (
                    <div className="text-[10px] text-gray-600 mt-0.5">
                      ⏱️ {(job.duration / 1000).toFixed(2)}s
                    </div>
                  )}
                  {job.errorMsg && (
                    <div className="text-[9px] text-red-600 mt-1 truncate">
                      ⚠️ {job.errorMsg}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
