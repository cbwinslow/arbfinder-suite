# AI Agent Tasks for Cloudflare Deployment

## Overview
This document provides detailed, actionable tasks that can be executed by AI agents to complete the Cloudflare Pages deployment setup.

---

## Task Template

```yaml
Task ID: AGENT-XXX
Title: [Short descriptive title]
Priority: [P0/P1/P2/P3]
Estimated Time: [X hours/minutes]
Dependencies: [List of task IDs this depends on]
Agent Type: [DevOps/Frontend/Backend/Security]
Status: [Not Started/In Progress/Completed/Blocked]
```

---

## 🔴 P0: Critical Deployment Blockers

### AGENT-001: Configure GitHub Secrets
**Priority**: P0 - Blocking  
**Estimated Time**: 15 minutes  
**Dependencies**: None  
**Agent Type**: DevOps  
**Status**: Not Started

#### Context
The GitHub Actions workflow requires Cloudflare credentials to deploy. These must be added as repository secrets.

#### Prerequisites
- Cloudflare account access
- GitHub repository admin access
- Cloudflare API token with Workers and Pages permissions

#### Detailed Steps
1. **Create Cloudflare API Token**
   - Navigate to: https://dash.cloudflare.com/profile/api-tokens
   - Click "Create Token"
   - Use template: "Edit Cloudflare Workers"
   - Add additional permissions:
     - Account → Cloudflare Pages → Edit
     - Account → Account Settings → Read
   - Set token name: `arbfinder-github-actions`
   - Click "Continue to summary"
   - Click "Create Token"
   - **IMPORTANT**: Copy token immediately (won't be shown again)

2. **Get Cloudflare Account ID**
   - Navigate to: https://dash.cloudflare.com
   - Select any website or go to Workers & Pages
   - Copy Account ID from right sidebar

3. **Add Secrets to GitHub**
   ```bash
   # Using GitHub CLI
   gh secret set CLOUDFLARE_API_TOKEN --body "your-token-here"
   gh secret set CLOUDFLARE_ACCOUNT_ID --body "your-account-id-here"
   ```
   
   OR via Web UI:
   - Go to repository Settings
   - Navigate to: Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CLOUDFLARE_API_TOKEN`
   - Value: [paste token]
   - Click "Add secret"
   - Repeat for `CLOUDFLARE_ACCOUNT_ID`

#### Verification
```bash
# List secrets (won't show values)
gh secret list

# Should output:
# CLOUDFLARE_API_TOKEN  Updated 2025-XX-XX
# CLOUDFLARE_ACCOUNT_ID Updated 2025-XX-XX

# Test workflow can access secrets (will only work in Actions)
# Trigger workflow manually: Actions → Deploy to Cloudflare → Run workflow
```

#### Acceptance Criteria
- [ ] CLOUDFLARE_API_TOKEN secret exists
- [ ] CLOUDFLARE_ACCOUNT_ID secret exists
- [ ] Workflow run shows no "secret not found" errors
- [ ] Token has required permissions
- [ ] Token hasn't expired

#### Rollback Plan
```bash
# Delete secrets if needed
gh secret delete CLOUDFLARE_API_TOKEN
gh secret delete CLOUDFLARE_ACCOUNT_ID

# Revoke token in Cloudflare Dashboard
# Navigate to API Tokens → Click token → Revoke
```

---

### AGENT-002: Update Workflow Domain Configuration
**Priority**: P0 - Blocking  
**Estimated Time**: 10 minutes  
**Dependencies**: None  
**Agent Type**: DevOps  
**Status**: Not Started

#### Context
The workflow file contains placeholder domain names that must be replaced with actual Cloudflare Worker URLs.

#### Prerequisites
- Access to Cloudflare Dashboard
- Worker deployed (or at least subdomain reserved)

#### Detailed Steps

1. **Determine Worker URLs**
   ```bash
   # After deploying worker once, get URL from output
   cd cloudflare
   npx wrangler deploy --dry-run
   
   # Or check Cloudflare Dashboard:
   # Workers & Pages → Overview → Your workers
   ```

2. **Update Workflow File**
   Edit `.github/workflows/cloudflare-deploy.yml`:
   
   Find and replace all instances of:
   ```yaml
   # OLD (line ~70)
   echo "url=https://arbfinder-worker.your-domain.workers.dev" >> $GITHUB_OUTPUT
   
   # NEW
   echo "url=https://arbfinder-worker-production.[your-subdomain].workers.dev" >> $GITHUB_OUTPUT
   ```
   
   Update all occurrences (typically 4-6 places):
   - Worker URL in get-worker-url step (line ~71)
   - Worker URL in get-worker-url step for staging (line ~73)
   - API_BASE_URL in set-api-base-url step (line ~136)
   - Worker URL in verify-deployment health check (line ~210, ~212)

3. **Commit Changes**
   ```bash
   git add .github/workflows/cloudflare-deploy.yml
   git commit -m "Configure actual Cloudflare Worker URLs"
   git push
   ```

#### Verification
```bash
# Check workflow file for placeholders
grep -n "your-domain" .github/workflows/cloudflare-deploy.yml
# Should return: (no matches)

# Validate YAML syntax
yamllint .github/workflows/cloudflare-deploy.yml

# Test workflow
git push origin main
# Monitor: Actions → Deploy to Cloudflare
```

#### Acceptance Criteria
- [ ] No "your-domain" placeholders remain
- [ ] URLs match actual Worker deployment
- [ ] URLs are consistent across all references
- [ ] Workflow syntax is valid
- [ ] Health checks use correct endpoints

#### Common Issues
- **Issue**: Worker URL not known yet
  - **Solution**: Deploy worker once to get URL, then update workflow
- **Issue**: Different URLs for production/staging
  - **Solution**: Use environment-specific logic in workflow (already present)

---

### AGENT-003: Fix Next.js Security Vulnerability
**Priority**: P0 - Security  
**Estimated Time**: 15 minutes  
**Dependencies**: None  
**Agent Type**: Frontend/Security  
**Status**: Not Started

#### Context
Next.js 14.2.32 has a known security vulnerability. Must update to latest patched version.

Reference: https://nextjs.org/blog/security-update-2025-12-11

#### Prerequisites
- Node.js 18+
- npm with write access to frontend/package.json

#### Detailed Steps

1. **Check Current Version**
   ```bash
   cd frontend
   npm list next
   # Output: next@14.2.32
   ```

2. **Update Next.js**
   ```bash
   cd frontend
   npm install next@latest
   ```

3. **Verify Compatibility**
   ```bash
   # Check for breaking changes
   npm run build
   
   # If build fails, check changelog
   # https://github.com/vercel/next.js/releases
   
   # If needed, update other dependencies
   npm update react react-dom
   ```

4. **Run Tests**
   ```bash
   # If tests exist
   npm test
   
   # Manual verification
   npm run dev
   # Open http://localhost:3000
   # Check all pages work
   ```

5. **Update package-lock.json**
   ```bash
   npm install  # Regenerate lock file
   ```

6. **Commit Changes**
   ```bash
   git add frontend/package.json frontend/package-lock.json
   git commit -m "Update Next.js to fix security vulnerability"
   git push
   ```

#### Verification
```bash
# Check updated version
cd frontend
npm list next
# Output should be >= 14.2.33

# Run security audit
npm audit
# Should show 0 high vulnerabilities

# Verify build works
npm run build
ls -la out/  # Should exist with files
```

#### Acceptance Criteria
- [ ] Next.js version >= 14.2.33 (or latest stable)
- [ ] No high/critical vulnerabilities in npm audit
- [ ] Build succeeds without errors
- [ ] All pages render correctly
- [ ] No breaking changes introduced

#### Rollback Plan
```bash
# If update causes issues
cd frontend
npm install next@14.2.32
npm install  # Restore lock file
```

#### Additional Security Checks
```bash
# Check all vulnerabilities
npm audit --audit-level=moderate

# Fix automatically if possible
npm audit fix

# For vulnerabilities that can't be auto-fixed
npm audit fix --force  # Use with caution
```

---

## 🟠 P1: High Priority Tasks

### AGENT-004: Implement Worker Health Check Endpoint
**Priority**: P1 - Monitoring  
**Estimated Time**: 45 minutes  
**Dependencies**: AGENT-001 (secrets)  
**Agent Type**: Backend  
**Status**: Not Started

#### Context
The deployment verification workflow expects a `/api/health` endpoint on the Worker. This must be implemented for monitoring and deployment verification.

#### Prerequisites
- TypeScript knowledge
- Wrangler CLI installed
- Cloudflare account with Worker deployed

#### Detailed Steps

1. **Locate Worker Entry Point**
   ```bash
   cd cloudflare
   cat src/index.ts  # Main entry point
   ```

2. **Implement Health Check Route**
   
   Create or update `cloudflare/src/health.ts`:
   ```typescript
   export interface HealthResponse {
     status: 'healthy' | 'degraded' | 'unhealthy';
     timestamp: string;
     version: string;
     environment: string;
     services?: {
       d1?: boolean;
       kv?: boolean;
       r2?: boolean;
     };
   }
   
   export async function handleHealth(
     env: Env,
     ctx: ExecutionContext
   ): Promise<Response> {
     const startTime = Date.now();
     
     // Basic health check
     const health: HealthResponse = {
       status: 'healthy',
       timestamp: new Date().toISOString(),
       version: '0.4.0',
       environment: env.ENVIRONMENT || 'production',
     };
     
     // Optional: Check service connectivity
     try {
       if (env.DB) {
         const dbCheck = await env.DB.prepare('SELECT 1 as test').first();
         health.services = { ...health.services, d1: !!dbCheck };
       }
       if (env.CACHE) {
         await env.CACHE.put('health_check', Date.now().toString(), { expirationTtl: 60 });
         const cacheCheck = await env.CACHE.get('health_check');
         health.services = { ...health.services, kv: !!cacheCheck };
       }
     } catch (error) {
       console.error('Service check failed:', error);
       health.status = 'degraded';
     }
     
     const responseTime = Date.now() - startTime;
     
     return new Response(JSON.stringify(health), {
       status: health.status === 'healthy' ? 200 : 503,
       headers: {
         'Content-Type': 'application/json',
         'Cache-Control': 'no-cache',
         'X-Response-Time': `${responseTime}ms`,
       },
     });
   }
   ```

3. **Update Main Router**
   
   Edit `cloudflare/src/index.ts`:
   ```typescript
   import { handleHealth } from './health';
   
   export default {
     async fetch(
       request: Request,
       env: Env,
       ctx: ExecutionContext
     ): Promise<Response> {
       const url = new URL(request.url);
       
       // Health check endpoint
       if (url.pathname === '/api/health') {
         return handleHealth(env, ctx);
       }
       
       // ... rest of your routes
       
       return new Response('Not Found', { status: 404 });
     },
   };
   ```

4. **Add TypeScript Types**
   
   Update `cloudflare/src/types.ts` (or create if doesn't exist):
   ```typescript
   export interface Env {
     ENVIRONMENT?: string;
     DB?: D1Database;
     CACHE?: KVNamespace;
     SESSIONS?: KVNamespace;
     IMAGES?: R2Bucket;
     // ... other bindings
   }
   ```

5. **Build and Test Locally**
   ```bash
   cd cloudflare
   npm run dev
   
   # In another terminal
   curl http://localhost:8787/api/health
   
   # Expected output:
   # {
   #   "status": "healthy",
   #   "timestamp": "2025-12-31T06:00:00Z",
   #   "version": "0.4.0",
   #   "environment": "production"
   # }
   ```

6. **Deploy to Staging**
   ```bash
   npx wrangler deploy --env staging
   
   # Test deployed endpoint
   curl https://arbfinder-worker-staging.[your-subdomain].workers.dev/api/health
   ```

7. **Commit Changes**
   ```bash
   git add cloudflare/src/
   git commit -m "Add health check endpoint to Worker"
   git push
   ```

#### Verification
```bash
# Test health endpoint
WORKER_URL="https://arbfinder-worker-staging.[your-subdomain].workers.dev"
curl -i "$WORKER_URL/api/health"

# Should return:
# HTTP/2 200
# content-type: application/json
# {
#   "status": "healthy",
#   ...
# }

# Test with monitoring tools
# Add to uptime monitoring service
# Set alert threshold: response time > 5000ms or status != 200
```

#### Acceptance Criteria
- [ ] `/api/health` endpoint returns 200 OK
- [ ] Response is valid JSON
- [ ] Response includes status, timestamp, version
- [ ] Endpoint works in local dev
- [ ] Endpoint works in staging
- [ ] Endpoint works in production
- [ ] Response time < 1000ms (typically ~50-200ms)
- [ ] Workflow verification step passes

#### Monitoring Setup
```javascript
// Add to monitoring service (e.g., Better Uptime, Pingdom)
{
  "url": "https://arbfinder-worker-production.[your-subdomain].workers.dev/api/health",
  "method": "GET",
  "interval": 60,  // Check every 60 seconds
  "timeout": 30,   // Timeout after 30 seconds
  "expectedStatusCode": 200,
  "expectedResponse": {
    "jsonPath": "$.status",
    "expectedValue": "healthy"
  }
}
```

---

### AGENT-005: Configure Cloudflare Services
**Priority**: P1 - Infrastructure  
**Estimated Time**: 2 hours  
**Dependencies**: AGENT-001 (secrets)  
**Agent Type**: DevOps  
**Status**: Not Started

#### Context
The Worker configuration (`wrangler.toml`) references multiple Cloudflare services with placeholder IDs. These services need to be created and configured.

#### Prerequisites
- Wrangler CLI installed
- Cloudflare account with Workers/Pages access
- CLOUDFLARE_API_TOKEN environment variable set

#### Services to Create
1. D1 Database (SQL database)
2. KV Namespaces (key-value storage) × 3
3. R2 Buckets (object storage) × 3
4. Hyperdrive (database connection pooling) - optional
5. Queues (async job processing) × 3
6. Analytics Engine binding

#### Detailed Steps

##### Part 1: Create D1 Database
```bash
cd cloudflare

# Create production database
wrangler d1 create arbfinder-db

# Output will include database_id, e.g.:
# ✅ Successfully created DB 'arbfinder-db'!
# 
# [[d1_databases]]
# binding = "DB"
# database_name = "arbfinder-db"
# database_id = "abc123..."

# Save this database_id!

# Create preview database (for development)
wrangler d1 create arbfinder-db-preview
# Save this database_id too!

# Update wrangler.toml:
# database_id = "abc123..."  # Production ID
# preview_database_id = "xyz789..."  # Preview ID
```

##### Part 2: Create KV Namespaces
```bash
# Create production KV namespaces
wrangler kv:namespace create "CACHE"
wrangler kv:namespace create "SESSIONS"
wrangler kv:namespace create "ALERTS"

# Each will output an ID like:
# ✅ Success!
# Add the following to your wrangler.toml:
# { binding = "CACHE", id = "abc123..." }

# Create preview namespaces (for development)
wrangler kv:namespace create "CACHE" --preview
wrangler kv:namespace create "SESSIONS" --preview
wrangler kv:namespace create "ALERTS" --preview

# Update wrangler.toml with all IDs
```

##### Part 3: Create R2 Buckets
```bash
# Create production buckets
wrangler r2 bucket create arbfinder-images
wrangler r2 bucket create arbfinder-data
wrangler r2 bucket create arbfinder-backups

# Create preview buckets
wrangler r2 bucket create arbfinder-images-preview
wrangler r2 bucket create arbfinder-data-preview
wrangler r2 bucket create arbfinder-backups-preview

# Verify creation
wrangler r2 bucket list
```

##### Part 4: Create Queues (Optional but Recommended)
```bash
# Create queues for async job processing
wrangler queues create arbfinder-snipe-queue
wrangler queues create arbfinder-alert-queue
wrangler queues create arbfinder-crawler-queue

# Verify creation
wrangler queues list
```

##### Part 5: Update wrangler.toml
Open `cloudflare/wrangler.toml` and replace all placeholder IDs:

```toml
# D1 Database bindings
[[d1_databases]]
binding = "DB"
database_name = "arbfinder-db"
database_id = "abc123..."  # Replace with actual ID from step 1
preview_database_id = "xyz789..."  # Replace with preview ID

# KV namespaces for caching
[[kv_namespaces]]
binding = "CACHE"
id = "cache_prod_id"  # Replace
preview_id = "cache_preview_id"  # Replace

[[kv_namespaces]]
binding = "SESSIONS"
id = "sessions_prod_id"  # Replace
preview_id = "sessions_preview_id"  # Replace

[[kv_namespaces]]
binding = "ALERTS"
id = "alerts_prod_id"  # Replace
preview_id = "alerts_preview_id"  # Replace

# R2 bucket bindings
[[r2_buckets]]
binding = "IMAGES"
bucket_name = "arbfinder-images"
preview_bucket_name = "arbfinder-images-preview"

[[r2_buckets]]
binding = "DATA"
bucket_name = "arbfinder-data"
preview_bucket_name = "arbfinder-data-preview"

[[r2_buckets]]
binding = "BACKUPS"
bucket_name = "arbfinder-backups"
preview_bucket_name = "arbfinder-backups-preview"
```

##### Part 6: Create Database Schema (if needed)
```bash
# Create migration file
cat > cloudflare/migrations/0001_initial.sql << 'EOF'
-- Initial schema for arbfinder-db
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price REAL,
    source TEXT,
    url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    keywords TEXT,
    max_price REAL,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_source ON items(source);
CREATE INDEX idx_items_price ON items(price);
CREATE INDEX idx_alerts_user ON alerts(user_id);
EOF

# Apply migration to production
wrangler d1 migrations apply arbfinder-db --remote

# Apply to preview
wrangler d1 migrations apply arbfinder-db-preview --local
```

##### Part 7: Test Service Connectivity
```bash
# Test D1
wrangler d1 execute arbfinder-db --remote --command "SELECT 1 as test"

# Test KV (requires worker deployed)
wrangler kv:key put --binding=CACHE "test_key" "test_value"
wrangler kv:key get --binding=CACHE "test_key"

# Test R2
echo "Test file content" > test.txt
wrangler r2 object put arbfinder-images/test.txt --file=test.txt
wrangler r2 object get arbfinder-images/test.txt
```

##### Part 8: Deploy Worker with Services
```bash
# Deploy to staging first
npx wrangler deploy --env staging

# Test services in worker
curl https://arbfinder-worker-staging.[your-subdomain].workers.dev/api/health
# Should show service status in response

# If all good, deploy to production
npx wrangler deploy --env production
```

##### Part 9: Commit Configuration
```bash
git add cloudflare/wrangler.toml cloudflare/migrations/
git commit -m "Configure Cloudflare services with actual IDs"
git push
```

#### Verification Checklist
```bash
# Verify all services exist
wrangler d1 list | grep arbfinder
wrangler kv:namespace list | grep -E "CACHE|SESSIONS|ALERTS"
wrangler r2 bucket list | grep arbfinder
wrangler queues list | grep arbfinder

# Verify wrangler.toml has no placeholders
grep -i "your-" cloudflare/wrangler.toml  # Should return nothing

# Test worker can access services
curl https://arbfinder-worker-staging.[your-subdomain].workers.dev/api/health
# Response should include "services": {"d1": true, "kv": true, ...}
```

#### Acceptance Criteria
- [ ] D1 database created (production + preview)
- [ ] All 3 KV namespaces created (prod + preview)
- [ ] All 3 R2 buckets created (prod + preview)
- [ ] Queues created (optional)
- [ ] wrangler.toml updated with actual IDs
- [ ] No placeholder IDs remain
- [ ] Database schema applied
- [ ] Worker can connect to all services
- [ ] Health check shows services as healthy

#### Cost Estimation
Free tier limits (as of 2025):
- D1: 5 GB storage, 5M reads/day, 100K writes/day
- KV: 100K reads/day, 1K writes/day, 1 GB storage
- R2: 10 GB storage, Class A operations: 1M/month
- Workers: 100K requests/day

Estimated costs (low traffic):
- **First month**: $0 (within free tier)
- **Growing traffic**: $5-20/month
- **High traffic**: $50-100/month

---

### AGENT-006: Create Environment Variable Configuration
**Priority**: P1 - Configuration  
**Estimated Time**: 30 minutes  
**Dependencies**: AGENT-002 (URLs configured)  
**Agent Type**: DevOps/Frontend  
**Status**: Not Started

#### Context
The frontend needs environment variables to connect to the API. Different variables are needed for production, staging, and local development.

#### Prerequisites
- Know your Worker URLs
- Access to repository

#### Detailed Steps

##### Step 1: Create Environment Files

1. **Production Environment** (`frontend/.env.production`)
   ```bash
   cd frontend
   cat > .env.production << 'EOF'
   # Cloudflare Pages - Production
   NEXT_PUBLIC_API_BASE=https://arbfinder-worker-production.[your-subdomain].workers.dev
   NEXT_PUBLIC_ENVIRONMENT=production
   NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX
   NEXT_PUBLIC_VERSION=0.4.0
   NEXT_PUBLIC_APP_NAME=ArbFinder Suite
   EOF
   ```

2. **Staging Environment** (`frontend/.env.staging`)
   ```bash
   cat > .env.staging << 'EOF'
   # Cloudflare Pages - Staging
   NEXT_PUBLIC_API_BASE=https://arbfinder-worker-staging.[your-subdomain].workers.dev
   NEXT_PUBLIC_ENVIRONMENT=staging
   NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX
   NEXT_PUBLIC_VERSION=0.4.0-staging
   NEXT_PUBLIC_APP_NAME=ArbFinder Suite (Staging)
   EOF
   ```

3. **Development Environment** (`frontend/.env.local.example`)
   ```bash
   cat > .env.local.example << 'EOF'
   # Local Development - Copy to .env.local and customize
   NEXT_PUBLIC_API_BASE=http://localhost:8787
   NEXT_PUBLIC_ENVIRONMENT=development
   NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID=
   NEXT_PUBLIC_VERSION=0.4.0-dev
   NEXT_PUBLIC_APP_NAME=ArbFinder Suite (Dev)
   NEXT_PUBLIC_DEBUG=true
   EOF
   ```

##### Step 2: Update .gitignore

Ensure `.env.local` is ignored but examples are tracked:
```bash
cd frontend

# Check if .env.local is in .gitignore
grep "\.env\.local" ../.gitignore || echo ".env.local" >> ../.gitignore
```

##### Step 3: Update Workflow to Use Correct Environment

Edit `.github/workflows/cloudflare-deploy.yml`:
```yaml
- name: Set environment variables
  working-directory: frontend
  run: |
    if [ "${{ github.ref }}" == "refs/heads/main" ]; then
      cp .env.production .env.local
      echo "Building for PRODUCTION"
    elif [ "${{ github.ref }}" == "refs/heads/staging" ]; then
      cp .env.staging .env.local
      echo "Building for STAGING"
    else
      # PR preview - use staging config
      cp .env.staging .env.local
      echo "Building for PREVIEW"
    fi
    
    # Show what we're building with (mask sensitive values)
    cat .env.local | grep -v "TOKEN\|SECRET\|KEY"
```

##### Step 4: Update Code to Use Environment Variables

Create or update `frontend/lib/config.ts`:
```typescript
// frontend/lib/config.ts
export const config = {
  apiBase: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8787',
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  gtmId: process.env.NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID,
  version: process.env.NEXT_PUBLIC_VERSION || '0.0.0',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'ArbFinder Suite',
  isDev: process.env.NEXT_PUBLIC_ENVIRONMENT === 'development',
  isProd: process.env.NEXT_PUBLIC_ENVIRONMENT === 'production',
  debug: process.env.NEXT_PUBLIC_DEBUG === 'true',
} as const;

// Helper to construct API URLs
export function apiUrl(path: string): string {
  const base = config.apiBase.replace(/\/$/, ''); // Remove trailing slash
  const cleanPath = path.replace(/^\//, ''); // Remove leading slash
  return `${base}/${cleanPath}`;
}

// Example usage:
// const response = await fetch(apiUrl('/api/health'));
```

Update API calls to use config:
```typescript
// Example in a component or API route
import { apiUrl } from '@/lib/config';

async function fetchData() {
  const response = await fetch(apiUrl('/api/items'));
  return response.json();
}
```

##### Step 5: Document Environment Variables

Create `frontend/ENV_VARIABLES.md`:
```markdown
# Environment Variables

## Required Variables

### `NEXT_PUBLIC_API_BASE`
- **Description**: Base URL for backend API
- **Type**: String (URL)
- **Example**: `https://arbfinder-worker-production.example.workers.dev`
- **Required**: Yes

### `NEXT_PUBLIC_ENVIRONMENT`
- **Description**: Deployment environment
- **Type**: String
- **Options**: `development`, `staging`, `production`
- **Required**: Yes

## Optional Variables

### `NEXT_PUBLIC_GOOGLE_TAG_MANAGER_ID`
- **Description**: Google Tag Manager container ID
- **Type**: String
- **Example**: `GTM-XXXXXXX`
- **Required**: No
- **Notes**: Leave empty to disable analytics

### `NEXT_PUBLIC_DEBUG`
- **Description**: Enable debug mode
- **Type**: Boolean (string)
- **Options**: `true`, `false`
- **Default**: `false`

## Setup Instructions

### Local Development
```bash
cp .env.local.example .env.local
# Edit .env.local with your local settings
npm run dev
```

### Cloudflare Pages
Environment variables are managed in:
1. `.env.production` for production builds
2. `.env.staging` for staging builds
3. Cloudflare Pages Dashboard for overrides

## Security Notes
- Never commit `.env.local` to git
- Use Cloudflare Pages Environment Variables for secrets
- Prefix public variables with `NEXT_PUBLIC_`
```

##### Step 6: Test Configuration

```bash
cd frontend

# Test production build
cp .env.production .env.local
npm run build
grep -r "production" out/index.html  # Should find references

# Test staging build
cp .env.staging .env.local
npm run build
grep -r "staging" out/index.html

# Test local development
cp .env.local.example .env.local
npm run dev
# Open http://localhost:3000
# Check browser console for environment
```

##### Step 7: Commit Changes

```bash
git add frontend/.env.production
git add frontend/.env.staging
git add frontend/.env.local.example
git add frontend/lib/config.ts
git add frontend/ENV_VARIABLES.md
git add .github/workflows/cloudflare-deploy.yml
git commit -m "Add environment variable configuration for all environments"
git push
```

#### Verification
```bash
# Check files exist
ls -la frontend/.env.*

# Verify no secrets in .env files
grep -i "secret\|password\|token" frontend/.env.production
# Should return nothing sensitive

# Test build process
cd frontend
npm run build
grep -r "NEXT_PUBLIC_API_BASE" .next/
# Should find references

# Test in deployed environment
# After deployment, check browser console:
console.log(config.apiBase);  # Should show correct URL
```

#### Acceptance Criteria
- [ ] `.env.production` file created
- [ ] `.env.staging` file created
- [ ] `.env.local.example` file created
- [ ] `.env.local` is in .gitignore
- [ ] Workflow uses correct env file per environment
- [ ] Code uses config helper
- [ ] Documentation complete
- [ ] No secrets committed
- [ ] Builds work with all environments

---

## 🟡 P2: Medium Priority Tasks

### AGENT-007: Add Build Caching
**Priority**: P2 - Performance  
**Estimated Time**: 30 minutes  
**Dependencies**: None  
**Agent Type**: DevOps  
**Status**: Not Started

#### Context
GitHub Actions can cache dependencies and build artifacts to speed up CI/CD runs. Without caching, each run downloads all dependencies from scratch.

#### Benefits
- **50-70% faster builds** after first run
- **Reduced bandwidth** usage
- **Lower GitHub Actions minutes** consumption
- **Faster feedback** on PRs

#### Detailed Steps

##### Step 1: Add Dependency Caching

Edit `.github/workflows/cloudflare-deploy.yml`:

1. **Cache Node.js dependencies (Frontend)**
   ```yaml
   - name: Setup Node.js
     uses: actions/setup-node@v4
     with:
       node-version: ${{ env.NODE_VERSION }}
       cache: 'npm'
       cache-dependency-path: frontend/package-lock.json  # Enable built-in caching
   ```

2. **Cache Node.js dependencies (Worker)**
   ```yaml
   - name: Setup Node.js
     uses: actions/setup-node@v4
     with:
       node-version: ${{ env.NODE_VERSION }}
       cache: 'npm'
       cache-dependency-path: cloudflare/package-lock.json
   ```

##### Step 2: Add Build Output Caching

Add after Node.js setup:
```yaml
- name: Cache Next.js build
  uses: actions/cache@v4
  with:
    path: |
      frontend/.next/cache
      frontend/node_modules/.cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('frontend/package-lock.json') }}-${{ hashFiles('frontend/**/*.{ts,tsx,js,jsx}') }}
    restore-keys: |
      ${{ runner.os }}-nextjs-${{ hashFiles('frontend/package-lock.json') }}-
      ${{ runner.os }}-nextjs-

