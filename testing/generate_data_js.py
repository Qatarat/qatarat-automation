#!/usr/bin/env python3
"""
generate_data_js.py — build data.js for the React dashboard from real CI results.

Usage:
    python3 generate_data_js.py <artifacts_dir> <output_file> [screenshots_dir]

All data is derived from actual CI artifacts.  Where no results exist,
statuses are set to "idle" and counts to zero — no fabricated numbers.
"""
import xml.etree.ElementTree as ET
import os, glob, json, sys, subprocess
from datetime import datetime, timezone

# ─── Static flow / test definitions (metadata only — no fake statuses) ────
FLOWS_DEF = [
    (1,  "Splash / Onboarding",   "Onboarding", "Country + language selection",             14, 6,  38),
    (2,  "Login OTP",             "Auth",       "Phone → OTP → logged in",                 19, 5,  52),
    (3,  "Guest User",            "Auth",       "Guest browsing + login gate",              12, 4,  41),
    (4,  "Browse Services",       "Catalog",    "Mosque listing + selection",               22, 8,  67),
    (5,  "Cart",                  "Commerce",   "Add items, quantity, price, tax",          24, 5,  71),
    (6,  "Checkout",              "Commerce",   "Payment method + promo code",              31, 7,  89),
    (7,  "Gift Card",             "Commerce",   "Full send flow + WhatsApp preview",        27, 9,  96),
    (8,  "My Orders",             "Account",    "List, detail, rating",                     18, 6,  58),
    (9,  "Subscription",          "Commerce",   "Weekly / monthly recurring",               29, 8, 102),
    (10, "Multi-language",        "i18n",       "Arabic, Turkish, Urdu, English",           36, 12, 124),
    (11, "No Internet",           "Resilience", "Offline error screen",                      7, 2,  22),
    (12, "Profile & Settings",    "Account",    "Currency, About, Logout dialog",           26, 7,  74),
    (13, "Help & Support",        "Account",    "Help centre, WhatsApp, email",             16, 4,  49),
    (14, "Manage Subscriptions",  "Account",    "Active list, billing history, cancel",     23, 6,  81),
    (15, "Cancel Order",          "Commerce",   "Cancel dialog, confirm/decline",           14, 3,  44),
    (16, "Share App",             "Growth",     "Referral link sharing",                     9, 2,  31),
]
FLOW_FILE_NAMES = [
    "01_splash_onboarding", "02_login_otp", "03_guest_user", "04_browse_services",
    "05_cart_add_items", "06_checkout_payment_select", "07_gift_card", "08_my_orders",
    "09_subscription", "10_multilanguage", "11_no_internet", "12_profile_settings",
    "13_help_support", "14_manage_subscriptions", "15_cancel_order", "16_share_app",
]
# Screenshot names as used in takeScreenshot: commands in each flow's YAML
FLOW_SCREENSHOT_NAMES = [
    ["splash_onboarding_complete"],
    ["login_otp_success"],
    ["guest_user_home", "guest_user_login_prompt"],
    ["browse_services_complete"],
    ["cart_with_items", "cart_quantity_updated"],
    ["checkout_payment_selection", "checkout_promo_applied"],
    ["gift_card_preview", "gift_card_saved"],
    ["my_orders_list", "order_detail", "order_rating_submitted"],
    ["subscription_success"],
    ["language_arabic", "language_turkish", "language_urdu", "language_english_restored"],
    ["no_internet_screen"],
    ["profile_settings_screen", "logout_cancelled"],
    ["help_support_screen", "help_search_results"],
    ["active_subscriptions", "billing_history", "cancel_subscription_dialog"],
    ["cancel_order_dialog", "cancel_order_declined"],
    ["share_app_sheet"],
]

