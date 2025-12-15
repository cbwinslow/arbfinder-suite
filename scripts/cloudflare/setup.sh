#!/bin/bash

#############################################################################
# Cloudflare Platform Setup Script for ArbFinder Suite
#
# This script automates the complete setup of Cloudflare services:
# - Workers deployment
# - D1 database creation and schema application
# - R2 storage buckets
# - KV namespaces
# - Pages deployment
# - WAF configuration
# - Observability setup
#
# Usage:
#   ./scripts/cloudflare/setup.sh [--auto]
#
# Requirements:
#   - wrangler CLI installed (npm install -g wrangler)
#   - Cloudflare account with API token
#   - Node.js v18+ installed
#
# Environment Variables:
#   CLOUDFLARE_API_TOKEN - API token with appropriate permissions
#   CLOUDFLARE_ACCOUNT_ID - Your Cloudflare account ID
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

# Progress bar
progress_bar() {
    local current=$1
    local total=$2
    local step_name=$3
    
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r[${GREEN}"
    printf "%${filled}s" | tr ' ' '='
    printf "${NC}"
    printf "%${empty}s" | tr ' ' '-'
    printf "] ${percent}%% - ${step_name}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
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
}

# Get Cloudflare credentials
get_credentials() {
    log_info "Setting up Cloudflare credentials..."
    
    if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
        echo ""
        log_warning "CLOUDFLARE_API_TOKEN not set in environment"
        echo ""
        echo "To create an API token:"
        echo "1. Go to https://dash.cloudflare.com/profile/api-tokens"
        echo "2. Click 'Create Token'"
        echo "3. Use 'Edit Cloudflare Workers' template"
        echo "4. Add permissions for D1, R2, Pages, WAF"
        echo "5. Copy the token"
        echo ""
        read -rp "Enter your Cloudflare API token: " CLOUDFLARE_API_TOKEN
        export CLOUDFLARE_API_TOKEN
    fi
    
    if [ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]; then
        echo ""
        read -rp "Enter your Cloudflare Account ID: " CLOUDFLARE_ACCOUNT_ID
        export CLOUDFLARE_ACCOUNT_ID
    fi
    
    # Save to wrangler config
    wrangler config set api_token="$CLOUDFLARE_API_TOKEN" 2>/dev/null || true
    
    log_success "Credentials configured"
}

# Validate credentials
validate_credentials() {
    log_info "Validating Cloudflare credentials..."
    
    if ! wrangler whoami &> /dev/null; then
        log_error "Failed to authenticate with Cloudflare. Please check your API token."
        exit 1
    fi
    
    log_success "Credentials valid"
}

# Create D1 database
setup_d1() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Setting up D1 database..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # Check if database already exists
    local db_exists=$(wrangler d1 list 2>/dev/null | grep -c "arbfinder" || true)
    
    if [ "$db_exists" -eq 0 ]; then
        log_info "\nCreating D1 database 'arbfinder'..."
        local db_output=$(wrangler d1 create arbfinder 2>&1)
        local db_id=$(echo "$db_output" | grep -oP 'database_id\s*=\s*"\K[^"]+' || echo "")
        
        if [ -z "$db_id" ]; then
            log_error "\nFailed to create D1 database"
            echo "$db_output"
            exit 1
        fi
        
        log_success "\nD1 database created: $db_id"
        
        # Update wrangler.toml
        if [ -f "wrangler.toml" ]; then
            sed -i.bak "s/database_id = \".*\"/database_id = \"$db_id\"/" wrangler.toml
            rm -f wrangler.toml.bak
        fi
        
        # Save to config
        echo "{\"d1_database_id\": \"$db_id\"}" > "$CONFIG_FILE"
    else
        log_success "\nD1 database already exists"
        local db_id=$(wrangler d1 list 2>/dev/null | grep "arbfinder" | awk '{print $2}')
    fi
    
    # Apply schema
    if [ -f "$PROJECT_ROOT/database/cloudflare_schema.sql" ]; then
        log_info "Applying database schema..."
        wrangler d1 execute arbfinder --file="$PROJECT_ROOT/database/cloudflare_schema.sql" 2>/dev/null || true
        log_success "Schema applied"
    else
        log_warning "Schema file not found, skipping schema application"
    fi
}

