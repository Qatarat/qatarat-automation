#!/usr/bin/env bash
# Appium CI runner — called from reactivecircus/android-emulator-runner script:
#   bash testing/run_appium_ci.sh [pytest_marker]
# Pass a pytest marker (payment|gift|subscription|account|streaming) as $1
# to run only that subset; omit for the full test suite.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPIUM_DIR="$SCRIPT_DIR/appium"
REPORTS_DIR="$APPIUM_DIR/reports"
ALLURE_DIR="$APPIUM_DIR/allure-results"
MARKER="${1:-}"
PLATFORM="${PLATFORM:-android}"

mkdir -p "$REPORTS_DIR/screenshots" "$ALLURE_DIR"

cd "$APPIUM_DIR"

# iOS: 420s per test — login flow on slow CI simulator takes ~260s (multi-strategy
# element search + OTP round-trip + navigation). 300s was too tight.
# Android: 300s unchanged.
if [ "$PLATFORM" = "ios" ]; then
  PER_TEST_TIMEOUT=420
else
  PER_TEST_TIMEOUT=300
fi

PYTEST_ARGS=(
  tests/
  -v
  --timeout="$PER_TEST_TIMEOUT"
  --timeout-method=signal
  --html="$REPORTS_DIR/report.html"
  --self-contained-html
  --tb=short
  -o "junit_family=xunit2"
  --junit-xml="$REPORTS_DIR/results.xml"
  --alluredir="$ALLURE_DIR"
)

if [ -n "$MARKER" ]; then
  echo "Running Appium tests with marker: $MARKER (platform: $PLATFORM)"
  python3 -m pytest "${PYTEST_ARGS[@]}" -m "$MARKER"
else
  echo "Running full Appium test suite (platform: $PLATFORM)"
  python3 -m pytest "${PYTEST_ARGS[@]}"
fi

RC=$?
echo ""
echo "Appium run complete (exit $RC)."
echo "  JUnit:  $REPORTS_DIR/results.xml"
echo "  HTML:   $REPORTS_DIR/report.html"
echo "  Allure: $ALLURE_DIR"
exit $RC
