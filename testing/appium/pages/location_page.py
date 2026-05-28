from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation

_MAP_LABELS = ["Map", "Location", "Select Location", "الموقع", "خريطة"]
_CONFIRM_LABELS = ["Confirm Location", "Set Location", "Use This Location", "تأكيد الموقع"]


class LocationPage(BasePage):

    def is_on_map_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _MAP_LABELS)

    def navigate_to_map(self):
        if self.is_on_map_screen(timeout=3):
            return self
        for label in ["Map", "Location", "Select Location"]:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def confirm_location(self):
        for label in _CONFIRM_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def search_location(self, query):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
            if els:
                els[0].click()
                els[0].clear()
                els[0].send_keys(query)
        except Exception:
            self.input_text("Search", query)
        wait_for_animation(self.driver)
        return self

    def allow_location_permission(self):
        for label in ["While using the app", "Allow", "Only this time"]:
            els = self.driver.find_elements(
                AppiumBy.XPATH, f'//*[@text="{label}"]'
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        return self

    def deny_location_permission(self):
        for label in ["Deny", "Don't allow"]:
            els = self.driver.find_elements(
                AppiumBy.XPATH, f'//*[@text="{label}"]'
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        return self

    def is_location_selected(self):
        return any(self.is_visible(lbl, timeout=5) for lbl in _CONFIRM_LABELS + _MAP_LABELS)
