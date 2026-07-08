from pages.base_page import BasePage
from utils.helpers import scroll_to_text, wait_for_animation


class CartPage(BasePage):

    def add_first_item(self):
        """Scroll to and tap the first 'Add' button. Returns True if added, False otherwise."""
        for nav_label in [None, "Select a Service", "Services", "Browse"]:
            if nav_label:
                self.tap_optional(nav_label, timeout=3)
                wait_for_animation(self.driver)
            try:
                scroll_to_text(self.driver, "Add")
                self.tap_optional("Add", timeout=3)
                wait_for_animation(self.driver, 1)
                return True
            except Exception:
                continue
        return False

    def open_cart(self):
        self.tap("Cart")
        wait_for_animation(self.driver)
        return self

    def assert_has_items(self):
        assert self.is_visible("Items in the cart") or self.is_visible("Checkout"), \
            "Cart appears to be empty"
        return self

    def apply_promo(self, code):
        self.tap_optional("Redeem your Promo Code")
        self.input_text("Promo Code", code)
        self.tap_optional("Apply")
        wait_for_animation(self.driver)
        return self

    def assert_promo_applied(self):
        self.assert_visible("Promo Code Applied")
        return self

    def update_quantity(self, increment=True):
        self.tap_optional("+" if increment else "-")
        wait_for_animation(self.driver, 0.5)
        return self

    def proceed_to_checkout(self):
        self.tap("Checkout")
        wait_for_animation(self.driver, 2)
        return self
