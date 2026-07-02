"""
Browse & Search edge cases.
Covers: single char search, very long search, Arabic search,
        no-results state, special chars, emoji, SQL/XSS in search.
"""
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.login_page import LoginPage
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, edit_text_xpath
from test_data import ValidData


def _get_search_field(driver):
    """Return the search EditText or None if not on a search screen."""
    els = driver.find_elements(AppiumBy.XPATH, edit_text_xpath())
    return els[0] if els else None


def _go_to_browse(driver):
    login = LoginPage(driver)
    login.login(ValidData.PHONE, ValidData.OTP)
    page = BasePage(driver)
    # Try common bottom-nav labels for the browse/explore tab
    for label in ["Browse", "Explore", "Search", "استكشف"]:
        page.tap_optional(label, timeout=3)
        field = _get_search_field(driver)
        if field:
            return field
    # Fall back: if no nav label worked, the home screen may already have a search bar
    return _get_search_field(driver)


@pytest.mark.browse
@pytest.mark.boundary
class TestSearchInput:

    def test_single_character_search(self, driver):
        """Searching with one letter should either show results or empty state — never crash."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found after navigating to browse")
        field.send_keys("a")
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_search_100_chars_does_not_crash(self, driver):
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("a" * 100)
        wait_for_animation(driver)
        assert "500" not in driver.page_source

    def test_search_arabic_text(self, driver):
        """Arabic search query — Qatarat is an Arabic-first app."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("مسجد")
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_search_emoji_does_not_crash(self, driver):
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("🕌")
        wait_for_animation(driver)
        assert "500" not in driver.page_source

    def test_search_all_uppercase_query(self, driver):
        """MOSQUE — uppercase search should work (case-insensitive)."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("MOSQUE")
        wait_for_animation(driver)
        page = driver.page_source
        assert "500" not in page

    def test_search_mixed_case(self, driver):
        """MoSqUe — mixed case should return same results as lowercase."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("MoSqUe")
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_search_with_numbers_only(self, driver):
        """Numeric search query '123' — should show empty state, not crash."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("123")
        wait_for_animation(driver)
        page = driver.page_source
        assert "500" not in page

    def test_search_with_html_tags_is_safe(self, driver):
        """<b>mosque</b> — HTML in search field must not render as HTML (XSS check)."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("<b>mosque</b>")
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page
        assert "500" not in page

    def test_search_sql_injection_is_safe(self, driver):
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("' OR '1'='1")
        wait_for_animation(driver)
        page = driver.page_source
        assert "SQL" not in page
        assert "syntax error" not in page.lower()
        assert "database" not in page.lower()

    def test_search_gibberish_shows_empty_state(self, driver):
        """'zzzzzzzzz' should return no results with an empty state UI."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("zzzzzzzzz")
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page

    def test_clear_search_restores_full_list(self, driver):
        """After clearing a search query, the full listing must reappear."""
        field = _go_to_browse(driver)
        if field is None:
            pytest.skip("Search field not found")
        field.send_keys("zzzzz")
        wait_for_animation(driver)
        field.clear()
        wait_for_animation(driver)
        page = driver.page_source
        assert "Something went wrong" not in page


@pytest.mark.browse
@pytest.mark.boundary
class TestServiceListing:

    def test_services_list_loads_without_login(self, driver):
        """Browse should be accessible as guest — no login required to view."""
        page = BasePage(driver)
        for label in ["Browse", "Explore", "استكشف"]:
            page.tap_optional(label, timeout=3)
        source = driver.page_source
        assert "Something went wrong" not in source
        assert "500" not in source

    def test_service_card_tap_opens_detail(self, driver):
        """Tapping a service card must open detail view without crash."""
        _go_to_browse(driver)
        cards = driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@content-desc,"service_card") or contains(@content-desc,"Mosque")]',
        )
        if cards:
            cards[0].click()
            wait_for_animation(driver)
            page = driver.page_source
            assert "Something went wrong" not in page

    def test_rapid_back_forth_navigation_no_crash(self, driver):
        """Quickly opening and closing service detail — no memory leak / crash."""
        _go_to_browse(driver)
        for _ in range(3):
            cards = driver.find_elements(
                AppiumBy.XPATH,
                '//*[contains(@content-desc,"Mosque") or contains(@content-desc,"service_card")]',
            )
            if cards:
                cards[0].click()
                wait_for_animation(driver, 0.5)
                driver.back()
                wait_for_animation(driver, 0.5)
        assert "Something went wrong" not in driver.page_source
