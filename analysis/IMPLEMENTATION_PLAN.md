# Implementation Plan — Artifact B to Artifact C

This plan starts after acceptance of the baseline audit. It does not re-audit Artifact A and does not treat Artifact B as an IPA.

## 1. What Artifact B actually is

Artifact B is a ZIP of Xcode `Debug-iphoneos` products for the Swift package in `ExistingIPAWorkspace/OverlaySource/`. It contains:

- `ExistingIPAOverlayCore.o` — arm64 Mach-O relocatable object;
- `ExistingIPAOverlayUI.o` — arm64 Mach-O relocatable object;
- compiler-specific `.swiftmodule`, `.swiftdoc`, `.swiftsourceinfo`, and ABI metadata for both modules;
- `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` with compiled assets and English/Indonesian localizations.

It contains no `Payload/`, `.app`, `.framework`, `.xcframework`, `.swiftinterface`, dynamic-library install name, provisioning profile, or code signature. The compiled modules are compiler-specific rather than stable binary-distribution interfaces. It is therefore an unsigned device-target **build product snapshot**, not an IPA and not a drop-in embedded framework.

The package source, rather than direct manual use of the loose `.o` files, is the supported integration input. Artifact B is the verified proof that those sources compile for arm64 `iphoneos`; the integration pipeline checks its checksum before rebuilding the package as part of an authorized host target.

## 2. Interface/API exposed

`Package.swift` exports package products named `ExistingIPAOverlay` and `ExistingIPAOverlayCore`. The product name and Swift import name are not the same: the UI product's compiled module is **`ExistingIPAOverlayUI`**.

Minimum supported host: iOS 16, Swift 5.9/Xcode 15 or newer. Artifact A declares iOS 13, so integrating B as currently built requires the authorized host to raise its deployment target to iOS 16. Preserving iOS 13–15 compatibility would require a separately rebuilt/lowered component after an API compatibility pass; that would no longer be the accepted Artifact B.

### Host-facing UI API

```swift
import ExistingIPAOverlayUI

ExistingIPAOverlayView()
ExistingIPAOverlayView(model: OverlayViewModel)
```

Other public UI symbols are:

- `OverlayViewModel` — observable expansion, section, settings, persistence, and reset state;
- `OverlayLocalization.text(_:language:)`;
- `OverlayTheme` design constants.

### Core API

Importable as `ExistingIPAOverlayCore`:

- `OverlaySection`, `OverlayLanguage`, and `OverlaySize` enums;
- `OverlaySettings` plus its initializer, defaults, and normalization;
- `KeyValueStoring` protocol;
- `OverlaySettingsStore` with `load`, `save`, and `reset`.

The component uses only local `UserDefaults` persistence under `ExistingIPAOverlay.settings.v1`. It exposes no host-game, network, ad, licensing, payment, automation, or anti-detection API.

## 3. Expected host integration mechanism

The legitimate mechanism is source-level Swift Package Manager integration into an authorized app target:

1. Add `OverlaySource/` as an `XCLocalSwiftPackageReference`.
2. Add product `ExistingIPAOverlay` to the app target's `packageProductDependencies`.
3. Add a `PBXBuildFile` for that product to the target's `PBXFrameworksBuildPhase`; merely declaring the target dependency is insufficient to link it.
4. In a host-owned source file, `import ExistingIPAOverlayUI` and present `ExistingIPAOverlayView` from an app-defined SwiftUI `ZStack`, UIKit `UIHostingController`, or another owner-selected presentation point.
5. Let Xcode statically link the package objects into the host executable and copy `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` to the app bundle root.
6. Test the host, archive for generic iOS, sign nested code and the app, export, and validate the resulting IPA.

The repository's configurator now models steps 1–3. It cannot choose step 4 because only the authorized host owner can select a lifecycle/presentation point without inventing an application architecture.

Directly copying Artifact B into `Payload/pool.app/Frameworks` would not work: B is not a loadable framework. Converting it into an injected dylib or patching Artifact A's executable would be a different binary-injection path and is not used.

## 4. Coexistence with the existing i3rby `libloader`

At the component level, no direct collision is visible:

- B is statically linked by SwiftPM; `libloader.framework` is dynamically loaded.
- B's module names, resource-bundle name, and `UserDefaults` key are distinct.
- B does not inspect, call, patch, replace, unlock, or bypass `libloader`.

