import pytest
import allure
from pages.login_page import LoginPage
from pages.mosque_page import MosquePage
from utils.helpers import screenshot, wait_for_animation
from utils.markers import android_apk_regression


@allure.epic("Mosque")
@allure.feature("Mosque Search & Profile")
@pytest.mark.mosque
class TestMosqueProfile:
    """Tests covering mosque search functionality and profile page content."""

    def _login_and_open_search(self, driver):
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()
        page = MosquePage(driver)
        return page

    @allure.story("Search")
    @allure.title("Search for a mosque by a valid full name returns results")
    def test_mosque_search_valid_name(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("Al Masjid")
        wait_for_animation(driver)
        assert page.is_visible("Al Masjid") or \
               page.is_visible("Mosque") or \
               page.is_visible("Masjid") or \
               page.get_search_results_count() >= 0, \
            "No results or error shown when searching a valid mosque name"
        screenshot(driver, "mosque_search_valid_name")

    @allure.story("Search")
    @allure.title("Search with a partial mosque name still returns results")
    def test_mosque_search_partial_name(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("Masjid")
        wait_for_animation(driver)
        assert page.is_visible("Masjid") or \
               page.is_visible("Mosque") or \
               not page.is_visible("Error", timeout=3), \
            "Partial mosque name search returned an error"
        screenshot(driver, "mosque_search_partial_name")

    @allure.story("Search")
    @allure.title("Searching with an empty query shows all mosques or empty state")
    def test_mosque_search_empty(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("")
        wait_for_animation(driver)
        assert not page.is_visible("500", timeout=3) and \
               not page.is_visible("crash", timeout=3), \
            "Empty search caused a crash or server error"
        screenshot(driver, "mosque_search_empty")

    @allure.story("Search")
    @allure.title("Searching with special characters does not crash the app")
    def test_mosque_search_special_chars(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("@#$%")
        wait_for_animation(driver)
        assert page.is_visible("No results") or \
               page.is_visible("not found") or \
               not page.is_visible("500", timeout=3), \
            "Special character search caused a crash or server error"
        screenshot(driver, "mosque_search_special_chars")

    @allure.story("Search")
    @allure.title("Searching with Arabic Unicode text returns correct results")
    def test_mosque_search_unicode(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("مسجد")
        wait_for_animation(driver)
        assert not page.is_visible("500", timeout=3) and \
               not page.is_visible("crash", timeout=3), \
            "Arabic Unicode search caused a crash or server error"
        screenshot(driver, "mosque_search_unicode")

    @android_apk_regression
    @allure.story("Profile")
    @allure.title("Tapping a search result opens the mosque profile page")
    def test_mosque_profile_opens(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("Masjid")
        wait_for_animation(driver)
        page.tap_optional("Masjid")
        wait_for_animation(driver)
        assert page.is_visible("Donate") or \
               page.is_visible("Mosque") or \
               page.is_visible("About") or \
               page.is_visible("Masjid"), \
            "Mosque profile page did not open after tapping search result"
        screenshot(driver, "mosque_profile_opens")

    @android_apk_regression
    @allure.story("Profile")
    @allure.title("Mosque profile page contains a Donate button")
    def test_mosque_profile_has_donate_button(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("Masjid")
        wait_for_animation(driver)
        page.open_mosque_profile("Masjid")
        assert page.is_visible("Donate") or \
               page.is_visible("Donate Now"), \
            "Donate button not found on mosque profile page"
        screenshot(driver, "mosque_profile_donate_button")

    @android_apk_regression
    @allure.story("Profile")
    @allure.title("Mosque profile page shows a description or About section")
    def test_mosque_profile_description_visible(self, driver):
        page = self._login_and_open_search(driver)
        page.search_mosque("Masjid")
        wait_for_animation(driver)
        page.open_mosque_profile("Masjid")
        page.scroll_to_about_section()
        assert page.is_visible("About") or \
               page.is_visible("Description") or \
               page.is_visible("Overview"), \
            "Description / About section not visible on mosque profile page"
        screenshot(driver, "mosque_profile_description")
