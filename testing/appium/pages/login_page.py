import os
import re
import subprocess
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.helpers import (
    wait_for_animation,
    is_ios,
    text_field_xpath,
    find_elements_by_label,
)

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
        return bool(self.driver.find_elements(AppiumBy.XPATH, text_field_xpath()))

    def _navigate_to_login_screen(self):
        """Click the login button on home/onboarding to reach the phone-input screen."""
        if self._already_on_login_screen():
            return self
        for label in _HOME_LOGIN_BTNS + _LOGIN_LABELS:
            els = find_elements_by_label(self.driver, label)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 2)
                if self._already_on_login_screen():
                    return self
        return self

    def _dismiss_system_dialogs(self):
        """Tap through system permission / alert dialogs."""
        for label in ["While using the app", "Only this time", "Allow", "OK", "ALLOW"]:
            els = find_elements_by_label(self.driver, label)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
        return self

    def _switch_to_english(self):
        """Tap the language toggle (shown as '  Ara' when in Arabic) and select English."""
        els = find_elements_by_label(self.driver, "Ara", contains=True)
        if not els:
            return self
        els[0].click()
        wait_for_animation(self.driver, 1.5)
        for eng_label in ["English", "en"]:
            hits = find_elements_by_label(self.driver, eng_label)
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
        # Some builds show a "Get Started" / "Next" / "Proceed" button after selection
        # before showing the phone entry screen. Tap it if visible.
        for label in ["Get Started", "Next", "Proceed", "Continue", "Start", "Let's Go",
                      "ابدأ", "التالي", "متابعة"]:
            self.tap_optional(label, timeout=2)
        wait_for_animation(self.driver, 1)
        return self

    def _select_bangladesh_country_code(self):
        """Open country code picker and select Bangladesh (+880) via search."""
        if find_elements_by_label(self.driver, "880", contains=True):
            return self
        cc_els = find_elements_by_label(self.driver, "+(", contains=True)
        if not cc_els:
            cc_els = find_elements_by_label(self.driver, "+880", contains=True)
        if not cc_els:
            return self
        cc_els[0].click()
        wait_for_animation(self.driver, 2)
        fields = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
        if fields:
            fields[0].click()
            fields[0].send_keys("Bangladesh")
            wait_for_animation(self.driver, 1.5)
        for label in ["Bangladesh\n(+880)", "Bangladesh"]:
            hits = find_elements_by_label(self.driver, label, contains=True)
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
        el = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((AppiumBy.XPATH, text_field_xpath()))
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
        on_dialog = (
            find_elements_by_label(self.driver, "SMS")
            or find_elements_by_label(self.driver, "Text message")
            or find_elements_by_label(self.driver, "WhatsApp")
        )
        if not on_dialog:
            return self
        for sms_label in ["SMS", "Text message"]:
            els = find_elements_by_label(self.driver, sms_label)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        for send_label in ["Send", "Continue", "متابعة", "إرسال"]:
            els = find_elements_by_label(self.driver, send_label)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 3)
                return self
        return self

    def _on_otp_or_delivery_screen(self):
        for label in ["SMS", "Send", "Verification code", "Confirm to Login"]:
            if find_elements_by_label(self.driver, label):
                return True
        return False

    def tap_continue(self):
        # Only tap the first matching label — multiple taps cause multiple OTP requests
        for label in _CONTINUE_LABELS:
            els = find_elements_by_label(self.driver, label)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 1)
                break
        deadline = time.time() + 10
        while time.time() < deadline:
            if self._on_otp_or_delivery_screen():
                break
            time.sleep(0.5)
        self._handle_otp_delivery_method()
        deadline = time.time() + 10
        while time.time() < deadline:
            if (
                find_elements_by_label(self.driver, "Verification code")
                or find_elements_by_label(self.driver, "Confirm to Login")
            ):
                break
            time.sleep(0.5)
        return self

    def _field_text(self, el) -> str:
        for attr in ("text", "value", "name", "label"):
            val = el.get_attribute(attr)
            if val:
                return str(val).strip()
        return ""

    def enter_otp(self, otp="1234"):
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: (
                    find_elements_by_label(d, "Verification code")
                    or find_elements_by_label(d, "Confirm to Login")
                    or d.find_elements(AppiumBy.XPATH, text_field_xpath())
                )
            )
        except Exception:
            pass
        wait_for_animation(self.driver, 1)
        try:
            fields = self.driver.find_elements(AppiumBy.XPATH, text_field_xpath())
            if not fields:
                if not is_ios():
                    self._adb_type_otp(otp)
                return self

            otp_fields = [
                f for f in fields
                if self._field_text(f) in ("", "null", "|")
                and len(self._field_text(f)) < 6
            ]
            if not otp_fields:
                if not is_ios():
                    self._adb_type_otp(otp)
                return self

            if len(otp_fields) >= len(otp):
                for i, digit in enumerate(otp):
                    otp_fields[i].click()
                    otp_fields[i].send_keys(digit)
                    time.sleep(0.2)
            else:
                otp_fields[0].click()
                time.sleep(0.2)
                otp_fields[0].send_keys(otp)
        except Exception:
            if not is_ios():
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
        deadline = time.time() + 3
        while time.time() < deadline:
            for label in _VERIFY_LABELS:
                els = find_elements_by_label(self.driver, label)
                if els:
                    els[0].click()
                    wait_for_animation(self.driver, 4)
                    return self
            time.sleep(0.3)
        for stem in ["Confirm", "Verify", "تأكيد", "تحقق"]:
            els = find_elements_by_label(self.driver, stem, contains=True)
            if els:
                els[0].click()
                wait_for_animation(self.driver, 4)
                return self
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
        guest_btns = (
            find_elements_by_label(self.driver, "Log In")
            or find_elements_by_label(self.driver, "Sign in")
            or find_elements_by_label(self.driver, "تسجيل الدخول")
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
        # timeout=4: gives the home screen 4s to render each indicator after app launch.
        # Android noReset=True keeps login tokens; after force-stop + 8s splash_wait
        # the home screen is usually loaded, so 4s/check finds "Cart" in first poll.
        # iOS noReset=False always starts fresh so this always returns False quickly.
        if self._is_already_logged_in(timeout=4):
            return self

        self._switch_to_english()
        self.select_country_and_language()
        self.skip_onboarding()
        self.enter_phone(phone)
        self.accept_terms()
        self.tap_continue()
        self._dismiss_system_dialogs()

        # Android only: inject SMS so the app can auto-read OTP
        if os.environ.get("TEST_OTP") and not is_ios():
            self._inject_sms_to_emulator(otp)

        self.enter_otp(otp)
        self.tap_verify()
        return self

    def assert_logged_in(self):
        assert self._is_already_logged_in(timeout=8), \
            "Login failed — expected to see home screen after login"
        return self
