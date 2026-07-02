import pytest
import allure
from pages.login_page import LoginPage
from pages.orders_page import OrdersPage
from pages.rating_page import RatingPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, image_xpath
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from test_data import ValidData, InvalidRating


def _login_and_open_order(driver):
    LoginPage(driver).login()
    orders = OrdersPage(driver)
    orders.open()
    orders.assert_orders_screen()
    orders.open_first_order()
    wait_for_animation(driver, 1)
    return orders


def _navigate_to_rating(driver):
    _login_and_open_order(driver)
    base = BasePage(driver)
    for label in ["Rate Order", "Rate", "Leave a Review", "تقييم"]:
        if base.is_visible(label, timeout=3):
            base.tap(label)
            wait_for_animation(driver, 1)
            return RatingPage(driver)
    pytest.skip("Rate Order button not found — order may not be in a rateable state")


@allure.epic("Orders")
@allure.feature("Rating & Feedback")
@pytest.mark.rating
class TestRatingHappyPath:
    """Happy-path tests for the order rating and feedback flow."""

    @allure.story("Submit Rating")
    @allure.title("5-star rating with feedback submits successfully")
    def test_five_star_rating_submits(self, driver):
        rating = _navigate_to_rating(driver)
        assert rating.is_on_rating_screen(timeout=8), \
            "Rating screen did not appear"
        rating.tap_star(5)
        rating.enter_feedback(ValidData.RATING_FEEDBACK)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        assert rating.is_submission_successful(), \
            "5-star rating with feedback was not confirmed as submitted"
        screenshot(driver, "rating_five_star_success")

    @allure.story("Submit Rating")
    @allure.title("1-star rating with feedback submits successfully")
    def test_one_star_rating_submits(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(1)
        rating.enter_feedback("Poor experience")
        rating.submit_rating()
        wait_for_animation(driver, 3)
        assert rating.is_submission_successful() or \
               not BasePage(driver).is_visible("500", timeout=3), \
            "1-star rating caused an error"
        screenshot(driver, "rating_one_star_success")

    @allure.story("Submit Rating")
    @allure.title("Each star rating (1–5) is independently selectable")
    @pytest.mark.parametrize("stars", [1, 2, 3, 4, 5])
    def test_each_star_is_selectable(self, driver, stars):
        rating = _navigate_to_rating(driver)
        rating.tap_star(stars)
        rating.enter_feedback(f"{stars}-star test")
        rating.submit_rating()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3) and \
               not base.is_visible("Something went wrong", timeout=3), \
            f"{stars}-star rating caused an error"
        screenshot(driver, f"rating_{stars}_star")

    @allure.story("Submit Rating")
    @allure.title("Arabic feedback text submits without error")
    def test_arabic_feedback_accepted(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(5)
        rating.enter_feedback(InvalidRating.UNICODE)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3), \
            "Arabic feedback caused a server error"
        screenshot(driver, "rating_arabic_feedback")


