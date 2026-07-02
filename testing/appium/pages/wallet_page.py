from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text, edit_text_xpath

_WALLET_NAV_LABELS  = ["Wallet", "My Wallet", "محفظة", "محفظتي"]
_WALLET_SCREEN_LABELS = ["Wallet", "Balance", "Top Up", "محفظة", "الرصيد", "رصيدي", "إضافة رصيد", "شحن"]
_BALANCE_LABELS     = ["Balance", "SAR", "Wallet Balance", "Available", "الرصيد", "رصيدي", "ر.س"]
_TOPUP_LABELS       = ["Top Up", "Add Funds", "Recharge", "إضافة رصيد", "شحن", "Add Money"]
_TXHISTORY_LABELS   = ["Transactions", "Transaction History", "History", "المعاملات", "سجل المعاملات"]


class WalletPage(BasePage):

    def navigate_to_wallet(self):
        # If already on wallet screen, done
        if self.is_on_wallet_screen(timeout=3):
            return self
        # Try direct tap (if "Wallet" is a bottom-nav item or already visible)
        for label in _WALLET_NAV_LABELS:
            self.tap_optional(label, timeout=2)
        if self.is_on_wallet_screen(timeout=3):
            return self
        # Wallet lives under the Profile tab on this app
        self.tap_optional("Profile", timeout=5)
        wait_for_animation(self.driver, 1.5)
        for label in _WALLET_NAV_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def is_on_wallet_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _WALLET_SCREEN_LABELS)

    def get_wallet_balance(self):
        for label in _BALANCE_LABELS:
            if self.is_visible(label, timeout=5):
                return label
        return None

    def tap_topup_button(self):
        for label in _TOPUP_LABELS:
            self.tap_optional(label)
        wait_for_animation(self.driver)
        return self

    def enter_topup_amount(self, amount):
        try:
            el = self.driver.find_element(AppiumBy.XPATH, edit_text_xpath())
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
        for label in _TXHISTORY_LABELS:
            try:
                scroll_to_text(self.driver, label, max_scrolls=5)
                self.tap_optional(label)
                break
            except Exception:
                pass
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
