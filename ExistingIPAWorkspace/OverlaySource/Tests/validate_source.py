#!/usr/bin/env python3
"""Dependency-free package, localization, and prohibited-capability checks."""
from __future__ import annotations

import json
from pathlib import Path
import plistlib
import re

root = Path(__file__).resolve().parents[1]
source_files = sorted((root / "Sources").rglob("*.swift"))
test_files = sorted((root / "Tests").rglob("*.swift"))
assert source_files, "no Swift sources"
assert test_files, "no Swift tests"

manifest = (root / "Package.swift").read_text()
assert "// swift-tools-version: 5.9" in manifest
assert ".iOS(.v16)" in manifest
assert '.library(name: "ExistingIPAOverlay"' in manifest
assert '.testTarget(name: "ExistingIPAOverlayCoreTests"' in manifest
assert 'name: "ExistingIPAOverlayUITests"' in manifest
assert ".package(" not in manifest, "external package dependency introduced"

plistlib.load(open(root / "Configuration/ResourceBundleInfo.reference.plist", "rb"))
for config in ("Debug.xcconfig", "Release.xcconfig"):
    text = (root / "Configuration" / config).read_text()
    assert "IPHONEOS_DEPLOYMENT_TARGET = 16.0" in text, f"wrong deployment target in {config}"
    assert "SWIFT_VERSION = 5.9" in text, f"wrong Swift version in {config}"


def strings(path: Path) -> dict[str, str]:
    pairs = re.findall(r'^"([^"]+)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', path.read_text(), re.M)
    return dict(pairs)


en = strings(root / "Sources/ExistingIPAOverlayUI/Resources/en.lproj/Localizable.strings")
id_ = strings(root / "Sources/ExistingIPAOverlayUI/Resources/id.lproj/Localizable.strings")
assert en.keys() == id_.keys(), f"localization mismatch: en-only={en.keys()-id_.keys()}, id-only={id_.keys()-en.keys()}"
assert all(value.strip() for value in en.values()), "empty English localization"
assert all(value.strip() for value in id_.values()), "empty Indonesian localization"
assert len(en) == 46, f"unexpected localization key count: {len(en)}"

ui_text = "\n".join(
    path.read_text() for path in source_files if "ExistingIPAOverlayUI" in path.parts
)
literal_keys = {
    key for key in re.findall(r'\bt\("([^"]+)"\)', ui_text)
    if "\\(" not in key
}
literal_keys.update(f"section.{name}" for name in ("overview", "appearance", "preferences", "language", "about"))
assert literal_keys <= en.keys(), f"UI references missing localization keys: {literal_keys-en.keys()}"

asset_contents = root / "Sources/ExistingIPAOverlayUI/Resources/Media.xcassets/Contents.json"
accent_contents = root / "Sources/ExistingIPAOverlayUI/Resources/Media.xcassets/OverlayAccent.colorset/Contents.json"
json.loads(asset_contents.read_text())
json.loads(accent_contents.read_text())

allowed_imports = {
    "ExistingIPAOverlayCore": {"Foundation"},
    "ExistingIPAOverlayUI": {"Foundation", "SwiftUI", "ExistingIPAOverlayCore"},
}
for path in source_files:
    target = next(part for part in path.parts if part in allowed_imports)
    imports = set(re.findall(r"(?m)^import\s+([A-Za-z0-9_]+)\s*$", path.read_text()))
    assert imports <= allowed_imports[target], f"unexpected imports in {path}: {imports-allowed_imports[target]}"

source_text = "\n".join(path.read_text() for path in source_files)
for pattern in (
    r"\bURLSession\b", r"\bNSURLSession\b", r"\bWKWebView\b", r"\bWebKit\b",
    r"\bStoreKit\b", r"\bSKPayment", r"\bAdSupport\b", r"\bASIdentifierManager\b",
    r"\bAppTrackingTransparency\b", r"\bATTrackingManager\b", r"\bNetwork\b",
    r"\bNWConnection\b", r"\bCFStream\b", r"\bsocket\s*\(", r"https?://",
    r"\bGameKit\b", r"\bGKMatch\b", r"\bAVCapture", r"\bReplayKit\b",
):
    assert not re.search(pattern, source_text), f"prohibited capability pattern in component source: {pattern}"

for path in source_files + test_files:
    text = path.read_text()
    assert text.count("{") == text.count("}"), f"brace mismatch: {path}"
    assert text.count("(") == text.count(")"), f"parenthesis mismatch: {path}"

print(
    f"OK: {len(source_files)} source files, {len(test_files)} Swift test files, "
    f"{len(en)} localized keys in 2 locales, no external/prohibited capabilities"
)
