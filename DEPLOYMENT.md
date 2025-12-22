# Deployment Guide

This guide covers deploying ArbFinder Suite to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloudflare Deployment](#cloudflare-deployment)
- [Traditional Hosting](#traditional-hosting)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Monitoring](#monitoring)

## Prerequisites

- Python 3.9+ installed
- Node.js 20+ installed
- Git installed
- Docker installed (optional)
- Cloudflare account (for Cloudflare deployment)

## Local Development

### Backend

```bash
# Clone repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies with locked versions
pip install -r requirements.lock

# Set environment variables
export ARBF_DB="~/.arb_finder.sqlite3"
export STRIPE_SECRET_KEY="your_stripe_key"

# Run API server
uvicorn backend.api.main:app --reload --port 8080
```

### Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm ci  # Use npm ci for reproducible builds with package-lock.json

# Set environment variables
echo "NEXT_PUBLIC_API_BASE=http://localhost:8080" > .env.local

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

### TypeScript Packages

```bash
# Build client package
cd packages/client
npm ci
npm run build

# Build CLI package
cd ../cli
npm ci
npm run build
npm link  # Make available globally
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

Services available:
- API: http://localhost:8080
- Frontend: http://localhost:3000

### Manual Docker Build

```bash
# Build backend image
docker build -t arbfinder-suite:latest .

# Run backend container
docker run -d \
  -p 8080:8080 \
  -e ARBF_DB=/data/arb_finder.sqlite3 \
  -e STRIPE_SECRET_KEY=your_key \
  -v $(pwd)/data:/data \
  --name arbfinder-api \
  arbfinder-suite:latest

# Build frontend image
cd frontend
docker build -t arbfinder-frontend:latest -f Dockerfile .

# Run frontend container
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE=http://localhost:8080 \
  --name arbfinder-frontend \
  arbfinder-frontend:latest
```

## Cloudflare Deployment

### Workers (Backend API)

```bash
# Navigate to cloudflare directory
cd cloudflare

# Install dependencies
npm ci

# Configure wrangler
# Edit wrangler.toml with your account details

# Deploy to production
npm run deploy:production

# Deploy to staging
npm run deploy:staging
```

### Pages (Frontend)

```bash
# Navigate to frontend
cd frontend

# Build for static export
# Edit next.config.mjs: change output to 'export'
npm run build

# Deploy using Cloudflare Pages
npx wrangler pages deploy out --project-name=arbfinder-suite

# Or use GitHub integration
# 1. Push to GitHub
# 2. Connect repository in Cloudflare Pages dashboard
# 3. Configure build settings:
#    - Build command: npm run build
#    - Build output directory: out
#    - Environment variables: NEXT_PUBLIC_API_BASE
```

### D1 Database

```bash
# Create D1 database
wrangler d1 create arbfinder-db

# Run migrations
wrangler d1 execute arbfinder-db --file=database/migrations/001_initial_schema.sql

# Query database
wrangler d1 execute arbfinder-db --command="SELECT * FROM listings LIMIT 10"
```

### R2 Storage

```bash
# Create R2 bucket
wrangler r2 bucket create arbfinder-storage

# Configure in wrangler.toml
[[r2_buckets]]
binding = "STORAGE"
bucket_name = "arbfinder-storage"
```

## Traditional Hosting

### VPS / Cloud Server

#### Backend

```bash
# On server, clone repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Install dependencies
pip install -r requirements.lock

# Install systemd service
sudo cp deployment/arbfinder-api.service /etc/systemd/system/
sudo systemctl enable arbfinder-api
sudo systemctl start arbfinder-api

# Check status
sudo systemctl status arbfinder-api
```

#### Frontend

```bash
# Build frontend
cd frontend
npm ci
npm run build

# Serve with PM2
npm install -g pm2
pm2 start npm --name "arbfinder-frontend" -- start
pm2 save
pm2 startup
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/arbfinder

# Backend API
server {
    listen 80;
    server_name api.arbfinder.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Frontend
server {
    listen 80;
    server_name arbfinder.com www.arbfinder.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/arbfinder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables

### Backend

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ARBF_DB` | Database path | `~/.arb_finder.sqlite3` | No |
| `STRIPE_SECRET_KEY` | Stripe API key | - | For payments |
| `FRONTEND_ORIGIN` | CORS origin | `http://localhost:3000` | No |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account | - | For R2 |
| `CLOUDFLARE_R2_ACCESS_KEY` | R2 access key | - | For R2 |
| `CLOUDFLARE_R2_SECRET_KEY` | R2 secret key | - | For R2 |

### Frontend

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_BASE` | Backend API URL | `http://localhost:8080` | Yes |

### Setting Variables

**Local development** (.env):
```bash
ARBF_DB=~/.arb_finder.sqlite3
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_BASE=http://localhost:8080
```

**Docker** (docker-compose.yml):
```yaml
environment:
  - ARBF_DB=/data/arb_finder.sqlite3
  - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
```

**Cloudflare Workers** (wrangler.toml):
```toml
[vars]
FRONTEND_ORIGIN = "https://arbfinder.pages.dev"
```

**Production server** (systemd):
```ini
[Service]
Environment="ARBF_DB=/var/lib/arbfinder/db.sqlite3"
Environment="STRIPE_SECRET_KEY=sk_live_..."
```

## Database Setup

### SQLite (Development)

```bash
# Database is created automatically on first run
python -c "from backend.arb_finder import db_init; db_init('~/.arb_finder.sqlite3')"
```

### PostgreSQL (Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb arbfinder
sudo -u postgres createuser arbfinder_user

# Update backend to use PostgreSQL
export DATABASE_URL="postgresql://arbfinder_user:password@localhost/arbfinder"
```

### Cloudflare D1 (Cloudflare)

```bash
# Create database
wrangler d1 create arbfinder-db

# Run migrations
wrangler d1 execute arbfinder-db --file=database/migrations/001_initial_schema.sql
```

## Monitoring

### Logs

**Docker**:
```bash
docker-compose logs -f
docker logs arbfinder-api --tail=100 -f
```

**Systemd**:
```bash
sudo journalctl -u arbfinder-api -f
```

**Cloudflare**:
```bash
wrangler tail
```

### Health Checks

```bash
# Backend health
curl http://localhost:8080/

# Frontend health
curl http://localhost:3000/

# API endpoints
curl http://localhost:8080/api/statistics
```

### Performance Monitoring

Use Cloudflare Analytics for Workers and Pages:
```bash
# View analytics
wrangler analytics --project=arbfinder-suite
```

## Backup & Restore

### Database Backup

```bash
# SQLite
cp ~/.arb_finder.sqlite3 ~/backups/arb_finder_$(date +%Y%m%d).sqlite3

# PostgreSQL
pg_dump arbfinder > arbfinder_backup_$(date +%Y%m%d).sql

# Cloudflare D1
wrangler d1 export arbfinder-db --output=backup.sql
```

### Restore

```bash
# SQLite
cp ~/backups/arb_finder_20231215.sqlite3 ~/.arb_finder.sqlite3

# PostgreSQL
psql arbfinder < arbfinder_backup_20231215.sql

# Cloudflare D1
wrangler d1 execute arbfinder-db --file=backup.sql
```

## SSL/TLS

### Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d arbfinder.com -d www.arbfinder.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Cloudflare (Automatic)

SSL is automatic with Cloudflare Pages and Workers. Configure in dashboard:
- SSL/TLS mode: Full (strict)
- Always Use HTTPS: On
- Automatic HTTPS Rewrites: On

## Scaling

### Horizontal Scaling

Use load balancer (Nginx, HAProxy) with multiple backend instances:

```nginx
upstream arbfinder_backend {
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}

server {
    location / {
        proxy_pass http://arbfinder_backend;
    }
}
```

### Cloudflare (Auto-scaling)

Workers and Pages auto-scale automatically. No configuration needed.

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find process using port
sudo lsof -i :8080
# Kill process
sudo kill -9 <PID>
```

**Database locked**:
```bash
# Check for stale locks
fuser ~/.arb_finder.sqlite3
```

**Module not found**:
```bash
# Reinstall dependencies
pip install -r requirements.lock --force-reinstall
```

**Build fails**:
```bash
# Clear caches
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS** - Always encrypt in production
3. **Update dependencies** - Keep packages up to date
4. **Enable firewall** - Restrict access to necessary ports
5. **Use strong passwords** - For database and admin accounts
6. **Regular backups** - Automate database backups
7. **Monitor logs** - Set up log aggregation
8. **Rate limiting** - Implement API rate limiting

## CI/CD Integration

The repository includes GitHub Actions workflows:
- `.github/workflows/comprehensive-ci.yml` - Testing
- `.github/workflows/deploy-production.yml` - Deployment

Deployment is triggered automatically on:
- Push to `main` branch
- New version tags (v*)

## Support

For deployment issues:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review logs
- Open an issue on GitHub
- Check documentation

## Additional Resources

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Documentation](https://docs.docker.com/)
