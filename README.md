# ArbFinder Suite

**Version 0.3.0** - Enhanced UI, CLI, TUI, and API

## Features

- 🔍 Async crawler for ShopGoodwill, GovDeals, GovernmentSurplus (+ eBay sold comps)
- 📊 Interactive TUI with rich terminal output and progress bars
- 📁 Manual importer for Facebook Marketplace (CSV/JSON)
- 🚀 FastAPI backend with search, filtering, and statistics
- 💎 Enhanced Next.js frontend with modern UI
- 🤖 CrewAI config for research → pricing → listing → crosslisting
- 📈 Real-time statistics and analytics
- 🎨 Beautiful dark mode interface with gradients

## Installation

### Backend Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Usage

### Interactive TUI Mode (Recommended)

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
├── backend/
│   ├── arb_finder.py      # Main CLI with TUI
│   ├── tui.py             # Rich TUI components
│   ├── api/
│   │   └── main.py        # FastAPI server
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx       # Main UI
│   │   ├── layout.tsx     # Layout
│   │   └── globals.css    # Styles
│   └── package.json
├── crew/
│   └── crewai.yaml        # AI agent config
└── exporters/
    └── fb_marketplace_template.csv
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

### In Progress 🚧
- [ ] Add Reverb & Mercari providers (sold + live)
- [ ] Add time-decay weighted comps and per-category fees
- [ ] Add AI: automatic title/description generation with templates

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

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT License - see LICENSE file for details
