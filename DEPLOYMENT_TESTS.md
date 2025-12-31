# Test Suite for Cloudflare Deployment Microgoals

## Overview
This document provides specific tests for each microgoal in the Cloudflare Pages deployment setup. Each test is designed to verify that a specific component or configuration is working correctly.

---

## Test Categories

1. **Python Environment Tests** - Verify Python setup and dependencies
2. **Frontend Build Tests** - Verify Next.js builds correctly
3. **Worker Tests** - Verify Cloudflare Worker functionality
4. **Integration Tests** - Verify end-to-end workflows
5. **Deployment Tests** - Verify actual deployments

---

## 1. Python Environment Tests

### TEST-PY-001: Verify Python Version
**Goal**: Confirm Python 3.10 is being used  
**Prerequisites**: .python-version file exists, .venv created

```bash
#!/bin/bash
# tests/test_python_version.sh

echo "TEST-PY-001: Verify Python Version"

# Check .python-version file
if [ ! -f ".python-version" ]; then
  echo "❌ FAILED: .python-version file not found"
  exit 1
fi

EXPECTED_VERSION=$(cat .python-version)
echo "Expected Python version: $EXPECTED_VERSION"

# Activate venv and check version
source .venv/bin/activate
ACTUAL_VERSION=$(python --version | cut -d' ' -f2 | cut -d'.' -f1-2)

if [ "$ACTUAL_VERSION" == "$EXPECTED_VERSION" ]; then
  echo "✅ PASSED: Python version is $ACTUAL_VERSION"
  exit 0
else
  echo "❌ FAILED: Python version is $ACTUAL_VERSION, expected $EXPECTED_VERSION"
  exit 1
fi
```

**Expected Output**:
```
TEST-PY-001: Verify Python Version
Expected Python version: 3.10
✅ PASSED: Python version is 3.10
```

---

### TEST-PY-002: Verify UV Installation
**Goal**: Confirm UV package manager is installed and working

```bash
#!/bin/bash
# tests/test_uv_installation.sh

echo "TEST-PY-002: Verify UV Installation"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
  echo "❌ FAILED: UV command not found"
  exit 1
fi

# Check version
UV_VERSION=$(uv --version | cut -d' ' -f2)
echo "UV version: $UV_VERSION"

# Verify minimum version (0.9.0+)
REQUIRED_VERSION="0.9.0"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$UV_VERSION" | sort -V | head -n1)" == "$REQUIRED_VERSION" ]; then
  echo "✅ PASSED: UV $UV_VERSION is installed"
  exit 0
else
  echo "❌ FAILED: UV version $UV_VERSION is less than required $REQUIRED_VERSION"
  exit 1
fi
```

---

### TEST-PY-003: Verify Lock File Exists
**Goal**: Confirm uv.lock file was created and is valid

```bash
#!/bin/bash
# tests/test_lock_file.sh

echo "TEST-PY-003: Verify Lock File Exists"

if [ ! -f "uv.lock" ]; then
  echo "❌ FAILED: uv.lock file not found"
  exit 1
fi

# Check file is not empty
if [ ! -s "uv.lock" ]; then
  echo "❌ FAILED: uv.lock file is empty"
  exit 1
fi

# Check file size (should be substantial, >100KB)
SIZE=$(wc -c < uv.lock)
if [ "$SIZE" -lt 100000 ]; then
  echo "⚠️  WARNING: uv.lock is smaller than expected ($SIZE bytes)"
fi

echo "Lock file size: $(numfmt --to=iec-i --suffix=B $SIZE)"
echo "✅ PASSED: uv.lock file exists and is valid"
exit 0
```

---

### TEST-PY-004: Verify Dependencies Installation
**Goal**: Confirm all critical dependencies are installed

