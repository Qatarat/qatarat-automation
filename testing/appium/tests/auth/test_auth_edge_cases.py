"""
Auth edge cases — phone formatting, OTP input quirks, session behaviour.
"""
import time
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import wait_for_animation
from test_data import ValidData, InvalidPhone, BoundaryValues


def _reach_phone_screen(driver):
    page = LoginPage(driver)
    page._dismiss_system_dialogs()
    page._switch_to_english()
    page.select_country_and_language()
    page.skip_onboarding()
    page._navigate_to_login_screen()
    wait_for_animation(driver)
    return page


def _get_phone_field(driver):
    """Return the phone input EditText, or None if not found."""
    els = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    return els[0] if els else None


@pytest.mark.auth
@pytest.mark.boundary
class TestPhoneInputEdgeCases:

    def test_phone_with_leading_spaces_trimmed_or_rejected(self, driver):
        """Leading/trailing spaces around phone number — must not crash, should trim."""
        login = _reach_phone_screen(driver)
        login.enter_phone("  " + ValidData.PHONE + "  ")
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_phone_with_country_code_plus_prefix(self, driver):
        """User types +880 prefix — should be handled."""
        login = _reach_phone_screen(driver)
        login.enter_phone("+880" + ValidData.PHONE)
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_phone_all_same_digits(self, driver):
        """'1111111111' — valid format but invalid number."""
        login = _reach_phone_screen(driver)
        login.enter_phone("1111111111")
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_phone_starting_with_zero(self, driver):
        """Phone starting with 0 — some regions use 0XXXXXXXXX format."""
        login = _reach_phone_screen(driver)
        login.enter_phone("0" + ValidData.PHONE[1:])
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_phone_with_dots(self, driver):
        """Dots in phone number — e.g. 880.168.522.0417"""
        login = _reach_phone_screen(driver)
        login.enter_phone("880.168.522.0417")
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_phone_with_parentheses(self, driver):
        """Formatted phone (880) 1685220417 — common copy-paste format."""
        login = _reach_phone_screen(driver)
        login.enter_phone("(880) 1685220417")
        login.tap_continue()
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_phone_exactly_max_length_not_exceeded(self, driver):
        """Phone input should cap at max digits, not allow infinite input."""
        _reach_phone_screen(driver)
        field = _get_phone_field(driver)
        if field is None:
            pytest.skip("Phone input field not found")
        field.send_keys("1" * 20)
        entered = (field.text or "").replace(" ", "").replace("-", "").replace("+", "")
        assert len(entered) <= 15, f"Phone field accepted {len(entered)} digits (E.164 max is 15)"

    def test_uppercase_in_phone_field_not_accepted(self, driver):
        """Phone field should be numeric — alpha chars must be blocked or ignored."""
        login = _reach_phone_screen(driver)
        login.enter_phone("ABCDEFGHIJ")
        login.tap_continue()
        page = driver.page_source
        assert "Enter OTP" not in page

    def test_phone_with_emoji_does_not_crash(self, driver):
        """Emoji in phone field — must not crash the app."""
        login = _reach_phone_screen(driver)
        login.enter_phone("📱8801685220417")
        login.tap_continue()
        assert "500" not in driver.page_source


@pytest.mark.auth
@pytest.mark.boundary
class TestOTPEdgeCases:

    def _reach_otp_screen(self, driver):
        """Navigate to OTP screen and return (login, base_page) tuple."""
        login = LoginPage(driver)
        login._dismiss_system_dialogs()
        login._switch_to_english()
        login.select_country_and_language()
        login.skip_onboarding()
        login.login_phone_only(ValidData.PHONE)
        wait_for_animation(driver, 3)
        return login

    def _get_otp_field(self, driver):
        """Return first empty EditText (OTP field), or None."""
        els = driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
        for el in els:
            val = (el.get_attribute("text") or "").strip()
            if val in ("", "null", "|") or len(val) < 6:
                return el
        return els[0] if els else None

    def test_otp_with_spaces_between_digits(self, driver):
        """OTP '1 2 3 4' with spaces — should be trimmed or rejected clearly."""
        self._reach_otp_screen(driver)
        field = self._get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys("1 2 3 4")
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_otp_uppercase_letters_blocked(self, driver):
        """OTP is numeric-only — uppercase must be rejected."""
        self._reach_otp_screen(driver)
        field = self._get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys("ABCD")
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        assert "Cart" not in driver.page_source

    def test_otp_special_chars_blocked(self, driver):
        """OTP '!@#$' must be rejected."""
        self._reach_otp_screen(driver)
        field = self._get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys("!@#$")
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        assert "Cart" not in driver.page_source

    def test_otp_very_long_input_does_not_crash(self, driver):
        """100-digit OTP input — must not crash or show server error."""
        self._reach_otp_screen(driver)
        field = self._get_otp_field(driver)
        if field is None:
            pytest.skip("OTP screen not reached")
        field.send_keys("1" * 100)
        BasePage(driver).tap_optional("Verify")
        BasePage(driver).tap_optional("Confirm to Login")
        assert "500" not in driver.page_source
        assert "crash" not in driver.page_source.lower()
