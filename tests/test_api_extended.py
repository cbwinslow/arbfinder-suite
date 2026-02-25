"""Extended tests for API endpoints - testing additional routes and edge cases."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_db_path():
    """Create a test database with sample data."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS listings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source TEXT, url TEXT UNIQUE, title TEXT, price REAL,
          currency TEXT, condition TEXT, ts REAL, meta_json TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS comps (
          key_title TEXT PRIMARY KEY, avg_price REAL, median_price REAL,
          count INTEGER, ts REAL
        )
    """)

    now = time.time()
    c.executemany(
        "INSERT INTO listings (source, url, title, price, currency, condition, ts, meta_json) VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                "ebay",
                "http://ebay.com/1",
                "RTX 3060 Graphics Card",
                250.0,
                "USD",
                "sold",
                now,
                "{}",
            ),
            (
                "shopgoodwill",
                "http://sg.com/1",
                "RTX 3060 GPU",
                180.0,
                "USD",
                "live",
                now - 100,
                "{}",
            ),
            (
                "govdeals",
                "http://gd.com/1",
                "iPad Pro 12.9 Inch",
                300.0,
                "USD",
                "live",
                now - 200,
                "{}",
            ),
            (
                "govdeals",
                "http://gd.com/2",
                "MacBook Pro M1",
                700.0,
                "USD",
                "live",
                now - 300,
                "{}",
            ),
        ],
    )
    c.executemany(
        "INSERT INTO comps (key_title, avg_price, median_price, count, ts) VALUES (?,?,?,?,?)",
        [
            ("rtx 3060", 300.0, 290.0, 5, now),
            ("ipad pro 12.9 inch", 450.0, 440.0, 3, now),
        ],
    )
    conn.commit()
    conn.close()

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="module")
def client(test_db_path):
    """Create test client with patched DB_PATH."""
    import backend.api.main as api_main
    from backend.api.main import app

    with patch.object(api_main, "DB_PATH", test_db_path):
        yield TestClient(app)


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_name(self, client):
        data = client.get("/").json()
        assert "name" in data
        assert "ArbFinder" in data["name"]

    def test_root_includes_version(self, client):
        data = client.get("/").json()
        assert "version" in data

    def test_root_includes_endpoints(self, client):
        data = client.get("/").json()
        assert "endpoints" in data


class TestHealthzEndpoint:
    """Tests for the /healthz liveness probe endpoint."""

    def test_healthz_returns_200(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_returns_ok_status(self, client):
        data = client.get("/healthz").json()
        assert data == {"status": "ok"}


class TestListingsEndpoint:
    """Tests for /api/listings endpoint."""

    def test_get_listings_returns_200(self, client):
        response = client.get("/api/listings")
        assert response.status_code == 200

    def test_get_listings_structure(self, client):
        data = client.get("/api/listings").json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "count" in data
        assert "data" in data

    def test_get_listings_has_data(self, client):
        data = client.get("/api/listings").json()
        assert data["total"] >= 4
        assert len(data["data"]) >= 4

    def test_get_listings_pagination_limit(self, client):
        response = client.get("/api/listings?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert len(data["data"]) == 2

    def test_get_listings_pagination_offset(self, client):
        all_data = client.get("/api/listings").json()
        offset_data = client.get("/api/listings?offset=2").json()
        assert offset_data["offset"] == 2
        # First item with offset should differ from first item without
        if all_data["data"] and offset_data["data"]:
            assert all_data["data"][0]["url"] != offset_data["data"][0]["url"]

    def test_get_listings_filter_by_source(self, client):
        response = client.get("/api/listings?source=govdeals")
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]:
            assert item["source"] == "govdeals"

    def test_get_listings_order_by_price(self, client):
        response = client.get("/api/listings?order_by=price")
        assert response.status_code == 200

    def test_get_listings_order_by_title(self, client):
        response = client.get("/api/listings?order_by=title")
        assert response.status_code == 200

    def test_get_listings_invalid_order_by(self, client):
        response = client.get("/api/listings?order_by=invalid_field")
        assert response.status_code == 422

    def test_get_listings_limit_too_high(self, client):
        response = client.get("/api/listings?limit=1000")
        assert response.status_code == 422

    def test_get_listings_limit_zero(self, client):
        response = client.get("/api/listings?limit=0")
        assert response.status_code == 422

    def test_get_listings_negative_offset(self, client):
        response = client.get("/api/listings?offset=-1")
        assert response.status_code == 422

    def test_listing_item_has_required_fields(self, client):
        data = client.get("/api/listings").json()
        if data["data"]:
            item = data["data"][0]
            for field in ["source", "url", "title", "price", "currency", "condition", "ts"]:
                assert field in item


class TestCreateListing:
    """Tests for POST /api/listings endpoint."""

    def test_create_listing_success(self, client):
        payload = {
            "title": "Test GPU",
            "price": 199.99,
            "url": "http://test.com/test-gpu-unique-12345",
            "currency": "USD",
            "source": "test",
        }
        response = client.post("/api/listings", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True

    def test_create_listing_minimal(self, client):
        payload = {
            "title": "Minimal Item",
            "price": 50.0,
            "url": "http://test.com/minimal-unique-54321",
        }
        response = client.post("/api/listings", json=payload)
        assert response.status_code == 200

    def test_create_listing_missing_required_fields(self, client):
        response = client.post("/api/listings", json={"title": "No price or URL"})
        assert response.status_code == 422


class TestSearchListings:
    """Tests for /api/listings/search endpoint."""

    def test_search_returns_results(self, client):
        response = client.get("/api/listings/search?q=RTX")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_search_no_results(self, client):
        response = client.get("/api/listings/search?q=ZZZNOMATCH12345")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_case_insensitive(self, client):
        lower = client.get("/api/listings/search?q=rtx").json()
        upper = client.get("/api/listings/search?q=RTX").json()
        # SQLite LIKE is case-insensitive for ASCII
        assert len(lower) == len(upper)

    def test_search_missing_query(self, client):
        response = client.get("/api/listings/search")
        assert response.status_code == 422

    def test_search_with_limit(self, client):
        response = client.get("/api/listings/search?q=GPU&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1

    def test_search_items_have_required_fields(self, client):
        response = client.get("/api/listings/search?q=RTX")
        data = response.json()
        if data:
            item = data[0]
            for field in ["source", "url", "title", "price"]:
                assert field in item


class TestStatisticsEndpoint:
    """Tests for /api/statistics endpoint."""

    def test_statistics_returns_200(self, client):
        response = client.get("/api/statistics")
        assert response.status_code == 200

    def test_statistics_has_required_fields(self, client):
        data = client.get("/api/statistics").json()
        assert "total_listings" in data
        assert "by_source" in data
        assert "total_comps" in data
        assert "recent_listings" in data

    def test_statistics_total_listings_positive(self, client):
        data = client.get("/api/statistics").json()
        assert data["total_listings"] >= 4

    def test_statistics_by_source(self, client):
        data = client.get("/api/statistics").json()
        assert isinstance(data["by_source"], dict)
        assert "govdeals" in data["by_source"]

    def test_statistics_price_stats(self, client):
        data = client.get("/api/statistics").json()
        if "price_stats" in data:
            assert "average" in data["price_stats"]
            assert "min" in data["price_stats"]
            assert "max" in data["price_stats"]


class TestCompsEndpoint:
    """Tests for /api/comps endpoint."""

    def test_comps_returns_200(self, client):
        response = client.get("/api/comps")
        assert response.status_code == 200

    def test_comps_returns_list(self, client):
        data = client.get("/api/comps").json()
        assert isinstance(data, list)

    def test_comps_has_data(self, client):
        data = client.get("/api/comps").json()
        assert len(data) >= 2

    def test_comps_item_structure(self, client):
        data = client.get("/api/comps").json()
        if data:
            item = data[0]
            assert "title" in item
            assert "avg_price" in item
            assert "median_price" in item
            assert "count" in item

    def test_comps_with_limit(self, client):
        response = client.get("/api/comps?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1


class TestCompsSearch:
    """Tests for /api/comps/search endpoint."""

    def test_comps_search_returns_results(self, client):
        response = client.get("/api/comps/search?q=rtx")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_comps_search_no_results(self, client):
        response = client.get("/api/comps/search?q=ZZZNOMATCH99999")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_comps_search_missing_query(self, client):
        response = client.get("/api/comps/search")
        assert response.status_code == 422


class TestStripeEndpoint:
    """Tests for Stripe checkout session endpoint."""

    def test_stripe_not_configured_returns_400(self, client):
        # Without STRIPE_SECRET_KEY, should return 400
        response = client.post(
            "/api/stripe/create-checkout-session?title=Test&price=50.0&currency=usd"
        )
        assert response.status_code == 400
        assert "Stripe not configured" in response.json()["detail"]


class TestInvalidEndpoints:
    """Tests for invalid/non-existent endpoints."""

    def test_nonexistent_endpoint_returns_404(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_api_nonexistent_returns_404(self, client):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
