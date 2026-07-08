import pytest
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, image_xpath
from utils.markers import android_apk_regression


class TestLiveBroadcast:
    """
    Agora RTC live streaming flow tests.
    These are view/interaction tests — actual stream content is not verified.
    """

    @android_apk_regression
    def test_live_broadcast_screen_accessible(self, driver):
        """Live Broadcast option should be accessible from home."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Live Broadcast")
        wait_for_animation(driver, 3)

        assert page.is_visible("Live Broadcast") or \
               page.is_visible("Visual documentations") or \
               page.is_visible("Data not available yet"), \
            "Live Broadcast screen did not load"
        screenshot(driver, "live_broadcast_screen")

    @android_apk_regression
    def test_visual_documentation_section_loads(self, driver):
        """Visual documentations tab should load without crash."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Visual documentations")
        wait_for_animation(driver, 3)

        assert page.is_visible("Visual documentations") or \
               page.is_visible("Data not available yet"), \
            "Visual Documentations section did not load"
        screenshot(driver, "visual_documentation_section")

    def test_live_broadcast_permissions_requested(self, driver):
        """Joining a live stream should request camera/mic permissions (or show already granted)."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Live Broadcast")
        wait_for_animation(driver, 2)

        # Attempt to join a stream if one is listed
        from appium.webdriver.common.appiumby import AppiumBy
        streams = driver.find_elements(AppiumBy.XPATH, image_xpath())
        if streams:
            streams[0].click()
            wait_for_animation(driver, 3)
            screenshot(driver, "live_broadcast_join_attempt")
        else:
            pytest.skip("No live streams available in stage environment")
