from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, scroll_to_text, clickable_view_xpath

_NOTIF_NAV_LABELS = ["Notifications", "Notification", "إشعارات", "الإشعارات"]
_NOTIF_SCREEN_LABELS = ["Notifications", "إشعارات", "No notifications", "لا توجد إشعارات"]
_EMPTY_STATE_LABELS = ["No notifications", "لا توجد إشعارات", "No new notifications", "Empty"]


class NotificationPage(BasePage):

    def navigate_to_notifications(self):
        if self.is_on_notifications_screen(timeout=3):
            return self
        for label in _NOTIF_NAV_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def is_on_notifications_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _NOTIF_SCREEN_LABELS)

    def get_notification_count(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"notification") or contains(@text,"notification")]',
            )
            return len(items)
        except Exception:
            return 0

    def tap_first_notification(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                clickable_view_xpath(),
            )
            if items:
                items[0].click()
                wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def is_empty_state_visible(self):
        return any(self.is_visible(lbl, timeout=5) for lbl in _EMPTY_STATE_LABELS)

    def clear_all_notifications(self):
        for label in ["Clear All", "Mark all as read", "حذف الكل"]:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def scroll_notifications(self, times=3):
        for _ in range(times):
            size = self.driver.get_window_size()
            self.driver.swipe(
                size["width"] // 2, int(size["height"] * 0.7),
                size["width"] // 2, int(size["height"] * 0.3),
                600,
            )
            wait_for_animation(self.driver, 0.5)
        return self
