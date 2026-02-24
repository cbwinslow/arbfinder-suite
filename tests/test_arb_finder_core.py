"""Extended tests for core arb_finder module functions."""

from __future__ import annotations

import csv
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.arb_finder import (
    Comp,
    Listing,
    ManualImport,
    PoliteClient,
    _price_re,
    compute_comps,
    db_init,
    db_upsert_comp,
    db_upsert_listing,
    export_csv,
    export_json,
    match_comps_to_live,
    sqlite_conn,
)


@pytest.fixture
def temp_db():
    """Temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    db_init(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


class TestListing:
    """Tests for the Listing dataclass."""

    def test_listing_basic(self):
        listing = Listing("ebay", "http://example.com", "RTX 3060", 250.0)
        assert listing.source == "ebay"
        assert listing.url == "http://example.com"
        assert listing.title == "RTX 3060"
        assert listing.price == 250.0
        assert listing.currency == "USD"
        assert listing.condition == "unknown"

    def test_listing_full(self):
        listing = Listing(
            source="shopgoodwill",
            url="http://sg.com/item/1",
            title="iPad Pro 12.9",
            price=400.0,
            currency="USD",
            condition="live",
            meta={"q": "iPad Pro"},
        )
        assert listing.condition == "live"
        assert listing.meta["q"] == "iPad Pro"

    def test_listing_timestamp_default(self):
        listing = Listing("test", "http://test.com", "Item", 100.0)
        assert listing.timestamp is not None
        assert listing.timestamp > 0


class TestComp:
    """Tests for the Comp dataclass."""

    def test_comp_basic(self):
        comp = Comp("rtx 3060", 250.0, 240.0, 5)
        assert comp.key_title == "rtx 3060"
        assert comp.avg_price == 250.0
        assert comp.median_price == 240.0
        assert comp.count == 5


class TestSqliteConn:
    """Tests for sqlite_conn context manager."""

    def test_sqlite_conn_yields_connection(self, temp_db):
        with sqlite_conn(temp_db) as conn:
            assert conn is not None
            cursor = conn.cursor()
            result = cursor.execute("SELECT 1").fetchone()
            assert result[0] == 1

    def test_sqlite_conn_closes_on_exit(self, temp_db):
        with sqlite_conn(temp_db) as conn:
            pass
        # Connection should be closed - trying to use it should fail
        with pytest.raises(Exception):
            conn.execute("SELECT 1")


class TestDbInit:
    """Tests for db_init function."""

    def test_creates_listings_table(self, temp_db):
        conn = sqlite3.connect(temp_db)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = [t[0] for t in tables]
        assert "listings" in table_names

    def test_creates_comps_table(self, temp_db):
        conn = sqlite3.connect(temp_db)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = [t[0] for t in tables]
        assert "comps" in table_names

    def test_idempotent_init(self, temp_db):
        """Should not raise if tables already exist."""
        db_init(temp_db)  # Second init should not fail
        conn = sqlite3.connect(temp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        conn.close()
        assert count >= 2


class TestDbUpsertListing:
    """Tests for db_upsert_listing function."""

    def test_insert_listing(self, temp_db):
        listing = Listing("ebay", "http://ebay.com/1", "RTX 3060", 250.0)
        db_upsert_listing(temp_db, listing)

        conn = sqlite3.connect(temp_db)
        row = conn.execute("SELECT title, price FROM listings WHERE url=?",
                           ("http://ebay.com/1",)).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "RTX 3060"
        assert row[1] == 250.0

    def test_upsert_updates_existing(self, temp_db):
        listing1 = Listing("ebay", "http://ebay.com/1", "RTX 3060", 250.0)
        listing2 = Listing("ebay", "http://ebay.com/1", "RTX 3060 Updated", 200.0)
        db_upsert_listing(temp_db, listing1)
        db_upsert_listing(temp_db, listing2)

        conn = sqlite3.connect(temp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE url=?", ("http://ebay.com/1",)
        ).fetchone()[0]
        row = conn.execute(
            "SELECT title, price FROM listings WHERE url=?", ("http://ebay.com/1",)
        ).fetchone()
        conn.close()
        assert count == 1
        assert row[0] == "RTX 3060 Updated"
        assert row[1] == 200.0

    def test_insert_with_meta(self, temp_db):
        listing = Listing("ebay", "http://ebay.com/2", "iPad", 300.0, meta={"q": "iPad"})
        db_upsert_listing(temp_db, listing)

        conn = sqlite3.connect(temp_db)
        row = conn.execute(
            "SELECT meta_json FROM listings WHERE url=?", ("http://ebay.com/2",)
        ).fetchone()
        conn.close()
        assert row is not None
        meta = json.loads(row[0])
        assert meta["q"] == "iPad"


class TestDbUpsertComp:
    """Tests for db_upsert_comp function."""

    def test_insert_comp(self, temp_db):
        comp = Comp("rtx 3060", 250.0, 240.0, 5)
        db_upsert_comp(temp_db, comp)

        conn = sqlite3.connect(temp_db)
        row = conn.execute(
            "SELECT avg_price, median_price, count FROM comps WHERE key_title=?",
            ("rtx 3060",)
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 250.0
        assert row[1] == 240.0
        assert row[2] == 5

    def test_upsert_comp_updates(self, temp_db):
        comp1 = Comp("rtx 3060", 250.0, 240.0, 5)
        comp2 = Comp("rtx 3060", 260.0, 255.0, 6)
        db_upsert_comp(temp_db, comp1)
        db_upsert_comp(temp_db, comp2)

        conn = sqlite3.connect(temp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM comps WHERE key_title=?", ("rtx 3060",)
        ).fetchone()[0]
        row = conn.execute(
            "SELECT avg_price, count FROM comps WHERE key_title=?", ("rtx 3060",)
        ).fetchone()
        conn.close()
        assert count == 1
        assert row[0] == 260.0
        assert row[1] == 6


class TestComputeComps:
    """Tests for compute_comps function."""

    def test_empty_listings_returns_empty(self):
        result = compute_comps([])
        assert result == {}

    def test_single_listing(self):
        listings = [Listing("ebay", "http://e.com/1", "RTX 3060", 250.0)]
        comps = compute_comps(listings)
        assert len(comps) == 1
        key = list(comps.keys())[0]
        assert comps[key].count == 1
        assert comps[key].avg_price == 250.0

    def test_similar_listings_grouped(self):
        listings = [
            Listing("ebay", "http://e.com/1", "RTX 3060 Gaming GPU", 250.0),
            Listing("ebay", "http://e.com/2", "RTX 3060 GPU Gaming", 240.0),
            Listing("ebay", "http://e.com/3", "RTX 3060 Graphics Card", 260.0),
        ]
        comps = compute_comps(listings, sim_threshold=80)
        # Similar titles should be grouped
        assert len(comps) <= 2

    def test_different_listings_separate_groups(self):
        listings = [
            Listing("ebay", "http://e.com/1", "RTX 3060", 250.0),
            Listing("ebay", "http://e.com/2", "iPhone 14 Pro", 900.0),
            Listing("ebay", "http://e.com/3", "MacBook Pro M1", 1200.0),
        ]
        comps = compute_comps(listings, sim_threshold=86)
        assert len(comps) == 3

    def test_comp_average_price(self):
        listings = [
            Listing("ebay", "http://e.com/1", "RTX 3060 GPU", 200.0),
            Listing("ebay", "http://e.com/2", "RTX 3060 card", 300.0),
        ]
        comps = compute_comps(listings, sim_threshold=80)
        key = list(comps.keys())[0]
        assert comps[key].avg_price == 250.0

    def test_comp_median_price_odd(self):
        listings = [
            Listing("ebay", f"http://e.com/{i}", f"RTX 3060 GPU item{i}", p)
            for i, p in enumerate([100.0, 200.0, 300.0])
        ]
        comps = compute_comps(listings, sim_threshold=80)
        key = list(comps.keys())[0]
        assert comps[key].median_price == 200.0

    def test_comp_median_price_even(self):
        listings = [
            Listing("ebay", f"http://e.com/{i}", f"RTX 3060 GPU item{i}", p)
            for i, p in enumerate([100.0, 200.0, 300.0, 400.0])
        ]
        comps = compute_comps(listings, sim_threshold=80)
        key = list(comps.keys())[0]
        assert comps[key].median_price == 250.0


class TestMatchCompsToLive:
    """Tests for match_comps_to_live function."""

    def test_empty_live_returns_empty(self):
        comps = {"rtx 3060": Comp("rtx 3060", 250.0, 240.0, 5)}
        result = match_comps_to_live([], comps)
        assert result == []

    def test_match_found(self):
        comps = {"rtx 3060": Comp("rtx 3060", 300.0, 280.0, 5)}
        live = [Listing("shopgoodwill", "http://sg.com/1", "RTX 3060 GPU", 200.0)]
        result = match_comps_to_live(live, comps, sim_threshold=70)
        assert len(result) == 1
        row = result[0]
        assert row["price"] == 200.0
        assert row["discount_vs_avg_pct"] is not None
        assert row["discount_vs_avg_pct"] > 0

    def test_no_match_returns_none_discount(self):
        comps = {"ipad pro": Comp("ipad pro", 500.0, 480.0, 3)}
        live = [Listing("shopgoodwill", "http://sg.com/1", "RTX 3060 GPU", 200.0)]
        result = match_comps_to_live(live, comps, sim_threshold=90)
        assert len(result) == 1
        assert result[0]["discount_vs_avg_pct"] is None

    def test_result_row_has_required_keys(self):
        comps = {"rtx 3060": Comp("rtx 3060", 300.0, 280.0, 5)}
        live = [Listing("shopgoodwill", "http://sg.com/1", "RTX 3060", 200.0)]
        result = match_comps_to_live(live, comps)
        assert len(result) == 1
        row = result[0]
        for key in ["source", "title", "url", "price", "currency", "similarity"]:
            assert key in row

    def test_discount_calculation(self):
        comps = {"rtx 3060": Comp("rtx 3060", 200.0, 200.0, 1)}
        live = [Listing("sg", "http://sg.com/1", "RTX 3060 GPU", 150.0)]
        result = match_comps_to_live(live, comps, sim_threshold=70)
        assert len(result) == 1
        # 150 vs avg 200 = 25% discount
        assert abs(result[0]["discount_vs_avg_pct"] - 25.0) < 1.0

    def test_empty_comps(self):
        live = [Listing("sg", "http://sg.com/1", "RTX 3060", 150.0)]
        result = match_comps_to_live(live, {})
        assert len(result) == 1
        assert result[0]["discount_vs_avg_pct"] is None


class TestExportCsv:
    """Tests for export_csv function."""

    def test_export_csv_creates_file(self):
        rows = [
            {"title": "RTX 3060", "price": 200.0, "url": "http://example.com", "source": "test"}
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            csv_path = f.name

        try:
            export_csv(rows, csv_path)
            assert os.path.exists(csv_path)
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                data = list(reader)
            assert len(data) == 1
            assert data[0]["title"] == "RTX 3060"
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_export_csv_empty_rows(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            csv_path = f.name
        try:
            export_csv([], csv_path)
            # File exists but is empty (function returns early)
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_export_csv_multiple_rows(self):
        rows = [
            {"title": "Item 1", "price": 100.0},
            {"title": "Item 2", "price": 200.0},
            {"title": "Item 3", "price": 300.0},
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            csv_path = f.name

        try:
            export_csv(rows, csv_path)
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                data = list(reader)
            assert len(data) == 3
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)


class TestExportJson:
    """Tests for export_json function."""

    def test_export_json_creates_file(self):
        rows = [{"title": "RTX 3060", "price": 200.0}]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as f:
            json_path = f.name

        try:
            export_json(rows, json_path)
            assert os.path.exists(json_path)
            with open(json_path) as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["title"] == "RTX 3060"
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)

    def test_export_json_empty_rows(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as f:
            json_path = f.name

        try:
            export_json([], json_path)
            with open(json_path) as f:
                data = json.load(f)
            assert data == []
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)


class TestManualImport:
    """Tests for ManualImport provider."""

    @pytest.mark.asyncio
    async def test_manual_import_no_path(self):
        client = MagicMock()
        provider = ManualImport(client, path=None)
        result = await provider.search("test")
        assert result == []

    @pytest.mark.asyncio
    async def test_manual_import_csv(self):
        client = MagicMock()

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv", mode="w", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["title", "price", "url", "currency", "condition"])
            writer.writeheader()
            writer.writerow({
                "title": "RTX 3060",
                "price": "250.00",
                "url": "http://example.com/1",
                "currency": "USD",
                "condition": "used",
            })
            writer.writerow({
                "title": "iPad Pro",
                "price": "400.00",
                "url": "http://example.com/2",
                "currency": "USD",
                "condition": "good",
            })
            csv_path = f.name

        try:
            provider = ManualImport(client, path=csv_path)
            result = await provider.search("test")
            assert len(result) == 2
            assert result[0].title == "RTX 3060"
            assert result[0].price == 250.0
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    @pytest.mark.asyncio
    async def test_manual_import_json(self):
        client = MagicMock()

        data = [
            {"title": "RTX 3060", "price": 250.0, "url": "http://example.com/1"},
            {"title": "iPad Pro", "price": 400.0, "url": "http://example.com/2"},
        ]

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w"
        ) as f:
            json.dump(data, f)
            json_path = f.name

        try:
            provider = ManualImport(client, path=json_path)
            result = await provider.search("test")
            assert len(result) == 2
            assert result[0].title == "RTX 3060"
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)

    @pytest.mark.asyncio
    async def test_manual_import_respects_limit(self):
        client = MagicMock()
        data = [{"title": f"Item {i}", "price": float(i * 10), "url": f"http://e.com/{i}"}
                for i in range(10)]

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w"
        ) as f:
            json.dump(data, f)
            json_path = f.name

        try:
            provider = ManualImport(client, path=json_path)
            result = await provider.search("test", limit=3)
            assert len(result) == 3
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)

    @pytest.mark.asyncio
    async def test_manual_import_csv_invalid_price(self):
        client = MagicMock()

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv", mode="w", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["title", "price", "url"])
            writer.writeheader()
            writer.writerow({"title": "Item", "price": "not_a_price", "url": "http://e.com/1"})
            csv_path = f.name

        try:
            provider = ManualImport(client, path=csv_path)
            result = await provider.search("test")
            # Invalid price should be skipped
            assert len(result) == 0
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)


class TestPriceRegex:
    """Tests for the price regex pattern."""

    def test_usd_price(self):
        m = _price_re.search("$250.00")
        assert m is not None
        assert m.group(1) == "$"
        assert m.group(2) == "250.00"

    def test_gbp_price(self):
        m = _price_re.search("£150.99")
        assert m is not None
        assert m.group(1) == "£"

    def test_eur_price(self):
        m = _price_re.search("€89.99")
        assert m is not None
        assert m.group(1) == "€"

    def test_no_decimal(self):
        m = _price_re.search("$500")
        assert m is not None
        assert m.group(2) == "500"

    def test_no_price_found(self):
        m = _price_re.search("no price here")
        assert m is None


class TestBuildParser:
    """Tests for build_parser function."""

    def test_build_parser_returns_parser(self):
        from backend.arb_finder import build_parser
        parser = build_parser()
        assert parser is not None
        assert parser.prog == "ArbFinder"

    def test_parser_default_args(self):
        from backend.arb_finder import build_parser
        parser = build_parser()
        args = parser.parse_args(["test query"])
        assert args.query == "test query"
        assert args.live_limit == 80
        assert args.comp_limit == 150
        assert args.sim_threshold == 86
        assert args.threshold_pct == 20.0

    def test_parser_custom_args(self):
        from backend.arb_finder import build_parser
        parser = build_parser()
        args = parser.parse_args([
            "RTX 3060",
            "--live-limit", "50",
            "--comp-limit", "100",
            "--sim-threshold", "90",
            "--threshold-pct", "30.0",
            "--csv", "output.csv",
            "--json", "output.json",
        ])
        assert args.query == "RTX 3060"
        assert args.live_limit == 50
        assert args.comp_limit == 100
        assert args.sim_threshold == 90
        assert args.threshold_pct == 30.0
        assert args.csv == "output.csv"
        assert args.json == "output.json"
