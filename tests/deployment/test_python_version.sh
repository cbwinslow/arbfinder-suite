#!/bin/bash
# Test Python version is correctly set to 3.10

set -e

echo "TEST: Verify Python Version"

# Check .python-version file
if [ ! -f ".python-version" ]; then
  echo "❌ FAILED: .python-version file not found"
  exit 1
fi

EXPECTED_VERSION=$(cat .python-version)
echo "Expected Python version: $EXPECTED_VERSION"

# Check if .venv exists
if [ ! -d ".venv" ]; then
  echo "❌ FAILED: .venv directory not found"
  exit 1
fi

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
