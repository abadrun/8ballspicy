#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate-authorized-host-settings.py")
SPEC = importlib.util.spec_from_file_location("host_settings", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def record(**overrides: str):
    settings = {
        "TARGET_NAME": "AuthorizedHost",
        "PRODUCT_TYPE": "com.apple.product-type.application",
        "IPHONEOS_DEPLOYMENT_TARGET": "16.0",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.authorized",
        "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator",
        "CODE_SIGNING_ALLOWED": "YES",
        "CODE_SIGN_STYLE": "Automatic",
        "DEVELOPMENT_TEAM": "ABCDE12345",
    }
    settings.update(overrides)
    return {"target": settings["TARGET_NAME"], "buildSettings": settings}


class AuthorizedHostSettingsTests(unittest.TestCase):
    def test_accepts_resolved_ios16_application_target(self):
        result = MODULE.validate(
            [record()],
            "AuthorizedHost",
            "16.0",
            "com.example.authorized",
            "ABCDE12345",
        )
        self.assertEqual(result["deploymentTarget"], "16.0")
        self.assertEqual(result["bundleIdentifier"], "com.example.authorized")

    def test_rejects_missing_target_with_available_target_diagnostic(self):
        with self.assertRaisesRegex(SystemExit, "cannot be identified.*OtherTarget"):
            MODULE.validate(
                [record(TARGET_NAME="OtherTarget")],
                "AuthorizedHost",
                "16.0",
                None,
                None,
            )

    def test_rejects_non_application_target(self):
        with self.assertRaisesRegex(SystemExit, "not an iOS application target"):
            MODULE.validate(
                [record(PRODUCT_TYPE="com.apple.product-type.framework")],
                "AuthorizedHost",
                "16.0",
                None,
                None,
            )

    def test_rejects_incompatible_deployment_target(self):
        with self.assertRaisesRegex(SystemExit, "deployment target 15.4 is incompatible"):
            MODULE.validate(
                [record(IPHONEOS_DEPLOYMENT_TARGET="15.4")],
                "AuthorizedHost",
                "16.0",
                None,
                None,
            )

    def test_rejects_unresolved_deployment_variable(self):
        with self.assertRaisesRegex(SystemExit, "not a resolved numeric version"):
            MODULE.validate(
                [record(IPHONEOS_DEPLOYMENT_TARGET="$(MINIMUM_IOS)")],
                "AuthorizedHost",
                "16.0",
                None,
                None,
            )

    def test_rejects_bundle_identifier_mismatch(self):
        with self.assertRaisesRegex(SystemExit, "does not match"):
            MODULE.validate(
                [record()], "AuthorizedHost", "16.0", "com.example.wrong", None
            )

    def test_rejects_disabled_production_signing(self):
        with self.assertRaisesRegex(SystemExit, "disables code signing"):
            MODULE.validate(
                [record(CODE_SIGNING_ALLOWED="NO")],
                "AuthorizedHost",
                "16.0",
                None,
                None,
            )

    def test_rejects_missing_team_configuration(self):
        with self.assertRaisesRegex(SystemExit, "no resolved DEVELOPMENT_TEAM"):
            MODULE.validate(
                [record(DEVELOPMENT_TEAM="")],
                "AuthorizedHost",
                "16.0",
                None,
                "ABCDE12345",
            )

    def test_rejects_wrong_authorized_team(self):
        with self.assertRaisesRegex(SystemExit, "does not match the authorized team"):
            MODULE.validate(
                [record(DEVELOPMENT_TEAM="ZZZZZ99999")],
                "AuthorizedHost",
                "16.0",
                None,
                "ABCDE12345",
            )


if __name__ == "__main__":
    unittest.main()
