# Qatarat (قطرات) — Automated Testing Suite

[![Maestro Smoke](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml)
[![Maestro Regression](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml)
[![Appium Android](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml)
[![Maestro iOS](https://github.com/Qatarat/qatarat-automation/actions/workflows/04-maestro-ios.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/04-maestro-ios.yml)
[![Appium iOS](https://github.com/Qatarat/qatarat-automation/actions/workflows/06-appium-ios.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/06-appium-ios.yml)

📊 **[View the Live Test Report Dashboard →](https://qatarat.github.io/qatarat-automation/)**

---

## What is this project?

**Qatarat (قطرات)** means "Droplets" in Arabic. It is a mobile app that lets people donate to mosques, pay Zakat, send Sadaqah, buy gift cards, and set up recurring charity donations. It supports Arabic and English, works on both Android and iOS phones.

**This repository** contains a fully automated testing system that checks whether the Qatarat app works correctly — without a human clicking through it every time. Think of it as a robot that opens the app, taps buttons, fills in forms, and checks that everything is working as expected, 24 hours a day.

---

## Why do we test automatically?

Every time a developer makes a change to the app, there is a risk something that worked before might stop working. Running 241 test checks by hand every day would take a team of testers many hours. With automation:

- **Tests run by themselves** every night and every time new code is pushed
- **Problems are caught immediately** — a developer sees a failure within minutes
- **The live dashboard** shows exactly which tests passed, which failed, and why
- **Both Android and iOS** are tested on real virtual devices

---

## Quick overview — numbers

| What | How many |
|------|----------|
| App scenarios (Maestro flows) | **50** |
| Deep automated tests (Appium) | **191** |
| Total automated checks | **241** |
| Platforms tested | **Android + iOS** |
| How often tests run | **Daily (automated)** |

---

## Live test report

The test results are published automatically to a dashboard website after every test run:

👉 **[Open the dashboard](https://qatarat.github.io/qatarat-automation/)**

The dashboard shows:
- A green/red summary of all 241 tests
- Results split by Android and iOS
- A run history (last 30 runs)
- Which exact step failed and why

---

## What is tested?

The automated tests cover **every main feature of the Qatarat app**:

| Area | What is checked |
|------|----------------|
| **Login** | Phone number entry, OTP code, wrong codes, resend |
| **Guest browsing** | Browsing without an account, login prompt |
| **Mosque listing** | Searching, filtering, profile pages |
| **Cart** | Adding items, changing quantity, removing, empty cart |
| **Checkout** | Payment methods, promo codes, order confirmation |
| **Donations** | Zakat calculator, Sadaqah, recurring donations |
| **Gift cards** | Sending, recipient details, WhatsApp share |
| **Wallet** | Balance, top-up, transaction history |
| **Saved cards** | Add card, view saved cards |
| **Profile** | Edit name/email, change language, currency |
| **Logout** | Logout and redirect to login screen |
| **Language** | Arabic (right-to-left), English |
| **Subscriptions** | Weekly/monthly setup, billing, cancel |
| **Security** | SQL injection, XSS attacks — app must not crash |
| **Edge cases** | Empty fields, very long text, special characters, Arabic text |
| **Offline** | App shows correct error when there is no internet |

---

## How it works — plain English

```
Developer pushes code
        ↓
GitHub Actions starts the robots automatically
        ↓
Robot opens the app in a virtual phone (Android or iOS)
        ↓
Robot taps buttons and fills in forms — just like a real user
        ↓
Robot checks: did the right screen appear? Is the text correct?
        ↓
Results are collected and published to the dashboard website
        ↓
Team sees green ✅ or red ❌ within minutes
```

There are two kinds of robots:

- **Maestro** — Reads simple instruction files (`.yaml`) and acts like a user tapping the screen. Easy to read, fast to write.
- **Appium** — More powerful, written in Python. Tests complicated things like card payments, security attacks, and edge cases.

---

## Setup guide — Android (step by step)

You need Android Studio to create a virtual Android phone on your computer.

### Step 1 — Install Android Studio

1. Go to **https://developer.android.com/studio** and download Android Studio
2. Open the installer and follow the on-screen steps (click Next → Next → Install → Finish)

### Step 2 — Install the Android 14 SDK

1. Open Android Studio
2. Click the **SDK Manager** icon in the toolbar (looks like a box with a down arrow)
3. Under **SDK Platforms**, tick **Android 14 (API Level 34)**
4. Click **Apply → OK** and wait for the download to finish

### Step 3 — Create a virtual Android phone

1. In Android Studio, click **Device Manager** (phone icon on the left side panel)
2. Click **Create Virtual Device**
3. Select **Pixel 7** → click **Next**
4. Select **API 34 (Android 14 — Tiramisu)** → click **Download** if shown → click **Next**
5. Name it exactly: `Pixel_7_API_34` → click **Finish**

### Step 4 — Start the virtual phone

1. In Device Manager, find `Pixel_7_API_34` and click the **▶ (Play)** button
2. Wait about 30 seconds for the Android phone to appear on screen
3. Open a Terminal and type: `adb devices`
4. You should see `emulator-5554 device` — this means it is ready

### Step 5 — Install the Qatarat app on it

```bash
# Install the APK (the Android app file)
adb install "path/to/qatarat.apk"
```

---

## Setup guide — iOS (step by step, Mac only)

iOS testing only works on a Mac computer because Apple only allows Xcode on Mac.

### Step 1 — Install Xcode

1. Open the **App Store** on your Mac
2. Search for **Xcode** and click **Get** (it is free, but large — about 12 GB)
3. Wait for the download and click **Open** when done
4. Accept the license agreement

### Step 2 — Download the iOS 17 simulator

1. In Xcode, go to the menu: **Xcode → Settings → Platforms**
2. Find **iOS 17** and click the **+** button to download it
3. Wait for the download (about 5 GB)

### Step 3 — Start the iPhone simulator

Open a Terminal app and type these commands one at a time:

```bash
# Start the iPhone 15 simulator
xcrun simctl boot "iPhone 15"

# Open the Simulator app on screen
open -a Simulator
```

A virtual iPhone will appear on your screen.

### Step 4 — Install the Qatarat iOS app

The iOS app file is already in this project folder. Install it:

```bash
# Find the booted simulator ID
SIM=$(xcrun simctl list devices booted | grep -oE "[A-F0-9-]{36}" | head -1)

# Install the app
xcrun simctl install "$SIM" "Qatarat (Lambda-Stage-IOS-1.8.2).ipa/Payload/Runner.app"
```

---

## Setup guide — Testing tools

Install these tools once on your computer. Then you can run any test.

### Install Maestro (the simple test robot)

Open Terminal and paste this command:

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

After it finishes, close Terminal and open a new one. Test it works:

```bash
maestro --version
```

### Install Appium (the advanced test robot)

You need **Node.js** first. Download it from **https://nodejs.org** and install it.

Then in Terminal:

```bash
# Install Appium
npm install -g appium

# Install Android support
appium driver install uiautomator2

# Install iOS support
appium driver install xcuitest

# Install Flutter support (Qatarat is a Flutter app)
appium driver install --source=npm appium-flutter-driver

# Check everything installed correctly
appium driver list --installed
```

### Install Python dependencies (for Appium tests)

```bash
# Go into the appium folder
cd testing/appium

# Create an isolated Python environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate   # Mac / Linux
# On Windows: .venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

---

## How to run tests

### Run the quick smoke test (8 most important flows, ~8 minutes)

This is the fastest check. Run it after any code change to confirm nothing critical broke.

```bash
cd testing
maestro test maestro/flows/suites/smoke.yaml
```

### Run all 50 scenario flows (~45 minutes)

```bash
cd testing
maestro test maestro/flows/suites/regression.yaml
```

### Run just one specific scenario

```bash
# Example: test the login flow
maestro test maestro/flows/02_login_otp.yaml

# Example: test mosque profile
maestro test maestro/flows/26_mosque_profile_view.yaml
```

### Run all 191 Appium deep tests (Android, ~75 minutes)

```bash
cd testing/appium
source .venv/bin/activate
python -m pytest tests/ -v
```

### Run Appium tests for just one area

```bash
# Only donation tests
python -m pytest tests/donation/ -v

# Only payment tests
python -m pytest tests/payment/ -v

# Only security tests
python -m pytest tests/ -m security -v
```

### Run tests on iOS simulator (Mac only)

```bash
# All tests on iPhone 15
PLATFORM=ios DEVICE_MODE=simulator python -m pytest tests/ -v

# Just one area on iOS
PLATFORM=ios DEVICE_MODE=simulator python -m pytest tests/donation/ -v
```

---

## Automated schedule — when do tests run automatically?

Tests run by themselves on GitHub Actions (a free cloud service). You do not need to do anything — they run automatically:

| Test suite | When it runs | Duration | What it covers |
|-----------|-------------|----------|---------------|
| Smoke (Android) | Every time code is pushed | ~8 min | 8 critical flows |
| Full regression (Android) | Every night at 1:00 AM UTC | ~45 min | All 50 flows |
| Appium deep tests (Android) | Every Monday | ~75 min | 191 deep tests |
| Maestro (iOS simulator) | Every Tuesday at 3:00 AM UTC | ~30 min | All 50 flows on iPhone |
| Appium deep tests (iOS) | Every Wednesday at 4:00 AM UTC | ~90 min | 191 deep tests on iPhone |
| Publish dashboard | After every test run | ~3 min | Updates the live website |

### How to run a test manually (without waiting for the schedule)

1. Go to the **Actions** tab at the top of this GitHub repository
2. Click on any workflow name (e.g. "Maestro Smoke")
3. Click the **Run workflow** button on the right side
4. Click the green **Run workflow** button
5. Wait for it to finish — then check the dashboard

---

## Setting up the live dashboard (one time)

The dashboard is a website hosted for free on GitHub Pages.

1. Go to the repository on GitHub
2. Click **Settings** (top right of the repo page)
3. In the left menu, click **Pages**
4. Under **Source**, select **Deploy from a branch**
5. Set **Branch** to `main` and **Folder** to `/docs`
6. Click **Save**
7. After a minute, your dashboard will be live at: `https://YOUR-ORG.github.io/qatarat-automation/`

---

## Test credentials (for running tests locally)

The test account used in all tests:

| Field | Value |
|-------|-------|
| Phone number | `8801685220417` |
| OTP code | `1234` (test environment only) |
| Environment | Stage (not production) |

> ⚠️ These credentials only work in the test/staging environment. They do not affect real users or real money.

---

## Project structure — where everything lives

```
Qatarat/
│
├── README.md                    ← This file
│
├── .github/
│   └── workflows/
│       ├── 01-maestro-smoke.yml       ← Smoke test (runs on every push)
│       ├── 02-maestro-regression.yml  ← Full nightly regression
│       ├── 03-appium-android.yml      ← Deep Android tests (Monday)
│       ├── 04-maestro-ios.yml         ← iOS flows (Tuesday)
│       ├── 05-publish-report.yml      ← Publishes dashboard (after tests)
│       └── 06-appium-ios.yml          ← Deep iOS tests (Wednesday)
│
├── testing/
│   ├── maestro/
│   │   ├── flows/
│   │   │   ├── 01_splash_onboarding.yaml
│   │   │   ├── 02_login_otp.yaml
│   │   │   │   … (50 flow files total)
│   │   │   └── suites/
│   │   │       ├── smoke.yaml        ← 8 quick critical flows
│   │   │       ├── regression.yaml   ← All 50 flows
│   │   │       └── negative.yaml     ← Error/edge case flows only
│   │   └── config/
│   │       └── app_config.yaml
│   │
│   ├── appium/
│   │   ├── capabilities/
│   │   │   ├── android_caps.py       ← Android device settings
│   │   │   └── ios_caps.py           ← iOS device settings
│   │   ├── pages/                    ← Each file = one screen in the app
│   │   │   ├── login_page.py
│   │   │   ├── cart_page.py
│   │   │   ├── donation_page.py
│   │   │   └── … (9 page files)
│   │   ├── tests/                    ← The actual test files
│   │   │   ├── auth/
│   │   │   ├── donation/
│   │   │   ├── payment/
│   │   │   ├── wallet/
│   │   │   ├── gift/
│   │   │   ├── subscription/
│   │   │   ├── orders/
│   │   │   ├── mosque/
│   │   │   ├── browse/
│   │   │   ├── promo/
│   │   │   ├── cart/
│   │   │   ├── checkout/
│   │   │   ├── account/
│   │   │   └── streaming/
│   │   ├── conftest.py               ← Test setup and teardown
│   │   └── requirements.txt          ← Python packages list
│   │
│   └── generate_data_js.py           ← Builds dashboard data from test results
│
└── docs/
    ├── index.html                    ← The live dashboard website
    └── .nojekyll                     ← Tells GitHub Pages how to serve the site
```

---

## Troubleshooting — common problems and fixes

### "adb: command not found"
Android tools are not in your PATH. Add this to your `~/.zshrc` or `~/.bashrc`:
```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
```
Then close and reopen Terminal.

### "maestro: command not found"
After installing Maestro, close Terminal completely and open a new window. The install script modifies your PATH but only in new sessions.

### Emulator won't start
Make sure **Hardware Acceleration** is enabled:
- On Mac: HAXM is usually automatic
- On Windows: Enable **Intel HAXM** in Android Studio's SDK Manager

### iOS simulator: "Unable to boot device"
```bash
# Reset the simulator
xcrun simctl erase all
xcrun simctl boot "iPhone 15"
```

### Tests fail with "App not found"
Make sure the Qatarat APK/IPA is installed on the device first. See the setup steps above.

### Dashboard not updating
Run the **Publish Report** workflow manually from the Actions tab after a test run finishes.

---

## Maestro flows — full list

| # | Flow name | What it tests |
|---|-----------|--------------|
| 01 | Splash & Onboarding | Country selection, language picker |
| 02 | Login OTP | Phone entry → OTP code → home screen |
| 03 | Guest User | Browsing without login, login prompt |
| 04 | Browse Services | Mosque listing, selecting a mosque |
| 05 | Cart — Add Items | Add to cart, change quantity, see subtotal |
| 06 | Checkout — Payment | Select payment method, apply promo code |
| 07 | Gift Card | Send a gift donation, WhatsApp share preview |
| 08 | My Orders | Order list, order detail, leave a rating |
| 09 | Subscription | Weekly and monthly recurring donation setup |
| 10 | Multi-language | Switch between Arabic, English, Urdu |
| 11 | No Internet | Correct error shown when offline |
| 12 | Profile & Settings | Currency, about page, logout dialog |
| 13 | Help & Support | Help centre, WhatsApp, email support links |
| 14 | Manage Subscriptions | Active list, billing details, cancel |
| 15 | Cancel Order | Cancel dialog — confirm and decline paths |
| 16 | Share App | Referral link sharing |
| 17 | Login — Invalid Phone | Empty, too short, letters, symbols — all blocked |
| 18 | Login — Wrong OTP | Wrong digits, all zeros, resend button visible |
| 19 | Invalid Promo Codes | Expired, SQL injection, special characters |
| 20 | Empty Cart Checkout | Checkout blocked when cart is empty |
| 21 | Gift Card Validation | XSS, SQL injection, invalid phone number |
| 22 | Cart Quantity Boundary | Max increment, cannot go below 1 |
| 23 | Background & Resume | App state preserved after going to home screen |
| 24 | Search Edge Cases | Empty search, very long text, Arabic, symbols |
| 25 | Payment Input Edge Cases | Letters in CVV, expired date, SQL injection |
| 26 | Mosque Profile View | Profile details, about tab, donation history |
| 27 | Donation — Zakat | Zakat calculator, enter wealth, proceed to payment |
| 28 | Donation — Sadaqah | Quick donation, select amount, confirm |
| 29 | Donation — Recurring | Set up monthly charity subscription |
| 30 | Donation — Gift Card | Gift donation with recipient and share |
| 31 | Wallet — Top-Up | Add money to wallet balance |
| 32 | Wallet — Balance View | Check balance, see transaction history |
| 33 | Payment Methods — Manage | Add a card, verify it appears in saved list |
| 34 | Promo Code — Valid | Apply a working promo at checkout |
| 35 | Promo Code — Invalid | Expired, wrong format, SQL injection at checkout |
| 36 | Language — Arabic | Switch to Arabic, confirm RTL layout |
| 37 | Language — English | Restore English language |
| 38 | Profile Edit | Edit name and email, save changes |
| 39 | Logout | Log out, redirected to login screen |
| 40 | OTP Resend | Tap resend OTP button, new code arrives |
| 41 | Search — Mosque Name | Type a mosque name, see results |
| 42 | Search — No Results | Search that returns nothing — shows empty state |
| 43 | Search — Special Characters | `@#$%^&` in search — no crash |
| 44 | Notifications View | Open notification panel, mark as read |
| 45 | Deep Link Handling | `qatarat://` link opens correct mosque profile |
| 46 | Live Broadcast View | Streaming section, join button |
| 47 | Dark Mode Toggle | Enable dark mode in settings |
| 48 | Background Resume | Background for 5 seconds, state preserved |
| 49 | Accessibility Labels | Key buttons have readable accessibility text |
| 50 | Session Handling | Session persists after closing and reopening app |

---

## Tech stack — what tools are used

| Tool | What it does |
|------|-------------|
| **Flutter / Dart** | The Qatarat app itself is built with Flutter |
| **Maestro** | Simple YAML-based UI automation — clicks, types, asserts |
| **Appium** | Advanced automation — deep tests, security, edge cases |
| **Python / pytest** | Language used to write the Appium tests |
| **Allure** | Generates detailed HTML test reports locally |
| **GitHub Actions** | Runs tests automatically in the cloud for free |
| **GitHub Pages** | Hosts the live dashboard website for free |
| **Android Emulator** | Virtual Pixel 7 phone (Android 14) for testing |
| **iOS Simulator** | Virtual iPhone 15 (iOS 17) for testing (Mac only) |

---

## Contact / author

Built and maintained by **Mejbaur Bahar Fagun** — Senior Software Engineer QA (IV)

- LinkedIn: [linkedin.com/in/mejbaur](https://www.linkedin.com/in/mejbaur/)
- Email: mejbaur@markopolo.ai

---

*If you find a bug in the tests or want to add new test coverage, open a GitHub Issue or pull request.*
