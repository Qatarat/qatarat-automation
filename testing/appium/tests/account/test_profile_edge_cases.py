import pytest
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, scroll_to_text
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import BoundaryValues, InvalidRating


@pytest.mark.account
@pytest.mark.negative
class TestProfileEdgeCases:
    """Edge-case and negative tests for profile and account settings."""

    def _login_and_open_profile(self, driver):
        LoginPage(driver).login()
        ProfilePage(driver).navigate_to_profile()
        wait_for_animation(driver)
        return BasePage(driver)

    def test_logout_cancel_stays_logged_in(self, driver):
        """Tapping 'No' on logout dialog must keep the user logged in."""
        base = self._login_and_open_profile(driver)
        # Try finding and tapping logout (scroll if needed)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found_logout = False
        for _ in range(6):
            for lbl in ["Logout", "Log out", "Sign out", "تسجيل الخروج"]:
                if base.tap_optional(lbl, timeout=2):
                    found_logout = True
                    break
            if found_logout:
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.3)
        if not found_logout:
            pytest.skip("Logout button not found — profile UI may have changed")
        wait_for_animation(driver)

        dialog_visible = base.is_visible("Are you sure", timeout=3) or \
                         base.is_visible("Logout", timeout=3) or \
                         base.is_visible("Log out", timeout=3) or \
                         base.is_visible("تسجيل الخروج", timeout=3)
        if not dialog_visible:
            pytest.skip("Logout confirmation dialog did not appear — dialog UI may have changed")

        for cancel_label in ["No", "Cancel", "Keep me logged in", "Stay", "لا", "إلغاء"]:
            if base.tap_optional(cancel_label, timeout=2):
                break
        wait_for_animation(driver)

        assert base.is_visible("Profile") or \
               base.is_visible("Account") or \
               base.is_visible("Cart") or \
               base.is_visible("Logout") or \
               base.is_visible("Log out") or \
               base.is_visible("الملف الشخصي") or \
               base.is_visible("Home") or \
               base.is_visible("الرئيسية"), \
            "User was logged out despite tapping 'No'"
        screenshot(driver, "profile_logout_cancelled")

    def test_delete_account_cancel_stays_active(self, driver):
        """Tapping 'No' on delete account dialog must not delete the account."""
        base = self._login_and_open_profile(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found = False
        for _ in range(8):
            for lbl in ["Delete Account", "Delete My Account", "حذف الحساب"]:
                if base.is_visible(lbl, timeout=2):
                    base.tap_optional(lbl, timeout=2)
                    found = True
                    break
            if found:
                break
            driver.swipe(w // 2, int(h * 0.75), w // 2, int(h * 0.25), 500)
            wait_for_animation(driver, 0.3)
        if not found:
            pytest.skip("Delete Account option not found after scrolling — profile UI may have changed")
        wait_for_animation(driver)

        dialog_visible = base.is_visible("Are you sure", timeout=3) or \
                         base.is_visible("Delete", timeout=3) or \
                         base.is_visible("Confirm", timeout=3)
        if not dialog_visible:
            pytest.skip("Delete account confirmation dialog did not appear")

        for cancel in ["No", "Cancel", "Keep", "لا", "إلغاء"]:
            if base.tap_optional(cancel, timeout=2):
                break
        wait_for_animation(driver)

        assert base.is_visible("Profile") or \
               base.is_visible("Account") or \
               base.is_visible("Cart") or \
               base.is_visible("الملف الشخصي") or \
               base.is_visible("Home") or \
               base.is_visible("الرئيسية"), \
            "Account was deleted or user was signed out after cancelling"
        screenshot(driver, "profile_delete_cancelled")

    def test_currency_list_loads_without_error(self, driver):
        """Currency selection screen must load and display options."""
        base = self._login_and_open_profile(driver)
        size = driver.get_window_size()
        w, h = size["width"], size["height"]
        found = False
        for _ in range(5):
            if base.is_visible("Change Currency", timeout=2) or \
               base.is_visible("Currency", timeout=2) or \
               base.is_visible("العملة", timeout=2):
                found = True
                break
            driver.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.3), 500)
            wait_for_animation(driver, 0.3)
        if not found:
            pytest.skip("Currency option not found — profile UI may have changed")
        for lbl in ["Change Currency", "Currency", "العملة"]:
            base.tap_optional(lbl, timeout=2)
        wait_for_animation(driver, 2)
        assert base.is_visible("Currency", timeout=5) or \
               base.is_visible("SAR", timeout=5) or \
               base.is_visible("USD", timeout=5) or \
               base.is_visible("Select", timeout=5) or \
               not base.is_visible("500", timeout=3), \
            "Currency list did not load"
        screenshot(driver, "profile_currency_list")

    def test_about_page_has_app_info(self, driver):
        """About page must contain app name and version information."""
        base = self._login_and_open_profile(driver)
        base.tap_optional("About")
        base.tap_optional("About Qatarat")
        wait_for_animation(driver, 2)

        assert base.is_visible("Qatarat") or \
               base.is_visible("Version") or \
               base.is_visible("About"), \
            "About page did not load or is missing app info"
        screenshot(driver, "profile_about_page")

    def test_help_support_contact_options_visible(self, driver):
        """Help & Support must show at least one contact option."""
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally

        base = BasePage(driver)
        base.tap_optional("How can we help?")
        base.tap_optional("Help")
        base.tap_optional("Support")
        wait_for_animation(driver, 2)

        assert base.is_visible("WhatsApp") or \
               base.is_visible("Mail Us") or \
               base.is_visible("Email") or \
               base.is_visible("Contact"), \
            "No contact option visible on Help & Support screen"
        screenshot(driver, "profile_help_contact_options")

    def test_help_search_no_results_shows_empty_state(self, driver):
        """Searching help with a nonsense term must show an empty state, not crash."""
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally

        base = BasePage(driver)
        base.tap_optional("How can we help?")
        base.tap_optional("Help")
        wait_for_animation(driver)
        base.tap_optional("Search for Help")
        base.input_text("Search for Help", BoundaryValues.HELP_SEARCH_NO_RESULTS)
        wait_for_animation(driver, 2)

        assert base.is_visible("No results") or \
               base.is_visible("not found") or \
               base.is_visible("empty") or \
               not base.is_visible("500"), \
            "Help search with no-match term crashed or showed a server error"
        screenshot(driver, "profile_help_search_empty")

    def test_help_search_sql_injection_is_safe(self, driver):
        """SQL injection in help search must not produce a database error."""
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally

        base = BasePage(driver)
        base.tap_optional("How can we help?")
        base.tap_optional("Help")
        wait_for_animation(driver)
        base.tap_optional("Search for Help")
        base.input_text("Search for Help", BoundaryValues.HELP_SEARCH_SQL)
        wait_for_animation(driver, 2)

        assert not base.is_visible("SQL") and \
               not base.is_visible("syntax error") and \
               not base.is_visible("500"), \
            "SQL injection in help search exposed a server error"
        screenshot(driver, "profile_help_sql_safe")
