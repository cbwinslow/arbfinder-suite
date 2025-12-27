# Cloudflare Deployment Scripts

This directory contains automated scripts for deploying the ArbFinder Suite to Cloudflare's platform, including Pages, Workers, D1, R2, and KV.

## 📋 Overview

The deployment process consists of several stages:

1. **Infrastructure Setup** - Create D1 databases, R2 buckets, KV namespaces
2. **Worker Deployment** - Deploy the backend Worker
3. **Pages Deployment** - Build and deploy the Next.js frontend
4. **Service Binding** - Connect Workers to Pages
5. **Testing** - Verify all services are working

## 🚀 Quick Start

### Complete Deployment (Recommended)

Deploy everything in one command:

```bash
./scripts/cloudflare/deploy_complete.sh
```

This will:
- ✅ Check prerequisites
- ✅ Set up infrastructure (D1, R2, KV)
- ✅ Deploy Worker
- ✅ Build and deploy Pages
- ✅ Configure bindings
- ✅ Run verification tests

### Step-by-Step Deployment

If you prefer more control, run scripts individually:

```bash
# 1. Setup infrastructure
./scripts/cloudflare/setup.sh

# 2. Deploy Worker
cd cloudflare
wrangler deploy

# 3. Deploy Pages
./scripts/cloudflare/deploy_pages.sh

# 4. Bind Workers to Pages
./scripts/cloudflare/bind_workers.sh

# 5. Verify deployment
./scripts/cloudflare/verify_deployment.sh
```

## 📜 Script Reference

### `deploy_complete.sh`

**Complete orchestration script** - Handles end-to-end deployment.

```bash
./scripts/cloudflare/deploy_complete.sh [OPTIONS]

Options:
  --skip-setup      Skip infrastructure setup (D1, R2, KV)
  --skip-worker     Skip Worker deployment
  --skip-pages      Skip Pages deployment
  --skip-test       Skip testing and verification
  --project-name    Pages project name (default: arbfinder-suite)
  --worker-name     Worker name (default: arbfinder-worker)
  --help            Show help message
```

**Examples:**

```bash
# Deploy everything
./scripts/cloudflare/deploy_complete.sh

# Deploy only Worker and Pages (infrastructure already exists)
./scripts/cloudflare/deploy_complete.sh --skip-setup

# Deploy with custom project name
./scripts/cloudflare/deploy_complete.sh --project-name my-arbfinder

# Quick redeploy (skip tests)
./scripts/cloudflare/deploy_complete.sh --skip-setup --skip-test
```

### `setup.sh`

**Infrastructure setup script** - Creates D1, R2, KV resources.

```bash
./scripts/cloudflare/setup.sh
```

Creates:
- D1 database: `arbfinder-db`
- R2 buckets: `arbfinder-images`, `arbfinder-data`, `arbfinder-backups`
- KV namespaces: `CACHE`, `SESSIONS`, `ALERTS`

### `deploy_pages.sh`

**Pages deployment script** - Builds and deploys Next.js frontend.

```bash
./scripts/cloudflare/deploy_pages.sh [OPTIONS]

Options:
  --project-name NAME   Pages project name (default: arbfinder-suite)
  --branch BRANCH       Git branch to deploy (default: main)
```

**What it does:**
1. Updates Next.js config for static export
2. Installs dependencies
3. Builds frontend (`npm run build`)
4. Creates Pages project (if needed)
5. Deploys to Cloudflare Pages
6. Restores original Next.js config

**Examples:**

```bash
# Deploy to production
./scripts/cloudflare/deploy_pages.sh

# Deploy with custom project name
./scripts/cloudflare/deploy_pages.sh --project-name my-site

# Deploy from staging branch
./scripts/cloudflare/deploy_pages.sh --branch staging
```

### `bind_workers.sh`

**Worker binding script** - Connects Workers to Pages project.

