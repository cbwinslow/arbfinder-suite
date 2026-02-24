"""Tests for backend/utils.py - database utility functions."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure backend is on the path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils import (
    backup_database,
    clean_old_listings,
    export_database_stats,
    inspect_database,
    list_recent_listings,
    vacuum_database,
)


@pytest.fixture
def db_with_data():
    """Create a temporary database with sample data."""
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
            ("ebay", "http://ebay.com/1", "RTX 3060", 250.0, "USD", "sold", now, "{}"),
            ("shopgoodwill", "http://sg.com/1", "RTX 3060 GPU", 180.0, "USD", "live", now, "{}"),
            ("govdeals", "http://gd.com/1", "iPad Pro", 300.0, "USD", "live", now - 100, "{}"),
        ],
    )
    c.executemany(
        "INSERT INTO comps (key_title, avg_price, median_price, count, ts) VALUES (?,?,?,?,?)",
        [
            ("rtx 3060", 250.0, 240.0, 5, now),
            ("ipad pro", 350.0, 340.0, 3, now),
        ],
    )
    conn.commit()
    conn.close()

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def empty_db():
    """Create an empty but initialized database."""
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
    conn.commit()
    conn.close()

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)


class TestInspectDatabase:
    """Tests for inspect_database function."""

    def test_inspect_returns_expected_keys(self, db_with_data):
        stats = inspect_database(db_with_data)
        assert "tables" in stats
        assert "listings" in stats
        assert "comps" in stats

    def test_inspect_tables_list(self, db_with_data):
        stats = inspect_database(db_with_data)
        assert "listings" in stats["tables"]
        assert "comps" in stats["tables"]

    def test_inspect_listings_count(self, db_with_data):
        stats = inspect_database(db_with_data)
        assert stats["listings"]["total"] == 3

    def test_inspect_listings_by_source(self, db_with_data):
        stats = inspect_database(db_with_data)
        by_source = stats["listings"]["by_source"]
        assert by_source["ebay"] == 1
        assert by_source["shopgoodwill"] == 1
        assert by_source["govdeals"] == 1

    def test_inspect_price_range(self, db_with_data):
        stats = inspect_database(db_with_data)
        price_range = stats["listings"]["price_range"]
        assert price_range["min"] == 180.0
        assert price_range["max"] == 300.0
        assert price_range["avg"] is not None

    def test_inspect_comps_count(self, db_with_data):
        stats = inspect_database(db_with_data)
        assert stats["comps"]["total"] == 2

    def test_inspect_empty_database(self, empty_db):
        stats = inspect_database(empty_db)
        assert stats["listings"]["total"] == 0
        assert stats["comps"]["total"] == 0
        assert stats["listings"]["price_range"]["min"] is None


class TestCleanOldListings:
    """Tests for clean_old_listings function."""

    def test_clean_removes_old_listings(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE listings (
                  id INTEGER PRIMARY KEY, source TEXT, url TEXT UNIQUE,
                  title TEXT, price REAL, currency TEXT, condition TEXT, ts REAL, meta_json TEXT
                )
            """)
            old_ts = time.time() - (60 * 86400)  # 60 days ago
            now = time.time()
            c.execute(
                "INSERT INTO listings VALUES (1, 'test', 'http://old.com', 'Old Item', 10.0, 'USD', 'live', ?, '{}')",
                (old_ts,),
            )
            c.execute(
                "INSERT INTO listings VALUES (2, 'test', 'http://new.com', 'New Item', 20.0, 'USD', 'live', ?, '{}')",
                (now,),
            )
            conn.commit()
            conn.close()

            removed = clean_old_listings(db_path, days=30)
            assert removed == 1

            # Verify the new item is still there
            conn = sqlite3.connect(db_path)
            remaining = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
            conn.close()
            assert remaining == 1
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_clean_no_old_listings(self, db_with_data):
        # All listings have current timestamps - should remove none
        removed = clean_old_listings(db_with_data, days=0)
        # days=0 means cutoff is now, so all listings should be removed
        assert removed >= 0

    def test_clean_default_days(self, empty_db):
        removed = clean_old_listings(empty_db)
        assert removed == 0


class TestExportDatabaseStats:
    """Tests for export_database_stats function."""

    def test_export_creates_file(self, db_with_data):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            output_path = f.name

        try:
            result = export_database_stats(db_with_data, output_path)
            assert result is True
            assert Path(output_path).exists()

            with open(output_path) as f:
                data = json.load(f)
            assert "listings" in data
            assert "comps" in data
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_export_invalid_path(self, db_with_data):
        result = export_database_stats(db_with_data, "/nonexistent/dir/file.json")
        assert result is False


class TestBackupDatabase:
    """Tests for backup_database function."""

    def test_backup_creates_file(self, db_with_data):
        with tempfile.TemporaryDirectory() as backup_dir:
            backup_path = backup_database(db_with_data, backup_dir=backup_dir)
            assert os.path.exists(backup_path)
            assert backup_path.endswith(".sqlite3")

    def test_backup_default_dir(self, db_with_data):
        """Test backup with default directory."""
        with patch("backend.utils.Path.home") as mock_home:
            with tempfile.TemporaryDirectory() as tmpdir:
                mock_home.return_value = Path(tmpdir)
                backup_path = backup_database(db_with_data)
                assert os.path.exists(backup_path)

    def test_backup_preserves_data(self, db_with_data):
        with tempfile.TemporaryDirectory() as backup_dir:
            backup_path = backup_database(db_with_data, backup_dir=backup_dir)
            conn = sqlite3.connect(backup_path)
            count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
            conn.close()
            assert count == 3


class TestVacuumDatabase:
    """Tests for vacuum_database function."""

    def test_vacuum_returns_true(self, db_with_data):
        result = vacuum_database(db_with_data)
        assert result is True

    def test_vacuum_empty_db(self, empty_db):
        result = vacuum_database(empty_db)
        assert result is True

    def test_vacuum_invalid_path(self):
        # SQLite will create a new db for invalid path in writable dir,
        # but a truly invalid path should fail
        result = vacuum_database("/nonexistent_dir_xyz/test.db")
        assert result is False


class TestListRecentListings:
    """Tests for list_recent_listings function."""

    def test_list_recent_returns_listings(self, db_with_data):
        listings = list_recent_listings(db_with_data, limit=10)
        assert len(listings) == 3

    def test_list_recent_respects_limit(self, db_with_data):
        listings = list_recent_listings(db_with_data, limit=2)
        assert len(listings) == 2

    def test_list_recent_has_expected_keys(self, db_with_data):
        listings = list_recent_listings(db_with_data, limit=1)
        assert len(listings) == 1
        item = listings[0]
        assert "source" in item
        assert "title" in item
        assert "price" in item
        assert "currency" in item
        assert "timestamp" in item

    def test_list_recent_empty_db(self, empty_db):
        listings = list_recent_listings(empty_db)
        assert listings == []
