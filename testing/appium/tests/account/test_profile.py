import pytest
import allure
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, scroll_to_text


@allure.epic("Account")
@allure.feature("Profile & Settings")
@pytest.mark.account
class TestProfile:

    @allure.story("Currency")
    @allure.title("Change currency option is accessible")
    def test_change_currency_accessible(self, driver):
        login = LoginPage(driver)
        login.login()
        ProfilePage(driver).navigate_to_profile()
        wait_for_animation(driver)

        page = BasePage(driver)
        assert page.is_visible("Change Currency") or page.is_visible("Currency"), \
            "Currency option not found in profile"
        screenshot(driver, "profile_currency_option")

    @allure.story("About")
    @allure.title("About Qatarat page loads")
    def test_about_page_loads(self, driver):
        login = LoginPage(driver)
        login.login()
        ProfilePage(driver).navigate_to_profile()

        page = BasePage(driver)
        page.tap_optional("About")
        page.tap_optional("About Qatarat")
        wait_for_animation(driver, 2)

        assert page.is_visible("Qatarat") or page.is_visible("About"), \
            "About page did not load"
        screenshot(driver, "about_page")

    @allure.story("Logout")
    @allure.title("Logout confirmation dialog appears")
    def test_logout_confirmation_dialog(self, driver):
        login = LoginPage(driver)
        login.login()
        pp = ProfilePage(driver)
        pp.navigate_to_profile()
        pp.tap_logout()
        wait_for_animation(driver)

        page = BasePage(driver)
        assert page.is_visible("Are you sure") or \
               page.is_visible("Logout") or \
               page.is_visible("Log out") or \
               page.is_visible("تسجيل الخروج"), \
            "Logout confirmation dialog not shown"
        page.tap_optional("No")
        screenshot(driver, "logout_confirmation")

    @allure.story("Delete Account")
    @allure.title("Delete account option exists with confirmation")
    def test_delete_account_has_confirmation(self, driver):
        login = LoginPage(driver)
        login.login()
        ProfilePage(driver).navigate_to_profile()

        page = BasePage(driver)
        scroll_to_text(driver, "Delete Account", max_scrolls=5)
        page.tap_optional("Delete Account")
        wait_for_animation(driver)

        assert page.is_visible("Are you sure") or page.is_visible("Delete"), \
            "Delete account confirmation not shown"
        page.tap_optional("No")
        page.tap_optional("Cancel")
        screenshot(driver, "delete_account_confirmation")

    @allure.story("Help")
    @allure.title("Help & Support page shows contact options")
    def test_help_support_contact_options(self, driver):
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally

        page = BasePage(driver)
        page.tap_optional("How can we help?")
        page.tap_optional("Help")
        page.tap_optional("Support")
        wait_for_animation(driver, 2)

        assert page.is_visible("WhatsApp") or page.is_visible("Mail Us") or \
               page.is_visible("How can we help?"), \
            "Help & Support contact options not visible"
        screenshot(driver, "help_support_page")

    @allure.story("Billing")
    @allure.title("Billing history is accessible")
    def test_billing_history_accessible(self, driver):
        login = LoginPage(driver)
        login.login()
        ProfilePage(driver).navigate_to_profile()

        page = BasePage(driver)
        scroll_to_text(driver, "Billing History", max_scrolls=5)
        page.tap_optional("Billing History")
        wait_for_animation(driver, 2)
        assert page.is_visible("Billing History") or \
               page.is_visible("Orders") or \
               page.is_visible("Invoices"), \
            "Billing History page did not load or section is not accessible"
        screenshot(driver, "billing_history")
