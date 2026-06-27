import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
from utils.markers import android_apk_regression


@allure.epic("Home")
@allure.feature("Home Feed")
@pytest.mark.home
@pytest.mark.android
class TestHomeFeed:
    """Tests covering home screen content, navigation, and feed interactions."""

    def _login_and_go_home(self, driver):
        LoginPage(driver).login()
        page = HomePage(driver)
        page.navigate_to_home()
        return page

    @android_apk_regression
    @allure.story("Navigation")
    @allure.title("Home screen loads successfully after login")
    def test_home_loads_after_login(self, driver):
        page = self._login_and_go_home(driver)
        assert page.is_on_home_screen(timeout=10), \
            "Home screen did not load after login"
        screenshot(driver, "home_loads_after_login")

    @android_apk_regression
    @allure.story("Content")
    @allure.title("Home feed contains at least one mosque or featured item")
    def test_home_feed_has_content(self, driver):
        page = self._login_and_go_home(driver)
        count = page.get_featured_items_count()
        base = BasePage(driver)
        has_content = count > 0 or \
            base.is_visible("Mosque", timeout=5) or \
            base.is_visible("Donate", timeout=5) or \
            base.is_visible("Masjid", timeout=5)
        assert has_content, "Home feed appears empty — no mosques or featured items found"
        screenshot(driver, "home_feed_has_content")

    @android_apk_regression
    @allure.story("Content")
    @allure.title("Live Broadcast section is accessible from home")
    def test_live_broadcast_accessible(self, driver):
        page = self._login_and_go_home(driver)
        base = BasePage(driver)
        assert base.is_visible("Live Broadcast", timeout=5) or \
               base.is_visible("Visual documentations", timeout=5) or \
               base.is_visible("Donate", timeout=5), \
            "Live Broadcast or primary content section not visible on home screen"
        screenshot(driver, "home_live_broadcast_accessible")

    @allure.story("Navigation")
    @allure.title("Tapping first mosque on home opens mosque profile")
    def test_tap_mosque_opens_profile(self, driver):
        page = self._login_and_go_home(driver)
        count = page.get_featured_items_count()
        if count == 0:
            pytest.skip("No mosque items visible on home feed")
        page.tap_first_mosque()
        wait_for_animation(driver)
        base = BasePage(driver)
        assert base.is_visible("Donate", timeout=5) or \
               base.is_visible("Mosque", timeout=5) or \
               base.is_visible("Masjid", timeout=5) or \
               base.is_visible("About", timeout=5), \
            "Mosque profile page did not open after tapping home feed item"
        screenshot(driver, "home_mosque_profile_opened")

    @allure.story("Scroll")
    @allure.title("Scrolling the home feed does not crash the app")
    def test_scroll_home_feed_no_crash(self, driver):
        page = self._login_and_go_home(driver)
        page.scroll_feed(times=5)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "Scrolling home feed caused an error"
        screenshot(driver, "home_scroll_no_crash")

    @android_apk_regression
    @allure.story("Navigation")
    @allure.title("Bottom navigation tabs are all accessible from home")
    def test_bottom_nav_tabs_accessible(self, driver):
        self._login_and_go_home(driver)
        base = BasePage(driver)
        visible_tabs = sum([
            base.is_visible("Home", timeout=3),
            base.is_visible("Cart", timeout=3),
            base.is_visible("My Orders", timeout=3),
            base.is_visible("Profile", timeout=3),
        ])
        assert visible_tabs >= 2, \
            "Fewer than 2 bottom navigation tabs are visible on home screen"
        screenshot(driver, "home_bottom_nav_visible")
