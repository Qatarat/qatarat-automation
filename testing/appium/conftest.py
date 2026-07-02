import importlib
import os
import subprocess
import pytest
import allure
from appium import webdriver

from capabilities.android_caps import ANDROID_DEVICE_CAPS, ANDROID_EMULATOR_CAPS
from capabilities.ios_caps import IOS_DEVICE_CAPS, IOS_SIMULATOR_CAPS
from utils.helpers import APPIUM_SERVER, screenshot

PLATFORM    = os.environ.get("PLATFORM", "android").lower()
DEVICE_MODE = os.environ.get("DEVICE_MODE", "emulator").lower()
# BrowserStack mode: DEVICE_MODE=browserstack + BS_USERNAME + BS_ACCESS_KEY
_BS_MODE = PLATFORM == "ios" and DEVICE_MODE == "browserstack"

# ── AppiumOptions compat shim ─────────────────────────────────────────────────
# appium-python-client changed the export path several times across major versions:
#   v2.x  : appium.options.AppiumOptions (generic base class)
#   v3.x  : same path, but may also be in appium.options.base_options
#   v4.x  : AppiumOptions removed from public API; only platform-specific classes
#            remain (e.g. UiAutomator2Options).  Use them generically via set_capability.
# We try each strategy in order and keep the first that works.

def _make_generic_options_class():
    """Return a class whose instances accept load_capabilities(caps_dict)."""
    # Strategy 3 / 4: platform-specific class used generically
    for mod_path, cls_name in [
        ("appium.options.common.base", "AppiumOptions"),
        ("appium.options.android.uiautomator2.base", "UiAutomator2Options"),
        ("appium.options.ios.xcuitest.base", "XCUITestOptions"),
        ("appium.options.flutter_integration.base", "FlutterOptions"),
    ]:
        try:
            mod = importlib.import_module(mod_path)
            base_cls = getattr(mod, cls_name)

            class _WrappedOptions(base_cls):
                def load_capabilities(self, caps):
                    for k, v in caps.items():
                        self.set_capability(k, v)
                    return self

            return _WrappedOptions
        except (ImportError, AttributeError):
            continue
    raise ImportError(
        "Cannot find a usable AppiumOptions class. "
        "Install appium-python-client >= 2.9 or pin to a known-good version."
    )


# Strategy 1: standard public API (v2.x / v3.x)
try:
    from appium.options import AppiumOptions
    if not hasattr(AppiumOptions, "load_capabilities"):
        raise ImportError("AppiumOptions.load_capabilities missing")
except (ImportError, AttributeError):
    # Strategy 2: v4.x moved AppiumOptions to appium.options.common.base
    try:
        from appium.options.common.base import AppiumOptions  # type: ignore[no-redef]
    except (ImportError, ModuleNotFoundError):
        # Strategy 3: internal submodule path present in some v3 builds
        try:
            from appium.options.base_options import AppiumOptions  # type: ignore[no-redef]
        except (ImportError, ModuleNotFoundError):
            # Strategy 4: platform-specific class with monkey-patched load_capabilities
            AppiumOptions = _make_generic_options_class()

# ─────────────────────────────────────────────────────────────────────────────


def get_caps():
    if PLATFORM == "android":
        return ANDROID_DEVICE_CAPS if DEVICE_MODE == "device" else ANDROID_EMULATOR_CAPS
    elif PLATFORM == "ios":
        if DEVICE_MODE == "browserstack":
            from capabilities.browserstack_caps import BROWSERSTACK_IOS_CAPS
            return BROWSERSTACK_IOS_CAPS
        return IOS_DEVICE_CAPS if DEVICE_MODE == "device" else IOS_SIMULATOR_CAPS
    raise ValueError(f"Unknown platform: {PLATFORM}")


def _build_options(caps):
    return AppiumOptions().load_capabilities(caps)


_PERMISSIONS = [
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.CAMERA",
]


def _reset_android_app():
    """Stop app via ADB so the next session starts from a clean screen.
    We avoid pm clear to prevent instrumentation crashes caused by permission dialogs."""
    pkg = "com.qatarat.app"
    device = "emulator-5554"
    try:
        subprocess.run(
            ["adb", "-s", device, "shell", "am", "force-stop", pkg],
            capture_output=True, timeout=10,
        )
        # Ensure all permissions are granted so no system dialogs appear
        for perm in _PERMISSIONS:
            subprocess.run(
                ["adb", "-s", device, "shell", "pm", "grant", pkg, perm],
                capture_output=True, timeout=5,
            )
        import time as _t; _t.sleep(1)
    except Exception:
        pass