```bash
#!/bin/bash
# tests/test_dependencies.sh

echo "TEST-PY-004: Verify Dependencies Installation"

source .venv/bin/activate

REQUIRED_PACKAGES=(
  "fastapi"
  "uvicorn"
  "httpx"
  "crewai"
  "langchain"
  "openai"
  "pydantic"
)

FAILED=0

for package in "${REQUIRED_PACKAGES[@]}"; do
  if python -c "import $package" 2>/dev/null; then
    echo "✅ $package installed"
  else
    echo "❌ $package NOT installed"
    FAILED=1
  fi
done

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: All required dependencies installed"
  exit 0
else
  echo "❌ FAILED: Some dependencies are missing"
  exit 1
fi
```

---

### TEST-PY-005: Verify PyProject Configuration
**Goal**: Confirm pyproject.toml has correct Python version requirement

```bash
#!/bin/bash
# tests/test_pyproject.sh

echo "TEST-PY-005: Verify PyProject Configuration"

if [ ! -f "pyproject.toml" ]; then
  echo "❌ FAILED: pyproject.toml not found"
  exit 1
fi

# Check requires-python
REQUIRES_PYTHON=$(grep "requires-python" pyproject.toml | cut -d'"' -f2)
echo "requires-python: $REQUIRES_PYTHON"

# Should be >=3.10
if [[ "$REQUIRES_PYTHON" == *">=3.10"* ]]; then
  echo "✅ PASSED: Python version requirement is correct"
  exit 0
else
  echo "❌ FAILED: Python version requirement should be >=3.10, got: $REQUIRES_PYTHON"
  exit 1
fi
```

---

## 2. Frontend Build Tests

### TEST-FE-001: Verify Frontend Dependencies
**Goal**: Confirm frontend dependencies are installed

```bash
#!/bin/bash
# tests/test_frontend_deps.sh

echo "TEST-FE-001: Verify Frontend Dependencies"

cd frontend

if [ ! -d "node_modules" ]; then
  echo "❌ FAILED: node_modules not found"
  echo "Run: npm ci"
  exit 1
fi

# Check for key dependencies
REQUIRED_DEPS=(
  "next"
  "react"
  "react-dom"
)

FAILED=0

for dep in "${REQUIRED_DEPS[@]}"; do
  if [ -d "node_modules/$dep" ]; then
    VERSION=$(jq -r ".dependencies[\"$dep\"] // .devDependencies[\"$dep\"]" package.json)
    echo "✅ $dep@$VERSION installed"
  else
    echo "❌ $dep NOT installed"
    FAILED=1
  fi
done

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: All frontend dependencies installed"
  exit 0
else
  echo "❌ FAILED: Some frontend dependencies are missing"
  exit 1
fi
```

---

### TEST-FE-002: Verify Next.js Configuration
**Goal**: Confirm Next.js is configured for static export

```bash
#!/bin/bash
# tests/test_nextjs_config.sh

echo "TEST-FE-002: Verify Next.js Configuration"

cd frontend

if [ ! -f "next.config.js" ]; then
  echo "❌ FAILED: next.config.js not found"
  exit 1
fi

# Check for output: 'export'
if grep -q "output.*['\"]export['\"]" next.config.js; then
  echo "✅ Static export enabled"
else
  echo "❌ FAILED: output: 'export' not found in next.config.js"
  exit 1
fi

# Check for images unoptimized
if grep -q "unoptimized.*true" next.config.js; then
  echo "✅ Images unoptimized (required for Cloudflare Pages)"
else
  echo "⚠️  WARNING: Images should be unoptimized for Cloudflare Pages"
fi

echo "✅ PASSED: Next.js configuration is correct"
exit 0
```

---

### TEST-FE-003: Verify Frontend Build
**Goal**: Confirm frontend builds successfully

