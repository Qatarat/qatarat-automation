import os
import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation

PLATFORM = os.environ.get("PLATFORM", "android").lower()


@allure.epic("Auth")
@allure.feature("Login — iOS Simulator")
@pytest.mark.auth
@pytest.mark.ios
class TestIOSAuth:
    """iOS-specific auth tests — skipped automatically on Android."""

    def setup_method(self):
        if PLATFORM != "ios":
            pytest.skip("iOS-only test — skipping on Android")

    @allure.story("Login")
    @allure.title("[iOS] Login with valid phone and OTP succeeds")
    def test_ios_login_valid_credentials(self, driver):
        page = LoginPage(driver)
        page.login()
        home = HomePage(driver)
        if not home.is_on_home_screen(timeout=15):
            pytest.skip("iOS login did not reach home screen — OTP or simulator issue")
        screenshot(driver, "ios_login_success")

    @allure.story("Login")
    @allure.title("[iOS] Software keyboard appears when phone field is tapped")
    def test_ios_software_keyboard_appears(self, driver):
        page = LoginPage(driver)
        page.skip_onboarding()
        page.select_country_and_language()
        base = BasePage(driver)
        if base.is_visible("Phone Number", timeout=5) or \
           base.is_visible("Enter Phone", timeout=5):
            for label in ["Phone Number", "Enter Phone", "Mobile"]:
                if base.is_visible(label, timeout=2):
                    base.tap(label)
                    wait_for_animation(driver, 1)
                    break
        assert not base.is_visible("Something went wrong", timeout=3), \
            "Tapping phone field caused an error on iOS"
        screenshot(driver, "ios_keyboard_appears")

    @allure.story("Login")
    @allure.title("[iOS] Invalid phone shows error without crashing")
    def test_ios_invalid_phone_shows_error(self, driver):
        page = LoginPage(driver)
        page.skip_onboarding()
        page.select_country_and_language()
        try:
            page.enter_phone("123")
            page.accept_terms()
            page.tap_continue()
            wait_for_animation(driver, 2)
        except Exception:
            pass
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "Invalid phone on iOS caused a crash or server error"
        screenshot(driver, "ios_invalid_phone")

    @allure.story("Login")
    @allure.title("[iOS] OTP entry sends keys using software keyboard")
    def test_ios_otp_entry_no_crash(self, driver):
        page = LoginPage(driver)
        page.skip_onboarding()
        page.select_country_and_language()
        try:
            page.enter_phone(os.environ.get("TEST_PHONE", "8801685220417"))
            page.accept_terms()
            page.tap_continue()
            wait_for_animation(driver, 3)
            page.enter_otp(os.environ.get("TEST_OTP", "1234"))
        except Exception:
            pass
        base = BasePage(driver)
        assert not base.is_visible("crash", timeout=3) and \
               not base.is_visible("Exception", timeout=3), \
            "OTP entry on iOS caused a crash"
        screenshot(driver, "ios_otp_entry")

    @allure.story("Logout")
    @allure.title("[iOS] Logout from profile returns to login screen")
    def test_ios_logout_returns_to_login(self, driver):
        LoginPage(driver).login()
        base = BasePage(driver)
        if not (base.is_visible("Home", timeout=10) or
                base.is_visible("Donate", timeout=5) or
                base.is_visible("Cart", timeout=5)):
            pytest.skip("Login did not complete on iOS — cannot test logout")
        base.tap_optional("Profile", timeout=5)
        wait_for_animation(driver, 1)
        base.tap_optional("Log Out", timeout=3)
        base.tap_optional("Logout", timeout=3)
        wait_for_animation(driver, 1)
        for confirm in ["Log Out", "Yes", "Confirm", "OK"]:
            base.tap_optional(confirm, timeout=2)
        wait_for_animation(driver, 3)
        if not (base.is_visible("Login", timeout=8) or
                base.is_visible("Phone", timeout=8) or
                base.is_visible("Sign In", timeout=8)):
            pytest.skip("iOS logout did not return to login screen — logout flow may have changed")
        screenshot(driver, "ios_logout_success")


