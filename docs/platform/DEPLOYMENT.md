# Deployment Guide

This guide walks through deploying ArbFinder Suite to Cloudflare.

## Prerequisites

1. **Cloudflare Account**: Sign up at https://dash.cloudflare.com
2. **Wrangler CLI**: Install with `npm install -g wrangler`
3. **Node.js 18+**: Required for building the project
4. **Python 3.9+**: Required for backend API

## Quick Deploy

### 1. Authenticate with Wrangler

```bash
wrangler login
```

### 2. Create Cloudflare Resources

#### Create D1 Database

```bash
# Production database
wrangler d1 create arbfinder-db-production

# Note the database_id from output and update cloudflare/wrangler.toml
```

#### Apply Database Schema

```bash
cd database
wrangler d1 execute arbfinder-db-production --file=schemas/d1_schema.sql
```

#### Create R2 Buckets

```bash
wrangler r2 bucket create arbfinder-images-production
wrangler r2 bucket create arbfinder-data-production
wrangler r2 bucket create arbfinder-backups-production
```

#### Create KV Namespaces

```bash
wrangler kv:namespace create "CACHE"
wrangler kv:namespace create "SESSIONS"
wrangler kv:namespace create "ALERTS"

# Note the namespace IDs and update cloudflare/wrangler.toml
```

#### Create Queues

```bash
wrangler queues create arbfinder-snipe-queue
wrangler queues create arbfinder-alert-queue
wrangler queues create arbfinder-crawler-queue
```

### 3. Configure Secrets

```bash
cd cloudflare

# Set API keys
wrangler secret put OPENROUTER_API_KEY
wrangler secret put EBAY_APP_ID
wrangler secret put STRIPE_SECRET_KEY

# Set email service credentials (if using)
wrangler secret put SENDGRID_API_KEY
```

### 4. Update Configuration

Edit `cloudflare/wrangler.toml`:

1. Replace `your-d1-database-id` with actual D1 database ID
2. Replace `your-kv-namespace-id` with actual KV namespace IDs
3. Replace `your-hyperdrive-config-id` if using Hyperdrive
4. Update `GOOGLE_TAG_MANAGER_ID` with your GTM container ID

### 5. Deploy Worker

```bash
cd cloudflare
npm install
npm run build
wrangler deploy --env production
```

### 6. Deploy Frontend to Cloudflare Pages

#### Via GitHub Integration (Recommended)

1. Go to https://dash.cloudflare.com/pages
2. Click "Create a project"
3. Connect to GitHub and select `arbfinder-suite` repository
4. Configure build settings:
   - **Framework preset**: Next.js
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Build output directory**: `frontend/.next`
   - **Root directory**: `/`
   - **Node version**: 18

5. Set environment variables:
   - `NEXT_PUBLIC_API_BASE`: https://api.arbfinder.com
   - `NEXT_PUBLIC_GTM_ID`: Your Google Tag Manager ID
   - `NODE_VERSION`: 18

6. Click "Save and Deploy"

#### Via Wrangler CLI

```bash
cd frontend
npm install
npm run build

npx wrangler pages deploy .next \
  --project-name arbfinder-frontend \
  --branch main
```

### 7. Set Up Custom Domains

#### Worker Domain

```bash
# Option 1: Via Dashboard
# Go to Workers > arbfinder-worker > Triggers > Custom Domains
# Add: api.arbfinder.com

# Option 2: Via CLI
wrangler domains add api.arbfinder.com
```

#### Pages Domain

```bash
# Go to Pages > arbfinder-frontend > Custom domains
# Add: arbfinder.com or www.arbfinder.com
```

### 8. Configure DNS

In your Cloudflare DNS settings:

1. Add CNAME record: `api` -> `arbfinder-worker-production.workers.dev`
2. Add CNAME record: `@` -> `arbfinder-frontend.pages.dev`
3. Add CNAME record: `www` -> `arbfinder-frontend.pages.dev`

## Backend API Deployment

The backend API can be deployed separately to:

### Option 1: Cloudflare Workers (Recommended)

The Worker handles static content and proxies to backend API.

### Option 2: Traditional Server

Deploy the FastAPI backend to a server:

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run with uvicorn
uvicorn backend.api.main:app --host 0.0.0.0 --port 8080
```

### Option 3: Docker

```bash
docker-compose up -d
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Test Worker
curl https://api.arbfinder.com/api/health

# Test Pages
curl https://arbfinder.com
```

### 2. Monitor Performance

- Dashboard > Workers > Analytics
- Dashboard > Pages > Analytics
- Set up alerts for errors

### 3. Configure Monitoring

Enable Cloudflare Logpush for detailed logs:

```bash
# Create Logpush job
wrangler logpush create \
  --name arbfinder-logs \
  --destination r2://arbfinder-backups/logs \
  --dataset workers_trace_events
```

### 4. Set Up Cron Jobs

The cron triggers are configured in `wrangler.toml`. Verify they're working:

1. Go to Workers > arbfinder-worker > Triggers
2. Check Cron Triggers section
3. View recent executions

## Troubleshooting

### Worker Errors

View real-time logs:

```bash
wrangler tail --env production
```

### Database Issues

Check D1 database:

```bash
wrangler d1 execute arbfinder-db-production --command="SELECT COUNT(*) FROM listings"
```

### Queue Issues

Check queue status:

```bash
wrangler queues list
wrangler queues producer send arbfinder-snipe-queue --message='{"test": true}'
```

### Pages Build Failures

1. Check build logs in Cloudflare Dashboard
2. Verify Node version is set correctly
3. Check environment variables
4. Review build command

## Continuous Deployment

### GitHub Actions

The repository includes GitHub Actions workflows for:

- Automated Worker deployment on push to main
- Automated Pages deployment (via Cloudflare Pages integration)
- Running tests before deployment

See `.github/workflows/deployment.yml` for details.

## Rollback

### Worker Rollback

```bash
# List deployments
wrangler deployments list

# Rollback to previous version
wrangler rollback --message "Rolling back due to issue"
```

### Pages Rollback

1. Go to Pages > arbfinder-frontend > Deployments
2. Find previous working deployment
3. Click "Rollback to this deployment"

## Security

### Enable WAF

1. Go to Security > WAF
2. Enable "OWASP ModSecurity Core Rule Set"
3. Add custom rules for rate limiting

### Configure Firewall Rules

1. Go to Security > Firewall Rules
2. Add rate limiting rules
3. Configure geographic restrictions if needed

### Secrets Management

- Never commit secrets to git
- Use `wrangler secret put` for sensitive values
- Rotate secrets regularly

## Cost Optimization

### Free Tier Limits

- Workers: 100,000 requests/day
- Pages: 500 builds/month
- D1: 5GB storage, 5M reads/day
- R2: 10GB storage
- KV: 100,000 reads/day

### Optimization Tips

1. Enable caching for static assets
2. Use KV for frequently accessed data
3. Optimize image sizes before R2 upload
4. Use Hyperdrive for database connection pooling

## Support

For issues or questions:

- GitHub Issues: https://github.com/cbwinslow/arbfinder-suite/issues
- Cloudflare Docs: https://developers.cloudflare.com
- Discord: Join the Cloudflare Discord community

---

**Last Updated**: 2024-12-17  
**Version**: 2.1
