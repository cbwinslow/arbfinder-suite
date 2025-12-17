# Cloudflare Platform Setup Guide

**Version**: 2.0  
**Last Updated**: 2025-12-15  
**Platform**: Cloudflare Workers, Pages, D1, R2, KV  

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Cost Estimation](#cost-estimation)

---

## Overview

This guide walks through setting up ArbFinder Suite on the Cloudflare platform, leveraging:

- **Cloudflare Workers**: Serverless compute for backend API
- **Cloudflare Pages**: Static site hosting for Next.js frontend with Google Tag Manager
- **Cloudflare D1**: SQLite-based edge database
- **Cloudflare R2**: S3-compatible object storage
- **Cloudflare KV**: Key-value storage for caching and alerts
- **Cloudflare Hyperdrive**: Database connection pooling
- **Cloudflare Durable Objects**: Stateful edge computing for snipe scheduling
- **Cloudflare Queues**: Async job processing for crawlers and alerts
- **Cloudflare WAF**: Web Application Firewall
- **Analytics Engine**: Custom business metrics and tracking

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge Network                  │
│                     (200+ locations)                        │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│  Pages         │   │  Workers        │   │   WAF       │
│  (Frontend)    │   │  (Backend API)  │   │  (Security) │
└────────────────┘   └────────┬────────┘   └─────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│  D1            │   │   R2            │   │   KV        │
│  (Database)    │   │  (Storage)      │   │  (Cache)    │
└────────────────┘   └─────────────────┘   └─────────────┘
```

---

## Prerequisites

### 1. Cloudflare Account

1. Sign up at https://dash.cloudflare.com/sign-up
2. Verify your email address
3. Note your Account ID (Dashboard > Workers > Account ID)

### 2. API Token

Create an API token with required permissions:

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use "Edit Cloudflare Workers" template
4. Add additional permissions:
   - Account > Account Settings > Read
   - Account > Workers R2 Storage > Edit
   - Account > Workers KV Storage > Edit
   - Account > D1 > Edit
   - Zone > Zone Settings > Edit (if using custom domain)
5. Click "Continue to summary" and "Create Token"
6. **Save the token securely** (shown only once)

### 3. Development Tools

Install required tools:

```bash
# Node.js 18+ and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Wrangler CLI (Cloudflare's CLI tool)
npm install -g wrangler

# Python 3.9+ (for setup scripts)
sudo apt-get install python3 python3-pip

# Python dependencies
pip install requests rich
```

### 4. Project Setup

Clone the repository:

```bash
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite
```

---

## Quick Start

### Automated Setup (Recommended)

Use the automated setup script:

```bash
# Set environment variables
export CLOUDFLARE_API_TOKEN="your-api-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"

# Run setup script
python3 scripts/cloudflare/setup_cloudflare.py --interactive

# Or with arguments
python3 scripts/cloudflare/setup_cloudflare.py \
  --api-key YOUR_TOKEN \
  --account-id YOUR_ACCOUNT_ID \
  --project-name arbfinder \
  --environment production
```

The script will:
1. Verify API credentials
2. Create D1 database
3. Create R2 buckets
4. Create KV namespaces
5. Generate configuration
6. Provide next steps

### Manual Setup

If you prefer manual setup, follow the [Detailed Setup](#detailed-setup) section.

---

## Detailed Setup

### Step 1: D1 Database

Create a D1 database for edge data storage:

```bash
# Authenticate with Wrangler
wrangler login

# Create production database
wrangler d1 create arbfinder-db-production

# Create staging database
wrangler d1 create arbfinder-db-staging

# Note the database IDs from output
```

**Output Example**:
```
✅ Successfully created DB 'arbfinder-db-production'

[[d1_databases]]
binding = "DB"
database_name = "arbfinder-db-production"
database_id = "abc123-def456-ghi789"
```

Apply database schema:

```bash
# Create schema file
cat > database/d1_schema.sql << 'EOF'
CREATE TABLE listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  price REAL NOT NULL,
  currency TEXT DEFAULT 'USD',
  condition TEXT,
  timestamp REAL NOT NULL,
  metadata TEXT
);

CREATE INDEX idx_listings_source ON listings(source);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_timestamp ON listings(timestamp);

CREATE TABLE comps (
  key_title TEXT PRIMARY KEY,
  avg_price REAL,
  median_price REAL,
  count INTEGER,
  timestamp REAL
);
EOF

# Apply schema
wrangler d1 execute arbfinder-db-production --file=database/d1_schema.sql
```

### Step 2: R2 Storage

Create R2 buckets for object storage:

```bash
# Images bucket
wrangler r2 bucket create arbfinder-images-production
wrangler r2 bucket create arbfinder-images-staging

