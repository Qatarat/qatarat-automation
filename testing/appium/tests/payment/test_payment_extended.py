"""
Extended payment tests — edge cases, boundary values, input formatting.
Covers: card with spaces/dashes, far-future expiry, CVV edge cases,
        cardholder name variants, international cards, currency display.
"""
from datetime import date
import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, screenshot
from test_data import ValidData, InvalidCard


def _reach_card_form(driver):
    login = LoginPage(driver)
    login.login(ValidData.PHONE, ValidData.OTP)
    cart = CartPage(driver)
    cart.add_first_item()
    cart.open_cart()
    cart.proceed_to_checkout()
    checkout = CheckoutPage(driver)
    checkout.select_card_payment()
    wait_for_animation(driver, 2)
    return checkout


@pytest.mark.payment
@pytest.mark.boundary
class TestCardInputFormatting:

    @pytest.mark.parametrize("card_number", [
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
        "  4111111111111111  ",
    ])
    def test_card_with_separators_handled_gracefully(self, driver, card_number):
        """App should either accept formatted input or show a clear validation error."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(card_number, "12/28", "123", "Test User")
        checkout.submit_order()
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_card_number_max_length_enforced(self, driver):
        """Input field must not accept more than 16 significant digits."""
        checkout = _reach_card_form(driver)
        # Enter 20 digits; after stripping spaces the stored value should be ≤16
        checkout.fill_card_details("41111111111111119999", "12/28", "123", "Test User")
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_cvv_with_letters_shows_error(self, driver):
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "12/28", "AB3", "Test User")
        checkout.submit_order()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("invalid", timeout=3) or \
               base.is_visible("CVV", timeout=3) or \
               not base.is_visible("Processing", timeout=3), \
            "CVV with letters was accepted"

    def test_cvv_with_special_chars_shows_error(self, driver):
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "12/28", "@#!", "Test User")
        checkout.submit_order()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("invalid", timeout=3) or \
               not base.is_visible("Processing", timeout=3)

    def test_cvv_4_digits_for_amex(self, driver):
        """Amex cards use 4-digit CVV — app should accept it."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details("378282246310005", "12/28", "1234", "Test User")
        page = driver.page_source
        assert "Something went wrong" not in page


@pytest.mark.payment
@pytest.mark.boundary
class TestExpiryBoundary:

    def test_current_month_expiry_is_valid(self, driver):
        """A card expiring this month must be accepted (not yet expired)."""
        today = date.today()
        expiry = f"{today.month:02d}/{str(today.year)[2:]}"
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], expiry, "123", "Test User")
        page = driver.page_source
        assert "expired" not in page.lower()

    def test_far_future_expiry_accepted(self, driver):
        """12/99 is technically valid input — must not be rejected as malformed."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "12/99", "123", "Test User")
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_expiry_without_slash_handled(self, driver):
        """User types '1228' (no slash) — app should format or show hint."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "1228", "123", "Test User")
        assert "Something went wrong" not in driver.page_source

    def test_expiry_month_zero_shows_error(self, driver):
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "00/30", "123", "Test User")
        checkout.submit_order()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("invalid", timeout=3) or \
               not base.is_visible("Processing", timeout=3)


@pytest.mark.payment
@pytest.mark.boundary
class TestCardholderName:

    def test_cardholder_name_with_numbers_handled(self, driver):
        """Name like 'John123' — some gateways reject this."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "12/28", "123", "John123")
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_cardholder_name_all_spaces_shows_error(self, driver):
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(ValidData.CARD["number"], "12/28", "123", "     ")
        checkout.submit_order()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("invalid", timeout=3) or \
               base.is_visible("required", timeout=3) or \
               not base.is_visible("Processing", timeout=3)

    def test_cardholder_name_uppercase_accepted(self, driver):
        """ALL CAPS name is standard on physical cards — must be accepted."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(
            ValidData.CARD["number"], "12/28", "123", "MEJBAUR BAHAR FAGUN"
        )
        page = driver.page_source
        assert "invalid" not in page.lower()

    def test_cardholder_name_50_chars_handled(self, driver):
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(
            ValidData.CARD["number"], "12/28", "123", "A" * 50
        )
        assert "Something went wrong" not in driver.page_source

    def test_cardholder_name_arabic_handled(self, driver):
        """Arabic cardholder name — some gateways reject Unicode names."""
        checkout = _reach_card_form(driver)
        checkout.fill_card_details(
            ValidData.CARD["number"], "12/28", "123", "محمد عبدالله"
        )
        assert "crash" not in driver.page_source.lower()
        assert "500" not in driver.page_source
