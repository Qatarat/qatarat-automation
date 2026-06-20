import os
import platform

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# .app bundle extracted from the IPA (works on Simulator)
_APP_BUNDLE = os.path.join(
    _ROOT,
    "ipa_extracted",
    "Payload",
    "Runner.app",
)

# Original IPA (for real-device installs via tidevice / Xcode)
_IPA_PATH = os.path.join(_ROOT, "qatarat-stage-ios.ipa")

# Detect macOS Tahoe (26.x) — iOS 26.5 simulator only, arm64-only, no Rosetta sim.
# The bundled IPA is x86_64 so it requires iOS 17.x runtime or a new arm64 build.
_macos_ver = tuple(int(x) for x in platform.mac_ver()[0].split(".")[:2])
_ON_TAHOE  = _macos_ver[0] >= 26       # macOS 26.x = Tahoe

# Default iOS version: 17.5 on older macOS (has Rosetta sim for x86_64 IPA),
# fall back to 26.5 on Tahoe if no iOS 17 runtime is installed.
_DEFAULT_IOS_VER = "26.5" if _ON_TAHOE else "17.5"
_DEFAULT_SIM_NAME = "iPhone 17 Pro" if _ON_TAHOE else "iPhone 15 Pro"

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
    "appium:deviceName": os.environ.get("IOS_SIM_NAME", _DEFAULT_SIM_NAME),
    "appium:platformVersion": os.environ.get("IOS_VERSION", _DEFAULT_IOS_VER),
    "appium:app": os.environ.get("IOS_APP_PATH", _APP_BUNDLE),
    **({"appium:udid": _sim_id} if _sim_id else {}),
    # Extended timeouts for macOS CI runners (macos-14 is slower than local Mac)
    "appium:simulatorStartupTimeout": 300000,   # 5 min (was 3 min)
    "appium:wdaLaunchTimeout": 180000,          # 3 min (was 2 min)
    "appium:wdaConnectionTimeout": 180000,      # 3 min (was 2 min)
    # usePreinstalledWDA: False (default) — build+install WDA on first session.
    # True would skip the build step but requires WDA already compiled, which
    # fails on fresh CI runners with FBSOpenApplicationServiceErrorDomain code=4.
    "appium:usePreinstalledWDA": False,
    # Reuse the already-running WDA between successive test sessions (safe + faster).
    # Unlike usePreinstalledWDA, this does NOT skip the initial build.
    "appium:useNewWDA": False,
    # Prevent slow Safari/webview context enumeration on every session
    "appium:includeSafariInWebviews": False,
    "appium:fullContextList": False,
    # Pre-set simulator language/locale so the app skips the country/language
    # selection screen on first launch (otherwise app stays on that screen
    # and the phone text field is never reachable)
    "appium:language": "en",
    "appium:locale": "en_US",
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
