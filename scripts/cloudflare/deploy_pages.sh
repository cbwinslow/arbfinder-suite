#!/bin/bash

#############################################################################
# Cloudflare Pages Deployment Script for ArbFinder Suite
#
# This script automates deployment of the Next.js frontend to Cloudflare Pages
#
# Usage:
#   ./scripts/cloudflare/deploy_pages.sh [--project-name NAME] [--branch BRANCH]
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
FRONTEND_DIR="$PROJECT_ROOT/frontend"
CONFIG_FILE="$PROJECT_ROOT/.cloudflare-config.json"

# Default values
PROJECT_NAME="arbfinder-suite"
BRANCH="main"
PRODUCTION_BRANCH="main"

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
        --branch)
            BRANCH="$2"
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
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found. Please install Node.js v18 or higher."
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
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    log_success "Frontend directory found"
}

# Update Next.js config for static export
update_nextjs_config() {
    log_info "Configuring Next.js for static export..."
    
    cd "$FRONTEND_DIR"
    
    # Backup original config
    if [ -f "next.config.js" ]; then
        cp next.config.js next.config.js.bak
        log_success "Backed up next.config.js"
    fi
    
    # Update config for static export
    cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

module.exports = nextConfig;
EOF
    
    log_success "Next.js configured for static export"
}

# Install frontend dependencies
install_dependencies() {
    log_info "Installing frontend dependencies..."
    
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        npm install
        log_success "Dependencies installed"
    else
        log_success "Dependencies already installed"
    fi
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Clean previous builds
    rm -rf out .next
    
    # Build
    npm run build
    
    if [ -d "out" ]; then
        log_success "Frontend built successfully"
    else
        log_error "Build failed - 'out' directory not created"
        exit 1
    fi
}

# Create Pages project if it doesn't exist
create_pages_project() {
    log_info "Checking Pages project..."
    
    # Check if project exists
    local project_exists=$(wrangler pages project list 2>/dev/null | grep -c "$PROJECT_NAME" || true)
    
    if [ "$project_exists" -eq 0 ]; then
        log_info "Creating Pages project '$PROJECT_NAME'..."
        wrangler pages project create "$PROJECT_NAME" --production-branch="$PRODUCTION_BRANCH"
        log_success "Pages project created"
    else
        log_success "Pages project '$PROJECT_NAME' already exists"
    fi
}

# Deploy to Pages
deploy_to_pages() {
    log_info "Deploying to Cloudflare Pages..."
    
    cd "$FRONTEND_DIR"
    
    # Deploy
    local deploy_output=$(wrangler pages deploy out --project-name="$PROJECT_NAME" --branch="$BRANCH" 2>&1)
    
    if echo "$deploy_output" | grep -q -E "(Published|Deployment complete)"; then
        # Extract Pages URL with more specific pattern
        local pages_url=$(echo "$deploy_output" | grep -oP 'https://[a-zA-Z0-9.-]+\.pages\.dev[/\S]*' | head -1 || echo "")
        log_success "Deployed to Cloudflare Pages"
        
        if [ -n "$pages_url" ]; then
            log_info "Pages URL: $pages_url"
            
            # Save to config
            if [ -f "$CONFIG_FILE" ]; then
                local temp=$(mktemp)
                jq --arg url "$pages_url" --arg name "$PROJECT_NAME" '. + {pages_url: $url, pages_project: $name}' "$CONFIG_FILE" > "$temp"
                mv "$temp" "$CONFIG_FILE"
            else
                echo "{\"pages_url\": \"$pages_url\", \"pages_project\": \"$PROJECT_NAME\"}" > "$CONFIG_FILE"
            fi
        fi
    else
        log_error "Deployment failed"
        echo "$deploy_output"
        exit 1
    fi
}

# Configure environment variables for Pages
configure_pages_env() {
    log_info "Configuring Pages environment variables..."
    
    log_info "Setting environment variables for Pages project..."
    log_warning "Note: Environment variables should be set via Cloudflare dashboard for security"
    log_info "Required environment variables:"
    log_info "  - NEXT_PUBLIC_API_BASE (e.g., https://arbfinder-worker.yourdomain.workers.dev)"
    log_info "  - NEXT_PUBLIC_GTM_ID (optional, for Google Tag Manager)"
    
    echo ""
    log_info "To set environment variables:"
    log_info "1. Go to https://dash.cloudflare.com/pages"
    log_info "2. Select your project '$PROJECT_NAME'"
    log_info "3. Go to Settings > Environment variables"
    log_info "4. Add the variables for Production and Preview environments"
}

# Restore original config
restore_config() {
    if [ -f "$FRONTEND_DIR/next.config.js.bak" ]; then
        log_info "Restoring original Next.js config..."
        mv "$FRONTEND_DIR/next.config.js.bak" "$FRONTEND_DIR/next.config.js"
        log_success "Original config restored"
    fi
}

# Main execution
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📦 ArbFinder Suite - Cloudflare Pages Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Trap to restore config on exit
    trap restore_config EXIT
    
    check_prerequisites
    update_nextjs_config
    install_dependencies
    build_frontend
    create_pages_project
    deploy_to_pages
    configure_pages_env
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "Cloudflare Pages Deployment Complete! 🎉"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        local pages_url=$(jq -r '.pages_url // "Not configured"' "$CONFIG_FILE")
        echo "Deployment URL: $pages_url"
    fi
    
    echo ""
    echo "Next Steps:"
    echo "  1. Set environment variables in Cloudflare dashboard"
    echo "  2. Configure custom domain (optional)"
    echo "  3. Deploy Workers and bind to Pages"
    echo "  4. Test the deployment"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Run main function
main "$@"
