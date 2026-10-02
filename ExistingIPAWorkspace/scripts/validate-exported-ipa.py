#!/usr/bin/env python3
"""Validate a real exported IPA structurally and print its SHA-256.

This tool never creates or modifies an IPA. It exits nonzero on any failed check.
"""
from __future__ import annotations

import argparse
import hashlib
import plistlib
import sys
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ipa", type=Path)
    parser.add_argument("--require-signature", action="store_true")
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
        apps = sorted({"/".join(name.split("/")[:2]) for name in names
                       if name.startswith("Payload/") and len(name.split("/")) > 1
                       and name.split("/")[1].endswith(".app")})
        if len(apps) != 1:
            fail(f"expected one Payload app bundle, found {len(apps)}")
        app = apps[0]
        plist_path = f"{app}/Info.plist"
        if plist_path not in names:
            fail("application Info.plist is missing")
        info = plistlib.loads(archive.read(plist_path))
        bundle_id = info.get("CFBundleIdentifier")
        executable = info.get("CFBundleExecutable")
        if not bundle_id or not executable:
            fail("bundle identifier or executable metadata is missing")
        if args.bundle_id and bundle_id != args.bundle_id:
            fail(f"bundle id {bundle_id!r} does not match required {args.bundle_id!r}")
        executable_path = f"{app}/{executable}"
        if executable_path not in names:
            fail(f"main executable is missing: {executable_path}")
        magic = archive.read(executable_path)[:4]
        if magic not in {b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"}:
            fail(f"main executable has unexpected Mach-O magic {magic.hex()}")
        code_resources = f"{app}/_CodeSignature/CodeResources"
        if args.require_signature and code_resources not in names:
            fail("CodeResources is missing from signed export")

    print("VALID")
    print(f"file={ipa}")
    print(f"sizeBytes={ipa.stat().st_size}")
    print(f"bundleIdentifier={bundle_id}")
    print(f"sha256={sha256(ipa)}")


if __name__ == "__main__":
    main()
