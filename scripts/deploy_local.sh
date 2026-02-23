#!/usr/bin/env bash
# ============================================================
# ArbFinder Local Development Startup Script
# Usage: ./scripts/deploy_local.sh [--frontend-only|--backend-only]
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

FRONTEND_ONLY=false
BACKEND_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --frontend-only) FRONTEND_ONLY=true ;;
    --backend-only)  BACKEND_ONLY=true ;;
    --help|-h)
      echo "Usage: $0 [--frontend-only|--backend-only]"
      echo "  --frontend-only  Start only the Next.js frontend (port 3000)"
      echo "  --backend-only   Start only the FastAPI backend (port 8080)"
      exit 0
      ;;
  esac
done

# Load .env if it exists
if [[ -f "$ROOT_DIR/.env" ]]; then
  info "Loading environment from .env"
  set -a; source "$ROOT_DIR/.env"; set +a
fi

cleanup() {
  info "Shutting down..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

cd "$ROOT_DIR"

# ── Backend ──────────────────────────────────────────────────
if [[ "$FRONTEND_ONLY" == false ]]; then
  info "Starting FastAPI backend on http://localhost:8080 ..."

  if command -v uvicorn &>/dev/null; then
    ARBF_DB="${ARBF_DB:-$HOME/.arb_finder.sqlite3}" \
    PYTHONPATH="$ROOT_DIR" \
      uvicorn backend.api.main:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    success "Backend PID: $BACKEND_PID"
  else
    error "uvicorn not found. Install with: pip install uvicorn"
    exit 1
  fi
fi

# ── Frontend ─────────────────────────────────────────────────
if [[ "$BACKEND_ONLY" == false ]]; then
  if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
    info "Installing frontend dependencies..."
    (cd "$ROOT_DIR/frontend" && npm ci)
  fi

  info "Starting Next.js frontend on http://localhost:3000 ..."
  NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-http://localhost:8080}" \
    (cd "$ROOT_DIR/frontend" && npm run dev) &
  FRONTEND_PID=$!
  success "Frontend PID: $FRONTEND_PID"
fi

# ── Wait ─────────────────────────────────────────────────────
info "Press Ctrl+C to stop all services"
echo ""
echo -e "  Backend:  ${GREEN}http://localhost:8080${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "  API docs: ${GREEN}http://localhost:8080/docs${NC}"
echo ""

wait
