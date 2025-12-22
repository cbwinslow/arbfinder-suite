"""
Tests for utils module
"""

import os
import sqlite3
import tempfile

import pytest

from backend import utils


def test_get_db_path_default():
    """Test default database path"""
    # Remove environment variable if set
    if "ARBF_DB" in os.environ:
        del os.environ["ARBF_DB"]
    
    db_path = utils.get_db_path()
    assert db_path is not None
    assert isinstance(db_path, str)
    assert db_path.endswith(".sqlite3") or db_path.endswith(".db")


def test_get_db_path_from_env():
    """Test database path from environment variable"""
    test_path = "/tmp/test_arb.db"
    os.environ["ARBF_DB"] = test_path
    
    db_path = utils.get_db_path()
    assert db_path == test_path
    
    # Cleanup
    if "ARBF_DB" in os.environ:
        del os.environ["ARBF_DB"]


def test_init_db_creates_tables():
    """Test that init_db creates required tables"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        # Initialize database
        utils.init_db(db_path)
        
        # Verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "listings" in tables
        assert "comps" in tables
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_insert_listing():
    """Test inserting a listing into the database"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        utils.init_db(db_path)
        
        listing = {
            "source": "test",
            "url": "https://example.com/item1",
            "title": "Test Item",
            "price": 100.0,
            "currency": "USD",
            "condition": "New",
            "ts": 1234567890.0,
            "meta_json": "{}"
        }
        
        utils.insert_listing(db_path, listing)
        
        # Verify the listing was inserted
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM listings WHERE url=?", (listing["url"],))
        count = cursor.fetchone()[0]
        assert count == 1
        
        cursor.execute("SELECT title, price FROM listings WHERE url=?", (listing["url"],))
        row = cursor.fetchone()
        assert row[0] == "Test Item"
        assert row[1] == 100.0
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_insert_duplicate_listing():
    """Test that duplicate listings are not inserted"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        utils.init_db(db_path)
        
        listing = {
            "source": "test",
            "url": "https://example.com/item1",
            "title": "Test Item",
            "price": 100.0,
            "currency": "USD",
            "condition": "New",
            "ts": 1234567890.0,
            "meta_json": "{}"
        }
        
        # Insert the same listing twice
        utils.insert_listing(db_path, listing)
        utils.insert_listing(db_path, listing)
        
        # Verify only one listing exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM listings WHERE url=?", (listing["url"],))
        count = cursor.fetchone()[0]
        assert count == 1
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_stats():
    """Test getting database statistics"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        utils.init_db(db_path)
        
        # Insert some test data
        for i in range(5):
            listing = {
                "source": "test",
                "url": f"https://example.com/item{i}",
                "title": f"Test Item {i}",
                "price": 100.0 + i,
                "currency": "USD",
                "condition": "New",
                "ts": 1234567890.0,
                "meta_json": "{}"
            }
            utils.insert_listing(db_path, listing)
        
        stats = utils.get_stats(db_path)
        
        assert stats is not None
        assert stats["total_listings"] == 5
        assert "recent_listings" in stats
        assert "price_stats" in stats
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