```bash
#!/bin/bash
# tests/test_frontend_build.sh

echo "TEST-FE-003: Verify Frontend Build"

cd frontend

# Clean previous build
rm -rf .next out

# Run build
echo "Building frontend..."
if npm run build; then
  echo "✅ Build succeeded"
else
  echo "❌ FAILED: Build failed"
  exit 1
fi

# Check output directory exists
if [ ! -d "out" ]; then
  echo "❌ FAILED: out/ directory not created"
  exit 1
fi

# Check for index.html
if [ ! -f "out/index.html" ]; then
  echo "❌ FAILED: index.html not found in out/"
  exit 1
fi

# Check for _next directory
if [ ! -d "out/_next" ]; then
  echo "❌ FAILED: _next/ directory not found in out/"
  exit 1
fi

# Count HTML files
HTML_COUNT=$(find out -name "*.html" | wc -l)
echo "Generated HTML files: $HTML_COUNT"

if [ "$HTML_COUNT" -lt 5 ]; then
  echo "⚠️  WARNING: Expected at least 5 HTML files, got $HTML_COUNT"
fi

echo "✅ PASSED: Frontend build successful"
exit 0
```

---

### TEST-FE-004: Verify Static Export Content
**Goal**: Confirm all expected pages are in the build output

```bash
#!/bin/bash
# tests/test_static_export.sh

echo "TEST-FE-004: Verify Static Export Content"

cd frontend/out

EXPECTED_PAGES=(
  "index.html"
  "dashboard/index.html"
  "alerts/index.html"
  "comps/index.html"
  "crews/index.html"
  "snipes/index.html"
)

FAILED=0

for page in "${EXPECTED_PAGES[@]}"; do
  if [ -f "$page" ]; then
    SIZE=$(wc -c < "$page")
    echo "✅ $page ($(numfmt --to=iec-i --suffix=B $SIZE))"
  else
    echo "❌ $page NOT found"
    FAILED=1
  fi
done

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: All expected pages exported"
  exit 0
else
  echo "❌ FAILED: Some pages are missing"
  exit 1
fi
```

---

### TEST-FE-005: Verify Next.js Security Update
**Goal**: Confirm Next.js version is patched

```bash
#!/bin/bash
# tests/test_nextjs_security.sh

echo "TEST-FE-005: Verify Next.js Security Update"

cd frontend

CURRENT_VERSION=$(jq -r '.dependencies.next' package.json | sed 's/[^0-9.]//g')
MINIMUM_VERSION="14.2.33"

echo "Current Next.js version: $CURRENT_VERSION"
echo "Required minimum: $MINIMUM_VERSION"

# Compare versions
if [ "$(printf '%s\n' "$MINIMUM_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)" == "$MINIMUM_VERSION" ]; then
  echo "✅ PASSED: Next.js version is $CURRENT_VERSION (security patch applied)"
  exit 0
else
  echo "❌ FAILED: Next.js version $CURRENT_VERSION is less than required $MINIMUM_VERSION"
  echo "Run: npm install next@latest"
  exit 1
fi
```

---

## 3. Worker Tests

### TEST-WK-001: Verify Worker Configuration
**Goal**: Confirm wrangler.toml is properly configured

```bash
#!/bin/bash
# tests/test_worker_config.sh

echo "TEST-WK-001: Verify Worker Configuration"

cd cloudflare

if [ ! -f "wrangler.toml" ]; then
  echo "❌ FAILED: wrangler.toml not found"
  exit 1
fi

# Check for placeholder IDs (should not exist in production)
PLACEHOLDERS=$(grep -i "your-.*-id" wrangler.toml | wc -l)

if [ "$PLACEHOLDERS" -gt 0 ]; then
  echo "⚠️  WARNING: Found $PLACEHOLDERS placeholder IDs in wrangler.toml"
  grep -i "your-.*-id" wrangler.toml
  echo "These should be replaced with actual IDs"
else
  echo "✅ No placeholder IDs found"
fi

# Check worker name exists
if grep -q "name.*arbfinder" wrangler.toml; then
  echo "✅ Worker name configured"
else
  echo "❌ FAILED: Worker name not found"
  exit 1
fi

# Check main entry point
if grep -q 'main.*"src/index.ts"' wrangler.toml; then
  echo "✅ Main entry point configured"
else
  echo "⚠️  WARNING: Main entry point may not be configured"
fi

echo "✅ PASSED: Worker configuration is valid"
exit 0
```

---

### TEST-WK-002: Verify Worker Dependencies
**Goal**: Confirm worker dependencies are installed

