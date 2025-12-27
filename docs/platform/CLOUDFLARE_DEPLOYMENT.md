# Complete Cloudflare Deployment Guide

This guide provides comprehensive instructions for deploying the ArbFinder Suite to Cloudflare's platform.

## 📚 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
- [Manual Deployment](#manual-deployment)
- [Automated Deployment with GitHub Actions](#automated-deployment-with-github-actions)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## 🌟 Overview

The ArbFinder Suite deployment on Cloudflare consists of:

### Frontend (Cloudflare Pages)
- **Technology**: Next.js static site
- **Hosting**: Cloudflare Pages
- **URL**: `https://arbfinder-suite.pages.dev`
- **Features**: Dashboard, alerts, comparisons, snipe scheduler, AI crews

### Backend (Cloudflare Worker)
- **Technology**: Cloudflare Worker (TypeScript)
- **URL**: `https://arbfinder-worker.workers.dev`
- **Features**: REST API, image handling, scheduled tasks, queues

### Infrastructure
- **Database**: D1 (SQLite-based edge database)
- **Storage**: R2 buckets (images, data, backups)
- **Cache**: KV namespaces (CACHE, SESSIONS, ALERTS)
- **Queues**: Snipe, Alert, and Crawler queues
- **Durable Objects**: Crawler state, snipe scheduler

## 🔧 Prerequisites

### 1. Cloudflare Account

Sign up for a free account:
- Go to https://dash.cloudflare.com/sign-up
- Verify your email address
- Note your Account ID (found in Dashboard)

### 2. Development Tools

Install required tools:

```bash
# Node.js 18+ and npm
node --version  # Should be v18 or higher
npm --version

# Wrangler CLI
npm install -g wrangler@latest
wrangler --version

# Git
git --version

# curl (for testing)
curl --version

# jq (optional, for JSON parsing)
jq --version
```

### 3. API Token

Create a Cloudflare API token with permissions:

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use "Edit Cloudflare Workers" template
4. Add these permissions:
   - Account > Workers R2 Storage > Edit
   - Account > Workers KV Storage > Edit
   - Account > D1 > Edit
   - Account > Cloudflare Pages > Edit
5. Click "Continue to summary" → "Create Token"
6. **Save the token securely** (shown only once)

### 4. Authentication

Authenticate with Cloudflare:

```bash
# Option 1: Interactive login (recommended)
wrangler login

# Option 2: Use API token
export CLOUDFLARE_API_TOKEN=your_token_here
export CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

## 🚀 Deployment Methods

### Method 1: One-Command Deployment (Recommended)

```bash
./scripts/cloudflare/deploy_complete.sh
```

This automated script will:
1. ✅ Check all prerequisites
2. ✅ Set up infrastructure (D1, R2, KV)
3. ✅ Deploy Worker backend
4. ✅ Build and deploy Pages frontend
5. ✅ Configure service bindings
6. ✅ Run verification tests

**Estimated time**: 5-10 minutes

### Method 2: Step-by-Step Deployment

For more control over the deployment process:

```bash
# Step 1: Setup infrastructure
./scripts/cloudflare/setup.sh

# Step 2: Deploy Worker
cd cloudflare
npm install
wrangler deploy
cd ..

# Step 3: Deploy Pages
./scripts/cloudflare/deploy_pages.sh

# Step 4: Bind Workers to Pages
./scripts/cloudflare/bind_workers.sh

# Step 5: Verify deployment
./scripts/cloudflare/verify_deployment.sh
```

### Method 3: GitHub Actions (CI/CD)

Automated deployment on every push to main/staging:

1. **Set GitHub Secrets**:
   - Go to your repo: Settings > Secrets and variables > Actions
   - Add secrets:
     - `CLOUDFLARE_API_TOKEN`
     - `CLOUDFLARE_ACCOUNT_ID`

2. **Enable Workflow**:
   - The workflow file is at `.github/workflows/cloudflare-deploy.yml`
   - It will trigger automatically on push to main/staging
   - Or manually via Actions tab

3. **Monitor Deployment**:
   - Go to Actions tab in GitHub
   - Click on the running workflow
   - View logs and deployment status

## 📖 Manual Deployment

If you prefer manual control, follow these detailed steps:

### Step 1: Create D1 Database

```bash
cd cloudflare

# Create database
wrangler d1 create arbfinder-db

# Note the database ID from output
# Update wrangler.toml with the database ID

# Apply schema (if you have one)
wrangler d1 execute arbfinder-db --file=../database/cloudflare_schema.sql
```

### Step 2: Create R2 Buckets

```bash
# Create buckets
wrangler r2 bucket create arbfinder-images
wrangler r2 bucket create arbfinder-data
wrangler r2 bucket create arbfinder-backups
```

### Step 3: Create KV Namespaces

```bash
# Create namespaces
wrangler kv:namespace create CACHE
wrangler kv:namespace create SESSIONS
wrangler kv:namespace create ALERTS

# Note the namespace IDs from output
# Update wrangler.toml with the namespace IDs
```

### Step 4: Deploy Worker

```bash
cd cloudflare

# Install dependencies
npm install

# Deploy
wrangler deploy

# Note the Worker URL from output
```

### Step 5: Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Update Next.js config for static export
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

module.exports = nextConfig;
EOF

# Build
npm run build

# Verify 'out' directory was created
ls -la out/
```

### Step 6: Deploy to Pages

```bash
cd frontend

# Create Pages project (first time only)
wrangler pages project create arbfinder-suite

# Deploy
wrangler pages deploy out --project-name=arbfinder-suite --branch=main

# Note the Pages URL from output
```

### Step 7: Configure Environment Variables

Set environment variables for Pages:

1. Go to https://dash.cloudflare.com/pages
2. Select `arbfinder-suite` project
3. Go to Settings > Environment variables
4. Add variables for **Production**:
   - `NEXT_PUBLIC_API_BASE`: Your Worker URL
   - `NEXT_PUBLIC_GTM_ID`: (Optional) Your GTM ID
5. Add same variables for **Preview**

### Step 8: Redeploy Pages

After setting environment variables:

```bash
cd frontend
wrangler pages deploy out --project-name=arbfinder-suite --branch=main
```

## ⚙️ Configuration

### Worker Configuration (wrangler.toml)

The Worker configuration is in `cloudflare/wrangler.toml`:

```toml
name = "arbfinder-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# Update these with your actual IDs
[[d1_databases]]
binding = "DB"
database_name = "arbfinder-db"
database_id = "YOUR_DATABASE_ID"

[[r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images"

[[kv_namespaces]]
binding = "CACHE"
id = "YOUR_KV_NAMESPACE_ID"

# Add more configurations as needed
```

### Pages Configuration

Create `frontend/wrangler.toml` for Pages Functions:

```toml
name = "arbfinder-suite"
compatibility_date = "2024-01-01"
pages_build_output_dir = "out"

[[service_bindings]]
binding = "WORKER"
service = "arbfinder-worker"
environment = "production"
```

### Environment Variables

**For Pages** (Set in Cloudflare Dashboard):
- `NEXT_PUBLIC_API_BASE`: Worker URL
- `NEXT_PUBLIC_GTM_ID`: Google Tag Manager ID (optional)

**For Worker** (Set in wrangler.toml):
```toml
[vars]
API_BASE_URL = "https://api.arbfinder.com"
ENVIRONMENT = "production"
GOOGLE_TAG_MANAGER_ID = "GTM-XXXXXXX"
```

## 🧪 Testing

### Automated Testing

Run the verification script:

```bash
./scripts/cloudflare/verify_deployment.sh
```

This will test:
- Worker health endpoint
- Worker CORS configuration
- Pages accessibility
- Database connectivity
- Storage buckets
- KV namespaces
- Response times

### Manual Testing

**Test Worker**:
```bash
# Health check
curl https://arbfinder-worker.your-domain.workers.dev/api/health

# Expected response:
# {"status":"ok","timestamp":1234567890}
```

**Test Pages**:
```bash
# Check if site is accessible
curl -I https://arbfinder-suite.pages.dev

# Expected response:
# HTTP/2 200
```

**Test Integration**:
```bash
# Test API call from frontend
# Open browser console on your Pages site
fetch('/api/health').then(r => r.json()).then(console.log)
```

### Monitoring

**View Real-Time Logs**:
```bash
# Worker logs
wrangler tail --name arbfinder-worker

# Pages logs
wrangler pages deployment tail --project-name arbfinder-suite
```

**Analytics**:
- Worker Analytics: https://dash.cloudflare.com > Workers & Pages > arbfinder-worker > Metrics
- Pages Analytics: https://dash.cloudflare.com > Pages > arbfinder-suite > Analytics

## 🔧 Troubleshooting

### Common Issues

#### Issue: Wrangler Not Authenticated
```bash
# Solution
wrangler login
# or
wrangler whoami
```

#### Issue: Build Failed
```bash
# Solution
cd frontend
rm -rf node_modules .next out
npm install
npm run build
```

#### Issue: Worker Deploy Failed
```bash
# Check wrangler.toml configuration
# Ensure all IDs are correct
# Try deploying with verbose flag
cd cloudflare
wrangler deploy --verbose
```

#### Issue: Pages Showing 404
```bash
# Ensure 'out' directory exists
ls -la frontend/out/

# Check Next.js config has output: 'export'
cat frontend/next.config.js

# Rebuild and redeploy
cd frontend
npm run build
wrangler pages deploy out --project-name=arbfinder-suite
```

#### Issue: Environment Variables Not Working
- Verify variables are set in both Production and Preview
- Redeploy after setting variables
- Check variable names match (NEXT_PUBLIC_ prefix for frontend)

### Debug Commands

```bash
# Check Wrangler auth
wrangler whoami

# List all Workers
wrangler deployments list

# List all Pages projects
wrangler pages project list

# List D1 databases
wrangler d1 list

# List R2 buckets
wrangler r2 bucket list

# List KV namespaces
wrangler kv:namespace list

# View detailed Worker info
cd cloudflare
wrangler deployments view

# View Pages deployment history
wrangler pages deployment list --project-name=arbfinder-suite
```

## 🔄 Maintenance

### Update Deployment

**Quick Update** (after code changes):
```bash
# Redeploy Worker
cd cloudflare
wrangler deploy

# Redeploy Pages
cd frontend
npm run build
wrangler pages deploy out --project-name=arbfinder-suite
```

**Or use the automated script**:
```bash
./scripts/cloudflare/deploy_complete.sh --skip-setup --skip-test
```

### Rollback

**Rollback Worker**:
```bash
cd cloudflare
wrangler rollback
```

**Rollback Pages**:
- Go to Cloudflare Dashboard > Pages > arbfinder-suite
- Click on Deployments
- Find the previous good deployment
- Click "..." > "Rollback to this deployment"

### Database Migrations

```bash
# Create migration
wrangler d1 migrations create arbfinder-db migration_name

# Apply migration
wrangler d1 migrations apply arbfinder-db
```

### Backup

**Backup D1 Database**:
```bash
wrangler d1 export arbfinder-db --output=backup.sql
```

**Backup R2 Data**:
```bash
# List objects
wrangler r2 object list arbfinder-data

# Download object
wrangler r2 object get arbfinder-data/path/to/file
```

### Monitoring and Alerts

Set up monitoring in Cloudflare Dashboard:
1. Go to Notifications
2. Create alerts for:
   - Worker errors
   - High response times
   - Storage quota warnings
   - Database errors

## 📊 Performance Optimization

### Enable Caching

Add caching headers in your Worker:
```typescript
return new Response(data, {
  headers: {
    'Cache-Control': 'public, max-age=3600',
    'CDN-Cache-Control': 'max-age=86400'
  }
});
```

### Optimize Images

Use Cloudflare Image Resizing for R2 images:
- Enable in Dashboard > Images > Image Resizing
- Use URLs like: `https://your-domain.com/cdn-cgi/image/width=800/image.jpg`

### Enable WAF

Configure Web Application Firewall:
1. Go to Security > WAF
2. Enable Managed Rules
3. Configure Rate Limiting
4. Set up Bot Fight Mode

## 🔐 Security

### Best Practices

1. **API Tokens**: Use scoped tokens with minimal permissions
2. **Environment Variables**: Never commit secrets to git
3. **CORS**: Configure appropriate CORS headers
4. **Rate Limiting**: Enable rate limiting on Worker
5. **Input Validation**: Validate all user inputs
6. **HTTPS**: Always use HTTPS (automatic with Cloudflare)

### Security Headers

Add security headers in your Worker:
```typescript
const headers = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin'
};
```

## 📚 Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [D1 Database Guide](https://developers.cloudflare.com/d1/)
- [R2 Storage Guide](https://developers.cloudflare.com/r2/)
- [Deployment Scripts README](../../scripts/cloudflare/README.md)
- [Quick Start Guide](../../scripts/cloudflare/QUICKSTART.md)

## 💬 Support

Need help?
- **GitHub Issues**: https://github.com/cbwinslow/arbfinder-suite/issues
- **Cloudflare Community**: https://community.cloudflare.com/
- **Documentation**: Review docs in `/docs` directory

---

**Last Updated**: 2025-12-27  
**Version**: 2.0  
**Maintainer**: [@cbwinslow](https://github.com/cbwinslow)
