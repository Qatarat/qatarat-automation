#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#   Qatarat — USB Device Test Runner  (Android & iOS)
#   Connect your phone via USB and run any test suite.
#   No emulator, no setup knowledge needed.
# ═══════════════════════════════════════════════════════════════════

set -e

# ── Colours ─────────────────────────────────────────────────────────
BOLD='\033[1m';    RESET='\033[0m'
GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m';   CYAN='\033[0;36m'
BLUE='\033[0;34m';  DIM='\033[2m'

log()     { echo -e "${GREEN}${BOLD}[✓]${RESET} $1"; }
warn()    { echo -e "${YELLOW}${BOLD}[!]${RESET} $1"; }
error()   { echo -e "${RED}${BOLD}[✗]${RESET} $1"; }
step()    { echo -e "\n${CYAN}${BOLD}▶  $1${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK_PATH="$SCRIPT_DIR/../Qatarat (Lambda-Stage).apk"

# ── PATH setup ──────────────────────────────────────────────────────
if [ -z "$JAVA_HOME" ]; then
  if   [ -d "/opt/homebrew/opt/openjdk@17" ]; then JAVA_HOME="/opt/homebrew/opt/openjdk@17"
  elif [ -d "/usr/local/opt/openjdk@17" ];    then JAVA_HOME="/usr/local/opt/openjdk@17"
  elif command -v java &>/dev/null;            then JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(which java)")")")"
  fi
fi
if [ -z "$ANDROID_HOME" ]; then
  if   [ -d "$HOME/Library/Android/sdk" ]; then ANDROID_HOME="$HOME/Library/Android/sdk"
  elif [ -d "$HOME/Android/sdk" ];          then ANDROID_HOME="$HOME/Android/sdk"
  fi
fi
export JAVA_HOME ANDROID_HOME
export PATH="${JAVA_HOME:+$JAVA_HOME/bin:}$HOME/.maestro/bin:${ANDROID_HOME:+$ANDROID_HOME/platform-tools:}/opt/homebrew/bin:/usr/local/bin:$PATH"

# ── Banner ──────────────────────────────────────────────────────────
clear
echo ""
echo -e "${CYAN}${BOLD}"
echo "  ██████╗  █████╗ ████████╗ █████╗ ██████╗  █████╗ ████████╗"
echo "  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝"
echo "  ██║  ██║███████║   ██║   ███████║██████╔╝███████║   ██║   "
echo "  ██║  ██║██╔══██║   ██║   ██╔══██║██╔══██╗██╔══██║   ██║   "
echo "  ██████╔╝██║  ██║   ██║   ██║  ██║██║  ██║██║  ██║   ██║   "
echo "  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   "
echo -e "${RESET}"
echo -e "  ${BOLD}Qatarat (قطرات) — Mobile Test Runner${RESET}"
echo -e "  ${DIM}Android & iOS USB Device Edition${RESET}"
echo ""
echo "  ─────────────────────────────────────────────────────────"
echo ""

# ── Platform selection ──────────────────────────────────────────────
echo -e "  ${BOLD}Which device are you testing on?${RESET}"
echo ""
echo -e "  ${BOLD}  1)${RESET} Android phone"
echo -e "  ${BOLD}  2)${RESET} iPhone (iOS)"
echo ""
read -p "  Enter choice [1 or 2]: " PLATFORM_CHOICE
case "$PLATFORM_CHOICE" in
  2) PLATFORM="ios"     ;;
  *) PLATFORM="android" ;;
esac
echo ""

# ── Prerequisites check ─────────────────────────────────────────────
step "Checking tools..."

MISSING=()
command -v java    &>/dev/null || MISSING+=("Java 17  →  run: cd testing && ./install.sh")
command -v maestro &>/dev/null || MISSING+=("Maestro  →  run: cd testing && ./install.sh")

if [ "$PLATFORM" = "android" ]; then
  command -v adb &>/dev/null || MISSING+=("ADB      →  run: cd testing && ./install.sh")
else
  # iOS needs Xcode CLI tools (for xcrun) — ship with Xcode, free
  if ! command -v xcrun &>/dev/null; then
    MISSING+=("Xcode CLI tools  →  run: xcode-select --install")
  fi
  # idb-companion — Maestro uses this to talk to iOS devices
  if ! command -v idb_companion &>/dev/null; then
    warn "idb-companion not found — installing via Homebrew (required for Maestro on iOS)..."
    if command -v brew &>/dev/null; then
      brew install facebook/fb/idb-companion 2>/dev/null || \
        warn "idb-companion install failed — try: brew install facebook/fb/idb-companion"
    else
      MISSING+=("idb-companion  →  brew install facebook/fb/idb-companion")
    fi
  fi
