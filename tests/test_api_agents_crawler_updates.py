"""Tests for DB-backed agents, crawler, and live_updates endpoints."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_db_path():
    """Create a temp DB and initialize all required tables."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Core tables
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

    # Agent jobs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT NOT NULL,
            status TEXT DEFAULT 'queued',
            input_data TEXT,
            output_data TEXT,
            error_msg TEXT,
            started_at REAL NOT NULL,
            completed_at REAL,
            duration INTEGER
        )
    """)

    # Crawl results table
    c.execute("""
        CREATE TABLE IF NOT EXISTS crawl_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_name TEXT NOT NULL,
            url TEXT,
            status TEXT NOT NULL,
            items_found INTEGER DEFAULT 0,
            duration_ms INTEGER,
            error_msg TEXT,
            metadata TEXT,
            crawled_at REAL NOT NULL
        )
    """)

    # Crew runs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS crew_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crew_type TEXT NOT NULL,
            targets TEXT,
            query TEXT,
            status TEXT DEFAULT 'queued',
            started_at REAL NOT NULL,
            completed_at REAL,
            duration_seconds REAL,
            items_processed INTEGER DEFAULT 0,
            items_created INTEGER DEFAULT 0,
            error_message TEXT,
            result_data TEXT
        )
    """)

    # Alerts tables
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_query TEXT NOT NULL,
            min_price REAL,
            max_price REAL,
            notification_method TEXT NOT NULL,
            notification_target TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at REAL NOT NULL,
            last_triggered_at REAL,
            trigger_count INTEGER DEFAULT 0,
            metadata TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            listing_id INTEGER,
            listing_url TEXT,
            listing_title TEXT,
            listing_price REAL,
            matched_at REAL NOT NULL,
            notification_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
        )
    """)

    # Snipes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS snipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_url TEXT NOT NULL,
            listing_title TEXT,
            max_bid REAL NOT NULL,
            auction_end_time REAL NOT NULL,
            lead_time_seconds INTEGER DEFAULT 5,
            status TEXT DEFAULT 'scheduled',
            created_at REAL NOT NULL,
            executed_at REAL,
            result TEXT,
            metadata TEXT
        )
    """)

    now = time.time()

    # Seed agent_jobs
    c.executemany(
        "INSERT INTO agent_jobs (agent_type, status, started_at, completed_at, duration) VALUES (?,?,?,?,?)",
        [
            ("web_crawler", "completed", now - 600, now - 500, 100000),
            ("price_specialist", "running", now - 100, None, None),
            ("data_validator", "failed", now - 200, now - 150, 50000),
        ],
    )

    # Seed crawl_results
    c.executemany(
        "INSERT INTO crawl_results (target_name, url, status, items_found, duration_ms, crawled_at) VALUES (?,?,?,?,?,?)",
        [
            ("shopgoodwill", "https://shopgoodwill.com", "success", 42, 3200, now - 300),
            ("govdeals", "https://govdeals.com", "success", 28, 2800, now - 200),
            ("govdeals", "https://govdeals.com", "error", 0, 1000, now - 100),
        ],
    )

    # Seed crew_runs
    c.execute(
        "INSERT INTO crew_runs (crew_type, status, started_at, completed_at, items_processed, items_created) VALUES (?,?,?,?,?,?)",
        ("price_ingestion", "completed", now - 500, now - 400, 50, 30),
    )

    conn.commit()
    conn.close()

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="module")
def client(test_db_path):
    """Create test client with all API modules patched to use test DB."""
    import backend.api.main as api_main
    import backend.api.agents as api_agents
    import backend.api.crawler as api_crawler
    import backend.api.live_updates as api_live
    from backend.api.main import app

    with (
        patch.object(api_main, "DB_PATH", test_db_path),
        patch.object(api_agents, "DB_PATH", test_db_path),
        patch.object(api_crawler, "DB_PATH", test_db_path),
        patch.object(api_live, "DB_PATH", test_db_path),
    ):
        yield TestClient(app)


# ---------------------------------------------------------------------------
# Agent Jobs
# ---------------------------------------------------------------------------


class TestAgentJobsList:
    def test_list_jobs_returns_200(self, client):
        response = client.get("/api/agents/jobs")
        assert response.status_code == 200

    def test_list_jobs_structure(self, client):
        data = client.get("/api/agents/jobs").json()
        assert "jobs" in data
        assert "total" in data
        assert isinstance(data["jobs"], list)

    def test_list_jobs_has_seeded_data(self, client):
        data = client.get("/api/agents/jobs").json()
        assert data["total"] >= 3

    def test_list_jobs_filter_by_status(self, client):
        data = client.get("/api/agents/jobs?status=completed").json()
        for job in data["jobs"]:
            assert job["status"] == "completed"

    def test_list_jobs_filter_by_agent_type(self, client):
        data = client.get("/api/agents/jobs?agent_type=web_crawler").json()
        for job in data["jobs"]:
            assert job["agentType"] == "web_crawler"

    def test_list_jobs_invalid_status_rejected(self, client):
        response = client.get("/api/agents/jobs?status=unknown_status")
        assert response.status_code == 422

    def test_list_jobs_limit(self, client):
        data = client.get("/api/agents/jobs?limit=1").json()
        assert len(data["jobs"]) <= 1

    def test_job_item_has_required_fields(self, client):
        data = client.get("/api/agents/jobs").json()
        if data["jobs"]:
            job = data["jobs"][0]
            for field in ["id", "agentType", "status", "startedAt"]:
                assert field in job


