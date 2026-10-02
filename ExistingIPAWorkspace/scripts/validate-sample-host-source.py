#!/usr/bin/env python3
"""Validate the clean sample host's source-level package integration contract."""
from __future__ import annotations

import plistlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOST = ROOT / "ExistingIPAWorkspace" / "SampleHost"
PROJECT = HOST / "ExistingIPAOverlaySampleHost.xcodeproj" / "project.pbxproj"
SCHEME = HOST / "ExistingIPAOverlaySampleHost.xcodeproj" / "xcshareddata" / "xcschemes" / "ExistingIPAOverlaySampleHost.xcscheme"
APP = HOST / "Sources" / "SampleHostApp.swift"
ROOT_VIEW = HOST / "Sources" / "SampleHostRootView.swift"
PLIST = HOST / "Resources" / "Info.plist"

for path in (PROJECT, SCHEME, APP, ROOT_VIEW, PLIST):
    if not path.is_file():
        raise SystemExit(f"INVALID: missing sample-host file: {path.relative_to(ROOT)}")

project = PROJECT.read_text()
source = APP.read_text() + "\n" + ROOT_VIEW.read_text()
info = plistlib.loads(PLIST.read_bytes())

required_project_tokens = (
    "XCLocalSwiftPackageReference",
    "relativePath = ../OverlaySource;",
    "XCSwiftPackageProductDependency",
    "productName = ExistingIPAOverlay;",
    "ExistingIPAOverlay in Frameworks",
    "isa = PBXFrameworksBuildPhase;",
    "IPHONEOS_DEPLOYMENT_TARGET = 16.0;",
    "SUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";",
)
for token in required_project_tokens:
    if token not in project:
        raise SystemExit(f"INVALID: sample project is missing {token!r}")

build_file = re.search(
    r"([A-F0-9]{24}) /\* ExistingIPAOverlay in Frameworks \*/ = \{isa = PBXBuildFile; productRef = ([A-F0-9]{24})",
    project,
)
if not build_file:
    raise SystemExit("INVALID: sample host does not link the package product with PBXBuildFile")
framework_phase = re.search(r"isa = PBXFrameworksBuildPhase;.*?files = \((.*?)\);", project, re.S)
if not framework_phase or build_file.group(1) not in framework_phase.group(1):
    raise SystemExit("INVALID: package PBXBuildFile is absent from the Frameworks build phase")

if not re.search(r"(?m)^import ExistingIPAOverlayUI$", source):
    raise SystemExit("INVALID: sample source does not import ExistingIPAOverlayUI")
if not re.search(r"ExistingIPAOverlayView\s*\(", source):
    raise SystemExit("INVALID: sample source does not construct ExistingIPAOverlayView")
if "@main" not in source or ": App" not in source:
    raise SystemExit("INVALID: sample source has no SwiftUI app entry point")

for prohibited in ("libloader", "dlopen", "MSHook", "fishhook", "URLSession", "WebKit", "StoreKit", "AdSupport"):
    if prohibited in source or prohibited in project:
        raise SystemExit(f"INVALID: prohibited sample-host token: {prohibited}")

if info.get("CFBundlePackageType") != "APPL":
    raise SystemExit("INVALID: sample Info.plist package type is not APPL")
if info.get("CFBundleIdentifier") != "$(PRODUCT_BUNDLE_IDENTIFIER)":
    raise SystemExit("INVALID: sample Info.plist does not use the target bundle identifier")

print("VALID")
print("host=ExistingIPAOverlaySampleHost")
print("packageProduct=ExistingIPAOverlay")
print("swiftModule=ExistingIPAOverlayUI")
print("entryPoint=ExistingIPAOverlayView")
print("minimumIOS=16.0")
