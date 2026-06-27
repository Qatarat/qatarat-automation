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

# Detect macOS version to choose the right default simulator.
# The IPA is an x86_64 simulator build; Rosetta 2 runs it on Apple Silicon for any macOS.
# macOS 26 (Tahoe) = Xcode 26 + iOS 26.x sims; macOS 15 (Sequoia) = Xcode 16 + iOS 18.x sims;
# macOS 14 (Sonoma) = Xcode 15 + iOS 17.x sims.
_mac_ver_str = platform.mac_ver()[0]  # empty string on Linux — guard against ValueError
_macos_ver = tuple(int(x) for x in _mac_ver_str.split(".")[:2]) if _mac_ver_str else (0, 0)
_ON_TAHOE    = _macos_ver[0] >= 26   # macOS 26.x = Tahoe
_ON_SEQUOIA  = _macos_ver[0] == 15   # macOS 15.x = Sequoia

# ios_ci_setup.sh exports IOS_VERSION from xcrun simctl — that always overrides these defaults.
# These only apply when running locally without ios_ci_setup.sh.
if _ON_TAHOE:
    _DEFAULT_IOS_VER = "26.5"
    _DEFAULT_SIM_NAME = "iPhone 17 Pro"
elif _ON_SEQUOIA:
    _DEFAULT_IOS_VER = "18.4"
    _DEFAULT_SIM_NAME = "iPhone 16 Pro"
else:
    _DEFAULT_IOS_VER = "17.5"
    _DEFAULT_SIM_NAME = "iPhone 15 Pro"

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
    # Extended timeouts for macOS CI runners (macos-15 with iOS 18 needs more headroom)
    "appium:simulatorStartupTimeout": 300000,   # 5 min
    "appium:wdaLaunchTimeout": 300000,          # 5 min — WDA re-compilation on cold sessions
    "appium:wdaConnectionTimeout": 300000,      # 5 min — iOS 18 sim connects slower than 17
    # usePreinstalledWDA: False (default) — build+install WDA on first session.
    # True skips the build step but requires WDA already compiled. The CI iOS
    # workflow runs a pre-warm session that compiles WDA, then sets
    # IOS_WDA_PREBUILT=1 via GITHUB_ENV so every subsequent test session reuses
    # the already-installed WDA bundle. Without this, each function-scoped
    # session re-builds WDA (~480s) and pytest-timeout kills it.
    "appium:usePreinstalledWDA": os.environ.get("IOS_WDA_PREBUILT", "") == "1",
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
    # Pre-grant permissions so system dialogs never appear mid-test.
    # Location dialog blocks all tests when it overlays the home screen.
    "appium:permissions": '{"com.qatarat.app": {"location": "yes", "notifications": "yes", "camera": "yes", "photos": "yes"}}',
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
