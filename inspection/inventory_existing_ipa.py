#!/usr/bin/env python3
"""Create a complete, read-only inventory of the existing IPA baseline.

Every ZIP member is listed and classified as ORIGINAL_GAME, EXISTING_OVERLAY,
or UNKNOWN. UNKNOWN is used for mixed/post-injection components rather than
silently attributing them to either owner. In addition to per-member hashes,
the report records all bundle identifiers, embedded frameworks, standalone
dylibs, Mach-O architectures, resource types, the application Info.plist, and
the static evidence that identifies the existing i3rby modification.

The script reads the archive directly and never modifies or extracts it. Use
``inspection/inspect_ipa.py --extract-to <temporary-directory>`` when a safe,
explicit extraction is required for the baseline procedure.
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IPA = ROOT / "8-ball-pool-i3rby-IPAOMTK.COM.ipa"
APP = "Payload/pool.app"
OVERLAY = f"{APP}/Frameworks/libloader.framework"
INFO_PLIST = f"{APP}/Info.plist"

CPU_NAMES = {
    7: "x86",
    12: "arm",
    18: "ppc",
    0x01000007: "x86_64",
    0x0100000C: "arm64",
    0x01000012: "ppc64",
}
I3RBY_MARKER = re.compile(rb"com\.i3rby\.[A-Za-z0-9._-]+")


def file_sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def member_digest_and_head(
    archive: zipfile.ZipFile, info: zipfile.ZipInfo, head_size: int = 4096
) -> tuple[str | None, bytes]:
    if info.is_dir():
        return None, b""
    result = hashlib.sha256()
    head = bytearray()
    with archive.open(info) as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
            if len(head) < head_size:
                head.extend(block[: head_size - len(head)])
    return result.hexdigest(), bytes(head)


def cpu_name(cpu_type: int) -> str:
    return CPU_NAMES.get(cpu_type, f"cpu-0x{cpu_type:08x}")


def macho_architectures(data: bytes) -> list[dict[str, Any]] | None:
    """Return architecture records for thin/fat Mach-O data, else None."""
    if len(data) < 8:
        return None
    magic = data[:4]
    thin_formats = {
        b"\xce\xfa\xed\xfe": "<",  # 32-bit little-endian
        b"\xcf\xfa\xed\xfe": "<",  # 64-bit little-endian
        b"\xfe\xed\xfa\xce": ">",  # 32-bit big-endian
        b"\xfe\xed\xfa\xcf": ">",  # 64-bit big-endian
    }
    if magic in thin_formats:
        endian = thin_formats[magic]
        cpu_type = struct.unpack_from(f"{endian}I", data, 4)[0]
        return [{"cpuType": cpu_type, "name": cpu_name(cpu_type)}]

    fat_formats = {
        b"\xca\xfe\xba\xbe": (">", False),
        b"\xbe\xba\xfe\xca": ("<", False),
        b"\xca\xfe\xba\xbf": (">", True),
        b"\xbf\xba\xfe\xca": ("<", True),
    }
    if magic not in fat_formats:
        return None
    endian, is_64 = fat_formats[magic]
    count = struct.unpack_from(f"{endian}I", data, 4)[0]
    record_size = 32 if is_64 else 20
    if count == 0 or len(data) < 8 + count * record_size:
        return None
    result = []
    for index in range(count):
        offset = 8 + index * record_size
        cpu_type = struct.unpack_from(f"{endian}I", data, offset)[0]
        result.append({"cpuType": cpu_type, "name": cpu_name(cpu_type)})
    return result


def macho(data: bytes) -> dict[str, Any]:
    """Parse details used for the known thin little-endian arm64 binaries."""
    architectures = macho_architectures(data)
    if not architectures:
        return {"recognized": False}
    result: dict[str, Any] = {
        "recognized": True,
        "architectures": sorted({item["name"] for item in architectures}),
        "slices": architectures,
    }
    if len(data) < 32 or data[:4] != b"\xcf\xfa\xed\xfe":
        return result

    cpu_type = struct.unpack_from("<I", data, 4)[0]
    command_count = struct.unpack_from("<I", data, 16)[0]
    command_bytes = struct.unpack_from("<I", data, 20)[0]
    commands_end = 32 + command_bytes
    offset, libraries, cryptid = 32, [], None
    if commands_end > len(data):
        result["loadCommandParseError"] = "load-command region exceeds file"
        return result
    for _ in range(command_count):
        if offset + 8 > commands_end:
            result["loadCommandParseError"] = "truncated load-command header"
            break
        command, size = struct.unpack_from("<II", data, offset)
        if size < 8 or offset + size > commands_end:
            result["loadCommandParseError"] = "invalid load-command size"
            break
        if command == 0xC:  # LC_LOAD_DYLIB
            name_offset = struct.unpack_from("<I", data, offset + 8)[0]
            if name_offset < size:
                name = data[offset + name_offset : offset + size].split(b"\0", 1)[0]
                libraries.append(name.decode("utf-8", "replace"))
        elif command == 0x2C:  # LC_ENCRYPTION_INFO_64
            cryptid = struct.unpack_from("<I", data, offset + 16)[0]
        offset += size
    result.update(
        {
            "cpuType": cpu_type,
            "cryptid": cryptid,
            "loadDylibs": libraries,
            "loadDylibCount": len(libraries),
        }
    )
    return result


def classify(path: str) -> tuple[str, str]:
    if path.startswith(OVERLAY + "/") or path == OVERLAY:
        return "EXISTING_OVERLAY", "member of the injected libloader.framework bundle"
    if path in {f"{APP}/pool", INFO_PLIST}:
        return "UNKNOWN", "host component contains or records post-build overlay/redistribution changes"
    if path.startswith(f"{APP}/_CodeSignature/"):
        return "UNKNOWN", "signature metadata was generated after overlay injection"
    if path.startswith(f"{APP}/SC_Info/"):
        return "UNKNOWN", "FairPlay metadata location contains only a redistribution placeholder"
    if path == f"{APP}/PkgInfo":
        return "ORIGINAL_GAME", "standard host application metadata"
    if path in {"Payload/", f"{APP}/"}:
        return "ORIGINAL_GAME", "application container"
    if path.startswith(f"{APP}/"):
        return "ORIGINAL_GAME", "host resource, localization, plug-in, or bundled dependency outside the injected overlay"
    return "UNKNOWN", "not attributable from the available static evidence"


def bundle_record(path: str, value: dict[str, Any], digest: str | None) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": digest,
        "bundleIdentifier": value.get("CFBundleIdentifier"),
        "bundleName": value.get("CFBundleName"),
        "bundleExecutable": value.get("CFBundleExecutable"),
        "packageType": value.get("CFBundlePackageType"),
        "shortVersion": value.get("CFBundleShortVersionString"),
        "buildVersion": value.get("CFBundleVersion"),
        "minimumOSVersion": value.get("MinimumOSVersion"),
        "supportedPlatforms": value.get("CFBundleSupportedPlatforms"),
    }


def extension(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    return suffix if suffix else "<none>"


def main() -> None:
    ipa = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_IPA
    if not ipa.is_file():
        raise SystemExit(f"IPA does not exist: {ipa}")

    with zipfile.ZipFile(ipa) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise SystemExit(f"ZIP integrity failure at {bad_member}")
        names = archive.namelist()
        if INFO_PLIST not in names:
            raise SystemExit(f"application Info.plist not found: {INFO_PLIST}")

        entries = []
        category_counts: Counter[str] = Counter()
        category_bytes: Counter[str] = Counter()
        extension_counts: Counter[str] = Counter()
        extension_bytes: Counter[str] = Counter()
        bundle_metadata: list[dict[str, Any]] = []
        macho_binaries: list[dict[str, Any]] = []
        digests: dict[str, str | None] = {}

        for item in archive.infolist():
            category, reason = classify(item.filename)
            digest, head = member_digest_and_head(archive, item)
            digests[item.filename] = digest
            category_counts[category] += 1
            category_bytes[category] += item.file_size
            if not item.is_dir():
                suffix = extension(item.filename)
                extension_counts[suffix] += 1
                extension_bytes[suffix] += item.file_size
                architectures = macho_architectures(head)
                if architectures:
                    macho_binaries.append(
                        {
                            "path": item.filename,
                            "category": category,
                            "sizeBytes": item.file_size,
                            "sha256": digest,
                            "architectures": sorted({record["name"] for record in architectures}),
                            "slices": architectures,
                        }
                    )
                if PurePosixPath(item.filename).name == "Info.plist":
                    try:
                        value = plistlib.loads(archive.read(item))
                    except (plistlib.InvalidFileException, ValueError, TypeError):
                        value = None
                    if isinstance(value, dict):
                        bundle_metadata.append(bundle_record(item.filename, value, digest))
            entries.append(
                {
                    "path": item.filename,
                    "category": category,
                    "classificationReason": reason,
                    "directory": item.is_dir(),
                    "sizeBytes": item.file_size,
                    "compressedSizeBytes": item.compress_size,
                    "crc32": f"{item.CRC:08x}",
                    "sha256": digest,
                }
            )

        info_data = archive.read(INFO_PLIST)
        info = plistlib.loads(info_data)
        executable = f"{APP}/{info['CFBundleExecutable']}"
        executable_data = archive.read(executable)
        executable_macho = macho(executable_data)
        overlay_binary = f"{OVERLAY}/libloader"
        overlay_data = archive.read(overlay_binary)
        overlay_macho = macho(overlay_data)

    framework_names = sorted(
        {
            path.split("/")[3]
            for path in names
            if path.startswith(f"{APP}/Frameworks/")
            and len(path.split("/")) > 3
            and path.split("/")[3].endswith(".framework")
        }
    )
    framework_paths = [f"{APP}/Frameworks/{name}" for name in framework_names]
    framework_directory_entries = sorted(
        {
            path.split("/")[3]
            for path in names
            if path.startswith(f"{APP}/Frameworks/")
            and len(path.split("/")) > 3
            and path.split("/")[3]
        }
    )
    localizations = sorted(
        {
            path.split("/")[2]
            for path in names
            if path.startswith(f"{APP}/")
            and len(path.split("/")) > 2
            and path.split("/")[2].endswith(".lproj")
        }
    )
    dylibs = sorted(
        path
        for path in names
        if path.startswith(f"{APP}/Frameworks/") and path.endswith(".dylib")
    )
    app_extensions = sorted(
        {
            "/".join(path.split("/")[:4])
            for path in names
            if path.startswith(f"{APP}/PlugIns/")
            and len(path.split("/")) > 3
            and path.split("/")[3].endswith(".appex")
        }
    )
    resource_bundles = sorted(
        {
            path[: path.index(".bundle/") + len(".bundle")]
            for path in names
            if ".bundle/" in path
        }
    )
    bundle_metadata.sort(key=lambda item: item["path"])
    macho_binaries.sort(key=lambda item: item["path"])
    bundle_identifiers = [
        {"path": item["path"], "bundleIdentifier": item["bundleIdentifier"]}
        for item in bundle_metadata
        if item["bundleIdentifier"]
    ]
    embedded_frameworks = []
    metadata_by_path = {item["path"]: item for item in bundle_metadata}
    macho_by_path = {item["path"]: item for item in macho_binaries}
    for framework_path in framework_paths:
        metadata = metadata_by_path.get(f"{framework_path}/Info.plist", {})
        binary_path = None
        executable_name = metadata.get("bundleExecutable")
        if executable_name and f"{framework_path}/{executable_name}" in macho_by_path:
            binary_path = f"{framework_path}/{executable_name}"
        embedded_frameworks.append(
            {
                "path": framework_path,
                "bundleIdentifier": metadata.get("bundleIdentifier"),
                "bundleExecutable": executable_name,
                "binary": binary_path,
                "architectures": macho_by_path.get(binary_path, {}).get("architectures", [])
                if binary_path
                else [],
                "classification": "EXISTING_OVERLAY"
                if framework_path == OVERLAY
                else "ORIGINAL_GAME",
            }
        )

    overlay_entries = [item["path"] for item in entries if item["category"] == "EXISTING_OVERLAY"]
    i3rby_markers = sorted(
        marker.decode("ascii", "replace") for marker in set(I3RBY_MARKER.findall(overlay_data))
    )
    info_selected_keys = (
        "CFBundleIdentifier",
        "CFBundleDisplayName",
        "CFBundleName",
        "CFBundleExecutable",
        "CFBundlePackageType",
        "CFBundleShortVersionString",
        "CFBundleVersion",
        "CFBundleSupportedPlatforms",
        "MinimumOSVersion",
        "AppID",
        "DecryptedBy",
        "NSUserTrackingUsageDescription",
    )
    extension_summary = [
        {
            "extension": suffix,
            "files": extension_counts[suffix],
            "uncompressedBytes": extension_bytes[suffix],
        }
        for suffix in sorted(extension_counts)
    ]

    report = {
        "schemaVersion": 2,
        "artifact": {
            "path": ipa.name,
            "sizeBytes": ipa.stat().st_size,
            "sha256": file_sha256(ipa),
            "zipEntries": len(entries),
            "zipFiles": sum(not item["directory"] for item in entries),
            "zipDirectories": sum(item["directory"] for item in entries),
            "uncompressedBytes": sum(item["sizeBytes"] for item in entries),
            "preservation": "tracked source artifact; inspected read-only",
        },
        "payload": "Payload/",
        "applicationBundle": APP,
        "application": {
            "bundleIdentifier": info.get("CFBundleIdentifier"),
            "displayName": info.get("CFBundleDisplayName"),
            "version": info.get("CFBundleShortVersionString"),
            "build": info.get("CFBundleVersion"),
            "mainExecutable": executable,
            "mainExecutableClassification": "UNKNOWN",
            "mainExecutableClassificationReason": "original game executable with an added load command for the injected overlay",
            "macho": executable_macho,
        },
        "applicationInfoPlist": {
            "path": INFO_PLIST,
            "sha256": digests[INFO_PLIST],
            "format": "binary" if info_data.startswith(b"bplist00") else "xml",
            "keyCount": len(info),
            "keys": sorted(info),
            "selectedValues": {key: info.get(key) for key in info_selected_keys if key in info},
            "modificationIndicators": {
                "decryptionWatermark": info.get("DecryptedBy"),
                "trackingDescription": info.get("NSUserTrackingUsageDescription"),
            },
        },
        "frameworkDirectoryEntries": framework_directory_entries,
        "frameworks": framework_names,
        "embeddedFrameworks": embedded_frameworks,
        "standaloneDylibs": dylibs,
        "appExtensions": app_extensions,
        "resourceBundles": resource_bundles,
        "localizationDirectories": localizations,
        "resources": {
            "fileCount": sum(extension_counts.values()),
            "extensionSummary": extension_summary,
        },
        "bundleIdentifiers": bundle_identifiers,
        "bundleMetadata": bundle_metadata,
        "machOBinaries": macho_binaries,
        "architectureSummary": {
            "machOBinaryCount": len(macho_binaries),
            "architectureSets": dict(
                sorted(Counter(",".join(item["architectures"]) for item in macho_binaries).items())
            ),
        },
        "overlay": {
            "framework": OVERLAY,
            "binary": overlay_binary,
            "macho": overlay_macho,
        },
        "existingI3rbyModification": {
            "attribution": "HIGH: the injected binary contains com.i3rby.* persistent-domain markers and the host executable loads that binary",
            "ownedMembers": overlay_entries,
            "i3rbyMarkers": i3rby_markers,
            "hostLoadReference": "@executable_path/Frameworks/libloader.framework/libloader",
            "mixedOrPostInjectionMembers": [
                {
                    "path": executable,
                    "reason": "mixed host executable with injected LC_LOAD_DYLIB; the entire executable is not attributed to i3rby",
                },
                {
                    "path": INFO_PLIST,
                    "reason": "host metadata contains redistribution and overlay licensing changes",
                },
                {
                    "path": f"{APP}/_CodeSignature/",
                    "reason": "post-injection signature metadata directory",
                },
                {
                    "path": f"{APP}/_CodeSignature/CodeResources",
                    "reason": "post-injection signature manifest covers libloader.framework",
                },
                {
                    "path": f"{APP}/SC_Info/",
                    "reason": "FairPlay metadata location reduced to a redistribution placeholder",
                },
                {
                    "path": f"{APP}/SC_Info/.keep",
                    "reason": "redistribution placeholder; not attributed to pristine host content",
                },
            ],
            "boundary": "Only libloader.framework members are classified as wholly owned by the existing overlay. Mixed host files remain UNKNOWN rather than being over-attributed.",
        },
        "classificationSummary": {
            category: {
                "entries": category_counts[category],
                "uncompressedBytes": category_bytes[category],
            }
            for category in ("ORIGINAL_GAME", "EXISTING_OVERLAY", "UNKNOWN")
        },
        "classificationCaveat": "ORIGINAL_GAME means structurally attributable to the host bundle and outside the injected overlay. It does not assert provenance or untampered bytes. Mixed/post-injection components are UNKNOWN.",
        "entries": entries,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
