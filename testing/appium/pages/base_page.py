from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.helpers import find_by_text, screenshot, wait_for_animation


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def tap(self, text):
        el = find_by_text(self.driver, text)
        el.click()
        wait_for_animation(self.driver)
        return self

    def tap_optional(self, text, timeout=3):
        try:
            el = find_by_text(self.driver, text, timeout=timeout)
            el.click()
            wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def assert_visible(self, text, timeout=10):
        find_by_text(self.driver, text, timeout=timeout)
        return self

    def input_text(self, placeholder, value):
        el = find_by_text(self.driver, placeholder)
        el.clear()
        el.send_keys(value)
        return self

    def screenshot(self, name):
        return screenshot(self.driver, name)

    def is_visible(self, text, timeout=5):
        try:
            find_by_text(self.driver, text, timeout=timeout)
            return True
        except Exception:
            return False
