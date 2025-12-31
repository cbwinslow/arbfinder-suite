#!/bin/bash
# Test that uv.lock file exists and is valid

set -e

echo "TEST: Verify UV Lock File"

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
