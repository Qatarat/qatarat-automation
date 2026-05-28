import importlib
import os
import subprocess
import pytest
import allure
from appium import webdriver

from capabilities.android_caps import ANDROID_DEVICE_CAPS, ANDROID_EMULATOR_CAPS
from capabilities.ios_caps import IOS_DEVICE_CAPS, IOS_SIMULATOR_CAPS
from utils.helpers import APPIUM_SERVER, screenshot

PLATFORM = os.environ.get("PLATFORM", "android").lower()
DEVICE_MODE = os.environ.get("DEVICE_MODE", "emulator").lower()

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


@pytest.fixture(scope="function")
def driver():
    import time as _time
    if PLATFORM == "android":
        _reset_android_app()
    d = webdriver.Remote(APPIUM_SERVER, options=_build_options(get_caps()))
    d.implicitly_wait(10)
    _time.sleep(4)   # wait for app splash / initial load
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture(scope="module")
def driver_module():
    caps = {**get_caps(), "appium:noReset": True}
    d = webdriver.Remote(APPIUM_SERVER, options=_build_options(caps))
    d.implicitly_wait(10)
    yield d
    d.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("driver_module")
        if driver:
            try:
                png = driver.get_screenshot_as_png()
                allure.attach(
                    png,
                    name=f"FAIL — {item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
                os.makedirs("reports/screenshots", exist_ok=True)
                screenshot(driver, f"FAIL_{item.name}")
            except Exception:
                pass
