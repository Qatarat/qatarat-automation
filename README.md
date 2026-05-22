# Qatarat (قطرات) — Mobile App Test Suite

[![Maestro Smoke](../../actions/workflows/01-maestro-smoke.yml/badge.svg)](../../actions/workflows/01-maestro-smoke.yml)
[![Maestro Regression](../../actions/workflows/02-maestro-regression.yml/badge.svg)](../../actions/workflows/02-maestro-regression.yml)
[![Appium Deep Tests](../../actions/workflows/03-appium-android.yml/badge.svg)](../../actions/workflows/03-appium-android.yml)

**Flutter app** · Android & iOS · Package `com.qatarat.app`

📊 **[View Live Test Report →](https://mejbaurbahar.github.io/Qatarat/)**

---

## Test on your phone (USB) — anyone can do this

### macOS / Linux

```bash
# 1. Clone the repo
git clone https://github.com/mejbaurbahar/Qatarat.git
cd Qatarat/testing

# 2. Install all tools (Java, ADB, Maestro, Appium, Python)
bash install.sh
source ~/.zshrc        # or source ~/.bashrc on Linux

# 3. Enable USB Debugging on your Android phone:
#    Settings → About Phone → tap Build Number 7 times
#    Settings → Developer Options → turn on USB Debugging
#    Connect phone via USB → tap Allow on the dialog that appears

# 4. Launch the interactive menu
bash run_on_device.sh
```

### Windows (WSL — recommended)

WSL (Windows Subsystem for Linux) lets you run the full test suite on Windows without any manual tool installation.

**One-time WSL setup (PowerShell as Administrator):**

```powershell
wsl --install
# Restart your PC when prompted
```

**After restart — open the WSL (Ubuntu) terminal:**

```bash
# Clone into WSL filesystem (faster I/O than /mnt/c or /mnt/h)
cd ~
git clone https://github.com/mejbaurbahar/Qatarat.git
cd Qatarat/testing

# Install everything automatically
bash install.sh
source ~/.bashrc

# Connect your Android phone via USB, then:
bash run_on_device.sh
```

> **USB devices in WSL:** WSL 2 needs [usbipd-win](https://github.com/dorssel/usbipd-win) to pass USB devices through.
> Install it from that link, then in an **elevated PowerShell**:
> ```powershell
> usbipd list                    # find your phone's BUSID
> usbipd attach --wsl --busid <BUSID>
> ```
> Then in WSL: `adb devices` should show your phone.

**Alternatively — run directly from Windows (no WSL):**

If you prefer native Windows, install each tool manually:

| Tool | Download |
|------|----------|
| Java 17 | https://adoptium.net/temurin/releases/?version=17 |
| Android Platform Tools (ADB) | https://developer.android.com/tools/releases/platform-tools |
| Node.js LTS | https://nodejs.org |
| Python 3 | https://www.python.org/downloads/ |

Then in **PowerShell**:
```powershell
# Maestro
iex "& { $(irm 'https://get.maestro.mobile.dev') }"

# Appium
npm install -g appium
appium driver install uiautomator2
appium driver install --source=npm appium-flutter-driver

# Python deps
cd H:\Qatarat\testing
python -m venv appium\.venv
appium\.venv\Scripts\pip install -r appium\requirements.txt

# Run Maestro flows (use Git Bash for .sh scripts)
bash run_maestro.sh
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| **App** | Flutter / Dart |
| **UI automation** | [Maestro](https://maestro.mobile.dev) 2.x — YAML flows |
| **Deep tests** | [Appium](https://appium.io) 2.x + `appium-flutter-driver` + `uiautomator2` |
| **Test language** | Python 3 with `pytest` |
| **Reporting** | [Allure](https://allurereport.org) + GitHub Pages dashboard |
| **CI / CD** | GitHub Actions (free — Ubuntu + Android emulator) |
| **Device** | Android API 33 emulator (CI) or any USB Android phone (local) |

---

## CI / CD — GitHub Actions (all free)

| Workflow | Trigger | Duration | Coverage |
|----------|---------|----------|----------|
| Maestro Smoke | Every push / PR | ~10 min | Login, cart, checkout |
| Maestro Regression | Nightly 01:00 UTC | ~30 min | All 23 flows |
| Appium Deep Tests | Every Monday | ~60 min | Payment, gift, subscriptions, account |
| Maestro iOS | Manual only | ~20 min | Smoke on iOS Simulator |
| Publish Report | After any test run | ~3 min | Deploys to GitHub Pages |

**Run any workflow manually:** [Actions tab](../../actions) → pick workflow → **Run workflow**

> **First-time setup:** Go to **Settings → Pages → Source → GitHub Actions** to enable the report page.

---

## What is tested (full coverage)

### Maestro flows — 23 flows (16 happy-path + 7 negative/boundary)

**Happy-path flows**

| # | Flow | What it covers |
|---|------|---------------|
| 01 | Splash / Onboarding | Country + language selection |
| 02 | Login OTP | Phone → OTP → logged in |
| 03 | Guest User | Guest browsing + login gate |
| 04 | Browse Services | Mosque listing + selection |
| 05 | Cart | Add items, quantity, price, tax |
| 06 | Checkout | Payment method + promo code |
| 07 | Gift Card | Full send flow + WhatsApp preview |
| 08 | My Orders | List, detail, rating |
| 09 | Subscription | Weekly / monthly recurring |
| 10 | Multi-language | Arabic, Turkish, Urdu, English |
| 11 | No Internet | Offline error screen |
| 12 | Profile & Settings | Currency, About, Logout dialog |
| 13 | Help & Support | Help centre, WhatsApp, email |
| 14 | Manage Subscriptions | Active list, billing history, cancel |
| 15 | Cancel Order | Cancel dialog, confirm/decline |
| 16 | Share App | Referral link sharing |

**Negative & boundary flows**

| # | Flow | What it covers |
|---|------|---------------|
| 17 | Login — Invalid Phone | Empty, too-short, alpha, special-char phone all blocked |
| 18 | Login — Wrong OTP | Wrong digits, all-zeros OTP rejected; resend link visible |
| 19 | Invalid Promo Codes | Wrong, empty, special-char, SQL injection all rejected |
| 20 | Empty Cart Checkout | Checkout blocked when cart is empty |
| 21 | Gift Card Validation | Empty form, invalid phone, XSS, SQL injection |
| 22 | Cart Quantity Boundary | 10× increment, decrement below 1, NaN check |
| 23 | App Background / Resume | Cart state preserved after backgrounding |

### Appium deep tests — 92 tests (31 happy-path + 61 negative/boundary)

**Happy-path tests**

| File | Tests |
|------|-------|
| `test_card_payment.py` | HyperPay card success, expired card, declined, promo code |
| `test_tabby_bnpl.py` | Tabby visibility, Shariah badge, Learn More, cancel |
| `test_bank_transfer.py` | Account details, receipt upload prompt, photo/gallery options |
| `test_gift_card.py` | Field validation, preview accuracy, gifts received section |
| `test_subscription.py` | Weekly, monthly, skip, success banner, unavailable items |
| `test_live_broadcast.py` | Broadcast screen, visual docs, permission handling |
| `test_profile.py` | Currency, About page, logout dialog, delete account, billing history |

**Negative & boundary tests**

| File | Tests | What gets caught |
|------|-------|-----------------|
| `auth/test_login_negative.py` | 9 | Alpha/empty/short phone accepted? Wrong OTP lets you in? |
| `cart/test_cart_boundary.py` | 6 | Empty cart checkout, NaN on high quantity, decrement below 1 |
| `payment/test_payment_negative.py` | 8 | Invalid card numbers, bad expiry, empty CVV, blank name |
| `promo/test_promo_codes.py` | 9 | Expired codes, SQL injection, case sensitivity, spaces |
| `gift/test_gift_card_boundary.py` | 9 | XSS in message, SQL injection, Arabic names, invalid phone |
| `orders/test_orders_edge_cases.py` | 7 | Empty feedback, special-char search, cancel flow |
| `subscription/test_subscription_boundary.py` | 6 | Back-button resets, frequency options, cancel declined |
| `account/test_profile_edge_cases.py` | 7 | SQL in help search, logout cancel, empty search state |

---

## Local commands

```bash
cd testing

bash run_on_device.sh              # interactive USB device menu

bash run_maestro.sh                # smoke suite (5 flows)
bash run_maestro.sh regression     # full regression (all 23 flows)
bash run_maestro.sh negative       # negative/boundary flows only (7 flows)
bash run_maestro.sh flow 12        # single flow by number

bash run_appium.sh payment         # payment tests
bash run_appium.sh gift            # gift card tests
bash run_appium.sh subscription    # subscription tests
bash run_appium.sh account         # profile & account tests
bash run_appium.sh                 # all 92 Appium tests

# Run only negative tests (Appium)
cd appium && python -m pytest tests/ -m negative -v

# Run only boundary tests
cd appium && python -m pytest tests/ -m boundary -v
```
