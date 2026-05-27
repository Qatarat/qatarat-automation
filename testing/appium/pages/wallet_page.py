from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text


class WalletPage(BasePage):

    def navigate_to_wallet(self):
        self.tap_optional("Wallet")
        self.tap_optional("My Wallet")
        wait_for_animation(self.driver)
        return self

    def get_wallet_balance(self):
        for label in ("Balance", "SAR", "Wallet Balance", "Available"):
            if self.is_visible(label, timeout=5):
                return label
        return None

    def tap_topup_button(self):
        self.tap_optional("Top Up")
        self.tap_optional("Add Funds")
        self.tap_optional("Recharge")
        wait_for_animation(self.driver)
        return self

    def enter_topup_amount(self, amount):
        try:
            el = self.driver.find_element(AppiumBy.XPATH, "//android.widget.EditText")
            el.clear()
            el.send_keys(str(amount))
        except Exception:
            self.input_text("Amount", str(amount))
        wait_for_animation(self.driver, 0.5)
        return self

    def confirm_topup(self):
        self.tap_optional("Confirm")
        self.tap_optional("Proceed")
        self.tap_optional("Pay")
        wait_for_animation(self.driver, 2)
        return self

    def get_transaction_history(self):
        scroll_to_text(self.driver, "Transactions", max_scrolls=5)
        self.tap_optional("Transactions")
        self.tap_optional("Transaction History")
        wait_for_animation(self.driver)
        return self

    def get_transaction_count(self):
        try:
            rows = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Transaction") or contains(@text,"SAR")]',
            )
            return len(rows)
        except Exception:
            return 0
