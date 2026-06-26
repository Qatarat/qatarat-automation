#!/usr/bin/env bash
# Smoke CI runner — called from reactivecircus/android-emulator-runner script:
# Each flow runs independently; failures are counted but don't stop the suite.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWS_DIR="$SCRIPT_DIR/maestro/flows"
REPORTS_DIR="$SCRIPT_DIR/maestro/reports"
mkdir -p "$REPORTS_DIR"

FLOW_TIMEOUT=180   # 3 min cap per flow for smoke — keeps suite within 90 min budget

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
        "name": "Maestro Smoke",
        "tests": "1",
        "failures": "1" if status == "failed" else "0",
        "errors": "0",
        "skipped": "0",
    },
)
case = ET.SubElement(suite, "testcase", {"classname": "maestro.android", "name": flow_name})
if status == "failed":
    failure = ET.SubElement(case, "failure", {"message": message})
    failure.text = message
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
      [ -s "$xml" ] || write_fallback_junit "$xml" "$flow" failed "$msg"
      FAIL=$((FAIL + 1))
    }
  # Capture device screenshot via ADB after every flow (works even on failure)
  adb exec-out screencap -p > "$REPORTS_DIR/${flow}-screenshot.png" 2>/dev/null \
    && echo "   📸 screenshot saved" || true
done

echo ""
echo "Smoke complete: $FAIL flow(s) failed."
exit $FAIL
