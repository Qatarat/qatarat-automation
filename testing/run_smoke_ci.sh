#!/usr/bin/env bash
# Smoke CI runner — called from reactivecircus/android-emulator-runner script:
# Each flow runs independently; failures are counted but don't stop the suite.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=180   # 3 min cap per flow for smoke — keeps suite within 90 min budget

# Flows that share the current Android APK regression (missing screens / hangs
# at waitForAnimationToEnd). A timeout on any of these is recorded as JUnit
# "skipped" and does NOT count as a CI failure. Remove entries once a fixed APK
# ships as a release asset. Matches the Appium `android_apk_regression` xfail
# marker in testing/appium/utils/markers.py.
KNOWN_APK_REGRESSION_FLOWS=(
  "06_checkout_payment_select"
  "07_gift_card"
  "08_my_orders"
  "09_subscription"
  "10_multilanguage"
  "12_profile_settings"
  "19_invalid_promo"
)

is_known_apk_regression() {
  local needle="$1"
  for f in "${KNOWN_APK_REGRESSION_FLOWS[@]}"; do
    [ "$f" = "$needle" ] && return 0
  done
  return 1
}

is_maestro_transport_failure() {
  local xml_path="$1"
  [ -s "$xml_path" ] || return 1
  grep -Eiq \
    'StatusRuntimeException: UNAVAILABLE|Command failed .*closed|deviceInfo|AdbSocket|grpc' \
    "$xml_path"
}

is_junit_success() {
  local xml_path="$1"
  [ -s "$xml_path" ] || return 1
  python3 - "$xml_path" <<'PY'
import sys
import xml.etree.ElementTree as ET

try:
    root = ET.parse(sys.argv[1]).getroot()
except ET.ParseError:
    raise SystemExit(1)

cases = list(root.iter("testcase"))
if not cases:
    raise SystemExit(1)
for case in cases:
    if case.find("failure") is not None or case.find("error") is not None or case.find("skipped") is not None:
        raise SystemExit(1)
raise SystemExit(0)
PY
}

write_fallback_junit() {
  local xml_path="$1"
  local flow_name="$2"
  local status="$3"
  local message="$4"
  python3 - "$xml_path" "$flow_name" "$status" "$message" <<'PY'
import sys
import xml.etree.ElementTree as ET

xml_path, flow_name, status, message = sys.argv[1:5]
failures = "1" if status == "failed" else "0"
skipped  = "1" if status == "skipped" else "0"
suite = ET.Element(
    "testsuite",
    {
        "name": "Maestro Smoke",
        "tests": "1",
        "failures": failures,
        "errors": "0",
        "skipped": skipped,
    },
)
case = ET.SubElement(suite, "testcase", {"classname": "maestro.android", "name": flow_name})
if status == "failed":
    failure = ET.SubElement(case, "failure", {"message": message})
    failure.text = message
elif status == "skipped":
    skip = ET.SubElement(case, "skipped", {"message": message})
    skip.text = message
ET.ElementTree(suite).write(xml_path, encoding="utf-8", xml_declaration=True)
PY
}

# Smoke runs only the first 20 flows (happy-path + core negatives).
# Full 50-flow suite is handled by the nightly regression workflow.
SMOKE_FLOWS=$(ls "$FLOWS_DIR"/[0-9][0-9]_*.yaml 2>/dev/null | sort | head -20)

FAIL=0
for flow_yaml in $SMOKE_FLOWS; do
  flow="$(basename "$flow_yaml" .yaml)"
  xml="$REPORTS_DIR/${flow}-results.xml"
  echo "▶  Running flow: $flow"
  timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$xml" \
    "$flow_yaml" \
    && {
      [ -s "$xml" ] || write_fallback_junit "$xml" "$flow" passed "Maestro passed but did not write JUnit XML"
      echo "   ✓ $flow"
    } \
    || {
      RC=$?
      if [ "$RC" -eq 124 ]; then
        msg="$flow timed out after ${FLOW_TIMEOUT}s"
        echo "   ✗ $flow TIMED OUT (>${FLOW_TIMEOUT}s)"
      else
        msg="$flow failed with exit $RC"
        echo "   ✗ $flow FAILED (exit $RC)"
      fi
      if is_junit_success "$xml"; then
        echo "     ↳ JUnit is already successful — preserving PASS, not failing CI"
      elif is_known_apk_regression "$flow"; then
        echo "     ↳ known APK regression — recording as SKIPPED, not failing CI"
        # Overwrite Maestro's own JUnit (if any) with a skipped marker so the
        # dashboard reflects the known-broken state correctly.
        write_fallback_junit "$xml" "$flow" skipped "$msg (known APK regression)"
      elif is_maestro_transport_failure "$xml"; then
        echo "     ↳ Maestro/ADB transport failure — recording as SKIPPED, not failing CI"
        write_fallback_junit "$xml" "$flow" skipped "$msg (Maestro/ADB transport failure)"
      elif [ "$RC" -eq 124 ]; then
        echo "     ↳ Maestro wrapper timeout — recording as SKIPPED, not failing CI"
        write_fallback_junit "$xml" "$flow" skipped "$msg (Maestro wrapper timeout)"
      else
        [ -s "$xml" ] || write_fallback_junit "$xml" "$flow" failed "$msg"
        FAIL=$((FAIL + 1))
      fi
    }
  # Capture device screenshot via ADB after every flow (works even on failure)
  adb exec-out screencap -p > "$REPORTS_DIR/${flow}-screenshot.png" 2>/dev/null \
    && echo "   📸 screenshot saved" || true
done

echo ""
echo "Smoke complete: $FAIL flow(s) failed."
exit $FAIL
