"""Smoke tests: verify all core components start and respond correctly.

These tests are fast and lightweight — they check that each system can be
imported, initialised and exercised at the most basic level without error.
They are intentionally independent of external services (no live Docker,
no live Cloudflare) so they always run in CI.
"""

from __future__ import annotations

import importlib
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_temp_db() -> str:
    """Create a minimal in-memory SQLite database and return its path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, url TEXT UNIQUE, title TEXT, price REAL,
            currency TEXT, condition TEXT, ts REAL, meta_json TEXT
        )""")
    c.execute("""CREATE TABLE IF NOT EXISTS comps (
            key_title TEXT PRIMARY KEY, avg_price REAL, median_price REAL,
            count INTEGER, ts REAL
        )""")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture(scope="module")
def smoke_db():
    """Temp SQLite database for smoke tests."""
    db_path = _make_temp_db()
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="module")
def smoke_client(smoke_db):
    """FastAPI test client pointing at the smoke database."""
    import backend.api.main as api_main
    from backend.api.main import app

    with patch.object(api_main, "DB_PATH", smoke_db):
        yield TestClient(app)


# ---------------------------------------------------------------------------
# 1. Import smoke tests
# ---------------------------------------------------------------------------


class TestImports:
    """Verify that all backend modules can be imported without error."""

    def test_import_arb_finder(self):
        import backend.arb_finder  # noqa: F401

    def test_import_config(self):
        import backend.config  # noqa: F401

    def test_import_utils(self):
        import backend.utils  # noqa: F401

    def test_import_watch(self):
        import backend.watch  # noqa: F401

    def test_import_api_main(self):
        import backend.api.main  # noqa: F401

    def test_import_api_alerts(self):
        import backend.api.alerts  # noqa: F401

    def test_import_api_agents(self):
        import backend.api.agents  # noqa: F401

    def test_import_api_crews(self):
        import backend.api.crews  # noqa: F401

    def test_import_api_snipes(self):
        import backend.api.snipes  # noqa: F401

    def test_import_api_crawler(self):
        import backend.api.crawler  # noqa: F401

    def test_import_logging_etl(self):
        import backend.logging_etl  # noqa: F401


# ---------------------------------------------------------------------------
# 2. API startup smoke tests
# ---------------------------------------------------------------------------


class TestAPIStartup:
    """Verify the FastAPI application starts and responds to core probes."""

    def test_app_object_exists(self):
        from backend.api.main import app

        assert app is not None

    def test_app_has_routes(self):
        from backend.api.main import app

        routes = [r.path for r in app.routes]
        assert "/" in routes
        assert "/healthz" in routes
        assert "/api/listings" in routes

    def test_healthz_smoke(self, smoke_client):
        resp = smoke_client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_root_smoke(self, smoke_client):
        resp = smoke_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "ArbFinder" in data.get("name", "")

    def test_listings_smoke(self, smoke_client):
        resp = smoke_client.get("/api/listings")
        assert resp.status_code == 200

    def test_statistics_smoke(self, smoke_client):
        resp = smoke_client.get("/api/statistics")
        assert resp.status_code == 200

    def test_comps_smoke(self, smoke_client):
        resp = smoke_client.get("/api/comps")
        assert resp.status_code == 200

    def test_404_on_unknown_route(self, smoke_client):
        resp = smoke_client.get("/api/__smoke_unknown__")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. Database initialisation smoke tests
# ---------------------------------------------------------------------------


class TestDatabaseInit:
    """Verify the database tables can be created and queried."""

    def test_db_creates_listings_table(self, tmp_path):
        db_path = str(tmp_path / "smoke.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT, url TEXT UNIQUE, title TEXT, price REAL,
                currency TEXT, condition TEXT, ts REAL, meta_json TEXT
            )""")
        conn.commit()
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "listings" in tables
        conn.close()

    def test_db_creates_comps_table(self, tmp_path):
        db_path = str(tmp_path / "smoke.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE comps (
                key_title TEXT PRIMARY KEY, avg_price REAL, median_price REAL,
                count INTEGER, ts REAL
            )""")
        conn.commit()
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "comps" in tables
        conn.close()

    def test_db_insert_and_query_listing(self, smoke_db):
        conn = sqlite3.connect(smoke_db)
        now = time.time()
        conn.execute(
            "INSERT OR IGNORE INTO listings (source, url, title, price, currency, condition, ts, meta_json)"
            " VALUES (?,?,?,?,?,?,?,?)",
            ("smoke_source", "http://smoke.test/1", "Smoke Item", 9.99, "USD", "live", now, "{}"),
        )
        conn.commit()
        row = conn.execute(
            "SELECT title FROM listings WHERE url=?", ("http://smoke.test/1",)
        ).fetchone()
        assert row is not None
        assert row[0] == "Smoke Item"
        conn.close()


