#!/usr/bin/env bash
# Smoke CI runner — called from reactivecircus/android-emulator-runner script:
# Each flow runs independently; failures are counted but don't stop the suite.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=180   # 3 min cap per flow for smoke — keeps suite within 90 min budget

# Smoke runs only the first 20 flows (happy-path + core negatives).
# Full 50-flow suite is handled by the nightly regression workflow.
SMOKE_FLOWS=$(ls "$FLOWS_DIR"/[0-9][0-9]_*.yaml 2>/dev/null | sort | head -20)

FAIL=0
for flow_yaml in $SMOKE_FLOWS; do
  flow="$(basename "$flow_yaml" .yaml)"
  echo "▶  Running flow: $flow"
  timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$REPORTS_DIR/${flow}-results.xml" \
    "$flow_yaml" \
    && echo "   ✓ $flow" \
    || {
      RC=$?
      [ "$RC" -eq 124 ] && echo "   ✗ $flow TIMED OUT (>${FLOW_TIMEOUT}s)" \
                        || echo "   ✗ $flow FAILED (exit $RC)"
      FAIL=$((FAIL + 1))
    }
  # Capture device screenshot via ADB after every flow (works even on failure)
  adb exec-out screencap -p > "$REPORTS_DIR/${flow}-screenshot.png" 2>/dev/null \
    && echo "   📸 screenshot saved" || true
done

echo ""
echo "Smoke complete: $FAIL flow(s) failed."
exit $FAIL
