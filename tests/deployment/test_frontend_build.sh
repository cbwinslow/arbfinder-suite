#!/bin/bash
# Test that frontend builds successfully

set -e

echo "TEST: Verify Frontend Build"

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm ci
fi

# Clean previous build
rm -rf .next out

# Run build
echo "Building frontend..."
if npm run build 2>&1 | tee /tmp/build.log; then
  echo "✅ Build succeeded"
else
  echo "❌ FAILED: Build failed"
  cat /tmp/build.log
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
