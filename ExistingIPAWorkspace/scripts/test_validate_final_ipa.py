#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import plistlib
import struct
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate-final-ipa.py")
BUNDLE = "ExistingIPAOverlay_ExistingIPAOverlayUI.bundle"


def plist(value: dict) -> bytes:
    return plistlib.dumps(value, fmt=plistlib.FMT_BINARY, sort_keys=True)


def make_ipa(path: Path, minimum_ios: str = "16.0", include_assets: bool = True) -> None:
    # Minimal 64-bit little-endian arm64 Mach-O header with no load commands.
    executable = b"\xcf\xfa\xed\xfe" + struct.pack("<IIIIIII", 0x0100000C, 0, 2, 0, 0, 0, 0)
    info = {
        "CFBundleIdentifier": "com.example.authorized",
        "CFBundleExecutable": "AuthorizedHost",
        "CFBundlePackageType": "APPL",
        "MinimumOSVersion": minimum_ios,
    }
    resource_info = {
        "CFBundleIdentifier": "overlaysource.ExistingIPAOverlayUI.resources",
        "CFBundlePackageType": "BNDL",
        "MinimumOSVersion": "16.0",
    }
    with zipfile.ZipFile(path, "w") as archive:
        root = "Payload/AuthorizedHost.app"
        archive.writestr(f"{root}/Info.plist", plist(info))
        archive.writestr(f"{root}/AuthorizedHost", executable)
        archive.writestr(f"{root}/{BUNDLE}/Info.plist", plist(resource_info))
        archive.writestr(f"{root}/{BUNDLE}/en.lproj/Localizable.strings", b'"key" = "value";')
        archive.writestr(f"{root}/{BUNDLE}/id.lproj/Localizable.strings", b'"key" = "nilai";')
        if include_assets:
            archive.writestr(f"{root}/{BUNDLE}/Assets.car", b"compiled-assets")


def validate(path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT),
            str(path),
            "--require-arm64",
            "--require-component",
            "ExistingIPAOverlayUI",
            "--require-resource-bundle",
            BUNDLE,
            "--require-bundle-resource",
            "Assets.car",
            "--require-bundle-resource",
            "en.lproj/Localizable.strings",
            "--require-bundle-resource",
            "id.lproj/Localizable.strings",
            "--minimum-ios",
            "16.0",
            "--bundle-id",
            "com.example.authorized",
            *extra,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class FinalIPAValidatorTests(unittest.TestCase):
    def test_accepts_expected_unsigned_structure_when_signing_is_not_requested(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "final.ipa"
            make_ipa(path)
            result = validate(path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("VALID", result.stdout)
            self.assertIn("minimumIOS=16.0", result.stdout)
            self.assertIn("component-specific SwiftPM resource bundle", result.stdout)

    def test_rejects_missing_required_resource(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "final.ipa"
            make_ipa(path, include_assets=False)
            result = validate(path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("required resource bundle file is missing: Assets.car", result.stderr)

    def test_rejects_incompatible_deployment_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "final.ipa"
            make_ipa(path, minimum_ios="15.0")
            result = validate(path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("deployment target 15.0 is incompatible", result.stderr)

    def test_rejects_explicitly_forbidden_baseline_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "final.ipa"
            make_ipa(path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result = validate(path, "--reject-sha256", digest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SHA-256 is explicitly rejected", result.stderr)

    def test_rejects_unsafe_archive_member_before_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "final.ipa"
            make_ipa(path)
            with zipfile.ZipFile(path, "a") as archive:
                archive.writestr("../escape", b"unsafe")
            result = validate(path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe ZIP member path", result.stderr)


if __name__ == "__main__":
    unittest.main()
