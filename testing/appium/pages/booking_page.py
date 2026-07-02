from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text, clickable_view_xpath

_BOOKING_NAV_LABELS = ["My Orders", "Orders", "Bookings", "طلباتي"]
_BOOKING_SCREEN_LABELS = ["My Orders", "Bookings", "Order Number", "طلباتي"]
_STATUS_LABELS = ["Pending", "Confirmed", "Completed", "Cancelled", "قيد الانتظار", "مؤكد"]
_CANCEL_LABELS = ["Cancel Order", "Cancel Booking", "إلغاء الطلب"]
_RESCHEDULE_LABELS = ["Reschedule", "Change Date", "إعادة جدولة"]


class BookingPage(BasePage):

    def navigate_to_bookings(self):
        if self.is_on_bookings_screen(timeout=3):
            return self
        for label in _BOOKING_NAV_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def is_on_bookings_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _BOOKING_SCREEN_LABELS)

    def open_first_booking(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Order") or contains(@text,"Order #")]',
            )
            if items:
                items[0].click()
                wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def get_booking_status(self):
        for label in _STATUS_LABELS:
            if self.is_visible(label, timeout=3):
                return label
        return None

    def cancel_booking(self):
        for label in _CANCEL_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        # Confirm cancellation if dialog appears
        for confirm in ["Yes", "Confirm", "Cancel Order", "تأكيد"]:
            self.tap_optional(confirm, timeout=3)
        wait_for_animation(self.driver, 2)
        return self

    def reschedule_booking(self):
        for label in _RESCHEDULE_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def select_new_date(self, day_offset=1):
        """Tap a future date on the calendar by tapping forward day_offset cells."""
        try:
            cells = self.driver.find_elements(
                AppiumBy.XPATH,
                clickable_view_xpath(),
            )
            if cells and len(cells) > day_offset:
                cells[day_offset].click()
                wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def confirm_reschedule(self):
        for label in ["Confirm", "Save", "Update", "تأكيد"]:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver, 2)
        return self

    def get_booking_count(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Order") or contains(@text,"Order #")]',
            )
            return len(items)
        except Exception:
            return 0