```bash
./scripts/cloudflare/bind_workers.sh [OPTIONS]

Options:
  --project-name NAME   Pages project name
  --worker-name NAME    Worker name
```

**What it does:**
1. Checks Pages project exists
2. Verifies Worker is deployed
3. Creates Pages functions directory
4. Sets up service bindings
5. Generates wrangler.toml for Pages

**Example:**

```bash
./scripts/cloudflare/bind_workers.sh --project-name arbfinder-suite --worker-name arbfinder-worker
```

### `verify_deployment.sh`

**Verification script** - Tests deployed services.

```bash
./scripts/cloudflare/verify_deployment.sh [--config FILE]
```

**Tests performed:**
- ✅ Worker health endpoint
- ✅ Worker CORS configuration
- ✅ Pages accessibility
- ✅ Pages HTML structure
- ✅ D1 database exists
- ✅ R2 buckets exist
- ✅ KV namespaces exist
- ✅ Worker deployment status
- ✅ Pages project status
- ✅ Response time performance

**Example output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 Verification Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Results:
  Total Tests: 10
  ✓ Passed: 8
  ✗ Failed: 0
  ⚠ Warnings: 2

Success Rate: 80%

✓ All critical tests passed! ✨
```

### `setup_cloudflare.py`

**Python orchestration script** - Alternative to bash scripts with more features.

```bash
# Install dependencies
pip install requests rich

# Run setup
python scripts/cloudflare/setup_cloudflare.py --interactive

# Or with API key
python scripts/cloudflare/setup_cloudflare.py \
  --api-key YOUR_API_KEY \
  --account-id YOUR_ACCOUNT_ID
```

## 🔧 Prerequisites

### Required Tools

1. **Node.js 18+** and npm
   ```bash
   node --version  # Should be v18 or higher
   npm --version
   ```

2. **Wrangler CLI**
   ```bash
   npm install -g wrangler@latest
   wrangler --version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **curl** (for testing)
   ```bash
   curl --version
   ```

5. **jq** (optional, for JSON parsing)
   ```bash
   jq --version
   ```

### Cloudflare Setup

1. **Cloudflare Account**
   - Sign up at https://dash.cloudflare.com/sign-up
   - Verify your email

2. **API Token**
   - Go to https://dash.cloudflare.com/profile/api-tokens
   - Click "Create Token"
   - Use "Edit Cloudflare Workers" template
   - Add permissions for:
     - Workers KV Storage (Edit)
     - Workers R2 Storage (Edit)
     - D1 (Edit)
     - Pages (Edit)

3. **Authentication**
   ```bash
   # Option 1: Interactive login
   wrangler login

   # Option 2: Set environment variable
   export CLOUDFLARE_API_TOKEN=your_token_here
   export CLOUDFLARE_ACCOUNT_ID=your_account_id_here
   ```

## 📝 Configuration

### Environment Variables

Set these in your shell or `.env` file:

```bash
# Required
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id

# Optional
PROJECT_NAME=arbfinder-suite
WORKER_NAME=arbfinder-worker
```

### Configuration File

Deployment details are saved to `.cloudflare-config.json`:

```json
{
  "worker_url": "https://arbfinder-worker.yourdomain.workers.dev",
  "worker_name": "arbfinder-worker",
  "pages_url": "https://arbfinder-suite.pages.dev",
  "pages_project": "arbfinder-suite",
  "d1_database_id": "your-database-id"
}
```

### Pages Environment Variables

Set these in Cloudflare Dashboard after deployment:

1. Go to https://dash.cloudflare.com/pages
2. Select your project
3. Go to Settings > Environment variables
4. Add for **Production** and **Preview**:

```
NEXT_PUBLIC_API_BASE=https://your-worker.workers.dev
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX (optional)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Failed

```bash
# Error: Not authenticated with Cloudflare
Solution: Run wrangler login
```

#### 2. Node Version Too Old

```bash
# Error: Node.js version must be 18 or higher
Solution: Update Node.js
  - Use nvm: nvm install 18 && nvm use 18
  - Or download from https://nodejs.org