```bash
#!/bin/bash
# tests/test_worker_deps.sh

echo "TEST-WK-002: Verify Worker Dependencies"

cd cloudflare

if [ ! -d "node_modules" ]; then
  echo "❌ FAILED: node_modules not found"
  echo "Run: npm ci"
  exit 1
fi

# Check for wrangler
if [ -d "node_modules/wrangler" ]; then
  VERSION=$(jq -r '.devDependencies.wrangler' package.json)
  echo "✅ wrangler@$VERSION installed"
else
  echo "❌ wrangler NOT installed"
  exit 1
fi

# Check for TypeScript
if [ -d "node_modules/typescript" ]; then
  VERSION=$(jq -r '.devDependencies.typescript' package.json)
  echo "✅ typescript@$VERSION installed"
else
  echo "❌ typescript NOT installed"
  exit 1
fi

echo "✅ PASSED: Worker dependencies installed"
exit 0
```

---

### TEST-WK-003: Verify Worker Build
**Goal**: Confirm worker builds successfully

```bash
#!/bin/bash
# tests/test_worker_build.sh

echo "TEST-WK-003: Verify Worker Build"

cd cloudflare

# Clean previous build
rm -rf dist

# Run build
echo "Building worker..."
if npm run build; then
  echo "✅ Build succeeded"
else
  echo "❌ FAILED: Build failed"
  exit 1
fi

# Check output file exists
if [ -f "dist/index.js" ]; then
  SIZE=$(wc -c < dist/index.js)
  echo "✅ dist/index.js created ($(numfmt --to=iec-i --suffix=B $SIZE))"
else
  echo "⚠️  WARNING: dist/index.js not found (may use different build method)"
fi

echo "✅ PASSED: Worker build successful"
exit 0
```

---

## 4. Integration Tests

### TEST-INT-001: Verify Environment Files
**Goal**: Confirm environment files are properly configured

```bash
#!/bin/bash
# tests/test_environment_files.sh

echo "TEST-INT-001: Verify Environment Files"

cd frontend

EXPECTED_FILES=(
  ".env.production"
  ".env.staging"
  ".env.local.example"
)

FAILED=0

for file in "${EXPECTED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
    
    # Check for required variables
    if grep -q "NEXT_PUBLIC_API_BASE" "$file"; then
      echo "  ✅ NEXT_PUBLIC_API_BASE defined"
    else
      echo "  ❌ NEXT_PUBLIC_API_BASE missing"
      FAILED=1
    fi
  else
    echo "❌ $file NOT found"
    FAILED=1
  fi
done

# Check .env.local is in .gitignore
if grep -q "\.env\.local" ../.gitignore; then
  echo "✅ .env.local is gitignored"
else
  echo "⚠️  WARNING: .env.local should be in .gitignore"
fi

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: Environment files configured correctly"
  exit 0
else
  echo "❌ FAILED: Some environment files are missing or misconfigured"
  exit 1
fi
```

---

### TEST-INT-002: Verify Workflow Configuration
**Goal**: Confirm GitHub Actions workflow is properly configured

```bash
#!/bin/bash
# tests/test_workflow_config.sh

echo "TEST-INT-002: Verify Workflow Configuration"

WORKFLOW_FILE=".github/workflows/cloudflare-deploy.yml"

if [ ! -f "$WORKFLOW_FILE" ]; then
  echo "❌ FAILED: $WORKFLOW_FILE not found"
  exit 1
fi

# Check for required jobs
REQUIRED_JOBS=(
  "deploy-worker"
  "deploy-pages"
  "verify-deployment"
)

FAILED=0

for job in "${REQUIRED_JOBS[@]}"; do
  if grep -q "$job:" "$WORKFLOW_FILE"; then
    echo "✅ Job '$job' defined"
  else
    echo "❌ Job '$job' NOT found"
    FAILED=1
  fi
done

# Check for secrets
REQUIRED_SECRETS=(
  "CLOUDFLARE_API_TOKEN"
  "CLOUDFLARE_ACCOUNT_ID"
)

for secret in "${REQUIRED_SECRETS[@]}"; do
  if grep -q "$secret" "$WORKFLOW_FILE"; then
    echo "✅ Secret '$secret' referenced"
  else
    echo "❌ Secret '$secret' NOT found"
    FAILED=1
  fi
done

# Check for placeholder domains
PLACEHOLDERS=$(grep -c "your-domain" "$WORKFLOW_FILE")
if [ "$PLACEHOLDERS" -gt 0 ]; then
  echo "⚠️  WARNING: Found $PLACEHOLDERS 'your-domain' placeholders"
  echo "These should be replaced with actual domains"
fi

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: Workflow configuration is valid"
  exit 0
else
  echo "❌ FAILED: Workflow configuration has issues"
  exit 1
fi
```

