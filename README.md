# Qatarat (قطرات) — Mobile App Test Suite

[![Maestro Smoke](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml)
[![Maestro Regression](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml)
[![Appium Deep Tests](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml)

**Flutter app** · Android & iOS · Package `com.qatarat.app`

📊 **[View Live Test Report →](https://qatarat.github.io/qatarat-automation/)**

---

## What is Qatarat?

Qatarat (قطرات — "Droplets") is a mosque and charity donation platform. Users can donate to mosques, calculate and pay Zakat, send Sadaqah, buy gift cards, subscribe to recurring donations, and watch live broadcasts. The app supports Arabic (RTL) and English.

---

## Test coverage at a glance

| Metric | Count |
|--------|-------|
| Maestro YAML flows | **50** |
| Appium Python tests | **191** |
| Total automated checks | **241** |
| Platforms | Android + iOS |
| CI workflows | 5 (GitHub Actions) |

---

## Enable the simulator — setup guide

### Android Emulator (Android Studio)

1. **Install Android Studio** → https://developer.android.com/studio
2. Open **SDK Manager** (top toolbar → SDK Manager icon)
   - Install **Android 14 (API 34)** SDK
3. Open **AVD Manager** (Device Manager in left panel)
   - Click **Create Virtual Device**
   - Choose **Pixel 7** → Next
   - Select **API 34 (Android 14 — Tiramisu)** → Download if needed → Next
   - Name it `Pixel_7_API_34` (must match exactly for CI) → Finish
4. Click **▶** to start the emulator
5. Verify with: `adb devices` — should list `emulator-5554`

```bash
# Quick launch from terminal (after SDK installed)
$ANDROID_HOME/emulator/emulator -avd Pixel_7_API_34 &
```

### iOS Simulator (Xcode — macOS only)

1. **Install Xcode** from the App Store (requires macOS 14+)
2. Open **Xcode → Preferences → Platforms** and download **iOS 17** simulator runtime
3. Launch simulator:
   ```bash
   # List available simulators
   xcrun simctl list devices | grep "iPhone 15"

   # Boot iPhone 15
   xcrun simctl boot "iPhone 15"

   # Open Simulator.app
   open -a Simulator
   ```
4. Install the IPA (for local Appium testing):
   ```bash
   xcrun simctl install booted "Qatarat (Lambda-Stage-IOS-1.8.2).ipa.zip"
   ```
5. Verify Appium iOS driver:
   ```bash
   appium driver install xcuitest
   appium driver list --installed
   ```

---

## Quick start — run tests locally

### Prerequisites

```bash
# Install Maestro
curl -Ls "https://get.maestro.mobile.dev" | bash

# Install Appium + drivers
npm install -g appium
appium driver install uiautomator2
appium driver install xcuitest
appium driver install --source=npm appium-flutter-driver

# Python virtualenv
cd testing/appium
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Run Maestro flows

```bash
cd testing

# Smoke (8 critical flows, ~8 min)
maestro test maestro/flows/suites/smoke.yaml

# Full regression (all 50 flows)
maestro test maestro/flows/suites/regression.yaml

# Negative tests only
maestro test maestro/flows/suites/negative.yaml

# Single flow by number
maestro test maestro/flows/26_mosque_profile_view.yaml
```

### Run Appium tests

```bash
cd testing/appium
source .venv/bin/activate

# All tests
python -m pytest tests/ -v --alluredir=allure-results

# By module
python -m pytest tests/donation/ -v
python -m pytest tests/payment/ -v
python -m pytest tests/mosque/ -v
python -m pytest tests/wallet/ -v
python -m pytest tests/account/ -v

# By marker
python -m pytest tests/ -m negative -v
python -m pytest tests/ -m security -v
python -m pytest tests/ -m boundary -v

# iOS (set env vars first)
PLATFORM=ios DEVICE_MODE=simulator python -m pytest tests/ -v
```

---

## CI / CD — GitHub Actions

| Workflow | Trigger | Duration | Coverage |
|----------|---------|----------|----------|
| Maestro Smoke | Every push / PR | ~8 min | 8 critical flows |
| Maestro Regression | Nightly 01:00 UTC | ~45 min | All 50 flows |
| Appium Deep Tests | Every Monday | ~75 min | 191 tests |
| Maestro iOS | Manual only | ~20 min | Smoke on iOS Simulator |
| Publish Report | After any test run | ~3 min | Deploys to GitHub Pages |

**GitHub Pages setup:**
1. Go to repository → **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** · Folder: **/docs**
4. Click **Save** — report available at your Pages URL

**Run a workflow manually:** [Actions tab](../../actions) → pick workflow → **Run workflow**

---

## What is tested — full coverage

### Maestro flows — 50 flows

**Happy-path flows (01–16)**

| # | Flow | What it covers |
|---|------|----------------|
| 01 | Splash / Onboarding | Country + language selection |
| 02 | Login OTP | Phone → OTP → logged-in home |
| 03 | Guest User | Guest browsing + login gate |
| 04 | Browse Services | Mosque listing + selection |
| 05 | Cart — Add Items | Cart controls, quantity, subtotal |
| 06 | Checkout — Payment | Payment method + promo code |
| 07 | Gift Card | Full send flow + WhatsApp preview |
| 08 | My Orders | List, detail view, rating |
| 09 | Subscription | Weekly / monthly recurring |
| 10 | Multi-language | Arabic, English, Urdu |
| 11 | No Internet | Offline error screen |
| 12 | Profile & Settings | Currency, About, Logout dialog |
| 13 | Help & Support | Help centre, WhatsApp, email |
| 14 | Manage Subscriptions | Active list, billing, cancel |
| 15 | Cancel Order | Cancel dialog, confirm / decline |
| 16 | Share App | Referral link sharing |

**Negative & boundary flows (17–25)**

| # | Flow | What it covers |
|---|------|----------------|
| 17 | Login — Invalid Phone | Empty, short, alpha, special-char blocked |
| 18 | Login — Wrong OTP | Wrong digits, all-zeros, resend visible |
| 19 | Invalid Promo Codes | Expired, SQL injection, special chars |
| 20 | Empty Cart Checkout | Checkout blocked when cart empty |
| 21 | Gift Card Validation | XSS, SQL injection, invalid phone |
| 22 | Cart Quantity Boundary | 10× increment, decrement below 1 |
| 23 | App Background / Resume | State preserved after backgrounding |
| 24 | Browse Search Edge Cases | Empty, long text, Arabic, special chars |
| 25 | Payment Input Edge Cases | Alpha CVV, expired date, SQL injection |

**Post-login deep coverage (26–50)**

| # | Flow | What it covers |
|---|------|----------------|
| 26 | Mosque Profile View | Profile, about, donation history |
| 27 | Donation — Zakat Flow | Zakat calculator, wealth entry, payment |
| 28 | Donation — Sadaqah | Quick donation, amount select, confirm |
| 29 | Donation — Recurring | Monthly subscription setup |
| 30 | Donation Gift Card | Gift donation, recipient, share |
| 31 | Wallet Top-Up | Top-up amount, payment method |
| 32 | Wallet Balance View | Balance check, transaction history |
| 33 | Payment Methods | Add card, verify in list |
| 34 | Promo Code — Valid | Apply valid promo at checkout |
| 35 | Promo Code — Invalid | Expired, wrong-format, SQL injection |
| 36 | Language — Arabic | Switch to Arabic, RTL layout |
| 37 | Language — English | Restore English |
| 38 | Profile Edit | Edit name/email, save |
| 39 | Logout | Logout, redirect to login |
| 40 | OTP Resend | Resend OTP button flow |
| 41 | Search — Mosque Name | Name search, results list |
| 42 | Search — Empty Results | No-results empty state |
| 43 | Search — Special Chars | @#$%^& — no crash |
| 44 | Notifications View | Notification panel, mark read |
| 45 | Deep Link Handling | qatarat:// URI → mosque profile |
| 46 | Live Broadcast View | Stream section, Agora join |
| 47 | Dark Mode Toggle | Dark mode in settings |
| 48 | Background Resume | Background 5s, state preserved |
| 49 | Accessibility Labels | Key elements have accessibility text |
| 50 | Session Handling | Session persists after restart |

---

### Appium deep tests — 191 tests

| Module | File(s) | Tests | Focus |
|--------|---------|-------|-------|
| Authentication | `auth/test_login_negative.py`, `test_auth_edge_cases.py` | 18 | Phone/OTP, SQL injection, XSS, session |
| Donation | `donation/test_donation_flow.py`, `test_zakat.py` | 18 | Amount boundaries, Zakat calc, Sadaqah |
| Payment | `payment/test_card_payment.py`, `test_payment_negative.py`, `test_payment_extended.py`, `test_tabby_bnpl.py`, `test_bank_transfer.py` | 23 | HyperPay, Tabby BNPL, bank transfer, card validation |
| Wallet | `wallet/test_wallet.py` | 8 | Balance, top-up, transaction history |
| Gift Cards | `gift/test_gift_card.py`, `test_gift_card_boundary.py` | 18 | XSS, SQL injection, Arabic name, WhatsApp |
| Subscriptions | `subscription/test_subscription.py`, `test_subscription_boundary.py` | 22 | Weekly/monthly, billing, cancel |
| Orders | `orders/test_orders_edge_cases.py` | 11 | Empty feedback, cancel, ratings |
| Mosque & Search | `mosque/test_mosque_profile.py`, `browse/test_browse_search.py` | 16 | Name search, Arabic query, XSS, SQL |
| Promo Codes | `promo/test_promo_codes.py` | 9 | Expired, SQL injection, case sensitivity |
| Cart | `cart/test_cart_boundary.py` | 6 | Empty checkout, NaN, boundary |
| Checkout | `checkout/test_checkout_edge_cases.py` | 10 | Promo expired, edge inputs |
| Account | `account/test_profile.py`, `test_profile_edge_cases.py`, `test_logout.py`, `test_edit_profile.py` | 28 | Profile edit, SQL/XSS, logout, re-login |
| Live Broadcast | `streaming/test_live_broadcast.py` | 8 | Agora RTC, offline, permissions |

---

## Test scenario types

Every feature tests all input classes:

| Type | Examples |
|------|---------|
| ✅ Valid | Correct phone, valid amounts, real promo codes |
| ❌ Invalid | Wrong format, expired codes, bad card numbers |
| 🔲 Empty | Blank fields, zero amounts |
| ⚠️ Boundary | Min/max values, 256-char strings, very large numbers |
| 🔐 Security | SQL injection: `'; DROP TABLE users --`, XSS: `<script>alert(1)</script>` |
| 🌍 Unicode | Arabic text `محمد أحمد`, emoji `😀🕌🙏` |
| ✏️ Edge | Mixed case, extra spaces, special chars `@#$%^&*` |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| **App** | Flutter / Dart |
| **UI automation** | [Maestro](https://maestro.mobile.dev) 2.x — YAML flows |
| **Deep tests** | [Appium](https://appium.io) 2.x + `appium-flutter-driver` |
| **Test language** | Python 3 · pytest · allure |
| **Reporting** | Allure + GitHub Pages dashboard |
| **CI / CD** | GitHub Actions (free — Ubuntu + Android emulator) |
| **Android** | Pixel 7 API 34 emulator |
| **iOS** | iPhone 15 iOS 17 Simulator (Xcode) |

---

## Project structure

```
testing/
├── maestro/
│   ├── flows/
│   │   ├── 01_splash_onboarding.yaml … 50_session_handling.yaml
│   │   └── suites/
│   │       ├── smoke.yaml        # 8 critical flows
│   │       ├── regression.yaml   # all 50 flows
│   │       └── negative.yaml     # negative/boundary only
│   └── config/app_config.yaml
├── appium/
│   ├── capabilities/
│   │   ├── android_caps.py
│   │   └── ios_caps.py
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── cart_page.py
│   │   ├── checkout_page.py
│   │   ├── orders_page.py
│   │   ├── donation_page.py
│   │   ├── mosque_page.py
│   │   ├── wallet_page.py
│   │   └── profile_page.py
│   ├── tests/
│   │   ├── auth/       donation/  mosque/     wallet/
│   │   ├── payment/    gift/      subscription/ orders/
│   │   ├── cart/       checkout/  promo/      browse/
│   │   ├── account/    streaming/
│   ├── conftest.py
│   └── test_data.py
docs/
├── index.html   ← live report dashboard (GitHub Pages)
└── .nojekyll
```

---

## Local commands

```bash
cd testing

# Maestro
maestro test maestro/flows/suites/smoke.yaml
maestro test maestro/flows/suites/regression.yaml
maestro test maestro/flows/26_mosque_profile_view.yaml   # single flow

# Appium
cd appium && source .venv/bin/activate
python -m pytest tests/ -v --alluredir=allure-results
python -m pytest tests/donation/ -v
python -m pytest tests/ -m negative -v
python -m pytest tests/ -m security -v
allure serve allure-results   # open Allure report locally

# iOS (macOS only)
PLATFORM=ios DEVICE_MODE=simulator python -m pytest tests/ -v
```

---

*Built by **Mejbaur Bahar Fagun** · Senior Software Engineer QA (IV) · [LinkedIn](https://www.linkedin.com/in/mejbaur/)*