# Create R2 buckets
setup_r2() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Setting up R2 storage..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # Create images bucket
    if ! wrangler r2 bucket list 2>/dev/null | grep -q "arbfinder-images"; then
        log_info "\nCreating R2 bucket 'arbfinder-images'..."
        wrangler r2 bucket create arbfinder-images
        log_success "Images bucket created"
    else
        log_success "\nImages bucket already exists"
    fi
    
    # Create data bucket
    if ! wrangler r2 bucket list 2>/dev/null | grep -q "arbfinder-data"; then
        log_info "Creating R2 bucket 'arbfinder-data'..."
        wrangler r2 bucket create arbfinder-data
        log_success "Data bucket created"
    else
        log_success "Data bucket already exists"
    fi
}

# Create KV namespace
setup_kv() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Setting up KV namespace..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # Check if KV namespace exists
    local kv_exists=$(wrangler kv:namespace list 2>/dev/null | grep -c "arbfinder-cache" || true)
    
    if [ "$kv_exists" -eq 0 ]; then
        log_info "\nCreating KV namespace 'arbfinder-cache'..."
        local kv_output=$(wrangler kv:namespace create "CACHE" 2>&1)
        local kv_id=$(echo "$kv_output" | grep -oP 'id\s*=\s*"\K[^"]+' || echo "")
        
        if [ -z "$kv_id" ]; then
            log_warning "\nFailed to create KV namespace (may already exist)"
        else
            log_success "\nKV namespace created: $kv_id"
            
            # Update wrangler.toml
            if [ -f "wrangler.toml" ]; then
                sed -i.bak "s/id = \"TO_BE_CONFIGURED\"/id = \"$kv_id\"/" wrangler.toml
                rm -f wrangler.toml.bak
            fi
        fi
    else
        log_success "\nKV namespace already exists"
    fi
}

# Deploy Worker
deploy_worker() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Deploying Worker..."
    
    cd "$PROJECT_ROOT/cloudflare"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "\nInstalling Worker dependencies..."
        npm install --silent
    fi
    
    # Deploy
    log_info "\nDeploying Worker..."
    local deploy_output=$(wrangler deploy 2>&1)
    
    if echo "$deploy_output" | grep -q "Published"; then
        local worker_url=$(echo "$deploy_output" | grep -oP 'https://[^\s]+' || echo "")
        log_success "\nWorker deployed"
        if [ -n "$worker_url" ]; then
            log_info "Worker URL: $worker_url"
            
            # Save to config
            if [ -f "$CONFIG_FILE" ]; then
                local temp=$(mktemp)
                jq --arg url "$worker_url" '. + {worker_url: $url}' "$CONFIG_FILE" > "$temp"
                mv "$temp" "$CONFIG_FILE"
            fi
        fi
    else
        log_warning "\nWorker deployment status unclear"
        echo "$deploy_output"
    fi
}

# Deploy Pages
deploy_pages() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Deploying Pages..."
    
    log_info "\nPages deployment..."
    log_warning "Pages deployment requires GitHub integration"
    log_info "Please complete Pages setup manually:"
    log_info "1. Go to https://dash.cloudflare.com/pages"
    log_info "2. Click 'Create application' → 'Connect to Git'"
    log_info "3. Select 'cbwinslow/arbfinder-suite' repository"
    log_info "4. Configure build settings:"
    log_info "   - Framework: Next.js"
    log_info "   - Build command: npm run build"
    log_info "   - Build output: out"
    log_info "   - Root directory: frontend"
    log_info "5. Add environment variables:"
    log_info "   - NEXT_PUBLIC_API_BASE"
    log_info "6. Deploy"
}

# Configure WAF
configure_waf() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Configuring WAF..."
    
    log_info "\nWAF configuration..."
    log_warning "WAF must be configured via Cloudflare dashboard"
    log_info "To configure WAF:"
    log_info "1. Go to https://dash.cloudflare.com/security"
    log_info "2. Configure Security Level (Medium recommended)"
    log_info "3. Add Rate Limiting rules:"
    log_info "   - Limit API requests to 100/minute per IP"
    log_info "4. Enable Bot Fight Mode"
    log_info "5. Configure DDoS protection"
    
    # Run helper script if it exists
    if [ -f "$SCRIPT_DIR/configure_waf.sh" ]; then
        bash "$SCRIPT_DIR/configure_waf.sh" || true
    fi
}

