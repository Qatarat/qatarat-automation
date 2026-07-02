from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text, edit_text_xpath


class MosquePage(BasePage):

    def search_mosque(self, name):
        self.tap_optional("Search")
        self.tap_optional("Search Mosques")
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, edit_text_xpath())
            if els:
                els[0].clear()
                els[0].send_keys(name)
            elif name:
                self.input_text("Search", name)
        except Exception:
            if name:
                self.input_text("Search", name)
        wait_for_animation(self.driver)
        return self

    def open_mosque_profile(self, name):
        scroll_to_text(self.driver, name, max_scrolls=6)
        self.tap_optional(name)
        wait_for_animation(self.driver)
        return self

    def get_mosque_name(self):
        for label in ("Mosque Name", "mosque", "Masjid"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def get_donation_count(self):
        for label in ("Donations", "Total Donations", "Donors"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def scroll_to_about_section(self):
        scroll_to_text(self.driver, "About", max_scrolls=8)
        return self

    def get_mosque_description(self):
        for label in ("About", "Description", "Overview"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def tap_donate_button(self):
        self.tap_optional("Donate")
        self.tap_optional("Donate Now")
        wait_for_animation(self.driver)
        return self

    def get_search_results_count(self):
        try:
            results = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Mosque") or contains(@text,"Mosque")]',
            )
            return len(results)
        except Exception:
            return 0
