#!/usr/bin/env python3
"""Validate resolved Xcode settings for an authorized production app target.

The caller must generate the JSON with xcodebuild -showBuildSettings -json for
its real project/workspace and scheme. This validator never edits the host.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

APP_PRODUCT_TYPE = "com.apple.product-type.application"


def fail(message: str) -> None:
    raise SystemExit(f"INVALID HOST: {message}")


def version(value: str, label: str) -> tuple[int, ...]:
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value):
        fail(f"{label} is not a resolved numeric version: {value!r}")
    return tuple(int(part) for part in value.split("."))


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"resolved build-settings JSON is missing or empty: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"resolved build-settings JSON is invalid: {error}")
    if not isinstance(value, list):
        fail("resolved build-settings JSON root must be an array")
    records = [item for item in value if isinstance(item, dict)]
    if len(records) != len(value):
        fail("resolved build-settings JSON contains a non-object record")
    return records


def validate(
    records: list[dict[str, Any]],
    target: str,
    minimum_ios: str,
    expected_bundle_id: str | None,
    expected_team_id: str | None,
) -> dict[str, str]:
    matches: list[dict[str, str]] = []
    for record in records:
        settings = record.get("buildSettings")
        if not isinstance(settings, dict):
            continue
        normalized = {str(key): str(value) for key, value in settings.items()}
        record_target = str(record.get("target", ""))
        if record_target == target or normalized.get("TARGET_NAME") == target:
            matches.append(normalized)

    if not matches:
        available = sorted(
            {
                str(record.get("target") or record.get("buildSettings", {}).get("TARGET_NAME"))
                for record in records
                if isinstance(record.get("buildSettings"), dict)
            }
            - {"", "None"}
        )
        suffix = f"; available targets: {', '.join(available)}" if available else ""
        fail(f"app target {target!r} cannot be identified in resolved Xcode settings{suffix}")

    app_matches = [item for item in matches if item.get("PRODUCT_TYPE") == APP_PRODUCT_TYPE]
    if not app_matches:
        found = sorted({item.get("PRODUCT_TYPE", "<missing>") for item in matches})
        fail(f"target {target!r} is not an iOS application target (PRODUCT_TYPE: {', '.join(found)})")

    signatures = {
        (
            item.get("IPHONEOS_DEPLOYMENT_TARGET", ""),
            item.get("PRODUCT_BUNDLE_IDENTIFIER", ""),
            item.get("SUPPORTED_PLATFORMS", ""),
            item.get("DEVELOPMENT_TEAM", ""),
            item.get("CODE_SIGN_STYLE", ""),
        )
        for item in app_matches
    }
    if len(signatures) != 1:
        fail(f"target {target!r} resolves to conflicting production build settings")

    settings = app_matches[0]
    deployment = settings.get("IPHONEOS_DEPLOYMENT_TARGET", "")
    if not deployment:
        fail(f"target {target!r} has no resolved IPHONEOS_DEPLOYMENT_TARGET")
    if version(deployment, "IPHONEOS_DEPLOYMENT_TARGET") < version(minimum_ios, "minimum iOS version"):
        fail(
            f"target {target!r} deployment target {deployment} is incompatible; "
            f"ExistingIPAOverlay requires iOS {minimum_ios} or newer"
        )

    platforms = settings.get("SUPPORTED_PLATFORMS", "").split()
    if "iphoneos" not in platforms:
        fail(f"target {target!r} does not support the iphoneos platform")

    bundle_id = settings.get("PRODUCT_BUNDLE_IDENTIFIER", "")
    if not bundle_id:
        fail(f"target {target!r} has no resolved PRODUCT_BUNDLE_IDENTIFIER")
    if expected_bundle_id and bundle_id != expected_bundle_id:
        fail(
            f"target {target!r} bundle identifier {bundle_id!r} does not match "
            f"the authorized production identifier {expected_bundle_id!r}"
        )

    if settings.get("CODE_SIGNING_ALLOWED", "YES") == "NO":
        fail(f"target {target!r} disables code signing for the production configuration")
    signing_style = settings.get("CODE_SIGN_STYLE", "")
    if signing_style not in {"Automatic", "Manual"}:
        fail(f"target {target!r} has no resolved Automatic or Manual CODE_SIGN_STYLE")
    team_id = settings.get("DEVELOPMENT_TEAM", "")
    if not team_id:
        fail(f"target {target!r} has no resolved DEVELOPMENT_TEAM signing configuration")
    if expected_team_id and team_id != expected_team_id:
        fail(
            f"target {target!r} development team {team_id!r} does not match "
            f"the authorized team {expected_team_id!r}"
        )

    return {
        "target": target,
        "bundleIdentifier": bundle_id,
        "deploymentTarget": deployment,
        "developmentTeam": team_id,
        "codeSignStyle": signing_style,
        "productType": APP_PRODUCT_TYPE,
        "supportedPlatforms": settings["SUPPORTED_PLATFORMS"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-settings", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--minimum-ios", default="16.0")
    parser.add_argument("--bundle-id")
    parser.add_argument("--team-id")
    args = parser.parse_args()

    result = validate(
        load_records(args.build_settings.resolve()),
        args.target,
        args.minimum_ios,
        args.bundle_id,
        args.team_id,
    )
    print("VALID HOST")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
