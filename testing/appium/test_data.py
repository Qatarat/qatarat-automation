"""
Centralised test data for all Qatarat test suites.
All boundary values, invalid inputs, and negative-case data live here.
"""


class ValidData:
    PHONE = "8801685220417"
    OTP = "1234"
    PROMO = "TEST10"

    CARD = {"number": "4111111111111111", "expiry": "12/25", "cvv": "123", "name": "Test User"}

    GIFT_RECIPIENT_NAME = "Fatima Hassan"
    GIFT_RECIPIENT_PHONE = "509876543"
    GIFT_SENDER_NAME = "Mohammed Test"
    GIFT_MESSAGE = "Blessed from Mecca!"

    RATING_FEEDBACK = "Excellent service, very satisfied!"
    RATING_STARS = 5

    HELP_SEARCH = "payment"


class InvalidPhone:
    EMPTY = ""
    TOO_SHORT = "123"
    TOO_LONG = "88016852204179999999"
    LETTERS_ONLY = "abcdefghij"
    MIXED = "abc123def45"
    SPECIAL_CHARS = "+880@abc#123"
    ALL_ZEROS = "0000000000"
    SPACES = "880 168 522 041 7"


class InvalidOTP:
    WRONG = "9999"
    ALL_ZEROS = "0000"
    TOO_SHORT = "12"
    TOO_LONG = "123456789"
    LETTERS = "abcd"
    SEQUENTIAL = "1235"   # one digit off
    REVERSED = "4321"


class InvalidCard:
    SHORT_NUMBER = {"number": "41111111", "expiry": "12/25", "cvv": "123", "name": "Test User"}
    EXPIRED = {"number": "4111111111111111", "expiry": "01/20", "cvv": "123", "name": "Test User"}
    DECLINED = {"number": "4000000000000002", "expiry": "12/25", "cvv": "123", "name": "Test User"}
    INVALID_MONTH = {"number": "4111111111111111", "expiry": "13/25", "cvv": "123", "name": "Test User"}
    PAST_YEAR = {"number": "4111111111111111", "expiry": "12/19", "cvv": "123", "name": "Test User"}
    EMPTY_CVV = {"number": "4111111111111111", "expiry": "12/25", "cvv": "", "name": "Test User"}
    SHORT_CVV = {"number": "4111111111111111", "expiry": "12/25", "cvv": "1", "name": "Test User"}
    LONG_CVV = {"number": "4111111111111111", "expiry": "12/25", "cvv": "123456", "name": "Test User"}
    EMPTY_NAME = {"number": "4111111111111111", "expiry": "12/25", "cvv": "123", "name": ""}
    LONG_NAME = {"number": "4111111111111111", "expiry": "12/25", "cvv": "123", "name": "A" * 100}
    LETTERS_IN_NUMBER = {"number": "ABCD1234EFGH5678", "expiry": "12/25", "cvv": "123", "name": "Test"}
    ALL_ZEROS_NUMBER = {"number": "0000000000000000", "expiry": "12/25", "cvv": "123", "name": "Test"}


class InvalidPromo:
    WRONG_CODE = "INVALID123"
    EXPIRED = "EXPIRED10"
    EMPTY = ""
    SPECIAL_CHARS = "TEST@#$%"
    LOWERCASE = "test10"
    WITH_SPACES = " TEST10 "
    TOO_LONG = "A" * 50
    SQL_INJECTION = "' OR '1'='1"
    NUMBERS_ONLY = "123456"


class InvalidGift:
    LONG_NAME = "A" * 150
    SPECIAL_NAME = "Ahmed@#$%^&*()"
    ARABIC_NAME = "أحمد علي"           # valid: Unicode should be accepted
    INVALID_PHONE = "abc"
    SHORT_PHONE = "123"
    LONG_PHONE = "5098765430000000"
    LONG_MESSAGE = "This is a very long message that exceeds the normal character limit. " * 10
    XSS_MESSAGE = "<script>alert('xss')</script>"
    SQL_MESSAGE = "'; DROP TABLE users; --"
    EMOJI_MESSAGE = "🕌🤲✨ Blessed from Mecca! 🌙"


class InvalidRating:
    EMPTY_FEEDBACK = ""
    LONG_FEEDBACK = "Great service! " * 30
    SPECIAL_CHARS = "!@#$%^&*()<>{}[]"
    UNICODE = "خدمة ممتازة جداً"
    SQL_INJECTION = "'; DROP TABLE ratings; --"
    XSS = "<img src=x onerror=alert(1)>"


class BoundaryValues:
    CART_MAX_QUANTITY_TAPS = 20   # how many times to tap "+"
    HELP_SEARCH_NO_RESULTS = "ZZZZZNOTEXISTQATARAT"
    HELP_SEARCH_SPECIAL = "@#$%^&*()"
    HELP_SEARCH_SQL = "' OR 1=1 --"
    ORDER_SEARCH_EMPTY = ""
    ORDER_SEARCH_NO_RESULTS = "ORDERNOTEXIST9999"
    PROFILE_LONG_NAME = "A" * 200
    PROFILE_SPECIAL_CHARS = "User!@#$%^&*()"
    LOCATION_SEARCH_CITY = "Doha"
    LOCATION_SEARCH_ARABIC = "الدوحة"
    LOCATION_SEARCH_SPECIAL = "@#$%^"
    LOCATION_SEARCH_LONG = "A" * 200


class WalletData:
    VALID_TOPUP_AMOUNT = "50"
    ZERO_AMOUNT = "0"
    NEGATIVE_AMOUNT = "-10"
    ALPHA_AMOUNT = "abc"
    MAX_AMOUNT = "999999"
    DECIMAL_AMOUNT = "25.50"


class SubscriptionData:
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    SKIP = "Skip"
