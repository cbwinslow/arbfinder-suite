"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Snipe {
  id: number;
  listing_url: string;
  listing_title: string | null;
  max_bid: number;
  auction_end_time: number;
  lead_time_seconds: number;
  status: string;
  created_at: number;
  executed_at: number | null;
  result: string | null;
}

export default function SnipesPage() {
  const [snipes, setSnipes] = useState<Snipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Form fields
  const [listingUrl, setListingUrl] = useState("");
  const [listingTitle, setListingTitle] = useState("");
  const [maxBid, setMaxBid] = useState("");
  const [auctionEndTime, setAuctionEndTime] = useState("");
  const [leadTimeSeconds, setLeadTimeSeconds] = useState("5");

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

  useEffect(() => {
    fetchSnipes();
  }, []);

  const fetchSnipes = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/snipes`);
      const data = await response.json();
      setSnipes(data.snipes || []);
    } catch (error) {
      console.error("Failed to fetch snipes:", error);
    }
    setLoading(false);
  };

  const createSnipe = async () => {
    if (!listingUrl || !maxBid || !auctionEndTime) {
      alert("Please fill in all required fields");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/snipes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          listing_url: listingUrl,
          listing_title: listingTitle || null,
          max_bid: parseFloat(maxBid),
          auction_end_time: auctionEndTime,
          lead_time_seconds: parseInt(leadTimeSeconds),
        }),
      });

      if (response.ok) {
        alert("Snipe scheduled successfully!");
        setShowForm(false);
        setListingUrl("");
        setListingTitle("");
        setMaxBid("");
        setAuctionEndTime("");
        setLeadTimeSeconds("5");
        await fetchSnipes();
      } else {
        const error = await response.json();
        alert(`Failed to schedule snipe: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to create snipe:", error);
      alert("Failed to schedule snipe");
    }
    setLoading(false);
  };

  const cancelSnipe = async (snipeId: number) => {
    if (!confirm("Are you sure you want to cancel this snipe?")) {
      return;
    }

    try {
      const response = await fetch(`${apiBase}/api/snipes/${snipeId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        alert("Snipe cancelled successfully");
        await fetchSnipes();
      } else {
        const error = await response.json();
        alert(`Failed to cancel snipe: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to cancel snipe:", error);
      alert("Failed to cancel snipe");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "scheduled":
        return "text-yellow-400 bg-yellow-900/30 border-yellow-500/30";
      case "executed":
        return "text-green-400 bg-green-900/30 border-green-500/30";
      case "cancelled":
        return "text-gray-400 bg-gray-900/30 border-gray-500/30";
      case "failed":
        return "text-red-400 bg-red-900/30 border-red-500/30";
      default:
        return "text-blue-400 bg-blue-900/30 border-blue-500/30";
    }
  };

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
            🎯 Auction Sniping
          </h1>
          <p className="text-gray-400 mt-2">
            Schedule bids to win auctions at the last moment
          </p>
        </div>

        <div className="flex gap-4">
          <Link
            href="/"
            className="text-blue-400 hover:text-blue-300 underline transition"
          >
            ← Back to Listings
          </Link>
          <button
            className="bg-purple-700 hover:bg-purple-600 px-6 py-3 rounded font-semibold transition"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? "Cancel" : "+ Schedule Snipe"}
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h3 className="text-blue-400 font-semibold mb-2">
          🎓 How Sniping Works
        </h3>
        <p className="text-gray-300 text-sm">
          Auction sniping is the practice of placing a bid at the last possible
          moment before an auction closes. This prevents others from having time
          to counter-bid. Enter the auction details, your maximum bid, and how
          many seconds before the auction ends you want to place the bid (lead
          time). The system will automatically execute the bid at the right
          moment.
        </p>
      </div>

      {/* Create Snipe Form */}
      {showForm && (
        <div className="bg-neutral-900 rounded-lg p-6 border border-purple-500/20">
          <h2 className="text-xl font-semibold mb-4 text-purple-400">
            Schedule New Snipe
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="text-sm text-gray-400 block mb-2">
                Auction URL *
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-purple-500 focus:outline-none transition"
                placeholder="https://example.com/auction/12345"
                value={listingUrl}
                onChange={(e) => setListingUrl(e.target.value)}
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-sm text-gray-400 block mb-2">
                Item Title (optional)
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-purple-500 focus:outline-none transition"
                placeholder="RTX 3080 Graphics Card"
                value={listingTitle}
                onChange={(e) => setListingTitle(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                Maximum Bid ($) *
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-purple-500 focus:outline-none transition"
                placeholder="150.00"
                type="number"
                step="0.01"
                value={maxBid}
                onChange={(e) => setMaxBid(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                Auction End Time *
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-purple-500 focus:outline-none transition"
                type="datetime-local"
                value={auctionEndTime}
                onChange={(e) => setAuctionEndTime(e.target.value)}
              />
            </div>

            <div className="md:col-span-2">
              <label className="text-sm text-gray-400 block mb-2">
                Lead Time (seconds before end)
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-purple-500 focus:outline-none transition"
                type="number"
                min="1"
                max="300"
                value={leadTimeSeconds}
                onChange={(e) => setLeadTimeSeconds(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Recommended: 5-15 seconds. Too early and others can outbid you;
                too late and the bid might not process.
              </p>
            </div>

            <button
              className="md:col-span-2 bg-purple-700 hover:bg-purple-600 px-6 py-3 rounded font-semibold transition disabled:opacity-50"
              onClick={createSnipe}
              disabled={loading}
            >
              {loading ? "Scheduling..." : "Schedule Snipe"}
            </button>
          </div>
        </div>
      )}

      {/* Snipes List */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-purple-400">
          Scheduled Snipes ({snipes.length})
        </h2>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            <p className="text-gray-400 mt-4">Loading...</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {snipes.map((snipe) => (
            <div
              key={snipe.id}
              className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-purple-500/50 transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded border ${getStatusColor(snipe.status)}`}
                    >
                      {snipe.status.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      ID: {snipe.id}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2">
                    {snipe.listing_title || "Untitled Auction"}
                  </h3>

                  <div className="space-y-1 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">Max Bid:</span>
                      <span className="text-2xl font-bold text-green-400">
                        ${snipe.max_bid.toFixed(2)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">Auction Ends:</span>
                      <span className="text-yellow-400">
                        {new Date(
                          snipe.auction_end_time * 1000,
                        ).toLocaleString()}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">Execute:</span>
                      <span className="text-purple-400">
                        {snipe.lead_time_seconds} seconds before end
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-gray-400">Created:</span>
                      <span className="text-gray-300">
                        {new Date(snipe.created_at * 1000).toLocaleString()}
                      </span>
                    </div>

                    {snipe.executed_at && (
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Executed:</span>
                        <span className="text-gray-300">
                          {new Date(snipe.executed_at * 1000).toLocaleString()}
                        </span>
                      </div>
                    )}

                    {snipe.result && (
                      <div className="mt-2 p-2 bg-neutral-800 rounded text-xs">
                        <span className="text-gray-400">Result:</span>{" "}
                        {snipe.result}
                      </div>
                    )}

                    <a
                      className="inline-block text-blue-400 hover:text-blue-300 underline transition mt-2"
                      href={snipe.listing_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Auction →
                    </a>
                  </div>
                </div>

                {snipe.status === "scheduled" && (
                  <button
                    className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded font-semibold transition text-sm"
                    onClick={() => cancelSnipe(snipe.id)}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {!loading && snipes.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl">No snipes scheduled</p>
            <p className="text-sm mt-2">
              Click "Schedule Snipe" to get started
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
