/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Enable static exports for Cloudflare Pages
  // Uncomment the line below for Cloudflare deployment
  // output: 'export',
};

module.exports = nextConfig;
