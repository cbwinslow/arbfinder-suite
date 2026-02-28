#!/usr/bin/env python3
"""Create GitHub tracking issues for the ArbFinder Suite test/logging/ETL initiative.

Usage:
    python3 scripts/create_tracking_issues.py [--dry-run] [--repo OWNER/REPO] [--token TOKEN]

Arguments:
    --dry-run       Print issue definitions without creating them (default: True unless --token given)
    --repo          GitHub repository in OWNER/REPO format (default: cbwinslow/arbfinder-suite)
    --token         GitHub personal access token (or set GITHUB_TOKEN env var)

The script is idempotent: it checks for existing issues with the same title and
skips creation if a matching issue already exists.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


ISSUES: List[Dict[str, Any]] = [
    # -----------------------------------------------------------------------
    # Smoke & E2E testing framework
    # -----------------------------------------------------------------------
    {
        "title": "🔥 Add comprehensive smoke tests for all core components",
        "body": (
            "## Overview\n"
            "Smoke tests that verify every core component starts and responds "
            "correctly without external service dependencies.\n\n"
            "## Tests Implemented (`tests/test_smoke.py`)\n"
            "- `TestImports` – all backend modules importable\n"
            "- `TestAPIStartup` – FastAPI app starts, routes exist, `/healthz` responds `200`\n"
            "- `TestDatabaseInit` – SQLite tables created and queryable\n"
            "- `TestConfiguration` – config module loads, DB_PATH patching works\n"
            "- `TestDockerConfig` – Dockerfile and docker-compose.yml are present and valid\n"
            "- `TestCloudflareConfig` – wrangler.toml has required fields\n"
            "- `TestLoggingETL` – logging/ETL module initialises correctly\n\n"
            "## Status\n✅ Implemented in PR #68 – 40 tests, all passing."
        ),
        "labels": ["testing", "smoke-tests", "enhancement"],
    },
    {
        "title": "🧪 Add end-to-end tests for full data flow, Docker, and Cloudflare",
        "body": (
            "## Overview\n"
            "Comprehensive E2E test suite covering the full data flow from DB "
            "seeding through API responses, plus deployment configuration validation.\n\n"
            "## Tests Implemented (`tests/test_e2e.py`)\n"
            "- `TestAPIDataFlow` – seed DB → query API → validate values (16 tests)\n"
            "- `TestAPIErrorHandling` – correct HTTP status codes for bad input (9 tests)\n"
            "- `TestDockerDeployment` – Dockerfile and docker-compose are production-ready (11 tests)\n"
            "- `TestCloudflareDeployment` – wrangler.toml has all required Cloudflare bindings (9 tests)\n"
            "- `TestGitHubActionsWorkflows` – all critical CI workflows exist (5 tests)\n"
            "- `TestLoggingETLE2E` – full ETL pipeline round-trip (5 tests)\n\n"
            "## Status\n✅ Implemented in PR #68 – 55 tests, all passing."
        ),
        "labels": ["testing", "e2e", "enhancement"],
    },
    # -----------------------------------------------------------------------
    # Logging, ETL, and reporting
    # -----------------------------------------------------------------------
    {
        "title": "📊 Implement structured logging and ETL pipeline (`backend/logging_etl.py`)",
        "body": (
            "## Overview\n"
            "Sophisticated error handling, structured JSON logging (JSONL format with "
            "rotation), and an Extract-Transform-Load pipeline for generating automated "
            "reports that can be fed back into AI models.\n\n"
            "## Components\n"
            "### `get_logger(name, ...)` \n"
            "Standard `logging.Logger` with JSON formatter, stderr + rotating file handler.\n\n"
            "### `ArbLogger`\n"
            "- Writes newline-delimited JSON (`.jsonl`) to `output/logs/arb_<date>.jsonl`\n"
            "- `log_event(event, data)` – structured event records\n"
            "- `log_error(context, exc)` – exception details with full traceback\n"
            "- `flush()` – writes buffered records to disk\n\n"
            "### `ReportWriter`\n"
            "- Writes versioned JSON reports to `output/reports/`\n"
            "- Each report: `<name>_<timestamp>.json` with name + generated_at envelope\n\n"
            "### `ETLPipeline`\n"
            "- **Extract** – accepts in-memory list of dicts\n"
            "- **Transform** – normalises prices, removes nulls, adds `_processed_at`\n"
            "- **Load** – writes JSON summary report with price stats and source breakdown\n\n"
            "## Status\n✅ Implemented in PR #68."
        ),
        "labels": ["logging", "etl", "enhancement", "infrastructure"],
    },
    {
        "title": "📁 Create output directory structure for logs, reports, and errors",
        "body": (
            "## Overview\n"
            "Establish a consistent directory structure for all runtime output:\n\n"
            "```\n"
            "output/\n"
            "├── logs/      # JSONL structured logs (git-ignored)\n"
            "├── reports/   # JSON reports (git-ignored)\n"
            "└── errors/    # Error log files (git-ignored)\n"
            "```\n\n"
            "Directories are tracked via `.gitkeep` files; generated content is excluded "
            "via `.gitignore` rules so logs don't pollute the repository.\n\n"
            "## Status\n✅ Implemented in PR #68."
        ),
        "labels": ["infrastructure", "enhancement"],
    },
    # -----------------------------------------------------------------------
    # CI/CD workflows
    # -----------------------------------------------------------------------
    {
        "title": "⚙️ Add smoke & E2E CI workflow with artifact collection",
        "body": (
            "## Overview\n"
            "GitHub Actions workflow (`.github/workflows/smoke-e2e-tests.yml`) that:\n\n"
            "1. **Smoke Tests job** – runs `tests/test_smoke.py` on every push/PR, "
            "uploads JUnit XML and run logs as artifacts (30-day retention)\n"
            "2. **E2E Tests job** – runs `tests/test_e2e.py` after smoke tests pass\n"
            "3. **Coverage job** – runs full test suite with `pytest-cov`, uploads "
            "HTML coverage report and `coverage.xml`\n"
            "4. **Docker Smoke job** – validates `docker compose config`, builds the "
            "Docker image, starts a container, and hits `/healthz`\n"
            "5. **Summary job** – fails the overall workflow if any required job fails\n\n"
            "All logs and reports are collected into the `output/` directory structure "
            "and uploaded as named artifacts for post-run analysis.\n\n"
            "## Status\n✅ Implemented in PR #68."
        ),
        "labels": ["ci-cd", "testing", "enhancement"],
    },
    {
        "title": "🤖 Add ETL reports & AI feedback workflow",
        "body": (
            "## Overview\n"
            "GitHub Actions workflow (`.github/workflows/etl-reports.yml`) that runs "
            "daily at 02:00 UTC and on `workflow_dispatch`:\n\n"
            "### Jobs\n"
            "1. **Collect Artifacts** – fetches recent workflow run metadata via "
            "GitHub API (last 7 days) into `output/etl-workspace/raw/`\n"
            "2. **Generate Reports** – runs `ETLPipeline` to process workflow data, "
            "produces `ci_health_summary` and `error_analysis` JSON reports\n"
            "3. **AI Feedback Package** – aggregates all JSON reports into a single "
            "`ai_feedback_bundle.json` optimised for AI model ingestion\n\n"
            "### Report Types (selectable via `workflow_dispatch`)\n"
            "- `full` – complete CI health + error analysis\n"
            "- `test-summary` – test pass/fail statistics\n"
            "- `error-analysis` – error patterns from log files\n"
            "- `performance` – run duration trends\n\n"
            "### Artifacts\n"
            "- `etl-reports-<run>` – 90-day retention, all generated reports\n"
            "- `ai-feedback-bundle-<run>` – 90-day retention, consolidated bundle\n\n"
            "## Status\n✅ Implemented in PR #68."
        ),
        "labels": ["ci-cd", "automation", "ai", "enhancement"],
    },
    # -----------------------------------------------------------------------
    # Follow-up improvements
    # -----------------------------------------------------------------------
    {
        "title": "🐳 Add live Docker container health-check test in CI (requires Docker daemon)",
        "body": (
            "## Context\n"
            "The current smoke-e2e workflow includes a Docker job that builds the image "
            "and optionally hits `/healthz`, but the container test is `continue-on-error: true` "
            "because the multi-stage build may require secrets or long build time.\n\n"
            "## Proposed Improvements\n"
            "1. Cache Docker layers in GitHub Actions for faster builds\n"
            "2. Use `docker compose up` with `--wait` for proper dependency ordering\n"
            "3. Add a dedicated integration test that exercises the full stack "
            "(Postgres + MinIO + backend) end-to-end\n"
            "4. Fail the CI job (not just warn) if the container health check fails\n\n"
            "## Acceptance Criteria\n"
            "- [ ] Docker build completes in < 5 minutes with layer caching\n"
            "- [ ] Container health check passes within 30 seconds\n"
            "- [ ] Full stack integration test (backend + DB) passes"
        ),
        "labels": ["testing", "docker", "enhancement"],
    },
    {
        "title": "☁️ Add Cloudflare Worker live deployment smoke tests",
        "body": (
            "## Context\n"
            "E2E tests currently validate the wrangler.toml configuration but do not "
            "test against a live Cloudflare Worker deployment.\n\n"
            "## Proposed Improvements\n"
            "1. Add a `post-deploy` job to `.github/workflows/cloudflare-deploy.yml` "
            "that hits the deployed worker URL and validates:\n"
            "   - `/api/health` returns `200`\n"
            "   - `/api/listings` returns valid JSON\n"
            "   - Response time < 500 ms\n"
            "2. Store deployment URLs as GitHub Actions outputs for downstream jobs\n"
            "3. Create a `tests/test_cloudflare_live.py` module that runs against "
            "the `CLOUDFLARE_WORKER_URL` env var (skipped if not set)\n\n"
            "## Acceptance Criteria\n"
            "- [ ] Cloudflare Worker health check runs automatically after every deploy\n"
            "- [ ] Test results uploaded as artifacts\n"
            "- [ ] Deployment URL posted as PR comment"
        ),
        "labels": ["testing", "cloudflare", "enhancement"],
    },
    {
        "title": "📈 Implement performance/load testing with automated reporting",
        "body": (
            "## Context\n"
            "The repository has `tests/load_test.py` but it is not integrated into "
            "the main CI pipeline and results are not persisted or trended.\n\n"
            "## Proposed Improvements\n"
            "1. Add a scheduled workflow (weekly) that runs the load test and stores "
            "results in `output/reports/` as a JSON report\n"
            "2. Integrate results into the ETL pipeline so performance trends are "
            "included in the AI feedback bundle\n"
            "3. Alert (via GitHub issue or Slack) when p95 latency exceeds threshold\n"
            "4. Add `pytest-benchmark` for micro-benchmarks of hot paths "
            "(e.g., listing search, fuzzy match)\n\n"
            "## Acceptance Criteria\n"
            "- [ ] Load test runs weekly via GitHub Actions\n"
            "- [ ] Results persisted and trended over time\n"
            "- [ ] Alert on regression (p95 > 1 s for `/api/listings`)"
        ),
        "labels": ["testing", "performance", "enhancement"],
    },
]


def _get_existing_titles(repo: str, token: str) -> set:
    """Return the titles of all open issues in *repo*."""
    titles = set()
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100&page={page}"
        req = urllib.request.Request(url, headers=_headers(token))
        try:
            with urllib.request.urlopen(req) as resp:
                issues = json.loads(resp.read())
        except urllib.error.URLError as e:
            print(f"Warning: could not fetch existing issues: {e}", file=sys.stderr)
            return titles
        if not issues:
            break
        for issue in issues:
            titles.add(issue["title"])
        page += 1
    return titles


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _ensure_label(repo: str, token: str, label: str) -> None:
    """Create *label* in *repo* if it doesn't already exist."""
    url = f"https://api.github.com/repos/{repo}/labels"
    # List existing labels (simplified – just try to create; ignore 422 duplicate)
    colour_map = {
        "smoke-tests": "0e8a16",
        "e2e": "0075ca",
        "logging": "e4e669",
        "etl": "d93f0b",
        "infrastructure": "c2e0c6",
        "ci-cd": "bfd4f2",
        "cloudflare": "f9d0c4",
        "ai": "5319e7",
        "performance": "fef2c0",
        "testing": "006b75",
        "automation": "1d76db",
        "docker": "0052cc",
        "enhancement": "a2eeef",
    }
    payload = json.dumps({
        "name": label,
        "color": colour_map.get(label, "ededed"),
    }).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers(token), method="POST")
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code != 422:  # 422 = already exists
            print(f"  ⚠ Could not create label '{label}': {e}", file=sys.stderr)


