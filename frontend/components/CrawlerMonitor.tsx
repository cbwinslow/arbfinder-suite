'use client';

import { useEffect, useState } from 'react';

interface CrawlerData {
  target_name: string;
  status: string;
  items_found: number;
  duration_ms: number;
  error_msg?: string;
  metadata?: {
    timestamp?: string;
  };
}

interface CrawlerMonitorProps {
  data: CrawlerData[];
  isLoading: boolean;
}

export default function CrawlerMonitor({ data, isLoading }: CrawlerMonitorProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'partial':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return '✓';
      case 'error':
        return '✗';
      case 'running':
        return '⟳';
      case 'partial':
        return '⚠';
      default:
        return '○';
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin text-4xl">⟳</div>
        <div className="mt-2 text-gray-600">Loading crawler data...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <div className="text-4xl mb-2">🕷️</div>
        <div>No crawler data available</div>
        <div className="text-sm mt-2">Start a crawl to see results here</div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="space-y-3">
        {data.map((crawler, index) => (
          <div
            key={index}
            className="
              border-2 
              border-t-white 
              border-l-white 
              border-r-[#808080] 
              border-b-[#808080]
              p-3
              bg-white
            "
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🕷️</span>
                <div>
                  <h3 className="font-bold text-black">
                    {crawler.target_name}
                  </h3>
                  {crawler.metadata?.timestamp && (
                    <div className="text-xs text-gray-500">
                      {new Date(crawler.metadata.timestamp).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
              <div
                className={`
                  px-2 py-1 
                  rounded 
                  text-xs 
                  font-bold 
                  flex items-center gap-1
                  ${getStatusColor(crawler.status)}
                `}
              >
                <span>{getStatusIcon(crawler.status)}</span>
                <span>{crawler.status.toUpperCase()}</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Items Found</div>
                <div className="text-lg font-bold text-black">
                  {crawler.items_found}
                </div>
              </div>
              <div>
                <div className="text-gray-600">Duration</div>
                <div className="text-lg font-bold text-black">
                  {(crawler.duration_ms / 1000).toFixed(2)}s
                </div>
              </div>
              <div>
                <div className="text-gray-600">Rate</div>
                <div className="text-lg font-bold text-black">
                  {crawler.duration_ms > 0
                    ? ((crawler.items_found / crawler.duration_ms) * 1000).toFixed(1)
                    : 0}
                  /s
                </div>
              </div>
            </div>

            {crawler.error_msg && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 text-red-700 text-xs">
                <strong>Error:</strong> {crawler.error_msg}
              </div>
            )}

            {/* Progress Bar */}
            <div className="mt-3">
              <div className="h-4 bg-[#c0c0c0] border-2 border-inset border-[#808080]">
                <div
                  className={`h-full ${
                    crawler.status === 'success'
                      ? 'bg-green-500'
                      : crawler.status === 'error'
                      ? 'bg-red-500'
                      : 'bg-blue-500'
                  }`}
                  style={{
                    width: crawler.status === 'success' ? '100%' : '0%',
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
