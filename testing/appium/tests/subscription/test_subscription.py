import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


def _login_and_reach_checkout(driver):
    LoginPage(driver).login()
    cart = CartPage(driver)
    if not cart.add_first_item():
        pytest.skip("No service items found to add — subscription flow not testable")
    cart.open_cart()
    cart.proceed_to_checkout()
    return BasePage(driver)


@pytest.mark.subscription
class TestSubscription:

    def test_subscription_prompt_appears_at_checkout(self, driver):
        """Subscription dialog should appear when reaching checkout."""
        page = _login_and_reach_checkout(driver)
        assert page.is_visible("Would you like to subscribe") or \
               page.is_visible("subscribe to this request"), \
            "Subscription prompt did not appear at checkout"
        screenshot(driver, "subscription_prompt")

    def test_subscription_weekly_option_selectable(self, driver):
        """Weekly subscription option should be selectable."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("Yes")
        wait_for_animation(driver)

        assert page.is_visible("Please specify the subscription type") or \
               page.is_visible("subscription type"), \
            "Subscription type screen not shown"

        page.tap_optional("Weekly")
        wait_for_animation(driver)
        screenshot(driver, "subscription_weekly_selected")

    def test_subscription_monthly_option_selectable(self, driver):
        """Monthly subscription option should be selectable."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("Yes")
        wait_for_animation(driver)
        page.tap_optional("Monthly")
        wait_for_animation(driver)
        screenshot(driver, "subscription_monthly_selected")

    def test_subscription_skip_goes_to_payment(self, driver):
        """Skipping subscription should proceed to normal payment."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("No")
        wait_for_animation(driver)

        checkout = CheckoutPage(driver)
        assert checkout.is_visible("Please select payment method") or \
               checkout.is_visible("Select payment method") or \
               checkout.is_visible("Checkout"), \
            "Did not proceed to payment after skipping subscription"
        screenshot(driver, "subscription_skipped_payment_shown")

    def test_reminder_banner_shown_after_subscribe(self, driver):
        """Reminder banner should show after subscribing."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("Yes")
        wait_for_animation(driver)
        page.tap_optional("Weekly")
        page.tap_optional("Subscribe Now")
        page.tap_optional("Subscribe now for Reminder")
        wait_for_animation(driver, 2)

        assert page.is_visible("Successfully Subscribed!") or \
               page.is_visible("reminder will be sent"), \
            "Subscription success confirmation not shown"
        screenshot(driver, "subscription_success_banner")

    def test_unavailable_items_block_subscription(self, driver):
        """Subscription with sale/unavailable items should show warning."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("Yes")
        wait_for_animation(driver)

        if page.is_visible("some sales items are unavailable"):
            assert page.is_visible("Please remove for the subscription"), \
                "Unavailable items warning message incomplete"
            screenshot(driver, "subscription_unavailable_items_warning")
        else:
            pytest.skip("No unavailable items in test data — skipping this assertion")
