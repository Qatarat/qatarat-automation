import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


APPIUM_SERVER = os.environ.get("APPIUM_SERVER", "http://127.0.0.1:4723")
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../reports/screenshots")


def wait_for_text(driver, text, timeout=15):
    return find_by_text(driver, text, timeout=timeout)


def tap_text(driver, text, timeout=15):
    el = wait_for_text(driver, text, timeout)
    el.click()
    return el


def find_by_text(driver, text, timeout=10):
    """Find element by visible text — tries multiple locator strategies."""
    strategies = [
        (AppiumBy.XPATH, f'//*[@content-desc="{text}"]'),
        (AppiumBy.ACCESSIBILITY_ID, text),
        (AppiumBy.XPATH, f'//*[@text="{text}"]'),
        (AppiumBy.XPATH, f'//*[contains(@content-desc,"{text}")]'),
        (AppiumBy.XPATH, f'//*[contains(@text,"{text}")]'),
    ]
    # Spread total timeout across strategies but cap per-strategy to avoid slow misses
    n = len(strategies)
    per_strategy = max(1, min(3, timeout // n))
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
            if direction == "down":
                driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 600)
            else:
                driver.swipe(w // 2, int(h * 0.3), w // 2, int(h * 0.7), 600)
    raise NoSuchElementException(f"Could not scroll to: {text}")


def enter_otp(driver, otp="1234"):
    for digit in otp:
        driver.find_element(AppiumBy.XPATH, f"//android.widget.EditText").send_keys(digit)
        time.sleep(0.1)
