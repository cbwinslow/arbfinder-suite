'use client'
import Link from 'next/link'

export default function AboutPage() {
  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          About ArbFinder Suite
        </h1>
        <p className="text-gray-400 text-lg max-w-3xl mx-auto">
          A comprehensive platform for discovering arbitrage opportunities across multiple online marketplaces
        </p>
      </div>

      {/* Version Info */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-purple-500/20 text-center">
        <div className="text-sm text-gray-400 mb-2">Current Version</div>
        <div className="text-3xl font-bold text-purple-400">v0.4.0</div>
        <div className="text-sm text-gray-500 mt-2">Enhanced CLI, TypeScript SDK, and Developer Tools</div>
      </div>

      {/* What is ArbFinder */}
      <div className="bg-neutral-900 rounded-lg p-8 border border-gray-800">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
          <span className="mr-2">🎯</span>
          What is ArbFinder Suite?
        </h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-gray-300 leading-relaxed mb-4">
            ArbFinder Suite is a powerful arbitrage finding platform that helps users discover profitable
            opportunities by comparing prices across multiple online marketplaces. The system automatically
            crawls various sources, collects pricing data, and identifies items selling below their fair
            market value.
          </p>
          <p className="text-gray-300 leading-relaxed">
            Whether you're a reseller, collector, or bargain hunter, ArbFinder Suite provides the tools
            you need to find undervalued items and make informed purchasing decisions.
          </p>
        </div>
      </div>

      {/* Key Features */}
      <div className="bg-neutral-900 rounded-lg p-8 border border-gray-800">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <span className="mr-2">✨</span>
          Key Capabilities
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start space-x-3">
            <div className="text-2xl">🔍</div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Multi-Source Data Collection</h3>
              <p className="text-gray-400 text-sm">
                Automatically crawls ShopGoodwill, GovDeals, GovernmentSurplus, and eBay for comprehensive market coverage
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl">💰</div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Price Intelligence</h3>
              <p className="text-gray-400 text-sm">
                Compares live listings with historical sold prices to identify arbitrage opportunities
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl">📊</div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">Real-Time Analytics</h3>
              <p className="text-gray-400 text-sm">
                Track statistics, trends, and market insights with comprehensive dashboards
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="text-2xl">🤖</div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">AI-Powered Automation</h3>
              <p className="text-gray-400 text-sm">
                Leverage CrewAI for automated research, pricing analysis, and listing generation
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-neutral-900 rounded-lg p-8 border border-gray-800">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <span className="mr-2">🛠️</span>
          Technology Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-green-400 mb-3">Backend</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>• Python 3.9+</li>
              <li>• FastAPI</li>
              <li>• SQLite</li>
              <li>• AsyncIO</li>
              <li>• Pytest</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-400 mb-3">Frontend</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>• Next.js 14</li>
              <li>• React 18</li>
              <li>• TypeScript</li>
              <li>• Tailwind CSS</li>
              <li>• Mobile-First Design</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-purple-400 mb-3">DevOps</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>• Docker</li>
              <li>• Docker Compose</li>
              <li>• GitHub Actions</li>
              <li>• Pre-commit Hooks</li>
              <li>• Automated Testing</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Open Source */}
      <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-lg p-8 border border-purple-500/20">
        <h2 className="text-2xl font-bold text-white mb-4 flex items-center justify-center">
          <span className="mr-2">🌟</span>
          Open Source Project
        </h2>
        <p className="text-gray-300 text-center mb-6 max-w-2xl mx-auto">
          ArbFinder Suite is open source and available under the MIT License.
          We welcome contributions, feedback, and feature requests from the community.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://github.com/cbwinslow/arbfinder-suite"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-purple-700 hover:bg-purple-600 px-8 py-3 rounded-lg font-semibold transition text-center"
          >
            View on GitHub
          </a>
          <a
            href="https://github.com/cbwinslow/arbfinder-suite/blob/main/CONTRIBUTING.md"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-neutral-800 hover:bg-neutral-700 px-8 py-3 rounded-lg font-semibold transition text-center"
          >
            Contributing Guide
          </a>
        </div>
      </div>

      {/* License & Credits */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-xl font-bold text-white mb-4">License & Credits</h2>
        <div className="space-y-3 text-sm text-gray-400">
          <p>
            <strong className="text-white">License:</strong> MIT License - see{' '}
            <a
              href="https://github.com/cbwinslow/arbfinder-suite/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              LICENSE
            </a>{' '}
            file for details
          </p>
          <p>
            <strong className="text-white">Author:</strong> cbwinslow and contributors
          </p>
          <p>
            <strong className="text-white">Repository:</strong>{' '}
            <a
              href="https://github.com/cbwinslow/arbfinder-suite"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              github.com/cbwinslow/arbfinder-suite
            </a>
          </p>
        </div>
      </div>

      {/* Get Started CTA */}
      <div className="text-center">
        <Link
          href="/"
          className="inline-block bg-green-700 hover:bg-green-600 px-8 py-3 rounded-lg font-semibold transition"
        >
          Get Started →
        </Link>
      </div>
    </main>
  )
}
