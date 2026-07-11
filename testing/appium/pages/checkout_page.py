from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text


class CheckoutPage(BasePage):

    def assert_payment_screen(self):
        assert self.is_visible("Please select payment method") or \
               self.is_visible("Select payment method"), \
            "Not on payment selection screen"
        return self

    def select_card_payment(self):
        self.tap_optional("Credit Card")
        self.tap_optional("Debit Card")
        self.tap_optional("Card")
        wait_for_animation(self.driver)
        return self

    def select_tabby(self):
        try:
            scroll_to_text(self.driver, "Pay later with Tabby")
        except Exception:
            pass
        self.tap_optional("Pay later with Tabby")
        wait_for_animation(self.driver)
        return self

    def select_bank_transfer(self):
        try:
            scroll_to_text(self.driver, "Bank Transfer")
        except Exception:
            pass
        self.tap_optional("Bank Transfer")
        wait_for_animation(self.driver)
        return self

    def fill_card_details(self, number, expiry, cvv, name):
        self.tap_optional("Card Number")
        self.input_text("Card Number", number)
        self.input_text("Expiry", expiry)
        self.input_text("CVV", cvv)
        self.input_text("Card Holder", name)
        return self

    def submit_order(self):
        self.tap_optional("Submit Order")
        self.tap_optional("Pay Now")
        wait_for_animation(self.driver, 4)
        return self

    def assert_processing(self):
        assert self.is_visible("Processing") or \
               self.is_visible("Please wait, initiating payment"), \
            "Payment processing screen not shown"
        return self

    def upload_bank_receipt(self, image_path):
        self.tap_optional("Please attach the payment receipt")
        self.tap_optional("Choose from Gallery")
        wait_for_animation(self.driver)
        return self

    def assert_order_placed(self, order_number=None):
        assert self.is_visible("Order Number") or \
               self.is_visible("Thank you for choosing"), \
            "Order confirmation not shown"
        return self
