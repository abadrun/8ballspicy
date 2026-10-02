#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("integrate-authorized-host-macos.sh")


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def required(container: str) -> list[str]:
    return [
        "--container", container,
        "--scheme", "AuthorizedHost",
        "--target", "AuthorizedHost",
        "--integration-source", "/missing/OverlayIntegration.swift",
        "--test-destination", "platform=iOS Simulator,name=iPhone 16",
        "--bundle-id", "com.example.authorized",
        "--team-id", "ABCDE12345",
        "--export-options", "/missing/ExportOptions.plist",
    ]


class ProductionHandoffGuardTests(unittest.TestCase):
    def test_missing_host_has_specific_error(self):
        result = run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Production host not supplied. Provide the authorized .xcodeproj/.xcworkspace and legitimate signing/export configuration.",
            result.stderr,
        )

    def test_ipa_is_never_accepted_as_host(self):
        result = run(*required("anything.ipa"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("IPA cannot be used as a host", result.stderr)

    def test_missing_project_path_has_specific_error(self):
        result = run(*required("/missing/AuthorizedHost.xcodeproj"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authorized host container does not exist", result.stderr)

    def test_workspace_requires_explicit_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "AuthorizedHost.xcworkspace"
            workspace.mkdir()
            result = run(*required(str(workspace)))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--project is required to identify the app target", result.stderr)

    def test_script_has_no_baseline_copy_or_fabricated_signing_command(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn('cp "$baseline"', text)
        self.assertNotIn("security create-keychain", text)
        self.assertNotIn("codesign --sign -", text)
        self.assertIn("exported IPA is byte-identical to Artifact A", text)
        self.assertIn("ExistingIPAWorkspace/SampleHost is never a production host", text)
        self.assertIn("final output path resolves to Artifact A; baseline overwrite is forbidden", text)
        self.assertIn('--baseline-ipa "$baseline"', text)
        self.assertIn("final-validation-report.json", text)
        self.assertIn("FINAL IPA PRODUCED AND VALIDATED", text)


if __name__ == "__main__":
    unittest.main()
