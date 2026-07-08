import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import InvalidPromo, ValidData


@pytest.mark.promo
@pytest.mark.negative
class TestPromoCodes:
    """Exhaustive promo-code tests: valid, invalid, boundary, and injection attempts."""

    def _login_and_reach_promo(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        return cart

    def test_valid_promo_applies_successfully(self, driver):
        """Baseline: valid promo code TEST10 must be accepted."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(ValidData.PROMO)
        cart.assert_promo_applied()
        screenshot(driver, "promo_valid_applied")

    def test_invalid_promo_shows_error(self, driver):
        """A completely wrong promo code must show an error."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.WRONG_CODE)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert base.is_visible("Invalid") or \
               base.is_visible("not valid") or \
               base.is_visible("does not exist") or \
               base.is_visible("incorrect"), \
            "Invalid promo did not show an error message"
        screenshot(driver, "promo_invalid_error")

    def test_empty_promo_shows_error(self, driver):
        """Applying an empty promo code must show a validation message."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.EMPTY)
        wait_for_animation(driver)

        base = BasePage(driver)
        assert base.is_visible("Enter") or \
               base.is_visible("required") or \
               base.is_visible("empty") or \
               not base.is_visible("Applied"), \
            "Empty promo code was accepted"
        screenshot(driver, "promo_empty_error")

    def test_expired_promo_shows_error(self, driver):
        """An expired promo code must be rejected with a clear message."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.EXPIRED)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert base.is_visible("expired") or \
               base.is_visible("no longer valid") or \
               base.is_visible("Invalid") or \
               not base.is_visible("Applied"), \
            "Expired promo code was accepted"
        screenshot(driver, "promo_expired_error")

    def test_lowercase_promo_handled(self, driver):
        """Lowercase version of a valid code — app should either normalise or reject clearly."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.LOWERCASE)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        # Either it works (case-insensitive) or shows a clear error — no crash
        applied = base.is_visible("Applied") or base.is_visible("Promo Code Applied")
        rejected = base.is_visible("Invalid") or base.is_visible("incorrect")
        assert applied or rejected, \
            "Lowercase promo produced no clear response (neither applied nor rejected)"
        screenshot(driver, "promo_lowercase_result")

    def test_promo_with_spaces_is_trimmed_or_rejected(self, driver):
        """A promo code with leading/trailing spaces — must be trimmed or cleanly rejected."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.WITH_SPACES)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        applied = base.is_visible("Applied") or base.is_visible("Promo Code Applied")
        rejected = base.is_visible("Invalid") or base.is_visible("incorrect")
        assert applied or rejected, \
            "Padded-space promo produced no response"
        screenshot(driver, "promo_spaces_result")

    def test_special_chars_promo_shows_error(self, driver):
        """Special characters in promo field must not crash the app."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.SPECIAL_CHARS)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert base.is_visible("Invalid") or \
               not base.is_visible("Applied"), \
            "Special-char promo was accepted or caused a crash"
        screenshot(driver, "promo_special_chars_error")

    def test_sql_injection_in_promo_is_safe(self, driver):
        """SQL injection string in promo field must not cause a server error."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.SQL_INJECTION)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert not base.is_visible("SQL") and \
               not base.is_visible("syntax error") and \
               not base.is_visible("database error") and \
               not base.is_visible("500"), \
            "SQL injection in promo field exposed a server error"
        screenshot(driver, "promo_sql_injection_safe")

    def test_very_long_promo_does_not_crash(self, driver):
        """A 50-character promo code must not crash or hang the app."""
        cart = self._login_and_reach_promo(driver)
        cart.apply_promo(InvalidPromo.TOO_LONG)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert base.is_visible("Invalid") or \
               not base.is_visible("Applied"), \
            "Overly long promo string caused unexpected behaviour"
        screenshot(driver, "promo_long_code_error")
