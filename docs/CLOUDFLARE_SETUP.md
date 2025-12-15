# Cloudflare Platform Setup Guide
# ArbFinder Suite

**Version**: 1.0  
**Date**: 2025-12-15  
**Difficulty**: Intermediate  
**Estimated Time**: 2-3 hours

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Account Setup](#account-setup)
3. [API Token Generation](#api-token-generation)
4. [Workers Deployment](#workers-deployment)
5. [D1 Database Setup](#d1-database-setup)
6. [R2 Storage Configuration](#r2-storage-configuration)
7. [Pages Deployment](#pages-deployment)
8. [WAF Configuration](#waf-configuration)
9. [Observability Setup](#observability-setup)
10. [Automated Setup Script](#automated-setup-script)
11. [Verification](#verification)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ Cloudflare account (free tier available)
- ✅ GitHub account (for Pages deployment)
- ✅ Credit card (for identity verification, won't be charged on free tier)

### Required Tools
```bash
# Install Node.js (v18+)
node --version  # Should be v18 or higher

# Install npm packages globally
npm install -g wrangler@latest

# Verify installation
wrangler --version
```

### Required Knowledge
- Basic command line usage
- Git fundamentals
- JavaScript/TypeScript basics
- SQL basics (for D1)

---

## Account Setup

### Step 1: Create Cloudflare Account

1. Navigate to [https://dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up)
2. Enter email and create password
3. Verify email address
4. Complete identity verification (requires credit card)

### Step 2: Enable Required Products

In the Cloudflare dashboard:

1. **Workers & Pages**
   - Navigate to Workers & Pages
   - Accept terms of service
   - Note: Free tier includes 100,000 requests/day

2. **D1 Database**
   - Navigate to Storage & Databases → D1
   - Enable D1 (currently in open beta)
   - Note: Free tier includes 5 GB storage

3. **R2 Storage**
   - Navigate to R2
   - Enable R2
   - Note: Free tier includes 10 GB storage/month

---

## API Token Generation

### Creating an API Token

API tokens are required for CLI and automated deployments.

#### Option 1: Using the Dashboard

1. Go to [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click "Create Token"
3. Use "Edit Cloudflare Workers" template
4. Customize permissions:
   ```
   Account Settings:Read
   Workers Scripts:Edit
   Workers KV Storage:Edit
   Workers Routes:Edit
   D1:Edit
   R2:Edit
   Pages:Edit
   Analytics:Read
   ```
5. Set Account Resources to your account
6. Set IP filtering (optional, recommended for security)
7. Set TTL (optional, recommended: 1 year)
8. Click "Continue to Summary"
9. Click "Create Token"
10. **IMPORTANT**: Copy the token immediately (it won't be shown again)

#### Option 2: Using the API Key Manager Script

We provide a helper script to create tokens programmatically:

```bash
# Run the API key manager script
./scripts/cloudflare/api_key_manager.sh create

# Follow the prompts
# The script will guide you through creating a token with correct permissions
```

### Storing the API Token

**Environment Variable (Recommended)**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export CLOUDFLARE_API_TOKEN="your-token-here"
export CLOUDFLARE_ACCOUNT_ID="your-account-id-here"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

**Wrangler Configuration**:
```bash
# Login with wrangler (stores token securely)
wrangler login

# Or set token manually
wrangler config set api_token="your-token-here"
```

**GitHub Secrets** (for CI/CD):
```
1. Go to repository → Settings → Secrets and variables → Actions
2. Add secret: CLOUDFLARE_API_TOKEN
3. Add secret: CLOUDFLARE_ACCOUNT_ID
```

---

## Workers Deployment

### Understanding Workers

Cloudflare Workers are serverless functions that run on Cloudflare's edge network.

**Benefits**:
- Global distribution (low latency)
- No server management
- Pay per request
- Automatic scaling

### Step 1: Configure wrangler.toml

The `cloudflare/wrangler.toml` file defines your Worker configuration:

```toml
name = "arbfinder-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[env.production]
name = "arbfinder-worker-prod"
workers_dev = false
routes = [
  { pattern = "api.arbfinder.com/*", zone_name = "arbfinder.com" }
]

[env.staging]
name = "arbfinder-worker-staging"
workers_dev = true

# Environment variables
[vars]
ENVIRONMENT = "production"
API_BASE_URL = "https://api.arbfinder.com"

# Bindings (configured in next steps)
[[d1_databases]]
binding = "DB"
database_name = "arbfinder"
database_id = "TO_BE_CONFIGURED"

[[r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images"

[[r2_buckets]]
binding = "DATA"
bucket_name = "arbfinder-data"

[[kv_namespaces]]
binding = "CACHE"
id = "TO_BE_CONFIGURED"

# Cron triggers for scheduled tasks
[triggers]
crons = [
  "0 */4 * * *",   # Crawler every 4 hours
  "*/15 * * * *",  # Metadata enrichment every 15 min
  "*/10 * * * *"   # Image processing every 10 min
]
```

### Step 2: Deploy Worker

```bash
# Navigate to cloudflare directory
cd cloudflare

# Install dependencies
npm install

# Deploy to staging
npm run deploy:staging

# Deploy to production
npm run deploy:production

# Or use wrangler directly
wrangler deploy --env production
```

### Step 3: Verify Deployment

```bash
# Test health endpoint
curl https://arbfinder-worker-prod.YOUR_SUBDOMAIN.workers.dev/api/health

# Should return:
# {"status":"ok","timestamp":1702650000000}
```

### Step 4: Configure Custom Domain (Optional)

```bash
# Add route for custom domain
wrangler route add "api.arbfinder.com/*" arbfinder-worker-prod

# Update DNS:
# 1. Go to Cloudflare DNS settings
# 2. Add CNAME record: api → arbfinder-worker-prod.workers.dev
# 3. Enable proxy (orange cloud)
```

---

## D1 Database Setup

### Understanding D1

D1 is Cloudflare's SQL database built on SQLite. It's edge-distributed for low latency.

### Step 1: Create Database

```bash
# Create database
wrangler d1 create arbfinder

# Output will show database ID:
# Database created with ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Copy this ID to wrangler.toml
```

### Step 2: Update wrangler.toml

```toml
[[d1_databases]]
binding = "DB"
database_name = "arbfinder"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # From step 1
```

### Step 3: Apply Schema

```bash
# Apply the database schema
wrangler d1 execute arbfinder --file=../database/cloudflare_schema.sql

# Or execute SQL directly
wrangler d1 execute arbfinder --command="CREATE TABLE IF NOT EXISTS listings (...)"
```

**Schema File** (`database/cloudflare_schema.sql`):
```sql
-- Listings table
CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  price REAL,
  currency TEXT DEFAULT 'USD',
  condition TEXT,
  image_url TEXT,
  metadata JSON,
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Comparables table
CREATE TABLE IF NOT EXISTS comps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  sold_price REAL NOT NULL,
  sold_date INTEGER NOT NULL,
  platform TEXT NOT NULL,
  condition TEXT,
  url TEXT,
  created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_listings_source ON listings(source);
CREATE INDEX IF NOT EXISTS idx_listings_created ON listings(created_at);
CREATE INDEX IF NOT EXISTS idx_comps_title ON comps(title);
CREATE INDEX IF NOT EXISTS idx_comps_date ON comps(sold_date);
```

### Step 4: Verify Database

```bash
# List tables
wrangler d1 execute arbfinder --command="SELECT name FROM sqlite_master WHERE type='table'"

# Insert test data
wrangler d1 execute arbfinder --command="INSERT INTO listings (source, url, title, price) VALUES ('test', 'https://test.com', 'Test Item', 100.00)"

# Query data
wrangler d1 execute arbfinder --command="SELECT * FROM listings LIMIT 10"
```

### Step 5: Query from Worker

In your Worker code:

```typescript
export default {
  async fetch(request: Request, env: Env) {
    // Query D1 database
    const results = await env.DB.prepare(
      "SELECT * FROM listings ORDER BY created_at DESC LIMIT 10"
    ).all();
    
    return Response.json(results);
  }
};
```

---

## R2 Storage Configuration

### Understanding R2

R2 is Cloudflare's S3-compatible object storage with no egress fees.

### Step 1: Create Buckets

```bash
# Create bucket for images
wrangler r2 bucket create arbfinder-images

# Create bucket for data exports
wrangler r2 bucket create arbfinder-data

# List buckets
wrangler r2 bucket list
```

### Step 2: Update wrangler.toml

Already configured in Workers section:
```toml
[[r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images"

[[r2_buckets]]
binding = "DATA"
bucket_name = "arbfinder-data"
```

### Step 3: Configure CORS (Optional)

For direct browser uploads:

```bash
# Create CORS policy file
cat > r2-cors-policy.json <<EOF
{
  "allowed_origins": ["https://arbfinder.com", "https://www.arbfinder.com"],
  "allowed_methods": ["GET", "PUT", "POST"],
  "allowed_headers": ["Content-Type"],
  "max_age_seconds": 3600
}
EOF

# Apply CORS policy (via dashboard or API)
# Currently CORS must be configured via dashboard:
# R2 → Select Bucket → Settings → CORS Policy
```

### Step 4: Upload Files

**From Worker**:
```typescript
// Upload file to R2
async function uploadImage(file: File, env: Env) {
  const filename = `${Date.now()}-${file.name}`;
  const buffer = await file.arrayBuffer();
  
  await env.IMAGES.put(filename, buffer, {
    httpMetadata: {
      contentType: file.type,
      cacheControl: "public, max-age=31536000"
    }
  });
  
  return filename;
}
```

**From CLI**:
```bash
# Upload file
wrangler r2 object put arbfinder-images/test.jpg --file=./test.jpg

# Download file
wrangler r2 object get arbfinder-images/test.jpg --file=./downloaded.jpg

# List objects
wrangler r2 object list arbfinder-images
```

### Step 5: Public Access (Optional)

To make buckets publicly accessible:

```bash
# Enable public access
# Go to R2 Dashboard → Select Bucket → Settings → Public Access
# Enable and note the public URL: https://pub-xxxxx.r2.dev
```

Or use a custom domain:
```bash
# In Cloudflare dashboard:
# 1. R2 → Select Bucket → Settings → Custom Domains
# 2. Add domain: images.arbfinder.com
# 3. DNS record will be created automatically
```

---

## Pages Deployment

### Understanding Pages

Cloudflare Pages is a JAMstack platform for deploying static sites and frontend frameworks.

### Step 1: Connect Repository

1. Go to Workers & Pages → Pages
2. Click "Create application"
3. Click "Connect to Git"
4. Authorize GitHub
5. Select repository: `cbwinslow/arbfinder-suite`
6. Configure build settings:
   ```
   Framework preset: Next.js
   Build command: npm run build
   Build output directory: out
   Root directory: frontend
   ```

### Step 2: Environment Variables

Add environment variables for Pages:

```
NEXT_PUBLIC_API_BASE=https://api.arbfinder.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### Step 3: Deploy

```bash
# Deploy via git push (automatic)
git push origin main

# Or deploy directly with wrangler
cd frontend
npm run build
wrangler pages deploy out --project-name=arbfinder
```

### Step 4: Custom Domain

1. Pages → arbfinder → Custom domains
2. Add domain: `arbfinder.com` and `www.arbfinder.com`
3. Follow DNS instructions
4. SSL certificate will be provisioned automatically

---

## WAF Configuration

### Understanding WAF

Web Application Firewall protects your application from attacks.

### Step 1: Enable WAF

WAF is included with Cloudflare's proxy. Ensure your domain is:
1. Added to Cloudflare
2. DNS proxied (orange cloud icon)

### Step 2: Configure Security Level

1. Go to Security → Settings
2. Set Security Level:
   ```
   Essentially Off: No protection (not recommended)
   Low: Only clear threats
   Medium: Moderate protection (recommended for most)
   High: Increased protection
   I'm Under Attack: Maximum protection
   ```

### Step 3: Create Custom Rules

**Rate Limiting Rule**:
```
Dashboard → Security → WAF → Rate limiting rules → Create rule

Name: API Rate Limit
When incoming requests match:
  - URI Path contains "/api/"
  
Then:
  - Block for 60 seconds
  - When rate exceeds 100 requests per 1 minute
  - Per IP address
```

**Bot Protection**:
```
Security → Bots → Configure Bot Management

Enable:
- ✅ Verified Bots (allow good bots)
- ✅ Machine Learning (detect bad bots)
- ✅ JavaScript Detection
- ✅ Block automated browser access
```

### Step 4: DDoS Protection

DDoS protection is automatic, but you can configure:

```
Security → DDoS

Enable:
- ✅ HTTP DDoS Attack Protection (automatic)
- ✅ Network-layer DDoS Attack Protection (automatic)

Configure sensitivity if needed (default is usually best)
```

### Step 5: Security Testing

Use the helper script:

```bash
# Run security tests
./scripts/cloudflare/test_security.sh

# This will test:
# - Rate limiting
# - DDoS protection
# - SQL injection prevention
# - XSS prevention
```

---

## Observability Setup

### Logging

**Enable Logpush** (requires paid plan):

```bash
# Create logpush job
wrangler logpush create \
  --destination-conf="https://logs.example.com/cloudflare" \
  --dataset=workers_trace_events \
  --fields=EventTimestampMs,EventType,Exceptions,Logs,ScriptName
```

**View Logs (Free tier)**:

```bash
# Tail worker logs in real-time
wrangler tail

# Filter by status
wrangler tail --status error

# Filter by method
wrangler tail --method POST
```

### Analytics

**Dashboard Analytics**:
1. Go to Workers & Pages → arbfinder-worker
2. View Metrics tab for:
   - Requests per second
   - Errors rate
   - CPU time
   - Duration

**GraphQL Analytics API**:

```bash
# Query analytics
curl -X POST https://api.cloudflare.com/client/v4/graphql \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { viewer { zones(filter: { zoneTag: \"YOUR_ZONE_ID\" }) { httpRequests1dGroups(limit: 10) { sum { requests } } } } }"
  }'
```

### Performance Monitoring

**Real User Monitoring (RUM)**:

Add to your frontend:

```html
<!-- Cloudflare Web Analytics -->
<script defer src='https://static.cloudflareinsights.com/beacon.min.js'
        data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
```

Get token from: Analytics → Web Analytics

---

## Automated Setup Script

We provide a comprehensive setup script to automate the entire process.

### Usage

```bash
# Make script executable
chmod +x scripts/cloudflare/setup.sh

# Run interactive setup
./scripts/cloudflare/setup.sh

# Or run with environment variables
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
./scripts/cloudflare/setup.sh --auto
```

### What the Script Does

1. ✅ Validates Cloudflare credentials
2. ✅ Creates D1 database
3. ✅ Applies database schema
4. ✅ Creates R2 buckets
5. ✅ Creates KV namespace
6. ✅ Deploys Workers
7. ✅ Configures bindings
8. ✅ Deploys Pages
9. ✅ Configures WAF rules
10. ✅ Sets up observability
11. ✅ Runs verification tests

### Script Output

```
🚀 ArbFinder Cloudflare Setup
=============================

Step 1/10: Validating credentials... ✅
Step 2/10: Creating D1 database... ✅
  Database ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Step 3/10: Applying schema... ✅
  Tables created: 5
Step 4/10: Creating R2 buckets... ✅
  Buckets: arbfinder-images, arbfinder-data
Step 5/10: Deploying Worker... ✅
  URL: https://arbfinder-worker.YOUR_SUBDOMAIN.workers.dev
Step 6/10: Deploying Pages... ✅
  URL: https://arbfinder.pages.dev
Step 7/10: Configuring WAF... ✅
  Rules created: 3
Step 8/10: Setting up observability... ✅
Step 9/10: Running tests... ✅
Step 10/10: Generating summary... ✅

Setup Complete! 🎉

Deployment URLs:
  - Worker: https://arbfinder-worker.YOUR_SUBDOMAIN.workers.dev
  - Frontend: https://arbfinder.pages.dev
  - API Docs: https://arbfinder.pages.dev/docs

Next Steps:
  1. Configure custom domain
  2. Set up CI/CD in GitHub Actions
  3. Review security settings
  4. Monitor logs and metrics

Configuration saved to: .cloudflare-config.json
```

---

## Verification

### Comprehensive Test Suite

```bash
# Run all verification tests
./scripts/cloudflare/verify_deployment.sh

# Tests include:
# ✅ Worker health check
# ✅ D1 database connectivity
# ✅ R2 upload/download
# ✅ Pages deployment
# ✅ API endpoints
# ✅ Security rules
# ✅ Performance benchmarks
```

### Manual Verification

**Worker**:
```bash
curl https://YOUR_WORKER_URL/api/health
# Expected: {"status":"ok"}
```

**D1 Database**:
```bash
curl https://YOUR_WORKER_URL/api/listings?limit=10
# Expected: {"listings":[...],"total":...}
```

**R2 Storage**:
```bash
# Upload test image
curl -X POST https://YOUR_WORKER_URL/api/upload/image \
  -F "file=@test.jpg"
# Expected: {"success":true,"url":"https://..."}
```

**Pages**:
```bash
curl https://YOUR_PAGES_URL
# Expected: HTML response with frontend
```

---

## Troubleshooting

### Common Issues

#### 1. Worker Deployment Fails

**Error**: `Authentication error`

**Solution**:
```bash
# Re-login to wrangler
wrangler logout
wrangler login

# Or set token manually
wrangler config set api_token="YOUR_TOKEN"
```

#### 2. D1 Database Not Found

**Error**: `Database not found`

**Solution**:
```bash
# List databases
wrangler d1 list

# Verify database ID in wrangler.toml matches
# If not, update wrangler.toml with correct ID
```

#### 3. R2 Bucket Access Denied

**Error**: `Access denied to R2 bucket`

**Solution**:
```bash
# Verify bucket exists
wrangler r2 bucket list

# Verify binding in wrangler.toml
# Redeploy worker
wrangler deploy
```

#### 4. Pages Build Fails

**Error**: `Build command failed`

**Solution**:
```bash
# Test build locally
cd frontend
npm install
npm run build

# Check build logs in Cloudflare dashboard
# Verify environment variables are set
```

#### 5. API Returns 500 Errors

**Solution**:
```bash
# Check worker logs
wrangler tail

# Look for error messages
# Common issues:
# - Missing environment variables
# - Database connection errors
# - R2 bucket not found
```

### Getting Help

1. **Cloudflare Community**: https://community.cloudflare.com/
2. **Discord**: https://discord.gg/cloudflaredev
3. **Documentation**: https://developers.cloudflare.com/
4. **GitHub Issues**: https://github.com/cbwinslow/arbfinder-suite/issues

---

## Cost Estimation

### Free Tier Limits

**Workers**:
- 100,000 requests/day
- 10ms CPU time per request
- FREE

**D1**:
- 5 GB storage
- 5 million rows read/day
- 100,000 rows written/day
- FREE (in beta)

**R2**:
- 10 GB storage/month
- 1 million Class A operations/month
- 10 million Class B operations/month
- FREE egress (no data transfer fees)

**Pages**:
- 500 builds/month
- Unlimited requests
- FREE

### Paid Plan (if needed)

**Workers Paid** ($5/month):
- 10 million requests/month included
- $0.50 per additional million requests

**R2 Paid**:
- $0.015 per GB/month storage
- Operations priced per million

**Estimated Monthly Cost** (with moderate traffic):
- Free tier: $0
- With 1M requests + 50GB storage: ~$5-10/month

---

## Next Steps

After completing this setup:

1. ✅ Configure custom domain
2. ✅ Set up CI/CD pipeline (see `.github/workflows/deployment.yml`)
3. ✅ Configure monitoring alerts
4. ✅ Set up backup strategy
5. ✅ Review security best practices
6. ✅ Load test your deployment
7. ✅ Set up staging environment

---

**Related Documentation**:
- [Workers Deployment](WORKERS_GUIDE.md)
- [D1 Database Guide](D1_GUIDE.md)
- [R2 Storage Guide](R2_GUIDE.md)
- [Security Best Practices](SECURITY.md)

**Last Updated**: 2025-12-15  
**Maintained By**: DevOps Team
