#!/bin/bash

#############################################################################
# Worker Binding Script for Cloudflare Pages
#
# This script binds Cloudflare Workers to a Pages project to handle
# backend API calls, scheduled tasks, and other serverless functions
#
# Usage:
#   ./scripts/cloudflare/bind_workers.sh [--project-name NAME]
#
# Requirements:
#   - wrangler CLI installed
#   - Cloudflare account with API token
#   - Pages project already created
#   - Worker already deployed
#############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.cloudflare-config.json"

# Default values
PROJECT_NAME="arbfinder-suite"
WORKER_NAME="arbfinder-worker"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --worker-name)
            WORKER_NAME="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check wrangler
    if ! command -v wrangler &> /dev/null; then
        log_error "Wrangler CLI not found. Please install: npm install -g wrangler"
        exit 1
    fi
    log_success "Wrangler $(wrangler --version)"
    
    # Check authentication
    if ! wrangler whoami &> /dev/null; then
        log_error "Not authenticated with Cloudflare. Please run: wrangler login"
        exit 1
    fi
    log_success "Authenticated with Cloudflare"
}

# Check if Pages project exists
check_pages_project() {
    log_info "Checking Pages project..."
    
    local project_exists=$(wrangler pages project list 2>/dev/null | grep -c "$PROJECT_NAME" || true)
    
    if [ "$project_exists" -eq 0 ]; then
        log_error "Pages project '$PROJECT_NAME' not found"
        log_info "Please deploy to Pages first: ./scripts/cloudflare/deploy_pages.sh"
        exit 1
    fi
    
    log_success "Pages project '$PROJECT_NAME' exists"
}

# Check if Worker exists
check_worker() {
    log_info "Checking Worker deployment..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # List workers and check if our worker exists
    local worker_exists=$(wrangler deployments list 2>/dev/null | grep -c "$WORKER_NAME" || true)
    
    if [ "$worker_exists" -eq 0 ]; then
        log_warning "Worker '$WORKER_NAME' not found or not deployed"
        log_info "Deploying Worker..."
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        
        # Deploy worker
        wrangler deploy
        log_success "Worker deployed"
    else
        log_success "Worker '$WORKER_NAME' exists"
    fi
}

# Configure service bindings
configure_service_bindings() {
    log_info "Configuring service bindings..."
    
    log_info "Service bindings allow your Pages functions to call Workers"
    log_warning "Note: Service bindings must be configured via wrangler.toml or Cloudflare dashboard"
    
    echo ""
    log_info "To bind Workers to Pages:"
    log_info "1. Create a Pages function in frontend/functions/ (if needed)"
    log_info "2. Configure service bindings in wrangler.toml for Pages"
    log_info "3. Or use the Cloudflare dashboard:"
    log_info "   a. Go to Pages project settings"
    log_info "   b. Navigate to Functions > Settings"
    log_info "   c. Add service bindings to your Worker"
}

# Create Pages Functions directory structure
setup_pages_functions() {
    log_info "Setting up Pages Functions..."
    
    local functions_dir="$PROJECT_ROOT/frontend/functions"
    
    if [ ! -d "$functions_dir" ]; then
        mkdir -p "$functions_dir/api"
        log_success "Created functions directory"
        
        # Create example API function
        cat > "$functions_dir/api/[[path]].ts" << 'EOF'
/**
 * Cloudflare Pages Function
 * Proxies API requests to the Worker
 */

interface Env {
  WORKER: Fetcher;
}

export async function onRequest(context: {
  request: Request;
  env: Env;
  params: { path: string[] };
}): Promise<Response> {
  const { request, env, params } = context;
  
  // If Worker binding is available, proxy to it
  if (env.WORKER) {
    return env.WORKER.fetch(request);
  }
  
  // Otherwise, return a fallback response
  return new Response(
    JSON.stringify({
      error: 'Worker not bound',
      message: 'Please configure Worker service binding'
    }),
    {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    }
  );
}
EOF
        
        log_success "Created example Pages function"
        log_info "Function created at: frontend/functions/api/[[path]].ts"
    else
        log_success "Functions directory already exists"
    fi
}

# Create wrangler configuration for Pages
create_pages_wrangler_config() {
    log_info "Creating Pages wrangler configuration..."
    
    local pages_wrangler="$PROJECT_ROOT/frontend/wrangler.toml"
    
    if [ ! -f "$pages_wrangler" ]; then
        cat > "$pages_wrangler" << EOF
name = "$PROJECT_NAME"
compatibility_date = "2024-01-01"

# Pages configuration
pages_build_output_dir = "out"

# Service bindings - bind to Worker
[[service_bindings]]
binding = "WORKER"
service = "$WORKER_NAME"
environment = "production"

# Environment variables for Pages Functions
[env.production.vars]
ENVIRONMENT = "production"

[env.preview.vars]
ENVIRONMENT = "preview"
EOF
        
        log_success "Created wrangler.toml for Pages"
        log_info "Configuration saved to: frontend/wrangler.toml"
    else
        log_success "Pages wrangler.toml already exists"
    fi
}

# Display binding instructions
display_instructions() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "Worker Binding Configuration Complete! 🎉"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo "Configuration Summary:"
    echo "  Pages Project: $PROJECT_NAME"
    echo "  Worker: $WORKER_NAME"
    echo "  Functions Directory: frontend/functions/"
    echo "  Wrangler Config: frontend/wrangler.toml"
    echo ""
    
    echo "Next Steps:"
    echo ""
    echo "  1. Deploy with service bindings:"
    echo "     cd frontend"
    echo "     wrangler pages deploy out --project-name=$PROJECT_NAME"
    echo ""
    echo "  2. Or configure bindings via Cloudflare Dashboard:"
    echo "     a. Go to https://dash.cloudflare.com/pages"
    echo "     b. Select '$PROJECT_NAME'"
    echo "     c. Go to Settings > Functions"
    echo "     d. Add Service Binding:"
    echo "        - Variable: WORKER"
    echo "        - Service: $WORKER_NAME"
    echo ""
    echo "  3. Test the integration:"
    echo "     curl https://YOUR_PAGES_URL/api/health"
    echo ""
    echo "  4. Monitor logs:"
    echo "     wrangler pages deployment tail --project-name=$PROJECT_NAME"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🔗 ArbFinder Suite - Worker Binding Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    check_prerequisites
    check_pages_project
    check_worker
    configure_service_bindings
    setup_pages_functions
    create_pages_wrangler_config
    display_instructions
}

# Run main function
main "$@"
