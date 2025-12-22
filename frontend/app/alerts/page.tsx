"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Alert {
  id: number;
  search_query: string;
  min_price: number | null;
  max_price: number | null;
  notification_method: string;
  notification_target: string;
  status: string;
  created_at: number;
  last_triggered_at: number | null;
  trigger_count: number;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Form fields
  const [searchQuery, setSearchQuery] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [notificationMethod, setNotificationMethod] = useState("email");
  const [notificationTarget, setNotificationTarget] = useState("");

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/alerts`);
      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (error) {
      console.error("Failed to fetch alerts:", error);
    }
    setLoading(false);
  };

  const createAlert = async () => {
    if (!searchQuery || !notificationTarget) {
      alert("Please fill in all required fields");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/alerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          search_query: searchQuery,
          min_price: minPrice ? parseFloat(minPrice) : null,
          max_price: maxPrice ? parseFloat(maxPrice) : null,
          notification_method: notificationMethod,
          notification_target: notificationTarget,
        }),
      });

      if (response.ok) {
        alert("Alert created successfully!");
        setShowForm(false);
        setSearchQuery("");
        setMinPrice("");
        setMaxPrice("");
        setNotificationTarget("");
        await fetchAlerts();
      } else {
        const error = await response.json();
        alert(`Failed to create alert: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to create alert:", error);
      alert("Failed to create alert");
    }
    setLoading(false);
  };

  const deleteAlert = async (alertId: number) => {
    if (!confirm("Are you sure you want to delete this alert?")) {
      return;
    }

    try {
      const response = await fetch(`${apiBase}/api/alerts/${alertId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        alert("Alert deleted successfully");
        await fetchAlerts();
      } else {
        const error = await response.json();
        alert(`Failed to delete alert: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to delete alert:", error);
      alert("Failed to delete alert");
    }
  };

  const toggleAlertStatus = async (alertId: number, currentStatus: string) => {
    const action = currentStatus === "active" ? "pause" : "resume";

    try {
      const response = await fetch(
        `${apiBase}/api/alerts/${alertId}/${action}`,
        {
          method: "PATCH",
        },
      );

      if (response.ok) {
        await fetchAlerts();
      } else {
        const error = await response.json();
        alert(`Failed to ${action} alert: ${error.detail}`);
      }
    } catch (error) {
      console.error(`Failed to ${action} alert:`, error);
      alert(`Failed to ${action} alert`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-900/30 border-green-500/30";
      case "paused":
        return "text-yellow-400 bg-yellow-900/30 border-yellow-500/30";
      case "deleted":
        return "text-red-400 bg-red-900/30 border-red-500/30";
      default:
        return "text-blue-400 bg-blue-900/30 border-blue-500/30";
    }
  };

  const getNotificationIcon = (method: string) => {
    switch (method) {
      case "email":
        return "📧";
      case "webhook":
        return "🔗";
      case "twitter":
        return "🐦";
      case "facebook":
        return "📘";
      default:
        return "🔔";
    }
  };

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
            🔔 Price Alerts
          </h1>
          <p className="text-gray-400 mt-2">
            Get notified when items match your criteria
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
            className="bg-orange-700 hover:bg-orange-600 px-6 py-3 rounded font-semibold transition"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? "Cancel" : "+ Create Alert"}
          </button>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h3 className="text-blue-400 font-semibold mb-2">
          📢 How Price Alerts Work
        </h3>
        <p className="text-gray-300 text-sm">
          Set up alerts to be notified when new listings match your search
          criteria and price range. You can receive alerts via email, webhook,
          or social media. The system checks for new matches automatically and
          sends you a notification when items are found. Perfect for finding
          deals on specific items within your budget!
        </p>
      </div>

      {/* Create Alert Form */}
      {showForm && (
        <div className="bg-neutral-900 rounded-lg p-6 border border-orange-500/20">
          <h2 className="text-xl font-semibold mb-4 text-orange-400">
            Create New Alert
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="text-sm text-gray-400 block mb-2">
                Search Query *
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-orange-500 focus:outline-none transition"
                placeholder="RTX 3080, iPad Pro, vintage watch..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                Minimum Price ($)
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-orange-500 focus:outline-none transition"
                placeholder="200.00"
                type="number"
                step="0.01"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                Maximum Price ($)
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-orange-500 focus:outline-none transition"
                placeholder="400.00"
                type="number"
                step="0.01"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                Notification Method *
              </label>
              <select
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-orange-500 focus:outline-none transition"
                value={notificationMethod}
                onChange={(e) => setNotificationMethod(e.target.value)}
              >
                <option value="email">📧 Email</option>
                <option value="webhook">🔗 Webhook</option>
                <option value="twitter">🐦 Twitter</option>
                <option value="facebook">📘 Facebook</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-2">
                {notificationMethod === "email"
                  ? "Email Address"
                  : notificationMethod === "webhook"
                    ? "Webhook URL"
                    : notificationMethod === "twitter"
                      ? "Twitter Handle"
                      : "Facebook Page"}{" "}
                *
              </label>
              <input
                className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-orange-500 focus:outline-none transition"
                placeholder={
                  notificationMethod === "email"
                    ? "you@example.com"
                    : notificationMethod === "webhook"
                      ? "https://your-webhook.com/alert"
                      : notificationMethod === "twitter"
                        ? "@yourusername"
                        : "YourPageName"
                }
                value={notificationTarget}
                onChange={(e) => setNotificationTarget(e.target.value)}
              />
            </div>

            <button
              className="md:col-span-2 bg-orange-700 hover:bg-orange-600 px-6 py-3 rounded font-semibold transition disabled:opacity-50"
              onClick={createAlert}
              disabled={loading}
            >
              {loading ? "Creating..." : "Create Alert"}
            </button>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-orange-400">
          Your Alerts ({alerts.filter((a) => a.status !== "deleted").length})
        </h2>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
            <p className="text-gray-400 mt-4">Loading...</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4">
          {alerts
            .filter((a) => a.status !== "deleted")
            .map((alert) => (
              <div
                key={alert.id}
                className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-orange-500/50 transition"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded border ${getStatusColor(alert.status)}`}
                      >
                        {alert.status.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        ID: {alert.id}
                      </span>
                      {alert.trigger_count > 0 && (
                        <span className="text-xs bg-purple-900/30 text-purple-400 px-2 py-1 rounded">
                          🔥 {alert.trigger_count} matches
                        </span>
                      )}
                    </div>

                    <h3 className="text-lg font-semibold text-white mb-2">
                      🔍 "{alert.search_query}"
                    </h3>

                    <div className="space-y-1 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Price Range:</span>
                        <span className="text-green-400 font-semibold">
                          {alert.min_price !== null
                            ? `$${alert.min_price.toFixed(2)}`
                            : "Any"}{" "}
                          -
                          {alert.max_price !== null
                            ? ` $${alert.max_price.toFixed(2)}`
                            : " Any"}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Notify via:</span>
                        <span className="text-blue-400">
                          {getNotificationIcon(alert.notification_method)}{" "}
                          {alert.notification_method}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Target:</span>
                        <span className="text-gray-300">
                          {alert.notification_target}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Created:</span>
                        <span className="text-gray-300">
                          {new Date(alert.created_at * 1000).toLocaleString()}
                        </span>
                      </div>

                      {alert.last_triggered_at && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Last Triggered:</span>
                          <span className="text-yellow-400">
                            {new Date(
                              alert.last_triggered_at * 1000,
                            ).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {alert.status === "active" ? (
                      <button
                        className="bg-yellow-700 hover:bg-yellow-600 px-4 py-2 rounded font-semibold transition text-sm"
                        onClick={() =>
                          toggleAlertStatus(alert.id, alert.status)
                        }
                      >
                        Pause
                      </button>
                    ) : alert.status === "paused" ? (
                      <button
                        className="bg-green-700 hover:bg-green-600 px-4 py-2 rounded font-semibold transition text-sm"
                        onClick={() =>
                          toggleAlertStatus(alert.id, alert.status)
                        }
                      >
                        Resume
                      </button>
                    ) : null}

                    <button
                      className="bg-red-700 hover:bg-red-600 px-4 py-2 rounded font-semibold transition text-sm"
                      onClick={() => deleteAlert(alert.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
        </div>

        {!loading &&
          alerts.filter((a) => a.status !== "deleted").length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p className="text-xl">No alerts configured</p>
              <p className="text-sm mt-2">
                Click "Create Alert" to get started
              </p>
            </div>
          )}
      </div>
    </main>
  );
}
