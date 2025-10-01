# ArbFinder Suite

## Features
- Async crawler for ShopGoodwill, GovDeals, GovernmentSurplus (+ eBay sold comps)
- Manual importer for Facebook Marketplace (CSV/JSON)
- FastAPI backend for listings + Stripe checkout
- Next.js frontend to view/add listings and pay
- CrewAI config for research → pricing → listing → crosslisting

## Run Backend
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.api.main:app --reload --port 8080
```

## Run Crawler
```bash
python3 backend/arb_finder.py "RTX 3060" --csv rtx_deals.csv --providers shopgoodwill,govdeals,governmentsurplus --threshold-pct 25
```

### Manual Import (Facebook Marketplace export)
```bash
python3 backend/arb_finder.py "ignored" --providers manual --manual-path /path/to/fb_export.csv --csv fb_deals.csv
```

## Run Frontend
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```
Set `NEXT_PUBLIC_API_BASE` to the backend URL.

## Payments
Set `STRIPE_SECRET_KEY` and `FRONTEND_ORIGIN` in backend env. The UI will request a Checkout session from `/api/stripe/create-checkout-session`.

## Notes
- Always respect robots.txt and site ToS.
- Prefer official APIs for stability (eBay, Reverb, Amazon Associates).
- Facebook Marketplace: use manual export/import; do not scrape.

## Roadmap
- Add Reverb & Mercari providers (sold + live)
- Add time-decay weighted comps and per-category fees
- Add AI: automatic title/description generation with templates
- Add OAuth + multi-user inventory
