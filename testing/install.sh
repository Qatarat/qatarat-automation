#!/usr/bin/env bash
# Qatarat App — Full Test Environment Installer
# Supports: macOS (Homebrew) and Linux/WSL (apt-get)
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
fail() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "================================================"
echo "  Qatarat Test Suite — Environment Setup"
echo "================================================"
echo ""

# ── Detect OS ───────────────────────────────────────
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS="mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  OS="linux"
  # Detect WSL
  if grep -qi microsoft /proc/version 2>/dev/null; then
    OS="wsl"
  fi
fi
log "Detected OS: $OS"

# Determine shell config file
SHELL_RC="$HOME/.bashrc"
if [[ "$OS" == "mac" ]]; then
  SHELL_RC="$HOME/.zshrc"
fi

add_to_shell_rc() {
  local marker="$1"
  local block="$2"
  if ! grep -q "$marker" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "$block" >> "$SHELL_RC"
  fi
}

# ── Java 17 ─────────────────────────────────────────
if [[ "$OS" == "mac" ]]; then
  if ! command -v brew &>/dev/null; then
    fail "Homebrew not found. Install from https://brew.sh first."
  fi
  log "Homebrew found: $(brew --version | head -1)"

  JAVA_OK=false
  if [ -x "/opt/homebrew/opt/openjdk@17/bin/java" ] || \
     [ -x "/usr/local/opt/openjdk@17/bin/java" ]; then
    JAVA_OK=true
  fi

  if [ "$JAVA_OK" = false ]; then
    warn "Java 17 not found — installing via Homebrew..."
    brew install openjdk@17
  fi

  # Support both Apple Silicon and Intel paths
  if [ -d "/opt/homebrew/opt/openjdk@17" ]; then
    export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
  else
    export JAVA_HOME="/usr/local/opt/openjdk@17"
  fi
  export PATH="$JAVA_HOME/bin:$PATH"

  add_to_shell_rc "openjdk@17" \
"# Java 17 (added by Qatarat test installer)
export JAVA_HOME=\"$JAVA_HOME\"
export PATH=\"\$JAVA_HOME/bin:\$PATH\""

else
  # Linux / WSL
  if ! java -version &>/dev/null 2>&1 || ! java -version 2>&1 | grep -q "17"; then
    warn "Java 17 not found — installing via apt..."
    sudo apt-get update -qq
    sudo apt-get install -y openjdk-17-jdk
  fi
  export JAVA_HOME="$(dirname $(dirname $(readlink -f $(which java))))"
  export PATH="$JAVA_HOME/bin:$PATH"

  add_to_shell_rc "JAVA_HOME" \
"# Java 17 (added by Qatarat test installer)
export JAVA_HOME=\"$(dirname $(dirname $(readlink -f $(which java))))\"
export PATH=\"\$JAVA_HOME/bin:\$PATH\""
fi

log "Java OK: $(java -version 2>&1 | head -1)"

# ── Android Platform Tools (ADB) ────────────────────
if [[ "$OS" == "mac" ]]; then
  ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"

  if ! command -v adb &>/dev/null && [ ! -f "$ANDROID_HOME/platform-tools/adb" ]; then
    warn "ADB not found — installing Android command-line tools..."
    brew install --cask android-commandlinetools 2>/dev/null || true
    mkdir -p "$ANDROID_HOME"
    yes | JAVA_HOME="$JAVA_HOME" sdkmanager \
      --sdk_root="$ANDROID_HOME" \
      "platform-tools" "platforms;android-34" "build-tools;34.0.0" \
      2>&1 | grep -v "^[[:space:]]*$" | tail -5 || true
  fi

else
  # Linux / WSL — download platform-tools directly (avoids full Android Studio)
  ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/sdk}"

  if ! command -v adb &>/dev/null && [ ! -f "$ANDROID_HOME/platform-tools/adb" ]; then
    warn "ADB not found — downloading Android platform-tools..."
    mkdir -p "$ANDROID_HOME"
    PT_ZIP="$ANDROID_HOME/platform-tools.zip"
    curl -L -o "$PT_ZIP" \
      "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
    unzip -q "$PT_ZIP" -d "$ANDROID_HOME"
    rm "$PT_ZIP"
    log "platform-tools extracted to $ANDROID_HOME/platform-tools"
  fi
fi

export ANDROID_HOME="$ANDROID_HOME"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

add_to_shell_rc "ANDROID_HOME" \
"# Android SDK (added by Qatarat test installer)
export ANDROID_HOME=\"$ANDROID_HOME\"
export PATH=\"\$ANDROID_HOME/platform-tools:\$PATH\""

command -v adb &>/dev/null \
  && log "ADB OK: $(adb version | head -1)" \
  || warn "ADB not in PATH yet — will work after: source $SHELL_RC"

