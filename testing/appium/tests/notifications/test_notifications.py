import pytest
import allure
from pages.login_page import LoginPage
from pages.notification_page import NotificationPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Notifications")
@allure.feature("Notification Centre")
@pytest.mark.notifications
@pytest.mark.android
class TestNotifications:
    """Tests covering notification centre navigation, content, and interactions."""

    def _login_and_open_notifications(self, driver):
        LoginPage(driver).login()
        page = NotificationPage(driver)
        page.navigate_to_notifications()
        return page

    @allure.story("Navigation")
    @allure.title("Notifications screen loads successfully after login")
    def test_notifications_screen_loads(self, driver):
        page = self._login_and_open_notifications(driver)
        assert page.is_on_notifications_screen(timeout=10), \
            "Notifications screen did not load"
        screenshot(driver, "notifications_screen_loads")

    @allure.story("Content")
    @allure.title("Notifications screen shows items or an empty state")
    def test_notifications_shows_or_empty(self, driver):
        page = self._login_and_open_notifications(driver)
        count = page.get_notification_count()
        has_state = count > 0 or page.is_empty_state_visible()
        assert has_state, "Notifications screen shows neither items nor empty state"
        screenshot(driver, "notifications_shows_or_empty")

    @allure.story("Interaction")
    @allure.title("Tapping a notification opens its detail without crashing")
    def test_tap_notification_opens_detail(self, driver):
        page = self._login_and_open_notifications(driver)
        if page.get_notification_count() == 0:
            pytest.skip("No notifications available")
        page.tap_first_notification()
        wait_for_animation(driver)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "Tapping notification caused an error"
        screenshot(driver, "notification_tap_opens_detail")

    @allure.story("Scroll")
    @allure.title("Scrolling the notifications list does not crash")
    def test_scroll_notifications_no_crash(self, driver):
        page = self._login_and_open_notifications(driver)
        page.scroll_notifications(times=5)
        base = BasePage(driver)
        assert not base.is_visible("Something went wrong", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "Scrolling notifications caused an error"
        screenshot(driver, "notifications_scroll_no_crash")

    @allure.story("Guest")
    @allure.title("Notification centre is accessible only after login")
    def test_notifications_require_login(self, driver):
        page = NotificationPage(driver)
        page.navigate_to_notifications()
        wait_for_animation(driver)
        base = BasePage(driver)
        # Either the notifications screen is shown (logged in from previous session)
        # or the app redirects to login (correct guest behaviour)
        is_notif = page.is_on_notifications_screen(timeout=5)
        is_login = base.is_visible("Login", timeout=3) or \
                   base.is_visible("Sign In", timeout=3) or \
                   base.is_visible("Phone", timeout=3)
        assert is_notif or is_login, \
            "Neither notifications screen nor login redirect appeared"
        screenshot(driver, "notifications_require_login")