- name: Cache Worker build
  uses: actions/cache@v4
  with:
    path: |
      cloudflare/.wrangler
      cloudflare/node_modules/.cache
    key: ${{ runner.os }}-worker-${{ hashFiles('cloudflare/package-lock.json') }}-${{ hashFiles('cloudflare/src/**/*.ts') }}
    restore-keys: |
      ${{ runner.os }}-worker-${{ hashFiles('cloudflare/package-lock.json') }}-
      ${{ runner.os }}-worker-
```

##### Step 3: Add Python Dependency Caching (Optional)

If backend tests are run in workflow:
```yaml
- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: |
      .venv
      ~/.cache/uv
    key: ${{ runner.os }}-python-3.10-${{ hashFiles('uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-python-3.10-
```

##### Step 4: Configure Cache Expiration

Add to workflow file (top-level):
```yaml
env:
  CACHE_VERSION: v1  # Increment to bust all caches
```

Update cache keys to include version:
```yaml
key: ${{ env.CACHE_VERSION }}-${{ runner.os }}-nextjs-...
```

##### Step 5: Monitor Cache Performance

Add step to show cache stats:
```yaml
- name: Cache statistics
  run: |
    echo "=== Cache Status ==="
    if [ -d "frontend/.next/cache" ]; then
      echo "✅ Next.js cache found"
      du -sh frontend/.next/cache
    else
      echo "❌ Next.js cache not found (first run)"
    fi
    
    if [ -d "frontend/node_modules" ]; then
      echo "✅ Node modules cached"
      echo "Files: $(find frontend/node_modules -type f | wc -l)"
    fi
```

##### Step 6: Test Caching

```bash
# First run - cache miss
git add .github/workflows/cloudflare-deploy.yml
git commit -m "Add build caching to workflow"
git push

# Check workflow logs:
# - "Cache not found for input keys"
# - Build takes ~2-3 minutes

# Second run - cache hit
git commit --allow-empty -m "Test cache hit"
git push

# Check workflow logs:
# - "Cache restored from key"
# - Build takes ~30-60 seconds
```

#### Verification
```bash
# Compare build times
gh run list --workflow=cloudflare-deploy.yml --limit 10

# Check specific run
gh run view <run-id>

# Expected improvements:
# - First run: 2-3 minutes
# - Cached run: 30-60 seconds
# - 50-70% time reduction
```

#### Acceptance Criteria
- [ ] Node.js dependencies cached
- [ ] Next.js build cache configured
- [ ] Worker build cache configured
- [ ] Cache hit rate >80% after first run
- [ ] Build time reduced by >50%
- [ ] Workflow logs show cache status
- [ ] Cache invalidates on dependency changes

#### Cache Size Limits
GitHub Actions cache limits:
- **Maximum cache size**: 10 GB per repository
- **Cache retention**: 7 days for unused caches
- **Cache access**: Most recent cache used first

Typical cache sizes:
- Node modules: 200-500 MB
- Next.js cache: 50-200 MB
- Python venv: 100-300 MB

#### Common Issues

**Issue**: Cache not restoring  
**Solution**: Check key hash matches, ensure paths are correct

**Issue**: Builds using stale cache  
**Solution**: Increment CACHE_VERSION or delete cache via GitHub UI

**Issue**: Cache too large  
**Solution**: Exclude unnecessary files in cache path

---

### AGENT-008: Create Test Suite
**Priority**: P2 - Quality  
**Estimated Time**: 4 hours  
**Dependencies**: AGENT-004 (health endpoint)  
**Agent Type**: QA/Testing  
**Status**: Not Started

#### Context
Automated tests ensure deployments work correctly and catch regressions. Tests should cover frontend pages, Worker endpoints, and integration scenarios.

#### Test Types
1. **Unit Tests**: Test individual components/functions
2. **Integration Tests**: Test API endpoints and data flow
3. **E2E Tests**: Test user workflows end-to-end
4. **Deployment Tests**: Verify deployed services work

#### Detailed Steps

##### Part 1: Set Up Test Framework

```bash
cd frontend

# Install testing dependencies
npm install --save-dev \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  @jest/globals \
  jest \
  jest-environment-jsdom \
  @playwright/test

# Create Jest config
cat > jest.config.js << 'EOF'
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
};

module.exports = createJestConfig(customJestConfig);
EOF

# Create Jest setup
cat > jest.setup.js << 'EOF'
import '@testing-library/jest-dom';
EOF

# Add test scripts to package.json
npm pkg set scripts.test="jest"
npm pkg set scripts.test:watch="jest --watch"
npm pkg set scripts.test:coverage="jest --coverage"
```

##### Part 2: Write Frontend Unit Tests

Create `frontend/__tests__/lib/config.test.ts`:
```typescript
import { config, apiUrl } from '@/lib/config';

describe('Config', () => {
  it('should have valid apiBase', () => {
    expect(config.apiBase).toBeDefined();
    expect(config.apiBase).toMatch(/^https?:\/\//);
  });

  it('should construct API URLs correctly', () => {
    const url = apiUrl('/api/health');
    expect(url).toContain('/api/health');
    expect(url).toMatch(/^https?:\/\//);
  });

  it('should handle trailing slashes', () => {
    const url1 = apiUrl('api/health');
    const url2 = apiUrl('/api/health');
    expect(url1).toBe(url2);
  });
});
```

Create `frontend/__tests__/app/page.test.tsx`:
```typescript
import { render, screen } from '@testing-library/react';
import Page from '@/app/page';

describe('Homepage', () => {
  it('renders without crashing', () => {
    render(<Page />);
    expect(screen.getByText(/ArbFinder/i)).toBeInTheDocument();
  });

  it('displays main navigation', () => {
    render(<Page />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});
```

##### Part 3: Write Worker Tests

Create `cloudflare/src/__tests__/health.test.ts`:
```typescript
import { handleHealth } from '../health';

describe('Health Check', () => {
  it('should return healthy status', async () => {
    const env = {} as Env;
    const ctx = {} as ExecutionContext;
    
    const response = await handleHealth(env, ctx);
    expect(response.status).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.version).toBeDefined();
  });
});
```

##### Part 4: Write Integration Tests

Create `tests/integration/api.test.ts`:
```typescript
describe('API Integration', () => {
  const API_BASE = process.env.TEST_API_BASE || 'http://localhost:8787';

  it('health endpoint returns 200', async () => {
    const response = await fetch(`${API_BASE}/api/health`);
    expect(response.status).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  it('returns 404 for invalid routes', async () => {
    const response = await fetch(`${API_BASE}/invalid-route`);
    expect(response.status).toBe(404);
  });
});
```

##### Part 5: Write E2E Tests with Playwright

Create `frontend/playwright.config.ts`:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

Create `frontend/e2e/homepage.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';

test('homepage loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/ArbFinder/);
  await expect(page.locator('h1')).toContainText(/ArbFinder/);
});

test('navigation works', async ({ page }) => {
  await page.goto('/');
  await page.click('a[href="/dashboard"]');
  await expect(page).toHaveURL(/dashboard/);
});
```

##### Part 6: Add Tests to CI/CD

Update `.github/workflows/cloudflare-deploy.yml`:
```yaml
test-frontend:
  name: Test Frontend
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 18
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: frontend
      run: npm ci
    
    - name: Run unit tests
      working-directory: frontend
      run: npm test -- --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        files: ./frontend/coverage/lcov.info
        flags: frontend

test-worker:
  name: Test Worker
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 18
        cache: 'npm'
        cache-dependency-path: cloudflare/package-lock.json
    
    - name: Install dependencies
      working-directory: cloudflare
      run: npm ci
    
    - name: Run tests
      working-directory: cloudflare
      run: npm test

deploy-pages:
  needs: [test-frontend, test-worker]  # Wait for tests
  # ... rest of deployment job
```

##### Part 7: Run Tests Locally

```bash
# Frontend tests
cd frontend
npm test
npm run test:coverage

# Worker tests
cd cloudflare
npm test

# E2E tests
cd frontend
npx playwright install
npx playwright test

# Integration tests
cd tests/integration
npm test
```

#### Verification
```bash
# Check all tests pass
cd frontend && npm test && cd ..
cd cloudflare && npm test && cd ..

# Check coverage
cd frontend
npm run test:coverage
# Should see coverage report in coverage/

# Run in CI
git add .
git commit -m "Add comprehensive test suite"
git push
# Check GitHub Actions for test results
```

#### Acceptance Criteria
- [ ] Jest configured for frontend
- [ ] Unit tests for key components
- [ ] Worker endpoint tests
- [ ] Integration tests for API
- [ ] E2E tests with Playwright
- [ ] Tests run in CI/CD
- [ ] Coverage >70%
- [ ] All tests passing

---

## Test Summary Template

After completing testing tasks, use this template:

```markdown
# Test Results Summary

## Test Coverage
- Frontend Unit Tests: XX/XX passing (XX% coverage)
- Worker Tests: XX/XX passing
- Integration Tests: XX/XX passing
- E2E Tests: XX/XX passing

## Performance Metrics
- Page Load Time: XXXms
- API Response Time: XXms
- Build Time: XXs
- Deployment Time: XXs

## Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Status: Fixed/In Progress/Blocked
   
## Next Steps
- [ ] Task 1
- [ ] Task 2
```

---

## 📝 Task Completion Checklist

Use this checklist to track overall progress:

### Critical (P0)
- [ ] AGENT-001: Configure GitHub Secrets
- [ ] AGENT-002: Update Workflow Domain Configuration
- [ ] AGENT-003: Fix Next.js Security Vulnerability

### High Priority (P1)
- [ ] AGENT-004: Implement Worker Health Check Endpoint
- [ ] AGENT-005: Configure Cloudflare Services
- [ ] AGENT-006: Create Environment Variable Configuration

### Medium Priority (P2)
- [ ] AGENT-007: Add Build Caching
- [ ] AGENT-008: Create Test Suite

### Verification
- [ ] All workflows passing
- [ ] Deployments successful
- [ ] Health checks working
- [ ] Tests passing
- [ ] Documentation complete

---

## 🔄 Iteration Process

For each task:
1. Read task details thoroughly
2. Gather prerequisites
3. Execute steps in order
4. Verify each step works
5. Run acceptance tests
6. Document any issues
7. Mark task complete
8. Move to next task

If blocked:
1. Document the blocker
2. Update task status to "Blocked"
3. Note dependencies in task
4. Work on unblocked tasks
5. Return when blocker resolved

---

## 📞 Support

If you encounter issues with any task:

1. **Check the Troubleshooting section** in CLOUDFLARE_DEPLOYMENT_GUIDE.md
2. **Review Cloudflare documentation**:
   - https://developers.cloudflare.com/pages
   - https://developers.cloudflare.com/workers
3. **Check GitHub Actions logs** for error details
4. **Test locally** before deploying
5. **Ask for help** in project discussions

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-31  
**Total Estimated Time**: 8-10 hours for all tasks
