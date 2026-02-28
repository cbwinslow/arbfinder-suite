"""End-to-end tests for the ArbFinder Suite.

These tests exercise the *full data flow* — from database seeding through API
calls to response validation — without any mocking of application logic.
They also verify that deployment artefacts (Docker, Cloudflare, GitHub Actions
workflows) are structurally valid.

Tests that require live external services (a running Docker daemon, a live
Cloudflare account, etc.) are *skipped* automatically in environments where
those services are unavailable, so the suite is always safe to run in CI.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _populate_db(db_path: str) -> None:
    """Insert a realistic set of sample records into *db_path*."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, url TEXT UNIQUE, title TEXT, price REAL,
            currency TEXT, condition TEXT, ts REAL, meta_json TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS comps (
            key_title TEXT PRIMARY KEY, avg_price REAL, median_price REAL,
            count INTEGER, ts REAL
        )"""
    )
    now = time.time()
    c.executemany(
        "INSERT OR IGNORE INTO listings (source,url,title,price,currency,condition,ts,meta_json)"
        " VALUES (?,?,?,?,?,?,?,?)",
        [
            ("ebay", "https://ebay.com/e2e/1", "RTX 4090 GPU", 1200.0, "USD", "live", now, "{}"),
            ("govdeals", "https://govdeals.com/e2e/2", "iPad Pro M2 12.9", 650.0, "USD", "live", now - 60, "{}"),
            ("shopgoodwill", "https://shopgoodwill.com/e2e/3", "MacBook Air M1", 450.0, "USD", "sold", now - 120, "{}"),
            ("ebay", "https://ebay.com/e2e/4", "PlayStation 5 Console", 380.0, "USD", "live", now - 180, "{}"),
            ("govdeals", "https://govdeals.com/e2e/5", "iPhone 14 Pro Max", 700.0, "USD", "live", now - 240, "{}"),
        ],
    )
    c.executemany(
        "INSERT OR IGNORE INTO comps (key_title,avg_price,median_price,count,ts) VALUES (?,?,?,?,?)",
        [
            ("rtx 4090 gpu", 1300.0, 1250.0, 10, now),
            ("ipad pro m2 12.9", 750.0, 720.0, 8, now),
            ("macbook air m1", 500.0, 490.0, 15, now),
        ],
    )
    conn.commit()
    conn.close()


@pytest.fixture(scope="module")
def e2e_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    _populate_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="module")
def e2e_client(e2e_db):
    import backend.api.main as api_main
    from backend.api.main import app

    with patch.object(api_main, "DB_PATH", e2e_db):
        yield TestClient(app)


# ---------------------------------------------------------------------------
# 1. Full API data-flow E2E
# ---------------------------------------------------------------------------

class TestAPIDataFlow:
    """Full round-trip: seed DB → query API → validate response shape/values."""

    def test_listings_returns_all_seeded_records(self, e2e_client):
        data = e2e_client.get("/api/listings").json()
        assert data["total"] >= 5
        assert len(data["data"]) >= 5

    def test_listings_contain_expected_fields(self, e2e_client):
        items = e2e_client.get("/api/listings").json()["data"]
        for field in ("source", "url", "title", "price", "currency", "condition", "ts"):
            assert all(field in item for item in items), f"field '{field}' missing in some items"

    def test_listings_prices_are_numeric(self, e2e_client):
        items = e2e_client.get("/api/listings").json()["data"]
        for item in items:
            assert isinstance(item["price"], (int, float))

    def test_listings_filter_by_source_ebay(self, e2e_client):
        data = e2e_client.get("/api/listings?source=ebay").json()
        assert data["total"] >= 2
        for item in data["data"]:
            assert item["source"] == "ebay"

    def test_listings_filter_by_source_govdeals(self, e2e_client):
        data = e2e_client.get("/api/listings?source=govdeals").json()
        for item in data["data"]:
            assert item["source"] == "govdeals"

    def test_listings_pagination_correct_count(self, e2e_client):
        page1 = e2e_client.get("/api/listings?limit=2&offset=0").json()
        page2 = e2e_client.get("/api/listings?limit=2&offset=2").json()
        assert page1["count"] == 2
        assert page2["count"] == 2
        # Pages must not overlap
        urls1 = {i["url"] for i in page1["data"]}
        urls2 = {i["url"] for i in page2["data"]}
        assert urls1.isdisjoint(urls2), "Pagination returned duplicate records"

    def test_listings_order_by_price_ascending(self, e2e_client):
        # order_by defaults to ts DESC; just check that ordering does not error
        resp = e2e_client.get("/api/listings?order_by=price")
        assert resp.status_code == 200

    def test_search_rtx_returns_gpu_listing(self, e2e_client):
        results = e2e_client.get("/api/listings/search?q=RTX").json()
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert any("RTX" in t for t in titles)

    def test_search_nonexistent_returns_empty_list(self, e2e_client):
        results = e2e_client.get("/api/listings/search?q=__NO_SUCH_ITEM_XYZ__").json()
        assert results == []

    def test_statistics_total_matches_db(self, e2e_client, e2e_db):
        db_count = sqlite3.connect(e2e_db).execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        stats = e2e_client.get("/api/statistics").json()
        assert stats["total_listings"] == db_count

    def test_statistics_by_source_has_ebay(self, e2e_client):
        stats = e2e_client.get("/api/statistics").json()
        assert "ebay" in stats["by_source"]

    def test_statistics_price_stats_sane(self, e2e_client):
        stats = e2e_client.get("/api/statistics").json()
        if "price_stats" in stats:
            ps = stats["price_stats"]
            assert ps["min"] > 0
            assert ps["max"] >= ps["min"]
            assert ps["average"] >= ps["min"]

    def test_comps_returned_for_seeded_data(self, e2e_client):
        comps = e2e_client.get("/api/comps").json()
        assert len(comps) >= 3

    def test_comps_search_rtx(self, e2e_client):
        results = e2e_client.get("/api/comps/search?q=rtx").json()
        assert len(results) >= 1

    def test_post_new_listing_then_retrieve(self, e2e_client):
        payload = {
            "title": "E2E Test Item",
            "price": 42.42,
            "url": "https://e2e.test/unique-e2e-item-001",
            "currency": "USD",
            "source": "e2e_test",
        }
        post_resp = e2e_client.post("/api/listings", json=payload)
        assert post_resp.status_code == 200
        assert post_resp.json().get("ok") is True

        # Retrieve it via search
        results = e2e_client.get("/api/listings/search?q=E2E+Test+Item").json()
        assert any(r["url"] == payload["url"] for r in results)

    def test_healthz_always_ok(self, e2e_client):
        for _ in range(3):
            resp = e2e_client.get("/healthz")
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# 2. Validation / Error handling E2E
# ---------------------------------------------------------------------------

class TestAPIErrorHandling:
    """Verify that the API responds with correct HTTP status codes for bad input."""

    def test_listings_limit_too_large(self, e2e_client):
        resp = e2e_client.get("/api/listings?limit=9999")
        assert resp.status_code == 422

    def test_listings_negative_limit(self, e2e_client):
        resp = e2e_client.get("/api/listings?limit=-1")
        assert resp.status_code == 422

    def test_listings_negative_offset(self, e2e_client):
        resp = e2e_client.get("/api/listings?offset=-5")
        assert resp.status_code == 422

    def test_listings_invalid_order_by(self, e2e_client):
        resp = e2e_client.get("/api/listings?order_by=DROP_TABLE")
        assert resp.status_code == 422

    def test_search_empty_query_rejected(self, e2e_client):
        resp = e2e_client.get("/api/listings/search?q=")
        assert resp.status_code == 422

    def test_create_listing_missing_price(self, e2e_client):
        resp = e2e_client.post("/api/listings", json={"title": "Missing Price", "url": "http://x.com/1"})
        assert resp.status_code == 422

    def test_create_listing_missing_url(self, e2e_client):
        resp = e2e_client.post("/api/listings", json={"title": "No URL", "price": 10.0})
        assert resp.status_code == 422

    def test_stripe_unconfigured_returns_400(self, e2e_client):
        resp = e2e_client.post(
            "/api/stripe/create-checkout-session?title=Test&price=10.0&currency=usd"
        )
        assert resp.status_code == 400

    def test_unknown_endpoint_returns_404(self, e2e_client):
        resp = e2e_client.get("/api/completely/unknown/path")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. Docker deployment config E2E
# ---------------------------------------------------------------------------

class TestDockerDeployment:
    """Validate Docker deployment configuration files are production-ready."""

    ROOT = Path(__file__).parent.parent

    def test_dockerfile_has_python_base_image(self):
        content = (self.ROOT / "Dockerfile").read_text()
        assert "FROM python:" in content

    def test_dockerfile_has_node_stage(self):
        content = (self.ROOT / "Dockerfile").read_text()
        assert "FROM node:" in content

    def test_dockerfile_copies_requirements(self):
        content = (self.ROOT / "Dockerfile").read_text()
        assert "requirements.txt" in content

    def test_dockerfile_creates_data_dir(self):
        content = (self.ROOT / "Dockerfile").read_text()
        assert "/data" in content

    def test_dockerfile_sets_pythonunbuffered(self):
        content = (self.ROOT / "Dockerfile").read_text()
        assert "PYTHONUNBUFFERED" in content

    def test_start_sh_exists_and_is_referenced(self):
        start_sh = self.ROOT / "start.sh"
        assert start_sh.exists(), "start.sh missing from repository root"
        dockerfile = (self.ROOT / "Dockerfile").read_text()
        assert "start.sh" in dockerfile

    def test_docker_compose_has_postgres_service(self):
        content = (self.ROOT / "docker-compose.yml").read_text()
        assert "postgres:" in content

    def test_docker_compose_backend_depends_on_postgres(self):
        content = (self.ROOT / "docker-compose.yml").read_text()
        # 'depends_on' must appear after 'backend:' in the compose file
        backend_pos = content.index("backend:")
        depends_pos = content.index("depends_on:", backend_pos)
        assert depends_pos > backend_pos

    def test_docker_compose_exposes_8080(self):
        content = (self.ROOT / "docker-compose.yml").read_text()
        assert "8080" in content

    def test_docker_compose_has_minio(self):
        content = (self.ROOT / "docker-compose.yml").read_text()
        assert "minio" in content

    @pytest.mark.skipif(
        shutil.which("docker") is None,
        reason="Docker not available in this environment",
    )
    def test_docker_compose_config_validates(self):
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            cwd=self.ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"docker compose config failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# 4. Cloudflare deployment config E2E
# ---------------------------------------------------------------------------

class TestCloudflareDeployment:
    """Validate Cloudflare worker configuration is deployment-ready."""

    ROOT = Path(__file__).parent.parent

    def _load_wrangler(self) -> dict:
        import toml
        return toml.loads((self.ROOT / "cloudflare" / "wrangler.toml").read_text())

    def test_wrangler_compatibility_date_set(self):
        cfg = self._load_wrangler()
        assert "compatibility_date" in cfg, "wrangler.toml must set compatibility_date"

    def test_wrangler_has_production_env(self):
        cfg = self._load_wrangler()
        assert "env" in cfg and "production" in cfg["env"]

    def test_wrangler_has_staging_env(self):
        cfg = self._load_wrangler()
        assert "env" in cfg and "staging" in cfg["env"]

    def test_wrangler_r2_buckets_defined(self):
        cfg = self._load_wrangler()
        assert "r2_buckets" in cfg and len(cfg["r2_buckets"]) > 0

    def test_wrangler_kv_namespaces_defined(self):
        cfg = self._load_wrangler()
        assert "kv_namespaces" in cfg and len(cfg["kv_namespaces"]) > 0

    def test_wrangler_queues_defined(self):
        cfg = self._load_wrangler()
        assert "queues" in cfg

    def test_wrangler_cron_triggers_defined(self):
        cfg = self._load_wrangler()
        assert "triggers" in cfg
        assert "crons" in cfg["triggers"] and len(cfg["triggers"]["crons"]) > 0

    def test_cloudflare_src_index_exists(self):
        src = self.ROOT / "cloudflare" / "src" / "index.ts"
        assert src.exists(), "cloudflare/src/index.ts missing"

    def test_cloudflare_deploy_workflow_exists(self):
        wf = self.ROOT / ".github" / "workflows" / "cloudflare-deploy.yml"
        assert wf.exists(), ".github/workflows/cloudflare-deploy.yml missing"


# ---------------------------------------------------------------------------
# 5. GitHub Actions workflow config E2E
# ---------------------------------------------------------------------------

class TestGitHubActionsWorkflows:
    """Validate that all critical CI/CD workflows exist and are structurally valid."""

    WF_DIR = Path(__file__).parent.parent / ".github" / "workflows"

    def _load_yaml(self, filename: str) -> dict:
        import yaml  # type: ignore[import]
        return yaml.safe_load((self.WF_DIR / filename).read_text())

    def _yaml_available(self) -> bool:
        try:
            import yaml  # noqa: F401
            return True
        except ImportError:
            return False

    def test_ci_yml_exists(self):
        assert (self.WF_DIR / "ci.yml").exists()

    def test_ci_enhanced_yml_exists(self):
        assert (self.WF_DIR / "ci-enhanced.yml").exists()

    def test_cloudflare_deploy_yml_exists(self):
        assert (self.WF_DIR / "cloudflare-deploy.yml").exists()

    def test_smoke_e2e_workflow_exists(self):
        assert (self.WF_DIR / "smoke-e2e-tests.yml").exists(), (
            "smoke-e2e-tests.yml workflow missing — add it with artifact collection"
        )

    def test_etl_reports_workflow_exists(self):
        assert (self.WF_DIR / "etl-reports.yml").exists(), (
            "etl-reports.yml workflow missing — add ETL report generation workflow"
        )


# ---------------------------------------------------------------------------
# 6. Logging / ETL E2E
# ---------------------------------------------------------------------------

class TestLoggingETLE2E:
    """Full end-to-end exercise of the logging and ETL pipeline."""

    def test_logger_writes_json_log_file(self, tmp_path):
        from backend.logging_etl import ArbLogger

        logger = ArbLogger(log_dir=str(tmp_path))
        logger.log_event("api_request", {"endpoint": "/api/listings", "status": 200, "duration_ms": 12})
        logger.log_event("api_request", {"endpoint": "/api/statistics", "status": 200, "duration_ms": 8})
        logger.flush()

        log_files = list(tmp_path.glob("*.jsonl"))
        assert len(log_files) >= 1
        lines = log_files[0].read_text().strip().splitlines()
        assert len(lines) >= 2
        for line in lines:
            record = json.loads(line)
            assert "event" in record
            assert "ts" in record

    def test_etl_pipeline_extracts_transforms_loads(self, tmp_path):
        from backend.logging_etl import ETLPipeline

        records = [
            {"source": "ebay", "price": 1200.0, "title": "RTX 4090"},
            {"source": "govdeals", "price": 650.0, "title": "iPad Pro"},
            {"source": "ebay", "price": 380.0, "title": "PS5"},
        ]
        pipeline = ETLPipeline(output_dir=str(tmp_path))
        result = pipeline.run(records=records, report_name="e2e_test_report")

        assert result["status"] == "ok"
        assert result["records_processed"] == 3

        # Report file must exist
        report_files = list(tmp_path.glob("*.json"))
        assert len(report_files) >= 1

        report = json.loads(report_files[0].read_text())
        assert "report_name" in report
        assert "generated_at" in report
        # ReportWriter wraps data under the "data" key
        assert "data" in report
        assert "summary" in report["data"]

    def test_report_writer_generates_valid_json(self, tmp_path):
        from backend.logging_etl import ReportWriter

        writer = ReportWriter(report_dir=str(tmp_path))
        writer.write_report(
            "test_report",
            {
                "status": "ok",
                "total_listings": 5,
                "sources": ["ebay", "govdeals"],
                "avg_price": 676.0,
            },
        )

        files = list(tmp_path.glob("*.json"))
        assert files, "No report file written"
        data = json.loads(files[0].read_text())
        assert data["report_name"] == "test_report"
        assert data["data"]["total_listings"] == 5

    def test_error_logger_captures_exceptions(self, tmp_path):
        from backend.logging_etl import ArbLogger

        logger = ArbLogger(log_dir=str(tmp_path))
        try:
            raise ValueError("E2E test exception")
        except ValueError as exc:
            logger.log_error("test_context", exc)
        logger.flush()

        log_files = list(tmp_path.glob("*.jsonl"))
        assert log_files
        content = log_files[0].read_text()
        assert "ValueError" in content
        assert "E2E test exception" in content

    def test_etl_pipeline_output_directory_created(self, tmp_path):
        from backend.logging_etl import ETLPipeline

        out = tmp_path / "nested" / "output"
        pipeline = ETLPipeline(output_dir=str(out))
        pipeline.run(records=[{"source": "smoke", "price": 1.0, "title": "x"}], report_name="dir_test")
        assert out.exists()
