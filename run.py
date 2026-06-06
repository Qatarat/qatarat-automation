#!/usr/bin/env python3
"""
Qatarat — one-command launcher + test runner
Works on macOS, Linux, and Windows.

Usage:
  python run.py               # start app only
  python run.py smoke         # start app + Maestro smoke tests  (8 flows, ~8 min)
  python run.py regression    # start app + all 50 Maestro flows (~45 min)
  python run.py appium        # start app + all 191 Appium tests (~75 min)
  python run.py all           # start app + Maestro regression + Appium
"""

import os
import sys
import time
import shutil
import platform
import subprocess

# ── Config ────────────────────────────────────────────────────────────────────
AVD      = "Pixel_7_API_34"
PACKAGE  = "com.qatarat.app"
ACTIVITY = ".MainActivity"
APK_NAME = "Qatarat (Lambda-Stage).apk"
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM   = platform.system()   # 'Darwin' | 'Linux' | 'Windows'
ROOT     = os.path.dirname(os.path.abspath(__file__))
TESTING  = os.path.join(ROOT, "testing")
APPIUM   = os.path.join(TESTING, "appium")

# ── OS helpers ────────────────────────────────────────────────────────────────

def _exe(name):
    return name + (".exe" if SYSTEM == "Windows" else "")

def _sdk_defaults():
    home = os.path.expanduser("~")
    if SYSTEM == "Darwin":
        return [os.path.join(home, "Library", "Android", "sdk")]
    if SYSTEM == "Linux":
        return [os.path.join(home, "Android", "Sdk"), "/opt/android-sdk"]
    # Windows
    local = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
    return [os.path.join(local, "Android", "Sdk")]

def find_sdk():
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        p = os.environ.get(var)
        if p and os.path.isdir(p):
            return p
    for p in _sdk_defaults():
        if os.path.isdir(p):
            return p
    return None

def find_tool(sdk, *parts):
    binary = _exe(parts[-1])
    full   = os.path.join(sdk, *parts[:-1], binary)
    if os.path.isfile(full):
        return full
    return shutil.which(binary)

def run(cmd, **kw):
    return subprocess.run(cmd, **kw)

