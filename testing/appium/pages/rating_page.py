from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation

_RATING_SCREEN_LABELS = ["Rate", "Rating", "Feedback", "Review", "تقييم"]
_SUBMIT_LABELS = ["Submit Rating", "Submit", "Send Feedback", "إرسال"]
_SUCCESS_LABELS = ["Thank You For Your Feedback!", "Rating Submitted", "Thank you", "شكراً"]


class RatingPage(BasePage):

    def is_on_rating_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _RATING_SCREEN_LABELS)

    def tap_star(self, stars=5):
        """Tap the nth star (1-indexed)."""
        try:
            star_els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.ImageView")
            if len(star_els) >= stars:
                star_els[stars - 1].click()
                wait_for_animation(self.driver, 0.5)
        except Exception:
            pass
        return self

    def enter_feedback(self, text):
        try:
            els = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
            if els:
                els[0].click()
                els[0].clear()
                els[0].send_keys(text)
        except Exception:
            self.input_text("feedback", text)
        wait_for_animation(self.driver, 0.5)
        return self

    def submit_rating(self):
        for label in _SUBMIT_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver, 2)
        return self

    def is_submission_successful(self):
        return any(self.is_visible(lbl, timeout=5) for lbl in _SUCCESS_LABELS)

    def rate_with_stars_and_feedback(self, stars=5, feedback="Great service!"):
        self.tap_star(stars)
        self.enter_feedback(feedback)
        self.submit_rating()
        return self
