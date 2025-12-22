"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

interface Comp {
  title: string;
  avg_price: number;
  median_price: number;
  count: number;
  timestamp: number;
}

export default function CompsPage() {
  const [comps, setComps] = useState<Comp[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

  useEffect(() => {
    fetchComps();
  }, []);

  const fetchComps = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/comps`);
      const data = await response.json();
      setComps(data);
    } catch (error) {
      console.error("Failed to fetch comps:", error);
    }
    setLoading(false);
  };

  const searchComps = async () => {
    if (!searchQuery.trim()) {
      fetchComps();
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${apiBase}/api/comps/search?q=${encodeURIComponent(searchQuery)}`,
      );
      const data = await response.json();
      setComps(data);
    } catch (error) {
      console.error("Search failed:", error);
    }
    setLoading(false);
  };

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Comparable Prices
          </h1>
          <p className="text-gray-400 mt-2">
            Historical price data from eBay sold listings
          </p>
        </div>
        <Link
          href="/"
          className="text-green-400 hover:text-green-300 underline"
        >
          ← Back to Listings
        </Link>
      </div>

      {/* Search */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-blue-500/20">
        <h2 className="text-xl font-semibold mb-4 text-blue-400">
          🔍 Search Comparables
        </h2>
        <div className="flex gap-4">
          <input
            className="flex-1 bg-neutral-800 p-3 rounded border border-gray-700 focus:border-blue-500 focus:outline-none transition"
            placeholder="Search by title..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && searchComps()}
          />
          <button
            className="bg-blue-700 hover:bg-blue-600 px-6 py-3 rounded font-semibold transition"
            onClick={searchComps}
            disabled={loading}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {/* Comps Table */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-blue-400">
          📊 Comparable Groups ({comps.length})
        </h2>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            <p className="text-gray-400 mt-4">Loading...</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {comps.map((comp, i) => (
            <div
              key={i}
              className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-blue-500/50 transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-3">
                    {comp.title}
                  </h3>

                  <div className="grid grid-cols-3 gap-6">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">
                        Average Price
                      </div>
                      <div className="text-2xl font-bold text-blue-400">
                        ${comp.avg_price.toFixed(2)}
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-gray-500 mb-1">
                        Median Price
                      </div>
                      <div className="text-2xl font-bold text-purple-400">
                        ${comp.median_price.toFixed(2)}
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-gray-500 mb-1">
                        Sample Size
                      </div>
                      <div className="text-2xl font-bold text-green-400">
                        {comp.count} items
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 text-xs text-gray-500">
                    Last updated:{" "}
                    {new Date(comp.timestamp * 1000).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {!loading && comps.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl">No comparable data found</p>
            <p className="text-sm mt-2">
              Run the crawler to collect price data
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