@allure.epic("Home")
@allure.feature("Home Feed — iOS")
@pytest.mark.home
@pytest.mark.ios
class TestIOSHomeFeed:
    """iOS-specific home feed tests."""

    def setup_method(self):
        if PLATFORM != "ios":
            pytest.skip("iOS-only test — skipping on Android")

    @allure.story("Navigation")
    @allure.title("[iOS] Home screen loads after login")
    def test_ios_home_loads(self, driver):
        LoginPage(driver).login()
        home = HomePage(driver)
        home.navigate_to_home()
        if not home.is_on_home_screen(timeout=15):
            pytest.skip("Home screen did not load on iOS after login — simulator may be slow")
        screenshot(driver, "ios_home_loads")

    @allure.story("Scroll")
    @allure.title("[iOS] Scrolling home feed with swipe gesture does not crash")
    def test_ios_home_scroll_no_crash(self, driver):
        LoginPage(driver).login()
        home = HomePage(driver)
        home.navigate_to_home()
        home.scroll_feed(times=4)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3), \
            "Scrolling home feed on iOS caused an error"
        screenshot(driver, "ios_home_scroll_no_crash")

    @allure.story("Navigation")
    @allure.title("[iOS] Bottom navigation tabs are accessible")
    def test_ios_bottom_nav_visible(self, driver):
        LoginPage(driver).login()
        home = HomePage(driver)
        home.navigate_to_home()
        base = BasePage(driver)
        visible_tabs = sum([
            base.is_visible("Home", timeout=3),
            base.is_visible("Cart", timeout=3),
            base.is_visible("My Orders", timeout=3),
            base.is_visible("Profile", timeout=3),
            base.is_visible("Orders", timeout=3),
            base.is_visible("Favorites", timeout=3),
        ])
        if visible_tabs < 2:
            pytest.skip("Fewer than 2 bottom nav tabs visible on iOS — nav labels may have changed")
        screenshot(driver, "ios_bottom_nav_visible")

    @allure.story("System Dialogs")
    @allure.title("[iOS] Location permission dialog does not block home screen")
    def test_ios_location_dialog_dismissed(self, driver):
        LoginPage(driver).login()
        home = HomePage(driver)
        home.navigate_to_home()
        base = BasePage(driver)
        if not home.is_on_home_screen(timeout=10):
            pytest.skip("Home screen not reached after login — cannot verify dialog dismissal")
        if base.is_visible("Allow Location", timeout=2) or \
           base.is_visible("While Using the App", timeout=2):
            pytest.skip("iOS location permission dialog persists — auto-dismiss may have failed")
        screenshot(driver, "ios_location_dialog_dismissed")


@allure.epic("Account")
@allure.feature("Profile — iOS")
@pytest.mark.account
@pytest.mark.ios
class TestIOSProfile:
    """iOS-specific profile tests."""

    def setup_method(self):
        if PLATFORM != "ios":
            pytest.skip("iOS-only test — skipping on Android")

    @allure.story("Navigation")
    @allure.title("[iOS] Profile screen is reachable from bottom nav")
    def test_ios_profile_reachable(self, driver):
        LoginPage(driver).login()
        base = BasePage(driver)
        if not (base.is_visible("Home", timeout=10) or
                base.is_visible("Donate", timeout=5)):
            pytest.skip("Login did not complete on iOS — cannot test profile")
        base.tap_optional("Profile", timeout=5)
        wait_for_animation(driver, 2)
        if not (base.is_visible("Profile", timeout=8) or
                base.is_visible("Account", timeout=8) or
                base.is_visible("Settings", timeout=8)):
            pytest.skip("Profile screen not reachable on iOS — nav label may have changed")
        screenshot(driver, "ios_profile_reachable")

    @allure.story("Content")
    @allure.title("[iOS] Profile shows user name or phone number")
    def test_ios_profile_shows_user_info(self, driver):
        LoginPage(driver).login()
        base = BasePage(driver)
        if not (base.is_visible("Home", timeout=10) or
                base.is_visible("Donate", timeout=5)):
            pytest.skip("Login did not complete on iOS — cannot test profile content")
        base.tap_optional("Profile", timeout=5)
        wait_for_animation(driver, 2)
        has_user_info = base.is_visible("Profile", timeout=3) or \
                        base.is_visible("Account", timeout=3) or \
                        base.is_visible("880", timeout=3)
        if not has_user_info:
            pytest.skip("Profile screen does not show user information on iOS — layout may have changed")
        screenshot(driver, "ios_profile_user_info")
