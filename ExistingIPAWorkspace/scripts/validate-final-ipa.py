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
import json
import plistlib
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


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


def zip_member_hashes(archive: zipfile.ZipFile) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for info in archive.infolist():
        if info.is_dir():
            continue
        digest = hashlib.sha256()
        with archive.open(info) as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        hashes[info.filename] = digest.hexdigest()
    return hashes


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def version(value: str, label: str) -> tuple[int, ...]:
    parts = value.split(".")
    if not parts or any(not part.isdigit() for part in parts):
        fail(f"{label} is not a numeric version: {value!r}")
    return tuple(int(part) for part in parts)


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
    parser.add_argument(
        "--require-component",
        metavar="NAME",
        help="require dynamic-load, executable-marker, or component-specific SwiftPM resource evidence",
    )
    parser.add_argument(
        "--require-resource-bundle",
        metavar="NAME.bundle",
        help="require a SwiftPM resource bundle at the application-bundle root",
    )
    parser.add_argument(
        "--require-bundle-resource",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="require a file inside --require-resource-bundle (repeatable)",
    )
    parser.add_argument("--minimum-ios", metavar="VERSION")
    parser.add_argument(
        "--baseline-ipa",
        type=Path,
        help="record file-level added/modified/removed paths relative to this immutable baseline",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="write a deterministic machine-readable validation report",
    )
    parser.add_argument(
        "--reject-sha256",
        action="append",
        default=[],
        metavar="HEX",
        help="reject an archive with this SHA-256 (repeatable)",
    )
    parser.add_argument("--bundle-id")
    args = parser.parse_args()
    ipa = args.ipa.resolve()
    if not ipa.is_file() or ipa.stat().st_size == 0:
        fail("IPA does not exist or is empty")
    ipa_sha256 = sha256(ipa)
    rejected_hashes = {value.lower() for value in args.reject_sha256}
    if any(len(value) != 64 or any(char not in "0123456789abcdef" for char in value) for value in rejected_hashes):
        fail("--reject-sha256 requires a 64-character hexadecimal digest")
    if ipa_sha256 in rejected_hashes:
        fail(f"IPA SHA-256 is explicitly rejected: {ipa_sha256}")
    if not zipfile.is_zipfile(ipa):
        fail("not a ZIP/IPA container")
    if args.require_bundle_resource and not args.require_resource_bundle:
        fail("--require-bundle-resource requires --require-resource-bundle")

    baseline_sha256: str | None = None
    baseline_hashes: dict[str, str] | None = None
    if args.baseline_ipa:
        baseline = args.baseline_ipa.resolve()
        if not baseline.is_file() or not zipfile.is_zipfile(baseline):
            fail(f"baseline IPA is missing or invalid: {baseline}")
        baseline_sha256 = sha256(baseline)
        with zipfile.ZipFile(baseline) as baseline_archive:
            bad_baseline = baseline_archive.testzip()
            if bad_baseline:
                fail(f"baseline ZIP integrity failed at {bad_baseline}")
            baseline_hashes = zip_member_hashes(baseline_archive)

    codesign_status = "NOT_REQUESTED"
    provisioning_status = "NOT_REQUESTED"
    signature_status = "UNKNOWN"
    final_hashes: dict[str, str] = {}

    with zipfile.ZipFile(ipa) as archive:
        bad = archive.testzip()
        if bad:
            fail(f"ZIP integrity failed at {bad}")
        names = archive.namelist()
        if len(set(names)) != len(names):
            fail("IPA contains duplicate ZIP member names")
        for name in names:
            member = PurePosixPath(name)
            if member.is_absolute() or ".." in member.parts or "\\" in name:
                fail(f"IPA contains an unsafe ZIP member path: {name!r}")
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
        app_version = info.get("CFBundleShortVersionString")
        build_version = info.get("CFBundleVersion")
        if not bundle_id or not executable:
            fail("bundle identifier or executable metadata is missing")
        if not isinstance(app_version, str) or not app_version:
            fail("application version (CFBundleShortVersionString) is missing")
        if not isinstance(build_version, str) or not build_version:
            fail("application build version (CFBundleVersion) is missing")
        if args.bundle_id and bundle_id != args.bundle_id:
            fail(f"bundle id {bundle_id!r} does not match required {args.bundle_id!r}")
        deployment_target = info.get("MinimumOSVersion")
        if args.minimum_ios:
            if not isinstance(deployment_target, str):
                fail("application MinimumOSVersion is missing")
            if version(deployment_target, "application MinimumOSVersion") < version(args.minimum_ios, "required minimum iOS"):
                fail(
                    f"application deployment target {deployment_target} is incompatible; "
                    f"required iOS floor is {args.minimum_ios}"
                )
        executable_path = f"{app}/{executable}"
        if executable_path not in names:
            fail(f"main executable is missing: {executable_path}")
        executable_data = archive.read(executable_path)
        slices = mach_slices(executable_data)
        architectures = sorted({cpu_name(cpu_type) for _, _, cpu_type, _ in slices})
        if args.require_arm64 and "arm64" not in architectures:
            fail(f"main executable has no arm64 slice (found {', '.join(architectures)})")
        code_resources = f"{app}/_CodeSignature/CodeResources"
        signature_status = "PRESENT" if code_resources in names else "ABSENT"
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
            swiftpm_resource_members = [
                name for name in names
                if args.require_component in name and ".bundle/" in name
            ]
            if not framework_members and not executable_reference and not swiftpm_resource_members:
                fail(
                    f"required component {args.require_component!r} has no executable, "
                    "framework, or SwiftPM resource evidence"
                )
            if framework_members and not executable_reference and not dylib_references:
                fail(f"required dynamic component {args.require_component!r} is embedded but not loaded")
            if executable_reference:
                component_evidence = "main executable contains component reference"
            elif dylib_references:
                component_evidence = f"main executable loads {dylib_references[0]}"
            else:
                component_evidence = "component-specific SwiftPM resource bundle (static linkage verified during host build/test)"

        resource_bundle_evidence = "not requested"
        if args.require_resource_bundle:
            bundle_name = args.require_resource_bundle
            if not bundle_name.endswith(".bundle") or "/" in bundle_name or "\\" in bundle_name:
                fail("required resource bundle must be a bundle basename ending in .bundle")
            resource_info_path = f"{app}/{bundle_name}/Info.plist"
            if resource_info_path not in names:
                fail(f"required resource bundle is missing from the app root: {bundle_name}")
            try:
                resource_info = plistlib.loads(archive.read(resource_info_path))
            except (plistlib.InvalidFileException, ValueError) as error:
                fail(f"required resource bundle Info.plist is invalid: {error}")
            if resource_info.get("CFBundlePackageType") != "BNDL":
                fail("required resource bundle has an unexpected package type")
            if args.minimum_ios:
                resource_minimum = resource_info.get("MinimumOSVersion")
                if not isinstance(resource_minimum, str):
                    fail("required resource bundle MinimumOSVersion is missing")
                if version(resource_minimum, "resource bundle MinimumOSVersion") < version(args.minimum_ios, "required minimum iOS"):
                    fail(
                        f"required resource bundle deployment target {resource_minimum} "
                        f"is below iOS {args.minimum_ios}"
                    )
            for relative in args.require_bundle_resource:
                if not relative or relative.startswith(("/", "\\")) or ".." in Path(relative).parts:
                    fail(f"invalid required bundle resource path: {relative!r}")
                member = f"{app}/{bundle_name}/{relative}"
                if member not in names:
                    fail(f"required resource bundle file is missing: {relative}")
            resource_bundle_evidence = resource_info_path

        if args.codesign_verify or args.require_provisioning:
            with tempfile.TemporaryDirectory(prefix="ipa-validation-") as temporary:
                root = Path(temporary)
                archive.extractall(root)
                app_path = root / app
                if args.codesign_verify:
                    verify_codesign(app_path)
                    codesign_status = "VERIFIED"
                if args.require_provisioning:
                    profile_path = app_path / "embedded.mobileprovision"
                    if not profile_path.is_file():
                        fail("embedded.mobileprovision is missing")
                    verify_provisioning(profile_path, bundle_id)
                    provisioning_status = "VERIFIED"

        final_hashes = zip_member_hashes(archive)

    delta = None
    if baseline_hashes is not None:
        added = sorted(final_hashes.keys() - baseline_hashes.keys())
        removed = sorted(baseline_hashes.keys() - final_hashes.keys())
        modified = sorted(
            name for name in final_hashes.keys() & baseline_hashes.keys()
            if final_hashes[name] != baseline_hashes[name]
        )
        delta = {
            "baselinePath": str(args.baseline_ipa.resolve()),
            "baselineSHA256": baseline_sha256,
            "added": added,
            "modified": modified,
            "removed": removed,
            "counts": {
                "added": len(added),
                "modified": len(modified),
                "removed": len(removed),
            },
        }

    report = {
        "schemaVersion": 1,
        "validation": "PASS",
        "ipa": {
            "path": str(ipa),
            "sha256": ipa_sha256,
            "sizeBytes": ipa.stat().st_size,
            "architectures": architectures,
            "bundleIdentifier": bundle_id,
            "appVersion": app_version,
            "buildVersion": build_version,
            "minimumIOS": deployment_target,
        },
        "signing": {
            "codeResources": signature_status,
            "codesign": codesign_status,
            "provisioning": provisioning_status,
        },
        "embeddedComponent": {
            "required": args.require_component,
            "evidence": component_evidence,
            "status": "PASS" if args.require_component else "NOT_REQUESTED",
        },
        "resourceBundle": {
            "required": args.require_resource_bundle,
            "evidence": resource_bundle_evidence,
            "requiredMembers": sorted(args.require_bundle_resource),
            "status": "PASS" if args.require_resource_bundle else "NOT_REQUESTED",
        },
        "changedFilesRelativeToBaseline": delta,
    }
    if args.report_json:
        report_path = args.report_json.resolve()
        if report_path == ipa:
            fail("validation report path cannot replace the IPA")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_report = report_path.with_suffix(report_path.suffix + ".tmp")
        temporary_report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary_report.replace(report_path)

    print("VALID")
    print(f"file={ipa}")
    print(f"sizeBytes={ipa.stat().st_size}")
    print(f"bundleIdentifier={bundle_id}")
    print(f"appVersion={app_version}")
    print(f"buildVersion={build_version}")
    print(f"minimumIOS={deployment_target or 'not declared'}")
    print(f"architectures={','.join(architectures)}")
    print(f"signing={signature_status};codesign={codesign_status};provisioning={provisioning_status}")
    print(f"component={component_evidence}")
    print(f"resourceBundle={resource_bundle_evidence}")
    if delta:
        counts = delta["counts"]
        print(
            "changedFilesRelativeToBaseline="
            f"added:{counts['added']},modified:{counts['modified']},removed:{counts['removed']}"
        )
    else:
        print("changedFilesRelativeToBaseline=not requested")
    print(f"sha256={ipa_sha256}")
    if args.report_json:
        print(f"report={args.report_json.resolve()}")


if __name__ == "__main__":
    main()
