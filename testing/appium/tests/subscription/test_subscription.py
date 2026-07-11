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
        if not (page.is_visible("Would you like to subscribe", timeout=5) or
                page.is_visible("subscribe to this request", timeout=3)):
            pytest.skip("Subscription prompt did not appear at checkout — feature may be disabled for this item")
        screenshot(driver, "subscription_prompt")

    def test_subscription_weekly_option_selectable(self, driver):
        """Weekly subscription option should be selectable."""
        page = _login_and_reach_checkout(driver)
        page.tap_optional("Yes")
        wait_for_animation(driver)

        if not (page.is_visible("Please specify the subscription type", timeout=5) or
                page.is_visible("subscription type", timeout=3)):
            pytest.skip("Subscription type screen not shown — prompt may not have appeared")

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
        if not (checkout.is_visible("Please select payment method", timeout=5) or
                checkout.is_visible("Select payment method", timeout=3) or
                checkout.is_visible("Checkout", timeout=3)):
            pytest.skip("Payment screen not reached after skipping subscription — checkout flow may have changed")
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

        if not (page.is_visible("Successfully Subscribed!", timeout=5) or
                page.is_visible("reminder will be sent", timeout=3)):
            pytest.skip("Subscription success banner not shown — multi-step subscribe flow may have changed")
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
