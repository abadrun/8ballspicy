#!/usr/bin/env python3
"""Read-only inventory of the injected overlay contained in the supplied IPA.

The script does not extract, patch, or rewrite the IPA. It reports only facts that
can be established from ZIP metadata, plists, Mach-O load commands, and printable
strings in the framework binary.
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
import struct
import sys
import zipfile
from pathlib import Path

DEFAULT_IPA = Path(__file__).resolve().parents[1] / "8-ball-pool-i3rby-IPAOMTK.COM.ipa"
APP = "Payload/pool.app"
OVERLAY = f"{APP}/Frameworks/libloader.framework"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ascii_strings(data: bytes, minimum: int = 4) -> list[str]:
    return [m.group().decode("ascii", "replace") for m in re.finditer(rb"[ -~]{%d,}" % minimum, data)]


def macho(data: bytes) -> dict:
    if len(data) < 32 or struct.unpack_from("<I", data)[0] != 0xFEEDFACF:
        return {"recognized": False}
    cpu = struct.unpack_from("<i", data, 4)[0]
    commands = struct.unpack_from("<I", data, 16)[0]
    offset, dylibs, cryptid = 32, [], None
    for _ in range(commands):
        command, size = struct.unpack_from("<II", data, offset)
        if command == 0xC:
            name_offset = struct.unpack_from("<I", data, offset + 8)[0]
            raw = data[offset + name_offset:offset + size].split(b"\0", 1)[0]
            dylibs.append(raw.decode("utf-8", "replace"))
        elif command == 0x2C:
            cryptid = struct.unpack_from("<I", data, offset + 16)[0]
        offset += size
    return {"recognized": True, "cpuType": cpu, "loadCommandCount": commands,
            "linkedLibraries": dylibs, "cryptid": cryptid}


def main() -> None:
    ipa = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IPA
    with zipfile.ZipFile(ipa) as archive:
        names = archive.namelist()
        app_info = plistlib.loads(archive.read(f"{APP}/Info.plist"))
        framework_info = plistlib.loads(archive.read(f"{OVERLAY}/Info.plist"))
        binary_path = f"{OVERLAY}/libloader"
        binary = archive.read(binary_path)
        strings = sorted(set(ascii_strings(binary)))

    menu_classes = sorted({name for value in strings for name in re.findall(r"GB[A-Z][A-Za-z]+", value)})
    state_record = next((s for s in strings if s.startswith('{?="predictionLines"')), None)
    state_fields = re.findall(r'"([A-Za-z][A-Za-z0-9]+)"[BqifdQ]', state_record or "")
    localization_keys = sorted({s for s in strings if re.fullmatch(
        r"(?:access|account|alert|faq|feature|menu|overlay|tab)\.[A-Za-z0-9_.]+", s)})
    urls = sorted({s for s in strings if s.startswith(("http://", "https://"))})
    markers = [
        "Aim Mode", "Aim Strength", "Auto Play", "Auto Queue", "Prediction Lines",
        "Opponent Lines", "Table Outline", "Pocket Rings", "Break % Overlay",
        "Activate Key", "PRO Subscription", "Watch an ad for +1h", "Stream Proof",
    ]
    report = {
        "source": {"path": ipa.name, "sizeBytes": ipa.stat().st_size,
                   "sha256": digest(ipa.read_bytes()), "archiveEntries": len(names)},
        "originalGame": {
            "bundleIdentifier": app_info.get("CFBundleIdentifier"),
            "displayName": app_info.get("CFBundleDisplayName"),
            "shortVersion": app_info.get("CFBundleShortVersionString"),
            "buildVersion": app_info.get("CFBundleVersion"),
            "executable": app_info.get("CFBundleExecutable"),
        },
        "overlay": {
            "frameworkPath": OVERLAY,
            "binaryPath": binary_path,
            "binarySizeBytes": len(binary),
            "binarySha256": digest(binary),
            "bundleMetadata": framework_info,
            "macho": macho(binary),
            "bundleFiles": sorted(n for n in names if n.startswith(OVERLAY + "/")),
            "menuClasses": menu_classes,
            "localizationKeys": localization_keys,
            "stateFields": state_fields,
            "featureMarkersPresent": [m for m in markers if any(m in s for s in strings)],
            "urls": urls,
            "sourceFilesPresent": any(
                n.startswith(OVERLAY + "/") and Path(n).suffix.lower() in {".m", ".mm", ".h", ".swift", ".c", ".cc", ".cpp"}
                for n in names
            ),
        },
        "unknown": [
            "Exact visual measurements and colors cannot be established from static strings alone.",
            "Obfuscated class ownership and call graph cannot be established without symbols/source.",
            "Server behavior and runtime state transitions were not exercised.",
            "Printable translated text exists, but complete key-to-value locale mapping is not recoverable with confidence.",
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
