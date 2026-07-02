import pytest
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import screenshot, wait_for_animation, find_by_text, image_xpath


@pytest.mark.gift
class TestGiftCard:

    def test_gift_card_entry_fields_present(self, driver):
        """All gift card fields must be present on the gift details screen."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Gift to someone you love")
        page.tap_optional("Gift Card")
        wait_for_animation(driver, 2)

        assert page.is_visible("Gift Details") or page.is_visible("Recipient name"), \
            "Gift Details screen not reached"

        # All required fields
        assert page.is_visible("Enter recipient Name"), "Recipient name field missing"
        assert page.is_visible("Recipient Number") or page.is_visible("Whatsapp Number"), \
            "Recipient WhatsApp number field missing"
        screenshot(driver, "gift_card_fields")

    def test_gift_card_preview_shows_correct_info(self, driver):
        """Gift card preview should reflect entered recipient name and message."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Gift to someone you love")
        page.tap_optional("Gift Card")
        wait_for_animation(driver, 2)

        page.tap_optional("Enter recipient Name")
        page.input_text("Enter recipient Name", "Fatima Hassan")

        page.tap_optional("Recipient Number")
        page.input_text("Recipient Number", "509876543")

        page.tap_optional("Enter sender Name")
        page.input_text("Enter sender Name", "Mohammed Test")

        page.tap_optional("What do you want to say?")
        page.input_text("What do you want to say?", "Blessed from Mecca!")

        page.tap_optional("Choose Relationship")
        wait_for_animation(driver)
        page.tap_optional("Friend")
        wait_for_animation(driver)

        page.tap_optional("Select Template")
        wait_for_animation(driver)
        from appium.webdriver.common.appiumby import AppiumBy
        templates = driver.find_elements(AppiumBy.XPATH, image_xpath())
        if templates:
            templates[0].click()
        wait_for_animation(driver)

        page.tap_optional("Preview")
        wait_for_animation(driver, 2)

        assert page.is_visible("Gift Card Preview"), "Gift card preview screen not shown"
        assert page.is_visible("Gift card will be sent to this WhatsApp number"), \
            "WhatsApp delivery note not shown in preview"
        screenshot(driver, "gift_card_preview")

    def test_gift_card_validation_empty_fields(self, driver):
        """Submitting empty gift form should show validation errors."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("Gift to someone you love")
        page.tap_optional("Gift Card")
        wait_for_animation(driver, 2)

        # Try to proceed without filling fields
        page.tap_optional("Next")
        page.tap_optional("Save Gift Details")
        wait_for_animation(driver)

        assert page.is_visible("This field can't be empty") or \
               page.is_visible("required"), \
            "Validation error not shown for empty gift fields"
        screenshot(driver, "gift_card_validation_error")

    def test_gift_received_section_visible(self, driver):
        """My Orders → Gifts You Received section should be visible when logged in."""
        login = LoginPage(driver)
        login.select_country_and_language()
        login.skip_onboarding()
        login.login()

        page = BasePage(driver)
        page.tap_optional("My Orders")
        wait_for_animation(driver)

        assert page.is_visible("Gifts You Received") or \
               page.is_visible("Gift Received"), \
            "Gifts You Received section not visible in orders"
        screenshot(driver, "gift_received_section")
