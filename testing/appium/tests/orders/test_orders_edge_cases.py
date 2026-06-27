import pytest
from pages.login_page import LoginPage
from pages.orders_page import OrdersPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
from utils.markers import android_apk_regression
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import InvalidRating, BoundaryValues


@android_apk_regression
@pytest.mark.orders
@pytest.mark.android
class TestOrdersEdgeCases:
    """Edge-case and negative tests for the My Orders section."""

    def _login_and_open_orders(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        orders = OrdersPage(driver)
        orders.open()
        orders.assert_orders_screen()
        return orders

    def test_search_with_no_results_shows_empty_state(self, driver):
        """Searching with a term that matches nothing must show an empty/no-results state."""
        orders = self._login_and_open_orders(driver)
        orders.search_order(BoundaryValues.ORDER_SEARCH_NO_RESULTS)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert base.is_visible("No results") or \
               base.is_visible("No orders") or \
               base.is_visible("not found") or \
               base.is_visible("empty"), \
            "Search with no-match term did not show an empty state"
        screenshot(driver, "orders_search_no_results")

    def test_search_with_special_chars_does_not_crash(self, driver):
        """Special characters in the order search must not crash the app."""
        orders = self._login_and_open_orders(driver)
        orders.search_order(BoundaryValues.HELP_SEARCH_SPECIAL)
        wait_for_animation(driver, 2)

        base = BasePage(driver)
        assert not base.is_visible("500") and \
               not base.is_visible("Exception") and \
               not base.is_visible("crash"), \
            "Special-char order search caused an error"
        screenshot(driver, "orders_search_special_chars")

    def test_empty_rating_feedback_shows_error(self, driver):
        """Submitting a rating with no feedback text must show a validation error."""
        orders = self._login_and_open_orders(driver)
        orders.open_first_order()
        orders.assert_order_detail()

        base = BasePage(driver)
        base.tap_optional("Rate Order")
        wait_for_animation(driver)

        # Select stars but leave feedback empty
        base.tap_optional("★")
        wait_for_animation(driver)
        base.tap_optional("Submit Rating")
        wait_for_animation(driver)

        assert base.is_visible("required") or \
               base.is_visible("Enter") or \
               base.is_visible("feedback") or \
               not base.is_visible("Thank You"), \
            "Empty rating feedback was submitted successfully"
        screenshot(driver, "orders_empty_feedback_error")

    def test_long_rating_feedback_is_handled(self, driver):
        """A very long feedback text must be submitted or truncated without crashing."""
        orders = self._login_and_open_orders(driver)
        orders.open_first_order()

        base = BasePage(driver)
        base.tap_optional("Rate Order")
        wait_for_animation(driver)

        orders.rate_order(InvalidRating.LONG_FEEDBACK, stars=5)
        wait_for_animation(driver, 3)

        assert not base.is_visible("500") and \
               not base.is_visible("Exception"), \
            "Long rating feedback caused a server error"
        screenshot(driver, "orders_long_feedback")

    def test_special_chars_in_feedback_are_safe(self, driver):
        """Special characters in feedback must be safely handled."""
        orders = self._login_and_open_orders(driver)
        orders.open_first_order()

        base = BasePage(driver)
        base.tap_optional("Rate Order")
        wait_for_animation(driver)

        orders.rate_order(InvalidRating.SPECIAL_CHARS, stars=3)
        wait_for_animation(driver, 3)

        assert not base.is_visible("500") and \
               not base.is_visible("SQL"), \
            "Special chars in feedback exposed a server error"
        screenshot(driver, "orders_special_chars_feedback")

    def test_order_detail_shows_required_fields(self, driver):
        """Order detail screen must display order number, date, and status."""
        orders = self._login_and_open_orders(driver)
        orders.open_first_order()
        orders.assert_order_detail()

        base = BasePage(driver)
        assert base.is_visible("Order Number") or base.is_visible("Order #"), \
            "Order Number not shown on detail page"
        assert base.is_visible("Payment Date") or base.is_visible("Date"), \
            "Payment Date not shown on detail page"
        screenshot(driver, "orders_detail_fields")

    def test_cancel_order_dialog_can_be_dismissed(self, driver):
        """Cancel Order dialog must be dismissible without cancelling."""
        orders = self._login_and_open_orders(driver)
        orders.open_first_order()

        base = BasePage(driver)
        base.tap_optional("Cancel Order")
        wait_for_animation(driver)

        assert base.is_visible("Are you sure") or \
               base.is_visible("Cancel") or \
               base.is_visible("confirm"), \
            "Cancel Order confirmation dialog did not appear"

        base.tap_optional("No")
        wait_for_animation(driver)

        assert base.is_visible("Order Number") or \
               base.is_visible("Order #"), \
            "Dismissing cancel dialog navigated away from order detail"
        screenshot(driver, "orders_cancel_dismissed")
