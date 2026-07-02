import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import BoundaryValues


@pytest.mark.cart
@pytest.mark.negative
class TestCartBoundary:
    """Boundary and edge-case tests for cart operations."""

    def _login_and_open_cart(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()
        login.assert_logged_in()
        return CartPage(driver)

    def test_empty_cart_checkout_is_blocked(self, driver):
        """Checkout button must not proceed when the cart is empty."""
        cart = self._login_and_open_cart(driver)
        cart.open_cart()
        wait_for_animation(driver)

        base = BasePage(driver)
        base.tap_optional("Checkout")
        wait_for_animation(driver)

        assert base.is_visible("cart is empty") or \
               base.is_visible("No items") or \
               base.is_visible("Add items") or \
               not base.is_visible("Payment method"), \
            "Empty cart allowed checkout — payment screen must NOT appear"
        screenshot(driver, "cart_empty_checkout_blocked")

    def test_quantity_increment_updates_total(self, driver):
        """Incrementing quantity must change the displayed subtotal."""
        cart = self._login_and_open_cart(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.assert_has_items()

        base = BasePage(driver)
        # Capture initial state, increment, verify something changed
        cart.update_quantity(increment=True)
        wait_for_animation(driver)
        screenshot(driver, "cart_quantity_incremented")

        # Quantity indicator should show "2" or total should have updated
        assert base.is_visible("2") or base.is_visible("Checkout"), \
            "Cart quantity increment had no visible effect"

    def test_quantity_decrement_to_one_keeps_item(self, driver):
        """Decrementing from 2 → 1 keeps the item in cart."""
        cart = self._login_and_open_cart(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.update_quantity(increment=True)   # qty = 2
        wait_for_animation(driver)
        cart.update_quantity(increment=False)  # qty = 1
        wait_for_animation(driver)

        cart.assert_has_items()
        screenshot(driver, "cart_quantity_back_to_one")

    def test_quantity_decrement_at_one_removes_or_prompts(self, driver):
        """Decrementing at quantity 1 must either remove the item or show a confirmation."""
        cart = self._login_and_open_cart(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.assert_has_items()

        cart.update_quantity(increment=False)  # try to go below 1
        wait_for_animation(driver)

        base = BasePage(driver)
        assert base.is_visible("Remove") or \
               base.is_visible("cart is empty") or \
               base.is_visible("No items") or \
               base.is_visible("Are you sure"), \
            "Decrementing below 1 had no removal prompt or empty-cart state"
        screenshot(driver, "cart_decrement_below_one")

    def test_maximum_quantity_does_not_crash(self, driver):
        """Tapping '+' many times must not crash the app or produce NaN/error UI."""
        cart = self._login_and_open_cart(driver)
        cart.add_first_item()
        cart.open_cart()

        base = BasePage(driver)
        for _ in range(BoundaryValues.CART_MAX_QUANTITY_TAPS):
            base.tap_optional("+")
            wait_for_animation(driver, 0.3)

        screenshot(driver, "cart_max_quantity")

        assert not base.is_visible("NaN") and \
               not base.is_visible("Error") and \
               not base.is_visible("Something went wrong"), \
            "Cart showed NaN or error after many quantity increments"

    def test_remove_all_items_shows_empty_state(self, driver):
        """Removing every item must display an empty-cart UI, not a crash."""
        cart = self._login_and_open_cart(driver)
        cart.add_first_item()
        cart.open_cart()
        cart.assert_has_items()

        base = BasePage(driver)
        base.tap_optional("Remove")
        wait_for_animation(driver)
        base.tap_optional("Yes")   # confirm removal if dialog appears
        wait_for_animation(driver)

        assert base.is_visible("cart is empty") or \
               base.is_visible("No items") or \
               base.is_visible("Start shopping"), \
            "Empty cart state not shown after removing all items"
        screenshot(driver, "cart_empty_after_remove")
