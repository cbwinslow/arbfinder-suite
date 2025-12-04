# ArbFinder Platform Guide

Complete guide for the ArbFinder web platform with retro Windows theme, Crawl4AI integration, CrewAI agents, and cloud storage.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Web Dashboard](#web-dashboard)
5. [Crawler Configuration](#crawler-configuration)
6. [AI Agents](#ai-agents)
7. [Cloud Storage](#cloud-storage)
8. [Cloudflare Workers](#cloudflare-workers)
9. [Database Schema](#database-schema)
10. [Deployment](#deployment)

## Overview

The ArbFinder Suite now includes:

- **Retro Windows-themed Dashboard**: Modern, crisp UI with nostalgic Windows 95/98 aesthetics
- **Crawl4AI Integration**: Automated web scraping for price data ingestion
- **Prisma ORM**: Database abstraction supporting PostgreSQL and MySQL
- **CrewAI Agents**: Intelligent agents for data processing, enrichment, and quality control
- **MinIO & Cloudflare R2**: Cloud storage for images and data
- **Cloudflare Workers**: Serverless edge computing for data processing
- **Next.js Dashboard**: Real-time monitoring of crawlers and AI agents

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Retro Windows Dashboard                             │  │
│  │  - Crawler Monitor                                    │  │
│  │  - AI Agent Status                                    │  │
│  │  - Live Updates Feed                                  │  │
│  │  - Statistics Dashboard                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend API (FastAPI)                        │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Crawler Service  │  │  Agent Manager   │              │
│  │   (Crawl4AI)     │  │    (CrewAI)      │              │
│  └──────────────────┘  └──────────────────┘              │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ Storage Manager  │  │  Prisma ORM      │              │
│  │ (MinIO/R2)       │  │  (Postgres/MySQL)│              │
│  └──────────────────┘  └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Workers (Edge)                      │
│  - Scheduled Crawls                                         │
│  - Image Processing                                         │
│  - Metadata Enrichment                                      │
│  - R2 Storage Access                                        │
└─────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

#### Backend
```bash
# Install Python dependencies
pip install -e ".[dev]"

# Or use the requirements file
pip install -r backend/requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

#### Cloudflare Worker
```bash
cd cloudflare
npm install
```

### 2. Database Setup

#### PostgreSQL
```bash
# Create database
createdb arbfinder

# Set environment variable
export DATABASE_PROVIDER=postgresql
export DATABASE_URL=postgresql://user:password@localhost:5432/arbfinder

# Generate Prisma client
cd prisma
npx prisma generate
npx prisma db push
```

#### MySQL
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE arbfinder;"

# Set environment variable
export DATABASE_PROVIDER=mysql
export DATABASE_URL=mysql://user:password@localhost:3306/arbfinder

# Generate Prisma client
cd prisma
npx prisma generate
npx prisma db push
```

### 3. Configure Services

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- Database credentials
- MinIO/Cloudflare R2 credentials
- OpenAI API key
- Cloudflare account details

### 4. Configure Crawlers

Edit `config/crawler.toml` to add or modify crawler targets:

```toml
[[targets]]
name = "example_site"
url = "https://example.com"
enabled = true
schedule = "0 */4 * * *"
category_urls = [
    "https://example.com/deals",
]

[targets.selectors]
item_container = ".product"
title = ".product-title"
price = ".product-price"
image = ".product-image img"
link = ".product-link"
```

### 5. Start Services

#### Development Mode
```bash
# Terminal 1: Start backend API
uvicorn backend.api.main:app --reload --port 8080

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Start Cloudflare Worker (optional)
cd cloudflare
npm run dev
```

#### Production Mode
```bash
# Build frontend
cd frontend
npm run build

# Start with Docker Compose
docker-compose up -d
```

## Web Dashboard

Access the dashboard at `http://localhost:3000/dashboard`

### Features

#### Crawler Monitor
- Real-time status of all crawlers
- Items found per crawler
- Duration and success rate
- Error messages and diagnostics

#### AI Agent Status
- Active agent jobs
- Queue status
- Job completion times
- Error tracking

#### Live Updates
- Terminal-style activity feed
- Real-time events from crawlers and agents
- Color-coded by event type
- Auto-scrolling to latest updates

#### Statistics Cards
- Total items crawled
- Active agents count
- Success rate percentage
- Queue size

### Retro Windows Theme

The UI features authentic Windows 95/98 styling:
- Window borders with 3D beveled edges
- Classic title bars with minimize/maximize/close buttons
- System colors (silver-gray `#c0c0c0`, teal `#008080`)
- Pixel-perfect recreation of classic UI elements

## Crawler Configuration

### TOML Configuration

The crawler configuration uses TOML format for clarity and ease of editing.

#### Global Settings
```toml
[crawler]
user_agent = "ArbFinder/1.0"
timeout = 30
max_retries = 3
delay_between_requests = 2
concurrent_requests = 5
```

#### Target Sites
```toml
[[targets]]
name = "site_name"
url = "https://example.com"
enabled = true
schedule = "0 */4 * * *"  # Cron expression
category_urls = [
    "https://example.com/category1",
    "https://example.com/category2",
]

[targets.selectors]
item_container = ".item"
title = ".title"
price = ".price"
image = "img"
link = "a"
condition = ".condition"
```

### Crawler Service API

#### Run Single Crawler
```bash
POST /api/crawler/run/shopgoodwill
```

#### Run All Crawlers
```bash
POST /api/crawler/run-all
```

#### Get Crawler Status
```bash
GET /api/crawler/status
```

#### List Targets
```bash
GET /api/crawler/targets
```

## AI Agents

### Agent Types

1. **Web Crawler Agent**: Crawls websites and extracts data
2. **Data Validator**: Validates and cleans incoming data
3. **Market Researcher**: Analyzes market trends and pricing
4. **Price Specialist**: Computes optimal pricing strategies
5. **Listing Writer**: Creates SEO-optimized listings
6. **Image Processor**: Processes and uploads images
7. **Metadata Enricher**: Fills missing metadata fields
8. **Title Enhancer**: Improves product titles
9. **Cross-lister**: Posts to multiple platforms
10. **Quality Monitor**: Monitors data quality

### Agent API

#### List Agent Jobs
```bash
GET /api/agents/jobs?limit=20&status=running
```

#### Create Agent Job
```bash
POST /api/agents/jobs
{
  "agent_type": "metadata_enricher",
  "input_data": {
    "batch_size": 50
  }
}
```

#### Get Agent Types
```bash
GET /api/agents/types
```

### CrewAI Configuration

Edit `crew/crewai.yaml` to configure agents and workflows:

```yaml
agents:
  metadata_enricher:
    role: "Metadata Enrichment Agent"
    goal: "Fill missing metadata using AI"
    tools: [openai_api, metadata_database]

workers:
  metadata_worker:
    agent: metadata_enricher
    schedule: "*/15 * * * *"
    task: "Process metadata queue"
```

## Cloud Storage

### MinIO Setup

```bash
# Start MinIO with Docker
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"

# Set environment variables
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
```

### Cloudflare R2

```bash
# Set environment variables
export CLOUDFLARE_ACCOUNT_ID=your-account-id
export CLOUDFLARE_R2_ACCESS_KEY=your-access-key
export CLOUDFLARE_R2_SECRET_KEY=your-secret-key
export CLOUDFLARE_R2_BUCKET=arbfinder
```

### Storage API

#### Upload Image
```python
from backend.storage import MinIOClient

client = MinIOClient()
with open('image.jpg', 'rb') as f:
    url = client.upload_file('arbfinder-images', 'image.jpg', f, 'image/jpeg')
```

## Cloudflare Workers

### Deploy Worker

```bash
cd cloudflare

# Deploy to production
npm run deploy:production

# Deploy to staging
npm run deploy:staging
```

### Worker Features

- **Scheduled Tasks**: Automatic crawler runs every 4 hours
- **Image Processing**: Upload and serve images from R2
- **Metadata Processing**: Background jobs every 15 minutes
- **Caching**: KV-based caching for fast image delivery

### Worker Endpoints

- `POST /api/upload/image`: Upload image to R2
- `GET /api/images/{filename}`: Retrieve image from R2
- `GET /api/health`: Health check

## Database Schema

### Key Tables

#### Listings
```sql
- id: Primary key
- source: Origin site
- url: Unique listing URL
- title: Product title
- price: Current price
- metadata: JSON metadata
- createdAt: Timestamp
```

#### CrawlResults
```sql
- id: Primary key
- targetUrl: Crawled URL
- status: success/error/pending
- itemsFound: Number of items
- priceData: JSON price data
- startedAt: Start time
- completedAt: End time
```

#### AgentJobs
```sql
- id: Primary key
- agentType: Agent identifier
- status: queued/running/completed/failed
- input: JSON input
- output: JSON output
- startedAt: Start time
- completedAt: End time
```

See `prisma/schema.prisma` for complete schema.

## Deployment

### Cloudflare Pages (Frontend)

```bash
cd frontend

# Build for production
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy out
```

### Backend Deployment

#### Docker
```bash
docker build -t arbfinder-backend .
docker run -p 8080:8080 arbfinder-backend
```

#### Docker Compose
```bash
docker-compose up -d
```

### Environment Variables for Production

Update `.env` with production values:
- Use production database URLs
- Set secure API keys
- Configure production Cloudflare account
- Enable SSL/HTTPS

## Monitoring and Debugging

### View Logs

#### Backend
```bash
tail -f arbfinder.log
```

#### Cloudflare Worker
```bash
cd cloudflare
npm run tail
```

### Dashboard Metrics

Access real-time metrics at:
- `http://localhost:3000/dashboard` - Main dashboard
- `http://localhost:8080/api/activity-stats` - API statistics

### Troubleshooting

1. **Crawler not finding items**: Check CSS selectors in `config/crawler.toml`
2. **Database connection errors**: Verify `DATABASE_URL` in `.env`
3. **Agent jobs not running**: Check CrewAI configuration in `crew/crewai.yaml`
4. **Images not uploading**: Verify MinIO/R2 credentials in `.env`

## API Reference

### Crawler Endpoints
- `GET /api/crawler/status` - Get crawler status
- `POST /api/crawler/run/{target}` - Run specific crawler
- `POST /api/crawler/run-all` - Run all crawlers
- `GET /api/crawler/targets` - List targets

### Agent Endpoints
- `GET /api/agents/jobs` - List agent jobs
- `POST /api/agents/jobs` - Create agent job
- `GET /api/agents/types` - List agent types

### Live Updates
- `GET /api/live-updates` - Get activity feed
- `GET /api/activity-stats` - Get statistics

## Support

For issues and questions:
- GitHub Issues: https://github.com/cbwinslow/arbfinder-suite/issues
- Documentation: See README.md and other guides
- Examples: See EXAMPLES.md in the tui/ directory

## License

MIT License - see LICENSE file for details
