#!/usr/bin/env python3
"""Identify one real iOS application target in an authorized Xcode project."""
from __future__ import annotations

import argparse
import re
import runpy
from pathlib import Path

APP_PRODUCT_TYPE = "com.apple.product-type.application"
CONFIGURATOR = Path(__file__).with_name("configure-authorized-host-package.py")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def application_targets(project: Path) -> list[str]:
    if project.suffix != ".xcodeproj" or not project.is_dir():
        fail(f"authorized host project is missing or invalid: {project}")
    pbxproj = project / "project.pbxproj"
    if not pbxproj.is_file():
        fail(f"authorized host project has no project.pbxproj: {project}")

    namespace = runpy.run_path(str(CONFIGURATOR))
    iter_objects = namespace["iter_objects"]
    text = pbxproj.read_text(encoding="utf-8")
    names: set[str] = set()
    for _, comment, _, _, body in iter_objects(text):
        if "isa = PBXNativeTarget;" not in body:
            continue
        product_match = re.search(r'(?m)^\s*productType\s*=\s*"?([^";]+)"?;', body)
        if not product_match or product_match.group(1).strip() != APP_PRODUCT_TYPE:
            continue
        name_match = re.search(r'(?m)^\s*name\s*=\s*(?:"((?:\\.|[^"])*)"|([^;]+));', body)
        if name_match:
            name = name_match.group(1) if name_match.group(1) is not None else name_match.group(2)
            name = name.replace('\\"', '"').replace("\\\\", "\\").strip()
        else:
            name = comment.strip()
        if name:
            names.add(name)
    return sorted(names)


def identify(project: Path, requested: str | None) -> str:
    targets = application_targets(project)
    if requested:
        if requested not in targets:
            available = ", ".join(targets) if targets else "none"
            fail(
                f"requested target {requested!r} is not an iOS application target; "
                f"available application targets: {available}"
            )
        return requested
    if not targets:
        fail("no iOS application target was found; production integration cannot continue")
    if len(targets) > 1:
        fail(
            "multiple iOS application targets are ambiguous: "
            f"{', '.join(targets)}; supply --target explicitly"
        )
    return targets[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--target", help="explicit target; omit only when the project has exactly one app target")
    args = parser.parse_args()
    print(identify(args.project.resolve(), args.target))


if __name__ == "__main__":
    main()
