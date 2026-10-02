#!/usr/bin/env python3
"""Create a complete, read-only inventory of the existing IPA.

Every ZIP member is listed and classified as ORIGINAL_GAME, EXISTING_OVERLAY,
or UNKNOWN. UNKNOWN is used for mixed/tampered components rather than guessing.
The script never extracts or modifies the archive.
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IPA = ROOT / "8-ball-pool-i3rby-IPAOMTK.COM.ipa"
APP = "Payload/pool.app"
OVERLAY = f"{APP}/Frameworks/libloader.framework"


def file_sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def member_sha256(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str | None:
    if info.is_dir():
        return None
    result = hashlib.sha256()
    with archive.open(info) as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def macho(data: bytes) -> dict:
    if len(data) < 32 or struct.unpack_from("<I", data)[0] != 0xFEEDFACF:
        return {"recognized": False}
    cpu = struct.unpack_from("<i", data, 4)[0]
    count = struct.unpack_from("<I", data, 16)[0]
    offset, libraries, cryptid = 32, [], None
    for _ in range(count):
        command, size = struct.unpack_from("<II", data, offset)
        if command == 0xC:
            name_offset = struct.unpack_from("<I", data, offset + 8)[0]
            name = data[offset + name_offset:offset + size].split(b"\0", 1)[0]
            libraries.append(name.decode("utf-8", "replace"))
        elif command == 0x2C:
            cryptid = struct.unpack_from("<I", data, offset + 16)[0]
        offset += size
    return {"recognized": True, "cpuType": cpu, "cryptid": cryptid,
            "loadDylibs": libraries, "loadDylibCount": len(libraries)}


def classify(path: str) -> tuple[str, str]:
    if path.startswith(OVERLAY + "/") or path == OVERLAY:
        return "EXISTING_OVERLAY", "member of the injected libloader.framework bundle"
    if path in {f"{APP}/pool", f"{APP}/Info.plist"}:
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


def main() -> None:
    ipa = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_IPA
    with zipfile.ZipFile(ipa) as archive:
        names = archive.namelist()
        info = plistlib.loads(archive.read(f"{APP}/Info.plist"))
        executable = f"{APP}/{info['CFBundleExecutable']}"
        executable_macho = macho(archive.read(executable))
        overlay_macho = macho(archive.read(f"{OVERLAY}/libloader"))
        entries = []
        category_counts: Counter[str] = Counter()
        category_bytes: Counter[str] = Counter()
        for item in archive.infolist():
            category, reason = classify(item.filename)
            category_counts[category] += 1
            category_bytes[category] += item.file_size
            entries.append({
                "path": item.filename,
                "category": category,
                "classificationReason": reason,
                "directory": item.is_dir(),
                "sizeBytes": item.file_size,
                "compressedSizeBytes": item.compress_size,
                "crc32": f"{item.CRC:08x}",
                "sha256": member_sha256(archive, item),
            })

    frameworks = sorted({p.split("/")[3] for p in names
                         if p.startswith(f"{APP}/Frameworks/") and len(p.split("/")) > 3 and p.split("/")[3]})
    localizations = sorted({p.split("/")[2] for p in names
                            if p.startswith(f"{APP}/") and len(p.split("/")) > 2 and p.split("/")[2].endswith(".lproj")})
    dylibs = sorted(p for p in names if p.startswith(f"{APP}/Frameworks/") and p.endswith(".dylib"))
    report = {
        "artifact": {
            "path": ipa.name,
            "sizeBytes": ipa.stat().st_size,
            "sha256": file_sha256(ipa),
            "zipEntries": len(entries),
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
        "frameworks": frameworks,
        "standaloneDylibs": dylibs,
        "localizationDirectories": localizations,
        "overlay": {
            "framework": OVERLAY,
            "binary": f"{OVERLAY}/libloader",
            "macho": overlay_macho,
        },
        "classificationSummary": {
            category: {"entries": category_counts[category], "uncompressedBytes": category_bytes[category]}
            for category in ("ORIGINAL_GAME", "EXISTING_OVERLAY", "UNKNOWN")
        },
        "classificationCaveat": "ORIGINAL_GAME means structurally attributable to the host bundle and outside the injected overlay. It does not assert provenance or untampered bytes. Mixed/tampered components are UNKNOWN.",
        "entries": entries,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
