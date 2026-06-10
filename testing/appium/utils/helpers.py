import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


APPIUM_SERVER = os.environ.get("APPIUM_SERVER", "http://127.0.0.1:4723")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../reports/screenshots")


def is_ios() -> bool:
    return os.environ.get("PLATFORM", "android").lower() == "ios"


def text_field_xpath() -> str:
    """XPath matching editable fields on Android or iOS."""
    if is_ios():
        return "//XCUIElementTypeTextField | //XCUIElementTypeSecureTextField"
    return "//android.widget.EditText"


def find_elements_by_label(driver, label: str, contains: bool = False):
    """Find elements by visible label — Android content-desc/text or iOS name/label/value."""
    if is_ios():
        if contains:
            xp = (
                f'//*[contains(@name,"{label}") or contains(@label,"{label}") '
                f'or contains(@value,"{label}")]'
            )
        else:
            xp = (
                f'//*[@name="{label}" or @label="{label}" or @value="{label}"]'
            )
    else:
        if contains:
            xp = (
                f'//*[contains(@content-desc,"{label}") or contains(@text,"{label}")]'
            )
        else:
            xp = f'//*[@content-desc="{label}" or @text="{label}"]'
    return driver.find_elements(AppiumBy.XPATH, xp)


def wait_for_text(driver, text, timeout=15):
    return find_by_text(driver, text, timeout=timeout)


def tap_text(driver, text, timeout=15):
    el = wait_for_text(driver, text, timeout)
    el.click()
    return el


def find_by_text(driver, text, timeout=10):
    """Find element by visible text — tries multiple locator strategies per platform."""
    if is_ios():
        strategies = [
            (AppiumBy.ACCESSIBILITY_ID, text),
            (AppiumBy.XPATH, f'//*[@name="{text}"]'),
            (AppiumBy.XPATH, f'//*[@label="{text}"]'),
            (AppiumBy.XPATH, f'//*[@value="{text}"]'),
            (AppiumBy.XPATH, f'//*[contains(@name,"{text}")]'),
            (AppiumBy.XPATH, f'//*[contains(@label,"{text}")]'),
            (AppiumBy.XPATH, f'//*[contains(@value,"{text}")]'),
            (AppiumBy.XPATH, f'//XCUIElementTypeButton[@name="{text}"]'),
            (AppiumBy.XPATH, f'//XCUIElementTypeStaticText[@name="{text}"]'),
        ]
        # Each strategy gets at least 2s — iOS CI simulators are significantly slower
        # than local Macs; 1s (the old value) caused false negatives on every strategy.
        per_strategy = max(2, min(4, timeout // max(1, len(strategies) // 3)))
    else:
        strategies = [
            (AppiumBy.XPATH, f'//*[@content-desc="{text}"]'),
            (AppiumBy.ACCESSIBILITY_ID, text),
            (AppiumBy.XPATH, f'//*[@text="{text}"]'),
            (AppiumBy.XPATH, f'//*[contains(@content-desc,"{text}")]'),
            (AppiumBy.XPATH, f'//*[contains(@text,"{text}")]'),
        ]
        per_strategy = max(1, min(3, timeout // len(strategies)))

    deadline = time.time() + timeout
    for by, val in strategies:
        if time.time() >= deadline:
            break
        wait = min(per_strategy, max(1, deadline - time.time()))
        try:
            return WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((by, val))
            )
        except (TimeoutException, NoSuchElementException):
            continue
    raise NoSuchElementException(f"Could not find element with text: {text}")


def clear_and_type(driver, element, text: str) -> None:
    """Clear a text field and type new text — handles iOS quirks.

    On iOS, element.clear() can leave stale cursor state or silently fail.
    This function verifies the clear worked and falls back to mobile: clearText.
    """
    element.click()
    time.sleep(0.3)
    if is_ios():
        element.clear()
        time.sleep(0.2)
        current = element.get_attribute("value") or ""
        if current:
            try:
                driver.execute_script("mobile: clearText", {"element": element.id})
                time.sleep(0.2)
            except Exception:
                pass
    else:
        element.clear()
    if text:
        element.send_keys(text)
        time.sleep(0.1)


def screenshot(driver, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, f"{name}_{int(time.time())}.png")
    driver.save_screenshot(path)
    return path


def wait_for_animation(driver, seconds=1.5):
    time.sleep(seconds)


def scroll_to_text(driver, text, direction="down", max_scrolls=10):
    for _ in range(max_scrolls):
        try:
            return find_by_text(driver, text, timeout=2)
        except NoSuchElementException:
            size = driver.get_window_size()
            w, h = size["width"], size["height"]
            if is_ios():
                # Stay within safe scroll zone — avoid triggering home indicator / control center
                start_y = int(h * 0.65)
                end_y = int(h * 0.35)
            else:
                start_y = int(h * 0.7)
                end_y = int(h * 0.3)
            if direction == "down":
                driver.swipe(w // 2, start_y, w // 2, end_y, 800)
            else:
                driver.swipe(w // 2, end_y, w // 2, start_y, 800)
    raise NoSuchElementException(f"Could not scroll to: {text}")


def enter_otp(driver, otp="1234"):
    fields = driver.find_elements(AppiumBy.XPATH, text_field_xpath())
    if not fields:
        raise NoSuchElementException("No text fields found for OTP entry")
    if len(fields) >= len(otp):
        for i, digit in enumerate(otp):
            fields[i].click()
            fields[i].send_keys(digit)
            time.sleep(0.1)
    else:
        fields[0].click()
        fields[0].send_keys(otp)
