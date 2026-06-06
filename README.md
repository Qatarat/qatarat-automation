# Qatarat (قطرات) — Automated Testing Suite

[![Maestro Smoke](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/01-maestro-smoke.yml)
[![Maestro Regression](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/02-maestro-regression.yml)
[![Appium Android](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/03-appium-android.yml)
[![Maestro iOS](https://github.com/Qatarat/qatarat-automation/actions/workflows/04-maestro-ios.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/04-maestro-ios.yml)
[![Appium iOS](https://github.com/Qatarat/qatarat-automation/actions/workflows/06-appium-ios.yml/badge.svg)](https://github.com/Qatarat/qatarat-automation/actions/workflows/06-appium-ios.yml)

📊 **[Live Test Report Dashboard](https://qatarat.github.io/qatarat-automation/)**

---

Qatarat (قطرات) means "Droplets" in Arabic. It is a mobile app for mosque donations, Zakat, Sadaqah, gift cards, and recurring charity. This repository contains the automated testing system — 241 checks across Android and iOS.

---

## Quick start — one command

**Requirements:** Python 3, Android Studio with a `Pixel_7_API_34` emulator created.

```bash
# macOS / Linux
./run.sh

# Windows
run.bat

# Any OS
python run.py
```

This single command starts the emulator, installs the app, and launches it. No manual steps needed.

---

## Run with tests

```bash
./run.sh smoke         # app + 8 critical Maestro flows       (~8 min)
./run.sh regression    # app + all 50 Maestro flows            (~45 min)
./run.sh appium        # app + all 191 Appium deep tests       (~75 min)
./run.sh all           # app + Maestro regression + Appium     (~2 hrs)
```

Windows: replace `./run.sh` with `run.bat`. Any OS: use `python run.py <mode>`.

The script auto-detects your Android SDK on all operating systems, skips the emulator if one is already running, and saves HTML + JUnit + Allure reports to `testing/appium/reports/`.

---

## First-time setup

### 1. Android Studio

1. Download and install [Android Studio](https://developer.android.com/studio)
2. Open SDK Manager → tick **Android 14 (API 34)** → Apply
3. Open Device Manager → Create Virtual Device → **Pixel 7** → **API 34** → name it `Pixel_7_API_34` → Finish

### 2. Maestro (for Maestro test modes)

```bash
curl -Ls "https://get.maestro.mobile.dev" | bash
```

### 3. Appium + Python (for Appium test mode)

```bash
npm install -g appium
appium driver install uiautomator2
appium driver install --source=npm appium-flutter-driver

cd testing/appium
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> The `run.py` script will auto-create the Python venv and install Appium on first run if they are missing.

---

## Test credentials

| Field | Value |
|-------|-------|
| Phone | `8801685220417` |
| OTP | `1234` |
| Environment | Stage only — no real money |

---

## What is tested

| Area | Checks |
|------|--------|
| Login / OTP | Phone entry, wrong codes, resend |
| Guest browsing | Browse without account, login prompt |
| Mosque listing | Search, filter, profile pages |
| Cart | Add, quantity, remove, empty cart |
| Checkout | Payment methods, promo codes, confirmation |
| Donations | Zakat calculator, Sadaqah, recurring |
| Gift cards | Send, recipient details, WhatsApp share |
| Wallet | Balance, top-up, transaction history |
| Profile | Edit, language, currency, logout |
| Security | SQL injection, XSS — app must not crash |
| Edge cases | Empty fields, long text, Arabic, offline |

Total: **50 Maestro flows + 191 Appium tests = 241 automated checks**

---

## Automated schedule (GitHub Actions)

| Suite | When | Duration |
|-------|------|----------|
| Smoke (Android) | Every push | ~8 min |
| Regression (Android) | Nightly 1 AM UTC | ~45 min |
| Appium Android | Every Monday | ~75 min |
| Maestro iOS | Every Tuesday 3 AM UTC | ~30 min |
| Appium iOS | Every Wednesday 4 AM UTC | ~90 min |

To trigger manually: go to the **Actions** tab → pick a workflow → **Run workflow**.

---

## Project structure

```
Qatarat/
├── run.py                        ← universal launcher (macOS, Linux, Windows)
├── run.sh                        ← macOS / Linux shortcut
├── run.bat                       ← Windows shortcut
├── Qatarat (Lambda-Stage).apk    ← Android app
├── .github/workflows/            ← CI pipelines
├── testing/
│   ├── maestro/flows/            ← 50 Maestro YAML flows
│   └── appium/                   ← 191 Appium Python tests
└── docs/                         ← live dashboard website
```

---

## Troubleshooting

**`adb: command not found`** — add to `~/.zshrc`:
```bash
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
```

**`maestro: command not found`** — close and reopen Terminal after installing.

**Emulator won't start** — enable Hardware Acceleration in Android Studio SDK Manager.

**iOS simulator won't boot** — run `xcrun simctl erase all` then try again.

---

Built and maintained by **Mejbaur Bahar Fagun** — Senior Software Engineer QA (IV)
[linkedin.com/in/mejbaur](https://www.linkedin.com/in/mejbaur/) · mejbaur@markopolo.ai
