#!/usr/bin/env bash
# ============================================================
# ArbFinder Remote Server Deployment Script
# Usage: ./scripts/deploy_remote.sh [options]
#
# Options:
#   -h HOST         Remote host (e.g., user@example.com)
#   -p PORT         SSH port (default: 22)
#   -d DIR          Remote deploy directory (default: /opt/arbfinder)
#   --no-build      Skip building Docker images locally
#   --restart-only  Just restart the remote stack
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
REMOTE_HOST=""
SSH_PORT=22
REMOTE_DIR="/opt/arbfinder"
NO_BUILD=false
RESTART_ONLY=false
IMAGE_TAG="arbfinder:latest"

# ── Parse args ────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h) REMOTE_HOST="$2"; shift 2 ;;
    -p) SSH_PORT="$2"; shift 2 ;;
    -d) REMOTE_DIR="$2"; shift 2 ;;
    --no-build)      NO_BUILD=true; shift ;;
    --restart-only)  RESTART_ONLY=true; shift ;;
    --help)
      sed -n '2,15p' "$0"
      exit 0 ;;
    *) error "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$REMOTE_HOST" ]]; then
  error "Remote host is required. Use: $0 -h user@host"
  exit 1
fi

SSH_OPTS="-p $SSH_PORT -o StrictHostKeyChecking=yes"
SCP_OPTS="-P $SSH_PORT -o StrictHostKeyChecking=yes"

# NOTE: If this is the first connection to the host, add it to known_hosts first:
#   ssh-keyscan -p "$SSH_PORT" "$REMOTE_HOST" >> ~/.ssh/known_hosts

remote() { ssh $SSH_OPTS "$REMOTE_HOST" "$@"; }

cd "$ROOT_DIR"

# ── Restart only ──────────────────────────────────────────────
if [[ "$RESTART_ONLY" == true ]]; then
  info "Restarting stack on $REMOTE_HOST:$REMOTE_DIR ..."
  remote "cd $REMOTE_DIR && docker compose restart"
  success "Stack restarted."
  exit 0
fi

# ── Build ─────────────────────────────────────────────────────
if [[ "$NO_BUILD" == false ]]; then
  info "Building Docker image locally..."
  docker build -t "$IMAGE_TAG" "$ROOT_DIR"
  success "Image built: $IMAGE_TAG"
fi

# ── Export and transfer image ──────────────────────────────────
info "Saving image and transferring to $REMOTE_HOST..."
docker save "$IMAGE_TAG" | ssh $SSH_OPTS "$REMOTE_HOST" "docker load"
success "Image transferred."

# ── Copy compose files ────────────────────────────────────────
info "Copying deployment files to $REMOTE_HOST:$REMOTE_DIR ..."
remote "mkdir -p $REMOTE_DIR"
scp $SCP_OPTS \
  "$ROOT_DIR/docker-compose.yml" \
  "$ROOT_DIR/.env.example" \
  "$REMOTE_HOST:$REMOTE_DIR/"

# Copy .env if present (and not example)
if [[ -f "$ROOT_DIR/.env" ]]; then
  warn "Copying .env to remote (ensure this is safe for your environment)"
  scp $SCP_OPTS "$ROOT_DIR/.env" "$REMOTE_HOST:$REMOTE_DIR/.env"
else
  info "No .env found locally - copying .env.example as .env"
  remote "cp $REMOTE_DIR/.env.example $REMOTE_DIR/.env 2>/dev/null || true"
fi

# ── Deploy ────────────────────────────────────────────────────
info "Starting stack on remote..."
remote "cd $REMOTE_DIR && docker compose pull 2>/dev/null || true && docker compose up -d --remove-orphans"

success "Deployed to $REMOTE_HOST!"
echo ""
echo -e "  Backend:  ${GREEN}http://$REMOTE_HOST:8080${NC}"
echo -e "  Frontend: ${GREEN}http://$REMOTE_HOST:3000${NC}"
echo ""
info "Monitor with: ssh $REMOTE_HOST 'cd $REMOTE_DIR && docker compose logs -f'"
