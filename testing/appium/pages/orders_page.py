from pages.base_page import BasePage
from utils.helpers import wait_for_animation, is_ios, image_xpath


class OrdersPage(BasePage):

    def open(self):
        self.tap("My Orders")
        wait_for_animation(self.driver)
        return self

    def assert_orders_screen(self):
        assert self.is_visible("My Orders") or self.is_visible("Recent Orders"), \
            "Orders screen not visible"
        return self

    def search_order(self, query):
        self.tap_optional("Search orders...")
        self.input_text("Search orders...", query)
        wait_for_animation(self.driver)
        return self

    def open_first_order(self):
        self.tap_optional("See All Orders")
        wait_for_animation(self.driver)
        # Tap the first order item
        from appium.webdriver.common.appiumby import AppiumBy
        orders = self.driver.find_elements(AppiumBy.XPATH,
            "//XCUIElementTypeTable//XCUIElementTypeCell" if is_ios()
            else "//android.widget.ListView/android.view.View")
        if orders:
            orders[0].click()
        wait_for_animation(self.driver)
        return self

    def assert_order_detail(self):
        assert self.is_visible("Order Number") and self.is_visible("Payment Date"), \
            "Order detail fields missing"
        return self

    def rate_order(self, feedback="Great service!", stars=5):
        self.tap_optional("Rate Order")
        wait_for_animation(self.driver)
        # Tap star rating (tap the nth star)
        from appium.webdriver.common.appiumby import AppiumBy
        star_els = self.driver.find_elements(AppiumBy.XPATH, image_xpath())
        if len(star_els) >= stars:
            star_els[stars - 1].click()
        self.tap_optional("Type your feedback")
        self.input_text("Type your feedback", feedback)
        self.tap_optional("Submit Rating")
        wait_for_animation(self.driver, 2)
        return self

    def assert_rating_submitted(self):
        assert self.is_visible("Thank You For Your Feedback!"), \
            "Rating submission confirmation not shown"
        return self