```

#### 3. Wrangler Not Found

```bash
# Error: wrangler command not found
Solution: npm install -g wrangler@latest
```

#### 4. Build Failed

```bash
# Error: Frontend build failed
Solution: 
  cd frontend
  rm -rf node_modules .next out
  npm install
  npm run build
```

#### 5. Database Already Exists

```bash
# Warning: D1 database may already exist
This is OK - the script will use the existing database
```

#### 6. Pages Deployment Failed

```bash
# Error: Pages deployment failed
Solutions:
  1. Check if 'out' directory was created
  2. Verify Next.js config is correct
  3. Check wrangler authentication
  4. Try manual deployment:
     cd frontend
     npm run build
     wrangler pages deploy out --project-name=arbfinder-suite
```

### Debug Commands

```bash
# Check Wrangler auth
wrangler whoami

# List Workers
wrangler deployments list

# List Pages projects
wrangler pages project list

# List D1 databases
wrangler d1 list

# List R2 buckets
wrangler r2 bucket list

# List KV namespaces
wrangler kv:namespace list

# View Worker logs
wrangler tail --name arbfinder-worker

# View Pages logs
wrangler pages deployment tail --project-name arbfinder-suite
```

## 📊 Monitoring

### View Real-Time Logs

```bash
# Worker logs
wrangler tail --name arbfinder-worker

# Pages logs
wrangler pages deployment tail --project-name arbfinder-suite

# With filters
wrangler tail --name arbfinder-worker --format pretty --status error
```

### Check Deployment Status

```bash
# Worker deployment info
wrangler deployments list

# Pages deployment info
wrangler pages deployment list --project-name arbfinder-suite
```

### Analytics

- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **Workers Analytics**: Dashboard > Workers & Pages > Select worker > Metrics
- **Pages Analytics**: Dashboard > Pages > Select project > Analytics

## 🔄 Redeployment

### Redeploy Everything

```bash
./scripts/cloudflare/deploy_complete.sh --skip-setup
```

### Redeploy Worker Only

```bash
cd cloudflare
wrangler deploy
```

### Redeploy Pages Only

```bash
./scripts/cloudflare/deploy_pages.sh
```

### Update Infrastructure Only

```bash
./scripts/cloudflare/setup.sh
```

## 🧹 Cleanup

To remove all Cloudflare resources:

```bash
# Delete Pages project
wrangler pages project delete arbfinder-suite

# Delete Worker
wrangler delete arbfinder-worker

# Delete D1 database
wrangler d1 delete arbfinder-db

# Delete R2 buckets
wrangler r2 bucket delete arbfinder-images
wrangler r2 bucket delete arbfinder-data
wrangler r2 bucket delete arbfinder-backups

# Delete KV namespaces
wrangler kv:namespace delete --namespace-id <ID>
```

## 📚 Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [ArbFinder Suite Documentation](../../docs/platform/CLOUDFLARE_SETUP.md)

## 💡 Tips

1. **Use `--skip-setup`** for faster redeployments after initial setup
2. **Test locally first** with `wrangler dev` before deploying
3. **Monitor logs** during first deployment to catch issues early
4. **Set environment variables** via dashboard for security
5. **Use preview environments** for testing before production
6. **Enable Logpush** for production monitoring (paid plan)
7. **Configure WAF rules** for additional security
8. **Set up custom domain** for professional URLs

## 🤝 Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review logs with `wrangler tail`
3. Run verification: `./scripts/cloudflare/verify_deployment.sh`
4. Check [GitHub issues](https://github.com/cbwinslow/arbfinder-suite/issues)
5. Consult [Cloudflare documentation](https://developers.cloudflare.com/)

---

**Last Updated**: 2025-12-27  
**Maintainer**: [@cbwinslow](https://github.com/cbwinslow)