# ── Node.js ──────────────────────────────────────────
if ! command -v node &>/dev/null; then
  if [[ "$OS" == "mac" ]]; then
    fail "Node.js not found. Install from https://nodejs.org first."
  else
    warn "Node.js not found — installing via apt..."
    sudo apt-get update -qq
    sudo apt-get install -y nodejs npm
  fi
fi
log "Node OK: $(node --version)"

# ── Maestro ──────────────────────────────────────────
export PATH="$HOME/.maestro/bin:$PATH"

if ! command -v maestro &>/dev/null; then
  warn "Maestro not found — installing..."
  curl -Ls "https://get.maestro.mobile.dev" | bash
  export PATH="$HOME/.maestro/bin:$PATH"
  add_to_shell_rc ".maestro/bin" \
"# Maestro (added by Qatarat test installer)
export PATH=\"\$HOME/.maestro/bin:\$PATH\""
fi

command -v maestro &>/dev/null \
  && log "Maestro OK: $(maestro --version)" \
  || warn "Maestro not in PATH yet — will work after: source $SHELL_RC"

# ── Appium ───────────────────────────────────────────
if ! command -v appium &>/dev/null; then
  warn "Appium not found — installing globally..."
  npm install -g appium
fi
log "Appium OK: $(appium --version)"

# ── Appium Drivers ────────────────────────────────────
warn "Installing/verifying Appium drivers..."
appium driver install uiautomator2 2>/dev/null || true
appium driver install xcuitest 2>/dev/null || true
appium driver install --source=npm appium-flutter-driver 2>/dev/null || true
appium plugin install execute-driver 2>/dev/null || true
log "Appium drivers OK"

# ── Python venv + deps ────────────────────────────────
if [[ "$OS" != "mac" ]] && ! command -v python3 &>/dev/null; then
  warn "Python3 not found — installing..."
  sudo apt-get install -y python3 python3-venv python3-pip
fi

VENV_DIR="$SCRIPT_DIR/appium/.venv"
if [ ! -d "$VENV_DIR" ]; then
  warn "Creating Python virtualenv at appium/.venv ..."
  python3 -m venv "$VENV_DIR"
fi

warn "Installing Python dependencies into venv..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/appium/requirements.txt" --quiet
log "Python deps OK (venv: appium/.venv)"

# Patch run_appium.sh to use venv python
sed -i${OS=="mac" && echo " ''"} \
  "s|python3 -m pytest|\"$VENV_DIR/bin/python\" -m pytest|g" \
  "$SCRIPT_DIR/run_appium.sh" 2>/dev/null || true

# ── iOS tools (macOS only — optional, for iPhone USB testing) ─────────
if [[ "$OS" == "mac" ]]; then
  echo ""
  read -p "$(echo -e "${YELLOW}[?]${NC} Install iOS testing tools for iPhone USB testing? [y/N]: ")" DO_IOS
  if [[ "$DO_IOS" =~ ^[Yy]$ ]]; then
    if ! command -v xcrun &>/dev/null; then
      warn "Xcode CLI tools not found — run: xcode-select --install"
    else
      log "Xcode CLI tools: $(xcode-select -p)"
    fi
    if ! command -v idb_companion &>/dev/null; then
      warn "Installing idb-companion (Maestro needs this for iOS devices)..."
      brew tap facebook/fb 2>/dev/null || true
      brew install facebook/fb/idb-companion \
        && log "idb-companion installed" \
        || warn "idb-companion install failed — try: brew install facebook/fb/idb-companion"
    else
      log "idb-companion: OK"
    fi
    echo ""
    warn "iOS requires the app pre-installed via Xcode or TestFlight — iOS blocks unsigned IPA sideloading."
  fi
fi

# ── Summary ───────────────────────────────────────────
echo ""
echo "================================================"
echo "  Setup Complete — Status"
echo "================================================"
echo ""
java -version 2>&1 | head -1            && log "Java 17"        || warn "Java: check failed"
command -v adb &>/dev/null              && log "ADB: $(adb version | head -1 | cut -c1-50)" \
                                        || warn "ADB: run 'source $SHELL_RC' then check again"
command -v maestro &>/dev/null          && log "Maestro: $(maestro --version)" \
                                        || warn "Maestro: run 'source $SHELL_RC' then check again"
command -v appium &>/dev/null           && log "Appium: $(appium --version)"   || warn "Appium: not found"
[ -f "$VENV_DIR/bin/python" ]           && log "Python venv: $VENV_DIR"        || warn "Python venv: not found"
echo ""
warn "Reload your shell:  source $SHELL_RC"
echo ""
echo "  Next steps:"
echo "  1. source $SHELL_RC"
echo "  2. Connect Android device OR start an Android emulator"
echo "  3. adb devices                     # confirm device is listed"
echo "  4. cd testing && bash run_maestro.sh   # Phase 1 smoke"
echo "  5. cd testing && bash run_appium.sh    # Phase 2 deep tests"
echo ""