# Setup observability
setup_observability() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Setting up observability..."
    
    log_info "\nObservability setup..."
    log_info "To enable full observability:"
    log_info "1. Enable Logpush (requires paid plan)"
    log_info "2. Configure Analytics → Web Analytics"
    log_info "3. Set up alerts for errors and performance"
    log_info "4. Use 'wrangler tail' to view real-time logs"
    
    # Run helper script if it exists
    if [ -f "$SCRIPT_DIR/setup_observability.sh" ]; then
        bash "$SCRIPT_DIR/setup_observability.sh" || true
    fi
}

# Run verification tests
run_verification() {
    local step=$1
    local total=$2
    
    progress_bar "$step" "$total" "Running verification tests..."
    
    log_info "\nRunning verification tests..."
    
    # Test worker health endpoint
    if [ -f "$CONFIG_FILE" ]; then
        local worker_url=$(jq -r '.worker_url // empty' "$CONFIG_FILE")
        if [ -n "$worker_url" ]; then
            log_info "Testing Worker health endpoint..."
            if curl -sf "${worker_url}/api/health" > /dev/null 2>&1; then
                log_success "Worker health check passed"
            else
                log_warning "Worker health check failed (may not be ready yet)"
            fi
        fi
    fi
    
    # Run full verification script if it exists
    if [ -f "$SCRIPT_DIR/verify_deployment.sh" ]; then
        bash "$SCRIPT_DIR/verify_deployment.sh" || log_warning "Verification script encountered issues"
    fi
}

# Generate summary
generate_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "Cloudflare Setup Complete! 🎉"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        log_info "Configuration saved to: $CONFIG_FILE"
        echo ""
        
        local worker_url=$(jq -r '.worker_url // "Not configured"' "$CONFIG_FILE")
        local d1_id=$(jq -r '.d1_database_id // "Not configured"' "$CONFIG_FILE")
        
        echo "Deployment Details:"
        echo "  Worker URL: $worker_url"
        echo "  D1 Database ID: $d1_id"
        echo "  R2 Buckets: arbfinder-images, arbfinder-data"
        echo "  KV Namespace: arbfinder-cache"
        echo ""
    fi
    
    echo "Next Steps:"
    echo "  1. Configure custom domain (if desired)"
    echo "  2. Complete Pages deployment via GitHub integration"
    echo "  3. Set up WAF rules in Cloudflare dashboard"
    echo "  4. Configure environment variables for production"
    echo "  5. Set up monitoring and alerts"
    echo "  6. Run: wrangler tail (to view live logs)"
    echo ""
    echo "Documentation:"
    echo "  Setup Guide: docs/CLOUDFLARE_SETUP.md"
    echo "  Worker Code: cloudflare/src/index.ts"
    echo "  Configuration: cloudflare/wrangler.toml"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    clear
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🚀 ArbFinder Suite - Cloudflare Platform Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    local total_steps=10
    local current_step=0
    
    # Step 1: Prerequisites
    ((current_step++))
    progress_bar "$current_step" "$total_steps" "Checking prerequisites..."
    check_prerequisites
    echo ""
    
    # Step 2: Credentials
    ((current_step++))
    progress_bar "$current_step" "$total_steps" "Setting up credentials..."
    get_credentials
    echo ""
    
    # Step 3: Validation
    ((current_step++))
    progress_bar "$current_step" "$total_steps" "Validating credentials..."
    validate_credentials
    echo ""
    
    # Step 4: D1 Database
    ((current_step++))
    setup_d1 "$current_step" "$total_steps"
    echo ""
    
    # Step 5: R2 Storage
    ((current_step++))
    setup_r2 "$current_step" "$total_steps"
    echo ""
    
    # Step 6: KV Namespace
    ((current_step++))
    setup_kv "$current_step" "$total_steps"
    echo ""
    
    # Step 7: Deploy Worker
    ((current_step++))
    deploy_worker "$current_step" "$total_steps"
    echo ""
    
    # Step 8: Deploy Pages
    ((current_step++))
    deploy_pages "$current_step" "$total_steps"
    echo ""
    
    # Step 9: Configure WAF
    ((current_step++))
    configure_waf "$current_step" "$total_steps"
    echo ""
    
    # Step 10: Observability
    ((current_step++))
    setup_observability "$current_step" "$total_steps"
    echo ""
    
    # Verification
    run_verification "$current_step" "$total_steps"
    echo ""
    
    # Summary
    generate_summary
}

# Run main function
main "$@"