def out(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""

# ── Emulator helpers ──────────────────────────────────────────────────────────

def emulator_running(adb):
    return "emulator" in out([adb, "devices"])

def wait_boot(adb, timeout=180):
    print("  Waiting for boot (up to 3 min)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if out([adb, "shell", "getprop", "sys.boot_completed"]) == "1":
            return True
        time.sleep(5)
    return False

# ── Python / venv helpers ─────────────────────────────────────────────────────

def _venv_python():
    if SYSTEM == "Windows":
        return os.path.join(APPIUM, ".venv", "Scripts", "python.exe")
    return os.path.join(APPIUM, ".venv", "bin", "python")

def python_cmd():
    venv = _venv_python()
    if os.path.isfile(venv):
        return venv
    for p in ("python3", "python"):
        if shutil.which(p):
            return p
    return None

def ensure_venv():
    venv_py = _venv_python()
    if os.path.isfile(venv_py):
        return venv_py
    py = shutil.which("python3") or shutil.which("python")
    if not py:
        _die("Python not found. Install from https://python.org")
    req = os.path.join(APPIUM, "requirements.txt")
    venv_dir = os.path.join(APPIUM, ".venv")
    print("  Creating Python venv...")
    run([py, "-m", "venv", venv_dir], check=True)
    pip = os.path.join(venv_dir, "Scripts" if SYSTEM == "Windows" else "bin", "pip")
    print("  Installing Python dependencies...")
    run([pip, "install", "-r", req, "-q"], check=True)
    return venv_py

def ensure_appium():
    if shutil.which("appium"):
        return
    npm = shutil.which("npm")
    if not npm:
        _die("npm not found. Install Node.js from https://nodejs.org")
    print("  Installing Appium...")
    run([npm, "install", "-g", "appium"], check=True)
    run(["appium", "driver", "install", "uiautomator2"], check=True)
    run(["appium", "driver", "install", "--source=npm", "appium-flutter-driver"], check=True)

def ensure_maestro():
    if shutil.which("maestro"):
        return
    if SYSTEM == "Windows":
        _die("Maestro auto-install not supported on Windows.\n"
             "Install manually: https://maestro.mobile.dev/getting-started/installing-maestro")
    print("  Installing Maestro...")
    run('curl -Ls "https://get.maestro.mobile.dev" | bash', shell=True, check=True)
    if not shutil.which("maestro"):
        _die("Maestro installed but not on PATH. Open a new terminal and re-run.")

def _die(msg):
    print(f"\nERROR: {msg}")
    sys.exit(1)

# ── Appium server ─────────────────────────────────────────────────────────────

def start_appium():
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:4723/status", timeout=2)
        print("  Appium already running on :4723")
        return None
    except Exception:
        pass
    print("  Starting Appium server...")
    log = open(os.path.join(APPIUM, "appium.log"), "a")
    p = subprocess.Popen(
        ["appium", "--port", "4723"],
        stdout=log, stderr=log,
        cwd=APPIUM
    )
    time.sleep(4)
    return p

# ── Main steps ────────────────────────────────────────────────────────────────

def step_launch_app(adb, emulator_bin, apk):
    # Start emulator if needed
    if emulator_running(adb):
        print("[1/3] Emulator already running — skipping start.")
    else:
        print(f"[1/3] Starting emulator ({AVD})...")
        kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen([emulator_bin, "-avd", AVD, "-no-snapshot-load",
                          "-no-audio", "-no-boot-anim"], **kwargs)
        if not wait_boot(adb):
            _die("Emulator did not boot within 3 minutes.")
        time.sleep(3)
        print("  Boot complete.")

    # Install
    print("[2/3] Installing APK...")
    r = run([adb, "install", "-r", apk])
    if r.returncode != 0:
        _die("APK installation failed.")

    # Launch
    print("[3/3] Launching Qatarat...")
    run([adb, "shell", "am", "start", "-n", f"{PACKAGE}/{ACTIVITY}"])
    print("  App is running.\n")

def step_maestro(mode):
    ensure_maestro()
    if mode == "smoke":
        suite = os.path.join(TESTING, "maestro", "flows", "suites", "smoke.yaml")
        label = "Maestro Smoke (8 flows)"
    else:
        suite = os.path.join(TESTING, "maestro", "flows", "suites", "regression.yaml")
        label = "Maestro Regression (50 flows)"

    if not os.path.isfile(suite):
        _die(f"Suite file not found: {suite}")

    print(f"── {label} ──")
    r = run(["maestro", "test", suite], cwd=TESTING)
    print(f"  Maestro exit: {r.returncode}\n")
    return r.returncode

def step_appium():
    ensure_appium()
    venv_py = ensure_venv()
    appium_proc = start_appium()

    os.makedirs(os.path.join(APPIUM, "reports"), exist_ok=True)
    os.makedirs(os.path.join(APPIUM, "allure-results"), exist_ok=True)

    print("── Appium Tests (191 checks) ──")
    r = run(
        [venv_py, "-m", "pytest", "tests/", "-v",
         "--html=reports/report.html", "--self-contained-html",
         "--junit-xml=reports/results.xml",
         "--alluredir=allure-results",
         "--tb=short"],
        cwd=APPIUM
    )
    print(f"  Appium exit: {r.returncode}")
    print(f"  Report: {os.path.join(APPIUM, 'reports', 'report.html')}\n")

    if appium_proc:
        appium_proc.terminate()

    return r.returncode

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "app"
    valid = ("app", "smoke", "regression", "appium", "all")
    if mode not in valid:
        print(__doc__)
        _die(f"Unknown mode '{mode}'. Valid: {valid}")

    print("=" * 48)
    print(f"  Qatarat Launcher  |  OS: {SYSTEM}  |  Mode: {mode}")
    print("=" * 48)

    # ── Locate SDK ────────────────────────────────────────────────────────────
    sdk = find_sdk()
    if not sdk:
        _die(
            "Android SDK not found.\n"
            "  Set ANDROID_HOME to your SDK path and retry.\n"
            "  e.g.  export ANDROID_HOME=~/Library/Android/sdk"
        )
    print(f"SDK: {sdk}")

    adb          = find_tool(sdk, "platform-tools", "adb")
    emulator_bin = find_tool(sdk, "emulator", "emulator")
    apk          = os.path.join(ROOT, APK_NAME)

    if not adb:
        _die("adb not found. Install Android Platform Tools via SDK Manager.")
    if not emulator_bin:
        _die("emulator not found. Install Android Emulator via SDK Manager.")
    if not os.path.isfile(apk):
        _die(f"APK not found: {apk}")

    # ── Step 1: always start app ───────────────────────────────────────────────
    step_launch_app(adb, emulator_bin, apk)

    # ── Steps 2+: optional tests ───────────────────────────────────────────────
    exit_code = 0
    if mode in ("smoke",):
        exit_code = step_maestro("smoke")
    elif mode in ("regression",):
        exit_code = step_maestro("regression")
    elif mode == "appium":
        exit_code = step_appium()
    elif mode == "all":
        rc1 = step_maestro("regression")
        rc2 = step_appium()
        exit_code = rc1 or rc2

    status = "PASSED" if exit_code == 0 else "FAILED"
    print(f"{'=' * 48}")
    print(f"  Done — {status}")
    print(f"{'=' * 48}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
