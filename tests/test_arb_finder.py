"""
Tests for arb_finder module
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


def test_db_init_and_tables():
    """Test database initialization and table structure"""
    import sqlite3

    from backend.arb_finder import db_init

    # Create a temporary database file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    try:
        # Test database initialization
        db_init(db_path)

        # Verify tables exist and have correct structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "listings" in tables
        assert "comps" in tables

        # Check listings table structure
        cursor.execute("PRAGMA table_info(listings)")
        listings_cols = [row[1] for row in cursor.fetchall()]

        assert "id" in listings_cols
        assert "title" in listings_cols
        assert "price" in listings_cols
        assert "url" in listings_cols

        conn.close()
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
