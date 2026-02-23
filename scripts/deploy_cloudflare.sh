#!/usr/bin/env bash
# ============================================================
# ArbFinder Cloudflare Pages Deployment Script
# Usage: ./scripts/deploy_cloudflare.sh [--preview|--production]
#
# Prerequisites:
#   1. npm install -g wrangler  (or npx wrangler)
#   2. wrangler login           (authenticate with Cloudflare)
#   3. Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars
#      or configure them in .env
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── Defaults ──────────────────────────────────────────────────
ENVIRONMENT="preview"
PROJECT_NAME="${CF_PAGES_PROJECT:-arbfinder}"
FRONTEND_DIR="$ROOT_DIR/frontend"

for arg in "$@"; do
  case "$arg" in
    --production|-p) ENVIRONMENT="production" ;;
    --preview)       ENVIRONMENT="preview" ;;
    --help|-h)
      sed -n '2,12p' "$0"
      exit 0 ;;
  esac
done

# ── Load env ──────────────────────────────────────────────────
if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a; source "$ROOT_DIR/.env"; set +a
fi

# ── Check credentials ─────────────────────────────────────────
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  warn "CLOUDFLARE_API_TOKEN not set."
  warn "Set it in .env or export it before running this script."
  warn "Create a token at: https://dash.cloudflare.com/profile/api-tokens"
fi

# ── Find wrangler ─────────────────────────────────────────────
if command -v wrangler &>/dev/null; then
  WRANGLER="wrangler"
elif command -v npx &>/dev/null; then
  WRANGLER="npx wrangler"
else
  error "wrangler not found. Install with: npm install -g wrangler"
  exit 1
fi

info "Using wrangler: $($WRANGLER --version 2>&1 | head -1)"

# ── Build frontend ────────────────────────────────────────────
info "Building Next.js frontend for static export..."
cd "$FRONTEND_DIR"

if [[ ! -d "node_modules" ]]; then
  info "Installing frontend dependencies..."
  npm ci
fi

# Ensure next.config.js has output: 'export'
if ! grep -q "output.*export" next.config.js 2>/dev/null; then
  warn "next.config.js may not have 'output: export'. Cloudflare Pages requires static export."
fi

NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-}" npm run build
success "Frontend built. Output: $FRONTEND_DIR/out"

cd "$ROOT_DIR"

# ── Deploy to Cloudflare Pages ────────────────────────────────
OUT_DIR="$FRONTEND_DIR/out"
if [[ ! -d "$OUT_DIR" ]]; then
  # Next.js 14 default is .next/ for static export
  OUT_DIR="$FRONTEND_DIR/.next"
fi

info "Deploying to Cloudflare Pages ($ENVIRONMENT)..."
info "Project: $PROJECT_NAME | Directory: $OUT_DIR"

if [[ "$ENVIRONMENT" == "production" ]]; then
  $WRANGLER pages deploy "$OUT_DIR" \
    --project-name "$PROJECT_NAME" \
    --branch main \
    --commit-dirty=true
else
  $WRANGLER pages deploy "$OUT_DIR" \
    --project-name "$PROJECT_NAME" \
    --commit-dirty=true
fi

success "Deployed to Cloudflare Pages ($ENVIRONMENT)!"
echo ""
if [[ "$ENVIRONMENT" == "production" ]]; then
  echo -e "  Production URL: ${GREEN}https://${PROJECT_NAME}.pages.dev${NC}"
else
  echo -e "  Preview URL:    ${GREEN}Check output above for the preview URL${NC}"
fi
echo ""
info "View deployments: https://dash.cloudflare.com/pages"
