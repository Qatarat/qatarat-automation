#!/usr/bin/env bash
# Wrapper for Android Appium matrix run inside reactivecircus/android-emulator-runner.
# The action executes the `script:` block one line at a time via separate `sh -c`
# invocations, so shell variables (RC, REC_PID) do not persist across lines.
# Bundling the logic in one script keeps a single shell process.
#
# Expected env: GROUP_NAME (required), TEST_PATHS, TEST_MARKER, PLATFORM, TEST_OTP.

set -e

APK_NAME="Qatarat (Lambda-Stage).apk"
GROUP="${GROUP_NAME:-default}"
REC_REMOTE="/sdcard/android-appium-${GROUP}.mp4"
REC_LOCAL="testing/appium/reports/android-appium-${GROUP}.mp4"

echo "=== Waiting for device ==="
adb wait-for-device

echo "=== Installing APK ==="
if ! timeout 120 adb install -r "$APK_NAME"; then
    echo "::error::adb install failed"
    exit 1
fi

echo "=== APK installed — running group: $GROUP | paths: ${TEST_PATHS:-tests/} ==="
mkdir -p testing/appium/reports

rm -f "$REC_LOCAL"
adb shell rm -f "$REC_REMOTE" >/dev/null 2>&1 || true

adb shell screenrecord --time-limit 180 "$REC_REMOTE" \
    >/tmp/android-appium-screenrecord.log 2>&1 &
REC_PID=$!

set +e
bash testing/run_appium_ci.sh
RC=$?
set -e

kill -INT "$REC_PID" >/dev/null 2>&1 || true
wait "$REC_PID" >/dev/null 2>&1 || true
sleep 2
adb pull "$REC_REMOTE" "$REC_LOCAL" >/dev/null 2>&1 || true
ls -lh "$REC_LOCAL" 2>/dev/null || echo "No Android Appium recording pulled"

echo "Android Appium wrapper complete (RC=$RC)"
exit "$RC"
