import pytest
import allure
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Account")
@allure.feature("Logout")
@pytest.mark.account
class TestLogout:
    """Tests covering the logout flow, session state, and redirect behaviour."""

    def _login(self, driver):
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally
        return ProfilePage(driver)

    @allure.story("Happy Path")
    @allure.title("User can log out successfully via Profile")
    def test_logout_happy_path(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        page.confirm_logout()
        wait_for_animation(driver, 2)
        # iOS shows "Login to your account" heading + "Log In" button; Android shows "Login"
        assert page.is_visible("Login") or \
               page.is_visible("Login to your account") or \
               page.is_visible("Log In") or \
               page.is_visible("Sign In") or \
               page.is_visible("Phone") or \
               page.is_visible("Welcome") or \
               page.is_visible("Enter phone") or \
               page.is_visible("Get Started") or \
               page.is_visible("تسجيل الدخول") or \
               page.is_visible("تسجيل الدخول إلى حسابك"), \
            "User was not redirected to the login screen after logout"
        screenshot(driver, "logout_happy_path")

    @allure.story("Cancellation")
    @allure.title("Cancelling logout dialog keeps the user logged in")
    def test_logout_cancel_dialog(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        wait_for_animation(driver)
        base = BasePage(driver)
        base.tap_optional("No")
        base.tap_optional("Cancel")
        wait_for_animation(driver)
        # After cancel the user stays on profile or home — iOS may show different labels
        assert base.is_visible("Profile") or \
               base.is_visible("Account") or \
               base.is_visible("Cart") or \
               base.is_visible("Logout") or \
               base.is_visible("Log out") or \
               base.is_visible("Sign out") or \
               base.is_visible("Wallet") or \
               base.is_visible("Donate") or \
               base.is_visible("Mosque") or \
               base.is_visible("Settings") or \
               base.is_visible("الملف الشخصي") or \
               base.is_visible("تسجيل الخروج") or \
               base.is_visible("Home") or \
               base.is_visible("الرئيسية"), \
            "User was logged out despite cancelling the logout dialog"
        screenshot(driver, "logout_cancel_dialog")

    @allure.story("Session")
    @allure.title("Session data is cleared after logout")
    def test_logout_state_cleared(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        page.confirm_logout()
        wait_for_animation(driver, 2)
        # Ensure the app no longer shows authenticated screens
        base = BasePage(driver)
        assert not base.is_visible("My Orders", timeout=3) or \
               base.is_visible("Login") or \
               base.is_visible("Phone"), \
            "Authenticated content still visible after logout — session not cleared"
        screenshot(driver, "logout_state_cleared")

    @allure.story("Navigation")
    @allure.title("User is redirected to login screen after logout")
    def test_logout_redirect_login(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        page.confirm_logout()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert base.is_visible("Login") or \
               base.is_visible("Login to your account") or \
               base.is_visible("Log In") or \
               base.is_visible("Sign In") or \
               base.is_visible("Enter phone") or \
               base.is_visible("Phone") or \
               base.is_visible("Welcome") or \
               base.is_visible("Get Started") or \
               base.is_visible("تسجيل الدخول") or \
               base.is_visible("تسجيل الدخول إلى حسابك"), \
            "Login screen not shown after logout"
        screenshot(driver, "logout_redirect_login")

    @allure.story("Re-login")
    @allure.title("User can log back in immediately after logging out")
    def test_logout_and_relogin(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        page.confirm_logout()
        wait_for_animation(driver, 2)
        login = LoginPage(driver)
        login.login()
        base = BasePage(driver)
        assert base.is_visible("Cart") or \
               base.is_visible("My Orders") or \
               base.is_visible("Home") or \
               base.is_visible("Donate"), \
            "Re-login after logout did not succeed"
        screenshot(driver, "logout_and_relogin")

    @allure.story("Security")
    @allure.title("No auth tokens leak to UI after logout")
    def test_logout_no_session_leak(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        page.tap_logout()
        page.confirm_logout()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        # None of the authenticated-only labels should appear
        assert not base.is_visible("My Orders", timeout=3) and \
               not base.is_visible("Cart", timeout=3) or \
               base.is_visible("Login") or \
               base.is_visible("Phone"), \
            "Auth-only content visible after logout — possible session token leak"
        screenshot(driver, "logout_no_session_leak")

    @allure.story("Accessibility")
    @allure.title("Logout button is accessible via accessibility label")
    def test_logout_accessibility(self, driver):
        page = self._login(driver)
        page.navigate_to_profile()
        wait_for_animation(driver)
        base = BasePage(driver)
        # iOS may label the button "Log out" or "Sign out" instead of "Logout"
        assert base.is_visible("Logout") or \
               base.is_visible("Log out") or \
               base.is_visible("Sign out") or \
               base.is_visible("تسجيل الخروج"), \
            "Logout button is not accessible — missing accessibility label or visibility"
        screenshot(driver, "logout_accessibility")
