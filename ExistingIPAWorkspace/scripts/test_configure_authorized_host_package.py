#!/usr/bin/env python3
"""Unit tests for project-file wiring; fixtures are parser data, not a host app."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("configure-authorized-host-package.py")
SPEC = importlib.util.spec_from_file_location("configure_authorized_host_package", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

PROJECT_ID = "111111111111111111111111"
TARGET_ID = "222222222222222222222222"
FRAMEWORKS_ID = "333333333333333333333333"
SOURCES_ID = "444444444444444444444444"

FIXTURE = f"""// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{
\t}};
\tobjectVersion = 60;
\tobjects = {{

/* Begin PBXFrameworksBuildPhase section */
\t\t{FRAMEWORKS_ID} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{SOURCES_ID} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */

/* Begin PBXNativeTarget section */
\t\t{TARGET_ID} /* AuthorizedHost */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = AAAAAAAAAAAAAAAAAAAAAAAA /* Build configuration list */;
\t\t\tbuildPhases = (
\t\t\t\t{SOURCES_ID} /* Sources */,
\t\t\t\t{FRAMEWORKS_ID} /* Frameworks */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = AuthorizedHost;
\t\t\tproductName = AuthorizedHost;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
\t\t{PROJECT_ID} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t}};
\t\t\ttargets = (
\t\t\t\t{TARGET_ID} /* AuthorizedHost */,
\t\t\t);
\t\t}};
/* End PBXProject section */
\t}};
\trootObject = {PROJECT_ID} /* Project object */;
}}
"""


class ConfigureAuthorizedHostPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pbxproj-parser-test-")
        self.root = Path(self.temporary.name)
        self.project = self.root / "AuthorizedHost.xcodeproj"
        self.project.mkdir()
        self.pbxproj = self.project / "project.pbxproj"
        self.pbxproj.write_text(FIXTURE, encoding="utf-8")
        self.package = Path(__file__).resolve().parents[1] / "OverlaySource"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_dry_run_does_not_write(self) -> None:
        before = self.pbxproj.read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            MODULE.configure(self.project, "AuthorizedHost", self.package, apply=False)
        self.assertEqual(before, self.pbxproj.read_bytes())
        self.assertIn("DRY RUN", output.getvalue())

    def test_apply_links_product_in_target_frameworks_phase_and_is_idempotent(self) -> None:
        MODULE.configure(self.project, "AuthorizedHost", self.package, apply=True)
        text = self.pbxproj.read_text(encoding="utf-8")

        _, _, target = MODULE.find_object(text, "PBXNativeTarget", "AuthorizedHost")
        dependency_id = MODULE.target_product_dependency(text, target, "ExistingIPAOverlay")
        self.assertIsNotNone(dependency_id)
        build_file_id = MODULE.product_build_file(text, dependency_id)
        self.assertIsNotNone(build_file_id)
        _, _, _, frameworks = MODULE.target_frameworks_phase(text, target)
        self.assertIn(build_file_id, MODULE.array_object_ids(frameworks, "files"))
        self.assertIn("isa = XCLocalSwiftPackageReference;", text)
        self.assertIn("productName = ExistingIPAOverlay;", text)
        self.assertIn("ExistingIPAOverlay in Frameworks", text)
        objects_end = text.rfind("\n\t};", 0, text.index("\trootObject ="))
        self.assertLess(text.index("/* Begin XCLocalSwiftPackageReference section */"), objects_end)
        self.assertLess(text.index("/* Begin XCSwiftPackageProductDependency section */"), objects_end)

        before = self.pbxproj.read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            MODULE.configure(self.project, "AuthorizedHost", self.package, apply=True)
        self.assertEqual(before, self.pbxproj.read_bytes())
        self.assertIn("ALREADY CONFIGURED", output.getvalue())

    def test_target_without_frameworks_phase_is_rejected(self) -> None:
        self.pbxproj.write_text(
            FIXTURE.replace(f"\t\t\t\t{FRAMEWORKS_ID} /* Frameworks */,\n", ""),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(MODULE.ConfigurationError, "PBXFrameworksBuildPhase"):
            MODULE.configure(self.project, "AuthorizedHost", self.package, apply=False)

    def test_repository_sample_host_with_one_line_build_record_is_recognized(self) -> None:
        sample = Path(__file__).resolve().parents[1] / "SampleHost" / "ExistingIPAOverlaySampleHost.xcodeproj"
        before = (sample / "project.pbxproj").read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            MODULE.configure(sample, "ExistingIPAOverlaySampleHost", self.package, apply=False)
        self.assertEqual(before, (sample / "project.pbxproj").read_bytes())
        self.assertIn("ALREADY CONFIGURED", output.getvalue())


if __name__ == "__main__":
    unittest.main()
