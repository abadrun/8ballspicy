# Build and export runbook

## Current executable status

| Operation | Status |
|---|---|
| Original IPA checksum | **VERIFIED** |
| Debian structural/source tests | **DONE** |
| macOS package tests | **DONE / VERIFIED** — GitHub Actions run `36967006266` passed |
| unsigned iOS Simulator component build | **DONE / VERIFIED** — artifact `11210610256` produced by run `36967006266` |
| Authorized host project integration | **NOT DONE — authorized host source is not present** |
| Host archive | **REQUIRES MACOS/XCODE** |
| Apple signing/export | **REQUIRES DEVELOPER SIGNING** |
| Launch and overlay interaction test | **REQUIRES DEVICE TEST** |
| Final IPA | **NOT DONE** |

## Commands available now

Debian-safe checks:

```bash
bash ExistingIPAWorkspace/Preservation/verify_original.sh
python3 ExistingIPAWorkspace/OverlaySource/Tests/validate_source.py
python3 inspection/inventory_existing_ipa.py > /tmp/ipa-inventory.json
cmp /tmp/ipa-inventory.json ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json
```

The committed workflow `.github/workflows/build-overlay.yml` runs the real Swift tests and an unsigned iOS Simulator build on a GitHub-hosted Mac. Run `36967006266` completed successfully in 1m41s and uploaded the 674,196-byte Actions artifact `ExistingIPAOverlay-ios-simulator-build` (artifact ID `11210610256`). Its build script is:

```bash
bash ExistingIPAWorkspace/scripts/build-overlay-macos.sh
```

The workflow artifact is a component build, **not an IPA** and not a signed application.

## Developer inputs required for the final application

All are mandatory:

1. An authorized Xcode `.xcworkspace` or `.xcodeproj` for the host application.
2. A shared host scheme that archives successfully.
3. A host-owned source integration point that imports `ExistingIPAOverlay` and presents `ExistingIPAOverlayView`.
4. Apple Developer Team ID.
5. Installed signing certificate/private key in the macOS keychain.
6. Provisioning/entitlement configuration valid for the host bundle identifier.
7. A developer-supplied `ExportOptions.plist` matching the intended legitimate distribution method.
8. A registered device or permitted distribution target for launch validation.

The compiled reference IPA cannot substitute for item 1 without binary injection and re-signing, which this workspace does not perform.

## Authorized host integration

In the host project on a Mac:

1. **File → Add Package Dependencies → Add Local…**
2. Select `ExistingIPAWorkspace/OverlaySource`.
3. Link product `ExistingIPAOverlay` to the authorized application target.
4. From host-owned SwiftUI source, import and present the view:

```swift
import ExistingIPAOverlay

// Within a host-owned ZStack or overlay container:
ExistingIPAOverlayView()
```

Do not modify the preserved reference IPA. Build from the authorized host source project.

## Exact archive/export command

After the developer inputs above exist:

```bash
bash ExistingIPAWorkspace/scripts/archive-authorized-host-macos.sh \
  --container /absolute/path/AuthorizedHost.xcworkspace \
  --scheme AuthorizedHost \
  --team-id ABCDE12345 \
  --export-options /absolute/path/ExportOptions.plist \
  --output-dir "$PWD/output"
```

For an `.xcodeproj`, pass that path instead. The script:

1. re-verifies the preserved baseline;
2. resolves package dependencies;
3. archives for generic iOS with the supplied team;
4. verifies the archive's app signature with `codesign`;
5. exports through `xcodebuild -exportArchive`;
6. requires exactly one real exported IPA;
7. validates ZIP, Payload/app, Info.plist, executable Mach-O, and CodeResources;
8. writes the real IPA to `output/`;
9. writes `<exported-name>.ipa.sha256` only after successful validation.

Validate any exported IPA again with:

```bash
python3 ExistingIPAWorkspace/scripts/validate-exported-ipa.py \
  output/AuthorizedHost.ipa --require-signature
```

## Final environment-dependent status

Until the authorized host and signing inputs are supplied:

```text
NOT PRODUCED YET — XCODE/BUILD TOOLCHAIN REQUIRED
```