class TestAgentJobGet:
    def test_get_existing_job(self, client):
        # Create a job first
        create_resp = client.post("/api/agents/jobs?agent_type=web_crawler")
        assert create_resp.status_code == 200
        job_id = create_resp.json()["job_id"]

        resp = client.get(f"/api/agents/jobs/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == job_id
        assert data["agentType"] == "web_crawler"

    def test_get_nonexistent_job_returns_404(self, client):
        response = client.get("/api/agents/jobs/999999")
        assert response.status_code == 404


class TestAgentJobCreate:
    def test_create_valid_job(self, client):
        resp = client.post("/api/agents/jobs?agent_type=price_specialist")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["status"] == "queued"
        assert isinstance(data["job_id"], int)
        assert data["job_id"] > 0

    def test_create_invalid_agent_type(self, client):
        resp = client.post("/api/agents/jobs?agent_type=invalid_bot")
        assert resp.status_code == 400

    def test_created_job_retrievable(self, client):
        create_resp = client.post("/api/agents/jobs?agent_type=data_validator")
        job_id = create_resp.json()["job_id"]
        get_resp = client.get(f"/api/agents/jobs/{job_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["agentType"] == "data_validator"


class TestAgentTypes:
    def test_list_types_returns_200(self, client):
        resp = client.get("/api/agents/types")
        assert resp.status_code == 200

    def test_list_types_has_data(self, client):
        data = client.get("/api/agents/types").json()
        assert "agent_types" in data
        assert len(data["agent_types"]) > 0


# ---------------------------------------------------------------------------
# Crawler Status (DB-backed)
# ---------------------------------------------------------------------------


class TestCrawlerStatus:
    def test_status_returns_200(self, client):
        resp = client.get("/api/crawler/status")
        assert resp.status_code == 200

    def test_status_structure(self, client):
        data = client.get("/api/crawler/status").json()
        assert "results" in data
        assert "total_items" in data
        assert "active_targets" in data

    def test_status_reads_db_data(self, client):
        data = client.get("/api/crawler/status").json()
        # We seeded shopgoodwill and govdeals; govdeals had two rows,
        # latest-per-target query should return one per target
        target_names = [r["target_name"] for r in data["results"]]
        assert "shopgoodwill" in target_names
        assert "govdeals" in target_names

    def test_status_result_fields(self, client):
        data = client.get("/api/crawler/status").json()
        if data["results"]:
            result = data["results"][0]
            for field in ["target_name", "status", "items_found"]:
                assert field in result


# ---------------------------------------------------------------------------
# Live Updates (DB-backed)
# ---------------------------------------------------------------------------


class TestLiveUpdates:
    def test_live_updates_returns_200(self, client):
        resp = client.get("/api/live-updates")
        assert resp.status_code == 200

    def test_live_updates_structure(self, client):
        data = client.get("/api/live-updates").json()
        assert "updates" in data
        assert "total" in data

    def test_live_updates_has_data(self, client):
        data = client.get("/api/live-updates").json()
        # We seeded crawl_results and crew_runs
        assert data["total"] >= 1

    def test_live_updates_filter_by_type(self, client):
        data = client.get("/api/live-updates?type_filter=crawler").json()
        for update in data["updates"]:
            assert update["type"] == "crawler"

    def test_live_updates_limit(self, client):
        data = client.get("/api/live-updates?limit=2").json()
        assert len(data["updates"]) <= 2

    def test_live_updates_item_fields(self, client):
        data = client.get("/api/live-updates").json()
        if data["updates"]:
            upd = data["updates"][0]
            for field in ["id", "timestamp", "type", "message"]:
                assert field in upd


class TestActivityStats:
    def test_activity_stats_returns_200(self, client):
        resp = client.get("/api/activity-stats")
        assert resp.status_code == 200

    def test_activity_stats_structure(self, client):
        data = client.get("/api/activity-stats").json()
        assert "last_hour" in data
        assert "last_24_hours" in data
        assert "active_agents" in data
        assert "active_crawlers" in data

    def test_activity_stats_last_hour_fields(self, client):
        data = client.get("/api/activity-stats").json()
        for key in ["crawls", "items_found", "agent_jobs", "errors"]:
            assert key in data["last_hour"]
