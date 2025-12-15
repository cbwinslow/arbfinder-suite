# ArbFinder Suite

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Version 0.4.0** - Enhanced CLI, TypeScript SDK, and Developer Tools

## Features

- 🔍 Async crawler for ShopGoodwill, GovDeals, GovernmentSurplus (+ eBay sold comps)
- 📊 Interactive TUI with rich terminal output and progress bars
- 🖥️ **NEW**: Enhanced CLI with subcommands (search, watch, config, db, server)
- 🎨 **NEW**: Bubbletea TUI - Multi-pane interactive interface with database integration
- 📦 **NEW**: TypeScript/Node.js SDK and CLI tools
- 🧪 **NEW**: Comprehensive test suite with pytest
- 🐳 **NEW**: Docker and Docker Compose support
- 📁 Manual importer for Facebook Marketplace (CSV/JSON)
- 🚀 FastAPI backend with search, filtering, and statistics
- 💎 Enhanced Next.js frontend with modern UI
- 🤖 CrewAI config for research → pricing → listing → crosslisting
- 📈 Real-time statistics and analytics
- 🎨 Beautiful dark mode interface with gradients
- 🛠️ **NEW**: Developer tools (Makefile, pre-commit hooks, VS Code config)

## Quick Start

### Using pip (Recommended)

```bash
# Install from source
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite
pip install -e .

# Run CLI
arbfinder --version
arbfinder search "RTX 3060" --csv deals.csv
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# - API: http://localhost:8080
# - Frontend: http://localhost:3000
```

## Installation

### Backend Setup

```bash
# Clone repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test]"

# Or install just the dependencies
pip install -r backend/requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### TypeScript Packages (Optional)

```bash
# Install and build client library
cd packages/client
npm install
npm run build

# Install and build CLI tool
cd ../cli
npm install
npm run build
npm link  # Make available globally
```

## Usage

### Enhanced CLI (New!)

The new CLI provides a cleaner interface with subcommands:

```bash
# Search for deals
arbfinder search "RTX 3060" --csv deals.csv

# Watch for new deals
arbfinder watch "iPad Pro" --interval 1800

# Manage configuration
arbfinder config show
arbfinder config set threshold_pct 30.0

# Database operations
arbfinder db stats
arbfinder db backup
arbfinder db clean --days 30

# Run API server
arbfinder server --port 8080 --reload

# Generate shell completions
arbfinder completion bash > ~/.arbfinder-completion.bash
source ~/.arbfinder-completion.bash
```

### TypeScript CLI (New!)

```bash
# Using the TypeScript CLI
arbfinder-ts list --limit 20
arbfinder-ts search "RTX 3080"
arbfinder-ts stats
arbfinder-ts comps "iPad"

# Connect to remote API
arbfinder-ts --api-url https://api.example.com list
```

### Interactive TUI Mode (Python)

Run the crawler in interactive mode with rich terminal UI:

```bash
python3 backend/arb_finder.py --interactive
```

or simply:

```bash
python3 backend/arb_finder.py -i
```

This will prompt you for:
- Search query
- Provider selection
- Discount threshold
- Export options

### Bubbletea TUI (Go - Advanced)

Run the advanced multi-pane TUI built with Bubbletea:

```bash
make build-tui  # Build the TUI
make run-tui    # Run the TUI
```

Or directly:

```bash
cd tui
go run .
```

Features:
- **Multiple Panes**: Search, Results, Statistics, Configuration
- **Database Integration**: Save searches, configs, and price history
- **API Integration**: Real-time data from the backend server
- **Keyboard Navigation**: Full keyboard-driven interface
- **Data Persistence**: SQLite database for local storage

See [tui/README.md](tui/README.md) for detailed TUI documentation.

### Command Line Mode

Run with specific parameters:

```bash
python3 backend/arb_finder.py "RTX 3060" \
  --csv rtx_deals.csv \
  --providers shopgoodwill,govdeals,governmentsurplus \
  --threshold-pct 25
```

### CLI Options

- `-i, --interactive` - Run in interactive TUI mode
- `-q, --quiet` - Suppress progress output
- `-v, --verbose` - Enable verbose logging
- `-w, --watch` - Enable watch mode (continuous monitoring)
- `--watch-interval SEC` - Watch mode interval in seconds (default: 3600)
- `--config FILE` - Path to config file (default: ~/.arbfinder_config.json)
- `--save-config` - Save current arguments to config file
- `--csv FILE` - Export results to CSV
- `--json FILE` - Export results to JSON
- `--threshold-pct PCT` - Minimum discount percentage (default: 20.0)
- `--providers LIST` - Comma-separated provider list
- `--sim-threshold NUM` - Similarity threshold 0-100 (default: 86)
- `--live-limit NUM` - Max live listings per provider (default: 80)
- `--comp-limit NUM` - Max sold comps to fetch (default: 150)

### Watch Mode

Monitor for deals continuously:

```bash
python3 backend/arb_finder.py "RTX 3060" --watch --watch-interval 1800
```

This will check for new deals every 30 minutes and notify you when deals exceeding your threshold are found.

### Configuration Files

Create a config file to save your preferences:

```bash
# Save current settings
python3 backend/arb_finder.py "RTX 3060" --threshold-pct 25 --save-config

