'use client'
import Link from 'next/link'

interface Feature {
  icon: string
  title: string
  description: string
  category: string
}

const features: Feature[] = [
  {
    category: 'Data Collection',
    icon: '🔍',
    title: 'Multi-Source Crawler',
    description: 'Async crawler for ShopGoodwill, GovDeals, GovernmentSurplus, and eBay sold comps'
  },
  {
    category: 'Data Collection',
    icon: '📁',
    title: 'Manual Import',
    description: 'Import Facebook Marketplace listings via CSV/JSON for comprehensive coverage'
  },
  {
    category: 'User Interface',
    icon: '📊',
    title: 'Interactive TUI',
    description: 'Rich terminal UI with progress bars and colored output for CLI enthusiasts'
  },
  {
    category: 'User Interface',
    icon: '🎨',
    title: 'Bubbletea TUI',
    description: 'Multi-pane Go-based terminal interface with database integration'
  },
  {
    category: 'User Interface',
    icon: '💎',
    title: 'Next.js Frontend',
    description: 'Modern, responsive web interface with dark mode and mobile-first design'
  },
  {
    category: 'CLI Tools',
    icon: '🖥️',
    title: 'Enhanced CLI',
    description: 'Comprehensive CLI with subcommands: search, watch, config, db, server'
  },
  {
    category: 'CLI Tools',
    icon: '📦',
    title: 'TypeScript SDK',
    description: 'Node.js SDK and CLI tools for programmatic access'
  },
  {
    category: 'API',
    icon: '🚀',
    title: 'FastAPI Backend',
    description: 'RESTful API with search, filtering, statistics, and real-time data'
  },
  {
    category: 'API',
    icon: '📈',
    title: 'Statistics & Analytics',
    description: 'Real-time metrics, price trends, and market insights'
  },
  {
    category: 'Automation',
    icon: '🤖',
    title: 'CrewAI Integration',
    description: 'AI-powered research, pricing, listing, and crosslisting workflows'
  },
  {
    category: 'Automation',
    icon: '👁️',
    title: 'Watch Mode',
    description: 'Continuous monitoring for deals with customizable intervals'
  },
  {
    category: 'Deployment',
    icon: '🐳',
    title: 'Docker Support',
    description: 'Containerized deployment with Docker and Docker Compose'
  },
  {
    category: 'Deployment',
    icon: '🛠️',
    title: 'Developer Tools',
    description: 'Makefile, pre-commit hooks, VS Code config, and comprehensive testing'
  },
  {
    category: 'Data Analysis',
    icon: '💰',
    title: 'Price Comparison',
    description: 'Compare live listings with sold comps to find arbitrage opportunities'
  },
  {
    category: 'Data Analysis',
    icon: '🎯',
    title: 'Smart Filtering',
    description: 'Filter by source, price, date, and discount threshold'
  },
  {
    category: 'Integration',
    icon: '💳',
    title: 'Stripe Checkout',
    description: 'Integrated payment processing for quick purchases'
  },
]

export default function FeaturesPage() {
  const categories = Array.from(new Set(features.map(f => f.category)))

  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
          Features
        </h1>
        <p className="text-gray-400 text-lg max-w-3xl mx-auto">
          ArbFinder Suite is a comprehensive arbitrage finding platform with powerful tools
          for discovering, analyzing, and tracking profitable deals across multiple marketplaces.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-neutral-900 rounded-lg p-4 border border-green-500/20 text-center">
          <div className="text-3xl font-bold text-green-400">{features.length}</div>
          <div className="text-sm text-gray-400 mt-1">Features</div>
        </div>
        <div className="bg-neutral-900 rounded-lg p-4 border border-blue-500/20 text-center">
          <div className="text-3xl font-bold text-blue-400">{categories.length}</div>
          <div className="text-sm text-gray-400 mt-1">Categories</div>
        </div>
        <div className="bg-neutral-900 rounded-lg p-4 border border-purple-500/20 text-center">
          <div className="text-3xl font-bold text-purple-400">3</div>
          <div className="text-sm text-gray-400 mt-1">Interfaces</div>
        </div>
        <div className="bg-neutral-900 rounded-lg p-4 border border-yellow-500/20 text-center">
          <div className="text-3xl font-bold text-yellow-400">5+</div>
          <div className="text-sm text-gray-400 mt-1">Data Sources</div>
        </div>
      </div>

      {/* Features by Category */}
      {categories.map(category => (
        <div key={category} className="space-y-4">
          <h2 className="text-2xl font-bold text-green-400 flex items-center">
            <span className="mr-2">📂</span>
            {category}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features
              .filter(f => f.category === category)
              .map((feature, idx) => (
                <div
                  key={idx}
                  className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-green-500/50 transition group"
                >
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-green-400 transition">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              ))}
          </div>
        </div>
      ))}

      {/* CTA */}
      <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-lg p-8 border border-green-500/20 text-center">
        <h2 className="text-2xl font-bold text-white mb-3">Ready to Find Deals?</h2>
        <p className="text-gray-400 mb-6">
          Start discovering arbitrage opportunities across multiple marketplaces today
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="bg-green-700 hover:bg-green-600 px-8 py-3 rounded-lg font-semibold transition"
          >
            View Dashboard
          </Link>
          <Link
            href="/docs"
            className="bg-neutral-800 hover:bg-neutral-700 px-8 py-3 rounded-lg font-semibold transition"
          >
            Read Documentation
          </Link>
        </div>
      </div>
    </main>
  )
}
