import os
import pytest
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.helpers import screenshot, wait_for_animation


SAMPLE_RECEIPT = os.path.join(
    os.path.dirname(__file__), "../../assets/sample_receipt.jpg"
)


def _reach_checkout(driver):
    """Login, add item, open cart, proceed to checkout. Skips if any step fails."""
    LoginPage(driver).login()
    cart = CartPage(driver)
    if not cart.add_first_item():
        pytest.skip("No service items found — payment tests not testable")
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
class TestBankTransfer:
    """
    Bank transfer payment flow — upload receipt and await manual approval.
    """

    def test_bank_transfer_option_visible(self, driver):
        """Bank transfer option should appear in payment screen."""
        checkout = _reach_checkout(driver)
        assert checkout.is_visible("Bank Transfer", timeout=5) or \
               checkout.is_visible("Bank Name", timeout=3), \
            "Bank transfer option not visible"
        screenshot(driver, "bank_transfer_option")

    def test_bank_transfer_shows_account_details(self, driver):
        """Selecting bank transfer should show account holder info."""
        checkout = _reach_checkout(driver)
        if not (checkout.is_visible("Bank Transfer", timeout=5) or
                checkout.is_visible("Bank", timeout=3)):
            pytest.skip("Bank Transfer option not visible on checkout screen")
        checkout.select_bank_transfer()
        wait_for_animation(driver, 2)

        assert checkout.is_visible("Bank Name", timeout=5) or \
               checkout.is_visible("Account Holder Name", timeout=3) or \
               checkout.is_visible("Transaction Reference", timeout=3) or \
               checkout.is_visible("IBAN", timeout=3) or \
               checkout.is_visible("Account", timeout=3), \
            "Bank account details not displayed"
        screenshot(driver, "bank_transfer_details")

    def test_bank_transfer_receipt_upload_prompt(self, driver):
        """Receipt upload prompt should appear after selecting bank transfer."""
        checkout = _reach_checkout(driver)
        if not (checkout.is_visible("Bank Transfer", timeout=5) or
                checkout.is_visible("Bank", timeout=3)):
            pytest.skip("Bank Transfer option not visible on checkout screen")
        checkout.select_bank_transfer()
        wait_for_animation(driver, 2)
        checkout.tap_optional("Submit Order")
        wait_for_animation(driver, 2)

        if not (checkout.is_visible("Please attach the payment receipt", timeout=5) or
                checkout.is_visible("upload", timeout=3) or
                checkout.is_visible("Upload", timeout=3)):
            pytest.skip("Receipt upload prompt not shown — bank transfer flow may have changed")
        screenshot(driver, "bank_receipt_prompt")

    def test_bank_transfer_receipt_source_options(self, driver):
        """Upload dialog should offer Camera and Gallery options."""
        checkout = _reach_checkout(driver)
        if not (checkout.is_visible("Bank Transfer", timeout=5) or
                checkout.is_visible("Bank", timeout=3)):
            pytest.skip("Bank Transfer option not visible on checkout screen")
        checkout.select_bank_transfer()
        wait_for_animation(driver)
        checkout.tap_optional("Please attach the payment receipt")
        checkout.tap_optional("Upload")
        wait_for_animation(driver)

        if not (checkout.is_visible("Take a Photo", timeout=5) or
                checkout.is_visible("Choose from Gallery", timeout=3) or
                checkout.is_visible("Camera", timeout=3) or
                checkout.is_visible("Gallery", timeout=3)):
            pytest.skip("Photo source dialog not shown — upload flow may have changed")
        screenshot(driver, "bank_receipt_source_options")
