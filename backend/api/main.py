#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import os, json, sqlite3
from typing import Any, Dict, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe

DB_PATH = os.getenv("ARBF_DB", os.path.expanduser("~/.arb_finder.sqlite3"))
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

app = FastAPI(title="ArbFinder API")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN, "*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

class Listing(BaseModel):
    title: str
    price: float
    url: str
    currency: str = "USD"
    source: str = "manual"

@app.get("/api/listings")
def get_listings(limit: int = 100) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    q = "SELECT source,url,title,price,currency,condition,ts,meta_json FROM listings ORDER BY ts DESC LIMIT ?"
    rows = []
    for r in c.execute(q, (limit,)):
        rows.append({"source": r[0], "url": r[1], "title": r[2], "price": r[3], "currency": r[4], "condition": r[5], "ts": r[6], "meta": json.loads(r[7] or "{}")})
    conn.close(); return rows

@app.post("/api/listings")
def create_listing(item: Listing) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO listings (source,url,title,price,currency,condition,ts,meta_json) VALUES (?,?,?,?,?,?,strftime('%s','now'),?)",
        (item.source, item.url, item.title, item.price, item.currency, "manual", json.dumps({}))
    ); conn.commit(); conn.close()
    return {"ok": True}

@app.post("/api/stripe/create-checkout-session")
def create_checkout_session(title: str = Query(...), price: float = Query(...), currency: str = Query("usd")):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=400, detail="Stripe not configured")
    amount = int(round(price * 100))
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price_data": {"currency": currency, "product_data": {"name": title}, "unit_amount": amount}, "quantity": 1}],
        success_url=f"{FRONTEND_ORIGIN}/success",
        cancel_url=f"{FRONTEND_ORIGIN}/cancel",
    )
    return {"url": session.url}