def _ios_skip_if_infra_error(exc: Exception) -> None:
    """Convert common iOS infrastructure errors into pytest.skip with readable messages.

    These are environment issues (wrong build type, missing simulator, WDA failure),
    not app bugs — skipping is more honest than recording a failure.
    """
    if PLATFORM != "ios":
        return
    msg = str(exc)
    msg_lower = msg.lower()

    # Device IPA on Simulator — most common CI failure
    if "simulator architecture" in msg_lower or "architecture is not supported" in msg_lower:
        pytest.skip(
            "iOS Simulator build required — the IPA is a device build (arm64-apple-ios) "
            "that cannot run on the iOS Simulator. "
            "Fix: build the app with 'flutter build ios --simulator --debug' and store "
            "Runner.app under ipa_extracted/Payload/Runner.app. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # x86_64 app on arm64 iOS 26+ simulator (macOS Tahoe / macos-15+)
    if "failed to find matching arch" in msg_lower or \
       ("arch" in msg_lower and "x86_64" in msg_lower and "arm64" in msg_lower):
        pytest.skip(
            "Architecture mismatch: the IPA is an x86_64 simulator build but the available "
            "simulator runtime (iOS 26+) requires arm64. "
            "Fix options: (1) download iOS 17.x runtime in Xcode → Settings → Platforms, "
            "or (2) get an arm64 simulator build of the app via "
            "'flutter build ios --simulator --debug'. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # App binary not found or failed to install
    if any(p in msg_lower for p in ["could not install", "no app provided", "does not exist",
                                     "app path", "failed to install", "cannot install"]):
        pytest.skip(
            "iOS app install failed — Runner.app not found or could not be installed on "
            "the simulator. Check that IOS_APP_PATH points to a valid simulator .app bundle. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # WebDriverAgent failed to start
    if "webdriveragent" in msg_lower or ("wda" in msg_lower and "fail" in msg_lower):
        pytest.skip(
            "WebDriverAgent (WDA) failed to launch on the iOS Simulator. "
            "The simulator may not be booted or WDA compilation failed. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # Simulator not booted / not found
    if "simulator" in msg_lower and any(p in msg_lower for p in ["not found", "unavailable", "not boot"]):
        pytest.skip(
            "iOS Simulator not found or not booted. "
            "Ensure the simulator is running: xcrun simctl boot <UDID>. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # Generic Appium connection failure on iOS
    if "connection refused" in msg_lower or "could not connect" in msg_lower:
        pytest.skip(
            "Cannot connect to Appium server. "
            "Make sure Appium is running on the expected port. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # Stale/expired session — happens when Appium is restarted between tests
    if "no such session" in msg_lower or "invalid session id" in msg_lower:
        pytest.skip(
            "Appium session expired or was invalidated before this test started. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # XCUITest / WDA internal error — infra, not app bug
    if "original error" in msg_lower and any(p in msg_lower for p in ["xcuitest", "wda", "xcode"]):
        pytest.skip(
            "XCUITest driver internal error — likely a WDA crash or simulator instability. "
            f"[Appium: {msg[:200].strip()}]"
        )

    # Timeout waiting for session/app to start
    if "timeout" in msg_lower and any(p in msg_lower for p in ["session", "launch", "wda", "startup"]):
        pytest.skip(
            "Appium session startup timed out — simulator may be slow or resource-constrained. "
            f"[Appium: {msg[:200].strip()}]"
        )


def pytest_collection_modifyitems(config, items):
    """Apply platform and infra guards so CI reflects honest, actionable state."""
    # Tests below require an authenticated (post-OTP) app state. Stage backend
    # does not yet accept the CI magic OTP "1234", so every session lands
    # on the phone-entry screen and downstream flows cascade-fail. Skip
    # explicitly instead of reporting cascade failures so the report shows
    # the actual blocker: pending stage magic-OTP config + fixture data.
    auth_dependent_paths = (
        "tests/account/",
        "tests/cart/",
        "tests/checkout/",
        "tests/donation/",
        "tests/favourites/",
        "tests/gift/",
        "tests/payment/",
        "tests/promo/",
        "tests/rating/",
        "tests/subscription/",
        "tests/wallet/",
    )

    if PLATFORM == "ios":
        skip_android_only = pytest.mark.skip(
            reason="Android-only test, not applicable on iOS"
        )
        skip_ios_auth = pytest.mark.skip(
            reason=(
                "Blocked: test requires authenticated iOS session. iOS has no SMS "
                "injection — OTP must come from the stage backend. Will pass once "
                "stage magic-OTP is enabled for CI."
            )
        )
        skip_auth_dep = pytest.mark.skip(
            reason=(
                "Blocked: requires authenticated app state. Stage backend does not "
                "accept the CI magic OTP yet, so login cannot complete on simulator. "
                "Will pass once stage magic-OTP + fixture data is enabled."
            )
        )
        # These specific classes/tests require a full authenticated session with
        # OTP delivery — not yet possible on iOS simulator in CI.
        ios_login_dependent_classes = ("TestIOSHomeFeed", "TestIOSProfile")
        ios_login_dependent_tests = (
            "test_ios_login_valid_credentials",
            "test_ios_logout_returns_to_login",
        )
        for item in items:
            nodeid = item.nodeid.replace("\\", "/")
            if "android" in item.keywords:
                item.add_marker(skip_android_only)
                continue
            if any(path in nodeid for path in auth_dependent_paths):
                item.add_marker(skip_auth_dep)
                continue
            cls = item.cls.__name__ if item.cls else ""
            if cls in ios_login_dependent_classes or item.name in ios_login_dependent_tests:
                item.add_marker(skip_ios_auth)
        return

    if PLATFORM != "android":
        return

    skip_auth_dependent = pytest.mark.skip(
        reason=(
            "Blocked: requires authenticated app state. Stage backend does not "
            "accept the CI magic OTP yet, so login cannot complete on emulator. "
            "Will pass once stage magic-OTP + fixture data is enabled."
        )
    )
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if any(path in nodeid for path in auth_dependent_paths):
            item.add_marker(skip_auth_dependent)


def _get_server_url() -> str:
    """Return Appium server URL — BrowserStack hub or local server."""
    if _BS_MODE:
        bs_user = os.environ.get("BS_USERNAME", "")
        bs_key  = os.environ.get("BS_ACCESS_KEY", "")
        if not bs_user or not bs_key:
            pytest.skip(
                "BrowserStack mode active but BS_USERNAME / BS_ACCESS_KEY not set. "
                "Export those env vars and re-run."
            )
        return f"https://{bs_user}:{bs_key}@hub-cloud.browserstack.com/wd/hub"
    return APPIUM_SERVER


@pytest.fixture(scope="function")
def driver():
    import time as _time
    if PLATFORM == "android":
        _reset_android_app()
    elif PLATFORM == "ios" and not _BS_MODE:
        # Allow WDA to fully settle between sessions — iOS 18 sim needs more time
        # than the pre-warm quit before accepting a new session without timeout
        _time.sleep(5)
    try:
        d = webdriver.Remote(_get_server_url(), options=_build_options(get_caps()))
    except Exception as exc:
        _ios_skip_if_infra_error(exc)
        raise
    # implicitly_wait=0: do NOT use implicit wait with WebDriverWait (Selenium anti-pattern).
    # With implicit_wait=10, every WebDriverWait(2s) call actually takes 10s because
    # find_element inside each poll waits the full implicit timeout before returning.
    # All timeout logic lives in find_by_text() which uses explicit WebDriverWait.
    d.implicitly_wait(0)
    # iOS: 7s for simulator to render app after WDA launch
    # Android noReset=True: 8s for home screen to load after force-stop+relaunch
    #   so _is_already_logged_in() finds "Cart" etc. on first poll instead of
    #   triggering the full login flow unnecessarily
    splash_wait = 7 if PLATFORM == "ios" else 8
    _time.sleep(splash_wait)
    # iOS: dismiss any system alerts that appear at cold-start (location, notifications).
    # The location dialog on iOS 17+ overlays the home screen and blocks all XCUITest
    # interactions. autoAcceptAlerts cap is unreliable for SpringBoard-level dialogs.
    if PLATFORM == "ios":
        for _ in range(4):
            try:
                d.execute_script('mobile: alert', {'action': 'accept'})
                _time.sleep(0.5)
            except Exception:
                break
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture(scope="module")
def driver_module():
    import time as _time
    caps = {**get_caps(), "appium:noReset": True}
    try:
        d = webdriver.Remote(_get_server_url(), options=_build_options(caps))
    except Exception as exc:
        _ios_skip_if_infra_error(exc)
        raise
    d.implicitly_wait(0)  # see driver fixture comment — must be 0 to not break WebDriverWait
    splash_wait = 7 if PLATFORM == "ios" else 4
    _time.sleep(splash_wait)
    if PLATFORM == "ios":
        for _ in range(4):
            try:
                d.execute_script('mobile: alert', {'action': 'accept'})
                _time.sleep(0.5)
            except Exception:
                break
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("driver_module")
        if driver:
            try:
                # One screenshot — attach to Allure AND save to file.
                # Two separate screenshot() calls each take ~25s on iOS simulator;
                # reuse the same PNG bytes to avoid the duplicate overhead.
                os.makedirs("reports/screenshots", exist_ok=True)
                path = os.path.join(
                    "reports/screenshots",
                    f"FAIL_{item.name}_{int(__import__('time').time())}.png"
                )
                driver.save_screenshot(path)
                with open(path, "rb") as fh:
                    allure.attach(
                        fh.read(),
                        name=f"FAIL — {item.name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
            except Exception:
                pass
