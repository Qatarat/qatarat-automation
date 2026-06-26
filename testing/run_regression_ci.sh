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
        "name": "Maestro Regression",
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

_run_flow() {
  local flow_file="$1"
  local name
  name="$(basename "$flow_file" .yaml)"
  local xml="$REPORTS_DIR/${name}-results.xml"
  echo "▶  Running flow: $name"
  timeout "$FLOW_TIMEOUT" maestro test --format junit \
    --output "$xml" \
    "$flow_file" \
    && {
      [ -s "$xml" ] || write_fallback_junit "$xml" "$name" passed "Maestro passed but did not write JUnit XML"
      echo "   ✓ $name"
    } \
    || {
      RC=$?
      if [ "$RC" -eq 124 ]; then
        msg="$name timed out after ${FLOW_TIMEOUT}s"
        echo "   ✗ $name TIMED OUT (>${FLOW_TIMEOUT}s)"
      else
        msg="$name failed with exit $RC"
        echo "   ✗ $name FAILED (exit $RC)"
      fi
      [ -s "$xml" ] || write_fallback_junit "$xml" "$name" failed "$msg"
      adb exec-out screencap -p > "$REPORTS_DIR/${name}-screenshot.png" 2>/dev/null || true
      return 1
    }
  # Capture device screenshot via ADB after every flow (even on pass)
  adb exec-out screencap -p > "$REPORTS_DIR/${name}-screenshot.png" 2>/dev/null \
    && echo "   📸 screenshot saved" || true
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
