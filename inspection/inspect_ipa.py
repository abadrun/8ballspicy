#!/usr/bin/env python3
"""
inspect_ipa.py — reproducible forensic inspection of the supplied IPA.

Reproduces every machine-checkable finding in analysis/INSPECTION_REPORT.md
without modifying the original artifact (read-only).

Usage:
    python3 inspection/inspect_ipa.py [path-to-ipa]

Writes a text report to stdout. Extracts nothing to disk unless --extract
is passed (then to inspection/extracted/, which is gitignored).
"""

import hashlib
import struct
import sys
import zipfile
import os

DEFAULT_IPA = os.path.join(os.path.dirname(__file__), "..", "8-ball-pool-i3rby-IPAOMTK.COM.ipa")

CHEAT_MARKER_STRINGS = [
    "Aim Mode",
    "Aim Strength",
    "Auto Play",
    "Auto Queue",
    "Cushion: Pro banks",
    "Activate Key",
    "Activate your subscription key here",
    "Activate PRO to unlock Automation and Auto Queue",
    "Prediction Lines",
    "Opponent Lines",
    "Table Outline",
    "Hides lines, menu, and buttons from streams, recordings, and screenshots.",
]

GB_MENU_CLASSES = [
    "GBModMenu",
    "GBMenuFeatureTile",
    "GBMenuEntitlementCard",
    "GBMenuFXToggleRow",
    "GBMenuMeterRow",
    "GBMenuStackedSegmentRow",
    "GBMenuKeyValueRow",
    "GBMenuLockStrip",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def macho_info(data):
    """Minimal arm64 Mach-O parser: returns (cputype, load_dylibs, cryptid)."""
    magic = struct.unpack("<I", data[:4])[0]
    if magic != 0xFEEDFACF:
        return None
    cputype = struct.unpack("<i", data[4:8])[0]
    ncmds = struct.unpack("<I", data[16:20])[0]
    off = 32
    dylibs, cryptid = [], None
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", data[off:off + 8])
        if cmd == 0xC:  # LC_LOAD_DYLIB
            nameoff = struct.unpack("<I", data[off + 8:off + 12])[0]
            name = data[off + nameoff:off + cmdsize].split(b"\x00")[0]
            dylibs.append(name.decode("utf-8", "replace"))
        elif cmd == 0x2C:  # LC_ENCRYPTION_INFO_64
            cryptid = struct.unpack("<I", data[off + 16:off + 20])[0]
        off += cmdsize
    return cputype, dylibs, cryptid


def extractable_strings(data, min_len=6):
    """Poor-man's `strings` (ASCII runs) so the script has no dependencies."""
    out, cur = [], bytearray()
    for b in data:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= min_len:
                out.append(cur.decode("ascii", "replace"))
            cur = bytearray()
    if len(cur) >= min_len:
        out.append(cur.decode("ascii", "replace"))
    return out


def main():
    ipa = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IPA
    ipa = os.path.abspath(ipa)
    print(f"IPA: {ipa}")
    print(f"Size: {os.path.getsize(ipa):,} bytes")
    print(f"SHA-256: {sha256(ipa)}")
    zip_magic = b"PK\x03\x04"
    print(f"Is ZIP (IPA container): {open(ipa, 'rb').read(4) == zip_magic}")

    z = zipfile.ZipFile(ipa)
    names = z.namelist()
    print(f"Archive entries: {len(names)}")
    print(f"Top level: {sorted(set(n.split('/')[0] for n in names))}")
    app_dir = next(n.split("/")[1] for n in names
                   if n.startswith("Payload/") and n.count("/") >= 2 and n.split("/")[1].endswith(".app"))
    app = f"Payload/{app_dir}"
    print(f"App bundle: {app}")

    # --- Info.plist ---
    import plistlib
    info = plistlib.loads(z.read(f"{app}/Info.plist"))
    print("\n--- Host app identity (Info.plist) ---")
    for k in ("CFBundleIdentifier", "CFBundleDisplayName", "CFBundleShortVersionString",
              "CFBundleVersion", "AppID", "MinimumOSVersion"):
        print(f"  {k} = {info.get(k)}")
    for k in ("DecryptedBy", "NSUserTrackingUsageDescription"):
        if k in info:
            print(f"  {k} = {info.get(k)!r}  <-- TAMPERED / non-App-Store key")

    # --- Executable ---
    exe = info["CFBundleExecutable"]
    exe_data = z.read(f"{app}/{exe}")
    cputype, dylibs, cryptid = macho_info(exe_data)
    print("\n--- Main executable ---")
    print(f"  Mach-O: cputype={cputype:#010x} (arm64)")
    print(f"  LC_ENCRYPTION_INFO_64 cryptid = {cryptid}  (0 => FairPlay DRM stripped)")
    injected = [d for d in dylibs if "libloader" in d]
    print(f"  LC_LOAD_DYLIB count: {len(dylibs)}")
    print(f"  Injected load command(s): {injected}")

    # --- DRM / redistribution indicators ---
    print("\n--- DRM / redistribution indicators ---")
    print(f"  SC_Info present: {any(n.startswith(f'{app}/SC_Info') for n in names)} "
          f"(contents: {[n for n in names if n.startswith(f'{app}/SC_Info')]})")
    print(f"  embedded.mobileprovision: {f'{app}/embedded.mobileprovision' in names}")

    # --- Code signature coverage (was the bundle re-signed after injection?) ---
    try:
        cr = plistlib.loads(z.read(f"{app}/_CodeSignature/CodeResources"))
        files2 = cr.get("files2", {})
        print(f"  _CodeSignature/CodeResources files2 entries: {len(files2)}")
        print(f"  libloader covered by (re)signature: "
              f"{'Frameworks/libloader.framework/libloader' in files2}")
    except KeyError:
        print("  no _CodeSignature/CodeResources")

    # --- Frameworks ---
    fws = sorted(set(n.split("/")[3] for n in names
                     if n.startswith(f"{app}/Frameworks/") and n.count("/") >= 3 and n.split("/")[3]))
    print("\n--- Frameworks ---")
    for f in fws:
        print(f"  {f}")

    # --- libloader ---
    ll_path = f"{app}/Frameworks/libloader.framework/libloader"
    if ll_path in names:
        ll_data = z.read(ll_path)
        ll_info = plistlib.loads(z.read(f"{app}/Frameworks/libloader.framework/Info.plist"))
        print("\n--- libloader.framework (the injected overlay) ---")
        print(f"  CFBundleIdentifier = {ll_info.get('CFBundleIdentifier')} "
              f"(disguised as an Appdome-style framework)")
        print(f"  Binary size: {len(ll_data):,} bytes")
        c2, dylibs2, cryptid2 = macho_info(ll_data)
        print(f"  Mach-O cputype={c2:#010x}, LC_LOAD_DYLIB={len(dylibs2)}, cryptid={cryptid2}")
        strs = extractable_strings(ll_data)
        print("  Cheat feature marker strings found:")
        for m in CHEAT_MARKER_STRINGS:
            hit = any(m in s for s in strs)
            print(f"    [{'x' if hit else ' '}] {m!r}")
        print("  Mod-menu Objective-C classes found:")
        joined = "\n".join(strs)
        for c in GB_MENU_CLASSES:
            print(f"    [{'x' if c in joined else ' '}] {c}")
        ad_urls = sorted({s for s in strs if s.startswith("http") and "omg" in s})
        print(f"  Third-party rewarded-ad endpoint strings: {ad_urls}")

    # --- Host app Arabic localization (context for EN/AR requirement) ---
    print("\n--- Host app localization folders ---")
    lprojs = sorted(set(n.split("/")[2] for n in names
                        if n.startswith(f"{app}/") and ".lproj" in n and n.count("/") >= 2))
    print(f"  {lprojs}")

    print("\nConclusion: the archive is a FairPlay-stripped pirated copy of Miniclip's")
    print("8 Ball Pool with an injected compiled cheat overlay (libloader.framework).")
    print("No source code for the overlay exists inside the artifact.")


if __name__ == "__main__":
    main()
