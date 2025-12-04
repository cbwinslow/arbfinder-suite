'use client';

import { useEffect, useRef } from 'react';

interface Update {
  id: number;
  timestamp: string;
  type: string;
  message: string;
  data?: any;
}

interface LiveUpdatesProps {
  updates: Update[];
  isLoading: boolean;
}

export default function LiveUpdates({ updates, isLoading }: LiveUpdatesProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new updates arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [updates]);

  const getUpdateIcon = (type: string) => {
    const icons: Record<string, string> = {
      crawler: '🕷️',
      agent: '🤖',
      price: '💰',
      image: '🖼️',
      metadata: '🔍',
      error: '❌',
      success: '✅',
      info: 'ℹ️',
    };
    return icons[type] || '📝';
  };

  const getUpdateColor = (type: string) => {
    const colors: Record<string, string> = {
      error: 'text-red-600 bg-red-50',
      success: 'text-green-600 bg-green-50',
      crawler: 'text-blue-600 bg-blue-50',
      agent: 'text-purple-600 bg-purple-50',
      price: 'text-yellow-600 bg-yellow-50',
      info: 'text-gray-600 bg-gray-50',
    };
    return colors[type] || 'text-gray-600 bg-gray-50';
  };

  if (isLoading) {
    return (
      <div className="p-4 text-center">
        <div className="inline-block animate-spin text-2xl">⟳</div>
        <div className="mt-2 text-sm text-gray-600">Loading updates...</div>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="p-3 h-[400px] overflow-y-auto bg-black text-green-400 font-mono text-sm"
      style={{
        fontFamily: 'Courier New, monospace',
      }}
    >
      {updates.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <div>No updates yet. Waiting for activity...</div>
          <div className="mt-2 animate-pulse">▋</div>
        </div>
      ) : (
        <div className="space-y-1">
          {updates.map((update) => (
            <div key={update.id} className="flex items-start gap-2">
              <span className="text-gray-500 text-xs">
                [{new Date(update.timestamp).toLocaleTimeString()}]
              </span>
              <span>{getUpdateIcon(update.type)}</span>
              <span className="flex-1">{update.message}</span>
            </div>
          ))}
          <div className="animate-pulse">▋</div>
        </div>
      )}
    </div>
  );
}