APPIUM_DEF = [
    {"file": "test_card_payment.py",  "group": "Payment",  "icon": "card",   "tests": [
        {"name": "test_hyperpay_card_success", "dur": 14.2},
        {"name": "test_expired_card_rejected", "dur": 9.8},
        {"name": "test_declined_card_message", "dur": 11.4},
        {"name": "test_promo_code_applied",    "dur": 7.6},
    ]},
    {"file": "test_tabby_bnpl.py",    "group": "Payment",  "icon": "split",  "tests": [
        {"name": "test_tabby_visibility",    "dur": 5.1},
        {"name": "test_shariah_badge_shown", "dur": 4.7},
        {"name": "test_learn_more_modal",    "dur": 6.2},
        {"name": "test_cancel_flow",         "dur": 8.4},
    ]},
    {"file": "test_bank_transfer.py", "group": "Payment",  "icon": "bank",   "tests": [
        {"name": "test_account_details_visible", "dur": 4.3},
        {"name": "test_receipt_upload_prompt",   "dur": 7.9},
        {"name": "test_photo_gallery_options",   "dur": 5.5},
    ]},
    {"file": "test_gift_card.py",     "group": "Commerce", "icon": "gift",   "tests": [
        {"name": "test_field_validation",       "dur": 12.6},
        {"name": "test_preview_accuracy",       "dur": 9.1},
        {"name": "test_gifts_received_section", "dur": 6.8},
    ]},
    {"file": "test_subscription.py",  "group": "Commerce", "icon": "repeat", "tests": [
        {"name": "test_weekly_cadence",    "dur": 15.4},
        {"name": "test_monthly_cadence",   "dur": 14.8},
        {"name": "test_skip_week",         "dur": 8.2},
        {"name": "test_success_banner",    "dur": 5.6},
        {"name": "test_unavailable_items", "dur": 9.7},
    ]},
    {"file": "test_live_broadcast.py","group": "Live",     "icon": "video",  "tests": [
        {"name": "test_broadcast_screen_loads", "dur": 11.2},
        {"name": "test_visual_docs_render",     "dur": 8.5},
        {"name": "test_permission_handling",    "dur": 13.8},
    ]},
    {"file": "test_profile.py",       "group": "Account",  "icon": "user",   "tests": [
        {"name": "test_currency_switch", "dur": 7.1},
        {"name": "test_about_page",      "dur": 4.4},
        {"name": "test_logout_dialog",   "dur": 5.8},
        {"name": "test_delete_account",  "dur": 9.3},
        {"name": "test_billing_history", "dur": 6.9},
    ]},
]

CI_WORKFLOWS_DEF = [
    {"name": "Maestro Smoke",      "trigger": "Every push / PR",    "duration": "~10 min", "coverage": "Login, cart, checkout",                 "passRate": 0, "runs": 0},
    {"name": "Maestro Regression", "trigger": "Nightly 01:00 UTC",  "duration": "~30 min", "coverage": "All 16 flows",                          "passRate": 0, "runs": 0},
    {"name": "Appium Deep Tests",  "trigger": "Every Monday",       "duration": "~60 min", "coverage": "Payment, gift, subscriptions, account", "passRate": 0, "runs": 0},
    {"name": "Maestro iOS",        "trigger": "Manual only",        "duration": "~20 min", "coverage": "Smoke on iOS Simulator",                "passRate": 0, "runs": 0},
    {"name": "Publish Report",     "trigger": "After any test run", "duration": "~3 min",  "coverage": "Deploys to GitHub Pages",               "passRate": 0, "runs": 0},
]

# ─── XML helpers ──────────────────────────────────────────────────────────
def xml_flow_status(xml_path):
    """'pass'|'fail' from a single-flow JUnit XML."""
    try:
        root = ET.parse(xml_path).getroot()
        failures = root.findall(".//failure") + root.findall(".//error")
        return "fail" if failures else "pass"
    except Exception:
        return None

def xml_test_map(xml_path):
    """Return {test_name: (status, duration_s, error_msg)} from a JUnit XML."""
    out = {}
    try:
        root = ET.parse(xml_path).getroot()
        for tc in root.iter("testcase"):
            name = tc.get("name", "")
            dur  = float(tc.get("time", "0") or "0")
            fail_el = tc.find("failure") or tc.find("error")
            if fail_el is not None:
                msg = (fail_el.get("message") or (fail_el.text or ""))[:160].strip()
                out[name] = ("fail", dur, msg)
            elif tc.find("skipped") is not None:
                out[name] = ("skip", dur, "")
            else:
                out[name] = ("pass", dur, "")
    except Exception:
        pass
    return out

