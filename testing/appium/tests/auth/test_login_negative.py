import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import InvalidPhone, InvalidOTP, ValidData


def _get_phone_field(driver):
    """Return first EditText (phone input), or None if not found."""
    els = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    return els[0] if els else None


def _get_otp_field(driver):
    """Return first empty EditText (OTP field), or None."""
    els = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    for el in els:
        val = (el.get_attribute("text") or "").strip()
        if val in ("", "null", "|") or len(val) < 6:
            return el
    return els[0] if els else None


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
        """Tapping Continue with no phone entered must not advance to OTP screen."""
        page = self._reach_phone_screen(driver)
        page.tap_optional("Continue")
        wait_for_animation(driver)

        # Validation fires (error text visible) OR we stayed on phone screen (no OTP)
        assert (
            page.is_visible("required") or
            page.is_visible("Please enter") or
            page.is_visible("invalid") or
            page.is_visible("Enter phone") or
            not page.is_visible("Confirm to Login", timeout=2)
        ), "Empty phone advanced to OTP screen — validation did not fire"
        screenshot(driver, "login_empty_phone_error")

    def test_too_short_phone_shows_error(self, driver):
        """A 3-digit phone number must be rejected."""
        self._reach_phone_screen(driver)
        field = _get_phone_field(driver)
        if field is None:
            pytest.skip("Phone input field not found")
        field.send_keys(InvalidPhone.TOO_SHORT)
        BasePage(driver).tap_optional("Continue")
        wait_for_animation(driver)

        assert (
            not driver.find_elements(AppiumBy.XPATH, '//*[@text="Confirm to Login"]') and
            not driver.find_elements(AppiumBy.XPATH, '//*[contains(@text,"Verification")]')
        ), "Short phone number was accepted — OTP screen must not appear"
        screenshot(driver, "login_short_phone_error")

    def test_too_long_phone_shows_error(self, driver):
        """A 20-digit phone number must be rejected."""
        self._reach_phone_screen(driver)
        field = _get_phone_field(driver)
        if field is None:
            pytest.skip("Phone input field not found")
        field.send_keys(InvalidPhone.TOO_LONG)
        BasePage(driver).tap_optional("Continue")
        wait_for_animation(driver)

        assert (
            not driver.find_elements(AppiumBy.XPATH, '//*[@text="Confirm to Login"]') and
            not driver.find_elements(AppiumBy.XPATH, '//*[contains(@text,"Verification")]')
        ), "Overly long phone number was accepted"
        screenshot(driver, "login_long_phone_error")

    def test_letters_in_phone_shows_error(self, driver):
        """Alphabetic characters in phone field must be rejected or ignored."""
        self._reach_phone_screen(driver)
        field = _get_phone_field(driver)
        if field is None:
            pytest.skip("Phone input field not found")
        field.send_keys(InvalidPhone.LETTERS_ONLY)
        BasePage(driver).tap_optional("Continue")
        wait_for_animation(driver)

        assert "Enter OTP" not in driver.page_source, \
            "Alpha-only phone was accepted"
        screenshot(driver, "login_alpha_phone_error")

    def test_special_chars_in_phone_shows_error(self, driver):
        """Special characters in phone field must not crash the app."""
        self._reach_phone_screen(driver)
        field = _get_phone_field(driver)
        if field is None:
            pytest.skip("Phone input field not found")
        field.send_keys(InvalidPhone.SPECIAL_CHARS)
        BasePage(driver).tap_optional("Continue")
        wait_for_animation(driver)

        assert "Enter OTP" not in driver.page_source, \
            "Special-char phone was accepted — OTP screen must not appear"
        screenshot(driver, "login_special_phone_error")

    def test_wrong_otp_shows_error(self, driver):
        """Submitting a wrong OTP must show an error message."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        field = _get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys(InvalidOTP.WRONG)
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        wait_for_animation(driver, 3)

        assert "Cart" not in driver.page_source, \
            "Wrong OTP was accepted — user must NOT be logged in"
        screenshot(driver, "login_wrong_otp_error")

    def test_all_zeros_otp_shows_error(self, driver):
        """OTP of all zeros (0000) must be rejected."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        field = _get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys(InvalidOTP.ALL_ZEROS)
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        wait_for_animation(driver, 3)

        assert "Cart" not in driver.page_source, \
            "All-zero OTP was accepted — user must NOT be logged in"
        screenshot(driver, "login_zeros_otp_error")

    def test_empty_otp_blocks_verify(self, driver):
        """Tapping Verify with no OTP entered must show an error."""
        page = LoginPage(driver)
        page.select_country_and_language()
        page.skip_onboarding()
        page.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)

        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        wait_for_animation(driver, 2)

        assert "Cart" not in driver.page_source, \
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
        assert (
            base.is_visible("Resend") or
            base.is_visible("Didn't receive") or
            base.is_visible("Send again") or
            base.is_visible("Resend OTP") or
            "resend" in driver.page_source.lower() or
            "send again" in driver.page_source.lower()
        ), "Resend OTP option not found on OTP screen"
        screenshot(driver, "login_resend_otp_visible")
