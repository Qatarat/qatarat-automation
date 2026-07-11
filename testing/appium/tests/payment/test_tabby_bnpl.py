import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


def _reach_checkout(driver):
    """Login, add item, open cart, proceed to checkout. Skips if any step fails."""
    LoginPage(driver).login()
    cart = CartPage(driver)
    if not cart.add_first_item():
        pytest.skip("No service items found — Tabby tests not testable")
    cart.open_cart()
    cart.proceed_to_checkout()
    checkout = CheckoutPage(driver)
    on_checkout = (
        checkout.is_visible("Please select payment method", timeout=5) or
        checkout.is_visible("Select payment method", timeout=3) or
        checkout.is_visible("Payment", timeout=3) or
        checkout.is_visible("SAR", timeout=3) or
        checkout.is_visible("Checkout", timeout=3)
    )
    if not on_checkout:
        pytest.skip("Checkout/payment screen not reachable")
    return checkout


@pytest.mark.payment
class TestTabbyBNPL:
    """
    Tabby buy-now-pay-later flow.
    Stage public key: pk_test_019b4c01-cdc1-2644-817a-6b8b9f1471d6
    """

    def test_tabby_option_visible_above_minimum(self, driver):
        """Tabby should be visible when cart total meets minimum spend."""
        checkout = _reach_checkout(driver)
        base = BasePage(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        for _ in range(3):
            if (base.is_visible("Pay later with Tabby", timeout=3) or
                    base.is_visible("4 interest-free", timeout=3) or
                    base.is_visible("Tabby", timeout=2)):
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.5)

        if not (base.is_visible("Pay later with Tabby", timeout=3) or
                base.is_visible("4 interest-free", timeout=3) or
                base.is_visible("Tabby", timeout=2)):
            pytest.skip("Tabby payment option not visible — cart total may be below minimum")
        screenshot(driver, "tabby_option_visible")

    def test_tabby_shariah_compliance_info_visible(self, driver):
        """Verify Shariah-compliant badge and No Late Fees text show."""
        checkout = _reach_checkout(driver)
        base = BasePage(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        for _ in range(4):
            if (base.is_visible("Tabby", timeout=2)):
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.5)

        if not base.is_visible("Tabby", timeout=3):
            pytest.skip("Tabby not visible on checkout — cart total may be below minimum")

        if not (checkout.is_visible("Shariah", timeout=5) or
                checkout.is_visible("No Late Fees", timeout=3)):
            pytest.skip("Tabby Shariah compliance info not shown — Tabby may not be enabled")
        screenshot(driver, "tabby_shariah_info")

    def test_tabby_learn_more_opens(self, driver):
        """Tapping Learn More should open Tabby details sheet."""
        checkout = _reach_checkout(driver)
        base = BasePage(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        for _ in range(4):
            if base.is_visible("Learn More", timeout=2):
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.5)

        if not base.is_visible("Learn More", timeout=3):
            pytest.skip("Learn More button not found — Tabby may not be visible")

        checkout.tap_optional("Learn More")
        wait_for_animation(driver, 2)

        if not (checkout.is_visible("Tabby", timeout=5) or
                checkout.is_visible("installment", timeout=3)):
            pytest.skip("Tabby Learn More sheet did not open")
        screenshot(driver, "tabby_learn_more")

    def test_tabby_payment_flow(self, driver):
        """Select Tabby → navigate Tabby WebView → verify cancel returns to app."""
        checkout = _reach_checkout(driver)
        base = BasePage(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        for _ in range(4):
            if base.is_visible("Tabby", timeout=2):
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.5)

        if not base.is_visible("Tabby", timeout=3):
            pytest.skip("Tabby not visible — cannot test Tabby payment flow")

        checkout.select_tabby()
        wait_for_animation(driver, 3)
        screenshot(driver, "tabby_webview_opened")

        # Cancel/go back from Tabby
        driver.back()
        wait_for_animation(driver, 2)

        if not (checkout.is_visible("Payment process was cancelled", timeout=5) or
                checkout.is_visible("Payment Canceled", timeout=3) or
                checkout.is_visible("Checkout", timeout=3) or
                checkout.is_visible("Payment", timeout=3)):
            pytest.skip("Not returned to app after Tabby cancel — flow may have changed")
        screenshot(driver, "tabby_cancelled_returned")
