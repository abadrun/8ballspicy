#!/usr/bin/env python3
"""Validate an unsigned generic-iphoneos Swift component build.

This validator never modifies the artifact. It distinguishes a device-target
component build from a simulator build or an IPA and checks the arm64 Mach-O
object products emitted by Xcode for the Swift package.
"""
from __future__ import annotations

import argparse
import hashlib
import plistlib
import struct
import sys
import zipfile
from pathlib import Path

ARM64_CPUTYPE = 0x0100000C
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
    if not artifact.is_file() or artifact.stat().st_size == 0:
        fail("component archive does not exist or is empty")
    if not zipfile.is_zipfile(artifact):
        fail("component is not a ZIP archive")

    with zipfile.ZipFile(artifact) as archive:
        bad = archive.testzip()
        if bad:
            fail(f"ZIP integrity failed at {bad}")
        names = set(archive.namelist())
        device_names = [name for name in names if name.startswith("Debug-iphoneos/")]
        if not device_names:
            fail("Debug-iphoneos product directory is missing")
        if any(name.startswith("Payload/") or ".app/" in name for name in names):
            fail("component archive must not contain an application payload")
        if any("iphonesimulator" in name or "simulator" in name.lower() for name in names):
            fail("simulator product is present")

        required_products = {
            "Debug-iphoneos/ExistingIPAOverlayCore.o",
            "Debug-iphoneos/ExistingIPAOverlayCore.swiftmodule/arm64-apple-ios.swiftmodule",
            "Debug-iphoneos/ExistingIPAOverlayUI.o",
            "Debug-iphoneos/ExistingIPAOverlayUI.swiftmodule/arm64-apple-ios.swiftmodule",
            "Debug-iphoneos/ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Info.plist",
        }
        missing = sorted(required_products - names)
        if missing:
            fail(f"required component products are missing: {', '.join(missing)}")

        arm64_modules = [name for name in device_names if "arm64-apple-ios" in name]
        if not arm64_modules:
            fail("arm64-apple-ios Swift module output is missing")

        object_names = [name for name in device_names if name.endswith(".o")]
        if not object_names:
            fail("compiled Mach-O object products are missing")
        for name in object_names:
            data = archive.read(name)
            if data[:4] not in {MACHO64_LE, MACHO64_BE}:
                fail(f"{name} is not a 64-bit Mach-O object")
            cputype = struct.unpack_from("<I" if data[:4] == MACHO64_LE else ">I", data, 4)[0]
            if cputype != ARM64_CPUTYPE:
                fail(f"{name} has cputype 0x{cputype:08x}, expected arm64")

        ui_object = archive.read("Debug-iphoneos/ExistingIPAOverlayUI.o")
        ui_module = archive.read(
            "Debug-iphoneos/ExistingIPAOverlayUI.swiftmodule/arm64-apple-ios.swiftmodule"
        )
        if b"ExistingIPAOverlayView" not in ui_object or b"ExistingIPAOverlayView" not in ui_module:
            fail("public ExistingIPAOverlayView entry point is missing from the UI products")
        if b"ExistingIPAOverlayUI" not in ui_object or b"ExistingIPAOverlayUI" not in ui_module:
            fail("ExistingIPAOverlayUI Swift module marker is missing")

        bundle_plist = "Debug-iphoneos/ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Info.plist"
        info = plistlib.loads(archive.read(bundle_plist))
        if info.get("CFBundlePackageType") != "BNDL":
            fail("resource bundle metadata has an unexpected package type")
        if info.get("CFBundleIdentifier") != "overlaysource.ExistingIPAOverlayUI.resources":
            fail("resource bundle identifier is unexpected")
        if info.get("MinimumOSVersion") != "16.0":
            fail("resource bundle minimum iOS version is unexpected")

    print("VALID")
    print(f"file={artifact}")
    print(f"sizeBytes={artifact.stat().st_size}")
    print("deviceProduct=Debug-iphoneos")
    print("architecture=arm64")
    print("swiftModules=ExistingIPAOverlayCore,ExistingIPAOverlayUI")
    print("entryPoint=ExistingIPAOverlayUI.ExistingIPAOverlayView")
    print("resourceBundle=ExistingIPAOverlay_ExistingIPAOverlayUI.bundle")
    print(f"sha256={digest(artifact)}")


if __name__ == "__main__":
    main()
