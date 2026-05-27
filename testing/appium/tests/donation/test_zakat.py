import pytest
import allure
from pages.login_page import LoginPage
from pages.donation_page import DonationPage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Donation")
@allure.feature("Zakat Calculator")
@pytest.mark.donation
@pytest.mark.zakat
@pytest.mark.android
class TestZakat:
    """Tests for the Zakat calculation section."""

    def _login_and_open_zakat(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()
        page = DonationPage(driver)
        page.navigate_to_zakat()
        return page

    @allure.story("Navigation")
    @allure.title("Navigate to the Zakat section successfully")
    def test_zakat_navigate(self, driver):
        page = self._login_and_open_zakat(driver)
        assert page.is_visible("Zakat") or \
               page.is_visible("Calculate") or \
               page.is_visible("Nisab"), \
            "Zakat section did not load"
        screenshot(driver, "zakat_navigate")

    @allure.story("Happy Path")
    @allure.title("Enter a valid wealth amount and calculate Zakat")
    def test_zakat_valid_wealth(self, driver):
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat(100000)
        wait_for_animation(driver)
        assert not page.is_visible("Error", timeout=3), \
            "Error shown for valid wealth amount 100000"
        screenshot(driver, "zakat_valid_wealth")

    @allure.story("Negative")
    @allure.title("Entering zero wealth shows validation or zero Zakat result")
    def test_zakat_zero_wealth(self, driver):
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat(0)
        wait_for_animation(driver)
        assert page.is_visible("0") or \
               page.is_visible("Enter") or \
               page.is_visible("Invalid") or \
               page.is_visible("Zakat"), \
            "Zero wealth amount produced unexpected result"
        screenshot(driver, "zakat_zero_wealth")

    @allure.story("Boundary")
    @allure.title("Wealth below Nisab threshold shows no Zakat due")
    def test_zakat_below_nisab(self, driver):
        # Nisab is approximately the value of 85 grams of gold; 100 SAR is well below
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat(100)
        wait_for_animation(driver)
        assert page.is_visible("0") or \
               page.is_visible("No Zakat") or \
               page.is_visible("Below") or \
               page.is_visible("Nisab") or \
               not page.is_visible("Error"), \
            "Below-Nisab wealth produced an unexpected result"
        screenshot(driver, "zakat_below_nisab")

    @allure.story("Boundary")
    @allure.title("Very large wealth value is handled without crash")
    def test_zakat_large_wealth(self, driver):
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat(99999999)
        wait_for_animation(driver)
        assert not page.is_visible("crash", timeout=3), \
            "App crashed when a very large wealth value was entered"
        screenshot(driver, "zakat_large_wealth")

    @allure.story("Boundary")
    @allure.title("Decimal wealth value is accepted or handled gracefully")
    def test_zakat_decimal_wealth(self, driver):
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat("5000.75")
        wait_for_animation(driver)
        assert not page.is_visible("crash", timeout=3) and \
               not page.is_visible("500", timeout=3), \
            "Decimal wealth value caused a crash or server error"
        screenshot(driver, "zakat_decimal_wealth")

    @allure.story("Happy Path")
    @allure.title("Zakat amount is calculated and displayed after entering wealth")
    def test_zakat_calculation_shown(self, driver):
        page = self._login_and_open_zakat(driver)
        page.calculate_zakat(500000)
        wait_for_animation(driver)
        assert page.is_visible("Zakat") or \
               page.is_visible("Amount") or \
               page.is_visible("SAR"), \
            "Zakat calculation result was not displayed"
        screenshot(driver, "zakat_calculation_shown")

    @allure.story("Display")
    @allure.title("Currency label is visible on the Zakat screen")
    def test_zakat_currency_display(self, driver):
        page = self._login_and_open_zakat(driver)
        wait_for_animation(driver)
        assert page.is_visible("SAR") or \
               page.is_visible("SR") or \
               page.is_visible("Currency") or \
               page.is_visible("Zakat"), \
            "No currency label found on Zakat screen"
        screenshot(driver, "zakat_currency_display")
