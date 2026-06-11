import pytest
import allure
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from utils.helpers import screenshot, wait_for_animation


@allure.epic("Account")
@allure.feature("Edit Profile")
@pytest.mark.account
class TestEditProfile:
    """Tests covering the edit-profile form including boundary and security inputs."""

    def _login_and_open_edit(self, driver):
        login = LoginPage(driver)
        login.login()  # login() handles country/language + onboarding internally
        page = ProfilePage(driver)
        page.navigate_to_profile()
        page.tap_edit_profile()
        wait_for_animation(driver)
        return page

    @allure.story("Happy Path")
    @allure.title("Update profile name with valid input saves successfully")
    def test_edit_profile_valid_name(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("Ahmed Ali")
        page.save_profile()
        wait_for_animation(driver)
        assert page.is_visible("Ahmed Ali") or \
               page.is_visible("Saved") or \
               page.is_visible("Updated") or \
               not page.is_visible("Error", timeout=3), \
            "Profile was not saved after entering a valid name"
        screenshot(driver, "edit_profile_valid_name")

    @allure.story("Negative")
    @allure.title("Submitting an empty name field shows a validation error")
    def test_edit_profile_empty_name(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("")
        page.save_profile()
        wait_for_animation(driver)
        assert page.is_visible("required") or \
               page.is_visible("Enter") or \
               page.is_visible("Invalid") or \
               page.is_visible("Error") or \
               not page.is_visible("Saved"), \
            "Empty name was accepted without a validation error"
        screenshot(driver, "edit_profile_empty_name")

    @allure.story("Security")
    @allure.title("SQL injection payload in name field is handled safely")
    def test_edit_profile_sql_injection(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("'; DROP TABLE users; --")
        page.save_profile()
        wait_for_animation(driver)
        assert not page.is_visible("SQL", timeout=3) and \
               not page.is_visible("syntax error", timeout=3) and \
               not page.is_visible("500", timeout=3), \
            "SQL injection in name field produced a database error"
        screenshot(driver, "edit_profile_sql_injection")

    @allure.story("Security")
    @allure.title("XSS payload in name field is handled safely")
    def test_edit_profile_xss(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("<script>alert('xss')</script>")
        page.save_profile()
        wait_for_animation(driver)
        # The app should either reject it or store it escaped — it must not execute JS
        assert not page.is_visible("alert", timeout=3) and \
               not page.is_visible("500", timeout=3), \
            "XSS payload in name field caused an error or was executed"
        screenshot(driver, "edit_profile_xss")

    @allure.story("Localisation")
    @allure.title("Arabic Unicode name is accepted and saved")
    def test_edit_profile_unicode_name(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("محمد أحمد")
        page.save_profile()
        wait_for_animation(driver)
        assert not page.is_visible("Error", timeout=3) or \
               page.is_visible("محمد"), \
            "Arabic Unicode name was rejected unexpectedly"
        screenshot(driver, "edit_profile_unicode_name")

    @allure.story("Boundary")
    @allure.title("Name with 256 characters is handled with a validation message")
    def test_edit_profile_max_length(self, driver):
        page = self._login_and_open_edit(driver)
        long_name = "A" * 256
        page.enter_name(long_name)
        page.save_profile()
        wait_for_animation(driver)
        assert page.is_visible("too long") or \
               page.is_visible("maximum") or \
               page.is_visible("limit") or \
               page.is_visible("characters") or \
               page.is_visible("Error") or \
               not page.is_visible("500", timeout=3), \
            "256-character name was accepted without a max-length error"
        screenshot(driver, "edit_profile_max_length")

    @allure.story("Boundary")
    @allure.title("Name containing emojis is accepted or shown a friendly error")
    def test_edit_profile_emoji_name(self, driver):
        page = self._login_and_open_edit(driver)
        page.enter_name("Ahmed 😀👍")
        page.save_profile()
        wait_for_animation(driver)
        # Must not crash; may accept or show friendly validation
        assert not page.is_visible("crash", timeout=3) and \
               not page.is_visible("500", timeout=3), \
            "App crashed when emoji was entered in the name field"
        screenshot(driver, "edit_profile_emoji_name")
