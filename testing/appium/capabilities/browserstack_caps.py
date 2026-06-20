import os

# BrowserStack credentials — set these env vars or fill directly:
#   export BS_USERNAME="your_username"
#   export BS_ACCESS_KEY="your_access_key"
BS_USERNAME   = os.environ.get("BS_USERNAME", "")
BS_ACCESS_KEY = os.environ.get("BS_ACCESS_KEY", "")
BS_SERVER     = f"https://{BS_USERNAME}:{BS_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

# IPA must be uploaded first:
#   curl -u "user:key" -X POST https://api-cloud.browserstack.com/app-automate/upload \
#        -F "file=@qatarat-stage-ios.ipa"
# Then set: export BS_APP_URL="bs://..."
BS_APP_URL = os.environ.get("BS_APP_URL", "")

BROWSERSTACK_IOS_CAPS = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:app": BS_APP_URL,
    "appium:deviceName": os.environ.get("BS_DEVICE", "iPhone 15 Pro"),
    "appium:platformVersion": os.environ.get("BS_IOS_VERSION", "17"),
    "appium:noReset": False,
    "appium:newCommandTimeout": 300,
    "appium:autoAcceptAlerts": True,
    # BrowserStack-specific
    "bstack:options": {
        "userName": BS_USERNAME,
        "accessKey": BS_ACCESS_KEY,
        "projectName": "Qatarat iOS",
        "buildName": os.environ.get("BS_BUILD", "local"),
        "sessionName": "Appium iOS Tests",
        "debug": True,
        "networkLogs": True,
        "video": True,
        "appiumVersion": "2.0",
    },
}