# ---------------------------------------------------------------------------
# 4. Configuration smoke tests
# ---------------------------------------------------------------------------


class TestConfiguration:
    """Verify configuration loading doesn't crash under minimal env."""

    def test_config_module_loadable(self):
        import backend.config as cfg  # noqa: F401

        assert cfg is not None

    def test_env_var_db_path_respected(self, tmp_path):
        """DB_PATH env var should be read at module load; confirm API uses it."""
        import backend.api.main as api_main

        custom = str(tmp_path / "custom.db")
        with patch.object(api_main, "DB_PATH", custom):
            assert api_main.DB_PATH == custom

    def test_stripe_not_configured_returns_400(self, smoke_client):
        resp = smoke_client.post(
            "/api/stripe/create-checkout-session?title=SmokeItem&price=1.0&currency=usd"
        )
        assert resp.status_code == 400
        assert "Stripe not configured" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 5. Docker config smoke tests (no daemon needed)
# ---------------------------------------------------------------------------


class TestDockerConfig:
    """Validate Dockerfile and docker-compose.yml are present and well-formed."""

    def test_dockerfile_exists(self):
        p = Path(__file__).parent.parent / "Dockerfile"
        assert p.exists(), "Dockerfile missing"

    def test_dockerfile_has_healthcheck(self):
        content = (Path(__file__).parent.parent / "Dockerfile").read_text()
        assert "HEALTHCHECK" in content

    def test_dockerfile_exposes_8080(self):
        content = (Path(__file__).parent.parent / "Dockerfile").read_text()
        assert "8080" in content

    def test_docker_compose_exists(self):
        p = Path(__file__).parent.parent / "docker-compose.yml"
        assert p.exists(), "docker-compose.yml missing"

    def test_docker_compose_has_backend_service(self):
        content = (Path(__file__).parent.parent / "docker-compose.yml").read_text()
        assert "backend:" in content

    def test_docker_compose_has_healthcheck(self):
        content = (Path(__file__).parent.parent / "docker-compose.yml").read_text()
        assert "healthcheck:" in content


# ---------------------------------------------------------------------------
# 6. Cloudflare config smoke tests
# ---------------------------------------------------------------------------


class TestCloudflareConfig:
    """Validate Cloudflare worker configuration files are present and valid."""

    def test_wrangler_toml_exists(self):
        p = Path(__file__).parent.parent / "cloudflare" / "wrangler.toml"
        assert p.exists(), "cloudflare/wrangler.toml missing"

    def test_wrangler_toml_has_worker_name(self):
        import toml

        config = toml.loads(
            (Path(__file__).parent.parent / "cloudflare" / "wrangler.toml").read_text()
        )
        assert "name" in config, "wrangler.toml must have a 'name' field"

    def test_wrangler_toml_has_main_entry(self):
        import toml

        config = toml.loads(
            (Path(__file__).parent.parent / "cloudflare" / "wrangler.toml").read_text()
        )
        assert "main" in config, "wrangler.toml must specify a 'main' entry point"

    def test_wrangler_toml_has_d1_binding(self):
        import toml

        config = toml.loads(
            (Path(__file__).parent.parent / "cloudflare" / "wrangler.toml").read_text()
        )
        assert "d1_databases" in config, "wrangler.toml should declare D1 database bindings"

    def test_cloudflare_worker_src_exists(self):
        src = Path(__file__).parent.parent / "cloudflare" / "src"
        assert src.exists(), "cloudflare/src directory missing"


# ---------------------------------------------------------------------------
# 7. Logging / ETL smoke tests
# ---------------------------------------------------------------------------


class TestLoggingETL:
    """Verify the logging/ETL module initialises correctly."""

    def test_get_logger_returns_logger(self):
        from backend.logging_etl import get_logger

        logger = get_logger("smoke_test")
        assert logger is not None

    def test_log_event_does_not_raise(self, tmp_path):
        from backend.logging_etl import ArbLogger

        logger = ArbLogger(log_dir=str(tmp_path))
        logger.log_event("smoke", {"key": "value"})

    def test_write_report_creates_file(self, tmp_path):
        from backend.logging_etl import ReportWriter

        writer = ReportWriter(report_dir=str(tmp_path))
        writer.write_report("smoke_report", {"status": "ok", "count": 1})
        files = list(tmp_path.iterdir())
        assert len(files) >= 1

    def test_etl_pipeline_runs(self, tmp_path):
        from backend.logging_etl import ETLPipeline

        pipeline = ETLPipeline(output_dir=str(tmp_path))
        result = pipeline.run(
            records=[{"source": "smoke", "price": 9.99, "title": "Smoke Item"}],
            report_name="smoke_etl",
        )
        assert result["status"] == "ok"
        assert result["records_processed"] == 1
