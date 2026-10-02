# ExistingIPAOverlay component readiness — 2026-10-02

## Result

Artifact A and the previously accepted Artifact B were not modified. This verification produced additional reproducible Simulator and device component archives in GitHub Actions; neither archive is an IPA. Artifact C was not created.

- Workflow run: [`37018507081`](https://github.com/abadrun/8ballspicy/actions/runs/37018507081)
- Job: `110875251387`
- Tested commit: `26755b1f2c8c693ff21673cf3ac3231e3564de5f`
- Runner: `macos-15`
- Result: **PASS**
- Reproducible-build artifact: `ExistingIPAOverlay-reproducible-builds` (Actions artifact `11231528753`)
- Test-evidence artifact: `ExistingIPAOverlay-test-evidence` (Actions artifact `11231253906`)

## Canonical reproducible component hashes

| Target | Archive | SHA-256 |
|---|---|---|
| iOS Simulator | `ExistingIPAOverlay-ios-simulator-reproducible.zip` | `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5` |
| iPhoneOS arm64 | `ExistingIPAOverlay-ios-device-reproducible.zip` | `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f` |

The workflow built the complete package twice from clean DerivedData, normalized ZIP timestamps, permissions, names, ordering, and compression, then compared both ZIPs and their member manifests byte-for-byte. Both comparisons passed. `.swiftsourceinfo` is deliberately omitted because it is volatile Xcode IDE indexing metadata rather than a compile, link, resource, or runtime input; the distributable `.swiftmodule`, `.swiftdoc`, ABI metadata, object products, and resource bundle remain included.

The accepted device component at `output/ExistingIPAOverlay-ios-device-build.zip` remains unchanged at SHA-256 `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`. It is distinct from the newer canonical reproducible device archive above.

## Verification performed

The successful workflow completed all of these gates:

1. Dependency-free source, resource, localization, and prohibited-capability validation.
2. Native Swift package build and all 17 Core/UI test methods.
3. The same package tests against a booted iOS Simulator, including SwiftUI body evaluation and `UIHostingController` appearance lifecycle.
4. Clean sample-host Simulator build, package/resource validation, installation, launch, and termination.
5. Clean sample-host generic iPhoneOS arm64 build and validation.
6. iOS 16 deployment-target verification from Xcode build settings and built app/resource metadata.
7. Two independent Simulator and iPhoneOS component builds.
8. Byte-for-byte archive and per-member-manifest comparison.
9. Independent canonical Simulator/device archive validators.
10. Evidence and component artifact upload.

Coverage includes settings defaults and normalization, Codable round trips, malformed data handling, storage-key isolation, isolated real `UserDefaults`, EN/ID key parity and lookup, missing-key fallback, resource-bundle color lookup, view-model load/save/reset, expansion and reduced-motion state, SwiftUI body construction, and hosting-controller lifecycle.

The static policy validator confirms no external Swift package dependencies and no source references to networking, URL loading, WebKit, sockets, Network framework, advertising/tracking, StoreKit/payment, licensing/activation, GameKit/gameplay automation, screen capture/replay, hooking, or `libloader`. Component persistence is confined to local `UserDefaults` key `ExistingIPAOverlay.settings.v1`.

## Exact authorized-host consumption procedure

These steps are for an authorized source-level host only; they do not patch or inject into Artifact A.

1. Supply the authorized production app's `.xcodeproj` or `.xcworkspace`, app target, and shared scheme. The app deployment target must be iOS 16.0 or newer.
2. Add local package path `ExistingIPAWorkspace/OverlaySource` and package product `ExistingIPAOverlay` to the app target's Frameworks build phase. For a conventional project, the repository tool can validate first and then apply the linkage:

   ```bash
   python3 ExistingIPAWorkspace/scripts/configure-authorized-host-package.py \
     --project /absolute/path/AuthorizedHost.xcodeproj \
     --target AuthorizedHost \
     --package-path "$PWD/ExistingIPAWorkspace/OverlaySource"

   python3 ExistingIPAWorkspace/scripts/configure-authorized-host-package.py \
     --project /absolute/path/AuthorizedHost.xcodeproj \
     --target AuthorizedHost \
     --package-path "$PWD/ExistingIPAWorkspace/OverlaySource" \
     --apply
   ```

3. In a host-owned source file that belongs to the app target, import the module and present the view at an owner-approved location:

   ```swift
   import ExistingIPAOverlayUI
   import SwiftUI

   struct AuthorizedOverlayPresentation: View {
       var body: some View {
           ExistingIPAOverlayView()
       }
   }
   ```

4. Resolve packages, run the host's tests on an iOS Simulator, and build generic iPhoneOS. SwiftPM statically links the product and copies `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` to the app.
5. If and only if legitimate signing/provisioning and export inputs are present, follow `ExistingIPAWorkspace/FINAL_BUILD_RUNBOOK.md`. Preserve any authorized baseline behavior only through owner-provided source and permission; do not patch, inject, hook, bypass controls, or modify `libloader`.

The repository's clean sample host proves this consumption path but is intentionally not Artifact C and is not a substitute for the authorized production host.

## Required status

- `COMPONENT STATUS: READY`
- `CORE TESTS: PASS`
- `UI TESTS: PASS`
- `SIMULATOR BUILD: PASS`
- `DEVICE BUILD: PASS`
- `RESOURCE BUNDLE: PASS`
- `LOCALIZATION: PASS`
- `PERSISTENCE: PASS`
- `PACKAGE INTEGRATION TEST: PASS`
- `COMPONENT SHA-256: 3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f`
- `HOST INTEGRATION: BLOCKED — AUTHORIZED HOST PROJECT REQUIRED`
- `FINAL IPA: NOT PRODUCED`
- `SINGLE REMAINING HOST REQUIREMENT: Supply the authorized production app Xcode project/workspace and app target, with an owner-approved presentation point and lawful source-level permission for required baseline coexistence, plus legitimate Apple signing/provisioning inputs for final export.`
