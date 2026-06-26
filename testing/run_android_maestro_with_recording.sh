#!/usr/bin/env bash
# Run one Android Maestro suite and preserve its result after recorder cleanup.

set -uo pipefail

MODE="${1:?Usage: $0 <smoke|regression> [flow-prefix]}"
FLOW_PREFIX="${2:-}"

case "$MODE" in
  smoke)
    RUNNER=(bash testing/run_smoke_ci.sh)
    ;;
  regression)
    RUNNER=(bash testing/run_regression_ci.sh "$FLOW_PREFIX")
    ;;
  *)
    echo "Unknown suite: $MODE" >&2
    exit 2
    ;;
esac

REC_PID=""

cleanup() {
  local rc=$?
  trap - EXIT INT TERM
  rm -f /tmp/android_rec_on
  adb shell "pkill -INT screenrecord" 2>/dev/null || true
  sleep 3
  if [ -n "$REC_PID" ]; then
    kill "$REC_PID" 2>/dev/null || true
    wait "$REC_PID" 2>/dev/null || true
  fi
  exit "$rc"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

adb install -r "Qatarat (Lambda-Stage).apk"
touch /tmp/android_rec_on
mkdir -p /tmp/adb_segs
bash testing/record_android.sh /tmp/adb_segs &
REC_PID=$!

"${RUNNER[@]}"