def create_issues(
    repo: str,
    token: str,
    dry_run: bool = True,
) -> None:
    """Create all tracking issues in *repo*."""
    if dry_run:
        print(f"[DRY RUN] Would create {len(ISSUES)} issues in {repo}:\n")
        for i, issue in enumerate(ISSUES, 1):
            print(f"  {i}. {issue['title']}")
            print(f"     Labels: {', '.join(issue.get('labels', []))}")
        return

    print(f"Fetching existing issues from {repo}…")
    existing = _get_existing_titles(repo, token)
    print(f"Found {len(existing)} existing open issues.\n")

    url = f"https://api.github.com/repos/{repo}/issues"
    created = 0
    skipped = 0

    for issue in ISSUES:
        title = issue["title"]
        if title in existing:
            print(f"  ⏭  SKIP (exists): {title}")
            skipped += 1
            continue

        # Ensure labels exist
        for label in issue.get("labels", []):
            _ensure_label(repo, token, label)

        payload = json.dumps({
            "title": title,
            "body": issue["body"],
            "labels": issue.get("labels", []),
        }).encode()
        req = urllib.request.Request(url, data=payload, headers=_headers(token), method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                created_issue = json.loads(resp.read())
            print(f"  ✅ Created #{created_issue['number']}: {title}")
            created += 1
            time.sleep(0.5)  # be polite to the API
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"  ❌ FAILED: {title}\n     {e.code}: {body}", file=sys.stderr)

    print(f"\nDone: {created} created, {skipped} skipped.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="cbwinslow/arbfinder-suite", help="OWNER/REPO")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""), help="GitHub token")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Print issues without creating (default: True if no token)",
    )
    args = parser.parse_args()

    dry_run = args.dry_run
    if dry_run is None:
        dry_run = not bool(args.token)

    if not dry_run and not args.token:
        print("Error: --token or GITHUB_TOKEN required when not using --dry-run.", file=sys.stderr)
        sys.exit(1)

    create_issues(repo=args.repo, token=args.token, dry_run=dry_run)


if __name__ == "__main__":
    main()