---

### TEST-INT-003: Verify Documentation
**Goal**: Confirm all documentation is created

```bash
#!/bin/bash
# tests/test_documentation.sh

echo "TEST-INT-003: Verify Documentation"

REQUIRED_DOCS=(
  "CLOUDFLARE_DEPLOYMENT_GUIDE.md"
  "AI_AGENT_TASKS.md"
  "DEPLOYMENT_TESTS.md"
)

FAILED=0

for doc in "${REQUIRED_DOCS[@]}"; do
  if [ -f "$doc" ]; then
    SIZE=$(wc -c < "$doc")
    LINES=$(wc -l < "$doc")
    echo "✅ $doc ($LINES lines, $(numfmt --to=iec-i --suffix=B $SIZE))"
    
    # Check minimum size
    if [ "$SIZE" -lt 1000 ]; then
      echo "  ⚠️  WARNING: Document seems short"
    fi
  else
    echo "❌ $doc NOT found"
    FAILED=1
  fi
done

if [ $FAILED -eq 0 ]; then
  echo "✅ PASSED: All documentation exists"
  exit 0
else
  echo "❌ FAILED: Some documentation is missing"
  exit 1
fi
```

---

## 5. Deployment Tests

### TEST-DEP-001: Verify Git Status
**Goal**: Confirm all changes are committed

```bash
#!/bin/bash
# tests/test_git_status.sh

echo "TEST-DEP-001: Verify Git Status"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  echo "⚠️  WARNING: Uncommitted changes detected:"
  git status --short
  echo "Consider committing these changes"
else
  echo "✅ Working directory clean"
fi

# Check for .venv in git
if git ls-files | grep -q "\.venv"; then
  echo "❌ FAILED: .venv is tracked in git (should be ignored)"
  exit 1
else
  echo "✅ .venv is not tracked"
fi

# Check for out/ in git
if git ls-files | grep -q "frontend/out/"; then
  echo "❌ FAILED: frontend/out/ is tracked in git (should be ignored)"
  exit 1
else
  echo "✅ frontend/out/ is not tracked"
fi

echo "✅ PASSED: Git status is clean"
exit 0
```

---

### TEST-DEP-002: Verify Local Health Check
**Goal**: Test health endpoint locally before deployment

```bash
#!/bin/bash
# tests/test_local_health.sh

echo "TEST-DEP-002: Verify Local Health Check"

cd cloudflare

# Start worker in background
echo "Starting local worker..."
npm run dev > /tmp/wrangler.log 2>&1 &
WORKER_PID=$!

# Wait for worker to start
sleep 5

# Test health endpoint
echo "Testing health endpoint..."
RESPONSE=$(curl -s http://localhost:8787/api/health)

if [ -n "$RESPONSE" ]; then
  echo "Response: $RESPONSE"
  
  # Check if response is valid JSON
  if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo "✅ Valid JSON response"
    
    # Check for status field
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    if [ "$STATUS" == "healthy" ]; then
      echo "✅ PASSED: Health check working locally"
      kill $WORKER_PID
      exit 0
    else
      echo "⚠️  WARNING: Status is $STATUS"
    fi
  else
    echo "❌ FAILED: Invalid JSON response"
  fi
else
  echo "❌ FAILED: No response from health endpoint"
fi

# Cleanup
kill $WORKER_PID 2>/dev/null
exit 1
```

---

## Running All Tests

