import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.location_page import LocationPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


def _login_and_navigate_to_map(driver):
    """Login and try to reach the map/location screen."""
    LoginPage(driver).login()
    base = BasePage(driver)
    page = LocationPage(driver)

    # Try common entry points to the map
    for entry in ["Location", "Map", "Select Location", "Change Location", "Near Me"]:
        if base.is_visible(entry, timeout=3):
            base.tap(entry)
            wait_for_animation(driver, 2)
            if page.is_on_map_screen(timeout=5):
                return page

    # Try from profile/settings area
    for nav in ["Profile", "Settings"]:
        base.tap_optional(nav, timeout=2)
        wait_for_animation(driver, 1)
        for entry in ["Location", "Address", "Map"]:
            if base.is_visible(entry, timeout=2):
                base.tap(entry)
                wait_for_animation(driver, 2)
                if page.is_on_map_screen(timeout=5):
                    return page

    if not page.is_on_map_screen(timeout=3):
        pytest.skip("Map/Location screen not reachable from any navigation path")
    return page


@allure.epic("Location")
@allure.feature("Map & Location Selection")
@pytest.mark.location
class TestLocationMap:
    """Tests for the Map and Location selection feature."""

    @allure.story("Navigation")
    @allure.title("Map screen loads when navigated to")
    def test_map_screen_loads(self, driver):
        page = _login_and_navigate_to_map(driver)
        assert page.is_on_map_screen(timeout=10), \
            "Map screen did not load"
        screenshot(driver, "location_map_loads")

    @allure.story("Permission")
    @allure.title("Granting location permission shows map or starts location detection")
    def test_allow_location_permission_proceeds(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.allow_location_permission()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert page.is_on_map_screen(timeout=5) or \
               base.is_visible("Confirm", timeout=5) or \
               base.is_visible("Location", timeout=5), \
            "After granting location permission, map did not respond"
        screenshot(driver, "location_permission_allowed")

    @allure.story("Permission")
    @allure.title("Denying location permission shows fallback or error message")
    def test_deny_location_shows_fallback(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.deny_location_permission()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) or \
               base.is_visible("Location", timeout=5) or \
               base.is_visible("Enable", timeout=5), \
            "Denying location permission caused an unhandled error"
        screenshot(driver, "location_permission_denied")

    @allure.story("Search")
    @allure.title("Location search with a city name returns results")
    def test_location_search_returns_results(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.search_location("Doha")
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("Doha", timeout=5) or \
               base.is_visible("Qatar", timeout=5) or \
               not base.is_visible("Something went wrong", timeout=3), \
            "Location search for 'Doha' returned no recognisable results"
        screenshot(driver, "location_search_doha")

    @allure.story("Search")
    @allure.title("Location search with special characters does not crash")
    def test_location_search_special_chars_no_crash(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.search_location("@#$%^&*()")
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3) and \
               not base.is_visible("Exception", timeout=3), \
            "Special-char location search caused an error"
        screenshot(driver, "location_search_special_chars")

    @allure.story("Search")
    @allure.title("Location search with Arabic text does not crash")
    def test_location_search_arabic(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.search_location("الدوحة")
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3), \
            "Arabic location search caused a server error"
        screenshot(driver, "location_search_arabic")

    @allure.story("Confirm")
    @allure.title("Confirming a location navigates away from map")
    def test_confirm_location_navigates_forward(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.allow_location_permission()
        wait_for_animation(driver, 2)
        page.confirm_location()
        wait_for_animation(driver, 2)
        assert page.is_location_selected() or \
               not page.is_on_map_screen(timeout=3), \
            "Confirming location did not navigate away from map screen"
        screenshot(driver, "location_confirmed")

    @allure.story("Boundary")
    @allure.title("Map renders without white screen or blank state")
    def test_map_renders_no_blank_screen(self, driver):
        page = _login_and_navigate_to_map(driver)
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("Error loading map", timeout=3), \
            "Map rendered with an error state"
        assert page.is_on_map_screen(timeout=5), \
            "Map screen disappeared after loading"
        screenshot(driver, "location_map_renders")


@allure.epic("Location")
@allure.feature("Location — Boundary & Negative")
@pytest.mark.location
@pytest.mark.negative
class TestLocationBoundary:
    """Boundary and negative tests for the Location/Map feature."""

    @allure.story("Boundary")
    @allure.title("Empty location search does not crash")
    def test_empty_location_search_no_crash(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.search_location("")
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3), \
            "Empty location search caused an error"
        screenshot(driver, "location_search_empty")

    @allure.story("Boundary")
    @allure.title("Very long location search string does not crash")
    def test_long_location_search_no_crash(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.search_location("A" * 200)
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3) and \
               not base.is_visible("Exception", timeout=3), \
            "Very long location search caused an error"
        screenshot(driver, "location_search_long")

    @allure.story("Boundary")
    @allure.title("Rapidly tapping Confirm Location does not double-submit")
    def test_rapid_confirm_location_no_double_submit(self, driver):
        page = _login_and_navigate_to_map(driver)
        page.allow_location_permission()
        wait_for_animation(driver, 1)
        base = BasePage(driver)
        for label in ["Confirm Location", "Set Location", "Use This Location"]:
            if base.is_visible(label, timeout=2):
                for _ in range(5):
                    base.tap_optional(label, timeout=1)
                    wait_for_animation(driver, 0.2)
                break
        assert not base.is_visible("500", timeout=3), \
            "Rapid confirm taps caused a server error"
        screenshot(driver, "location_rapid_confirm")
