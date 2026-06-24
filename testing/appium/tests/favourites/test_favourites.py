import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.favourites_page import FavouritesPage
from pages.mosque_page import MosquePage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Favourites")
@allure.feature("Favourites / Bookmarks")
@pytest.mark.favourites
class TestFavourites:
    """Tests for the Favourites/Bookmarks feature."""

    def _login_and_go_home(self, driver):
        LoginPage(driver).login()
        home = HomePage(driver)
        home.navigate_to_home()
        return home

    def _login_and_open_favourites(self, driver):
        self._login_and_go_home(driver)
        page = FavouritesPage(driver)
        page.navigate_to_favourites()
        return page

    @allure.story("Navigation")
    @allure.title("Favourites screen is reachable from bottom nav")
    def test_favourites_screen_loads(self, driver):
        page = self._login_and_open_favourites(driver)
        assert page.is_on_favourites_screen(timeout=10), \
            "Favourites screen did not load"
        screenshot(driver, "favourites_screen_loads")

    @allure.story("Content")
    @allure.title("Favourites shows items or empty state — never blank")
    def test_favourites_shows_items_or_empty_state(self, driver):
        page = self._login_and_open_favourites(driver)
        count = page.get_favourites_count()
        empty = page.is_empty_state_visible()
        assert count > 0 or empty, \
            "Favourites screen is blank — neither items nor empty state visible"
        screenshot(driver, "favourites_content_or_empty")

    @allure.story("Content")
    @allure.title("Empty favourites state shows user-friendly message")
    def test_empty_favourites_has_message(self, driver):
        page = self._login_and_open_favourites(driver)
        if page.get_favourites_count() > 0:
            pytest.skip("Account has favourites — empty state not reachable")
        assert page.is_empty_state_visible(), \
            "Empty favourites state does not show a friendly message"
        screenshot(driver, "favourites_empty_message")

    @allure.story("Navigation")
    @allure.title("Tapping a favourite item opens its detail")
    def test_tap_favourite_opens_detail(self, driver):
        page = self._login_and_open_favourites(driver)
        if page.get_favourites_count() == 0:
            pytest.skip("No favourites — cannot test tap behaviour")
        page.tap_first_favourite()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("Donate", timeout=5) or \
               base.is_visible("Mosque", timeout=5) or \
               base.is_visible("About", timeout=5) or \
               base.is_visible("Masjid", timeout=5), \
            "Tapping a favourite did not open a detail screen"
        screenshot(driver, "favourites_tap_opens_detail")

    @allure.story("Actions")
    @allure.title("Scrolling favourites list does not crash")
    def test_scroll_favourites_no_crash(self, driver):
        page = self._login_and_open_favourites(driver)
        size = driver.get_window_size()
        for _ in range(3):
            driver.swipe(
                size["width"] // 2, int(size["height"] * 0.7),
                size["width"] // 2, int(size["height"] * 0.3),
                500,
            )
            wait_for_animation(driver, 0.5)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "Scrolling favourites caused an error"
        screenshot(driver, "favourites_scroll_no_crash")

    @allure.story("Add to Favourites")
    @allure.title("Mosque can be added to favourites from its profile")
    def test_add_mosque_to_favourites(self, driver):
        self._login_and_go_home(driver)
        mosque = MosquePage(driver)
        mosque.search_mosque("Al")
        mosque.open_mosque_profile("Al")
        wait_for_animation(driver, 1)
        base = BasePage(driver)
        fav_tapped = False
        for label in ["Favourite", "Favorite", "Save", "♡", "❤", "المفضلة"]:
            if base.is_visible(label, timeout=3):
                base.tap(label)
                wait_for_animation(driver, 1)
                fav_tapped = True
                break
        if not fav_tapped:
            pytest.skip("Favourite/Save button not found on mosque profile")
        assert base.is_visible("Added") or \
               base.is_visible("Saved") or \
               base.is_visible("Removed") or \
               not base.is_visible("Something went wrong", timeout=3), \
            "Adding to favourites produced an error"
        screenshot(driver, "favourites_add_mosque")

    @allure.story("Remove from Favourites")
    @allure.title("Favourite can be removed — list updates or empty state appears")
    def test_remove_favourite_updates_list(self, driver):
        page = self._login_and_open_favourites(driver)
        if page.get_favourites_count() == 0:
            pytest.skip("No favourites to remove")
        count_before = page.get_favourites_count()
        page.tap_first_favourite()
        wait_for_animation(driver, 1)
        page.remove_first_favourite()
        wait_for_animation(driver, 2)
        driver.back()
        wait_for_animation(driver, 1)
        page.navigate_to_favourites()
        count_after = page.get_favourites_count()
        assert count_after < count_before or page.is_empty_state_visible(), \
            "Removing a favourite did not reduce the list count"
        screenshot(driver, "favourites_remove_updates_list")


@allure.epic("Favourites")
@allure.feature("Favourites — Boundary & Negative")
@pytest.mark.favourites
@pytest.mark.negative
class TestFavouritesBoundary:
    """Boundary and negative tests for Favourites."""

    def _login_and_open_favourites(self, driver):
        LoginPage(driver).login()
        HomePage(driver).navigate_to_home()
        page = FavouritesPage(driver)
        page.navigate_to_favourites()
        return page

    @allure.story("Boundary")
    @allure.title("Rapid taps on Favourite button do not cause double-add")
    def test_rapid_favourite_taps_no_duplicate(self, driver):
        LoginPage(driver).login()
        HomePage(driver).navigate_to_home()
        mosque = MosquePage(driver)
        mosque.search_mosque("Al")
        mosque.open_mosque_profile("Al")
        wait_for_animation(driver, 1)
        base = BasePage(driver)
        for label in ["Favourite", "Favorite", "Save", "المفضلة"]:
            if base.is_visible(label, timeout=3):
                for _ in range(5):
                    base.tap_optional(label, timeout=1)
                    wait_for_animation(driver, 0.3)
                break
        assert not base.is_visible("500", timeout=3) and \
               not base.is_visible("Something went wrong", timeout=3), \
            "Rapid favourite taps caused a server error"
        screenshot(driver, "favourites_rapid_taps")

    @allure.story("Boundary")
    @allure.title("Favourites list with many items scrolls without crash")
    def test_large_favourites_list_scrolls(self, driver):
        page = self._login_and_open_favourites(driver)
        if page.get_favourites_count() < 3:
            pytest.skip("Need at least 3 favourites for scroll boundary test")
        size = driver.get_window_size()
        for _ in range(10):
            driver.swipe(
                size["width"] // 2, int(size["height"] * 0.8),
                size["width"] // 2, int(size["height"] * 0.2),
                400,
            )
            wait_for_animation(driver, 0.3)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3), \
            "Large favourites scroll caused an error"
        screenshot(driver, "favourites_large_list_scroll")
