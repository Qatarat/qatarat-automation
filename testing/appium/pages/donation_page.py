from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text


class DonationPage(BasePage):

    def navigate_to_donations(self):
        self.tap_optional("Donate")
        self.tap_optional("Donations")
        wait_for_animation(self.driver)
        return self

    def select_mosque(self, name):
        scroll_to_text(self.driver, name, max_scrolls=8)
        self.tap_optional(name)
        wait_for_animation(self.driver)
        return self

    def enter_donation_amount(self, amount):
        self.tap_optional("Enter Amount")
        self.tap_optional("Amount")
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            el = self.driver.find_element(AppiumBy.XPATH, "//android.widget.EditText")
            el.clear()
            el.send_keys(str(amount))
        except Exception:
            self.input_text("Amount", str(amount))
        wait_for_animation(self.driver, 0.5)
        return self

    def select_payment_method(self, method):
        scroll_to_text(self.driver, method, max_scrolls=5)
        self.tap_optional(method)
        wait_for_animation(self.driver)
        return self

    def confirm_donation(self):
        self.tap_optional("Confirm")
        self.tap_optional("Donate Now")
        self.tap_optional("Proceed")
        wait_for_animation(self.driver, 2)
        return self

    def get_confirmation_message(self):
        for label in ("Thank you", "Donation Confirmed", "Success", "Jazakallah"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def navigate_to_zakat(self):
        self.tap_optional("Zakat")
        wait_for_animation(self.driver)
        return self

    def calculate_zakat(self, wealth_amount):
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
            if els:
                els[0].clear()
                els[0].send_keys(str(wealth_amount))
        except Exception:
            self.input_text("Wealth", str(wealth_amount))
        self.tap_optional("Calculate")
        wait_for_animation(self.driver)
        return self

    def navigate_to_sadaqah(self):
        self.tap_optional("Sadaqah")
        wait_for_animation(self.driver)
        return self
