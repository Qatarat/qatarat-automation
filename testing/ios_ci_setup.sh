#!/usr/bin/env bash
# Shared iOS Simulator setup for GitHub Actions (and local CI).
# Boots a simulator, extracts/installs Runner.app, exports env vars.
#
# Outputs (GITHUB_ENV when set):
#   SIM_ID, SIM_NAME, APP_PATH, IOS_APP_PATH, IOS_SIM_COMPATIBLE, IOS_APP_ARCH
#
# Usage:
#   bash testing/ios_ci_setup.sh [path/to/qatarat-stage-ios.ipa]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IPA_FILE="${1:-$ROOT/qatarat-stage-ios.ipa}"
IPA_EXTRACTED="$ROOT/ipa_extracted"

export_env() {
  export "$1=$2"
  if [ -n "${GITHUB_ENV:-}" ]; then
    echo "$1=$2" >> "$GITHUB_ENV"
  fi
}

install_rosetta() {
  if ! pgrep -q oahd 2>/dev/null; then
    echo "Installing Rosetta (required for x86_64 simulator builds on Apple Silicon)..."
    sudo softwareupdate --install-rosetta --agree-to-license 2>/dev/null || true
  else
    echo "Rosetta already installed"
  fi
}

extract_app() {
  if [ -d "$IPA_EXTRACTED/Payload/Runner.app" ]; then
    APP_PATH="$IPA_EXTRACTED/Payload/Runner.app"
    echo "Using pre-extracted Runner.app"
  elif [ -f "$IPA_FILE" ]; then
    echo "Extracting IPA from $IPA_FILE..."
    rm -rf "$ROOT/ipa_extracted"
    unzip -q "$IPA_FILE" -d "$ROOT/ipa_extracted/"
    APP_PATH="$ROOT/ipa_extracted/Payload/Runner.app"
  else
    echo "::error::No IPA found at $IPA_FILE"
    exit 1
  fi
  if [ ! -d "$APP_PATH" ]; then
    echo "::error::Payload/Runner.app not found after extract"
    exit 1
  fi
  export_env APP_PATH "$APP_PATH"
  export_env IOS_APP_PATH "$APP_PATH"
}

detect_arch() {
  local binary="$APP_PATH/Runner"
  if [ ! -f "$binary" ]; then
    echo "::error::Runner binary not found at $binary"
    exit 1
  fi
  ARCH_INFO=$(lipo -info "$binary" 2>/dev/null || file "$binary" 2>/dev/null || echo "unknown")
  echo "Binary architecture: $ARCH_INFO"
  export_env IOS_APP_ARCH "$ARCH_INFO"

  IS_SIM=false
  WANT_ROSETTA=false
  HAS_X86=false
  HAS_ARM64=false
  echo "$ARCH_INFO" | grep -qi "x86_64" && HAS_X86=true
  echo "$ARCH_INFO" | grep -qi "arm64"  && HAS_ARM64=true

  if [ "$HAS_X86" = "true" ]; then
    IS_SIM=true
    # Rosetta only needed when x86_64-only — universal (arm64+x86_64) runs natively
    if [ "$HAS_ARM64" = "false" ]; then
      WANT_ROSETTA=true
      install_rosetta
    fi
  elif [ "$HAS_ARM64" = "true" ]; then
    # arm64 could be device or simulator — check LC_BUILD_VERSION platform 7 (iPhoneSimulator)
    if otool -l "$binary" 2>/dev/null | grep -A 4 "LC_BUILD_VERSION" | grep -q "platform 7"; then
      IS_SIM=true
    fi
  fi

  if [ "$IS_SIM" != "true" ]; then
    echo "::error::Runner.app is a DEVICE build — need: flutter build ios --simulator --debug"
    export_env IOS_SIM_COMPATIBLE "false"
    exit 1
  fi
  export_env IOS_SIM_COMPATIBLE "true"
  export_env IOS_WANT_ROSETTA "$WANT_ROSETTA"
}

pick_simulator() {
  local want_rosetta="${1:-false}"
  local devices sim_id sim_name line

  devices=$(xcrun simctl list devices available)
  echo "=== Available iPhone simulators ==="
  echo "$devices" | grep -i iphone | head -20 || true

  sim_id=""
  sim_name=""

  if [ "$want_rosetta" = "true" ]; then
    while IFS= read -r line; do
      if echo "$line" | grep -qi "iphone" && echo "$line" | grep -qi "rosetta"; then
        sim_id=$(echo "$line" | grep -oE "[A-F0-9-]{36}" | head -1)
        sim_name=$(echo "$line" | sed 's/(.*//' | xargs)
        break
      fi
    done <<< "$devices"
    if [ -n "$sim_id" ]; then
      echo "Selected Rosetta simulator: $sim_name ($sim_id)"
    fi
  fi

  if [ -z "$sim_id" ]; then
    for prefer in "iPhone 15 Pro" "iPhone 16 Pro" "iPhone 15" "iPhone 16" "iPhone 17 Pro" "iPhone"; do
      line=$(echo "$devices" | grep "$prefer" | grep -v "Max\|Plus" | head -1 || true)
      if [ -n "$line" ]; then
        sim_id=$(echo "$line" | grep -oE "[A-F0-9-]{36}" | head -1)
        sim_name=$(echo "$line" | sed 's/(.*//' | xargs)
        break
      fi
    done
  fi

  if [ -z "$sim_id" ]; then
    echo "::error::No iPhone simulator found on this runner"
    exit 1
  fi

  export_env SIM_ID "$sim_id"
  export_env SIM_NAME "$sim_name"
  export_env IOS_SIM_NAME "$sim_name"

  # Detect the actual iOS version for this simulator so Appium gets an exact match.
  # Parse the section header above the device line: "-- iOS 17.5 --"
  local ios_ver
  ios_ver=$(xcrun simctl list devices available | awk -v id="$sim_id" '
    /^-- iOS / { ver = $3 }
    index($0, id) { if (ver != "") print ver; exit }
  ')
  if [ -n "${ios_ver:-}" ]; then
    echo "Detected iOS version: $ios_ver"
    export_env IOS_VERSION "$ios_ver"
  fi
}

boot_simulator() {
  echo "Booting simulator $SIM_NAME ($SIM_ID)..."
  xcrun simctl boot "$SIM_ID" 2>/dev/null || true
  xcrun simctl bootstatus "$SIM_ID" -b
  open -a Simulator 2>/dev/null || true
  sleep 2
}

install_app() {
  echo "Installing $APP_PATH on $SIM_ID..."
  if ! xcrun simctl install "$SIM_ID" "$APP_PATH"; then
    if [ "${IOS_WANT_ROSETTA:-false}" = "true" ]; then
      echo "::error::x86_64 app install failed. Ensure Rosetta simulator runtime is available."
      echo "::error::On Apple Silicon: xcodebuild -downloadPlatform iOS -architectureVariant universal"
    fi
    exit 1
  fi
  echo "App installed successfully"
  xcrun simctl get_app_container "$SIM_ID" com.qatarat.app 2>/dev/null && echo "App verified" || true
}

# ── Main ──────────────────────────────────────────────────────────────────────
cd "$ROOT"
extract_app
detect_arch
pick_simulator "${IOS_WANT_ROSETTA:-false}"
boot_simulator
install_app
echo "✅ iOS CI setup complete — $SIM_NAME ($SIM_ID)"
