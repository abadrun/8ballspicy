#!/usr/bin/env python3
"""Validate an unsigned iOS Simulator Swift component build."""
from __future__ import annotations

import argparse
import hashlib
import plistlib
import struct
import zipfile
from pathlib import Path

CPU_NAMES = {
    0x01000007: "x86_64",
    0x0100000C: "arm64",
}
MACHO64_LE = b"\xcf\xfa\xed\xfe"
MACHO64_BE = b"\xfe\xed\xfa\xcf"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    artifact = args.artifact.resolve()
    if not artifact.is_file() or not zipfile.is_zipfile(artifact):
        fail("simulator component ZIP does not exist or is invalid")

    with zipfile.ZipFile(artifact) as archive:
        bad = archive.testzip()
        if bad:
            fail(f"ZIP integrity failed at {bad}")
        names = set(archive.namelist())
        prefix = "Debug-iphonesimulator/"
        if not any(name.startswith(prefix) for name in names):
            fail("Debug-iphonesimulator product directory is missing")
        if any(name.startswith("Payload/") or ".app/" in name for name in names):
            fail("component archive must not contain an application payload")
        if any(name.startswith("Debug-iphoneos/") for name in names):
            fail("device products are mixed into the simulator component")

        required = {
            f"{prefix}ExistingIPAOverlayCore.o",
            f"{prefix}ExistingIPAOverlayUI.o",
            f"{prefix}ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Info.plist",
        }
        missing = sorted(required - names)
        if missing:
            fail(f"required simulator products are missing: {', '.join(missing)}")
        module_names = [
            name for name in names
            if name.startswith(prefix)
            and name.endswith("-apple-ios-simulator.swiftmodule")
            and ("ExistingIPAOverlayCore.swiftmodule/" in name or "ExistingIPAOverlayUI.swiftmodule/" in name)
        ]
        if len(module_names) < 2:
            fail("simulator Swift modules for Core and UI are missing")

        object_names = sorted(name for name in names if name.startswith(prefix) and name.endswith(".o"))
        architectures = set()
        for name in object_names:
            data = archive.read(name)
            if data[:4] not in {MACHO64_LE, MACHO64_BE}:
                fail(f"{name} is not a 64-bit Mach-O object")
            endian = "<" if data[:4] == MACHO64_LE else ">"
            cpu = struct.unpack_from(f"{endian}I", data, 4)[0]
            architecture = CPU_NAMES.get(cpu)
            if architecture not in {"arm64", "x86_64"}:
                fail(f"{name} has unsupported simulator CPU 0x{cpu:08x}")
            architectures.add(architecture)

        ui_object = archive.read(f"{prefix}ExistingIPAOverlayUI.o")
        if b"ExistingIPAOverlayUI" not in ui_object or b"ExistingIPAOverlayView" not in ui_object:
            fail("simulator UI object is missing public module/view markers")

        resource_info = plistlib.loads(
            archive.read(f"{prefix}ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Info.plist")
        )
        if resource_info.get("CFBundlePackageType") != "BNDL":
            fail("simulator resource bundle package type is unexpected")
        if resource_info.get("MinimumOSVersion") != "16.0":
            fail("simulator resource bundle minimum iOS version is unexpected")
        if "iPhoneSimulator" not in resource_info.get("CFBundleSupportedPlatforms", []):
            fail("resource bundle is not marked for iPhoneSimulator")

    print("VALID")
    print(f"file={artifact}")
    print("platform=iOS Simulator")
    print(f"architectures={','.join(sorted(architectures))}")
    print("swiftModules=ExistingIPAOverlayCore,ExistingIPAOverlayUI")
    print("entryPoint=ExistingIPAOverlayUI.ExistingIPAOverlayView")
    print("resourceBundle=ExistingIPAOverlay_ExistingIPAOverlayUI.bundle")
    print(f"sha256={digest(artifact)}")


if __name__ == "__main__":
    main()
