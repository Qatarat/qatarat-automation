#!/usr/bin/env python3
"""
Qatarat — iOS local test runner
Only works on macOS.

Usage:
  python run_ios.py               # start iOS app only
  python run_ios.py smoke         # start app + Maestro smoke tests
  python run_ios.py regression    # start app + all Maestro flows
  python run_ios.py appium        # start app + all Appium tests
  python run_ios.py all           # start app + Maestro regression + Appium
"""

import os
import sys
import time
import shutil
import platform
import subprocess
import re

if platform.system() != "Darwin":
    print("ERROR: iOS testing is only supported on macOS.")
    sys.exit(1)

ROOT = os.path.dirname(os.path.abspath(__file__))
TESTING = os.path.join(ROOT, "testing")
APPIUM = os.path.join(TESTING, "appium")

IPA_FILE = "qatarat-stage-ios.ipa"
APP_DIR = "ipa_extracted/Payload/Runner.app"
BUNDLE_ID = "com.qatarat.app"

def run(cmd, **kw):
    return subprocess.run(cmd, **kw)

def out(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""

def _die(msg):
    print(f"\nERROR: {msg}")
    sys.exit(1)

def ensure_gh_cli():
    if not shutil.which("gh"):
        _die("GitHub CLI (gh) not found. Install it with: brew install gh")

def download_ipa():
    if os.path.isdir(APP_DIR):
        print(f"  App already extracted at {APP_DIR}")
        return
    if not os.path.isfile(IPA_FILE):
        print("  Downloading iOS IPA from GitHub Release...")
        ensure_gh_cli()
        r = run(["gh", "release", "download", "ios-ipa-v1.8.2", "--repo", "Qatarat/qatarat-automation", "--pattern", IPA_FILE, "--output", IPA_FILE, "--clobber"])
        if r.returncode != 0:
            _die("Failed to download IPA. Are you logged in to GitHub CLI? Try: gh auth login")
    
    print("  Extracting IPA...")
    shutil.rmtree("ipa_extracted", ignore_errors=True)
    run(["unzip", "-q", IPA_FILE, "-d", "ipa_extracted"], stdout=subprocess.DEVNULL)
    if not os.path.isdir(APP_DIR):
        _die(f"Extracted IPA but could not find {APP_DIR}")

def get_simulator():
    print("  Finding an iPhone Simulator...")
    devices = out(["xcrun", "simctl", "list", "devices", "available"])
    sim_id = None
    for line in devices.splitlines():
        if "iPhone 15 Pro" in line and "Max" not in line and "Plus" not in line:
            m = re.search(r"([A-F0-9-]{36})", line)
            if m:
                sim_id = m.group(1)
                break
    if not sim_id:
        for line in devices.splitlines():
            if "iPhone 15" in line:
                m = re.search(r"([A-F0-9-]{36})", line)
                if m:
                    sim_id = m.group(1)
                    break
    if not sim_id:
        _die("Could not find an iPhone 15 simulator. Please install one via Xcode.")
    return sim_id

def boot_simulator(sim_id):
    sim_status = out(["xcrun", "simctl", "list", "devices"])
    if "(Booted)" in [line for line in sim_status.splitlines() if sim_id in line][0]:
        print(f"  Simulator {sim_id} already booted.")
        return
    print(f"  Booting simulator {sim_id}...")
    run(["xcrun", "simctl", "boot", sim_id])
    run(["xcrun", "simctl", "bootstatus", sim_id, "-b"])
    print("  Simulator booted.")
    time.sleep(2)

def install_and_launch(sim_id):
    print("  Installing app to Simulator...")
    r = run(["xcrun", "simctl", "install", sim_id, APP_DIR])
    if r.returncode != 0:
        _die("Failed to install app on simulator.")
    print("  Launching Qatarat app...")
    run(["xcrun", "simctl", "launch", sim_id, BUNDLE_ID])
    print("  App is running.\n")

# ── Python / venv helpers ─────────────────────────────────────────────────────

def _venv_python():
    return os.path.join(APPIUM, ".venv", "bin", "python")

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
    pip = os.path.join(venv_dir, "bin", "pip")
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
    run(["appium", "driver", "install", "xcuitest"], check=True)
    run(["appium", "driver", "install", "--source=npm", "appium-flutter-driver"], check=True)

def ensure_maestro():
    if shutil.which("maestro"):
        return
    print("  Installing Maestro...")
    run('curl -Ls "https://get.maestro.mobile.dev" | bash', shell=True, check=True)
    if not shutil.which("maestro"):
        _die("Maestro installed but not on PATH. Open a new terminal and re-run.")

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
    log = open(os.path.join(APPIUM, "appium-ios.log"), "a")
    p = subprocess.Popen(
        ["appium", "--port", "4723"],
        stdout=log, stderr=log,
        cwd=APPIUM
    )
    time.sleep(4)
    return p

# ── Main steps ────────────────────────────────────────────────────────────────

def step_maestro(mode):
    ensure_maestro()
    if mode == "smoke":
        suite = os.path.join(TESTING, "maestro", "flows", "suites", "smoke.yaml")
        label = "Maestro Smoke (iOS)"
    else:
        suite = os.path.join(TESTING, "maestro", "flows", "suites", "regression.yaml")
        label = "Maestro Regression (iOS)"

    if not os.path.isfile(suite):
        _die(f"Suite file not found: {suite}")

    print(f"── {label} ──")
    r = run(["bash", os.path.join(TESTING, "run_maestro_ios_ci.sh"), mode], cwd=ROOT)
    print(f"  Maestro exit: {r.returncode}\n")
    return r.returncode

def step_appium():
    ensure_appium()
    venv_py = ensure_venv()
    appium_proc = start_appium()

    os.makedirs(os.path.join(APPIUM, "reports"), exist_ok=True)
    os.makedirs(os.path.join(APPIUM, "allure-results"), exist_ok=True)

    print("── Appium Tests (iOS) ──")
    env = os.environ.copy()
    env["PLATFORM"] = "ios"
    env["DEVICE_MODE"] = "simulator"
    env["IOS_SIM_NAME"] = "iPhone 15 Pro"
    env["IOS_VERSION"] = "17.0"
    env["IOS_APP_PATH"] = os.path.abspath(APP_DIR)
    env["APPIUM_HOST"] = "localhost"
    env["APPIUM_PORT"] = "4723"

    r = run(
        [venv_py, "-m", "pytest", "tests/", "-v",
         "--html=reports/report-ios.html", "--self-contained-html",
         "--junit-xml=reports/results-ios.xml",
         "--alluredir=allure-results",
         "--tb=short"],
        cwd=APPIUM,
        env=env
    )
    print(f"  Appium exit: {r.returncode}")
    print(f"  Report: {os.path.join(APPIUM, 'reports', 'report-ios.html')}\n")

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
    print(f"  Qatarat iOS Launcher  |  OS: macOS  |  Mode: {mode}")
    print("=" * 48)

    download_ipa()
    sim_id = get_simulator()
    boot_simulator(sim_id)
    install_and_launch(sim_id)

    exit_code = 0
    if mode == "smoke":
        exit_code = step_maestro("smoke")
    elif mode == "regression":
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
