#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("identify-authorized-host-target.py")
SPEC = importlib.util.spec_from_file_location("target_identifier", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def project_with_targets(root: Path, targets: list[tuple[str, str]]) -> Path:
    project = root / "AuthorizedHost.xcodeproj"
    project.mkdir()
    objects = []
    for index, (name, product_type) in enumerate(targets, start=1):
        identifier = f"{index:024X}"
        objects.append(
            f"\t\t{identifier} /* {name} */ = {{\n"
            "\t\t\tisa = PBXNativeTarget;\n"
            f"\t\t\tname = \"{name}\";\n"
            f"\t\t\tproductType = \"{product_type}\";\n"
            "\t\t};"
        )
    (project / "project.pbxproj").write_text(
        "// !$*UTF8*$!\n{\n\tobjects = {\n"
        "/* Begin PBXNativeTarget section */\n"
        + "\n".join(objects)
        + "\n/* End PBXNativeTarget section */\n\t};\n}\n",
        encoding="utf-8",
    )
    return project


class AuthorizedHostTargetIdentificationTests(unittest.TestCase):
    def test_auto_identifies_exactly_one_application_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = project_with_targets(
                Path(temporary),
                [("AuthorizedHost", MODULE.APP_PRODUCT_TYPE), ("SupportKit", "com.apple.product-type.framework")],
            )
            self.assertEqual(MODULE.identify(project, None), "AuthorizedHost")

    def test_multiple_application_targets_fail_as_ambiguous(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = project_with_targets(
                Path(temporary),
                [("Production", MODULE.APP_PRODUCT_TYPE), ("Staging", MODULE.APP_PRODUCT_TYPE)],
            )
            with self.assertRaisesRegex(SystemExit, "multiple iOS application targets are ambiguous"):
                MODULE.identify(project, None)

    def test_explicit_application_target_resolves_ambiguity(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = project_with_targets(
                Path(temporary),
                [("Production", MODULE.APP_PRODUCT_TYPE), ("Staging", MODULE.APP_PRODUCT_TYPE)],
            )
            self.assertEqual(MODULE.identify(project, "Production"), "Production")

    def test_explicit_non_application_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = project_with_targets(
                Path(temporary),
                [("Production", MODULE.APP_PRODUCT_TYPE), ("SupportKit", "com.apple.product-type.framework")],
            )
            with self.assertRaisesRegex(SystemExit, "is not an iOS application target"):
                MODULE.identify(project, "SupportKit")

    def test_repository_sample_has_one_identifiable_app_target(self):
        project = SCRIPT.parents[1] / "SampleHost/ExistingIPAOverlaySampleHost.xcodeproj"
        self.assertEqual(MODULE.identify(project, None), "ExistingIPAOverlaySampleHost")


if __name__ == "__main__":
    unittest.main()
