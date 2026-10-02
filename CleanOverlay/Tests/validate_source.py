#!/usr/bin/env python3
"""Structural checks usable when Xcode/Swift are unavailable."""
from pathlib import Path
import plistlib
import re

root = Path(__file__).resolve().parents[1]
swift = list((root / "Sources").rglob("*.swift"))
assert swift, "no Swift sources"
assert (root / "Package.swift").is_file()
assert (root / "Tests/CleanOverlayCoreTests/OverlaySettingsTests.swift").is_file()
plistlib.load(open(root / "Configuration/Info.plist", "rb"))


def strings(path: Path) -> set[str]:
    return set(re.findall(r'^"([^"]+)"\s*=', path.read_text(), re.M))

en = strings(root / "Sources/CleanOverlayUI/Resources/en.lproj/Localizable.strings")
id_ = strings(root / "Sources/CleanOverlayUI/Resources/id.lproj/Localizable.strings")
assert en == id_, f"localization mismatch: en-only={en-id_}, id-only={id_-en}"

source_text = "\n".join(path.read_text() for path in swift)
for token in ["WebKit", "StoreKit", "AdSupport", "URLSession", "WKWebView",
              "Auto Play", "Auto Queue", "Aim Strength", "Prediction Lines",
              "subscription key", "screen capture"]:
    assert token not in source_text, f"excluded token in Swift source: {token}"

for path in swift:
    text = path.read_text()
    assert text.count("{") == text.count("}"), f"brace mismatch: {path}"
    assert text.count("(") == text.count(")"), f"parenthesis mismatch: {path}"

print(f"OK: {len(swift)} Swift files, {len(en)} localized keys in 2 locales")
