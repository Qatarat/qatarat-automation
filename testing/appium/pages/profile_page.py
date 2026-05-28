from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation


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
            els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
            if els:
                els[0].clear()
                els[0].send_keys(name)
        except Exception:
            self.input_text("Name", name)
        return self

    def enter_email(self, email):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
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
        for _ in range(6):
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[@content-desc="Logout" or @text="Logout" or '
                '@content-desc="Log out" or @text="Log out" or '
                '@content-desc="Sign out" or @text="Sign out"]',
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver)
                return self
            self.driver.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 600)
            wait_for_animation(self.driver, 0.5)
        self.tap_optional("Logout")
        self.tap_optional("Log out")
        self.tap_optional("Sign out")
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
