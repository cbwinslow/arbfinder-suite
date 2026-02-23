#!/usr/bin/env bash
# ============================================================
# ArbFinder Docker Deployment Helper
# Usage: ./scripts/deploy_docker.sh [build|up|down|logs|status]
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── Require Docker ────────────────────────────────────────────
require_docker() {
  if ! command -v docker &>/dev/null; then
    error "Docker is not installed. Install from: https://docs.docker.com/get-docker/"
    exit 1
  fi
  if ! docker info &>/dev/null; then
    error "Docker daemon is not running. Start Docker and retry."
    exit 1
  fi
}

CMD="${1:-up}"

cd "$ROOT_DIR"

# Load .env if present
if [[ -f ".env" ]]; then
  info "Loading environment from .env"
  set -a; source ".env"; set +a
fi

case "$CMD" in

  # ── build ──────────────────────────────────────────────────
  build)
    require_docker
    info "Building ArbFinder Docker images..."
    docker compose build --no-cache
    success "Build complete."
    ;;

  # ── up ─────────────────────────────────────────────────────
  up)
    require_docker
    info "Starting ArbFinder stack (backend + frontend + postgres + minio)..."
    docker compose up -d --build
    echo ""
    success "Stack is up!"
    echo -e "  Backend:   ${GREEN}http://localhost:8080${NC}"
    echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
    echo -e "  API docs:  ${GREEN}http://localhost:8080/docs${NC}"
    echo -e "  MinIO UI:  ${GREEN}http://localhost:9001${NC}"
    echo ""
    info "Run '${BASH_SOURCE[0]} logs' to follow logs."
    ;;

  # ── down ───────────────────────────────────────────────────
  down)
    require_docker
    info "Stopping ArbFinder stack..."
    docker compose down
    success "Stack stopped."
    ;;

  # ── logs ───────────────────────────────────────────────────
  logs)
    require_docker
    docker compose logs -f "${2:-}"
    ;;

  # ── status ─────────────────────────────────────────────────
  status)
    require_docker
    docker compose ps
    ;;

  # ── restart ────────────────────────────────────────────────
  restart)
    require_docker
    info "Restarting ArbFinder stack..."
    docker compose restart "${2:-}"
    success "Restarted."
    ;;

  # ── clean ──────────────────────────────────────────────────
  clean)
    require_docker
    warn "This will stop and remove all containers AND volumes!"
    read -r -p "Are you sure? [y/N] " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      docker compose down -v --remove-orphans
      docker system prune -f
      success "Cleaned."
    else
      info "Aborted."
    fi
    ;;

  # ── help ───────────────────────────────────────────────────
  help|-h|--help)
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build    Build Docker images"
    echo "  up       Start the full stack (default)"
    echo "  down     Stop the stack"
    echo "  logs     Follow container logs (optionally: logs <service>)"
    echo "  status   Show container status"
    echo "  restart  Restart stack (optionally: restart <service>)"
    echo "  clean    Remove containers and volumes (destructive)"
    ;;

  *)
    error "Unknown command: $CMD"
    echo "Run '$0 help' for usage."
    exit 1
    ;;

esac