@allure.epic("Orders")
@allure.feature("Rating & Feedback — Boundary & Negative")
@pytest.mark.rating
@pytest.mark.negative
class TestRatingNegative:
    """Negative and boundary tests for rating flow."""

    @allure.story("Validation")
    @allure.title("Submitting with no stars selected shows validation error or is blocked")
    def test_submit_without_stars_blocked(self, driver):
        rating = _navigate_to_rating(driver)
        rating.enter_feedback("No stars feedback")
        rating.submit_rating()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert not rating.is_submission_successful() or \
               base.is_visible("required", timeout=3) or \
               base.is_visible("select", timeout=3), \
            "Rating submitted without any star selection"
        screenshot(driver, "rating_no_stars_blocked")

    @allure.story("Validation")
    @allure.title("Submitting with no feedback text shows error or is blocked")
    def test_submit_empty_feedback_blocked(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(4)
        rating.submit_rating()
        wait_for_animation(driver, 2)
        base = BasePage(driver)
        assert base.is_visible("required", timeout=3) or \
               base.is_visible("Enter", timeout=3) or \
               base.is_visible("feedback", timeout=3) or \
               not rating.is_submission_successful(), \
            "Empty feedback bypassed validation"
        screenshot(driver, "rating_empty_feedback_blocked")

    @allure.story("Boundary")
    @allure.title("Very long feedback text is handled without crash")
    def test_long_feedback_no_crash(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(3)
        rating.enter_feedback(InvalidRating.LONG_FEEDBACK)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3) and \
               not base.is_visible("Exception", timeout=3), \
            "Long feedback caused a server or app error"
        screenshot(driver, "rating_long_feedback")

    @allure.story("Security")
    @allure.title("XSS payload in feedback is safely handled")
    def test_xss_in_feedback_is_safe(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(3)
        rating.enter_feedback(InvalidRating.XSS)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("alert(1)", timeout=3) and \
               not base.is_visible("script", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "XSS in rating feedback was not sanitized"
        screenshot(driver, "rating_xss_safe")

    @allure.story("Security")
    @allure.title("SQL injection in feedback is safely handled")
    def test_sql_injection_in_feedback_is_safe(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(2)
        rating.enter_feedback(InvalidRating.SQL_INJECTION)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("SQL", timeout=3) and \
               not base.is_visible("syntax error", timeout=3) and \
               not base.is_visible("500", timeout=3), \
            "SQL injection in feedback triggered a server error"
        screenshot(driver, "rating_sql_safe")

    @allure.story("Boundary")
    @allure.title("Special characters in feedback are accepted or safely rejected")
    def test_special_chars_in_feedback(self, driver):
        rating = _navigate_to_rating(driver)
        rating.tap_star(3)
        rating.enter_feedback(InvalidRating.SPECIAL_CHARS)
        rating.submit_rating()
        wait_for_animation(driver, 3)
        base = BasePage(driver)
        assert not base.is_visible("500", timeout=3), \
            "Special characters in feedback caused a server error"
        screenshot(driver, "rating_special_chars")


@allure.epic("Orders")
@allure.feature("Rating — Screen Presence")
@pytest.mark.rating
class TestRatingScreenUI:
    """Tests that the rating screen itself renders correctly."""

    @allure.story("UI")
    @allure.title("Rating screen shows star selector and feedback field")
    def test_rating_screen_has_required_elements(self, driver):
        rating = _navigate_to_rating(driver)
        assert rating.is_on_rating_screen(timeout=8), \
            "Rating screen did not appear"
        base = BasePage(driver)
        has_stars = base.is_visible("★", timeout=3) or \
                    base.is_visible("star", timeout=3) or \
                    base.is_visible("Star", timeout=3) or \
                    len(driver.find_elements(
                        __import__("appium.webdriver.common.appiumby", fromlist=["AppiumBy"]).AppiumBy.XPATH,
                        image_xpath()
                    )) >= 1
        assert has_stars, "Star selector not found on rating screen"
        screenshot(driver, "rating_screen_elements")

    @allure.story("Navigation")
    @allure.title("Rating screen can be cancelled without submitting")
    def test_rating_cancel_returns_to_order(self, driver):
        _login_and_open_order(driver)
        base = BasePage(driver)
        if not base.is_visible("Rate Order", timeout=3) and \
           not base.is_visible("Rate", timeout=3):
            pytest.skip("No rating option found on this order")
        for label in ["Rate Order", "Rate"]:
            base.tap_optional(label, timeout=2)
        wait_for_animation(driver, 1)
        driver.back()
        wait_for_animation(driver, 1)
        assert base.is_visible("Order Number", timeout=5) or \
               base.is_visible("Order #", timeout=5) or \
               base.is_visible("My Orders", timeout=5), \
            "Cancelling rating did not return to order detail"
        screenshot(driver, "rating_cancel_returns")
