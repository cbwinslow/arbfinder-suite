# ArbFinder Suite — Bug Report & Tasks List

**Date**: 2026-02-23  
**Version**: 0.4.0  
**Assessment**: Comprehensive review of backend, frontend, tests, and deployment infrastructure.

---

## 🐛 Bugs Found & Fixed

### BUG-001 — `WatchMode._find_new_deals()` crashes on `None` discount ✅ FIXED
- **File**: `backend/watch.py` line 88
- **Severity**: High — crashes at runtime when any listing has no comparable price
- **Root cause**: `result.get("discount_vs_avg_pct", 0)` returns `None` (not 0) when the
  key exists with value `None`; subsequent `None >= threshold` raises `TypeError`.
- **Fix**: Changed to `result.get("discount_vs_avg_pct") or 0` to coerce `None` → `0`.

### BUG-002 — `WatchMode.run()` off-by-one in iteration counter ✅ FIXED
- **File**: `backend/watch.py` lines 40–45
- **Severity**: Medium — `max_iterations=2` causes 2 search calls (correct) but the loop
  breaks after incrementing to 3, so `wm.iteration == 3` not 2, and logs "completed after
  3 iterations" when only 2 were executed.
- **Fix**: Moved the limit check *before* `self.iteration += 1` so the counter accurately
  reflects completed iterations.

### BUG-003 — Deprecated `regex=` parameter in FastAPI Query ✅ FIXED
- **Files**: `backend/api/main.py`, `backend/api/alerts.py`, `backend/api/crews.py`,
  `backend/api/snipes.py`
- **Severity**: Low — emits `FastAPIDeprecationWarning` on every request; will break in a
  future FastAPI release.
- **Fix**: Replaced `regex=` with the current `pattern=` keyword argument.

---

## ⚠️ Known Issues (Not Yet Fixed)

### ISSUE-001 — `DB_PATH` set at module import time in API
- **File**: `backend/api/main.py` line 32
- **Severity**: Medium — `DB_PATH = os.getenv("ARBF_DB", ...)` is evaluated once at import.
  Changing `ARBF_DB` env var after import (e.g., in tests or dynamic config reload) has no
  effect without a process restart.
- **Recommendation**: Wrap DB access in a function that reads the env var lazily, or use
  dependency injection via FastAPI's `Depends()`.

### ISSUE-002 — ManualImport CSV silently skips rows with bad price
- **File**: `backend/arb_finder.py` — `ManualImport.search()`
- **Severity**: Low — rows with non-numeric price fields are swallowed without a warning.
- **Recommendation**: Log a warning with the row number/content when skipping.

### ISSUE-003 — PoliteClient retry loop returns `None` on all retries exhausted
- **File**: `backend/arb_finder.py` — `PoliteClient.get()`
- **Severity**: Medium — if all `RETRY_MAX` attempts fail, `resp` is `None` but is returned
  as-is. Callers may fail with `AttributeError` when accessing `.text`.
- **Recommendation**: Raise a `httpx.HTTPError` after exhausting retries instead of
  returning `None`.

### ISSUE-004 — CORS allows `"*"` (all origins) in addition to `FRONTEND_ORIGIN`
- **File**: `backend/api/main.py` lines 37–42
- **Severity**: Medium (security) — `allow_origins=[FRONTEND_ORIGIN, "*"]` effectively
  allows every origin. The explicit `"*"` should be removed; use `FRONTEND_ORIGIN` only.
- **Recommendation**: Remove `"*"` from `allow_origins` and ensure `FRONTEND_ORIGIN` covers
  all legitimate origins via a configurable list.

### ISSUE-005 — Frontend `next.config.js` needs `output: 'export'` for Cloudflare Pages
- **File**: `frontend/next.config.js`
- **Severity**: Low — static export (`output: 'export'`) is required for Cloudflare Pages
  but may not be set by default.
- **Recommendation**: Add `output: 'export'` when deploying to Cloudflare.

### ISSUE-006 — No health-check endpoint for the backend liveness probe
- **File**: `backend/api/main.py`
- **Severity**: Low — the Dockerfile `HEALTHCHECK` hits `/` which returns API metadata
  rather than a lightweight `/healthz` endpoint.
- **Recommendation**: Add a dedicated `/healthz` route that returns `{"status": "ok"}`.

### ISSUE-007 — Frontend missing environment variable validation
- **File**: `frontend/app/`
- **Severity**: Low — `NEXT_PUBLIC_API_BASE` defaults to an empty string if not set;
  API calls will silently fail.
- **Recommendation**: Add a startup check that logs a clear warning if the variable is missing.

---

## 📋 Tasks List

