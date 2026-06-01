import os

ANDROID_CAPS = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:app": os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../Qatarat (Lambda-Stage).apk")
    ),
    "appium:appPackage": "com.qatarat.app",
    "appium:appActivity": ".MainActivity",
    "appium:noReset": True,
    "appium:fullReset": False,
    # Allow 5 min server-side inactivity (matches pytest --timeout=300)
    "appium:newCommandTimeout": 300,
    "appium:androidInstallTimeout": 90000,
    "appium:autoGrantPermissions": True,
    "appium:skipDeviceInitialization": False,
    "appium:uiautomator2ServerInstallTimeout": 90000,
    "appium:adbExecTimeout": 60000,
    # First session installs the UiAutomator2 server; subsequent sessions skip the
    # version-check round-trip (fast pm-list check only) since the emulator is fresh.
    "appium:skipServerInstallationCheck": True,
}

# Caps for running on a real device (override UDID)
ANDROID_DEVICE_CAPS = {
    **ANDROID_CAPS,
    "appium:deviceName": os.environ.get("ANDROID_DEVICE_NAME", "Android Device"),
    "appium:udid": os.environ.get("ANDROID_UDID", ""),
    "appium:platformVersion": os.environ.get("ANDROID_VERSION", "13"),
}

# Caps for emulator
ANDROID_EMULATOR_CAPS = {
    **ANDROID_CAPS,
    "appium:deviceName": os.environ.get("ANDROID_EMU_NAME", "Pixel_7_API_34"),
    "appium:avd": os.environ.get("ANDROID_AVD", "Pixel_7_API_34"),
    "appium:platformVersion": "13",    # api-level 33 = Android 13
    "appium:isHeadless": False,
}
