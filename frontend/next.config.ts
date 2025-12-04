import type { NextConfig } from 'next'

const nextConfig: NextConfig = { 
  reactStrictMode: true,
  output: 'standalone',
  // Enable static exports for Cloudflare Pages
  // Uncomment the line below for Cloudflare deployment
  // output: 'export',
}

export default nextConfig
