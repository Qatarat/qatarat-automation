import os

IOS_CAPS = {
    "platformName": "iOS",
    "appium:automationName": "Flutter",           # uses appium-flutter-driver
    "appium:bundleId": "com.qatarat.app",
    "appium:noReset": False,
    "appium:newCommandTimeout": 120,
    "appium:autoAcceptAlerts": True,
    # Flutter-specific
    "appium:retryBackoffTime": 500,
    "appium:maxRetryCount": 3,
}

# Real device — requires IPA and provisioning
# UDID read from IOS_UDID (set by run_on_device.sh) or IOS_DEVICE_NAME env var
_ios_udid = os.environ.get("IOS_UDID", "")
IOS_DEVICE_CAPS = {
    **IOS_CAPS,
    "appium:deviceName": os.environ.get("IOS_DEVICE_NAME", "iPhone"),
    "appium:udid": _ios_udid,
    "appium:platformVersion": os.environ.get("IOS_VERSION", "17"),
    "appium:app": os.environ.get("IOS_APP_PATH", ""),  # path to .ipa file
    "appium:xcodeOrgId": os.environ.get("XCODE_ORG_ID", ""),
    "appium:xcodeSigningId": "iPhone Developer",
    "appium:updatedWDABundleId": "com.qatarat.app.WebDriverAgentRunner",
}

# Simulator
IOS_SIMULATOR_CAPS = {
    **IOS_CAPS,
    "appium:deviceName": os.environ.get("IOS_SIM_NAME", "iPhone 15 Pro"),
    "appium:platformVersion": "17.5",
    "appium:app": os.environ.get("IOS_APP_PATH", ""),  # path to .app (simulator build)
    "appium:simulatorStartupTimeout": 120000,
}
