#!/bin/bash
# Test that pyproject.toml has correct Python version requirement

set -e

echo "TEST: Verify PyProject Configuration"

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