# Use saved config
python3 backend/arb_finder.py --config ~/.arbfinder_config.json
```

See `config.example.json` for a complete example.

### Manual Import (Facebook Marketplace)

Export your Facebook Marketplace listings and import them:

```bash
python3 backend/arb_finder.py "ignored" \
  --providers manual \
  --manual-path /path/to/fb_export.csv \
  --csv fb_deals.csv
```

## API Server

### Start the API Server

```bash
uvicorn backend.api.main:app --reload --port 8080
```

### API Endpoints

- `GET /` - API information
- `GET /api/listings` - Get listings with pagination
  - Query params: `limit`, `offset`, `source`, `order_by`
- `GET /api/listings/search?q=query` - Search listings
- `POST /api/listings` - Create new listing
- `GET /api/statistics` - Get database statistics
- `GET /api/comps` - Get comparable prices
- `GET /api/comps/search?q=query` - Search comparables
- `POST /api/stripe/create-checkout-session` - Stripe checkout

### Example API Calls

```bash
# Get statistics
curl http://localhost:8080/api/statistics

# Search listings
curl http://localhost:8080/api/listings/search?q=nvidia

# Get listings with pagination
curl "http://localhost:8080/api/listings?limit=10&offset=0&order_by=price"
```

## TypeScript/Node.js SDK

Use the official SDK to integrate ArbFinder into your Node.js applications:

```typescript
import { ArbFinderClient } from '@arbfinder/client';

// Create a client
const client = new ArbFinderClient({
  baseURL: 'http://localhost:8080',
  timeout: 30000,
});

// Get listings
const listings = await client.getListings({
  limit: 10,
  order_by: 'ts',
});

// Search listings
const results = await client.searchListings('RTX 3060');

// Get statistics
const stats = await client.getStatistics();

// Get comparable prices
const comps = await client.getComps();
```

See the [client package README](packages/client/README.md) for full documentation.

## Frontend

### Development Mode

```bash
cd frontend
cp .env.example .env.local  # Create if it doesn't exist
echo "NEXT_PUBLIC_API_BASE=http://localhost:8080" > .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Features

- 🎨 Modern, responsive design with Tailwind CSS
- 🔍 Real-time search and filtering
- 📊 Statistics dashboard
- 🎯 Sort by date, price, or title
- 📱 Mobile-friendly interface
- 💳 Stripe checkout integration
- ⚡ Fast, optimized performance

### Production Build

```bash
cd frontend
npm run build
npm start
```

## Environment Variables

### Backend

- `ARBF_DB` - Database path (default: `~/.arb_finder.sqlite3`)
- `STRIPE_SECRET_KEY` - Stripe API key for payments
- `FRONTEND_ORIGIN` - Frontend URL for CORS (default: `http://localhost:3000`)

### Frontend

- `NEXT_PUBLIC_API_BASE` - Backend API URL (default: `http://localhost:8080`)

## Payments

Set `STRIPE_SECRET_KEY` in backend environment. The UI will request a Checkout session from `/api/stripe/create-checkout-session`.

```bash
export STRIPE_SECRET_KEY=sk_test_...
export FRONTEND_ORIGIN=http://localhost:3000
uvicorn backend.api.main:app --reload --port 8080
```

## Architecture

```
arbfinder-suite/
├── backend/                # Python backend
│   ├── __init__.py         # Package initialization
│   ├── arb_finder.py       # Core arbitrage finder
│   ├── cli.py              # Enhanced CLI with subcommands (NEW)
│   ├── tui.py              # Rich TUI components
│   ├── config.py           # Configuration management
│   ├── utils.py            # Database utilities
│   ├── watch.py            # Watch mode
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py         # FastAPI server
│   └── requirements.txt
├── tui/                    # Go Bubbletea TUI (NEW)
│   ├── main.go             # Main TUI application
│   ├── database.go         # SQLite database layer
│   ├── api_client.go       # API client
│   ├── search_pane.go      # Search interface
│   ├── results_pane.go     # Results display
│   ├── stats_pane.go       # Statistics view
│   ├── config_pane.go      # Configuration manager
│   ├── go.mod              # Go dependencies
│   └── README.md           # TUI documentation
├── frontend/               # Next.js frontend
│   ├── app/
│   │   ├── page.tsx        # Main UI
│   │   ├── layout.tsx      # Layout
│   │   ├── globals.css     # Styles
│   │   └── comps/
│   │       └── page.tsx    # Comps viewer
│   └── package.json
├── packages/               # TypeScript/Node.js packages (NEW)
│   ├── client/             # API client SDK
│   │   ├── src/
│   │   │   └── index.ts
│   │   └── package.json
│   └── cli/                # TypeScript CLI
│       ├── src/
│       │   └── cli.ts
│       └── package.json
├── tests/                  # Test suite (NEW)
│   ├── test_cli.py
│   └── test_config.py
├── crew/
│   └── crewai.yaml         # AI agent config
├── exporters/
│   └── fb_marketplace_template.csv
├── pyproject.toml          # Python project config (NEW)
├── Makefile                # Development tasks (NEW)
├── Dockerfile              # Docker image (NEW)
├── docker-compose.yml      # Docker Compose config (NEW)
└── DEVELOPER.md            # Developer guide (NEW)
```

