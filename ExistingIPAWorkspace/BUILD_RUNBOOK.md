# Build and export runbook

## Current status

| Operation | Status |
|---|---|
| Original IPA checksum | **VERIFIED** — `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` |
| Debian structural/source tests | **DONE** |
| Swift package tests on macOS | **PASSED** — workflow `36972725882` |
| Generic iOS device component build | **PASSED** — `iphoneos`, arm64 |
| Device component validation | **PASSED** — ZIP, Mach-O objects, Swift modules, and resource bundle |
| Authorized host project integration | **NOT AVAILABLE — no authorized host source is present** |
| Host archive/export | **NOT AVAILABLE — requires authorized host and signing inputs** |
| Apple signing/provisioning | **NOT PERFORMED** |
| Physical-device runtime launch | **NOT PERFORMED — requires a signed host and registered device** |
| Final IPA | **NOT PRODUCED** |

## Produced device component

The macOS workflow runs the real Swift tests and builds the Swift package with:

```text
xcodebuild -scheme ExistingIPAOverlay \
  -destination 'generic/platform=iOS' \
  -sdk iphoneos \
  CODE_SIGNING_ALLOWED=NO clean build
```

Run [`36972725882`](https://github.com/abadrun/8ballspicy/actions/runs/36972725882) completed successfully on `macos-15`. Its package tests, device-target build, and arm64 validation all passed. The validated component is tracked at:

```text
output/ExistingIPAOverlay-ios-device-build.zip
SHA-256 c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b
Size 354246 bytes
Architecture arm64
```

The ZIP contains `Debug-iphoneos` Swift object products, arm64 Swift modules, and the processed resource bundle. It is a compiled **component**, not an IPA or signed application. The Actions artifact is `ExistingIPAOverlay-ios-device-build` (artifact ID `11212302365`).

Revalidate it with:

```bash
python3 ExistingIPAWorkspace/scripts/validate-device-component.py \
  output/ExistingIPAOverlay-ios-device-build.zip
unzip -t output/ExistingIPAOverlay-ios-device-build.zip
sha256sum output/ExistingIPAOverlay-ios-device-build.zip
```

The build script is:

```bash
bash ExistingIPAWorkspace/scripts/build-overlay-macos.sh
```

It rejects non-macOS execution, invokes Swift package tests unless `SKIP_TESTS=1`, targets `generic/platform=iOS` with the `iphoneos` SDK, and rejects output without an arm64 Mach-O product. It intentionally disables code signing because this is a reusable component rather than an app.

## Authorized host assessment

The current branch, every remote branch, repository paths, and available workflow artifacts were checked for an authorized `.xcodeproj` or `.xcworkspace` for `pool.app`. None was found. `mr-spicy-ui/swift/` is a neutral standalone reference implementation; its README explicitly says it is not connected to the supplied IPA and it has no Xcode project/workspace. It is not an authorized host for this component.

The component was therefore not inserted into `Payload/pool.app`, and the third-party executable was not changed. The original IPA remains preserved by `Preservation/verify_original.sh`.

## Developer inputs required for a final application

All are mandatory:

1. An authorized Xcode `.xcworkspace` or `.xcodeproj` for the host application.
2. A shared host scheme that archives successfully.
3. Host deployment target iOS 16 or newer (the accepted component cannot preserve Artifact A's iOS 13–15 compatibility).
4. A host-owned source integration point that imports the `ExistingIPAOverlayUI` Swift module and presents `ExistingIPAOverlayView`.
5. Apple Developer Team ID.
6. Installed signing certificate/private key in the macOS keychain.
7. Provisioning/entitlement configuration valid for the host bundle identifier.
8. A developer-supplied `ExportOptions.plist` matching the intended legitimate distribution method.
9. A registered device or permitted distribution target for launch validation.

The compiled reference IPA cannot substitute for item 1 without binary injection and re-signing, which this workspace does not perform.

## Archive/export command when legitimate inputs exist

```bash
bash ExistingIPAWorkspace/scripts/archive-authorized-host-macos.sh \
  --container /absolute/path/AuthorizedHost.xcworkspace \
  --scheme AuthorizedHost \
  --team-id ABCDE12345 \
  --export-options /absolute/path/ExportOptions.plist \
  --output-dir "$PWD/output"
```

The archive script re-verifies the preserved baseline, resolves package dependencies, archives generic iOS, verifies the app signature, exports through `xcodebuild -exportArchive`, validates the resulting IPA, and writes its real checksum. It must only be run with an authorized host and legitimate developer signing configuration.