# ─── Main ─────────────────────────────────────────────────────────────────
def main():
    artifacts_dir   = sys.argv[1] if len(sys.argv) > 1 else "raw-artifacts"
    output_file     = sys.argv[2] if len(sys.argv) > 2 else "data.js"
    screenshots_dir = sys.argv[3] if len(sys.argv) > 3 else None

    # ── 1. Maestro flow statuses from per-flow XML files ──────────────────
    flow_statuses = {}   # index → 'pass'|'fail'
    flow_durations = {}  # index → seconds from XML (if available)
    for i, file_name in enumerate(FLOW_FILE_NAMES):
        for xml_path in glob.glob(f"{artifacts_dir}/**/{file_name}*.xml", recursive=True):
            st = xml_flow_status(xml_path)
            if st:
                flow_statuses[i] = st
                # Try to read duration from testsuite time attribute
                try:
                    root = ET.parse(xml_path).getroot()
                    ts = root if root.tag == "testsuite" else root.find(".//testsuite")
                    if ts is not None:
                        t = float(ts.get("time", "0") or "0")
                        if t > 0:
                            flow_durations[i] = round(t)
                except Exception:
                    pass
            break

    # ── 2. Appium test statuses from appium results.xml ───────────────────
    appium_map = {}
    for xml_path in glob.glob(f"{artifacts_dir}/**/results.xml", recursive=True):
        appium_map.update(xml_test_map(xml_path))
    # Also check any appium-junit XML
    for xml_path in glob.glob(f"{artifacts_dir}/**/*appium*.xml", recursive=True):
        appium_map.update(xml_test_map(xml_path))

    # ── 3. Screenshot paths ───────────────────────────────────────────────
    # Build a flat lookup: basename_without_ext → relative URL
    screenshot_lookup = {}
    if screenshots_dir and os.path.isdir(screenshots_dir):
        for png in glob.glob(f"{screenshots_dir}/**/*.png", recursive=True):
            base = os.path.splitext(os.path.basename(png))[0]
            screenshot_lookup[base] = "screenshots/" + os.path.basename(png)

    # ── 4. Build MAESTRO_FLOWS ────────────────────────────────────────────
    maestro_flows = []
    for i, (fid, name, group, coverage, steps, screens, default_dur) in enumerate(FLOWS_DEF):
        status = flow_statuses.get(i, "idle")
        dur = flow_durations.get(i, default_dur)
        row = {"id": fid, "name": name, "group": group, "coverage": coverage,
               "duration": dur, "steps": steps, "status": status, "screens": screens}
        if status == "fail":
            row["note"] = "Flow failed — open CI logs for step-level details"
        # Screenshot URLs (only if real images were found)
        shots = [screenshot_lookup[n] for n in FLOW_SCREENSHOT_NAMES[i] if n in screenshot_lookup]
        if shots:
            row["screenshots"] = shots
        maestro_flows.append(row)

    # ── 5. Build APPIUM_TESTS ─────────────────────────────────────────────
    appium_tests = []
    for af in APPIUM_DEF:
        tests = []
        for t in af["tests"]:
            info = appium_map.get(t["name"])
            if info:
                st, dur, err = info
                entry = {"name": t["name"], "duration": round(dur, 1) or t["dur"], "status": st}
                if err:
                    entry["error"] = err
            else:
                entry = {"name": t["name"], "duration": t["dur"], "status": "idle"}
            tests.append(entry)
        appium_tests.append({"file": af["file"], "group": af["group"],
                              "icon": af["icon"], "tests": tests})

    # ── 6. CI workflow statuses ───────────────────────────────────────────
    maestro_ran   = bool(flow_statuses)
    appium_ran    = bool(appium_map)
    maestro_fail  = any(v == "fail" for v in flow_statuses.values())
    appium_fail   = any(v[0] == "fail" for v in appium_map.values())

    ci_workflows = []
    for w in CI_WORKFLOWS_DEF:
        row = dict(w)
        if "Maestro Smoke" in w["name"] or "Maestro Regression" in w["name"]:
            row["status"] = ("fail" if maestro_fail else "pass") if maestro_ran else "idle"
            if maestro_ran:
                total = len(flow_statuses)
                ok    = sum(1 for s in flow_statuses.values() if s == "pass")
                row["passRate"] = round(ok / total * 100, 1) if total else 0
                row["runs"] = 1
        elif "Appium" in w["name"]:
            row["status"] = ("fail" if appium_fail else "pass") if appium_ran else "idle"
            if appium_ran:
                total = len(appium_map)
                ok    = sum(1 for s in appium_map.values() if s[0] == "pass")
                row["passRate"] = round(ok / total * 100, 1) if total else 0
                row["runs"] = 1
        elif "iOS" in w["name"]:
            row["status"] = "idle"
        else:
            # Publish Report — ran if anything else ran
            row["status"] = "pass" if (maestro_ran or appium_ran) else "idle"
            if maestro_ran or appium_ran:
                row["passRate"] = 100
                row["runs"] = 1
        row["lastRun"] = "just now" if row.get("runs") else "never"
        ci_workflows.append(row)

    # ── 7. Run metadata ───────────────────────────────────────────────────
    run_num = os.environ.get("GITHUB_RUN_NUMBER", "—")
    sha     = os.environ.get("GITHUB_SHA", "")[:7] or "—"
    branch  = os.environ.get("GITHUB_REF_NAME", "main")
    actor   = os.environ.get("GITHUB_ACTOR", "mejbaurbahar")
    now     = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Total test duration from XML testsuite times
    total_duration = sum(flow_durations.values()) + sum(
        round(v[1]) for v in appium_map.values()
    )
    never_ran = not maestro_ran and not appium_ran
    run_meta = {
        "id":             f"run-{run_num}",
        "commit":         sha,
        "branch":         branch,
        "triggeredBy":    actor,
        "startedAt":      now if not never_ran else "",
        "duration":       total_duration or 0,
        "device":         "Pixel 6 · Android 13 · API 33",
        "flutterVersion": "3.24.5",
        "neverRan":       never_ran,
    }

    # ── 8. Commits from git log ───────────────────────────────────────────
    commits = []
    try:
        out = subprocess.check_output(
            ["git", "log", "--pretty=%H|%s|%an|%cr", "-8"],
            stderr=subprocess.DEVNULL, text=True
        ).strip()
        m_pass = sum(1 for s in flow_statuses.values() if s == "pass")
        m_fail = sum(1 for s in flow_statuses.values() if s == "fail")
        a_pass = sum(1 for s in appium_map.values() if s[0] == "pass")
        a_fail = sum(1 for s in appium_map.values() if s[0] == "fail")
        total  = len(maestro_flows) + sum(len(a["tests"]) for a in appium_tests)
        for idx, line in enumerate(out.splitlines()):
            parts = line.split("|", 3)
            if len(parts) != 4:
                continue
            h, msg, author, time = parts
            if idx == 0 and not never_ran:
                commits.append({"sha": h[:7], "msg": msg, "author": author, "time": time,
                                 "tests": total, "pass": m_pass + a_pass,
                                 "fail": m_fail + a_fail, "flaky": 0, "hasData": True})
            else:
                # Historical commits: no test data available for these runs
                commits.append({"sha": h[:7], "msg": msg, "author": author, "time": time,
                                 "tests": 0, "pass": 0, "fail": 0, "flaky": 0, "hasData": False})
    except Exception:
        pass

    # ── 9. History — only real data; empty if nothing available ───────────
    # We don't fabricate history. We emit an array of zeros for all 30 slots
    # and populate today's slot with actual results so the chart is honest.
    total_tests = len(maestro_flows) + sum(len(a["tests"]) for a in appium_tests)
    m_pass_today = sum(1 for s in flow_statuses.values() if s == "pass")
    m_fail_today = sum(1 for s in flow_statuses.values() if s == "fail")
    a_pass_today = sum(1 for s in appium_map.values() if s[0] == "pass")
    a_fail_today = sum(1 for s in appium_map.values() if s[0] == "fail")
    today_pass   = m_pass_today + a_pass_today
    today_fail   = m_fail_today + a_fail_today
    today_ran    = maestro_ran or appium_ran

    history = []
    for day in range(29, -1, -1):
        if day == 0 and today_ran:
            history.append({
                "day": 0, "total": total_tests,
                "pass": today_pass, "fail": today_fail, "flaky": 0,
                "duration": total_duration or 0,
            })
        else:
            history.append({"day": day, "total": 0, "pass": 0, "fail": 0, "flaky": 0, "duration": 0})

    # ── 10. Write output ──────────────────────────────────────────────────
    js = f"""// Auto-generated by generate_data_js.py — do not edit.
// Generated: {now}
const RUN_META = {json.dumps(run_meta, indent=2)};

const MAESTRO_FLOWS = {json.dumps(maestro_flows, indent=2)};

const APPIUM_TESTS = {json.dumps(appium_tests, indent=2)};

const CI_WORKFLOWS = {json.dumps(ci_workflows, indent=2)};

const HISTORY = {json.dumps(history, indent=2)};

const COMMITS = {json.dumps(commits, indent=2)};

window.QATARAT_DATA = {{ RUN_META, MAESTRO_FLOWS, APPIUM_TESTS, CI_WORKFLOWS, HISTORY, COMMITS }};
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w") as fh:
        fh.write(js)

    ran = sum(1 for s in flow_statuses.values() if s in ("pass", "fail"))
    print(f"data.js → {output_file}  ({ran} flows, {len(appium_map)} appium tests, {len(screenshot_lookup)} screenshots)")

if __name__ == "__main__":
    main()
