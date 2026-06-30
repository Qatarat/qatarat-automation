# Mobile Test Coverage Matrix

Purpose: keep Android and iOS coverage complete, explicit, and reviewable. The machine source is `testing/mobile_coverage_contract.json`; `testing/validate_report_inventory.py` fails if required coverage paths disappear.

## Current Inventory

- Appium pytest: 252 tests across Android/iOS suites.
- Maestro flows: 50 end-to-end flows.
- Platforms: Android APK, iOS simulator workflow, BrowserStack iOS helper.
- Reports: JUnit, HTML, Allure, screenshots, dashboard data.

## Feature Domains

| Domain | Appium coverage | Maestro coverage |
|---|---|---|
| Onboarding, country, language | auth edge cases, iOS auth | splash onboarding, multilanguage |
| Auth, OTP, session | login negative, OTP edge, iOS auth | login OTP, invalid phone, wrong OTP, OTP resend, session handling |
| Guest, browse, search | browse/search edge suite | guest, browse services, search name/empty/special |
| Home, mosque profile | home feed, mosque profile | mosque profile view |
| Cart, checkout, subscription | cart, checkout, subscription boundary | cart add, checkout, subscriptions, empty cart, quantity boundary |
| Payment, promo | bank transfer, card, extended payment, negative payment, Tabby, promo | invalid promo, payment edge, payment methods, valid/invalid promo |
| Donation, zakat, recurring | donation flow, zakat | zakat, sadaqah, recurring donation |
| Gift card | gift card, gift boundary | gift card, gift validation, donation gift card |
| Wallet | wallet top-up/balance/history | wallet top-up, wallet balance |
| Profile, account, help, logout | edit profile, logout, profile, profile edge | profile settings, help support, profile edit, logout |
| Orders, booking, rating | orders edge, booking, rating | my orders, cancel order |
| Notifications, streaming, location, favourites | notifications, live broadcast, location, favourites | notifications, live broadcast |
| Share, deep link, lifecycle, network, accessibility | browse/home/location stability checks | no internet, share, background/resume, deep link, dark mode, accessibility |

## Test Types

| Type | Coverage |
|---|---|
| Smoke | Maestro smoke suite, Appium smoke markers |
| Regression | Maestro regression suite, Appium matrix groups |
| Negative | invalid phone, wrong OTP, invalid promo, empty cart, payment negatives |
| Boundary | cart quantity, gift card boundaries, subscription boundaries, long/empty inputs |
| Security/input abuse | SQL strings, XSS-like strings, special chars, emoji, long input |
| Localization | Arabic language switch, Arabic input, iOS locale |
| Accessibility | Maestro accessibility labels flow |
| Offline/lifecycle | no internet, background/resume, session restore |
| Platform | Android caps/workflow, iOS caps/workflows |

## Test Data

`testing/appium/test_data.py` owns all reusable values:

- `ValidData`
- `InvalidPhone`
- `InvalidOTP`
- `InvalidCard`
- `InvalidPromo`
- `InvalidGift`
- `InvalidRating`
- `BoundaryValues`
- `WalletData`
- `SubscriptionData`

## Validation Commands

```bash
python3 testing/validate_report_inventory.py
python3 -m py_compile testing/validate_report_inventory.py testing/generate_data_js.py testing/appium/conftest.py
bash -n testing/run_appium_ci.sh testing/run_maestro_ios_ci.sh testing/run_smoke_ci.sh testing/run_regression_ci.sh
```

## Rule

No feature may be removed, skipped, renamed, or moved without updating `testing/mobile_coverage_contract.json` and passing validation.
