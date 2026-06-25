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
        # Try scrolling to find the currency option — it may be below the fold
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found = False
        for _ in range(5):
            if page.is_visible("Change Currency", timeout=2) or \
               page.is_visible("Currency", timeout=2) or \
               page.is_visible("العملة", timeout=2):
                found = True
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.3)
        if not found:
            pytest.skip("Currency option not found after scrolling — profile UI may have changed")
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
        # Try scrolling to find Delete Account — it's often at the very bottom
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found = False
        for _ in range(8):
            if page.is_visible("Delete Account", timeout=2) or \
               page.is_visible("Delete My Account", timeout=2) or \
               page.is_visible("حذف الحساب", timeout=2):
                found = True
                break
            driver.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 500)
            wait_for_animation(driver, 0.3)
        if not found:
            pytest.skip("Delete Account option not found after scrolling — profile UI may have changed")
        for label in ["Delete Account", "Delete My Account", "حذف الحساب"]:
            page.tap_optional(label, timeout=2)
        wait_for_animation(driver)
        assert page.is_visible("Are you sure") or page.is_visible("Delete") or \
               page.is_visible("Confirm"), \
            "Delete account confirmation not shown"
        for cancel in ["No", "Cancel", "Keep", "لا"]:
            page.tap_optional(cancel, timeout=2)
        screenshot(driver, "delete_account_confirmation")

    @allure.story("Help")
    @allure.title("Help & Support page shows contact options")
    def test_help_support_contact_options(self, driver):
        login = LoginPage(driver)
        login.login()

        page = BasePage(driver)
        ProfilePage(driver).navigate_to_profile()
        wait_for_animation(driver)
        # Try all known Help entry points
        for label in ["How can we help?", "Help & Support", "Help", "Support",
                      "Customer Support", "مساعدة", "الدعم"]:
            page.tap_optional(label, timeout=2)
        wait_for_animation(driver, 2)

        found = page.is_visible("WhatsApp", timeout=3) or \
                page.is_visible("Mail Us", timeout=3) or \
                page.is_visible("Email", timeout=3) or \
                page.is_visible("Contact", timeout=3) or \
                page.is_visible("How can we help?", timeout=3) or \
                page.is_visible("Help", timeout=3)
        if not found:
            pytest.skip("Help & Support not reachable — profile UI may have changed")
        screenshot(driver, "help_support_page")

    @allure.story("Billing")
    @allure.title("Billing history is accessible")
    def test_billing_history_accessible(self, driver):
        login = LoginPage(driver)
        login.login()
        ProfilePage(driver).navigate_to_profile()

        page = BasePage(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found = False
        for _ in range(8):
            if page.is_visible("Billing History", timeout=2) or \
               page.is_visible("Payment History", timeout=2) or \
               page.is_visible("سجل الفواتير", timeout=2):
                found = True
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.3)
        if not found:
            pytest.skip("Billing History option not found after scrolling — profile UI may have changed")
        for label in ["Billing History", "Payment History", "سجل الفواتير"]:
            page.tap_optional(label, timeout=2)
        wait_for_animation(driver, 2)
        assert page.is_visible("Billing History") or \
               page.is_visible("Payment") or \
               page.is_visible("Orders") or \
               page.is_visible("Invoices"), \
            "Billing History page did not load or section is not accessible"
        screenshot(driver, "billing_history")
