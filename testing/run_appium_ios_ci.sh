#!/usr/bin/env bash
# Appium iOS CI runner — runs Appium tests against an iOS Simulator
# Usage: bash testing/run_appium_ios_ci.sh [pytest_marker]
# Environment vars used:
#   IOS_SIM_NAME    — simulator device name (default: "iPhone 15 Pro")
#   IOS_VERSION     — iOS version (default: "17.5")
#   IOS_APP_PATH    — absolute path to Runner.app bundle (required)
#   APPIUM_HOST     — default localhost
#   APPIUM_PORT     — default 4723
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPIUM_DIR="$SCRIPT_DIR/appium"
REPORTS_DIR="$APPIUM_DIR/reports"
ALLURE_DIR="$APPIUM_DIR/allure-results"
MARKER="${1:-}"

mkdir -p "$REPORTS_DIR/screenshots" "$ALLURE_DIR"

# ── Validate IOS_APP_PATH is set ──────────────────────────────────────────────
if [ -z "${IOS_APP_PATH:-}" ]; then
  # Try auto-detect from project root
  ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  CANDIDATE="$ROOT/ipa_extracted/Payload/Runner.app"
  if [ -d "$CANDIDATE" ]; then
    export IOS_APP_PATH="$CANDIDATE"
    echo "Auto-detected IOS_APP_PATH: $IOS_APP_PATH"
  else
    echo "ERROR: IOS_APP_PATH not set and Runner.app not found at expected path."
    echo "  Expected: $CANDIDATE"
    echo "  Extract the IPA first: unzip qatarat-stage-ios.ipa -d ipa_extracted/"
    exit 1
  fi
fi

export PLATFORM=ios
export DEVICE_MODE=simulator
export IOS_SIM_NAME="${IOS_SIM_NAME:-iPhone 15 Pro}"
export IOS_VERSION="${IOS_VERSION:-17.5}"

cd "$APPIUM_DIR"

PYTEST_ARGS=(
  tests/
  -v
  --html="$REPORTS_DIR/report.html"
  --self-contained-html
  --tb=short
  -o "junit_family=xunit2"
  --junit-xml="$REPORTS_DIR/results.xml"
  --alluredir="$ALLURE_DIR"
)

if [ -n "$MARKER" ]; then
  echo "Running iOS Appium tests with marker: $MARKER"
  python3 -m pytest "${PYTEST_ARGS[@]}" -m "$MARKER"
else
  echo "Running full iOS Appium test suite"
  python3 -m pytest "${PYTEST_ARGS[@]}"
fi

RC=$?
echo ""
echo "iOS Appium run complete (exit $RC)."
echo "  JUnit:  $REPORTS_DIR/results.xml"
echo "  HTML:   $REPORTS_DIR/report.html"
echo "  Allure: $ALLURE_DIR"
exit $RC
