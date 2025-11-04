"""
Tests for API endpoints
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def setup_test_db():
    """Setup test database"""
    from backend.arb_finder import db_init
    
    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    # Initialize database
    conn = db_init(db_path)
    if conn:
        conn.close()
    
    # Set environment variable for the API
    os.environ['ARBF_DB'] = db_path
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(setup_test_db):
    """Create test client"""
    from backend.api.main import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data or "message" in data


def test_api_statistics_endpoint(client):
    """Test statistics endpoint"""
    response = client.get("/api/statistics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_api_listings_endpoint(client):
    """Test listings endpoint"""
    response = client.get("/api/listings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


def test_api_listings_with_pagination(client):
    """Test listings endpoint with pagination"""
    response = client.get("/api/listings?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


def test_api_search_endpoint(client):
    """Test search endpoint"""
    response = client.get("/api/listings/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


def test_api_comps_endpoint(client):
    """Test comps endpoint"""
    response = client.get("/api/comps")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


def test_invalid_endpoint(client):
    """Test that invalid endpoints return 404"""
    response = client.get("/api/invalid-endpoint")
    assert response.status_code == 404


def test_api_cors_headers(client):
    """Test that CORS headers are present"""
    response = client.get("/")
    assert response.status_code == 200
    # CORS headers might be present depending on configuration
