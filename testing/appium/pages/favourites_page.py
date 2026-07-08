from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from utils.helpers import wait_for_animation, is_ios

_FAV_NAV_LABELS = ["Favourites", "Favorites", "Favourite", "المفضلة", "مفضلة"]
_FAV_SCREEN_LABELS = ["Favourites", "Favorites", "My Favourites", "المفضلة"]
_EMPTY_LABELS = ["No favourites", "No favorites", "لا توجد مفضلة", "Empty"]


class FavouritesPage(BasePage):

    def navigate_to_favourites(self):
        if self.is_on_favourites_screen(timeout=3):
            return self
        for label in _FAV_NAV_LABELS:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self

    def is_on_favourites_screen(self, timeout=8):
        return any(self.is_visible(lbl, timeout=timeout) for lbl in _FAV_SCREEN_LABELS)

    def get_favourites_count(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                "//*[@accessible='true']" if is_ios() else "//*[@clickable='true']//android.view.View",
            )
            return len(items)
        except Exception:
            return 0

    def is_empty_state_visible(self):
        return any(self.is_visible(lbl, timeout=5) for lbl in _EMPTY_LABELS)

    def tap_first_favourite(self):
        try:
            items = self.driver.find_elements(
                AppiumBy.XPATH,
                "//*[@clickable='true']",
            )
            for el in items:
                desc = el.get_attribute("content-desc") or ""
                if any(kw in desc for kw in ["Mosque", "mosque", "Masjid"]):
                    el.click()
                    wait_for_animation(self.driver)
                    return self
            if items:
                items[0].click()
                wait_for_animation(self.driver)
        except Exception:
            pass
        return self

    def remove_first_favourite(self):
        for label in ["Remove", "Unfavourite", "إزالة"]:
            self.tap_optional(label, timeout=3)
        wait_for_animation(self.driver)
        return self
