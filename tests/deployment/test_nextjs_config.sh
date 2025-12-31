#!/bin/bash
# Test that Next.js is configured for static export

set -e

echo "TEST: Verify Next.js Configuration"

cd frontend

if [ ! -f "next.config.js" ]; then
  echo "❌ FAILED: next.config.js not found"
  exit 1
fi

# Check for output: 'export'
if grep -q 'output.*["\x27]export["\x27]' next.config.js; then
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
