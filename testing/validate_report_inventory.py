#!/usr/bin/env python3
"""Validate dashboard inventory against real test sources.

This protects the GitHub Pages report from silently drifting away from pytest
and Maestro source files. It does not run devices or Appium.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_TESTS = ROOT / "testing" / "appium" / "tests"
FLOWS = ROOT / "testing" / "maestro" / "flows"
DOCS_INDEX = ROOT / "docs" / "index.html"
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "05-publish-report.yml"
COVERAGE_CONTRACT = ROOT / "testing" / "mobile_coverage_contract.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def collect_pytest_names() -> set[str]:
    names: set[str] = set()
    for path in APP_TESTS.rglob("test_*.py"):
        names.update(re.findall(r"def\s+(test_[A-Za-z0-9_]+)\s*\(", path.read_text()))
    return names


def collect_dashboard_names() -> set[str]:
    html = DOCS_INDEX.read_text()
    return set(re.findall(r"\{name:'(test_[^']+)'", html))


def validate_coverage_contract() -> None:
    if not COVERAGE_CONTRACT.exists():
        fail("testing/mobile_coverage_contract.json missing")

    contract = json.loads(COVERAGE_CONTRACT.read_text())
    for section in ("domains", "test_types"):
        entries = contract.get(section, {})
        if not entries:
            fail(f"coverage contract section {section!r} is empty")
        for name, value in entries.items():
            paths: list[str] = []
            if isinstance(value, dict):
                for platform, platform_paths in value.items():
                    if platform not in {"appium", "maestro"}:
                        fail(f"{section}.{name} has unknown platform {platform!r}")
                    paths.extend(platform_paths)
            else:
                paths.extend(value)
            if not paths:
                fail(f"{section}.{name} has no source paths")
            for rel in paths:
                path = ROOT / rel
                if not path.exists():
                    fail(f"{section}.{name} references missing path: {rel}")

    test_data = (ROOT / "testing" / "appium" / "test_data.py").read_text()
    for class_name in contract.get("test_data_classes", []):
        if not re.search(rf"^class\s+{re.escape(class_name)}\b", test_data, re.M):
            fail(f"test data class missing: {class_name}")

    for rel in contract.get("required_workflows", []):
        if not (ROOT / rel).exists():
            fail(f"required workflow missing: {rel}")


def main() -> None:
    pytest_names = collect_pytest_names()
    dashboard_names = collect_dashboard_names()
    flow_files = sorted(FLOWS.glob("[0-9][0-9]_*.yaml"))

    if len(flow_files) != 50:
        fail(f"expected 50 Maestro flow YAML files, found {len(flow_files)}")

    missing = sorted(pytest_names - dashboard_names)
    extra = sorted(dashboard_names - pytest_names)
    if missing or extra:
        if missing:
            print("Missing from docs/index.html:", file=sys.stderr)
            for name in missing[:100]:
                print(f"  {name}", file=sys.stderr)
        if extra:
            print("Not found in pytest sources:", file=sys.stderr)
            for name in extra[:100]:
                print(f"  {name}", file=sys.stderr)
        fail("dashboard Appium inventory does not match pytest tests")

    expected_total = len(pytest_names)
    expected_all_checks = expected_total + len(flow_files)
    html = DOCS_INDEX.read_text()
    if f"{expected_total} Appium" not in html or f"{expected_total} Python/pytest" not in html:
        fail(f"docs/index.html visible counts do not mention {expected_total} Appium tests")
    if f"{expected_all_checks} automated" not in html or f">{expected_all_checks}<" not in html:
        fail(f"docs/index.html visible counts do not mention {expected_all_checks} total checks")

    publish = PUBLISH_WORKFLOW.read_text()
    for workflow_name in [
        "Maestro — Smoke (Android)",
        "Maestro — Full Regression (Android)",
        "Appium — Deep Tests (Android)",
        "Maestro — Smoke & Regression (iOS Simulator)",
        "Appium — Deep Tests (iOS Simulator)",
    ]:
        if workflow_name not in publish:
            fail(f"publish workflow is not subscribed to {workflow_name!r}")
    if 'Latest completed Appium iOS run ID' not in publish:
        fail("publish workflow must keep the last completed iOS Appium result set")

    validate_coverage_contract()

    print(
        f"OK: {len(flow_files)} Maestro flows, {expected_total} Appium tests, "
        "publish workflow subscriptions valid, coverage contract valid"
    )


if __name__ == "__main__":
    main()
