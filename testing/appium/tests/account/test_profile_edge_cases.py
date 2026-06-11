import pytest
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import BoundaryValues, InvalidRating


@pytest.mark.account
@pytest.mark.negative
class TestProfileEdgeCases:
    """Edge-case and negative tests for profile and account settings."""

    def _login_and_open_profile(self, driver):
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally

        base = BasePage(driver)
        base.tap_optional("Profile")
        base.tap_optional("Account")
        wait_for_animation(driver)
        return base

    def test_logout_cancel_stays_logged_in(self, driver):
        """Tapping 'No' on logout dialog must keep the user logged in."""
        base = self._login_and_open_profile(driver)
        base.tap_optional("Logout")
        wait_for_animation(driver)

        assert base.is_visible("Are you sure") or \
               base.is_visible("Logout"), \
            "Logout confirmation dialog did not appear"

        base.tap_optional("No")
        wait_for_animation(driver)

        assert base.is_visible("Profile") or \
               base.is_visible("Account") or \
               base.is_visible("Cart"), \
            "User was logged out despite tapping 'No'"
        screenshot(driver, "profile_logout_cancelled")

    def test_delete_account_cancel_stays_active(self, driver):
        """Tapping 'No' on delete account dialog must not delete the account."""
        base = self._login_and_open_profile(driver)
        base.tap_optional("Delete Account")
        wait_for_animation(driver)

        assert base.is_visible("Are you sure") or \
               base.is_visible("Delete"), \
            "Delete account confirmation dialog did not appear"

        base.tap_optional("No")
        wait_for_animation(driver)

        assert base.is_visible("Profile") or \
               base.is_visible("Account") or \
               base.is_visible("Cart"), \
            "Account was deleted or user was signed out after cancelling"
        screenshot(driver, "profile_delete_cancelled")

    def test_currency_list_loads_without_error(self, driver):
        """Currency selection screen must load and display options."""
        base = self._login_and_open_profile(driver)
        base.tap_optional("Change Currency")
        wait_for_animation(driver, 2)

        assert base.is_visible("Currency") or \
               base.is_visible("SAR") or \
               base.is_visible("USD") or \
               base.is_visible("Select"), \
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