# Data exports bucket
wrangler r2 bucket create arbfinder-data-production
wrangler r2 bucket create arbfinder-data-staging

# Backups bucket
wrangler r2 bucket create arbfinder-backups-production
```

Configure CORS for image bucket:

```bash
# Create CORS configuration
cat > cors-config.json << 'EOF'
{
  "CORSRules": [{
    "AllowedOrigins": ["https://arbfinder.com", "https://staging.arbfinder.com"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }]
}
EOF

# Apply CORS (using AWS S3 CLI with R2 endpoint)
aws s3api put-bucket-cors \
  --bucket arbfinder-images-production \
  --cors-configuration file://cors-config.json \
  --endpoint-url https://<account-id>.r2.cloudflarestorage.com
```

### Step 3: KV Namespaces

Create KV namespaces for caching:

```bash
# Cache namespace
wrangler kv:namespace create "CACHE" --preview
wrangler kv:namespace create "CACHE"

# Sessions namespace
wrangler kv:namespace create "SESSIONS" --preview
wrangler kv:namespace create "SESSIONS"

# Config namespace
wrangler kv:namespace create "CONFIG" --preview
wrangler kv:namespace create "CONFIG"

# Note the namespace IDs from output
```

### Step 4: Configure Wrangler

Update `cloudflare/wrangler.toml`:

```toml
name = "arbfinder-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"
node_compat = true

# Production environment
[env.production]
name = "arbfinder-worker-production"
route = { pattern = "arbfinder.com/api/*", zone_name = "arbfinder.com" }

# D1 Database
[[env.production.d1_databases]]
binding = "DB"
database_name = "arbfinder-db-production"
database_id = "your-database-id-here"

# R2 Buckets
[[env.production.r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images-production"

[[env.production.r2_buckets]]
binding = "DATA"
bucket_name = "arbfinder-data-production"

# KV Namespaces
[[env.production.kv_namespaces]]
binding = "CACHE"
id = "your-cache-namespace-id"

[[env.production.kv_namespaces]]
binding = "SESSIONS"
id = "your-sessions-namespace-id"

[[env.production.kv_namespaces]]
binding = "CONFIG"
id = "your-config-namespace-id"

# Environment Variables
[env.production.vars]
ENVIRONMENT = "production"
API_BASE_URL = "https://api.arbfinder.com"

# Secrets (use wrangler secret put)
# OPENROUTER_API_KEY
# EBAY_APP_ID
# STRIPE_SECRET_KEY

# Staging environment
[env.staging]
name = "arbfinder-worker-staging"
route = { pattern = "staging.arbfinder.com/api/*", zone_name = "arbfinder.com" }

# (Repeat bindings with staging IDs)
```

### Step 5: Set Secrets

Store sensitive values as secrets:

```bash
# OpenRouter API key
wrangler secret put OPENROUTER_API_KEY --env production
# Enter value when prompted

# eBay API credentials
wrangler secret put EBAY_APP_ID --env production
wrangler secret put EBAY_CERT_ID --env production

# Stripe API key
wrangler secret put STRIPE_SECRET_KEY --env production

# Database URL (if using external PostgreSQL)
wrangler secret put DATABASE_URL --env production
```

### Step 6: Deploy Worker

Deploy the Cloudflare Worker:

```bash
cd cloudflare

# Install dependencies
npm install

# Build TypeScript
npm run build

# Deploy to production
wrangler deploy --env production

# Deploy to staging
wrangler deploy --env staging
```

**Output**:
```
✨ Built successfully!
🚀 Deployed arbfinder-worker-production
   https://arbfinder-worker-production.your-subdomain.workers.dev
```

### Step 7: Deploy Pages

Deploy frontend to Cloudflare Pages:

#### Via Dashboard (Recommended for GitHub)

1. Go to https://dash.cloudflare.com/pages
2. Click "Create a project"
3. Connect to Git provider (GitHub)
4. Select `arbfinder-suite` repository
5. Configure build:
   - **Framework preset**: Next.js
   - **Build command**: `cd frontend && npm run build`
   - **Build output directory**: `frontend/.next`
   - **Root directory**: `/`
   - **Environment variables**:
     - `NEXT_PUBLIC_API_BASE=https://api.arbfinder.com`
     - `NODE_VERSION=18`

#### Via Wrangler

```bash
cd frontend

# Build Next.js
npm run build

# Deploy to Pages
npx wrangler pages deploy .next \
  --project-name arbfinder-frontend \
  --branch main
```

### Step 8: Configure WAF

Set up Web Application Firewall rules:

1. Go to Cloudflare Dashboard > Security > WAF
2. Enable "OWASP ModSecurity Core Rule Set"
3. Add custom rules:

**Rate Limiting Rule**:
```
(http.request.uri.path contains "/api/crawl") and
(rate(http.request.uri.path, 60s) > 10)
```
Action: Block for 1 hour

**SQL Injection Protection**:
```
(http.request.uri.query contains "UNION" or
 http.request.uri.query contains "SELECT" or
 http.request.body contains "'; DROP")
```
Action: Block

**Geographic Restrictions** (optional):
```
(ip.geoip.country ne "US" and
 ip.geoip.country ne "CA" and
 ip.geoip.country ne "GB")
```
Action: Challenge (CAPTCHA)

### Step 9: Configure Observability

#### Enable Workers Analytics Engine

Add to your Worker code:

```typescript
// cloudflare/src/analytics.ts
export async function trackEvent(
  env: Env,
  event: string,
  data: Record<string, any>
) {
  if (env.ANALYTICS) {
    await env.ANALYTICS.writeDataPoint({
      blobs: [event],
      doubles: [data.value || 0],
      indexes: [data.userId || 'anonymous']
    });
  }
}

// Usage in your Worker
await trackEvent(env, 'deal_found', {
  value: listing.margin,
  userId: user.id
});
```

#### Configure Logpush

1. Go to Dashboard > Analytics > Logs
2. Click "Add Logpush job"
3. Select destination (S3, R2, etc.)
4. Choose dataset: "Workers Trace Events"
5. Enable job

---

## Configuration

### Environment Variables

Create `.env.production`:

```bash
# Cloudflare
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-api-token

# API Keys (stored as Wrangler secrets)
OPENROUTER_API_KEY=your-openrouter-key
EBAY_APP_ID=your-ebay-app-id
EBAY_CERT_ID=your-ebay-cert-id
STRIPE_SECRET_KEY=sk_live_xxx

# Database
DATABASE_URL=your-d1-or-postgres-url

# Frontend
NEXT_PUBLIC_API_BASE=https://api.arbfinder.com
```

### Custom Domain

Configure custom domain for Worker and Pages:

#### Worker Custom Domain

1. Go to Dashboard > Workers > arbfinder-worker
2. Click "Triggers" tab
3. Click "Add Custom Domain"
4. Enter: `api.arbfinder.com`
5. Click "Add Custom Domain"

#### Pages Custom Domain

1. Go to Dashboard > Pages > arbfinder-frontend
2. Click "Custom domains"
3. Click "Set up a custom domain"
4. Enter: `arbfinder.com` or `www.arbfinder.com`
5. Follow DNS instructions

---

## Deployment

### Continuous Deployment

#### GitHub Actions for Workers

Create `.github/workflows/deploy-worker.yml`:

```yaml
name: Deploy Worker

on:
  push:
    branches: [main]
    paths:
      - 'cloudflare/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        working-directory: ./cloudflare
        run: npm ci
      
      - name: Deploy to Cloudflare Workers
        working-directory: ./cloudflare
        run: npx wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

#### Automatic Pages Deployment

Cloudflare Pages automatically deploys on:
- Push to main branch (production)
- Pull requests (preview deployments)

---

## Troubleshooting

### Common Issues

#### Issue: "Error 1101: Worker threw exception"

**Cause**: Uncaught exception in Worker code  
**Solution**:
```bash
# View Worker logs
wrangler tail --env production

# Check for errors in the logs
```

#### Issue: "R2 bucket not found"

**Cause**: Bucket binding incorrect in wrangler.toml  
**Solution**:
```bash
# List R2 buckets
wrangler r2 bucket list

# Verify bucket name in wrangler.toml matches
```

#### Issue: "KV namespace not found"

**Cause**: KV namespace ID incorrect  
**Solution**:
```bash
# List KV namespaces
wrangler kv:namespace list

# Update namespace ID in wrangler.toml
```

#### Issue: "CORS error from frontend"

**Cause**: CORS headers not set in Worker  
**Solution**:
```typescript
// Add CORS headers in Worker
const headers = {
  'Access-Control-Allow-Origin': 'https://arbfinder.com',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
};
```

### Debug Mode

Enable verbose logging:

```bash
# Worker logs (real-time)
wrangler tail --env production --format pretty

# Pages logs
wrangler pages deployment tail --project-name arbfinder-frontend

# D1 query logging
wrangler d1 execute arbfinder-db-production --command="PRAGMA query_log"
```

---

## Cost Estimation

### Free Tier

Cloudflare offers generous free tiers:

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Workers | 100,000 requests/day | $5/10M requests |
| Pages | 500 builds/month | Unlimited |
| D1 | 5GB storage, 5M reads/day | $5/10M reads |
| R2 | 10GB storage, 1M Class A ops | $0.015/GB/month |
| KV | 100,000 reads/day, 1000 writes/day | $0.50/1M reads |

### Estimated Costs (1000 Active Users)

**Assumptions**:
- 1000 active users
- 50 requests per user per day
- 10GB image storage
- 5GB database storage

**Monthly Costs**:
- Workers: ~$0 (within free tier: 50k requests/day)
- Pages: $0 (within free tier)
- D1: ~$0 (within free tier: 1.5M reads/month)
- R2: ~$0.15 (10GB storage)
- KV: ~$0 (within free tier)

**Total: < $5/month** for 1000 users

### Scaling to 10,000 Users

**Assumptions**:
- 10,000 active users
- 50 requests per user per day
- 100GB image storage
- 20GB database storage

**Monthly Costs**:
- Workers: ~$7.50 (15M requests/month)
- Pages: $0
- D1: ~$10 (30M reads/month)
- R2: ~$1.50 (100GB storage)
- KV: ~$2 (10M reads/month)

**Total: ~$21/month** for 10,000 users

---

## Next Steps

After completing setup:

1. **Test Deployment**:
   ```bash
   # Test Worker endpoint
   curl https://api.arbfinder.com/health
   
   # Test Pages deployment
   curl https://arbfinder.com
   ```

2. **Monitor Performance**:
   - Dashboard > Workers > Analytics
   - Dashboard > Pages > Analytics
   - Set up alerts for errors

3. **Security Hardening**:
   - Review WAF rules
   - Enable rate limiting
   - Configure bot protection

4. **Optimize Costs**:
   - Enable caching for static assets
   - Use KV for frequently accessed data
   - Optimize image sizes before R2 upload

5. **Set Up Monitoring**:
   - Configure external monitoring (UptimeRobot, Pingdom)
   - Set up Sentry for error tracking
   - Enable Logpush for log analysis

---

## Resources

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [D1 Documentation](https://developers.cloudflare.com/d1/)
- [R2 Documentation](https://developers.cloudflare.com/r2/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [Community Discord](https://discord.gg/cloudflaredev)

---

## New Features Setup

### Auction Sniping

The sniping tool allows you to schedule bids to win auctions at the last moment:

**How it works**:
1. Monitor auction listings with API endpoints
2. Schedule a snipe (bid) through Durable Objects
3. System executes bid via API at precise timing before auction closes

**Setup**:
```bash
# Create Durable Object binding (already in wrangler.toml)
# No additional setup needed - managed by Worker
```

**API Usage**:
```bash
# Schedule a snipe
curl -X POST https://api.arbfinder.com/api/snipes \
  -H "Content-Type: application/json" \
  -d '{
    "listing_url": "https://example.com/auction/12345",
    "max_bid": 150.00,
    "auction_end_time": "2024-12-20T15:00:00Z",
    "lead_time_seconds": 5
  }'

# List scheduled snipes
curl https://api.arbfinder.com/api/snipes

# Cancel a snipe
curl -X DELETE https://api.arbfinder.com/api/snipes/SNIPE_ID
```

### Price Alerts

Set up alerts for items matching your price criteria:

**Setup KV Namespace**:
```bash
# Already configured in wrangler.toml as ALERTS
```

**API Usage**:
```bash
# Create price alert
curl -X POST https://api.arbfinder.com/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "RTX 3080",
    "min_price": 200,
    "max_price": 400,
    "notification_method": "email",
    "notification_target": "user@example.com"
  }'

# List alerts
curl https://api.arbfinder.com/api/alerts

# Delete alert
curl -X DELETE https://api.arbfinder.com/api/alerts/ALERT_ID
```

### Google Tag Manager Integration

Add Google Tag Manager to track user behavior:

**1. Get GTM Container ID**:
- Sign up at https://tagmanager.google.com
- Create a new container
- Note your container ID (GTM-XXXXXXX)

**2. Update Environment Variable**:
```bash
# In wrangler.toml
[vars]
GOOGLE_TAG_MANAGER_ID = "GTM-XXXXXXX"
```

**3. Add to Pages Deployment**:
The GTM script is automatically injected into all pages via the layout component.

### Crawl4AI/CrewAI Runner

Run AI agents and crews for data ingestion:

**Setup**:
```bash
# Queue binding already configured in wrangler.toml
```

**API Usage**:
```bash
# Start a crawler crew
curl -X POST https://api.arbfinder.com/api/crews/run \
  -H "Content-Type: application/json" \
  -d '{
    "crew_type": "price_ingestion",
    "targets": ["shopgoodwill", "govdeals"],
    "query": "electronics"
  }'

# Check crew status
curl https://api.arbfinder.com/api/crews/status/CREW_ID

# Get crew results
curl https://api.arbfinder.com/api/crews/results/CREW_ID
```

---

**End of Cloudflare Setup Guide**
