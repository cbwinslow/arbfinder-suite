# Quick Start: Web Platform & Dashboard

Get the ArbFinder web platform with retro Windows theme, crawlers, and AI agents up and running in minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL or MySQL (or use Docker)
- Git

## 🚀 Quick Setup

### Option 1: Automated Setup Script

```bash
# Clone the repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Run setup script
./setup.sh
```

The script will guide you through the setup process.

### Option 2: Docker Compose (Recommended)

```bash
# Clone and setup
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional - defaults work fine)
# nano .env

# Start all services
docker-compose up -d

# Wait for services to start (about 30 seconds)
# Check status
docker-compose ps
```

**Access the platform:**
- Dashboard: http://localhost:3000/dashboard
- API: http://localhost:8080
- MinIO Console: http://localhost:9001 (user: minioadmin, pass: minioadmin)

### Option 3: Manual Setup

#### Step 1: Database Setup

**PostgreSQL:**
```bash
# Install PostgreSQL
# Ubuntu/Debian: sudo apt install postgresql
# macOS: brew install postgresql

# Create database
createdb arbfinder

# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/arbfinder"
```

**MySQL:**
```bash
# Install MySQL
# Ubuntu/Debian: sudo apt install mysql-server
# macOS: brew install mysql

# Create database
mysql -u root -p -e "CREATE DATABASE arbfinder;"

# Set environment variable
export DATABASE_URL="mysql://user:password@localhost:3306/arbfinder"
```

#### Step 2: Install Dependencies

```bash
# Backend
pip install -e ".[dev]"

# Frontend
cd frontend
npm install
cd ..

# Cloudflare Worker (optional)
cd cloudflare
npm install
cd ..
```

#### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Minimum required settings:**
```env
DATABASE_PROVIDER=postgresql  # or mysql
DATABASE_URL=postgresql://user:pass@localhost:5432/arbfinder
OPENAI_API_KEY=sk-...  # For AI agents
```

#### Step 4: Initialize Database

```bash
# Generate Prisma client
npx prisma generate

# Create database tables
npx prisma db push
```

#### Step 5: Start Services

**Terminal 1 - Backend:**
```bash
uvicorn backend.api.main:app --reload --port 8080
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Optional Crawler Worker:**
```bash
python -m backend.crawler.crawler_service
```

## 🎨 Access the Dashboard

Open your browser and navigate to:

**http://localhost:3000/dashboard**

You should see the retro Windows-themed dashboard with:
- 🕷️ Web Crawler Monitor
- 🤖 AI Agent Status
- 📡 Live Updates Feed
- 📊 Statistics Cards

## 🧪 Test the Platform

### 1. Test the API

```bash
# Check API health
curl http://localhost:8080/

# Get crawler status
curl http://localhost:8080/api/crawler/status

# List agent types
curl http://localhost:8080/api/agents/types

# Get live updates
curl http://localhost:8080/api/live-updates
```

### 2. Run a Crawler

**Via API:**
```bash
# Run all crawlers
curl -X POST http://localhost:8080/api/crawler/run-all

# Run specific crawler
curl -X POST http://localhost:8080/api/crawler/run/shopgoodwill
```

**Via Python:**
```python
import asyncio
from backend.crawler.crawler_service import CrawlerService

async def test_crawler():
    crawler = CrawlerService()
    results = await crawler.crawl_all()
    for result in results:
        print(f"{result.target_name}: {result.items_found} items")

asyncio.run(test_crawler())
```

### 3. Test AI Agents

```bash
# Create an agent job
curl -X POST http://localhost:8080/api/agents/jobs \
  -H "Content-Type: application/json" \
  -d '{"agent_type": "metadata_enricher", "input_data": {"batch_size": 10}}'

# List agent jobs
curl http://localhost:8080/api/agents/jobs
```

## 🎯 Common Tasks

### Configure Crawler Targets

Edit `config/crawler.toml`:

```toml
[[targets]]
name = "my_custom_site"
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

### Configure AI Agents

Edit `crew/crewai.yaml`:

```yaml
agents:
  my_custom_agent:
    role: "Custom Agent"
    goal: "Process custom data"
    tools: [openai_api, custom_tool]

workers:
  my_worker:
    agent: my_custom_agent
    schedule: "*/30 * * * *"
    task: "Process queue"
```

### Upload Images to Storage

```python
from backend.storage import MinIOClient
from io import BytesIO

# Initialize client
client = MinIOClient()

# Upload image
with open('product.jpg', 'rb') as f:
    url = client.upload_file(
        'arbfinder-images',
        'product.jpg',
        f,
        'image/jpeg'
    )
    print(f"Uploaded: {url}")
```

## 📊 Monitoring

### View Dashboard Statistics

Visit: http://localhost:3000/dashboard

The dashboard shows:
- Total items crawled
- Active agents
- Success rates
- Queue sizes
- Live activity feed

### View API Logs

```bash
# If running with uvicorn
# Logs appear in terminal

# If using Docker
docker-compose logs -f backend
```

### Check Database

```bash
# PostgreSQL
psql -d arbfinder -c "SELECT COUNT(*) FROM listings;"

# MySQL
mysql -u root -p arbfinder -e "SELECT COUNT(*) FROM listings;"

# Or use Prisma Studio
npx prisma studio
```

## 🔧 Troubleshooting

### Dashboard not loading?

1. Check backend is running: `curl http://localhost:8080/`
2. Check frontend is running: `curl http://localhost:3000/`
3. Check browser console for errors
4. Verify CORS settings in `.env`

### Crawler not finding items?

1. Check CSS selectors in `config/crawler.toml`
2. Test selectors with browser dev tools
3. Check crawler logs for errors
4. Verify site allows crawling (robots.txt)

### Database connection errors?

1. Verify database is running
2. Check `DATABASE_URL` in `.env`
3. Test connection: `npx prisma db push`
4. Check database credentials

### AI agents not running?

1. Verify `OPENAI_API_KEY` in `.env`
2. Check agent configuration in `crew/crewai.yaml`
3. Look for errors in API logs
4. Test OpenAI API connection

### Docker issues?

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

## 🎓 Next Steps

1. **Read the Platform Guide**: See [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) for detailed documentation
2. **Configure Crawlers**: Add your own target sites in `config/crawler.toml`
3. **Customize Agents**: Modify `crew/crewai.yaml` for your workflow
4. **Deploy to Production**: See deployment section in PLATFORM_GUIDE.md
5. **Set up Cloudflare**: Deploy workers and configure R2 storage

## 📚 Additional Resources

- [README.md](README.md) - Project overview
- [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) - Comprehensive platform documentation
- [DEVELOPER.md](../development/DEVELOPER.md) - Development guide
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines

## 💬 Support

- Issues: https://github.com/cbwinslow/arbfinder-suite/issues
- Discussions: https://github.com/cbwinslow/arbfinder-suite/discussions

## 🚀 Happy Arbitrage Hunting!

The ArbFinder platform is now ready to help you find deals across multiple marketplaces with the power of AI and automation!
