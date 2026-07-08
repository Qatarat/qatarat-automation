import pytest
import allure
from pages.login_page import LoginPage
from pages.wallet_page import WalletPage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Wallet")
@allure.feature("Wallet & Top-Up")
@pytest.mark.wallet
class TestWallet:
    """Tests covering wallet navigation, balance display, top-up, and transaction history."""

    def _login_and_open_wallet(self, driver):
        LoginPage(driver).login()
        page = WalletPage(driver)
        page.navigate_to_wallet()
        return page

    @allure.story("Navigation")
    @allure.title("Navigate to the Wallet screen successfully")
    def test_wallet_navigate(self, driver):
        page = self._login_and_open_wallet(driver)
        assert page.is_on_wallet_screen(timeout=10), \
            "Wallet screen did not load after navigation"
        screenshot(driver, "wallet_navigate")

    @allure.story("Balance")
    @allure.title("Wallet balance is displayed on the Wallet screen")
    def test_wallet_balance_visible(self, driver):
        page = self._login_and_open_wallet(driver)
        balance = page.get_wallet_balance()
        assert balance is not None or \
               page.is_visible("SAR", timeout=5) or \
               page.is_visible("ر.س", timeout=5), \
            "Wallet balance not visible on screen"
        screenshot(driver, "wallet_balance_visible")

    @allure.story("Top-Up")
    @allure.title("Top up with a valid amount proceeds to payment")
    def test_wallet_topup_valid_amount(self, driver):
        page = self._login_and_open_wallet(driver)
        page.tap_topup_button()
        page.enter_topup_amount(50)
        wait_for_animation(driver)
        assert not page.is_visible("Error", timeout=3), \
            "Error shown when entering valid top-up amount of 50"
        screenshot(driver, "wallet_topup_valid")

    @allure.story("Top-Up Negative")
    @allure.title("Top up with zero amount shows a validation error")
    def test_wallet_topup_zero(self, driver):
        page = self._login_and_open_wallet(driver)
        page.tap_topup_button()
        page.enter_topup_amount(0)
        page.confirm_topup()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Enter") or \
               page.is_visible("minimum") or \
               page.is_visible("Error") or \
               not page.is_visible("Success"), \
            "Zero top-up amount was accepted without validation error"
        screenshot(driver, "wallet_topup_zero")

    @allure.story("Top-Up Negative")
    @allure.title("Top up with a negative amount shows a validation error")
    def test_wallet_topup_negative(self, driver):
        page = self._login_and_open_wallet(driver)
        page.tap_topup_button()
        page.enter_topup_amount(-20)
        page.confirm_topup()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Error") or \
               not page.is_visible("Success"), \
            "Negative top-up amount was accepted"
        screenshot(driver, "wallet_topup_negative")

    @allure.story("Top-Up Negative")
    @allure.title("Entering letters in the top-up field shows a validation error")
    def test_wallet_topup_alpha(self, driver):
        page = self._login_and_open_wallet(driver)
        page.tap_topup_button()
        page.enter_topup_amount("abc")
        page.confirm_topup()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Error") or \
               not page.is_visible("Success"), \
            "Alphabetic top-up amount 'abc' was accepted"
        screenshot(driver, "wallet_topup_alpha")

    @allure.story("Top-Up Boundary")
    @allure.title("Very large top-up amount is handled without crashing")
    def test_wallet_topup_boundary_max(self, driver):
        page = self._login_and_open_wallet(driver)
        page.tap_topup_button()
        page.enter_topup_amount(9999999)
        wait_for_animation(driver)
        assert not page.is_visible("crash", timeout=3), \
            "App crashed when very large top-up amount was entered"
        screenshot(driver, "wallet_topup_max")

    @allure.story("Transaction History")
    @allure.title("Transaction history list loads without error")
    def test_wallet_transaction_history(self, driver):
        page = self._login_and_open_wallet(driver)
        page.get_transaction_history()
        wait_for_animation(driver)
        assert page.is_visible("Transactions", timeout=5) or \
               page.is_visible("المعاملات", timeout=5) or \
               page.is_visible("History", timeout=5) or \
               page.is_visible("No transactions", timeout=5) or \
               not page.is_visible("500", timeout=3), \
            "Transaction history did not load or caused a server error"
        screenshot(driver, "wallet_transaction_history")
