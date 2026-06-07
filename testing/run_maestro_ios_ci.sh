#!/usr/bin/env bash
# iOS Maestro CI runner — per-flow JUnit XMLs (same pattern as Android smoke/regression).
# Usage: bash testing/run_maestro_ios_ci.sh [smoke|regression|negative]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
SUITE="${1:-smoke}"

mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=240

flows_for_suite() {
  case "$SUITE" in
    smoke)
      # Must match testing/maestro/flows/suites/smoke.yaml
      echo "$FLOWS_DIR/01_splash_onboarding.yaml"
      echo "$FLOWS_DIR/02_login_otp.yaml"
      echo "$FLOWS_DIR/03_guest_user.yaml"
      echo "$FLOWS_DIR/05_cart_add_items.yaml"
      echo "$FLOWS_DIR/06_checkout_payment_select.yaml"
      echo "$FLOWS_DIR/26_mosque_profile_view.yaml"
      echo "$FLOWS_DIR/28_donation_sadaqah.yaml"
      echo "$FLOWS_DIR/39_logout_success.yaml"
      ;;
    regression)
      ls "$FLOWS_DIR"/[0-9][0-9]_*.yaml 2>/dev/null | sort
      ;;
    negative)
      ls "$FLOWS_DIR"/1[789]_*.yaml "$FLOWS_DIR"/2[0123]_*.yaml 2>/dev/null | sort
      ;;
    *)
      echo "Unknown suite: $SUITE (expected smoke|regression|negative)" >&2
      return 1
      ;;
  esac
}

FAIL=0
while IFS= read -r flow_yaml; do
  [ -f "$flow_yaml" ] || continue
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
done < <(flows_for_suite)

echo ""
echo "iOS Maestro ${SUITE} complete: $FAIL flow(s) failed."
exit "$FAIL"
