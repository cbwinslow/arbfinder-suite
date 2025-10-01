export const metadata = { title: 'ArbFinder', description: 'Find arbitrage deals' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en"><body className="min-h-screen bg-black text-green-400">{children}</body></html>
  )
}
