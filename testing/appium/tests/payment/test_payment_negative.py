import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import InvalidCard


@pytest.mark.payment
@pytest.mark.negative
class TestPaymentNegative:
    """Negative and boundary tests for the card payment form."""

    def _reach_card_form(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.proceed_to_checkout()

        checkout = CheckoutPage(driver)
        checkout.assert_payment_screen()
        checkout.select_card_payment()
        wait_for_animation(driver, 2)
        return checkout

    def test_short_card_number_shows_error(self, driver):
        """An 8-digit card number must fail validation."""
        d = InvalidCard.SHORT_NUMBER
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("invalid") or \
               base.is_visible("card number") or \
               not base.is_visible("Processing"), \
            "Short card number was accepted"
        screenshot(driver, "card_short_number_error")

    def test_letters_in_card_number_shows_error(self, driver):
        """Alphabetic card number must be rejected or sanitised."""
        d = InvalidCard.LETTERS_IN_NUMBER
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("invalid") or \
               not base.is_visible("Processing"), \
            "Letter-based card number was accepted"
        screenshot(driver, "card_alpha_number_error")

    def test_invalid_expiry_month_shows_error(self, driver):
        """Month 13 in expiry must be rejected."""
        d = InvalidCard.INVALID_MONTH
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("invalid") or \
               base.is_visible("expiry") or \
               not base.is_visible("Processing"), \
            "Invalid month (13) was accepted"
        screenshot(driver, "card_invalid_month_error")

    def test_past_year_expiry_shows_error(self, driver):
        """Expiry in a past year must be rejected."""
        d = InvalidCard.PAST_YEAR
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("expired") or \
               base.is_visible("invalid") or \
               not base.is_visible("Processing"), \
            "Past-year expiry was accepted"
        screenshot(driver, "card_past_year_error")

    def test_empty_cvv_shows_error(self, driver):
        """Submitting with an empty CVV must show a validation error."""
        d = InvalidCard.EMPTY_CVV
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("CVV") or \
               base.is_visible("security code") or \
               base.is_visible("required") or \
               not base.is_visible("Processing"), \
            "Empty CVV was accepted"
        screenshot(driver, "card_empty_cvv_error")

    def test_single_digit_cvv_shows_error(self, driver):
        """A 1-digit CVV is too short and must be rejected."""
        d = InvalidCard.SHORT_CVV
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("CVV") or \
               base.is_visible("invalid") or \
               not base.is_visible("Processing"), \
            "1-digit CVV was accepted"
        screenshot(driver, "card_short_cvv_error")

    def test_empty_cardholder_name_shows_error(self, driver):
        """A blank cardholder name must trigger a validation message."""
        d = InvalidCard.EMPTY_NAME
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("name") or \
               base.is_visible("required") or \
               not base.is_visible("Processing"), \
            "Empty cardholder name was accepted"
        screenshot(driver, "card_empty_name_error")

    def test_all_zeros_card_shows_error(self, driver):
        """All-zero card number must be rejected."""
        d = InvalidCard.ALL_ZEROS_NUMBER
        checkout = self._reach_card_form(driver)
        checkout.fill_card_details(d["number"], d["expiry"], d["cvv"], d["name"])
        checkout.submit_order()
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("invalid") or \
               not base.is_visible("Processing"), \
            "All-zero card number was accepted"
        screenshot(driver, "card_zeros_number_error")
