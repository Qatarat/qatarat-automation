from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text

_HOME_INDICATORS = ["Home", "الرئيسية", "Donate", "Live Broadcast", "Visual documentations"]
_FEATURED_LABELS = ["Featured", "Recommended", "Popular", "مميز"]
_BANNER_LABELS = ["Banner", "Promotion", "Announcement"]


class HomePage(BasePage):

    def is_on_home_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _HOME_INDICATORS)

    def navigate_to_home(self):
        if self.is_on_home_screen(timeout=3):
            return self
        for label in ["Home", "الرئيسية"]:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def get_featured_items_count(self):
        try:
            results = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Mosque") or contains(@content-desc,"mosque")]',
            )
            return len(results)
        except Exception:
            return 0

    def tap_first_mosque(self):
        try:
            results = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Mosque") or contains(@content-desc,"mosque")]',
            )
            if results:
                results[0].click()
                wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def scroll_feed(self, times=3):
        for _ in range(times):
            size = self.driver.get_window_size()
            self.driver.swipe(
                size["width"] // 2, int(size["height"] * 0.7),
                size["width"] // 2, int(size["height"] * 0.3),
                600,
            )
            wait_for_animation(self.driver, 0.5)
        return self

    def tap_live_broadcast(self):
        self.tap_optional("Live Broadcast")
        wait_for_animation(self.driver, 2)
        return self

    def tap_donate(self):
        self.tap_optional("Donate")
        wait_for_animation(self.driver)
        return self

    def is_banner_visible(self):
        return any(self.is_visible(lbl, timeout=3) for lbl in _BANNER_LABELS)