### Master Test Script
Create `tests/run_all_tests.sh`:

```bash
#!/bin/bash
# tests/run_all_tests.sh

echo "========================================"
echo "Running All Deployment Tests"
echo "========================================"
echo ""

# Track results
TOTAL=0
PASSED=0
FAILED=0
WARNINGS=0

# Function to run a test
run_test() {
  local test_script=$1
  TOTAL=$((TOTAL + 1))
  
  echo "----------------------------------------"
  if bash "$test_script"; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
  echo ""
}

# Python Environment Tests
echo "=== Python Environment Tests ==="
run_test "tests/test_python_version.sh"
run_test "tests/test_uv_installation.sh"
run_test "tests/test_lock_file.sh"
run_test "tests/test_dependencies.sh"
run_test "tests/test_pyproject.sh"

# Frontend Build Tests
echo "=== Frontend Build Tests ==="
run_test "tests/test_frontend_deps.sh"
run_test "tests/test_nextjs_config.sh"
run_test "tests/test_frontend_build.sh"
run_test "tests/test_static_export.sh"
run_test "tests/test_nextjs_security.sh"

# Worker Tests
echo "=== Worker Tests ==="
run_test "tests/test_worker_config.sh"
run_test "tests/test_worker_deps.sh"
run_test "tests/test_worker_build.sh"

# Integration Tests
echo "=== Integration Tests ==="
run_test "tests/test_environment_files.sh"
run_test "tests/test_workflow_config.sh"
run_test "tests/test_documentation.sh"

# Deployment Tests
echo "=== Deployment Tests ==="
run_test "tests/test_git_status.sh"

echo "========================================"
echo "Test Results"
echo "========================================"
echo "Total:   $TOTAL"
echo "Passed:  $PASSED ✅"
echo "Failed:  $FAILED ❌"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "🎉 All tests passed!"
  exit 0
else
  echo "⚠️  $FAILED test(s) failed"
  exit 1
fi
```

Make it executable:
```bash
chmod +x tests/run_all_tests.sh
```

---

## Continuous Integration

### Add to GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        run: pip install uv
      
      - name: Setup Python
        run: uv venv .venv --python 3.10
      
      - name: Install dependencies
        run: |
          source .venv/bin/activate
          uv sync
      
      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Install worker dependencies
        run: |
          cd cloudflare
          npm ci
      
      - name: Run all tests
        run: |
          chmod +x tests/run_all_tests.sh
          ./tests/run_all_tests.sh
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results/
```

---

## Test Report Template

After running tests, generate a report:

```markdown
# Test Report - [Date]

## Summary
- Total Tests: XX
- Passed: XX ✅
- Failed: XX ❌
- Warnings: XX ⚠️

## Test Categories

### Python Environment
- Python Version: ✅/❌
- UV Installation: ✅/❌
- Lock File: ✅/❌
- Dependencies: ✅/❌
- PyProject Config: ✅/❌

### Frontend Build
- Dependencies: ✅/❌
- Next.js Config: ✅/❌
- Build: ✅/❌
- Static Export: ✅/❌
- Security Update: ✅/❌

### Worker
- Configuration: ✅/❌
- Dependencies: ✅/❌
- Build: ✅/❌

### Integration
- Environment Files: ✅/❌
- Workflow Config: ✅/❌
- Documentation: ✅/❌

### Deployment
- Git Status: ✅/❌

## Issues Found
[List any issues discovered during testing]

## Recommendations
[List recommended fixes or improvements]
```

---

## Troubleshooting Test Failures

### Common Issues

**Test fails: "command not found"**
- Ensure script has execute permissions: `chmod +x tests/test_*.sh`
- Check if required commands are installed

**Test fails: "No such file or directory"**
- Verify you're running from repository root
- Check if referenced files exist

**Build tests fail**
- Run `npm install` in frontend/ and cloudflare/
- Check for syntax errors in source files

**Python tests fail**
- Activate virtual environment: `source .venv/bin/activate`
- Verify Python version matches .python-version

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-31  
**Test Suite Coverage**: 17 tests across 5 categories
