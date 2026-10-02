# CleanOverlay

A clean, source-level SwiftUI reconstruction of the **legitimate menu and local-configuration patterns** observed during static inspection of the supplied compiled overlay.

It is not a binary patch and does not embed or depend on the supplied IPA. It contains no gameplay automation, prediction, aim assistance, queue automation, anti-detection, ads, payments, subscriptions, activation, or network code.

## Requirements

- Xcode 15 or newer
- iOS 16 or newer
- Swift 5.9

## Open and test

1. In Xcode, choose **File → Open** and select `CleanOverlay/Package.swift`.
2. Xcode creates the package schemes automatically. Select the `CleanOverlay-Package` scheme.
3. Run **Product → Test** to execute `CleanOverlayCoreTests`.
4. Add the `CleanOverlay` package product to an authorized iOS host target.
5. Present `CleanOverlayView()` in a SwiftUI overlay owned by that host.

Example:

```swift
import SwiftUI
import CleanOverlay

struct AuthorizedHostView: View {
    var body: some View {
        ZStack(alignment: .topTrailing) {
            HostContent()
            CleanOverlayView()
                .padding()
        }
    }
}
```

Do not inject this package into third-party applications. The host application must be one you are authorized to build and sign.

## Structure

```text
Package.swift
Configuration/
  Info.plist                 Example authorized-host plist
  Debug.xcconfig
  Release.xcconfig
Sources/
  CleanOverlayCore/          Codable settings and local persistence
  CleanOverlayUI/            SwiftUI shell, components, screens, theme
    Resources/en.lproj/
    Resources/id.lproj/
Tests/
  CleanOverlayCoreTests/
```

The Swift Package manifest is the source of truth for products, targets, platform, resources, tests, and the generated Xcode package scheme. The `.xcconfig` and `Info.plist` files are references for an authorized example host target; SwiftPM library targets do not consume an application Info.plist.

## Privacy and dependencies

- Persistence: `UserDefaults` only
- Network: none
- Analytics: none
- Ads: none
- Payment/activation: none
- External package dependencies: none

## Reconstruction limits

See `../analysis/OVERLAY_ARCHITECTURE.md` for the VERIFIED / RECONSTRUCTED / INFERRED / NOT REPRODUCIBLE classification. This source is not claimed to be identical to the compiled overlay.

## Build status

The current environment does not include Xcode or a Swift toolchain, so an actual iOS build and test run could not be performed here.

```text
NOT PRODUCED YET — SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```
