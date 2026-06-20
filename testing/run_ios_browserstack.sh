#!/usr/bin/env bash
# Run iOS Appium tests via BrowserStack — no Xcode or local simulator needed.
#
# SETUP (one time):
#   1. Sign up at https://www.browserstack.com/app-automate
#   2. Upload the IPA:
#        curl -u "USER:KEY" -X POST \
#          https://api-cloud.browserstack.com/app-automate/upload \
#          -F "file=@qatarat-stage-ios.ipa"
#      Copy the "app_url" from the response (bs://...)
#   3. Export credentials:
#        export BS_USERNAME="your_bs_username"
#        export BS_ACCESS_KEY="your_bs_access_key"
#        export BS_APP_URL="bs://..."
#
# USAGE:
#   bash testing/run_ios_browserstack.sh [marker]
#   Examples:
#     bash testing/run_ios_browserstack.sh account
#     bash testing/run_ios_browserstack.sh          # all tests

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPIUM_DIR="$SCRIPT_DIR/appium"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKER="${1:-}"

if [ -z "${BS_USERNAME:-}" ] || [ -z "${BS_ACCESS_KEY:-}" ]; then
    echo "ERROR: BS_USERNAME and BS_ACCESS_KEY must be set."
    echo ""
    echo "  export BS_USERNAME='your_username'"
    echo "  export BS_ACCESS_KEY='your_access_key'"
    echo "  export BS_APP_URL='bs://...'  (from upload response)"
    exit 1
fi

if [ -z "${BS_APP_URL:-}" ]; then
    # Pre-flight: detect simulator build before wasting upload time
    IPA="$ROOT/qatarat-stage-ios.ipa"
    if [ -f "$IPA" ]; then
        ARCH=$(python3 -c "
import zipfile, struct, os, sys
try:
    with zipfile.ZipFile('$IPA') as z:
        runner = [n for n in z.namelist() if n.endswith('Runner.app/Runner') and '__MACOSX' not in n]
        if runner:
            data = z.read(runner[0])[:8]
            if data[:4] == b'\\xca\\xfe\\xba\\xbe':
                print('fat')
            elif data[:4] in (b'\\xcf\\xfa\\xed\\xfe', b'\\xce\\xfa\\xed\\xfe'):
                cpu = struct.unpack('<I', data[4:8])[0]
                print('arm64' if cpu == 0x0100000c else 'x86_64' if cpu == 0x1000007 else 'unknown')
            elif data[:4] in (b'\\xfe\\xed\\xfa\\xcf', b'\\xfe\\xed\\xfa\\xce'):
                cpu = struct.unpack('>I', data[4:8])[0]
                print('arm64' if cpu == 0x0100000c else 'x86_64' if cpu == 0x1000007 else 'unknown')
            else:
                print('unknown')
        else:
            print('unknown')
except Exception as e:
    print('unknown')
" 2>/dev/null)
        if [ "$ARCH" = "x86_64" ]; then
            echo ""
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║  CANNOT RUN: IPA is an x86_64 SIMULATOR build               ║"
            echo "║  BrowserStack App Automate requires a DEVICE build (arm64)  ║"
            echo "╠══════════════════════════════════════════════════════════════╣"
            echo "║  HOW TO GET A DEVICE BUILD:                                 ║"
            echo "║  1. On Mac with Xcode + Apple Developer account:            ║"
            echo "║     flutter build ios --release                             ║"
            echo "║     (produces build/ios/iphoneos/Runner.app)                ║"
            echo "║  2. Archive and export as IPA with App Store/Ad Hoc profile ║"
            echo "║  3. Re-run: bash testing/run_ios_browserstack.sh            ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            echo ""
            exit 1
        fi
    fi

    echo "Uploading IPA to BrowserStack App Automate..."
    UPLOAD_RESP=$(curl -s -u "$BS_USERNAME:$BS_ACCESS_KEY" \
      -X POST "https://api-cloud.browserstack.com/app-automate/upload" \
      -F "file=@$IPA")
    BS_APP_URL=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('app_url',''))" 2>/dev/null || echo "")
    if [ -z "$BS_APP_URL" ]; then
        echo "ERROR: IPA upload failed. Response: $UPLOAD_RESP"
        exit 1
    fi
    export BS_APP_URL
    echo "IPA uploaded: $BS_APP_URL"
fi

export PLATFORM=ios
export DEVICE_MODE=browserstack

cd "$APPIUM_DIR"
mkdir -p reports/screenshots allure-results

PYTEST_ARGS=(
  tests/
  -v
  --timeout=300
  --html=reports/report-ios-browserstack.html
  --self-contained-html
  --junit-xml=reports/results-ios-browserstack.xml
  --alluredir=allure-results
  --tb=short
  -o "junit_family=xunit2"
)

if [ -n "$MARKER" ]; then
    echo "Running BrowserStack iOS tests — marker: $MARKER"
    python3 -m pytest "${PYTEST_ARGS[@]}" -m "$MARKER"
else
    echo "Running full BrowserStack iOS test suite..."
    python3 -m pytest "${PYTEST_ARGS[@]}"
fi

RC=$?
echo ""
echo "BrowserStack run complete (exit $RC)."
echo "  HTML:   $APPIUM_DIR/reports/report-ios-browserstack.html"
echo "  JUnit:  $APPIUM_DIR/reports/results-ios-browserstack.xml"
exit $RC
