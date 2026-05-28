import os
import re
import subprocess
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.helpers import wait_for_animation

# Arabic label mappings used when app language is Arabic
_LOGIN_LABELS = [
    "Login to your account",       # English
    "تسجيل الدخول إلى حسابك",    # Arabic
]
_HOME_LOGIN_BTNS = [
    "Login",
    "Log In",
    "تسجيل الدخول",               # Arabic home-screen login button
    "Sign in",
]
_CONTINUE_LABELS = ["Log In", "Continue", "متابعة", "تسجيل الدخول"]
_VERIFY_LABELS   = ["Confirm to Login", "Verify", "Confirm", "تأكيد تسجيل الدخول", "تحقق", "التحقق", "تأكيد"]
_SKIP_LABELS     = ["Skip", "تخطي"]


class LoginPage(BasePage):

    def _already_on_login_screen(self):
        # find_elements (plural) returns immediately with [] when nothing found
        # — avoids the 10-second implicitly_wait penalty for each missing element
        return bool(self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText"))

    def _navigate_to_login_screen(self):
        """Click the login button on home/onboarding to reach the phone-input screen."""
        if self._already_on_login_screen():
            return self
        for label in _HOME_LOGIN_BTNS + _LOGIN_LABELS:
            els = self.driver.find_elements(AppiumBy.XPATH, f'//*[@content-desc="{label}"]')
            if els:
                els[0].click()
                wait_for_animation(self.driver, 2)
                if self._already_on_login_screen():
                    return self
        return self

    def _dismiss_system_dialogs(self):
        """Tap through any Android system permission dialogs."""
        for label in ["While using the app", "Only this time", "Allow", "OK", "ALLOW"]:
            els = self.driver.find_elements(AppiumBy.XPATH, f'//*[@text="{label}"]')
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
        return self

    def _switch_to_english(self):
        """Tap the language toggle (shown as '  Ara' when in Arabic) and select English."""
        els = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@content-desc,"  Ara") or contains(@content-desc,"Ara")]',
        )
        if not els:
            return self
        els[0].click()
        wait_for_animation(self.driver, 1.5)
        for eng_label in ["English", "en"]:
            hits = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@text="{eng_label}" or @content-desc="{eng_label}"]',
            )
            if hits:
                hits[0].click()
                wait_for_animation(self.driver, 2)
                return self
        return self

    def skip_onboarding(self):
        for label in _SKIP_LABELS:
            self.tap_optional(label)
        return self

    def select_country_and_language(self, country="Saudi Arabia", language="English"):
        self.tap_optional("Select your country")
        self.tap_optional(country)
        self.tap_optional("Select your language")
        self.tap_optional(language)
        wait_for_animation(self.driver, 1)
        return self

    def _select_bangladesh_country_code(self):
        """Open country code picker and select Bangladesh (+880) via search."""
        # Already on Bangladesh? Skip
        if self.driver.find_elements(AppiumBy.XPATH, '//*[contains(@content-desc,"880")]'):
            return self
        # Open country code picker
        cc_els = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[contains(@content-desc,"+(")]',
        )
        if not cc_els:
            return self
        cc_els[0].click()
        wait_for_animation(self.driver, 2)
        # Type in the search EditText inside the picker
        fields = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
        if fields:
            fields[0].click()
            fields[0].send_keys("Bangladesh")
            wait_for_animation(self.driver, 1.5)
        # Tap Bangladesh result
        for label in ["Bangladesh\n(+880)", "Bangladesh"]:
            hits = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[contains(@content-desc,"{label}") or contains(@text,"{label}")]',
            )
            if hits:
                hits[0].click()
                wait_for_animation(self.driver, 1.5)
                return self
        return self

    def enter_phone(self, phone):
        self._navigate_to_login_screen()
        wait_for_animation(self.driver, 1)
        # Switch to Bangladesh country code for the test account (phone starts with 880)
        if phone.startswith("880"):
            self._select_bangladesh_country_code()
            phone_local = phone[3:] if len(phone) > 3 else phone  # strip 880 prefix
        else:
            phone_local = phone
        el = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.EditText"))
        )
        el.click()
        el.clear()
        el.send_keys(phone_local)
        return self

    def accept_terms(self):
        for label in ["By clicking continue", "بالضغط على متابعة"]:
            self.tap_optional(label)
        return self

    def _handle_otp_delivery_method(self):
        """Select SMS delivery method if the app shows a method-selection dialog."""
        # Only act if the delivery dialog is actually on screen
        on_dialog = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[@content-desc="SMS" or @text="SMS" or '
            '@content-desc="Text message" or @text="Text message" or '
            '@content-desc="WhatsApp" or @text="WhatsApp"]',
        )
        if not on_dialog:
            return self
        # Prefer SMS; fall back to whatever is available
        for sms_label in ["SMS", "Text message"]:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@content-desc="{sms_label}" or @text="{sms_label}"]',
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        # Tap the Send/Continue button to submit the delivery choice
        for send_label in ["Send", "Continue", "متابعة", "إرسال"]:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@content-desc="{send_label}" or @text="{send_label}"]',
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 3)
                return self
        return self

    def tap_continue(self):
        # Only tap the first matching label — multiple taps cause multiple OTP requests
        for label in _CONTINUE_LABELS:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[@content-desc="{label}" or @text="{label}"]',
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        # Wait up to 10s for the delivery-method dialog OR the OTP verification screen
        deadline = time.time() + 10
        while time.time() < deadline:
            if self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[@content-desc="SMS" or @content-desc="Send" or '
                '@text="SMS" or @text="Send" or '
                '@content-desc="Verification code" or @content-desc="Confirm to Login"]',
            ):
                break
            time.sleep(0.5)
        self._handle_otp_delivery_method()
        # Wait up to 10s for OTP verification screen to appear after delivery dialog is dismissed
        deadline = time.time() + 10
        while time.time() < deadline:
            if self.driver.find_elements(
                AppiumBy.XPATH,
                '//*[@content-desc="Verification code" or @content-desc="Confirm to Login"]',
            ):
                break
            time.sleep(0.5)
        return self

    def enter_otp(self, otp="1234"):
        # Wait for OTP verification screen (not the phone input screen)
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: d.find_elements(
                    AppiumBy.XPATH,
                    '//*[@content-desc="Verification code" or @content-desc="Confirm to Login"]',
                )
            )
        except Exception:
            pass
        wait_for_animation(self.driver, 1)
        try:
            fields = self.driver.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
            if not fields:
                # Fallback: tap anywhere on OTP area and use ADB keyboard input
                self._adb_type_otp(otp)
                return self

            # Filter to OTP fields only (empty or has only a cursor hint, not phone number)
            otp_fields = [
                f for f in fields
                if (f.get_attribute("text") or "").strip() in ("", "null", "|")
                and len(f.get_attribute("text") or "") < 6
            ]
            if not otp_fields:
                # All fields have long content (phone number) — OTP screen not ready yet
                # Use ADB input instead
                self._adb_type_otp(otp)
                return self

            if len(otp_fields) >= len(otp):
                # One box per digit
                for i, digit in enumerate(otp):
                    otp_fields[i].click()
                    otp_fields[i].send_keys(digit)
                    time.sleep(0.2)
            else:
                # Single combined field
                otp_fields[0].click()
                time.sleep(0.2)
                otp_fields[0].send_keys(otp)
        except Exception:
            self._adb_type_otp(otp)
        return self

    @staticmethod
    def _adb_type_otp(otp: str):
        """Type OTP using ADB keyevents as a fallback when Appium send_keys fails."""
        try:
            subprocess.run(
                ["adb", "-s", "emulator-5554", "shell", "input", "text", otp],
                capture_output=True, timeout=5,
            )
            time.sleep(0.5)
        except Exception:
            pass

    def tap_verify(self):
        # Wait up to 3s for the verify button to appear (OTP auto-submit may hide it quickly)
        deadline = time.time() + 3
        while time.time() < deadline:
            for label in _VERIFY_LABELS:
                els = self.driver.find_elements(AppiumBy.XPATH, f'//*[@content-desc="{label}"]')
                if els:
                    els[0].click()
                    wait_for_animation(self.driver, 4)
                    return self
            time.sleep(0.3)
        # Fallback: contains match on common stems
        for stem in ["Confirm", "Verify", "تأكيد", "تحقق"]:
            els = self.driver.find_elements(
                AppiumBy.XPATH,
                f'//*[contains(@content-desc,"{stem}") or contains(@text,"{stem}")]',
            )
            if els:
                els[0].click()
                wait_for_animation(self.driver, 4)
                return self
        # OTP may auto-submit — just wait for result
        wait_for_animation(self.driver, 4)
        return self

    # ── Home-screen indicators (any visible = already logged in) ──────────────
    _HOME_INDICATORS = [
        "Cart", "My Orders", "Home", "Explore",
        "الرئيسية", "السلة", "طلباتي", "استكشف",
    ]

    def _is_already_logged_in(self, timeout=5):
        # Check home indicators are visible
        if not any(self.is_visible(t, timeout=timeout) for t in self._HOME_INDICATORS):
            return False
        # Guest mode shows a "Log In" CTA on the home screen — real login does not
        guest_btns = self.driver.find_elements(
            AppiumBy.XPATH,
            '//*[@content-desc="Log In" or @content-desc="Sign in" or @content-desc="تسجيل الدخول"]',
        )
        return len(guest_btns) == 0

    @staticmethod
    def _inject_sms_to_emulator(otp: str, sender: str = "Qatarat"):
        """Inject a fake SMS into the Android emulator console so the app can auto-read it."""
        try:
            cmd = f'sms send {sender} "Your Qatarat verification code is {otp}"'
            proc = subprocess.run(
                ["bash", "-c", f'(echo "{cmd}"; sleep 1) | nc -w 2 localhost 5554'],
                capture_output=True, text=True, timeout=5,
            )
            time.sleep(1.5)
        except Exception:
            pass

    @staticmethod
    def _read_otp_from_emulator_sms(timeout: int = 30) -> str | None:
        """Poll the emulator SMS inbox for an OTP from the backend (4-6 digits)."""
        deadline = time.time() + timeout
        seen = set()
        while time.time() < deadline:
            try:
                result = subprocess.run(
                    ["adb", "-s", "emulator-5554", "shell",
                     "content query --uri content://sms/inbox"],
                    capture_output=True, text=True, timeout=10,
                )
                for line in result.stdout.splitlines():
                    if "body=" in line:
                        body = line.split("body=", 1)[1].split(",")[0]
                        match = re.search(r'\b(\d{4,6})\b', body)
                        if match and body not in seen:
                            seen.add(body)
                            return match.group(1)
            except Exception:
                pass
            time.sleep(2)
        return None

    def login_phone_only(self, phone="8801685220417"):
        self.enter_phone(phone)
        self.accept_terms()
        self.tap_continue()
        return self

    def login(self, phone="8801685220417", otp=None):
        # Resolve OTP: env var > explicit arg > default
        if otp is None:
            otp = os.environ.get("TEST_OTP", "1234")

        # Short-circuit if already on home screen (persisted login token)
        self._dismiss_system_dialogs()
        if self._is_already_logged_in(timeout=4):
            return self

        self._switch_to_english()
        self.select_country_and_language()
        self.skip_onboarding()
        self.enter_phone(phone)
        self.accept_terms()
        self.tap_continue()
        self._dismiss_system_dialogs()

        # If we have a real OTP (env var), inject it as SMS so the app can auto-read it
        if os.environ.get("TEST_OTP"):
            self._inject_sms_to_emulator(otp)

        self.enter_otp(otp)
        self.tap_verify()
        return self

    def assert_logged_in(self):
        assert self._is_already_logged_in(timeout=8), \
            "Login failed — expected to see home screen after login"
        return self
