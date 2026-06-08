from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, text_field_xpath, find_elements_by_label


class ProfilePage(BasePage):

    def navigate_to_profile(self):
        self.tap_optional("Profile")
        self.tap_optional("Account")
        wait_for_animation(self.driver)
        return self

    def tap_edit_profile(self):
        self.tap_optional("Edit Profile")
        self.tap_optional("Edit")
        wait_for_animation(self.driver)
        return self

    def enter_name(self, name):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            if els:
                els[0].clear()
                els[0].send_keys(name)
        except Exception:
            self.input_text("Name", name)
        return self

    def enter_email(self, email):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            for el in els:
                try:
                    content = el.get_attribute("text") or ""
                    if "@" in content or "email" in (el.get_attribute("hint") or "").lower():
                        el.clear()
                        el.send_keys(email)
                        return self
                except Exception:
                    continue
            if len(els) >= 2:
                els[1].clear()
                els[1].send_keys(email)
        except Exception:
            self.input_text("Email", email)
        return self

    def save_profile(self):
        self.tap_optional("Save")
        self.tap_optional("Update")
        wait_for_animation(self.driver, 2)
        return self

    def get_profile_name(self):
        for label in ("Profile", "Account", "My Profile"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def tap_logout(self):
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        logout_labels = ["Logout", "Log out", "Sign out"]
        for _ in range(6):
            els = []
            for label in logout_labels:
                els = find_elements_by_label(self.driver, label)
                if els:
                    break
            if els:
                els[0].click()
                wait_for_animation(self.driver)
                return self
            self.driver.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 600)
            wait_for_animation(self.driver, 0.5)
        for label in logout_labels:
            self.tap_optional(label)
        wait_for_animation(self.driver)
        return self

    def confirm_logout(self):
        self.tap_optional("Yes")
        self.tap_optional("Confirm")
        self.tap_optional("Logout")
        wait_for_animation(self.driver, 2)
        return self

    def navigate_to_settings(self):
        self.tap_optional("Settings")
        wait_for_animation(self.driver)
        return self

    def toggle_language(self):
        self.tap_optional("Language")
        self.tap_optional("Arabic")
        self.tap_optional("English")
        wait_for_animation(self.driver)
        return self
