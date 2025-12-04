#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional

import stripe
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import new routers
try:
    from .crawler import router as crawler_router
    from .agents import router as agents_router
    from .live_updates import router as live_updates_router
except ImportError:
    crawler_router = None
    agents_router = None
    live_updates_router = None

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app = FastAPI(
    title="ArbFinder API",
    description="API for finding arbitrage opportunities across marketplaces",
    version="0.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Include new routers
if crawler_router:
    app.include_router(crawler_router)
if agents_router:
    app.include_router(agents_router)
if live_updates_router:
    app.include_router(live_updates_router)


class Listing(BaseModel):
    title: str
    price: float
    url: str
    currency: str = "USD"
    source: str = "manual"


class ListingFilter(BaseModel):
    """Filter parameters for listing search."""

    source: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "ArbFinder API",
        "version": "0.3.0",
        "endpoints": {
            "listings": "/api/listings",
            "search": "/api/listings/search",
            "statistics": "/api/statistics",
            "comps": "/api/comps",
        },
    }


@app.get("/api/listings")
def get_listings(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    order_by: str = Query("ts", regex="^(ts|price|title)$"),
) -> Dict[str, Any]:
    """Get listings with pagination and filtering."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Build query with filters
    where_clauses = []
    params = []

    if source:
        where_clauses.append("source = ?")
        params.append(source)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Get total count
    count_query = f"SELECT COUNT(*) FROM listings {where_sql}"
    total = c.execute(count_query, params).fetchone()[0]

    # Get listings
    query = f"""
        SELECT source, url, title, price, currency, condition, ts, meta_json 
        FROM listings {where_sql}
        ORDER BY {order_by} DESC 
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    rows = []
    for r in c.execute(query, params):
        rows.append(
            {
                "source": r[0],
                "url": r[1],
                "title": r[2],
                "price": r[3],
                "currency": r[4],
                "condition": r[5],
                "ts": r[6],
                "meta": json.loads(r[7] or "{}"),
            }
        )

    conn.close()

    return {"total": total, "limit": limit, "offset": offset, "count": len(rows), "data": rows}


@app.post("/api/listings")
def create_listing(item: Listing) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO listings (source,url,title,price,currency,condition,ts,meta_json) VALUES (?,?,?,?,?,?,strftime('%s','now'),?)",
        (item.source, item.url, item.title, item.price, item.currency, "manual", json.dumps({})),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/api/listings/search")
def search_listings(
    q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=200)
) -> List[Dict[str, Any]]:
    """Search listings by title."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = """
        SELECT source, url, title, price, currency, condition, ts, meta_json 
        FROM listings 
        WHERE title LIKE ? 
        ORDER BY ts DESC 
        LIMIT ?
    """

    rows = []
    for r in c.execute(query, (f"%{q}%", limit)):
        rows.append(
            {
                "source": r[0],
                "url": r[1],
                "title": r[2],
                "price": r[3],
                "currency": r[4],
                "condition": r[5],
                "ts": r[6],
                "meta": json.loads(r[7] or "{}"),
            }
        )

    conn.close()
    return rows


@app.get("/api/statistics")
def get_statistics() -> Dict[str, Any]:
    """Get database statistics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    stats = {}

    # Total listings
    stats["total_listings"] = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]

    # Listings by source
    stats["by_source"] = {}
    for row in c.execute("SELECT source, COUNT(*) FROM listings GROUP BY source"):
        stats["by_source"][row[0]] = row[1]

    # Price statistics
    price_stats = c.execute(
        "SELECT AVG(price), MIN(price), MAX(price) FROM listings WHERE price > 0"
    ).fetchone()

    if price_stats and price_stats[0]:
        stats["price_stats"] = {
            "average": round(price_stats[0], 2),
            "min": round(price_stats[1], 2),
            "max": round(price_stats[2], 2),
        }

    # Total comps
    stats["total_comps"] = c.execute("SELECT COUNT(*) FROM comps").fetchone()[0]

    # Recent listings (last 24 hours)
    import time

    day_ago = time.time() - 86400
    stats["recent_listings"] = c.execute(
        "SELECT COUNT(*) FROM listings WHERE ts > ?", (day_ago,)
    ).fetchone()[0]

    conn.close()
    return stats


@app.get("/api/comps")
def get_comps(limit: int = Query(100, ge=1, le=500)) -> List[Dict[str, Any]]:
    """Get comparable prices."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = """
        SELECT key_title, avg_price, median_price, count, ts 
        FROM comps 
        ORDER BY ts DESC 
        LIMIT ?
    """

    rows = []
    for r in c.execute(query, (limit,)):
        rows.append(
            {
                "title": r[0],
                "avg_price": round(r[1], 2),
                "median_price": round(r[2], 2),
                "count": r[3],
                "timestamp": r[4],
            }
        )

    conn.close()
    return rows


@app.get("/api/comps/search")
def search_comps(q: str = Query(..., min_length=1)) -> List[Dict[str, Any]]:
    """Search comparable prices by title."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = """
        SELECT key_title, avg_price, median_price, count, ts 
        FROM comps 
        WHERE key_title LIKE ? 
        ORDER BY ts DESC 
        LIMIT 50
    """

    rows = []
    for r in c.execute(query, (f"%{q}%",)):
        rows.append(
            {
                "title": r[0],
                "avg_price": round(r[1], 2),
                "median_price": round(r[2], 2),
                "count": r[3],
                "timestamp": r[4],
            }
        )

    conn.close()
    return rows


@app.post("/api/stripe/create-checkout-session")
def create_checkout_session(
    title: str = Query(...), price: float = Query(...), currency: str = Query("usd")
):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=400, detail="Stripe not configured")
    amount = int(round(price * 100))
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": title},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }
        ],
        success_url=f"{FRONTEND_ORIGIN}/success",
        cancel_url=f"{FRONTEND_ORIGIN}/cancel",
    )
    return {"url": session.url}
