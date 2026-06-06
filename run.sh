#!/bin/sh
# macOS / Linux — one-command launcher + test runner
# Usage:
#   ./run.sh               → start app only
#   ./run.sh smoke         → app + Maestro smoke tests
#   ./run.sh regression    → app + all 50 Maestro flows
#   ./run.sh appium        → app + all 191 Appium tests
#   ./run.sh all           → app + Maestro regression + Appium
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  python3 run.py "$@"
elif command -v python >/dev/null 2>&1; then
  python run.py "$@"
else
  echo "ERROR: Python 3 not found. Install from https://python.org"
  exit 1
fi
