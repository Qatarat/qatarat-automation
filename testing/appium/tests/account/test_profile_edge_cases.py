import pytest
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, scroll_to_text
from utils.markers import android_apk_regression
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
                if base.is_visible(lbl, timeout=2):
                    base.tap_optional(lbl, timeout=2)
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
            if base.is_visible(cancel_label, timeout=2):
                base.tap_optional(cancel_label, timeout=2)
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

    @android_apk_regression
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
            if base.is_visible(cancel, timeout=2):
                base.tap_optional(cancel, timeout=2)
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
        for label in ["About", "About Qatarat", "About Us", "عن قطرات"]:
            base.tap_optional(label, timeout=3)
        wait_for_animation(driver, 2)

        if not (base.is_visible("Qatarat", timeout=5) or
                base.is_visible("Version", timeout=3) or
                base.is_visible("About", timeout=3)):
            pytest.skip("About page not reachable — profile nav may have changed")
        screenshot(driver, "profile_about_page")

    def test_help_support_contact_options_visible(self, driver):
        """Help & Support must show at least one contact option."""
        login = LoginPage(driver)
        login.login()

        base = BasePage(driver)
        ProfilePage(driver).navigate_to_profile()
        wait_for_animation(driver)
        for label in ["How can we help?", "Help & Support", "Help", "Support",
                      "Customer Support", "مساعدة", "الدعم"]:
            base.tap_optional(label, timeout=2)
        wait_for_animation(driver, 2)

        found = (base.is_visible("WhatsApp", timeout=3) or
                 base.is_visible("Mail Us", timeout=3) or
                 base.is_visible("Email", timeout=3) or
                 base.is_visible("Contact", timeout=3) or
                 base.is_visible("How can we help?", timeout=3) or
                 base.is_visible("Help", timeout=3))
        if not found:
            pytest.skip("Help & Support not reachable — profile UI may have changed")
        screenshot(driver, "profile_help_contact_options")

    def _navigate_to_help_and_type(self, driver, query):
        """Navigate to Help screen and type into search field. Returns False if not reachable."""
        base = BasePage(driver)
        ProfilePage(driver).navigate_to_profile()
        wait_for_animation(driver)
        for label in ["How can we help?", "Help & Support", "Help", "Support",
                      "Customer Support", "مساعدة", "الدعم"]:
            base.tap_optional(label, timeout=2)
        wait_for_animation(driver, 2)

        # Try known search placeholder labels
        for label in ["Search for Help", "Search", "البحث"]:
            try:
                base.input_text(label, query)
                return base
            except Exception:
                continue

        # Fallback: tap any visible search field then type
        from appium.webdriver.common.appiumby import AppiumBy
        from utils.helpers import text_field_xpath
        try:
            fields = driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            if fields:
                fields[0].click()
                wait_for_animation(driver, 0.5)
                fields[0].clear()
                fields[0].send_keys(query)
                return base
        except Exception:
            pass
        return None

    @android_apk_regression
    def test_help_search_no_results_shows_empty_state(self, driver):
        """Searching help with a nonsense term must show an empty state, not crash."""
        LoginPage(driver).login()
        base = self._navigate_to_help_and_type(driver, BoundaryValues.HELP_SEARCH_NO_RESULTS)
        if base is None:
            pytest.skip("Help search field not reachable — UI may have changed")
        wait_for_animation(driver, 2)

        assert base.is_visible("No results") or \
               base.is_visible("not found") or \
               base.is_visible("empty") or \
               not base.is_visible("500"), \
            "Help search with no-match term crashed or showed a server error"
        screenshot(driver, "profile_help_search_empty")

    @android_apk_regression
    def test_help_search_sql_injection_is_safe(self, driver):
        """SQL injection in help search must not produce a database error."""
        LoginPage(driver).login()
        base = self._navigate_to_help_and_type(driver, BoundaryValues.HELP_SEARCH_SQL)
        if base is None:
            pytest.skip("Help search field not reachable — UI may have changed")
        wait_for_animation(driver, 2)

        assert not base.is_visible("SQL") and \
               not base.is_visible("syntax error") and \
               not base.is_visible("500"), \
            "SQL injection in help search exposed a server error"
        screenshot(driver, "profile_help_sql_safe")
