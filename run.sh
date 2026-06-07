#!/bin/sh
# macOS / Linux — one-command launcher + test runner
# Usage:
#   ./run.sh               → start app only (Android)
#   ./run.sh smoke         → app + Maestro smoke tests (Android)
#   ./run.sh regression    → app + all 50 Maestro flows (Android)
#   ./run.sh appium        → app + all 191 Appium tests (Android)
#   ./run.sh all           → app + Maestro regression + Appium (Android)
#
# iOS Usage (macOS only):
#   ./run.sh ios               → start iOS app only
#   ./run.sh ios smoke         → iOS app + Maestro smoke tests
#   ./run.sh ios regression    → iOS app + Maestro regression
#   ./run.sh ios appium        → iOS app + Appium tests
#   ./run.sh ios all           → iOS app + Maestro + Appium
set -e
cd "$(dirname "$0")"

# If the first argument is "ios", route to run_ios.py
if [ "$1" = "ios" ]; then
  shift  # remove 'ios' from arguments
  if command -v python3 >/dev/null 2>&1; then
    python3 run_ios.py "$@"
  elif command -v python >/dev/null 2>&1; then
    python run_ios.py "$@"
  else
    echo "ERROR: Python 3 not found. Install from https://python.org"
    exit 1
  fi
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  python3 run.py "$@"
elif command -v python >/dev/null 2>&1; then
  python run.py "$@"
else
  echo "ERROR: Python 3 not found. Install from https://python.org"
  exit 1
fi
