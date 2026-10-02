# Existing IPA Overlay Source

This Swift Package is the maintainable source reconstruction of **permitted UI and local-configuration portions** of the overlay found in the repository's existing IPA. It is one part of `ExistingIPAWorkspace`; it is not a replacement application and is not the final product by itself.

Reference relationship:

```text
8-ball-pool-i3rby-IPAOMTK.COM.ipa (preserved reference/base)
  └─ Payload/pool.app
      └─ Frameworks/libloader.framework (compiled existing overlay)

ExistingIPAWorkspace/OverlaySource (maintainable permitted source)
  └─ reproduces only menu-shell and local interface patterns
```

The package does not embed or patch the supplied IPA. It contains no gameplay automation, prediction, aim assistance, queue automation, capture evasion, ads, payments, subscriptions, activation, or network code. Integrating any source into a compiled IPA would alter its signature and therefore requires an authorized host source/build plus legitimate Apple signing; this repository does not perform that step.

## Requirements

- Xcode 15 or newer
- iOS 16 or newer
- Swift 5.9

## Open and test

1. In Xcode, open `ExistingIPAWorkspace/OverlaySource/Package.swift`.
2. Select the generated `ExistingIPAOverlay-Package` scheme.
3. Run **Product → Test** to execute `ExistingIPAOverlayCoreTests` and `ExistingIPAOverlayUITests`.
4. An authorized developer may add the `ExistingIPAOverlay` package product to a host application they are entitled to build and sign.
5. Host source imports the product's Swift module with `import ExistingIPAOverlayUI`.
6. The SwiftUI entry point is `ExistingIPAOverlayView()`.

This package must not be injected into the supplied third-party binary. It is retained alongside the existing IPA so permitted work is source-maintainable if an authorized host build path becomes available.

## Structure

```text
Package.swift
Configuration/
  ResourceBundleInfo.reference.plist
  Debug.xcconfig
  Release.xcconfig
Sources/
  ExistingIPAOverlayCore/     Codable settings and local persistence
  ExistingIPAOverlayUI/       SwiftUI shell, components, screens, theme
    Resources/en.lproj/
    Resources/id.lproj/
Tests/
  ExistingIPAOverlayCoreTests/
  ExistingIPAOverlayUITests/
  validate_source.py
```

The package manifest defines products, targets, platform, resources, tests, and Xcode's generated package scheme. The reference plist documents resource-bundle metadata; SwiftPM generates the actual bundle metadata during an authorized build.

## Dependencies and privacy

- Persistence: `UserDefaults` only
- Network: none
- Analytics: none
- Ads: none
- Payment/activation: none
- External package dependencies: none

See `../../analysis/OVERLAY_ARCHITECTURE.md` and `../INTEGRATION_STATUS.md` for verified reconstruction boundaries.

## Build status

Full readiness passed on GitHub Actions run [37018507081](https://github.com/abadrun/8ballspicy/actions/runs/37018507081) with Xcode on `macos-15`:

- All 17 Core/UI tests passed natively and against iOS Simulator
- SwiftUI body and hosting-controller lifecycle checks passed
- Clean iOS 16 sample-host Simulator build/install/launch passed
- Clean generic iPhoneOS arm64 host build passed
- Resource bundle, EN/ID localization, and persistence checks passed
- Two clean complete builds produced byte-identical ZIPs and manifests
- Simulator SHA-256: `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5`
- Device SHA-256: `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f`

The workflow outputs are unsigned component builds, not IPAs. The earlier accepted component at `../../output/ExistingIPAOverlay-ios-device-build.zip` remains unchanged. The repository does not contain an authorized production host Xcode project for the supplied third-party app, so no production-host integration, signing, or IPA export was performed.
