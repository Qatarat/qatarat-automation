import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# .app bundle extracted from the IPA (works on Simulator)
_APP_BUNDLE = os.path.join(
    _ROOT,
    "Qatarat (Lambda-Stage-IOS-1.8.2).ipa",
    "Payload",
    "Runner.app",
)

# Original IPA (for real-device installs via tidevice / Xcode)
_IPA_PATH = os.path.join(_ROOT, "Qatarat (Lambda-Stage-IOS-1.8.2).ipa.zip")

IOS_CAPS = {
    "platformName": "iOS",
    # XCUITest works with any build (debug OR distribution/staging IPA).
    # Flutter driver requires a debug build with Observatory running — not available
    # in Lambda/BrowserStack staging IPAs, causing "architecture not supported" failures.
    "appium:automationName": "XCUITest",
    "appium:bundleId": "com.qatarat.app",
    "appium:noReset": False,
    # Match Android's 300s — prevents "New Command Timeout" mid-test on slow CI runners
    "appium:newCommandTimeout": 300,
    "appium:autoAcceptAlerts": True,
    "appium:retryBackoffTime": 500,
    "appium:maxRetryCount": 3,
    "appium:forceSimulatorSoftwareKeyboardPresence": True,
    # Ensure software keyboard (never hardware) — critical for send_keys on simulator
    "appium:connectHardwareKeyboard": False,
    # Clean up WDA artifacts between sessions; prevents stale XCUITest state
    "appium:clearSystemFiles": True,
    # Disable system animations — speeds up element detection, reduces flakiness
    "appium:reduceMotion": True,
    # Lower screenshot quality reduces per-screenshot memory pressure on CI
    "appium:screenshotQuality": 2,
    # Suppress Xcode compilation logs from Appium output
    "appium:showXcodeLog": False,
}

# ── Simulator (default for local dev + CI) ────────────────────────────────────
_sim_id = os.environ.get("SIM_ID", "")
IOS_SIMULATOR_CAPS = {
    **IOS_CAPS,
    "appium:deviceName": os.environ.get("IOS_SIM_NAME", "iPhone 15 Pro"),
    "appium:platformVersion": os.environ.get("IOS_VERSION", "17.5"),
    "appium:app": os.environ.get("IOS_APP_PATH", _APP_BUNDLE),
    **({"appium:udid": _sim_id} if _sim_id else {}),
    # Extended timeouts for macOS CI runners (macos-14 is slower than local Mac)
    "appium:simulatorStartupTimeout": 300000,   # 5 min (was 3 min)
    "appium:wdaLaunchTimeout": 180000,          # 3 min (was 2 min)
    "appium:wdaConnectionTimeout": 180000,      # 3 min (was 2 min)
    # Reuse WDA after first install — saves 30–60s per session on subsequent tests
    "appium:usePreinstalledWDA": True,
    # Prevent slow Safari/webview context enumeration on every session
    "appium:includeSafariInWebviews": False,
    "appium:fullContextList": False,
}

# ── Real device ───────────────────────────────────────────────────────────────
IOS_DEVICE_CAPS = {
    **IOS_CAPS,
    "appium:deviceName": os.environ.get("IOS_DEVICE_NAME", "iPhone"),
    "appium:udid": os.environ.get("IOS_UDID", ""),
    "appium:platformVersion": os.environ.get("IOS_VERSION", "17"),
    "appium:app": os.environ.get("IOS_APP_PATH", _IPA_PATH),
    "appium:xcodeOrgId": os.environ.get("XCODE_ORG_ID", ""),
    "appium:xcodeSigningId": "iPhone Developer",
    "appium:updatedWDABundleId": "com.qatarat.app.WebDriverAgentRunner",
}
