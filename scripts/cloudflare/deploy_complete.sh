#!/bin/bash

#############################################################################
# Complete Cloudflare Deployment Orchestrator
#
# This script orchestrates the complete deployment of ArbFinder Suite to
# Cloudflare platform, including:
#   - D1 Database setup
#   - R2 Storage buckets
#   - KV Namespaces
#   - Worker deployment
#   - Pages deployment
#   - Worker-Pages binding
#   - Environment configuration
#   - Testing and verification
#
# Usage:
#   ./scripts/cloudflare/deploy_complete.sh [OPTIONS]
#
# Options:
#   --skip-setup     Skip infrastructure setup (D1, R2, KV)
#   --skip-worker    Skip Worker deployment
#   --skip-pages     Skip Pages deployment
#   --skip-test      Skip testing and verification
#   --project-name   Pages project name (default: arbfinder-suite)
#   --worker-name    Worker name (default: arbfinder-worker)
#
# Requirements:
#   - wrangler CLI installed (npm install -g wrangler)
#   - Cloudflare account with API token
#   - Node.js v18+ installed
#
# Environment Variables:
#   CLOUDFLARE_API_TOKEN - API token (or use: wrangler login)
#   CLOUDFLARE_ACCOUNT_ID - Your Cloudflare account ID (optional)
#############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.cloudflare-config.json"

# Default values
SKIP_SETUP=false
SKIP_WORKER=false
SKIP_PAGES=false
SKIP_TEST=false
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

log_step() {
    echo -e "${CYAN}▶${NC} $1"
}

# Progress tracking
TOTAL_STEPS=8
CURRENT_STEP=0

progress_step() {
    ((CURRENT_STEP++))
    local step_name=$1
    echo ""
    echo -e "${MAGENTA}[Step $CURRENT_STEP/$TOTAL_STEPS]${NC} $step_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-setup)
            SKIP_SETUP=true
            shift
            ;;
        --skip-worker)
            SKIP_WORKER=true
            shift
            ;;
        --skip-pages)
            SKIP_PAGES=true
            shift
            ;;
        --skip-test)
            SKIP_TEST=true
            shift
            ;;
        --project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --worker-name)
            WORKER_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-setup      Skip infrastructure setup"
            echo "  --skip-worker     Skip Worker deployment"
            echo "  --skip-pages      Skip Pages deployment"
            echo "  --skip-test       Skip testing"
            echo "  --project-name    Pages project name"
            echo "  --worker-name     Worker name"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display banner