### Priority: High

| ID      | Task                                                          | File(s)                          | Status      |
|---------|---------------------------------------------------------------|----------------------------------|-------------|
| TASK-01 | Fix PoliteClient returning `None` after exhausting retries    | `backend/arb_finder.py`          | Open        |
| TASK-02 | Remove `"*"` from CORS `allow_origins`                        | `backend/api/main.py`            | Open        |
| TASK-03 | Make `DB_PATH` lazy (read env var per request)                | `backend/api/main.py`            | Open        |
| TASK-04 | Add `/healthz` endpoint                                       | `backend/api/main.py`            | Open        |

### Priority: Medium

| ID      | Task                                                          | File(s)                          | Status      |
|---------|---------------------------------------------------------------|----------------------------------|-------------|
| TASK-05 | Add warning log when ManualImport skips invalid rows          | `backend/arb_finder.py`          | Open        |
| TASK-06 | Validate `NEXT_PUBLIC_API_BASE` at frontend startup           | `frontend/app/`                  | Open        |
| TASK-07 | Add `output: 'export'` to `next.config.js` for CF Pages      | `frontend/next.config.js`        | Open        |
| TASK-08 | Increase test coverage of `backend/api/` routers              | `tests/`                         | In Progress |
| TASK-09 | Add integration tests for watch mode with real search func    | `tests/test_watch.py`            | Open        |

### Priority: Low

| ID      | Task                                                          | File(s)                          | Status      |
|---------|---------------------------------------------------------------|---------------------------------------|-------------|
| TASK-10 | Upgrade Next.js from 14.2.35 to latest stable                 | `frontend/package.json`               | Open        |
| TASK-11 | Add OpenAPI schema tests (validate response models)           | `tests/`                              | Open        |
| TASK-12 | Add frontend unit tests (Jest/Playwright)                     | `frontend/`                           | Open        |
| TASK-13 | Add load test scenarios for high-concurrency API calls        | `tests/load_test.py`                  | Open        |
| TASK-14 | Automate DB backup via cron in remote deployment              | `scripts/deploy_remote.sh`            | Open        |

---

## 📊 Test Coverage Summary

| Module                        | Before | After  |
|-------------------------------|--------|--------|
| `backend/config.py`           | 86%    | 86%    |
| `backend/cli.py`              | 35%    | 35%    |
| `backend/utils.py`            | 0%     | **100%** |
| `backend/watch.py`            | 0%     | **96%** |
| `backend/arb_finder.py`       | 0%     | **~35%** |
| `backend/api/main.py`         | 4%     | **~60%** |
| **Overall**                   | **3%** | **~22%** |

> Note: Modules requiring external services (crawl4ai, openrouter, minio) are excluded from
> automated test coverage by design. Mocks or integration tests with service stubs are
> recommended to increase their coverage.

---

## 🚀 Deployment Options Added

| Method           | Script                             | Description                          |
|------------------|------------------------------------|--------------------------------------|
| Local dev        | `scripts/deploy_local.sh`          | Start backend + frontend locally     |
| Docker           | `scripts/deploy_docker.sh`         | Docker Compose full-stack            |
| Remote server    | `scripts/deploy_remote.sh`         | Deploy via SSH to a VPS/bare metal   |
| Cloudflare Pages | `scripts/deploy_cloudflare.sh`     | Static frontend to Cloudflare Pages  |
| Kubernetes       | `infrastructure/` (existing)       | Pulumi-based infra (in progress)     |

---

## 🔍 UI/Feature Assessment

### Frontend (Next.js 14)
- ✅ Pages render correctly: home, listings, search, comps, stats, settings
- ✅ Tailwind CSS styling applied throughout
- ✅ lucide-react icons integrated
- ⚠️ No loading skeletons for async data fetches — can appear slow on first load
- ⚠️ No error boundary components — API failures show blank sections
- ⚠️ Mobile responsiveness not fully tested

### Backend (FastAPI)
- ✅ CRUD endpoints for listings and comps
- ✅ Pagination and filtering on `/api/listings`
- ✅ Full-text search on listings and comps
- ✅ Statistics endpoint
- ✅ Stripe checkout session endpoint (requires key)
- ⚠️ No authentication/authorization on any endpoints
- ⚠️ Input sanitization relies entirely on Pydantic — no additional XSS protection needed
  for REST JSON APIs, but SQL injection via the `ORDER BY` clause is mitigated by regex
  validation (now using `pattern=`).

### CLI
- ✅ Subcommands: search, watch, config, server, db
- ✅ Config file support (load/save)
- ✅ CSV/JSON export
- ✅ Watch mode with configurable interval
