#!/usr/bin/env bash
# Smoke CI runner — called from reactivecircus/android-emulator-runner script:
# Each flow runs independently; failures are counted but don't stop the suite.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=300   # 5 min hard cap per flow — prevents a stuck flow from eating the budget

FAIL=0
for flow in 01_splash_onboarding 02_login_otp 03_guest_user 05_cart_add_items 06_checkout_payment_select; do
  echo "▶  Running flow: $flow"
  timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$REPORTS_DIR/${flow}-results.xml" \
    "$FLOWS_DIR/${flow}.yaml" \
    && echo "   ✓ $flow" \
    || {
      RC=$?
      [ "$RC" -eq 124 ] && echo "   ✗ $flow TIMED OUT (>${FLOW_TIMEOUT}s)" \
                        || echo "   ✗ $flow FAILED (exit $RC)"
      FAIL=$((FAIL + 1))
    }
done

echo ""
echo "Smoke complete: $FAIL flow(s) failed."
exit $FAIL
