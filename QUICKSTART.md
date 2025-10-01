# Quick Start Guide

## 1. Installation

```bash
# Clone the repository
git clone https://github.com/cbwinslow/arbfinder-suite.git
cd arbfinder-suite

# Install backend dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 2. First Run (Interactive Mode)

The easiest way to get started is with interactive mode:

```bash
source .venv/bin/activate
python3 backend/arb_finder.py --interactive
```

This will guide you through:
- Entering a search query
- Selecting providers
- Setting discount threshold
- Exporting results

## 3. Run the API Server

In a new terminal:

```bash
source .venv/bin/activate
uvicorn backend.api.main:app --reload --port 8080
```

Visit http://localhost:8080 to see API documentation.

## 4. Run the Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 to see the web interface.

## 5. Example Searches

### Find GPU deals
```bash
python3 backend/arb_finder.py "RTX 3060" --csv gpu_deals.csv
```

### Find camera deals with high discount threshold
```bash
python3 backend/arb_finder.py "Canon EOS" --threshold-pct 30 --csv camera_deals.csv
```

### Watch for new deals continuously
```bash
python3 backend/arb_finder.py "iPad Pro" --watch --watch-interval 1800
```

### Use specific providers
```bash
python3 backend/arb_finder.py "vintage watches" \
  --providers shopgoodwill,govdeals \
  --threshold-pct 25 \
  --csv watches.csv
```

## 6. Save Configuration

Save your preferred settings:

```bash
python3 backend/arb_finder.py "RTX 3060" \
  --threshold-pct 25 \
  --providers shopgoodwill,govdeals,governmentsurplus \
  --save-config
```

Then reuse them:

```bash
python3 backend/arb_finder.py --config ~/.arbfinder_config.json
```

## 7. View Results

### In Terminal (with Rich formatting)
Results are automatically displayed when using the CLI

### Via Web UI
1. Start the API server
2. Start the frontend
3. Navigate to http://localhost:3000
4. View listings and search results

### CSV/JSON Export
Results are saved to the specified file path:
```bash
python3 backend/arb_finder.py "iPhone 13" --csv iphone_deals.csv --json iphone_deals.json
```

## 8. Stripe Integration (Optional)

To enable checkout functionality:

```bash
export STRIPE_SECRET_KEY=sk_test_...
export FRONTEND_ORIGIN=http://localhost:3000
uvicorn backend.api.main:app --reload --port 8080
```

## 9. Database Location

By default, data is stored in:
- SQLite database: `~/.arb_finder.sqlite3`
- Config file: `~/.arbfinder_config.json`
- Logs: `/tmp/ArbFinder.log`

## 10. Troubleshooting

### "Module not found" errors
```bash
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Frontend errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database errors
```bash
rm ~/.arb_finder.sqlite3  # This will delete all data
python3 backend/arb_finder.py "test" --csv test.csv  # Recreate database
```

## Tips

1. **Use quiet mode** for automated scripts: `--quiet`
2. **Enable verbose logging** for debugging: `--verbose`
3. **Set appropriate intervals** for watch mode to respect rate limits
4. **Use filters** to focus on specific sources: `--providers shopgoodwill`
5. **Adjust thresholds** based on category margins: `--threshold-pct 15`

## Next Steps

- Explore the [API documentation](http://localhost:8080/docs)
- Check out the [README](README.md) for advanced features
- View comparable prices at http://localhost:3000/comps
- Set up watch mode for continuous monitoring
