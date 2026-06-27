import pytest
import allure
from pages.login_page import LoginPage
from pages.booking_page import BookingPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation
from utils.markers import android_apk_regression


@android_apk_regression
@allure.epic("Booking")
@allure.feature("Booking Flow")
@pytest.mark.booking
@pytest.mark.android
class TestBookingFlow:
    """Tests covering booking list, detail, cancel, and reschedule flows."""

    def _login_and_open_bookings(self, driver):
        LoginPage(driver).login()
        page = BookingPage(driver)
        page.navigate_to_bookings()
        return page

    @allure.story("Navigation")
    @allure.title("My Orders / Bookings screen loads successfully")
    def test_bookings_screen_loads(self, driver):
        page = self._login_and_open_bookings(driver)
        assert page.is_on_bookings_screen(timeout=10), \
            "Bookings / My Orders screen did not load"
        screenshot(driver, "bookings_screen_loads")

    @allure.story("Content")
    @allure.title("Booking list shows items or an empty state")
    def test_booking_list_shows_or_empty(self, driver):
        page = self._login_and_open_bookings(driver)
        count = page.get_booking_count()
        base = BasePage(driver)
        has_content = count > 0 or \
            base.is_visible("No orders", timeout=5) or \
            base.is_visible("No bookings", timeout=5) or \
            base.is_visible("Empty", timeout=5)
        assert has_content, "Bookings screen shows neither items nor an empty state"
        screenshot(driver, "booking_list_state")

    @allure.story("Detail")
    @allure.title("Tapping a booking opens the booking detail screen")
    def test_booking_detail_opens(self, driver):
        page = self._login_and_open_bookings(driver)
        if page.get_booking_count() == 0:
            pytest.skip("No bookings available in test account")
        page.open_first_booking()
        wait_for_animation(driver)
        base = BasePage(driver)
        assert base.is_visible("Order Number", timeout=5) or \
               base.is_visible("Order #", timeout=5) or \
               base.is_visible("Booking", timeout=5) or \
               base.is_visible("Status", timeout=5), \
            "Booking detail screen did not open"
        screenshot(driver, "booking_detail_opens")

    @allure.story("Cancel")
    @allure.title("Cancel booking shows confirmation dialog")
    def test_cancel_booking_shows_confirmation(self, driver):
        page = self._login_and_open_bookings(driver)
        if page.get_booking_count() == 0:
            pytest.skip("No bookings available in test account")
        page.open_first_booking()
        wait_for_animation(driver)
        base = BasePage(driver)
        base.tap_optional("Cancel Order", timeout=5)
        base.tap_optional("Cancel Booking", timeout=3)
        wait_for_animation(driver)
        assert base.is_visible("Are you sure", timeout=5) or \
               base.is_visible("Confirm", timeout=5) or \
               base.is_visible("Cancel", timeout=5), \
            "Cancellation confirmation dialog did not appear"
        # Dismiss the dialog
        base.tap_optional("No")
        base.tap_optional("Keep")
        screenshot(driver, "booking_cancel_confirmation")

    @allure.story("Cancel Negative")
    @allure.title("Dismissing cancel confirmation keeps the booking active")
    def test_dismiss_cancel_keeps_booking(self, driver):
        page = self._login_and_open_bookings(driver)
        if page.get_booking_count() == 0:
            pytest.skip("No bookings available in test account")
        page.open_first_booking()
        wait_for_animation(driver)
        base = BasePage(driver)
        base.tap_optional("Cancel Order", timeout=5)
        wait_for_animation(driver)
        base.tap_optional("No")
        base.tap_optional("Keep")
        wait_for_animation(driver)
        assert base.is_visible("Order Number", timeout=5) or \
               base.is_visible("Booking", timeout=5), \
            "Booking detail screen not visible after dismissing cancel"
        screenshot(driver, "booking_cancel_dismissed")

    @allure.story("Status")
    @allure.title("Booking status label is visible on the detail screen")
    def test_booking_status_visible(self, driver):
        page = self._login_and_open_bookings(driver)
        if page.get_booking_count() == 0:
            pytest.skip("No bookings available")
        page.open_first_booking()
        wait_for_animation(driver)
        status = page.get_booking_status()
        base = BasePage(driver)
        has_status = status is not None or \
            base.is_visible("Pending", timeout=3) or \
            base.is_visible("Confirmed", timeout=3) or \
            base.is_visible("Completed", timeout=3) or \
            base.is_visible("Status", timeout=3)
        assert has_status, "No booking status label visible on detail screen"
        screenshot(driver, "booking_status_visible")
