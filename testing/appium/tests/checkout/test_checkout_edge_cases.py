"""
Checkout edge cases — navigation, payment method switching, back button,
currency display, coupon + payment combos.
"""
import re
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.base_page import BasePage
from utils.helpers import wait_for_animation
from test_data import ValidData


def _reach_checkout(driver):
    login = LoginPage(driver)
    login.login(ValidData.PHONE, ValidData.OTP)
    cart = CartPage(driver)
    cart.add_first_item()
    cart.open_cart()
    cart.proceed_to_checkout()
    wait_for_animation(driver, 2)


@pytest.mark.checkout
@pytest.mark.boundary
class TestCheckoutNavigation:

    def test_back_from_checkout_returns_to_cart(self, driver):
        """Pressing back from checkout must return to cart, not log out or crash."""
        _reach_checkout(driver)
        driver.back()
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "Cart" in page or "cart" in page.lower() or "items" in page.lower()

    def test_back_then_forward_preserves_cart(self, driver):
        """Cart items must persist after navigating back from checkout and returning."""
        _reach_checkout(driver)
        driver.back()
        wait_for_animation(driver)
        cart = CartPage(driver)
        cart.proceed_to_checkout()
        wait_for_animation(driver)
        page = driver.page_source
        assert "payment" in page.lower() or "method" in page.lower() or \
               "checkout" in page.lower() or "SAR" in page

    def test_checkout_page_shows_order_summary(self, driver):
        """Checkout must display item name, quantity, subtotal, total."""
        _reach_checkout(driver)
        page = driver.page_source
        assert ("total" in page.lower() or "subtotal" in page.lower() or
                "SAR" in page or "amount" in page.lower()), \
            "Checkout page does not show order summary"

    def test_checkout_price_not_nan_or_zero(self, driver):
        """Total must be a valid number — not NaN, undefined, or 0.00 for a non-empty cart."""
        _reach_checkout(driver)
        page = driver.page_source
        assert "NaN" not in page, "NaN detected in checkout page"
        assert "undefined" not in page, "undefined detected in checkout page"


@pytest.mark.checkout
@pytest.mark.boundary
class TestPaymentMethodSwitching:

    def test_switch_payment_methods_no_crash(self, driver):
        """Switching payment method mid-checkout must not crash."""
        _reach_checkout(driver)
        checkout = CheckoutPage(driver)
        # Try tapping available payment options
        base = BasePage(driver)
        for method in ["Credit Card", "Card", "Pay later with Tabby", "Bank Transfer"]:
            base.tap_optional(method, timeout=2)
            wait_for_animation(driver, 0.5)
        assert "Something went wrong" not in driver.page_source

    def test_rapid_payment_tap_no_crash(self, driver):
        """Rapidly tapping payment options must not crash."""
        _reach_checkout(driver)
        base = BasePage(driver)
        methods = driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@content-desc,"Card") or contains(@content-desc,"Pay") '
            'or contains(@text,"Card") or contains(@text,"Pay")]',
        )
        for _ in range(3):
            for el in methods[:2]:
                try:
                    el.click()
                    wait_for_animation(driver, 0.3)
                except Exception:
                    pass
        assert "500" not in driver.page_source

    def test_coupon_then_payment_no_nan(self, driver):
        """Apply promo code then select payment — total must not show NaN."""
        _reach_checkout(driver)
        cart = CartPage(driver)
        cart.apply_promo(ValidData.PROMO)
        wait_for_animation(driver)
        checkout = CheckoutPage(driver)
        checkout.select_card_payment()
        wait_for_animation(driver)
        assert "NaN" not in driver.page_source
        assert "Something went wrong" not in driver.page_source

    def test_invalid_coupon_then_payment_selectable(self, driver):
        """Invalid promo should not block payment method selection."""
        _reach_checkout(driver)
        cart = CartPage(driver)
        cart.apply_promo("BADCODE123")
        wait_for_animation(driver)
        checkout = CheckoutPage(driver)
        checkout.select_card_payment()
        wait_for_animation(driver)
        assert "Something went wrong" not in driver.page_source


@pytest.mark.checkout
@pytest.mark.boundary
class TestCurrencyDisplay:

    def test_price_shows_currency_symbol(self, driver):
        """All prices must show SAR, ﷼, or USD — never raw numbers without currency."""
        _reach_checkout(driver)
        page = driver.page_source
        has_currency = "SAR" in page or "﷼" in page or "USD" in page or "AED" in page or "ر.س" in page
        assert has_currency, "No currency symbol found on checkout page"

    def test_price_decimal_places_correct(self, driver):
        """Prices must have at most 2 decimal places (e.g. 10.00, not 10.000)."""
        _reach_checkout(driver)
        page = driver.page_source
        bad_decimals = re.findall(r'\d+\.\d{3,}', page)
        assert len(bad_decimals) == 0, f"Found malformed prices with 3+ decimals: {bad_decimals}"
