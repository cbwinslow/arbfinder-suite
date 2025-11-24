'use client'
import Link from 'next/link'

interface DocSection {
  icon: string
  title: string
  description: string
  links: { label: string; href: string; external?: boolean }[]
}

const docSections: DocSection[] = [
  {
    icon: '🚀',
    title: 'Getting Started',
    description: 'Quick start guides and installation instructions',
    links: [
      { label: 'Quick Start Guide', href: 'https://github.com/cbwinslow/arbfinder-suite#quick-start', external: true },
      { label: 'Installation', href: 'https://github.com/cbwinslow/arbfinder-suite#installation', external: true },
      { label: 'AI Quickstart', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/AI_QUICKSTART.md', external: true },
    ]
  },
  {
    icon: '📖',
    title: 'User Guides',
    description: 'Comprehensive guides for using all features',
    links: [
      { label: 'CLI Usage', href: 'https://github.com/cbwinslow/arbfinder-suite#usage', external: true },
      { label: 'Analysis CLI Guide', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/ANALYSIS_CLI.md', external: true },
      { label: 'API Documentation', href: 'https://github.com/cbwinslow/arbfinder-suite#api-server', external: true },
      { label: 'Examples & Tutorials', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/EXAMPLES.md', external: true },
    ]
  },
  {
    icon: '🏗️',
    title: 'Architecture & Design',
    description: 'System architecture and technical documentation',
    links: [
      { label: 'Project Summary', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/PROJECT_SUMMARY.md', external: true },
      { label: 'TUI Architecture', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/tui/ARCHITECTURE.md', external: true },
      { label: 'Database Schema', href: 'https://github.com/cbwinslow/arbfinder-suite#database-schema', external: true },
    ]
  },
  {
    icon: '👨‍💻',
    title: 'Developer Resources',
    description: 'Development setup and contribution guides',
    links: [
      { label: 'Developer Guide', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/DEVELOPER.md', external: true },
      { label: 'Contributing Guidelines', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/CONTRIBUTING.md', external: true },
      { label: 'CI/CD Automation', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/CI_CD_AUTOMATION.md', external: true },
    ]
  },
  {
    icon: '🔬',
    title: 'Research & Analysis',
    description: 'Research reports and methodologies',
    links: [
      { label: 'Research Report', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/RESEARCH_REPORT.md', external: true },
      { label: 'New Features', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/NEW_FEATURES.md', external: true },
    ]
  },
  {
    icon: '🗺️',
    title: 'Roadmap & Planning',
    description: 'Future plans and feature roadmap',
    links: [
      { label: 'Enterprise Roadmap', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/docs/ENTERPRISE_ROADMAP.md', external: true },
      { label: 'Changelog', href: 'https://github.com/cbwinslow/arbfinder-suite/blob/main/CHANGELOG.md', external: true },
    ]
  },
]

export default function DocsPage() {
  return (
    <main className="mx-auto max-w-7xl p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Documentation
        </h1>
        <p className="text-gray-400 text-lg max-w-3xl mx-auto">
          Everything you need to know about using, developing, and deploying ArbFinder Suite
        </p>
      </div>

      {/* Search Box (placeholder for future search functionality) */}
      <div className="bg-neutral-900 rounded-lg p-6 border border-blue-500/20">
        <div className="flex items-center gap-3">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search documentation... (coming soon)"
            className="flex-1 bg-transparent border-none focus:outline-none text-white placeholder-gray-500"
            disabled
          />
        </div>
      </div>

      {/* Documentation Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {docSections.map((section, idx) => (
          <div
            key={idx}
            className="bg-neutral-900 p-6 rounded-lg border border-gray-800 hover:border-blue-500/50 transition"
          >
            <div className="flex items-start space-x-4">
              <div className="text-4xl">{section.icon}</div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-white mb-2">{section.title}</h2>
                <p className="text-gray-400 text-sm mb-4">{section.description}</p>
                <ul className="space-y-2">
                  {section.links.map((link, linkIdx) => (
                    <li key={linkIdx}>
                      {link.external ? (
                        <a
                          href={link.href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1 transition"
                        >
                          {link.label}
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      ) : (
                        <Link
                          href={link.href}
                          className="text-blue-400 hover:text-blue-300 text-sm transition"
                        >
                          {link.label}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-8 border border-blue-500/20">
        <h2 className="text-2xl font-bold text-white mb-4 text-center">Quick Links</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <a
            href="https://github.com/cbwinslow/arbfinder-suite"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg border border-gray-800 hover:border-blue-500/50 transition text-center"
          >
            <div className="text-2xl mb-2">📦</div>
            <div className="text-sm font-semibold text-white">GitHub Repo</div>
          </a>
          <a
            href="https://github.com/cbwinslow/arbfinder-suite/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg border border-gray-800 hover:border-blue-500/50 transition text-center"
          >
            <div className="text-2xl mb-2">🐛</div>
            <div className="text-sm font-semibold text-white">Report Issues</div>
          </a>
          <Link
            href="/features"
            className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg border border-gray-800 hover:border-blue-500/50 transition text-center"
          >
            <div className="text-2xl mb-2">✨</div>
            <div className="text-sm font-semibold text-white">Features</div>
          </Link>
          <Link
            href="/about"
            className="bg-neutral-900 hover:bg-neutral-800 p-4 rounded-lg border border-gray-800 hover:border-blue-500/50 transition text-center"
          >
            <div className="text-2xl mb-2">ℹ️</div>
            <div className="text-sm font-semibold text-white">About</div>
          </Link>
        </div>
      </div>
    </main>
  )
}
