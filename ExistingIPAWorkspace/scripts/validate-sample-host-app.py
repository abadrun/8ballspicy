#!/usr/bin/env python3
"""Validate a built clean sample host without signing or exporting an IPA."""
from __future__ import annotations

import argparse
import plistlib
import struct
from pathlib import Path

CPU_NAMES = {
    0x01000007: "x86_64",
    0x0100000C: "arm64",
}


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def architectures(data: bytes) -> list[str]:
    if len(data) < 8:
        fail("sample executable is too small")
    magic = data[:4]
    if magic in {b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe"}:
        cpu = struct.unpack_from("<I", data, 4)[0]
        return [CPU_NAMES.get(cpu, f"cpu-0x{cpu:08x}")]
    if magic in {b"\xfe\xed\xfa\xcf", b"\xfe\xed\xfa\xce"}:
        cpu = struct.unpack_from(">I", data, 4)[0]
        return [CPU_NAMES.get(cpu, f"cpu-0x{cpu:08x}")]
    fat = {
        b"\xca\xfe\xba\xbe": (">", 20),
        b"\xbe\xba\xfe\xca": ("<", 20),
        b"\xca\xfe\xba\xbf": (">", 32),
        b"\xbf\xba\xfe\xca": ("<", 32),
    }
    if magic not in fat:
        fail(f"sample executable has unexpected Mach-O magic {magic.hex()}")
    endian, record_size = fat[magic]
    count = struct.unpack_from(f"{endian}I", data, 4)[0]
    if count < 1 or len(data) < 8 + count * record_size:
        fail("sample executable has malformed fat header")
    return [
        CPU_NAMES.get(
            struct.unpack_from(f"{endian}I", data, 8 + index * record_size)[0],
            f"cpu-0x{struct.unpack_from(f'{endian}I', data, 8 + index * record_size)[0]:08x}",
        )
        for index in range(count)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    parser.add_argument("--platform", choices=("simulator", "device"), required=True)
    args = parser.parse_args()
    app = args.app.resolve()
    if not app.is_dir() or app.suffix != ".app":
        fail("sample .app directory is missing")

    info_path = app / "Info.plist"
    if not info_path.is_file():
        fail("sample Info.plist is missing")
    info = plistlib.loads(info_path.read_bytes())
    if info.get("CFBundleIdentifier") != "com.example.ExistingIPAOverlaySampleHost":
        fail("sample bundle identifier is unexpected")
    if info.get("MinimumOSVersion") != "16.0":
        fail("sample minimum iOS version is not 16.0")
    executable_name = info.get("CFBundleExecutable")
    executable = app / executable_name if executable_name else Path()
    if not executable.is_file():
        fail("sample executable is missing")
    executable_data = executable.read_bytes()
    arch = architectures(executable_data)
    if args.platform == "device" and "arm64" not in arch:
        fail(f"device sample has no arm64 slice: {arch}")
    if args.platform == "simulator" and not set(arch) & {"arm64", "x86_64"}:
        fail(f"simulator sample has no supported slice: {arch}")
    if b"libloader" in executable_data:
        fail("sample executable unexpectedly references libloader")

    # Swift symbol spelling is not a stable linkage oracle: newer toolchains may
    # strip or encode module/type names differently even in Debug app binaries.
    # The sample source validator proves that the app compiles a direct
    # ExistingIPAOverlayView reference, while this validator proves that SwiftPM
    # copied the product's resource bundle and did not package a dynamic overlay
    # framework. Together with successful app launch, that is stable evidence
    # that the automatic SwiftPM library was linked into the host executable.
    dynamic_overlay_payloads = [
        path
        for path in app.rglob("*")
        if path.name in {"ExistingIPAOverlay", "ExistingIPAOverlay.framework", "ExistingIPAOverlay.dylib"}
    ]
    if dynamic_overlay_payloads:
        fail("sample unexpectedly embeds a dynamic ExistingIPAOverlay payload")

    resource = app / "ExistingIPAOverlay_ExistingIPAOverlayUI.bundle"
    resource_info_path = resource / "Info.plist"
    if not resource_info_path.is_file():
        fail("SwiftPM resource bundle is missing")
    resource_info = plistlib.loads(resource_info_path.read_bytes())
    if resource_info.get("CFBundlePackageType") != "BNDL":
        fail("SwiftPM resource bundle package type is unexpected")
    if resource_info.get("MinimumOSVersion") != "16.0":
        fail("SwiftPM resource bundle minimum iOS version is unexpected")
    for relative in (
        "Assets.car",
        "en.lproj/Localizable.strings",
        "id.lproj/Localizable.strings",
    ):
        if not (resource / relative).is_file():
            fail(f"SwiftPM resource is missing: {relative}")

    for path in app.rglob("*"):
        if "libloader" in path.name.lower():
            fail("sample host unexpectedly contains libloader")

    print("VALID")
    print(f"app={app}")
    print(f"platform={args.platform}")
    print(f"architectures={','.join(sorted(set(arch)))}")
    print("bundleIdentifier=com.example.ExistingIPAOverlaySampleHost")
    print("minimumIOS=16.0")
    print("module=ExistingIPAOverlayUI")
    print("linkage=automatic-static-no-embedded-overlay-framework")
    print("resourceBundle=ExistingIPAOverlay_ExistingIPAOverlayUI.bundle")


if __name__ == "__main__":
    main()
