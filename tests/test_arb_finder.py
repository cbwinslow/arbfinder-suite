"""
Tests for arb_finder module
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


def test_db_init():
    """Test database initialization"""
    from backend.arb_finder import db_init
    import sqlite3
    
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        # Test database initialization
        db_init(db_path)
        
        # Verify tables exist by connecting to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'listings' in tables
        assert 'comps' in tables
        
        conn.close()
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.mark.asyncio
async def test_fetch_provider_data_with_mock():
    """Test fetching provider data with mocked responses"""
    # This test is a placeholder for when fetch_provider_data is available
    # For now, we'll skip this test
    pytest.skip("fetch_provider_data not available yet")


def test_db_init_creates_required_tables():
    """Test that db_init creates all required tables"""
    from backend.arb_finder import db_init
    import sqlite3
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db_init(db_path)
        
        # Connect to verify tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check listings table structure
        cursor.execute("PRAGMA table_info(listings)")
        listings_cols = [row[1] for row in cursor.fetchall()]
        
        assert 'id' in listings_cols
        assert 'title' in listings_cols
        assert 'price' in listings_cols
        assert 'url' in listings_cols
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
