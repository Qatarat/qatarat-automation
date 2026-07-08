import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


@pytest.mark.subscription
@pytest.mark.negative
class TestSubscriptionBoundary:
    """Edge-case and boundary tests for subscription flows."""

    def _login_and_reach_subscription_prompt(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        cart = CartPage(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.proceed_to_checkout()
        return BasePage(driver)

    def test_skipping_subscription_reaches_payment(self, driver):
        """Tapping 'No' at subscription prompt must go to payment screen, not error."""
        base = self._login_and_reach_subscription_prompt(driver)
        base.tap_optional("No")
        wait_for_animation(driver, 2)

        assert base.is_visible("Please select payment method") or \
               base.is_visible("Select payment method") or \
               base.is_visible("Checkout"), \
            "Declining subscription did not reach payment screen"
        screenshot(driver, "subscription_skip_to_payment")

    def test_weekly_then_back_resets_selection(self, driver):
        """Selecting Weekly then pressing back must not auto-commit the subscription."""
        base = self._login_and_reach_subscription_prompt(driver)
        base.tap_optional("Yes")
        wait_for_animation(driver)
        base.tap_optional("Weekly")
        wait_for_animation(driver)
        base.tap_optional("Back")
        wait_for_animation(driver)

        # Should be back at checkout or subscription prompt, not subscribed
        assert not base.is_visible("Successfully Subscribed"), \
            "Pressing Back after selecting Weekly still subscribed the user"
        screenshot(driver, "subscription_back_resets")

    def test_subscription_prompt_has_both_options(self, driver):
        """Subscription prompt must show both Yes and No options."""
        base = self._login_and_reach_subscription_prompt(driver)

        assert base.is_visible("Yes") or base.is_visible("Subscribe"), \
            "'Yes / Subscribe' option missing on subscription prompt"
        assert base.is_visible("No") or base.is_visible("Skip"), \
            "'No / Skip' option missing on subscription prompt"
        screenshot(driver, "subscription_prompt_options")

    def test_subscription_frequency_options_shown(self, driver):
        """Both Weekly and Monthly frequency options must be visible after 'Yes'."""
        base = self._login_and_reach_subscription_prompt(driver)
        base.tap_optional("Yes")
        wait_for_animation(driver)

        assert base.is_visible("Weekly"), "Weekly option not shown"
        assert base.is_visible("Monthly"), "Monthly option not shown"
        screenshot(driver, "subscription_frequency_options")

    def test_cancel_active_subscription_declined(self, driver):
        """Cancel subscription dialog 'No' must keep subscription active."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        base = BasePage(driver)
        base.tap_optional("Active Subscription")
        base.tap_optional("Subscriptions")
        wait_for_animation(driver)

        screenshot(driver, "subscription_active_list")

        base.tap_optional("Cancel Subscription")
        wait_for_animation(driver)
        base.tap_optional("No")
        wait_for_animation(driver)

        assert base.is_visible("Billing History") or \
               base.is_visible("Subscription") or \
               base.is_visible("Active"), \
            "After declining cancel, subscription screen not maintained"
        screenshot(driver, "subscription_cancel_declined")

    def test_subscription_billing_history_accessible(self, driver):
        """Billing history page must load without error (accessed from subscription area)."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        base = BasePage(driver)
        base.tap_optional("Active Subscription")
        base.tap_optional("Subscriptions")
        wait_for_animation(driver)
        base.tap_optional("Billing History")
        wait_for_animation(driver)

        assert base.is_visible("Billing History") or \
               base.is_visible("No history") or \
               base.is_visible("Transaction"), \
            "Billing History page did not load"
        screenshot(driver, "subscription_billing_history")
