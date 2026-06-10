from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import (
    wait_for_animation,
    text_field_xpath,
    find_elements_by_label,
    find_by_text,
    clear_and_type,
    is_ios,
)


class ProfilePage(BasePage):

    # iOS tab bar labels vary by locale and build variant — check all
    _PROFILE_TAB_LABELS = [
        "Profile", "Account", "Me", "My Profile",
        "الملف الشخصي", "حساب", "أنا",  # Arabic equivalents
    ]

    _LOGOUT_LABELS = [
        "Logout", "Log out", "Sign out",
        "تسجيل الخروج", "خروج",          # Arabic
    ]

    _CONFIRM_LOGOUT_LABELS = [
        "Yes", "Confirm", "Logout", "Log out", "OK",
        "تأكيد", "نعم", "موافق",          # Arabic
    ]

    def navigate_to_profile(self):
        if is_ios():
            # iOS: find first visible label from the extended set (includes Arabic variants)
            for label in self._PROFILE_TAB_LABELS:
                if self.is_visible(label, timeout=2):
                    self.tap_optional(label, timeout=3)
                    wait_for_animation(self.driver, 1)
                    return self
            # None quickly visible — fall back to trying all labels
            for label in self._PROFILE_TAB_LABELS:
                self.tap_optional(label, timeout=3)
        else:
            # Android: tap Profile tab then the Account sub-section (original behaviour)
            self.tap_optional("Profile")
            self.tap_optional("Account")
        wait_for_animation(self.driver)
        return self

    def tap_edit_profile(self):
        self.tap_optional("Edit Profile")
        self.tap_optional("Edit")
        wait_for_animation(self.driver, 1.5)
        return self

    def enter_name(self, name):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            if els:
                clear_and_type(self.driver, els[0], name)
                return self
        except Exception:
            pass
        # Fallback: locate field by placeholder label
        for placeholder in ("Name", "Full Name", "الاسم"):
            try:
                self.input_text(placeholder, name)
                return self
            except Exception:
                continue
        return self

    def enter_email(self, email):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            for el in els:
                try:
                    content = el.get_attribute("value") or el.get_attribute("text") or ""
                    hint = (
                        el.get_attribute("hint")
                        or el.get_attribute("label")
                        or el.get_attribute("name")
                        or ""
                    )
                    if "@" in content or "email" in hint.lower() or "Email" in hint:
                        clear_and_type(self.driver, el, email)
                        return self
                except Exception:
                    continue
            if len(els) >= 2:
                clear_and_type(self.driver, els[1], email)
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
        # Scroll down up to 8 times looking for logout button
        for _ in range(8):
            for label in self._LOGOUT_LABELS:
                els = find_elements_by_label(self.driver, label)
                if els:
                    els[0].click()
                    wait_for_animation(self.driver)
                    return self
            # Use platform-safe swipe coordinates
            if is_ios():
                self.driver.swipe(w // 2, int(h * 0.65), w // 2, int(h * 0.35), 700)
            else:
                self.driver.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 600)
            wait_for_animation(self.driver, 0.5)
        wait_for_animation(self.driver)
        return self

    def confirm_logout(self):
        # Brief pause so the confirmation dialog finishes its opening animation
        wait_for_animation(self.driver, 0.5)
        # Use find_by_text (has timeout) — not find_elements_by_label (instant).
        # The dialog may not have rendered yet; instant lookup returns [] and skips it.
        for label in self._CONFIRM_LOGOUT_LABELS:
            try:
                el = find_by_text(self.driver, label, timeout=3)
                el.click()
                wait_for_animation(self.driver, 2)
                return self
            except Exception:
                continue
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
