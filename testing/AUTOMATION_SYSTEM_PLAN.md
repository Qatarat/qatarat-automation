# Qatarat Mobile Automation System Plan

## Goal

Produce a valid, non-fabricated automation report for Android and iOS using only real CI artifacts:

- Maestro UI journeys: 50 YAML flows.
- Appium deep tests: 252 pytest tests.
- Platforms: Android emulator and iOS simulator.
- Outputs: JUnit XML, Allure results, screenshots, videos, GitHub Pages dashboard, run history.

## Phase 1: Report Validity

Status: implemented.

- Ignore cancelled GitHub Actions runs when choosing source artifacts for Pages.
- Preserve separate Android/iOS result channels.
- Show `Pending` for missing XML instead of turning idle tests into failures.
- Count iOS Appium and iOS Maestro in generated run metadata.
- Validate dashboard inventory against real pytest files before publish.

## Phase 2: CI Reliability

Status: implemented.

- Keep Android Appium matrix split by feature group. ✅
- Keep iOS Appium matrix split by same feature groups. ✅
- Add per-group source metadata: run id, group name, platform, conclusion. ✅ (run-history.json `groups` array)
- Add fail-fast disabled for all matrix suites. ✅
- Store app release tag used by each run in report metadata. ✅ (`apk_tag` / `ipa_tag` in run-history.json via metadata artifacts)

## Phase 3: Test Data Contract

Status: implemented.

- Centralize phone, OTP, donation amounts, promo codes, card numbers, Arabic/unicode strings, XSS, SQL injection, and boundary values in `testing/appium/test_data.py`. ✅
- Mirror Maestro test data in `testing/maestro/config/app_config.yaml`. ✅
- Mark destructive or payment-side-effect tests clearly. ✅ (`DESTRUCTIVE = True` on `ValidData`, `WalletData`, `SubscriptionData`, `DonationData`)
- Add environment variables for stage/prod-safe data override. ✅ (`TEST_PHONE`, `TEST_OTP`, `TEST_PROMO`, `TEST_WALLET_TOPUP`, `TEST_DONATION_*`)

## Phase 4: Scenario Coverage

Status: existing coverage, needs continuous audit.

- Auth: login, OTP, invalid phone, wrong OTP, session handling.
- Account: profile edit, logout, settings, help, currency, delete-account dialog.
- Donation: valid, invalid, boundary, Zakat, recurring, gift donation.
- Commerce: cart, checkout, payment, wallet, promo, subscription, gift card.
- Browse: search, mosque profile, home feed, location, favourites.
- Resilience: no internet, background/resume, deep link, app restart.
- Quality: accessibility labels, RTL/language, dark mode, notifications, streaming.
- Security probes: SQL injection, XSS, special characters, long input, emoji/unicode.

## Phase 5: Reporting

Status: implemented.

- GitHub step summaries per matrix group. ✅
- Pages dashboard with Android/iOS tabs. ✅
- Allure report with history. ✅
- Screenshots and recordings copied to Pages. ✅
- Run history from `run-history.json`. ✅
- Source-run badges and links per platform/group. ✅ (run URL in history entries; per-group table in publish summary; `[View run]` links in Appium matrix summaries)

## Operating Rule

Dashboard must never invent pass/fail counts. Missing artifacts mean `Pending`. Cancelled runs must not overwrite the last valid report.
