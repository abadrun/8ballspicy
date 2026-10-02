# ExistingIPAOverlay clean sample host

This is a minimal, repository-owned SwiftUI application used only to prove that the local `ExistingIPAOverlay` Swift package can be consumed by an authorized source-level host.

It is deliberately unrelated to Artifact A and is **not** Artifact C. It contains no game code, `libloader`, binary injection, private hooks, signing credentials, or third-party assets.

## Integration demonstrated

The sample target:

1. references `../OverlaySource` through `XCLocalSwiftPackageReference`;
2. links package product `ExistingIPAOverlay` in its Frameworks build phase;
3. imports the compiled module with `import ExistingIPAOverlayUI`;
4. places `ExistingIPAOverlayView()` in a host-owned SwiftUI hierarchy;
5. targets iOS 16 or newer.

## Build

On macOS with Xcode:

```bash
xcodebuild \
  -project ExistingIPAWorkspace/SampleHost/ExistingIPAOverlaySampleHost.xcodeproj \
  -scheme ExistingIPAOverlaySampleHost \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath .build/SampleHostSimulator \
  CODE_SIGNING_ALLOWED=NO \
  clean build

xcodebuild \
  -project ExistingIPAWorkspace/SampleHost/ExistingIPAOverlaySampleHost.xcodeproj \
  -scheme ExistingIPAOverlaySampleHost \
  -destination 'generic/platform=iOS' \
  -derivedDataPath .build/SampleHostDevice \
  CODE_SIGNING_ALLOWED=NO \
  clean build
```

The CI integration test also installs and launches the Simulator build, then validates that the statically linked module and `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` are present. The generic iPhoneOS build remains unsigned and is never exported as an IPA.
