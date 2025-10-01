import './globals.css'

export const metadata = {
  title: 'ArbFinder Suite - Arbitrage Finder',
  description: 'Find arbitrage opportunities across multiple marketplaces'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-black text-green-400">
        {children}
        <footer className="border-t border-gray-800 mt-12 py-6">
          <div className="max-w-7xl mx-auto px-6 text-center text-gray-500 text-sm">
            <p>ArbFinder Suite v0.3 - Find deals, save money</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
