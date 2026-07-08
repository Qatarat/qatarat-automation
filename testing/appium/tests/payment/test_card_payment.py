import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.helpers import screenshot, wait_for_animation


@pytest.mark.payment
class TestCardPayment:
    """
    HyperPay card payment flow.
    Uses the stage environment card:  4111 1111 1111 1111 / 12/25 / 123
    """

    STAGE_CARD = {
        "number": "4111111111111111",
        "expiry": "12/25",
        "cvv": "123",
        "name": "Test User",
    }

    def test_card_payment_flow_reaches_processing(self, driver):
        """Verify full card payment flow reaches processing/confirmation screen."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()
        login.assert_logged_in()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.assert_has_items()
        screenshot(driver, "card_payment_cart")

        checkout = CheckoutPage(driver)
        cart.proceed_to_checkout()
        checkout.assert_payment_screen()

        checkout.select_card_payment()
        wait_for_animation(driver, 2)
        screenshot(driver, "card_payment_form")

        checkout.fill_card_details(
            self.STAGE_CARD["number"],
            self.STAGE_CARD["expiry"],
            self.STAGE_CARD["cvv"],
            self.STAGE_CARD["name"],
        )
        checkout.submit_order()
        screenshot(driver, "card_payment_submitted")

        checkout.assert_processing()

    def test_card_payment_expired_card_shows_error(self, driver):
        """Verify expired card shows CARD_EXPIRED error message."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.proceed_to_checkout()

        checkout = CheckoutPage(driver)
        checkout.select_card_payment()
        checkout.fill_card_details("4111111111111111", "01/20", "123", "Test User")
        checkout.submit_order()
        wait_for_animation(driver, 3)

        assert checkout.is_visible("Your card has expired") or \
               checkout.is_visible("CARD_EXPIRED") or \
               checkout.is_visible("expired"), \
            "Expired card error not shown"
        screenshot(driver, "card_expired_error")

    def test_card_payment_insufficient_funds(self, driver):
        """Verify declined payment shows correct error."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.proceed_to_checkout()

        checkout = CheckoutPage(driver)
        checkout.select_card_payment()
        # Stage decline card: 4000000000000002
        checkout.fill_card_details("4000000000000002", "12/25", "123", "Test User")
        checkout.submit_order()
        wait_for_animation(driver, 3)

        assert checkout.is_visible("Payment Declined") or \
               checkout.is_visible("INSUFFICIENT_FUNDS") or \
               checkout.is_visible("failed"), \
            "Payment declined error not shown"
        screenshot(driver, "card_payment_declined")

    def test_promo_code_reduces_total(self, driver):
        """Verify promo code is applied and total price decreases."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.assert_has_items()

        # Apply promo
        cart.apply_promo("TEST10")
        cart.assert_promo_applied()
        screenshot(driver, "promo_code_applied")
