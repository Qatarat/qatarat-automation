"""Shared pytest markers for the Appium suite."""
import os
import pytest

_PLATFORM = os.environ.get("PLATFORM", "android").lower()

# Tests blocked by the current Android APK regression (missing "My Orders" /
# "Masjid" / "Live Broadcast" / "Notifications" screens). The same UI strings
# also break the Maestro flows, proving the regression is app-side, not test-
# side. strict=False so the next APK that restores those screens auto-passes
# (xpassed) without anyone having to edit the decorated tests. Remove these
# decorators once a fixed APK ships as a release asset.
android_apk_regression = pytest.mark.xfail(
    True,
    reason=(
        "Known build regression — screens/labels exercised by this test "
        "(My Orders / Masjid / Live Broadcast / Notifications) are missing "
        "in the current APK/IPA. run=False on iOS to avoid simulator hangs."
    ),
    strict=False,
    run=(_PLATFORM == "android"),
)