show_banner() {
    clear
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🚀 ArbFinder Suite - Complete Cloudflare Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This script will deploy:"
    echo "  • Cloudflare D1 Database"
    echo "  • R2 Storage Buckets"
    echo "  • KV Namespaces"
    echo "  • Cloudflare Worker"
    echo "  • Cloudflare Pages (Frontend)"
    echo "  • Worker-Pages Bindings"
    echo ""
    echo "Configuration:"
    echo "  Project Name: $PROJECT_NAME"
    echo "  Worker Name: $WORKER_NAME"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Check all prerequisites
check_all_prerequisites() {
    progress_step "Checking Prerequisites"
    
    log_info "Checking required tools..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found. Please install Node.js v18 or higher."
        exit 1
    fi
    local node_version=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$node_version" -lt 18 ]; then
        log_error "Node.js version must be 18 or higher. Current: $(node --version)"
        exit 1
    fi
    log_success "Node.js $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found. Please install npm."
        exit 1
    fi
    log_success "npm $(npm --version)"
    
    # Check wrangler
    if ! command -v wrangler &> /dev/null; then
        log_warning "Wrangler CLI not found. Installing..."
        npm install -g wrangler@latest
        log_success "Wrangler installed"
    else
        log_success "Wrangler $(wrangler --version)"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git not found. Please install git."
        exit 1
    fi
    log_success "Git installed"
    
    # Check jq (for JSON processing)
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found (optional, but recommended)"
    else
        log_success "jq installed"
    fi
    
    # Check authentication
    log_info "Checking Cloudflare authentication..."
    if ! wrangler whoami &> /dev/null 2>&1; then
        log_warning "Not authenticated with Cloudflare"
        log_info "Please authenticate: wrangler login"
        
        # Try to login
        if command -v wrangler &> /dev/null; then
            wrangler login
        fi
    else
        log_success "Authenticated with Cloudflare"
    fi
}

# Run infrastructure setup
run_infrastructure_setup() {
    if [ "$SKIP_SETUP" = true ]; then
        log_warning "Skipping infrastructure setup"
        return
    fi
    
    progress_step "Setting up Infrastructure (D1, R2, KV)"
    
    log_info "Running infrastructure setup script..."
    
    if [ -f "$SCRIPT_DIR/setup.sh" ]; then
        bash "$SCRIPT_DIR/setup.sh" || {
            log_error "Infrastructure setup failed"
            exit 1
        }
    else
        log_warning "setup.sh not found, running manual setup..."
        
        cd "$PROJECT_ROOT/cloudflare"
        
        # Create D1 database
        log_info "Creating D1 database..."
        wrangler d1 create arbfinder-db || log_warning "D1 database may already exist"
        
        # Create R2 buckets
        log_info "Creating R2 buckets..."
        wrangler r2 bucket create arbfinder-images || log_warning "Images bucket may already exist"
        wrangler r2 bucket create arbfinder-data || log_warning "Data bucket may already exist"
        wrangler r2 bucket create arbfinder-backups || log_warning "Backups bucket may already exist"
        
        # Create KV namespaces
        log_info "Creating KV namespaces..."
        wrangler kv:namespace create CACHE || log_warning "CACHE namespace may already exist"
        wrangler kv:namespace create SESSIONS || log_warning "SESSIONS namespace may already exist"
        wrangler kv:namespace create ALERTS || log_warning "ALERTS namespace may already exist"
        
        log_success "Infrastructure setup complete"
    fi
}

# Deploy Worker
deploy_worker() {
    if [ "$SKIP_WORKER" = true ]; then
        log_warning "Skipping Worker deployment"
        return
    fi
    
    progress_step "Deploying Cloudflare Worker"
    
    log_info "Deploying Worker..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing Worker dependencies..."
        npm install
    fi
    
    # Deploy
    log_info "Deploying Worker to Cloudflare..."
    local deploy_output=$(wrangler deploy 2>&1)
    
    if echo "$deploy_output" | grep -q -E "(Published|deployed)"; then
        local worker_url=$(echo "$deploy_output" | grep -oP 'https://[^\s]+' | head -1 || echo "")
        log_success "Worker deployed successfully"
        
        if [ -n "$worker_url" ]; then
            log_info "Worker URL: $worker_url"
            
            # Save to config
            if command -v jq &> /dev/null; then
                if [ -f "$CONFIG_FILE" ]; then
                    local temp=$(mktemp)
                    jq --arg url "$worker_url" --arg name "$WORKER_NAME" '. + {worker_url: $url, worker_name: $name}' "$CONFIG_FILE" > "$temp"
                    mv "$temp" "$CONFIG_FILE"
                else
                    echo "{\"worker_url\": \"$worker_url\", \"worker_name\": \"$WORKER_NAME\"}" > "$CONFIG_FILE"
                fi
            fi
        fi
    else
        log_warning "Worker deployment status unclear"
        echo "$deploy_output"
    fi
}

# Deploy Pages
deploy_pages() {
    if [ "$SKIP_PAGES" = true ]; then
        log_warning "Skipping Pages deployment"
        return
    fi
    
    progress_step "Deploying Frontend to Cloudflare Pages"
    
    log_info "Running Pages deployment script..."
    
    if [ -f "$SCRIPT_DIR/deploy_pages.sh" ]; then
        bash "$SCRIPT_DIR/deploy_pages.sh" --project-name "$PROJECT_NAME" || {
            log_error "Pages deployment failed"
            exit 1
        }
    else
        log_error "deploy_pages.sh not found"
        exit 1
    fi
}

# Setup Worker-Pages binding
setup_bindings() {
    progress_step "Configuring Worker-Pages Bindings"
    
    log_info "Running binding configuration script..."
    
    if [ -f "$SCRIPT_DIR/bind_workers.sh" ]; then
        bash "$SCRIPT_DIR/bind_workers.sh" --project-name "$PROJECT_NAME" --worker-name "$WORKER_NAME" || {
            log_warning "Binding configuration encountered issues (may need manual configuration)"
        }
    else
        log_warning "bind_workers.sh not found, skipping automated binding"
    fi
}

# Configure environment variables
configure_environment() {
    progress_step "Configuring Environment Variables"
    
    log_info "Setting up environment variables..."
    
    local worker_url=""
    if [ -f "$CONFIG_FILE" ] && command -v jq &> /dev/null; then
        worker_url=$(jq -r '.worker_url // ""' "$CONFIG_FILE")
    fi
    
    log_info "Environment variables to configure:"
    echo ""
    echo "  For Pages (via Cloudflare Dashboard):"
    echo "    - NEXT_PUBLIC_API_BASE = ${worker_url:-https://your-worker.workers.dev}"
    echo "    - NEXT_PUBLIC_GTM_ID = GTM-XXXXXXX (optional)"
    echo ""
    echo "  For Worker (via wrangler.toml):"
    echo "    - Already configured in cloudflare/wrangler.toml"
    echo ""
    
    log_info "To set Pages environment variables:"
    log_info "1. Go to https://dash.cloudflare.com/pages"
    log_info "2. Select project '$PROJECT_NAME'"
    log_info "3. Go to Settings > Environment variables"
    log_info "4. Add variables for Production and Preview"
}

# Test deployment
test_deployment() {
    if [ "$SKIP_TEST" = true ]; then
        log_warning "Skipping tests"
        return
    fi
    
    progress_step "Testing Deployment"
    
    log_info "Running deployment tests..."
    
    # Test Worker
    if [ -f "$CONFIG_FILE" ] && command -v jq &> /dev/null; then
        local worker_url=$(jq -r '.worker_url // ""' "$CONFIG_FILE")
        
        if [ -n "$worker_url" ]; then
            log_info "Testing Worker health endpoint..."
            if curl -sf "${worker_url}/api/health" > /dev/null 2>&1; then
                log_success "Worker health check passed"
            else
                log_warning "Worker health check failed (may not be ready yet)"
            fi
        fi
        
        # Test Pages
        local pages_url=$(jq -r '.pages_url // ""' "$CONFIG_FILE")
        
        if [ -n "$pages_url" ]; then
            log_info "Testing Pages deployment..."
            if curl -sf "$pages_url" > /dev/null 2>&1; then
                log_success "Pages deployment accessible"
            else
                log_warning "Pages deployment check failed (may not be ready yet)"
            fi
        fi
    fi
}

# Generate deployment summary
generate_summary() {
    progress_step "Deployment Summary"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "Cloudflare Deployment Complete! 🎉"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        log_info "Configuration saved to: $CONFIG_FILE"
        echo ""
        
        if command -v jq &> /dev/null; then
            local worker_url=$(jq -r '.worker_url // "Not configured"' "$CONFIG_FILE")
            local pages_url=$(jq -r '.pages_url // "Not configured"' "$CONFIG_FILE")
            local d1_id=$(jq -r '.d1_database_id // "Not configured"' "$CONFIG_FILE")
            
            echo "Deployment Details:"
            echo "  📦 Pages URL: $pages_url"
            echo "  ⚡ Worker URL: $worker_url"
            echo "  🗄️  D1 Database ID: $d1_id"
            echo "  📦 R2 Buckets: arbfinder-images, arbfinder-data, arbfinder-backups"
            echo "  💾 KV Namespaces: CACHE, SESSIONS, ALERTS"
            echo ""
        fi
    fi
    
    echo "Next Steps:"
    echo "  1. Configure environment variables in Cloudflare dashboard"
    echo "  2. Set up custom domain (optional)"
    echo "  3. Configure WAF rules for security"
    echo "  4. Set up monitoring and alerts"
    echo "  5. Test all features thoroughly"
    echo ""
    echo "Monitoring Commands:"
    echo "  • Worker logs: wrangler tail --name $WORKER_NAME"
    echo "  • Pages logs: wrangler pages deployment tail --project-name $PROJECT_NAME"
    echo ""
    echo "Documentation:"
    echo "  • Setup Guide: docs/platform/CLOUDFLARE_SETUP.md"
    echo "  • Worker Code: cloudflare/src/index.ts"
    echo "  • Configuration: .cloudflare-config.json"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    show_banner
    
    # Confirm before proceeding
    if [ -t 0 ]; then  # Check if running interactively
        read -p "Press Enter to start deployment (or Ctrl+C to cancel)..."
        echo ""
    fi
    
    # Execute deployment steps
    check_all_prerequisites
    run_infrastructure_setup
    deploy_worker
    deploy_pages
    setup_bindings
    configure_environment
    test_deployment
    generate_summary
    
    echo ""
    log_success "All done! Your ArbFinder Suite is deployed to Cloudflare! 🚀"
    echo ""
}

# Run main function
main "$@"
