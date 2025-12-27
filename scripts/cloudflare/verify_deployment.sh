#!/bin/bash

#############################################################################
# Cloudflare Deployment Verification Script
#
# This script verifies that all Cloudflare services are properly deployed
# and functioning correctly
#
# Usage:
#   ./scripts/cloudflare/verify_deployment.sh [--config FILE]
#
# Requirements:
#   - curl installed
#   - jq installed (optional, for JSON parsing)
#   - Deployed Cloudflare services
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

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

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

# Test tracking
test_start() {
    ((TOTAL_TESTS++))
    echo -e "${BLUE}▶${NC} Testing: $1"
}

test_pass() {
    ((PASSED_TESTS++))
    log_success "$1"
}

test_fail() {
    ((FAILED_TESTS++))
    log_error "$1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load configuration
load_config() {
    log_info "Loading configuration from $CONFIG_FILE"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warning "Configuration file not found. Some tests may be skipped."
        return
    fi
    
    if command -v jq &> /dev/null; then
        WORKER_URL=$(jq -r '.worker_url // ""' "$CONFIG_FILE")
        PAGES_URL=$(jq -r '.pages_url // ""' "$CONFIG_FILE")
        D1_DATABASE_ID=$(jq -r '.d1_database_id // ""' "$CONFIG_FILE")
        WORKER_NAME=$(jq -r '.worker_name // "arbfinder-worker"' "$CONFIG_FILE")
        PAGES_PROJECT=$(jq -r '.pages_project // "arbfinder-suite"' "$CONFIG_FILE")
    else
        log_warning "jq not installed. Using default values."
        WORKER_URL=""
        PAGES_URL=""
        D1_DATABASE_ID=""
        WORKER_NAME="arbfinder-worker"
        PAGES_PROJECT="arbfinder-suite"
    fi
    
    log_success "Configuration loaded"
}

# Test Worker health endpoint
test_worker_health() {
    test_start "Worker health endpoint"
    
    if [ -z "$WORKER_URL" ]; then
        test_fail "Worker URL not configured"
        return
    fi
    
    local response=$(curl -s -w "\n%{http_code}" "${WORKER_URL}/api/health" 2>/dev/null || echo "000")
    local body=$(echo "$response" | head -n -1)
    local status=$(echo "$response" | tail -n 1)
    
    if [ "$status" = "200" ]; then
        test_pass "Worker is healthy (HTTP $status)"
        log_info "Response: $body"
    else
        test_fail "Worker health check failed (HTTP $status)"
    fi
}

# Test Worker CORS
test_worker_cors() {
    test_start "Worker CORS configuration"
    
    if [ -z "$WORKER_URL" ]; then
        test_fail "Worker URL not configured"
        return
    fi
    
    local headers=$(curl -s -I -X OPTIONS "${WORKER_URL}/api/health" 2>/dev/null || echo "")
    
    if echo "$headers" | grep -qi "Access-Control-Allow-Origin"; then
        test_pass "CORS headers present"
    else
        test_fail "CORS headers missing"
    fi
}

# Test Pages deployment
test_pages_deployment() {
    test_start "Pages deployment accessibility"
    
    if [ -z "$PAGES_URL" ]; then
        test_fail "Pages URL not configured"
        return
    fi
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$PAGES_URL" 2>/dev/null || echo "000")
    
    if [ "$status" = "200" ]; then
        test_pass "Pages site is accessible (HTTP $status)"
    else
        test_fail "Pages site not accessible (HTTP $status)"
    fi
}

# Test Pages meta tags
test_pages_meta() {
    test_start "Pages HTML structure"
    
    if [ -z "$PAGES_URL" ]; then
        test_fail "Pages URL not configured"
        return
    fi
    
    local html=$(curl -s "$PAGES_URL" 2>/dev/null || echo "")
    
    if echo "$html" | grep -qi "<html"; then
        test_pass "Valid HTML structure"
    else
        test_fail "Invalid HTML structure"
    fi
    
    if echo "$html" | grep -qi "<title>"; then
        test_pass "HTML has title tag"
    else
        test_warning "HTML missing title tag"
    fi
}

# Test D1 database
test_d1_database() {
    test_start "D1 database"
    
    if [ -z "$D1_DATABASE_ID" ]; then
        test_fail "D1 Database ID not configured"
        return
    fi
    
    # Check if database exists using wrangler
    if command -v wrangler &> /dev/null; then
        if wrangler d1 list 2>/dev/null | grep -q "$D1_DATABASE_ID"; then
            test_pass "D1 database exists"
        else
            test_fail "D1 database not found"
        fi
    else
        test_warning "wrangler not installed, skipping D1 test"
    fi
}

# Test R2 buckets
test_r2_buckets() {
    test_start "R2 storage buckets"
    
    if ! command -v wrangler &> /dev/null; then
        test_warning "wrangler not installed, skipping R2 test"
        return
    fi
    
    local buckets=("arbfinder-images" "arbfinder-data" "arbfinder-backups")
    local found_buckets=0
    
    for bucket in "${buckets[@]}"; do
        if wrangler r2 bucket list 2>/dev/null | grep -q "$bucket"; then
            ((found_buckets++))
        fi
    done
    
    if [ $found_buckets -eq ${#buckets[@]} ]; then
        test_pass "All R2 buckets exist ($found_buckets/${#buckets[@]})"
    elif [ $found_buckets -gt 0 ]; then
        test_warning "Some R2 buckets missing ($found_buckets/${#buckets[@]})"
    else
        test_fail "No R2 buckets found"
    fi
}

# Test KV namespaces
test_kv_namespaces() {
    test_start "KV namespaces"
    
    if ! command -v wrangler &> /dev/null; then
        test_warning "wrangler not installed, skipping KV test"
        return
    fi
    
    local namespaces=("CACHE" "SESSIONS" "ALERTS")
    local found_namespaces=0
    
    for ns in "${namespaces[@]}"; do
        if wrangler kv:namespace list 2>/dev/null | grep -qi "$ns"; then
            ((found_namespaces++))
        fi
    done
    
    if [ $found_namespaces -eq ${#namespaces[@]} ]; then
        test_pass "All KV namespaces exist ($found_namespaces/${#namespaces[@]})"
    elif [ $found_namespaces -gt 0 ]; then
        test_warning "Some KV namespaces missing ($found_namespaces/${#namespaces[@]})"
    else
        test_fail "No KV namespaces found"
    fi
}

# Test Worker deployment status
test_worker_deployment() {
    test_start "Worker deployment status"
    
    if ! command -v wrangler &> /dev/null; then
        test_warning "wrangler not installed, skipping worker deployment test"
        return
    fi
    
    cd "$PROJECT_ROOT/cloudflare"
    
    if wrangler deployments list 2>/dev/null | grep -q "$WORKER_NAME"; then
        test_pass "Worker is deployed"
    else
        test_fail "Worker not deployed"
    fi
}

# Test Pages project status
test_pages_project() {
    test_start "Pages project status"
    
    if ! command -v wrangler &> /dev/null; then
        test_warning "wrangler not installed, skipping pages project test"
        return
    fi
    
    if wrangler pages project list 2>/dev/null | grep -q "$PAGES_PROJECT"; then
        test_pass "Pages project exists"
    else
        test_fail "Pages project not found"
    fi
}

# Test response time
test_response_time() {
    test_start "Response time performance"
    
    if [ -z "$WORKER_URL" ]; then
        test_warning "Worker URL not configured, skipping response time test"
        return
    fi
    
    local response_time=$(curl -s -w "%{time_total}" -o /dev/null "${WORKER_URL}/api/health" 2>/dev/null || echo "0")
    
    # Convert to milliseconds
    local ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "0")
    
    if (( $(echo "$ms < 1000" | bc -l 2>/dev/null || echo 0) )); then
        test_pass "Response time: ${ms}ms (< 1000ms)"
    else
        test_warning "Response time: ${ms}ms (> 1000ms)"
    fi
}

# Generate report
generate_report() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  📊 Verification Report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo "Test Results:"
    echo "  Total Tests: $TOTAL_TESTS"
    echo "  ✓ Passed: $PASSED_TESTS"
    echo "  ✗ Failed: $FAILED_TESTS"
    echo "  ⚠ Warnings: $((TOTAL_TESTS - PASSED_TESTS - FAILED_TESTS))"
    echo ""
    
    local success_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    fi
    
    echo "Success Rate: $success_rate%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All critical tests passed! ✨"
    else
        log_warning "Some tests failed. Please review the results above."
    fi
    
    echo ""
    echo "Deployment URLs:"
    if [ -n "$PAGES_URL" ]; then
        echo "  🌐 Frontend: $PAGES_URL"
    fi
    if [ -n "$WORKER_URL" ]; then
        echo "  ⚡ API: $WORKER_URL"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🔍 ArbFinder Suite - Deployment Verification"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    load_config
    
    echo ""
    log_info "Running verification tests..."
    echo ""
    
    # Run all tests
    test_worker_health
    echo ""
    test_worker_cors
    echo ""
    test_pages_deployment
    echo ""
    test_pages_meta
    echo ""
    test_d1_database
    echo ""
    test_r2_buckets
    echo ""
    test_kv_namespaces
    echo ""
    test_worker_deployment
    echo ""
    test_pages_project
    echo ""
    test_response_time
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"
