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
3. Run **Product → Test** to execute `ExistingIPAOverlayCoreTests`.
4. An authorized developer may add the `ExistingIPAOverlay` product to source for a host application they are entitled to build and sign.
5. The SwiftUI entry point is `ExistingIPAOverlayView()`.

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

This environment has no Xcode or Swift toolchain. Compilation, simulator/device tests, host integration, signing, and export were not performed.

```text
NOT PRODUCED YET — BUILD/SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```
