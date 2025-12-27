# Cloudflare Pages Deployment - Quick Start Guide

Get your ArbFinder Suite deployed to Cloudflare Pages in under 10 minutes!

## 🚀 One-Command Deployment

```bash
./scripts/cloudflare/deploy_complete.sh
```

That's it! This single command will:
- ✅ Set up all infrastructure (D1, R2, KV)
- ✅ Deploy your Worker backend
- ✅ Build and deploy your Pages frontend
- ✅ Configure service bindings
- ✅ Run verification tests

## 📋 Prerequisites

Before running the deployment, ensure you have:

### 1. Cloudflare Account (Free)
Sign up at: https://dash.cloudflare.com/sign-up

### 2. Node.js 18+ Installed
```bash
node --version  # Should be v18 or higher
```

If you need to install Node.js:
- **macOS**: `brew install node@18`
- **Ubuntu/Debian**: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs`
- **Windows**: Download from https://nodejs.org

### 3. Wrangler CLI
```bash
npm install -g wrangler@latest
```

### 4. Authentication
```bash
wrangler login
```

This will open a browser window to authenticate with Cloudflare.

## 🎯 Step-by-Step Instructions

### Step 1: Clone the Repository (if not already done)

```bash
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite
```

### Step 2: Authenticate with Cloudflare

```bash
wrangler login
```

Follow the browser prompts to authenticate.

### Step 3: Run the Deployment Script

```bash
./scripts/cloudflare/deploy_complete.sh
```

The script will:
1. Check prerequisites (Node.js, Wrangler, etc.)
2. Create D1 database
3. Create R2 storage buckets
4. Create KV namespaces
5. Deploy Worker
6. Build and deploy Pages
7. Configure bindings
8. Run verification tests

### Step 4: Configure Environment Variables

After deployment, set environment variables:

1. Go to https://dash.cloudflare.com/pages
2. Select your project (`arbfinder-suite`)
3. Navigate to **Settings > Environment variables**
4. Click **Add variable** for both **Production** and **Preview**:
   - `NEXT_PUBLIC_API_BASE`: Your Worker URL (shown after deployment)
   - `NEXT_PUBLIC_GTM_ID`: (Optional) Your Google Tag Manager ID

### Step 5: Access Your Site!

Your site will be available at:
```
https://arbfinder-suite.pages.dev
```

The exact URL will be displayed at the end of the deployment.

## 🎨 What's Deployed

After successful deployment, you'll have:

### Frontend (Cloudflare Pages)
- **URL**: `https://arbfinder-suite.pages.dev`
- **Features**:
  - Dashboard page
  - Alerts management
  - Price comparison tools
  - Auction snipe scheduler
  - AI crew runner

### Backend (Cloudflare Worker)
- **URL**: `https://arbfinder-worker.your-subdomain.workers.dev`
- **Services**:
  - REST API endpoints
  - Image upload/storage
  - Scheduled tasks (crawlers, alerts)
  - Queue processing

### Database & Storage
- **D1 Database**: SQLite-based edge database
- **R2 Storage**: Object storage for images and data
- **KV Namespaces**: Key-value storage for caching and sessions

## 🔧 Common Issues & Solutions

### Issue: "wrangler command not found"
```bash
npm install -g wrangler@latest
```

### Issue: "Not authenticated"
```bash
wrangler login
```

### Issue: "Node version too old"
Update Node.js to version 18 or higher.

### Issue: "Build failed"
```bash
cd frontend
npm install
npm run build
```

### Issue: "Pages already exists"
That's OK! The script will deploy to the existing project.

## 🔄 Redeploying

To redeploy after making changes:

### Quick Redeploy (Skip Infrastructure Setup)
```bash
./scripts/cloudflare/deploy_complete.sh --skip-setup --skip-test
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

## 📊 Monitoring Your Deployment

### View Real-Time Logs
```bash
# Worker logs
wrangler tail --name arbfinder-worker

# Pages logs
wrangler pages deployment tail --project-name arbfinder-suite
```

### Check Deployment Status
```bash
# Verify everything is working
./scripts/cloudflare/verify_deployment.sh
```

### Cloudflare Dashboard
Visit https://dash.cloudflare.com to:
- View analytics
- Monitor performance
- Check error logs
- Configure settings

## 🎯 Next Steps

Now that your site is deployed:

1. **Configure Custom Domain** (Optional)
   - Go to Pages settings
   - Add your custom domain
   - Update DNS records

2. **Set Up Monitoring**
   - Configure Cloudflare Analytics
   - Set up email alerts
   - Enable error tracking

3. **Configure WAF Rules**
   - Set up security rules
   - Enable rate limiting
   - Configure DDoS protection

4. **Test Your Deployment**
   - Visit your Pages URL
   - Test all features
   - Check API endpoints

5. **Continuous Deployment**
   - Connect GitHub repository
   - Enable automatic deployments
   - Set up preview branches

## 📚 Additional Resources

- **Full Deployment Guide**: [scripts/cloudflare/README.md](README.md)
- **Cloudflare Setup Documentation**: [docs/platform/CLOUDFLARE_SETUP.md](../../docs/platform/CLOUDFLARE_SETUP.md)
- **Troubleshooting**: [scripts/cloudflare/README.md#troubleshooting](README.md#troubleshooting)
- **Cloudflare Workers Docs**: https://developers.cloudflare.com/workers/
- **Cloudflare Pages Docs**: https://developers.cloudflare.com/pages/

## 💬 Need Help?

- **GitHub Issues**: https://github.com/cbwinslow/arbfinder-suite/issues
- **Cloudflare Community**: https://community.cloudflare.com/
- **Documentation**: Read the full docs in `docs/` directory

## 🎉 Success!

If you see this at the end of deployment:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Cloudflare Deployment Complete! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Congratulations! Your ArbFinder Suite is now live on Cloudflare! 🚀

---

**Quick Commands Reference:**

```bash
# Deploy everything
./scripts/cloudflare/deploy_complete.sh

# Redeploy (skip setup)
./scripts/cloudflare/deploy_complete.sh --skip-setup

# Verify deployment
./scripts/cloudflare/verify_deployment.sh

# View logs
wrangler tail --name arbfinder-worker
wrangler pages deployment tail --project-name arbfinder-suite

# Check status
wrangler deployments list
wrangler pages project list
```

---

**Last Updated**: 2025-12-27  
**Estimated Time**: 5-10 minutes  
**Difficulty**: Beginner-friendly 🌟
