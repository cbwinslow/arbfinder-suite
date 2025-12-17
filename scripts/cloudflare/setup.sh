#!/bin/bash
set -e

# Cloudflare Platform Setup Script for ArbFinder Suite
# This script sets up all Cloudflare resources needed for the project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONFIG_FILE="${PROJECT_ROOT}/.env"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command_exists curl; then
        print_error "curl is required but not installed."
        exit 1
    fi
    
    if ! command_exists jq; then
        print_error "jq is required but not installed. Please install it: https://stedolan.github.io/jq/"
        exit 1
    fi
    
    if ! command_exists wrangler; then
        print_warning "Wrangler CLI not found. Installing..."
        npm install -g wrangler
    fi
    
    print_info "Prerequisites check complete."
}

# Load environment variables
load_env() {
    if [ -f "$CONFIG_FILE" ]; then
        print_info "Loading environment variables from $CONFIG_FILE"
        source "$CONFIG_FILE"
    else
        print_warning "No .env file found at $CONFIG_FILE"
        print_info "Creating .env file from template..."
        if [ -f "${PROJECT_ROOT}/.env.example" ]; then
            cp "${PROJECT_ROOT}/.env.example" "$CONFIG_FILE"
            print_info "Please edit $CONFIG_FILE and add your Cloudflare API credentials"
            exit 0
        fi
    fi
}

# Validate required environment variables
validate_env() {
    print_info "Validating environment variables..."
    
    if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
        print_error "CLOUDFLARE_API_TOKEN is not set"
        print_info "Get your API token from: https://dash.cloudflare.com/profile/api-tokens"
        print_info "Required permissions: Account.Workers Scripts, Account.D1, Account.R2, Zone.Workers Routes"
        exit 1
    fi
    
    if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
        print_error "CLOUDFLARE_ACCOUNT_ID is not set"
        print_info "Find your Account ID at: https://dash.cloudflare.com"
        exit 1
    fi
    
    print_info "Environment variables validated."
}

# Authenticate with Cloudflare
authenticate() {
    print_info "Authenticating with Cloudflare..."
    
    # Test API token
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        "https://api.cloudflare.com/client/v4/user/tokens/verify")
    
    if [ "$response" = "200" ]; then
        print_info "Authentication successful!"
    else
        print_error "Authentication failed. Please check your API token."
        exit 1
    fi
}

# Setup D1 Database
setup_d1() {
    print_info "Setting up D1 Database..."
    
    # Check if database exists
    DB_NAME="arbfinder-db"
    
    print_info "Creating D1 database: $DB_NAME"
    wrangler d1 create "$DB_NAME" --json > /tmp/d1_output.json || true
    
    DB_ID=$(jq -r '.id' /tmp/d1_output.json)
    
    if [ "$DB_ID" != "null" ] && [ -n "$DB_ID" ]; then
        print_info "D1 Database created: $DB_ID"
        echo "CLOUDFLARE_D1_DATABASE_ID=$DB_ID" >> "$CONFIG_FILE"
        export CLOUDFLARE_D1_DATABASE_ID="$DB_ID"
        
        # Run migrations
        print_info "Running database migrations..."
        if [ -f "${PROJECT_ROOT}/database/migrations/d1_schema.sql" ]; then
            wrangler d1 execute "$DB_NAME" --file="${PROJECT_ROOT}/database/migrations/d1_schema.sql"
            print_info "Migrations complete."
        else
            print_warning "No migration file found at database/migrations/d1_schema.sql"
        fi
    else
        print_warning "D1 database may already exist or creation failed"
    fi
}

# Setup R2 Buckets
setup_r2() {
    print_info "Setting up R2 Buckets..."
    
    # Create images bucket
    print_info "Creating R2 bucket: arbfinder-images"
    wrangler r2 bucket create arbfinder-images || print_warning "Bucket may already exist"
    
    # Create data bucket
    print_info "Creating R2 bucket: arbfinder-data"
    wrangler r2 bucket create arbfinder-data || print_warning "Bucket may already exist"
    
    # Create preview buckets
    print_info "Creating preview buckets..."
    wrangler r2 bucket create arbfinder-images-preview || print_warning "Bucket may already exist"
    wrangler r2 bucket create arbfinder-data-preview || print_warning "Bucket may already exist"
    
    print_info "R2 buckets created."
}

