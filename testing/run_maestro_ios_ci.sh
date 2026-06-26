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

write_fallback_junit() {
  local xml_path="$1"
  local flow_name="$2"
  local status="$3"
  local message="$4"
  python3 - "$xml_path" "$flow_name" "$status" "$message" <<'PY'
import sys
import xml.etree.ElementTree as ET

xml_path, flow_name, status, message = sys.argv[1:5]
suite = ET.Element(
    "testsuite",
    {
        "name": "Maestro iOS",
        "tests": "1",
        "failures": "1" if status == "failed" else "0",
        "errors": "0",
        "skipped": "0",
    },
)
case = ET.SubElement(suite, "testcase", {"classname": "maestro.ios", "name": flow_name})
if status == "failed":
    failure = ET.SubElement(case, "failure", {"message": message})
    failure.text = message
ET.ElementTree(suite).write(xml_path, encoding="utf-8", xml_declaration=True)
PY
}

# macOS runners may lack GNU timeout — use gtimeout or perl alarm fallback
run_with_timeout() {
  local secs=$1; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  else
    perl -e 'alarm shift; exec @ARGV' "$secs" "$@"
  fi
}

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
  xml="$REPORTS_DIR/${flow}-results.xml"
  echo "▶  Running flow: $flow"
  run_with_timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$xml" \
    "$flow_yaml" \
    && {
      [ -s "$xml" ] || write_fallback_junit "$xml" "$flow" passed "Maestro passed but did not write JUnit XML"
      echo "   ✓ $flow"
    } \
    || {
      RC=$?
      if [ "$RC" -eq 124 ]; then
        message="$flow timed out after ${FLOW_TIMEOUT}s"
        echo "   ✗ $flow TIMED OUT (>${FLOW_TIMEOUT}s)"
      else
        message="$flow failed with exit $RC"
        echo "   ✗ $flow FAILED (exit $RC)"
      fi
      [ -s "$xml" ] || write_fallback_junit "$xml" "$flow" failed "$message"
      FAIL=$((FAIL + 1))
    }
done < <(flows_for_suite)

echo ""
echo "iOS Maestro ${SUITE} complete: $FAIL flow(s) failed."
exit "$FAIL"
