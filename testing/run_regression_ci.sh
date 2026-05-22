#!/usr/bin/env bash
# Regression CI runner — called from reactivecircus/android-emulator-runner script:
# Pass a flow number prefix (e.g. "07") as $1 to run a single flow; omit for all 16.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
SOLO_FLOW="${1:-}"
mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=480   # 8 min hard cap per flow for regression (some flows are heavier)

_run_flow() {
  local flow_file="$1"
  local name
  name="$(basename "$flow_file" .yaml)"
  echo "▶  Running flow: $name"
  timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$REPORTS_DIR/${name}-results.xml" \
    "$flow_file" \
    && echo "   ✓ $name" \
    || {
      RC=$?
      [ "$RC" -eq 124 ] && echo "   ✗ $name TIMED OUT (>${FLOW_TIMEOUT}s)" \
                        || echo "   ✗ $name FAILED (exit $RC)"
      return 1
    }
}

FAIL=0
if [ -n "$SOLO_FLOW" ]; then
  FLOW_FILE="$(ls "$FLOWS_DIR/${SOLO_FLOW}"*.yaml 2>/dev/null | head -1)"
  if [ -z "$FLOW_FILE" ]; then
    echo "ERROR: no flow file found for prefix '$SOLO_FLOW'"
    exit 1
  fi
  _run_flow "$FLOW_FILE" || FAIL=1
else
  for flow_file in "$FLOWS_DIR"/[0-9][0-9]_*.yaml; do
    _run_flow "$flow_file" || FAIL=$((FAIL + 1))
  done
fi

echo ""
echo "Regression complete: $FAIL flow(s) failed."
exit $FAIL