# Setup KV Namespaces
setup_kv() {
    print_info "Setting up KV Namespaces..."
    
    # Create cache namespace
    print_info "Creating KV namespace: CACHE"
    KV_OUTPUT=$(wrangler kv:namespace create "CACHE" --json 2>/dev/null || echo '{"id":""}')
    KV_ID=$(echo "$KV_OUTPUT" | jq -r '.id')
    
    if [ -n "$KV_ID" ] && [ "$KV_ID" != "null" ]; then
        print_info "KV Namespace created: $KV_ID"
        echo "CLOUDFLARE_KV_CACHE_ID=$KV_ID" >> "$CONFIG_FILE"
        export CLOUDFLARE_KV_CACHE_ID="$KV_ID"
    fi
    
    # Create preview namespace
    print_info "Creating KV preview namespace"
    KV_PREVIEW_OUTPUT=$(wrangler kv:namespace create "CACHE" --preview --json 2>/dev/null || echo '{"id":""}')
    KV_PREVIEW_ID=$(echo "$KV_PREVIEW_OUTPUT" | jq -r '.id')
    
    if [ -n "$KV_PREVIEW_ID" ] && [ "$KV_PREVIEW_ID" != "null" ]; then
        print_info "KV Preview Namespace created: $KV_PREVIEW_ID"
        echo "CLOUDFLARE_KV_CACHE_PREVIEW_ID=$KV_PREVIEW_ID" >> "$CONFIG_FILE"
        export CLOUDFLARE_KV_CACHE_PREVIEW_ID="$KV_PREVIEW_ID"
    fi
    
    print_info "KV namespaces created."
}

# Deploy Workers
deploy_workers() {
    print_info "Deploying Cloudflare Workers..."
    
    cd "${PROJECT_ROOT}/cloudflare"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    # Build
    print_info "Building Worker..."
    npm run build || true
    
    # Deploy
    print_info "Deploying to Cloudflare..."
    wrangler deploy
    
    print_info "Workers deployed successfully."
    cd "$PROJECT_ROOT"
}

# Setup Pages
setup_pages() {
    print_info "Setting up Cloudflare Pages..."
    
    print_info "To deploy to Cloudflare Pages:"
    print_info "1. Go to https://dash.cloudflare.com"
    print_info "2. Navigate to Pages"
    print_info "3. Connect your GitHub repository"
    print_info "4. Set build command: cd frontend && npm install && npm run build"
    print_info "5. Set build output directory: frontend/.next"
    print_info "6. Add environment variables from .env"
    
    print_warning "Pages setup requires manual configuration via Cloudflare Dashboard"
}

# Setup WAF Rules
setup_waf() {
    print_info "Setting up WAF Rules..."
    
    if [ -z "$CLOUDFLARE_ZONE_ID" ]; then
        print_warning "CLOUDFLARE_ZONE_ID not set. Skipping WAF setup."
        print_info "Set CLOUDFLARE_ZONE_ID in .env to configure WAF rules"
        return
    fi
    
    # Rate limiting rule
    print_info "Creating rate limiting rule..."
    
    RATE_LIMIT_RULE=$(cat <<EOF
{
  "action": "block",
  "expression": "(http.request.uri.path contains \"/api/\" and rate(10s) > 100)",
  "description": "Rate limit API endpoints to 100 requests per 10 seconds"
}
EOF
)
    
    curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/firewall/rules" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$RATE_LIMIT_RULE" | jq .
    
    print_info "WAF rules configured."
}

# Setup Analytics and Logging
setup_observability() {
    print_info "Setting up observability..."
    
    print_info "Cloudflare Analytics is automatically enabled for Workers and Pages"
    print_info "View analytics at: https://dash.cloudflare.com"
    
    # Enable Logpush (requires Enterprise)
    print_warning "Logpush requires Cloudflare Enterprise plan"
    print_info "For detailed logging, consider using Workers Logpush or external logging service"
}

# Generate wrangler.toml with new IDs
update_wrangler_config() {
    print_info "Updating wrangler.toml with new resource IDs..."
    
    if [ -f "${PROJECT_ROOT}/cloudflare/wrangler.toml" ]; then
        # Update KV namespace IDs if they exist
        if [ -n "$CLOUDFLARE_KV_CACHE_ID" ]; then
            sed -i.bak "s/id = \"your-kv-namespace-id\"/id = \"$CLOUDFLARE_KV_CACHE_ID\"/" \
                "${PROJECT_ROOT}/cloudflare/wrangler.toml"
        fi
        
        if [ -n "$CLOUDFLARE_KV_CACHE_PREVIEW_ID" ]; then
            sed -i.bak "s/preview_id = \"your-preview-kv-namespace-id\"/preview_id = \"$CLOUDFLARE_KV_CACHE_PREVIEW_ID\"/" \
                "${PROJECT_ROOT}/cloudflare/wrangler.toml"
        fi
        
        print_info "wrangler.toml updated."
    fi
}

# Main setup function
main() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║   ArbFinder Suite - Cloudflare Platform Setup           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    check_prerequisites
    load_env
    validate_env
    authenticate
    
    echo ""
    print_info "Starting Cloudflare resource setup..."
    echo ""
    
    # Run setup steps
    setup_d1
    setup_r2
    setup_kv
    update_wrangler_config
    setup_waf
    setup_observability
    deploy_workers
    setup_pages
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║   Setup Complete!                                        ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    print_info "Your Cloudflare resources have been set up successfully."
    print_info "Configuration saved to: $CONFIG_FILE"
    echo ""
    print_info "Next steps:"
    print_info "1. Review and test your Workers at: https://dash.cloudflare.com"
    print_info "2. Configure Cloudflare Pages for your frontend"
    print_info "3. Test the deployment with: cd cloudflare && wrangler tail"
    echo ""
}

# Run main function
main "$@"
