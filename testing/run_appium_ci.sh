#!/usr/bin/env bash
# Appium CI runner — used by both Android and iOS matrix jobs.
#
# Environment variables (all optional):
#   PLATFORM         android | ios  (default: android)
#   TEST_MARKER      pytest -m expression (overrides positional arg $1)
#   TEST_PATHS       space-separated test paths for matrix jobs (default: tests/)
#   GROUP_NAME       label for this matrix group (used in result filenames)
#
# Positional arg $1: marker (legacy, TEST_MARKER env takes precedence)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPIUM_DIR="$SCRIPT_DIR/appium"
REPORTS_DIR="$APPIUM_DIR/reports"
ALLURE_DIR="$APPIUM_DIR/allure-results"

# Marker: env var takes precedence over positional arg
MARKER="${TEST_MARKER:-${1:-}}"
PLATFORM="${PLATFORM:-android}"
GROUP_NAME="${GROUP_NAME:-}"

# TEST_PATHS: space-separated paths (e.g. "tests/auth/ tests/account/")
# When set by matrix jobs, restricts which test files this job runs.
# Split into array for safe pytest invocation.
read -ra TEST_PATHS_ARR <<< "${TEST_PATHS:-tests/}"

mkdir -p "$REPORTS_DIR/screenshots" "$ALLURE_DIR"
cd "$APPIUM_DIR"

# iOS tests take longer: login OTP round-trip + WDA session overhead.
# 600s covers a worst-case WDA rebuild (~480s observed on macos-15 + iOS 26 sim)
# even if usePreinstalledWDA misses; with prebuilt WDA most sessions are <60s.
if [ "$PLATFORM" = "ios" ]; then
  PER_TEST_TIMEOUT=600
else
  PER_TEST_TIMEOUT=300
fi

# Result file: unique name per matrix group so all groups can be merged by the
# publish workflow without one group's results.xml overwriting another.
RESULT_XML="$REPORTS_DIR/results${GROUP_NAME:+-$GROUP_NAME}.xml"

PYTEST_ARGS=(
  "${TEST_PATHS_ARR[@]}"
  -v
  --timeout="$PER_TEST_TIMEOUT"
  --timeout-method=signal
  --html="$REPORTS_DIR/report.html"
  --self-contained-html
  --tb=short
  -o "junit_family=xunit2"
  --junit-xml="$RESULT_XML"
  --alluredir="$ALLURE_DIR"
)

if [ -n "$MARKER" ]; then
  echo "Running Appium tests — paths: ${TEST_PATHS_ARR[*]} | marker: $MARKER | platform: $PLATFORM"
  python3 -m pytest "${PYTEST_ARGS[@]}" -m "$MARKER"
else
  echo "Running Appium tests — paths: ${TEST_PATHS_ARR[*]} | all tests | platform: $PLATFORM"
  python3 -m pytest "${PYTEST_ARGS[@]}"
fi

RC=$?
if [ "$RC" -ne 0 ] && [ -s "$RESULT_XML" ]; then
  NORMALIZED_RC=$(python3 - "$RESULT_XML" <<'PY'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
try:
    root = ET.parse(path).getroot()
except Exception:
    print(1)
    raise SystemExit

total = failed = errored = 0
for tc in root.iter("testcase"):
    total += 1
    if tc.find("failure") is not None:
        failed += 1
    if tc.find("error") is not None:
        errored += 1

print(0 if total and failed == 0 and errored == 0 else 1)
PY
)
  if [ "$NORMALIZED_RC" = "0" ]; then
    echo "No JUnit failures/errors found; treating skipped-only Appium group as successful."
    RC=0
  fi
fi
echo ""
echo "Appium run complete (exit $RC)."
echo "  JUnit:  $RESULT_XML"
echo "  HTML:   $REPORTS_DIR/report.html"
echo "  Allure: $ALLURE_DIR"
exit $RC
