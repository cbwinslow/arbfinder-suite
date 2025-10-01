'use client'
import { useEffect, useState } from 'react'

interface Listing {
  source: string
  url: string
  title: string
  price: number
  currency: string
  condition: string
  ts: number
}

export default function Home() {
  const [rows, setRows] = useState<Listing[]>([])
  const [title, setTitle] = useState('')
  const [price, setPrice] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [stats, setStats] = useState<any>(null)
  const [sortBy, setSortBy] = useState<'ts' | 'price' | 'title'>('ts')
  const [filterSource, setFilterSource] = useState<string>('')

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080'

  useEffect(() => {
    fetchListings()
    fetchStats()
  }, [sortBy, filterSource])

  const fetchListings = async () => {
    setLoading(true)
    try {
      let url = `${apiBase}/api/listings?order_by=${sortBy}`
      if (filterSource) url += `&source=${filterSource}`
      
      const response = await fetch(url)
      const data = await response.json()
      setRows(data.data || data)
    } catch (error) {
      console.error('Failed to fetch listings:', error)
    }
    setLoading(false)
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(`${apiBase}/api/statistics`)
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const searchListings = async () => {
    if (!searchQuery.trim()) {
      fetchListings()
      return
    }
    
    setLoading(true)
    try {
      const response = await fetch(`${apiBase}/api/listings/search?q=${encodeURIComponent(searchQuery)}`)
      const data = await response.json()
      setRows(data)
    } catch (error) {
      console.error('Search failed:', error)
    }
    setLoading(false)
  }

  const checkout = async (t: string, p: number) => {
    const url = new URL(apiBase + '/api/stripe/create-checkout-session')
    url.searchParams.set('title', t)
    url.searchParams.set('price', String(p))
    const r = await fetch(url, { method: 'POST' })
    const j = await r.json()
    if (j.url) window.location.href = j.url
  }

  const submit = async () => {
    if (!title.trim() || !price) return
    
    setLoading(true)
    try {
      await fetch(`${apiBase}/api/listings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, price: Number(price), url: '#' })
      })
      setTitle('')
      setPrice('')
      await fetchListings()
      await fetchStats()
    } catch (error) {
      console.error('Failed to add listing:', error)
    }
    setLoading(false)
  }

  const sources = Array.from(new Set(rows.map(r => r.source)))

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
            ArbFinder Suite
          </h1>
          <p className="text-gray-400 mt-2">Find arbitrage opportunities across marketplaces</p>
        </div>
        
        {stats && (
          <div className="bg-neutral-900 rounded-lg p-4 border border-green-500/20">
            <div className="text-sm text-gray-400">Total Listings</div>
            <div className="text-3xl font-bold text-green-400">{stats.total_listings}</div>
          </div>
        )}
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-neutral-900 rounded-lg p-4 border border-green-500/20">
            <div className="text-sm text-gray-400">Recent (24h)</div>
            <div className="text-2xl font-bold text-green-400">{stats.recent_listings}</div>
          </div>
          <div className="bg-neutral-900 rounded-lg p-4 border border-blue-500/20">
            <div className="text-sm text-gray-400">Comparable Groups</div>
            <div className="text-2xl font-bold text-blue-400">{stats.total_comps}</div>
          </div>
          {stats.price_stats && (
            <>
              <div className="bg-neutral-900 rounded-lg p-4 border border-yellow-500/20">
                <div className="text-sm text-gray-400">Avg Price</div>
                <div className="text-2xl font-bold text-yellow-400">${stats.price_stats.average}</div>
              </div>
              <div className="bg-neutral-900 rounded-lg p-4 border border-purple-500/20">
                <div className="text-sm text-gray-400">Price Range</div>
                <div className="text-lg font-bold text-purple-400">
                  ${stats.price_stats.min} - ${stats.price_stats.max}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Search and Filter Section */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-green-500/20">
        <h2 className="text-xl font-semibold mb-4 text-green-400">🔍 Search & Filter</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <input
              className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-green-500 focus:outline-none transition"
              placeholder="Search listings..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && searchListings()}
            />
          </div>
          <button
            className="bg-green-700 hover:bg-green-600 px-6 py-3 rounded font-semibold transition"
            onClick={searchListings}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label className="text-sm text-gray-400 block mb-2">Sort By</label>
            <select
              className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-green-500 focus:outline-none"
              value={sortBy}
              onChange={e => setSortBy(e.target.value as any)}
            >
              <option value="ts">Most Recent</option>
              <option value="price">Price</option>
              <option value="title">Title</option>
            </select>
          </div>
          
          <div>
            <label className="text-sm text-gray-400 block mb-2">Filter by Source</label>
            <select
              className="w-full bg-neutral-800 p-3 rounded border border-gray-700 focus:border-green-500 focus:outline-none"
              value={filterSource}
              onChange={e => setFilterSource(e.target.value)}
            >
              <option value="">All Sources</option>
              {sources.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Add New Listing */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-blue-500/20">
        <h2 className="text-xl font-semibold mb-4 text-blue-400">➕ Add Listing</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            className="md:col-span-2 bg-neutral-800 p-3 rounded border border-gray-700 focus:border-blue-500 focus:outline-none transition"
            placeholder="Title"
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
          <input
            className="bg-neutral-800 p-3 rounded border border-gray-700 focus:border-blue-500 focus:outline-none transition"
            placeholder="Price"
            type="number"
            step="0.01"
            value={price}
            onChange={e => setPrice(e.target.value)}
          />
          <button
            className="md:col-span-3 bg-blue-700 hover:bg-blue-600 px-6 py-3 rounded font-semibold transition"
            onClick={submit}
            disabled={loading || !title.trim() || !price}
          >
            {loading ? 'Adding...' : 'Add Listing'}
          </button>
        </div>
      </div>

      {/* Listings Grid */}
      <div>
        <h2 className="text-2xl font-semibold mb-4 text-green-400">
          📦 Listings ({rows.length})
        </h2>
        
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
            <p className="text-gray-400 mt-4">Loading...</p>
          </div>
        )}
        
        <div className="grid grid-cols-1 gap-4">
          {rows.map((r, i) => (
            <div
              key={i}
              className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-green-500/50 transition group"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-semibold px-2 py-1 rounded bg-green-900/30 text-green-400 border border-green-500/30">
                      {r.source}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(r.ts * 1000).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-green-400 transition">
                    {r.title}
                  </h3>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-2xl font-bold text-green-400">
                      ${r.price.toFixed(2)} {r.currency}
                    </span>
                    <a
                      className="text-blue-400 hover:text-blue-300 underline transition"
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Source →
                    </a>
                  </div>
                </div>
                
                <button
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-6 py-3 rounded-lg font-semibold transition transform hover:scale-105"
                  onClick={() => checkout(r.title, r.price)}
                >
                  💳 Buy Now
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {!loading && rows.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-xl">No listings found</p>
            <p className="text-sm mt-2">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </main>
  )
}
