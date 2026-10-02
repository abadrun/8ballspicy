# Existing IPA integration status

## Base artifact — verified and preserved

- File: `8-ball-pool-i3rby-IPAOMTK.COM.ipa`
- SHA-256: `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`
- ZIP entries: 3,505
- Payload: `Payload/`
- App bundle: `Payload/pool.app`
- Main executable: `Payload/pool.app/pool`
- Existing overlay: `Payload/pool.app/Frameworks/libloader.framework/libloader`

The preservation verifier continues to compare the working IPA with the tracked original Git blob. The third-party app bundle and executable were not modified.

## Authorized source component

`OverlaySource/` is maintainable source for permitted menu-shell and local-settings UI. It contains no gameplay automation, prediction, aim assistance, queue automation, capture evasion, advertising, payments, activation, licensing, or network code.

The source was tested and compiled on GitHub Actions run [36972725882](https://github.com/abadrun/8ballspicy/actions/runs/36972725882):

- Swift package tests: **PASSED**
- Xcode destination: `generic/platform=iOS`
- SDK: `iphoneos`
- Product directory: `Debug-iphoneos`
- Architecture: **arm64**
- Component validator: **PASSED**
- Component artifact: `../output/ExistingIPAOverlay-ios-device-build.zip`
- Component SHA-256: `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`
- Signing: **not performed** (component has no app bundle, host entitlements, or provisioning profile)

This is a real device-target component build, not a simulator ZIP and not an IPA. It is a snapshot of relocatable `.o` products, compiler-specific Swift modules, and `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle`; it is not a drop-in `.framework` or `.xcframework`.

## Integration contract

An authorized host must add the local package product `ExistingIPAOverlay` to its app target and Frameworks build phase. Host source imports the compiled module as `ExistingIPAOverlayUI` and constructs `ExistingIPAOverlayView()`. Xcode then statically links the package objects into the host executable and copies the SwiftPM resource bundle to the app root. Because the accepted component declares iOS 16 while Artifact A declares iOS 13, the host owner must explicitly accept a deployment-target increase to iOS 16; it is not applied silently by the configurator.

The loose object files in the component ZIP are not copied into `Frameworks/`. The exact implementation-level plan and output delta are documented in `../analysis/IMPLEMENTATION_PLAN.md`.

## Host search and integration boundary

The current branch, all remote branches, repository paths, and available GitHub Actions artifacts were inspected for an authorized host Xcode project or workspace. None exists. `mr-spicy-ui/swift/` is a neutral standalone reference implementation, not a host for `pool.app`, and has no Xcode project/workspace or signing configuration.

The source component was not injected into `Payload/pool.app`. Replacing or adding executable code in the compiled third-party bundle would alter signed bytes and require binary injection, re-signing, and entitlements; those operations are intentionally not performed.

The single immediate missing input is an authorized host Xcode project/workspace containing the app target and lawful source-level ownership of the baseline integration, including `libloader` if coexistence is required. Signing/provisioning remains mandatory after that host integration builds, but it is not the next build-step input.

## Final application status

- Authorized host integration: **NOT AVAILABLE — authorized host source is absent**
- IPA archive/export: **NOT AVAILABLE**
- Apple signing/provisioning: **NOT PERFORMED**
- Physical-device runtime launch: **NOT PERFORMED — requires a signed host and registered device**
- Signed IPA: **NOT PRODUCED**
- Original IPA: **PRESERVED UNCHANGED**

The legitimate deliverable supported by the repository is the validated unsigned arm64 device component under `output/`. A signed application can be produced only after an authorized host owner supplies the host project, integration point, entitlements, provisioning, signing identity, export options, and device target.