fi

if [ ${#MISSING[@]} -gt 0 ]; then
  error "Missing tools:"
  for m in "${MISSING[@]}"; do echo -e "    ${RED}•${RESET} $m"; done
  echo ""
  if [ "$PLATFORM" = "android" ]; then
    read -p "  Run install.sh now? (y/n): " DO_INSTALL
    if [[ "$DO_INSTALL" =~ ^[Yy]$ ]]; then
      "$SCRIPT_DIR/install.sh"
      source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null || true
    else
      exit 1
    fi
  else
    exit 1
  fi
fi
log "All tools found"

# ═══════════════════════════════════════════════════════════════════
#   ANDROID PATH
# ═══════════════════════════════════════════════════════════════════
if [ "$PLATFORM" = "android" ]; then

  # ── APK check ─────────────────────────────────────────────────────
  if [ ! -f "$APK_PATH" ]; then
    error "APK not found at: $APK_PATH"
    echo "  Put 'Qatarat (Lambda-Stage).apk' in the project root folder."
    exit 1
  fi
  APK_SIZE=$(du -sh "$APK_PATH" | cut -f1)
  log "APK found ($APK_SIZE)"

  # ── Android device detection ───────────────────────────────────────
  step "Looking for a connected Android device..."
  echo ""
  echo -e "  ${YELLOW}How to enable USB Debugging:${RESET}"
  echo -e "  ${DIM}1. Settings → About Phone → tap 'Build Number' 7 times${RESET}"
  echo -e "  ${DIM}2. Settings → Developer Options → enable 'USB Debugging'${RESET}"
  echo -e "  ${DIM}3. Connect phone via USB cable (data cable, not charge-only)${RESET}"
  echo -e "  ${DIM}4. Unlock phone and tap 'Allow' on the USB Debugging dialog${RESET}"
  echo ""

  printf "  Resetting ADB server..."
  adb kill-server 2>/dev/null; adb start-server 2>/dev/null
  echo -e " ${DIM}done${RESET}"
  echo ""

  MAX_WAIT=90; WAIT=0; DEVICE_ID=""; LAST_STATE=""

  while [ $WAIT -lt $MAX_WAIT ]; do
    RAW=$(adb devices 2>/dev/null | tail -n +2 | grep -v "^$" || true)
    DEVICE_LINE=$(echo "$RAW" | grep "device$" | head -1)
    if [ -n "$DEVICE_LINE" ]; then
      DEVICE_ID=$(echo "$DEVICE_LINE" | awk '{print $1}')
      break
    fi
    UNAUTH=$(echo "$RAW" | grep "unauthorized" | head -1)
    if [ -n "$UNAUTH" ]; then
      UNAUTH_ID=$(echo "$UNAUTH" | awk '{print $1}')
      if [ "$LAST_STATE" != "unauth:$UNAUTH_ID" ]; then
        echo ""
        echo -e "  ${YELLOW}${BOLD}[!]${RESET} Phone detected (${UNAUTH_ID}) but not authorized yet."
        echo -e "  ${BOLD}    → Unlock your phone and tap 'Allow' on the USB Debugging dialog.${RESET}"
        LAST_STATE="unauth:$UNAUTH_ID"
      fi
    else
      printf "\r  ${YELLOW}Waiting for device...${RESET} ${DIM}${WAIT}s / ${MAX_WAIT}s${RESET}   "
      LAST_STATE="none"
    fi
    sleep 2; WAIT=$((WAIT + 2))
  done
  echo ""

  if [ -z "$DEVICE_ID" ]; then
    error "No device found after ${MAX_WAIT}s."
    echo ""
    echo -e "  ${BOLD}Common fixes:${RESET}"
    echo -e "  ${CYAN}•${RESET} Swap the USB cable — charge-only cables have no data pins"
    echo -e "  ${CYAN}•${RESET} Try a different USB port"
    echo -e "  ${CYAN}•${RESET} Unlock phone and check for the 'Allow USB Debugging' popup"
    echo -e "  ${CYAN}•${RESET} Developer Options → Revoke USB debugging authorizations → reconnect"
    echo -e "  ${CYAN}•${RESET} Samsung only: also enable 'Install via USB' in Developer Options"
    echo -e "  ${CYAN}•${RESET} Run: ${CYAN}adb kill-server && adb start-server && adb devices${RESET}"
    exit 1
  fi

  DEVICE_MODEL=$(adb -s "$DEVICE_ID" shell getprop ro.product.model   2>/dev/null | tr -d '\r')
  DEVICE_VER=$(  adb -s "$DEVICE_ID" shell getprop ro.build.version.release 2>/dev/null | tr -d '\r')
  DEVICE_BRAND=$(adb -s "$DEVICE_ID" shell getprop ro.product.brand   2>/dev/null | tr -d '\r')
  log "Device connected!"
  echo ""
  echo -e "  ${BOLD}Device:${RESET}  $DEVICE_BRAND $DEVICE_MODEL"
  echo -e "  ${BOLD}Android:${RESET} $DEVICE_VER"
  echo -e "  ${BOLD}ID:${RESET}      $DEVICE_ID"
  echo ""

  step "Installing Qatarat app on device..."
  adb -s "$DEVICE_ID" install -r "$APK_PATH" 2>&1 | grep -E "Success|Failure|error" || true
  log "App installed"

# ═══════════════════════════════════════════════════════════════════
#   iOS PATH
# ═══════════════════════════════════════════════════════════════════
else

  # ── iOS device detection ───────────────────────────────────────────
  step "Looking for a connected iPhone..."
  echo ""
  echo -e "  ${YELLOW}How to connect your iPhone for testing:${RESET}"
  echo -e "  ${DIM}1. Connect iPhone via USB Lightning or USB-C cable${RESET}"
  echo -e "  ${DIM}2. Unlock your iPhone${RESET}"
  echo -e "  ${DIM}3. Tap 'Trust' on the 'Trust This Computer?' dialog${RESET}"
  echo -e "  ${DIM}4. Enter your iPhone passcode if prompted${RESET}"
  echo ""
  echo -e "  ${YELLOW}${BOLD}Important — App must be pre-installed:${RESET}"
  echo -e "  ${DIM}  iOS does not allow sideloading unsigned apps.${RESET}"
  echo -e "  ${DIM}  Install Qatarat on your iPhone via:${RESET}"
  echo -e "  ${DIM}    • Xcode (open Qatarat project → run on device), or${RESET}"
  echo -e "  ${DIM}    • TestFlight (if you have a TestFlight invite)${RESET}"
  echo ""

  MAX_WAIT=90; WAIT=0; DEVICE_ID=""; LAST_UDID_COUNT=0

  while [ $WAIT -lt $MAX_WAIT ]; do
    # xcrun xctrace list devices shows real devices (not simulators) with their UDID
    # Format: "iPhone 14 Pro (17.5) (XXXXXXXX-XXXX-...)"
    DEVICES_RAW=$(xcrun xctrace list devices 2>/dev/null | \
      grep -E "iPhone|iPad" | grep -v "Simulator" | grep -v "^==" || true)

    if [ -n "$DEVICES_RAW" ]; then
      # Extract UDID from last column — format: "Name (version) (UDID)"
      FIRST_LINE=$(echo "$DEVICES_RAW" | head -1)
      UDID=$(echo "$FIRST_LINE" | grep -oE '\([A-F0-9a-f-]{36,}\)' | tr -d '()' | head -1)
      DEVICE_NAME_IOS=$(echo "$FIRST_LINE" | sed 's/ ([^)]*) ([^)]*)//')

      if [ -n "$UDID" ]; then
        DEVICE_ID="$UDID"
        break
      else
        # Device visible but UDID empty = not yet trusted
        NEW_COUNT=$(echo "$DEVICES_RAW" | wc -l | tr -d ' ')
        if [ "$NEW_COUNT" != "$LAST_UDID_COUNT" ]; then
          echo ""
          echo -e "  ${YELLOW}${BOLD}[!]${RESET} iPhone detected but not yet trusted."
          echo -e "  ${BOLD}    → On your iPhone: tap 'Trust' on the 'Trust This Computer?' dialog.${RESET}"
          echo -e "  ${BOLD}    → Enter your passcode if asked.${RESET}"
          LAST_UDID_COUNT="$NEW_COUNT"
        fi
      fi
    else
      printf "\r  ${YELLOW}Waiting for iPhone...${RESET} ${DIM}${WAIT}s / ${MAX_WAIT}s${RESET}   "
    fi

    sleep 2; WAIT=$((WAIT + 2))
  done
  echo ""

  if [ -z "$DEVICE_ID" ]; then
    error "No iPhone found after ${MAX_WAIT}s."
    echo ""
    echo -e "  ${BOLD}Common fixes:${RESET}"
    echo -e "  ${CYAN}•${RESET} Unlock your iPhone before plugging in"
    echo -e "  ${CYAN}•${RESET} Look for 'Trust This Computer?' on the iPhone screen and tap Trust"
    echo -e "  ${CYAN}•${RESET} Try a different cable or USB port"
    echo -e "  ${CYAN}•${RESET} Settings → General → Transfer or Reset iPhone → Reset → Reset Location & Privacy (re-triggers trust)"
    echo -e "  ${CYAN}•${RESET} Open Finder → click your iPhone in sidebar → it will prompt trust"
    echo -e "  ${CYAN}•${RESET} Run: ${CYAN}xcrun xctrace list devices${RESET}  (should show your iPhone + UDID)"
    exit 1
  fi

  log "iPhone connected!"
  echo ""
  echo -e "  ${BOLD}Device:${RESET}  $DEVICE_NAME_IOS"
  echo -e "  ${BOLD}UDID:${RESET}    $DEVICE_ID"
  echo ""
  echo -e "  ${DIM}Skipping app install — iOS requires app to be pre-installed via${RESET}"
  echo -e "  ${DIM}Xcode or TestFlight. If not installed yet, do that first.${RESET}"
  echo ""

fi  # end platform branch

# ── Test menu ───────────────────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────────────────────"
if [ "$PLATFORM" = "ios" ]; then
  echo -e "  ${BOLD}  Testing on:${RESET} ${CYAN}iOS (iPhone)${RESET}  ${DIM}UDID: ${DEVICE_ID:0:18}...${RESET}"
else
  echo -e "  ${BOLD}  Testing on:${RESET} ${GREEN}Android${RESET}  ${DIM}ID: $DEVICE_ID${RESET}"
fi
echo -e "  ${BOLD}  What do you want to test?${RESET}"
echo "  ─────────────────────────────────────────────────────────"
echo ""
echo -e "  ${CYAN}${BOLD}  MAESTRO (quick UI flows)${RESET}"
echo -e "  ${BOLD}  1)${RESET} Smoke Suite        ${DIM}~5 min  — login, cart, checkout${RESET}"
echo -e "  ${BOLD}  2)${RESET} Full Regression     ${DIM}~20 min — all 16 flows${RESET}"
echo ""
echo -e "  ${CYAN}${BOLD}  SINGLE FLOWS${RESET}"
echo -e "  ${BOLD}  3)${RESET} Login / OTP"
echo -e "  ${BOLD}  4)${RESET} Cart + Add Items"
echo -e "  ${BOLD}  5)${RESET} Checkout + Payment"
echo -e "  ${BOLD}  6)${RESET} Gift Card"
echo -e "  ${BOLD}  7)${RESET} My Orders + Rating"
echo -e "  ${BOLD}  8)${RESET} Subscription"
echo -e "  ${BOLD}  9)${RESET} Multi-language"
echo ""
echo -e "  ${CYAN}${BOLD}  APPIUM (deep tests — needs Appium server running)${RESET}"
if [ "$PLATFORM" = "ios" ]; then
  echo -e "  ${DIM}  Requires IPA signed for your device + XCODE_ORG_ID env var${RESET}"
fi
echo -e "  ${BOLD}  a)${RESET} Payment Tests      ${DIM}card, Tabby, bank transfer${RESET}"
echo -e "  ${BOLD}  b)${RESET} Gift Card Tests"
echo -e "  ${BOLD}  c)${RESET} Subscription Tests"
echo -e "  ${BOLD}  d)${RESET} All Appium Tests    ${DIM}~45 min${RESET}"
echo ""
echo "  ─────────────────────────────────────────────────────────"
echo ""
read -p "  Enter choice [1-9, a-d]: " CHOICE
echo ""

# ── Run helpers ─────────────────────────────────────────────────────
mkdir -p "$SCRIPT_DIR/maestro/reports" "$SCRIPT_DIR/appium/reports/screenshots"
REPORT_TS=$(date +%Y%m%d-%H%M%S)

run_maestro() {
  local FLOW="$1"
  local LABEL="$2"
  step "Running: $LABEL  [${PLATFORM}]"

  if [ "$PLATFORM" = "ios" ]; then
    MAESTRO_DRIVER=ios maestro \
      --device "$DEVICE_ID" \
      test "$FLOW" \
      --format junit \
      --output "$SCRIPT_DIR/maestro/reports/ios-${REPORT_TS}.xml"
  else
    maestro \
      --device "$DEVICE_ID" \
      test "$FLOW" \
      --format junit \
      --output "$SCRIPT_DIR/maestro/reports/android-${REPORT_TS}.xml"
  fi
}

run_appium() {
  local MARKER="$1"
  local LABEL="$2"
  step "Running: $LABEL  [${PLATFORM}]"

  if [ "$PLATFORM" = "ios" ] && [ -z "$XCODE_ORG_ID" ]; then
    warn "XCODE_ORG_ID not set — Appium iOS needs your Apple Developer Team ID."
    echo ""
    echo -e "  Set it before running:  ${CYAN}export XCODE_ORG_ID=XXXXXXXXXX${RESET}"
    echo -e "  Find yours at:  ${DIM}developer.apple.com → Account → Membership → Team ID${RESET}"
    echo ""
    read -p "  Enter Team ID now (or press Enter to skip): " TID
    if [ -n "$TID" ]; then
      export XCODE_ORG_ID="$TID"
    else
      warn "Skipping Appium test — re-run with XCODE_ORG_ID set."
      return
    fi
  fi

  if ! curl -s http://127.0.0.1:4723/status &>/dev/null; then
    warn "Starting Appium server..."
    appium --port 4723 --log /tmp/appium-device.log &
    APPIUM_BG_PID=$!
    local S=0
    until curl -s http://127.0.0.1:4723/status &>/dev/null || [ $S -ge 15 ]; do
      sleep 1; S=$((S+1))
    done
    [ $S -ge 15 ] && { error "Appium server did not start. Check /tmp/appium-device.log"; exit 1; }
    log "Appium started (PID $APPIUM_BG_PID)"
  fi

  PLATFORM="$PLATFORM" \
  DEVICE_MODE=device \
  IOS_UDID="$DEVICE_ID" \
  ANDROID_UDID="$DEVICE_ID" \
  XCODE_ORG_ID="${XCODE_ORG_ID:-}" \
    "$SCRIPT_DIR/appium/.venv/bin/python" -m pytest \
      "$SCRIPT_DIR/appium/tests/" \
      ${MARKER:+-m "$MARKER"} -v \
      --html="$SCRIPT_DIR/appium/reports/${PLATFORM}-${REPORT_TS}.html" \
      --self-contained-html \
      --tb=short
}

case "$CHOICE" in
  1) run_maestro "$SCRIPT_DIR/maestro/flows/suites/smoke.yaml"                   "Smoke Suite" ;;
  2) run_maestro "$SCRIPT_DIR/maestro/flows/suites/regression.yaml"              "Full Regression" ;;
  3) run_maestro "$SCRIPT_DIR/maestro/flows/02_login_otp.yaml"                   "Login / OTP" ;;
  4) run_maestro "$SCRIPT_DIR/maestro/flows/05_cart_add_items.yaml"              "Cart + Add Items" ;;
  5) run_maestro "$SCRIPT_DIR/maestro/flows/06_checkout_payment_select.yaml"     "Checkout" ;;
  6) run_maestro "$SCRIPT_DIR/maestro/flows/07_gift_card.yaml"                   "Gift Card" ;;
  7) run_maestro "$SCRIPT_DIR/maestro/flows/08_my_orders.yaml"                   "My Orders + Rating" ;;
  8) run_maestro "$SCRIPT_DIR/maestro/flows/09_subscription.yaml"                "Subscription" ;;
  9) run_maestro "$SCRIPT_DIR/maestro/flows/10_multilanguage.yaml"               "Multi-language" ;;
  a|A) run_appium "payment"      "Payment Tests (card, Tabby, bank)" ;;
  b|B) run_appium "gift"         "Gift Card Tests" ;;
  c|C) run_appium "subscription" "Subscription Tests" ;;
  d|D) run_appium ""             "All Appium Tests" ;;
  *)
    warn "Invalid choice: $CHOICE"
    exit 1
    ;;
esac

# ── Summary ─────────────────────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────────────────────"
log "Run complete!"
echo ""
echo -e "  ${BOLD}Reports saved to:${RESET}"
echo -e "  ${DIM}  Maestro: testing/maestro/reports/${RESET}"
echo -e "  ${DIM}  Appium:  testing/appium/reports/${RESET}"
echo ""
echo -e "  ${DIM}Run again:  cd testing && bash run_on_device.sh${RESET}"
echo ""