Therefore **technical coexistence is plausible**, but **legitimate coexistence is not currently buildable or proven**. It requires an authorized host source project that is itself entitled to include the existing `libloader.framework` binary or authorized source for that component. Artifact A is a compiled application archive and cannot serve as that source project. Its existing injected load command is not a legitimate source-level integration mechanism for B.

No change to `libloader` licensing, rewarded-ad grants, server authorization, tamper logic, anti-cheat, or multiplayer behavior is part of this plan.

## 5. Files that would change to create Artifact C

### Authorized host source tree

At minimum:

- `<AuthorizedHost>.xcodeproj/project.pbxproj` — local package reference, product dependency, Frameworks build-file linkage, and an iOS deployment target of at least 16.0;
- one host-owned Swift source file — imports `ExistingIPAOverlayUI` and presents `ExistingIPAOverlayView`;
- possibly host-owned tests for presentation/lifecycle behavior.

### Exported application bundle

Expected output deltas are:

- the main app executable — relinked with `ExistingIPAOverlayCore` and `ExistingIPAOverlayUI`;
- `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/**` — newly copied SwiftPM resources;
- `_CodeSignature/**` — regenerated for the complete app;
- `embedded.mobileprovision` and entitlements — generated from legitimate provisioning;
- nested-code signatures, including `libloader.framework/_CodeSignature/**`, if that framework is lawfully included;
- generated `Info.plist` build metadata, including `MinimumOSVersion = 16.0` for B as currently defined, and Swift runtime support selected by Xcode.

An exported IPA's ZIP metadata necessarily differs as well. A final artifact cannot honestly be represented as Artifact A plus recompression.

## 6. Files that must remain byte-identical

- The entire repository-root Artifact A must remain byte-identical and is never an output path.
- In any authorized C that claims baseline-content preservation, all payload files outside an explicit integration/signing allowlist must match A in a generated delta report.
- If authorized coexistence includes the existing overlay, `Frameworks/libloader.framework/libloader` and its functional `Info.plist` must remain byte-identical. Its signature metadata cannot remain identical after legitimate re-signing.
- Baseline game resources, localizations, media, and unrelated framework/dylib binaries must remain byte-identical unless the authorized host is rebuilt from owner source, in which case reproducible byte identity cannot be promised and preservation must instead be established by owner-approved source/version and behavior tests.

The unavoidable mutable allowlist is the relinked host executable, new B resource bundle, deployment-target/generated plist metadata, provisioning/entitlements, and all code-signature manifests. Everything else requires an explicit, documented reason to differ. The iOS 13 → 16 support change must be an explicit host-owner decision, not a silent integration side effect.

## 7. Host/signing requirement

Yes. A legitimate path still requires:

- macOS with Xcode and the iOS SDK;
- an authorized host `.xcodeproj` or `.xcworkspace`, app target, and shared scheme;
- a host-owned integration source point;
- rights to every component preserved from the baseline, including `libloader` if it is to coexist;
- a legitimate Apple signing identity, Team ID, provisioning/entitlements, and matching export options;
- a permitted simulator/device test destination.

Signing is required to export/install C, but it is not the first missing build input.

## 8. Single immediate blocker

**The single input preventing the next legitimate build step is an authorized host Xcode project/workspace containing the app target and lawful source-level ownership of the baseline integration, including `libloader` if coexistence is required.**

Without that host source container there is nowhere to link the package product or place `ExistingIPAOverlayView`. Apple signing inputs become the next prerequisite only after that source-level integration builds and tests successfully.

## Work completed with currently available files

The integration tooling could be improved without a host, so the following implementation work was performed:

- corrected the required host import from the product name `ExistingIPAOverlay` to the actual compiled module name `ExistingIPAOverlayUI`;
- completed project wiring by adding the package product to the target's Frameworks build phase, not only `packageProductDependencies`;
- added parser tests for dry-run behavior, complete linkage, idempotence, and rejection of targets without a Frameworks phase;
- strengthened Artifact B validation to require both arm64 modules, both object products, the public `ExistingIPAOverlayView` marker, and the exact resource bundle;
- strengthened final-IPA validation to require both the statically linked `ExistingIPAOverlayUI` marker and `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle`.

No host app, IPA, signature, credential, protected-control patch, or no-op repack was created.
