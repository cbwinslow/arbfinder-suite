#!/bin/bash
# Run all deployment tests

echo "========================================"
echo "Running Deployment Tests"
echo "========================================"
echo ""

# Track results
TOTAL=0
PASSED=0
FAILED=0

# Function to run a test
run_test() {
  local test_script=$1
  local test_name=$(basename "$test_script" .sh)
  
  TOTAL=$((TOTAL + 1))
  
  echo "----------------------------------------"
  echo "Running: $test_name"
  echo "----------------------------------------"
  
  if bash "$test_script"; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
  echo ""
}

# Change to repository root
cd "$(dirname "$0")/../.."

# Run tests
run_test "tests/deployment/test_python_version.sh"
run_test "tests/deployment/test_lock_file.sh"
run_test "tests/deployment/test_pyproject.sh"
run_test "tests/deployment/test_nextjs_config.sh"
run_test "tests/deployment/test_frontend_build.sh"

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
