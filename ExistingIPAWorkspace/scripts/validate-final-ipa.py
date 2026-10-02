#!/usr/bin/env python3
"""Validate a real exported iOS IPA without creating or modifying one.

Structural checks run everywhere. Signature and provisioning checks are enabled
only when requested and require the legitimate macOS Apple tooling that created
the export.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import plistlib
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


CPU_TYPE_ARM64 = 0x0100000C
FAT_MAGIC = b"\xca\xfe\xba\xbe"
FAT_CIGAM = b"\xbe\xba\xfe\xca"
FAT_MAGIC_64 = b"\xca\xfe\xba\xbf"
FAT_CIGAM_64 = b"\xbf\xba\xfe\xca"
THIN_64_LE = b"\xcf\xfa\xed\xfe"
THIN_64_BE = b"\xfe\xed\xfa\xcf"
THIN_32_LE = b"\xce\xfa\xed\xfe"
THIN_32_BE = b"\xfe\xed\xfa\xce"
LOAD_DYLIB_COMMANDS = {0xC, 0x80000018, 0x8000001F, 0x80000023}


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def cpu_name(cpu_type: int) -> str:
    if cpu_type == CPU_TYPE_ARM64:
        return "arm64"
    if cpu_type == 0x01000007:
        return "x86_64"
    if cpu_type == 12:
        return "arm"
    if cpu_type == 7:
        return "x86"
    return f"cpu-0x{cpu_type:08x}"


def mach_slices(data: bytes) -> list[tuple[int, int, int, str]]:
    """Return (offset, size, CPU type, endian) records for Mach-O slices."""
    if len(data) < 8:
        fail("main executable is too small to be Mach-O")
    magic = data[:4]
    if magic in {THIN_64_LE, THIN_32_LE}:
        return [(0, len(data), struct.unpack_from("<I", data, 4)[0], "<")]
    if magic in {THIN_64_BE, THIN_32_BE}:
        return [(0, len(data), struct.unpack_from(">I", data, 4)[0], ">")]
    if magic not in {FAT_MAGIC, FAT_CIGAM, FAT_MAGIC_64, FAT_CIGAM_64}:
        fail(f"main executable has unexpected Mach-O magic {magic.hex()}")

    endian = ">" if magic in {FAT_MAGIC, FAT_MAGIC_64} else "<"
    is_64 = magic in {FAT_MAGIC_64, FAT_CIGAM_64}
    count = struct.unpack_from(f"{endian}I", data, 4)[0]
    record_size = 32 if is_64 else 20
    if count == 0 or len(data) < 8 + count * record_size:
        fail("fat Mach-O header is malformed")
    records: list[tuple[int, int, int, str]] = []
    for index in range(count):
        cursor = 8 + index * record_size
        cpu_type = struct.unpack_from(f"{endian}I", data, cursor)[0]
        if is_64:
            offset, size = struct.unpack_from(f"{endian}QQ", data, cursor + 8)
        else:
            offset, size = struct.unpack_from(f"{endian}II", data, cursor + 8)
        if offset + size > len(data):
            fail("fat Mach-O slice is outside the executable")
        records.append((offset, size, cpu_type, endian))
    return records


def loaded_dylibs(data: bytes, slice_offset: int, slice_size: int, endian: str) -> list[str]:
    if slice_size < 28:
        return []
    magic = data[slice_offset:slice_offset + 4]
    is_64 = magic in {THIN_64_LE, THIN_64_BE}
    header_size = 32 if is_64 else 28
    if slice_size < header_size:
        return []
    ncmds = struct.unpack_from(f"{endian}I", data, slice_offset + 16)[0]
    sizeofcmds = struct.unpack_from(f"{endian}I", data, slice_offset + 20)[0]
    commands_end = slice_offset + header_size + sizeofcmds
    if commands_end > slice_offset + slice_size:
        return []
    paths: list[str] = []
    cursor = slice_offset + header_size
    for _ in range(ncmds):
        if cursor + 8 > commands_end:
            return paths
        command, command_size = struct.unpack_from(f"{endian}II", data, cursor)
        if command_size < 8 or cursor + command_size > commands_end:
            return paths
        if command in LOAD_DYLIB_COMMANDS and command_size >= 24:
            name_offset = struct.unpack_from(f"{endian}I", data, cursor + 8)[0]
            if 24 <= name_offset < command_size:
                raw_name = data[cursor + name_offset:cursor + command_size].split(b"\0", 1)[0]
                paths.append(raw_name.decode("utf-8", errors="replace"))
        cursor += command_size
    return paths


def verify_codesign(app_path: Path) -> None:
    codesign = shutil.which("codesign")
    if not codesign:
        fail("codesign is unavailable; signature verification requires macOS")
    result = subprocess.run(
        [codesign, "--verify", "--deep", "--strict", "--verbose=2", str(app_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        message = (result.stderr or result.stdout).strip().replace("\n", " ")
        fail(f"codesign verification failed: {message}")


def verify_provisioning(profile_path: Path, bundle_id: str) -> None:
    security = shutil.which("security")
    if not security:
        fail("security is unavailable; provisioning verification requires macOS")
    result = subprocess.run(
        [security, "cms", "-D", "-i", str(profile_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        fail("embedded.mobileprovision could not be decoded")
    try:
        profile = plistlib.loads(result.stdout)
    except (plistlib.InvalidFileException, ValueError) as error:
        fail(f"embedded.mobileprovision is not a valid plist: {error}")
    expires = profile.get("ExpirationDate")
    if not isinstance(expires, dt.datetime):
        fail("embedded.mobileprovision has no valid ExpirationDate")
    now = dt.datetime.now(tz=expires.tzinfo) if expires.tzinfo else dt.datetime.now()
    if expires <= now:
        fail("embedded.mobileprovision is expired")
    entitlements = profile.get("Entitlements")
    if not isinstance(entitlements, dict):
        fail("embedded.mobileprovision has no Entitlements dictionary")
    application_identifier = entitlements.get("application-identifier")
    if not isinstance(application_identifier, str) or not application_identifier.endswith(f".{bundle_id}"):
        fail("embedded.mobileprovision application-identifier does not match the app bundle identifier")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ipa", type=Path)
    parser.add_argument("--require-signature", action="store_true")
    parser.add_argument("--require-provisioning", action="store_true")
    parser.add_argument("--codesign-verify", action="store_true")
    parser.add_argument("--require-arm64", action="store_true")
    parser.add_argument("--require-component", metavar="NAME")
    parser.add_argument("--bundle-id")
    args = parser.parse_args()
    ipa = args.ipa.resolve()
    if not ipa.is_file() or ipa.stat().st_size == 0:
        fail("IPA does not exist or is empty")
    if not zipfile.is_zipfile(ipa):
        fail("not a ZIP/IPA container")

    with zipfile.ZipFile(ipa) as archive:
        bad = archive.testzip()
        if bad:
            fail(f"ZIP integrity failed at {bad}")
        names = archive.namelist()
        if not any(name.startswith("Payload/") for name in names):
            fail("Payload directory is missing")
        apps = sorted({"/".join(name.split("/")[:2]) for name in names
                       if name.startswith("Payload/") and len(name.split("/")) > 1
                       and name.split("/")[1].endswith(".app")})
        if len(apps) != 1:
            fail(f"expected one Payload app bundle, found {len(apps)}")
        app = apps[0]
        plist_path = f"{app}/Info.plist"
        if plist_path not in names:
            fail("application Info.plist is missing")
        try:
            info = plistlib.loads(archive.read(plist_path))
        except (plistlib.InvalidFileException, ValueError) as error:
            fail(f"application Info.plist is invalid: {error}")
        bundle_id = info.get("CFBundleIdentifier")
        executable = info.get("CFBundleExecutable")
        if not bundle_id or not executable:
            fail("bundle identifier or executable metadata is missing")
        if args.bundle_id and bundle_id != args.bundle_id:
            fail(f"bundle id {bundle_id!r} does not match required {args.bundle_id!r}")
        executable_path = f"{app}/{executable}"
        if executable_path not in names:
            fail(f"main executable is missing: {executable_path}")
        executable_data = archive.read(executable_path)
        slices = mach_slices(executable_data)
        architectures = sorted({cpu_name(cpu_type) for _, _, cpu_type, _ in slices})
        if args.require_arm64 and "arm64" not in architectures:
            fail(f"main executable has no arm64 slice (found {', '.join(architectures)})")
        code_resources = f"{app}/_CodeSignature/CodeResources"
        if args.require_signature and code_resources not in names:
            fail("CodeResources is missing from signed export")

        component_evidence = "not requested"
        if args.require_component:
            component_bytes = args.require_component.encode("utf-8")
            framework_members = [name for name in names if f"/Frameworks/{args.require_component}" in name]
            dylib_references = [
                dylib for offset, size, _, endian in slices
                for dylib in loaded_dylibs(executable_data, offset, size, endian)
                if args.require_component in dylib
            ]
            executable_reference = component_bytes in executable_data
            if not framework_members and not executable_reference:
                fail(f"required component {args.require_component!r} is neither embedded nor referenced by the main executable")
            if not executable_reference and not dylib_references:
                fail(f"required component {args.require_component!r} is present but not referenced/loaded by the main executable")
            if executable_reference:
                component_evidence = "main executable contains component reference"
            else:
                component_evidence = f"main executable loads {dylib_references[0]}"

        if args.codesign_verify or args.require_provisioning:
            with tempfile.TemporaryDirectory(prefix="ipa-validation-") as temporary:
                root = Path(temporary)
                archive.extractall(root)
                app_path = root / app
                if args.codesign_verify:
                    verify_codesign(app_path)
                if args.require_provisioning:
                    profile_path = app_path / "embedded.mobileprovision"
                    if not profile_path.is_file():
                        fail("embedded.mobileprovision is missing")
                    verify_provisioning(profile_path, bundle_id)

    print("VALID")
    print(f"file={ipa}")
    print(f"sizeBytes={ipa.stat().st_size}")
    print(f"bundleIdentifier={bundle_id}")
    print(f"architectures={','.join(architectures)}")
    print(f"component={component_evidence}")
    print(f"sha256={sha256(ipa)}")


if __name__ == "__main__":
    main()
