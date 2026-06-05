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
    "appium:newCommandTimeout": 120,
    "appium:autoAcceptAlerts": True,
    "appium:retryBackoffTime": 500,
    "appium:maxRetryCount": 3,
    "appium:forceSimulatorSoftwareKeyboardPresence": True,
}

# ── Simulator (default for local dev + CI) ────────────────────────────────────
IOS_SIMULATOR_CAPS = {
    **IOS_CAPS,
    "appium:deviceName": os.environ.get("IOS_SIM_NAME", "iPhone 15 Pro"),
    "appium:platformVersion": os.environ.get("IOS_VERSION", "17.5"),
    "appium:app": os.environ.get("IOS_APP_PATH", _APP_BUNDLE),
    "appium:simulatorStartupTimeout": 180000,
    "appium:wdaLaunchTimeout": 120000,
    "appium:wdaConnectionTimeout": 120000,
    "appium:usePreinstalledWDA": False,
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
