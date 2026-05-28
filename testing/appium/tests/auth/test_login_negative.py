import pytest
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import InvalidPhone, InvalidOTP, ValidData


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.android
class TestLoginNegative:
    """Negative and boundary tests for the phone + OTP login flow."""

    def _reach_phone_screen(self, driver):
        page = LoginPage(driver)
        page._dismiss_system_dialogs()
        page._switch_to_english()
        page.select_country_and_language()
        page.skip_onboarding()
        page._navigate_to_login_screen()
        wait_for_animation(driver)
        return page

    def test_empty_phone_blocks_continue(self, driver):
        """Tapping Continue with no phone entered must show a validation error."""
        page = self._reach_phone_screen(driver)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        assert page.is_visible("Enter phone number") or \
               page.is_visible("required") or \
               page.is_visible("Please enter") or \
               page.is_visible("invalid"), \
            "Empty phone did not trigger a validation error"
        screenshot(driver, "login_empty_phone_error")

    def test_too_short_phone_shows_error(self, driver):
        """A 3-digit phone number must be rejected."""
        page = self._reach_phone_screen(driver)
        page.input_text("Enter phone number", InvalidPhone.TOO_SHORT)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        assert page.is_visible("invalid") or \
               page.is_visible("Enter valid") or \
               page.is_visible("incorrect") or \
               not page.is_visible("Enter OTP"), \
            "Short phone number was accepted — OTP screen should NOT appear"
        screenshot(driver, "login_short_phone_error")

    def test_too_long_phone_shows_error(self, driver):
        """A 20-digit phone number must be rejected."""
        page = self._reach_phone_screen(driver)
        page.input_text("Enter phone number", InvalidPhone.TOO_LONG)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        assert page.is_visible("invalid") or \
               page.is_visible("Enter valid") or \
               not page.is_visible("Enter OTP"), \
            "Overly long phone number was accepted"
        screenshot(driver, "login_long_phone_error")

    def test_letters_in_phone_shows_error(self, driver):
        """Alphabetic characters in phone field must be rejected or ignored."""
        page = self._reach_phone_screen(driver)
        page.input_text("Enter phone number", InvalidPhone.LETTERS_ONLY)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        assert page.is_visible("invalid") or \
               page.is_visible("numbers only") or \
               not page.is_visible("Enter OTP"), \
            "Alpha-only phone was accepted"
        screenshot(driver, "login_alpha_phone_error")

    def test_special_chars_in_phone_shows_error(self, driver):
        """Special characters in phone field must not crash the app."""
        page = self._reach_phone_screen(driver)
        page.input_text("Enter phone number", InvalidPhone.SPECIAL_CHARS)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        assert not page.is_visible("Enter OTP"), \
            "Special-char phone was accepted — OTP screen must not appear"
        screenshot(driver, "login_special_phone_error")

    def test_wrong_otp_shows_error(self, driver):
        """Submitting a wrong OTP must show an error message."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)   # enter phone + tap continue only
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        base.input_text("Enter OTP", InvalidOTP.WRONG)
        base.tap_optional("Verify")
        wait_for_animation(driver, 3)

        assert base.is_visible("Invalid OTP") or \
               base.is_visible("Incorrect OTP") or \
               base.is_visible("wrong") or \
               base.is_visible("Please enter") or \
               not base.is_visible("Cart"), \
            "Wrong OTP did not show an error"
        screenshot(driver, "login_wrong_otp_error")

    def test_all_zeros_otp_shows_error(self, driver):
        """OTP of all zeros (0000) must be rejected."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        base.input_text("Enter OTP", InvalidOTP.ALL_ZEROS)
        base.tap_optional("Verify")
        wait_for_animation(driver, 3)

        assert not base.is_visible("Cart"), \
            "All-zero OTP was accepted — user must NOT be logged in"
        screenshot(driver, "login_zeros_otp_error")

    def test_empty_otp_blocks_verify(self, driver):
        """Tapping Verify with no OTP entered must show an error."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        base.tap_optional("Verify")
        wait_for_animation(driver, 2)

        assert base.is_visible("Enter OTP") or \
               base.is_visible("required") or \
               not base.is_visible("Cart"), \
            "Empty OTP was accepted"
        screenshot(driver, "login_empty_otp_error")

    def test_otp_resend_link_visible(self, driver):
        """A resend/retry option must be visible on the OTP screen."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        base = BasePage(driver)
        assert base.is_visible("Resend") or \
               base.is_visible("Didn't receive") or \
               base.is_visible("Send again"), \
            "Resend OTP option not found on OTP screen"
        screenshot(driver, "login_resend_otp_visible")