## Database Schema

### Listings Table

```sql
CREATE TABLE listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  url TEXT UNIQUE,
  title TEXT,
  price REAL,
  currency TEXT,
  condition TEXT,
  ts REAL,
  meta_json TEXT
);
```

### Comps Table

```sql
CREATE TABLE comps (
  key_title TEXT PRIMARY KEY,
  avg_price REAL,
  median_price REAL,
  count INTEGER,
  ts REAL
);
```

## Notes

- Always respect robots.txt and site ToS
- Prefer official APIs for stability (eBay, Reverb, Amazon Associates)
- Facebook Marketplace: use manual export/import; do not scrape
- Rate limiting is built-in to be polite to servers
- All HTTP requests use retry logic with exponential backoff

## Roadmap

### Completed ✅
- [x] Interactive TUI with Rich library
- [x] Progress bars and colored output
- [x] Watch mode for continuous monitoring
- [x] Configuration file support
- [x] Enhanced API with search and filtering
- [x] Statistics dashboard
- [x] Comparable prices viewer
- [x] Modern responsive UI
- [x] **Enhanced CLI with subcommands** (v0.4.0)
- [x] **TypeScript/Node.js SDK** (v0.4.0)
- [x] **Comprehensive test suite** (v0.4.0)
- [x] **Docker support** (v0.4.0)
- [x] **Developer tools and documentation** (v0.4.0)

### In Progress 🚧
- [ ] Add Reverb & Mercari providers (sold + live)
- [ ] Add time-decay weighted comps and per-category fees
- [ ] Add AI: automatic title/description generation with templates
- [ ] Increase test coverage to 80%+

### Planned 📋
- [ ] Add OAuth + multi-user inventory
- [ ] Add email/SMS notifications for deals
- [ ] Add price history tracking and charts
- [ ] Add image preview for listings
- [ ] Add scheduled crawling with cron
- [ ] Add export to PDF/Excel formats
- [ ] Add dark/light mode toggle
- [ ] Add favorites/watchlist feature
- [ ] Add browser extension for quick price checking
- [ ] Add mobile app (React Native)
- [ ] API rate limiting and authentication
- [ ] GraphQL API endpoint
- [ ] WebSocket support for real-time updates

## Development

### Quick Start

```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run tests
pytest

# Format code
black backend/

# Lint code
flake8 backend/

# Run with make
make test
make lint
make format
```

### Using Makefile

The project includes a Makefile for common tasks:

```bash
make help           # Show available commands
make install        # Install production dependencies
make install-dev    # Install development dependencies
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Run linters
make format         # Format code
make clean          # Clean build artifacts
make run-server     # Run API server
make run-frontend   # Run frontend dev server
make docker-build   # Build Docker image
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code formatting and linting:

```bash
pip install pre-commit
pre-commit install
```

Hooks will run automatically on `git commit`.

### VS Code

The repository includes VS Code settings for:
- Python debugging
- Test discovery
- Code formatting
- Linting

See `.vscode/settings.json` for configuration.

For detailed development information, see [DEVELOPER.md](DEVELOPER.md).

## Documentation

Comprehensive documentation is available:

### Getting Started
- **[README.md](README.md)** - This file (overview and quick start)
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Step-by-step implementation roadmap

### Project Information
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current project status and metrics
- **[TASKS.md](TASKS.md)** - Detailed task list with microgoals and tests
- **[FEATURES_OVERVIEW.md](FEATURES_OVERVIEW.md)** - Complete feature descriptions

### Technical Documentation
- **[AGENTS.md](AGENTS.md)** - AI agent system architecture and usage
- **[SRS.md](SRS.md)** - Software requirements specification
- **[RULES.md](RULES.md)** - Coding standards and conventions
- **[DEVELOPER.md](DEVELOPER.md)** - Development setup and workflow

### AI & Integration
- **[PROMPTS.md](PROMPTS.md)** - AI prompt library for various tasks
- **[MODEL_PROMPTS.md](MODEL_PROMPTS.md)** - Model-specific prompt optimization
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - GitHub Copilot configuration

### Setup Guides
- **Cloudflare Setup:** Run `scripts/cloudflare/setup.sh` for automated setup
- **OpenRouter Integration:** See `backend/lib/openrouter/` for SDK usage

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Follow code style (black, flake8)
7. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see LICENSE file for details
