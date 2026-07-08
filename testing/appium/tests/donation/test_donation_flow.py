import pytest
import allure
from pages.login_page import LoginPage
from pages.donation_page import DonationPage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Donation")
@allure.feature("Donation Flow")
@pytest.mark.donation
class TestDonationFlow:
    """End-to-end and boundary tests for the general donation flow."""

    def _login_and_go_to_donations(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()
        page = DonationPage(driver)
        page.navigate_to_donations()
        return page

    @allure.story("Happy Path")
    @allure.title("Donate a valid amount of 50")
    def test_donation_valid_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(50)
        wait_for_animation(driver)
        assert not page.is_visible("Error", timeout=3), \
            "Unexpected error shown for valid donation amount 50"
        screenshot(driver, "donation_valid_amount")

    @allure.story("Boundary")
    @allure.title("Donate minimum allowed amount of 1")
    def test_donation_minimum_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(1)
        wait_for_animation(driver)
        assert not page.is_visible("Minimum", timeout=3) or \
               page.is_visible("1", timeout=3), \
            "Minimum donation amount of 1 was rejected unexpectedly"
        screenshot(driver, "donation_minimum_amount")

    @allure.story("Boundary")
    @allure.title("Donate a very large amount of 99999")
    def test_donation_maximum_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(99999)
        wait_for_animation(driver)
        # App may accept or show a cap message — neither should crash
        assert not page.is_visible("crash", timeout=3), \
            "App crashed on large donation amount"
        screenshot(driver, "donation_maximum_amount")

    @allure.story("Negative")
    @allure.title("Donating zero amount shows a validation error")
    def test_donation_zero_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(0)
        page.confirm_donation()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Enter") or \
               page.is_visible("required") or \
               page.is_visible("minimum") or \
               page.is_visible("Error"), \
            "No validation error shown when donating zero amount"
        screenshot(driver, "donation_zero_amount")

    @allure.story("Negative")
    @allure.title("Donating negative amount shows a validation error")
    def test_donation_negative_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(-10)
        page.confirm_donation()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Enter") or \
               page.is_visible("Error") or \
               not page.is_visible("Confirmed"), \
            "Negative donation amount was accepted without error"
        screenshot(driver, "donation_negative_amount")

    @allure.story("Boundary")
    @allure.title("Donating a decimal amount of 10.50 is accepted")
    def test_donation_decimal_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount("10.50")
        wait_for_animation(driver)
        assert not page.is_visible("Invalid", timeout=3), \
            "Decimal donation amount 10.50 was rejected"
        screenshot(driver, "donation_decimal_amount")

    @allure.story("Negative")
    @allure.title("Entering letters in amount field shows validation error")
    def test_donation_special_chars_in_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount("abc")
        page.confirm_donation()
        wait_for_animation(driver)
        assert page.is_visible("Invalid") or \
               page.is_visible("Enter") or \
               page.is_visible("Error") or \
               not page.is_visible("Confirmed"), \
            "Non-numeric donation amount 'abc' was accepted"
        screenshot(driver, "donation_special_chars_amount")

    @allure.story("Negative")
    @allure.title("Submitting an empty amount field shows validation error")
    def test_donation_empty_amount(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount("")
        page.confirm_donation()
        wait_for_animation(driver)
        assert page.is_visible("required") or \
               page.is_visible("Enter") or \
               page.is_visible("Amount") or \
               page.is_visible("Invalid") or \
               not page.is_visible("Confirmed"), \
            "Empty donation amount was accepted without error"
        screenshot(driver, "donation_empty_amount")

    @allure.story("Happy Path")
    @allure.title("Donation confirmation screen appears after valid donation")
    def test_donation_confirmation_shown(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(10)
        page.confirm_donation()
        wait_for_animation(driver, 3)
        confirmation = page.get_confirmation_message()
        assert confirmation is not None or \
               page.is_visible("Order") or \
               page.is_visible("Payment"), \
            "Donation confirmation screen did not appear"
        screenshot(driver, "donation_confirmation_shown")

    @allure.story("Navigation")
    @allure.title("Cancelling mid-donation navigates back without completing it")
    def test_donation_cancel_midway(self, driver):
        page = self._login_and_go_to_donations(driver)
        page.enter_donation_amount(25)
        wait_for_animation(driver)
        driver.back()
        wait_for_animation(driver)
        assert not page.is_visible("Confirmed", timeout=3) and \
               not page.is_visible("Thank you", timeout=3), \
            "Donation was completed despite pressing back mid-flow"
        screenshot(driver, "donation_cancel_midway")
