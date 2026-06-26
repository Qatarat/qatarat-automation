#!/usr/bin/env bash
# Loop adb screenrecord in 170 s segments until /tmp/android_rec_on is removed.
# Usage: bash testing/record_android.sh <segments_dir>

SEGS_DIR="${1:-/tmp/adb_segs}"
mkdir -p "$SEGS_DIR"
SEG=0
ADB_PID=""

cleanup() {
  rm -f /tmp/android_rec_on
  if [ -n "${ADB_PID:-}" ]; then
    kill "$ADB_PID" 2>/dev/null || true
    wait "$ADB_PID" 2>/dev/null || true
  fi
  adb shell "pkill -INT screenrecord" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "[rec] android recorder started"

while [ -f /tmp/android_rec_on ]; do
  REMOTE="/data/local/tmp/rec_${SEG}.mp4"
  LOCAL="$SEGS_DIR/seg_${SEG}.mp4"

  adb shell "screenrecord --time-limit 170 $REMOTE" &
  ADB_PID=$!

  ELAPSED=0
  while [ $ELAPSED -lt 173 ] && [ -f /tmp/android_rec_on ]; do
    sleep 1; ELAPSED=$((ELAPSED + 1))
  done

  adb shell "pkill -INT screenrecord" 2>/dev/null || true
  sleep 1
  wait "$ADB_PID" 2>/dev/null || true
  sleep 1

  adb pull "$REMOTE" "$LOCAL" 2>/dev/null \
    && echo "[rec] seg_${SEG} pulled ($(du -sh "$LOCAL" 2>/dev/null | cut -f1))" \
    || echo "[rec] pull failed seg_${SEG}"

  SEG=$((SEG + 1))
done

echo "[rec] finished — $SEG segment(s) recorded"
