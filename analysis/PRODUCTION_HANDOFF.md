# Production handoff

**Handoff state:** `READY_FOR_HOST`; host status is `WAITING`. Production integration remains blocked until the real host and signing inputs listed below are supplied.

This document is the execution contract for producing Artifact C later. It does not authorize use of an unrelated host, binary injection, modification of Artifact A, modification of the accepted baseline `libloader`, fabricated signing, or no-op IPA repackaging.

## 1. Authoritative artifacts

| Artifact | Identity | SHA-256 | State |
|---|---|---|---|
| Artifact A | `8-ball-pool-i3rby-IPAOMTK.COM.ipa`, preserved i3rby baseline | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` | Immutable; do not replace, recompress, patch, inject into, or re-sign |
| Artifact B | `ExistingIPAOverlay-ios-device-reproducible.zip`, latest verified reproducible iPhoneOS arm64 component | `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f` | Verified CI component; not an IPA |
| Previous accepted component | `output/ExistingIPAOverlay-ios-device-build.zip`, earlier accepted unsigned iPhoneOS arm64 component | `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b` | Preserved unchanged for compatibility/evidence |
| Simulator component | `ExistingIPAOverlay-ios-simulator-reproducible.zip` | `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5` | Verified test artifact; not an IPA |
| Artifact C | Signed production IPA exported from the authorized host | Not available | **NOT PRODUCED** |

Machine-readable values are in [`PRODUCTION_MANIFEST.json`](PRODUCTION_MANIFEST.json). The immediate host procedure is [`HOST_INTEGRATION_CHECKLIST.md`](HOST_INTEGRATION_CHECKLIST.md). The component test/build evidence remains in [`COMPONENT_READINESS_2026-10-02.md`](COMPONENT_READINESS_2026-10-02.md).

## 2. Package contract

- Local Swift package path: `ExistingIPAWorkspace/OverlaySource`
- Package product linked to the app target: `ExistingIPAOverlay`
- Core Swift module: `ExistingIPAOverlayCore`
- UI Swift module imported by host source: `ExistingIPAOverlayUI`
- Public SwiftUI entry point: `ExistingIPAOverlayView()`
- SwiftPM resource bundle: `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle`
- Minimum supported host deployment target: **iOS 16.0**
- External package dependencies: none
- Component persistence: local `UserDefaults` key `ExistingIPAOverlay.settings.v1`

The product is consumed from source with the authorized host's Xcode toolchain. Do not copy Artifact B's loose compiler products into an app and do not place them in `Frameworks/`.

## 3. Required production inputs

All items are mandatory before production execution:

1. Owner-supplied authorized `.xcodeproj` or `.xcworkspace` containing the real production iOS application target.
2. Exact app target name and a shared scheme that builds/tests/archives that target.
3. Resolved production deployment target of iOS 16.0 or newer.
4. Owner-approved source file, included in the app target, that presents `ExistingIPAOverlayView` at the approved lifecycle/UI location.
5. Owner-approved coexistence contract for existing baseline behavior, including lawful permission and source/build ownership for any required `libloader` coexistence. The repository script does not copy or modify `libloader`.
6. Authorized production bundle identifier.
7. Ten-character Apple Team ID already configured on the production target.
8. Valid Apple signing certificate and private key installed in the macOS keychain.
9. Valid provisioning configuration for the production bundle identifier and intended export method.
10. `ExportOptions.plist` with an explicit `method`, the same `teamID`, a valid signing style, and provisioning-profile mapping when manual signing is selected.
11. An iOS Simulator destination on which the host test scheme can run.
12. An empty output directory. Existing `final.ipa` or `final.sha256` is never overwritten silently.
13. A host-owner-approved expected-delta allowlist and a same-source, same-configuration pre-integration control archive for final delta comparison.

An IPA, an unpacked third-party app, `mr-spicy-ui`, or the repository sample host is not an authorized production host.

## 4. Host-owned presentation point

The authorized developer must add a source file to the real app target. The minimum source-level contract is:

```swift
import ExistingIPAOverlayUI
import SwiftUI

struct AuthorizedOverlayPresentation: View {
    var body: some View {
        ExistingIPAOverlayView()
    }
}
```

The host owner decides how and where this view enters the production hierarchy. The integration script verifies the import and construction but deliberately does not invent the presentation location.

## 5. Resource-bundle contract

SwiftPM must copy `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` to the application-bundle root. Do not rename it or manually copy a resource snapshot. Both the archive and final IPA must contain:

```text
ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Info.plist
ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/Assets.car
ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/en.lproj/Localizable.strings
ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/id.lproj/Localizable.strings
```

The bundle `Info.plist` must declare `CFBundlePackageType = BNDL` and an iOS deployment target of 16.0 or newer. Missing resources are a hard failure.

## 6. Deterministic production checklist

Execute in order on macOS with Xcode. Stop at the first failure; do not bypass a gate.

- [ ] **Freeze inputs.** Record the authorized host commit, Xcode version, scheme, target, bundle ID, Team ID, signing style, provisioning identity, export method, and expected-delta allowlist.
- [ ] **Verify immutable inputs.** Run `bash ExistingIPAWorkspace/Preservation/verify_original.sh`; verify latest Artifact B metadata equals `3c01a9d...ecd3f`, verify the previous accepted local component remains `c0e66b...088b`, and confirm `analysis/PRODUCTION_MANIFEST.json` still says `STATE = READY_FOR_HOST` and `FINAL_IPA_STATUS = NOT_PRODUCED`.
- [ ] **Identify the actual target.** Run `xcodebuild -list -json` on the supplied project/workspace. Confirm the selected target is `com.apple.product-type.application`, not a framework, test bundle, sample, or unrelated app.
- [ ] **Create a control build.** Archive/export the authorized host at the frozen commit and settings before package integration. Inventory it for later expected-versus-actual delta comparison. This control is not Artifact C.
- [ ] **Add the host-owned presentation source.** Include it in the production target and confirm it imports `ExistingIPAOverlayUI` and constructs `ExistingIPAOverlayView()`.
- [ ] **Prepare legitimate signing.** Confirm the target already resolves to the authorized Team ID and bundle ID, the signing identity exists, and `ExportOptions.plist` matches the intended distribution method.
- [ ] **Use an empty output directory.** Never point output at Artifact A and never overwrite an existing final export.
- [ ] **Run the guarded pipeline** with real values:

  ```bash
  bash ExistingIPAWorkspace/scripts/integrate-authorized-host-macos.sh \
    --container /absolute/path/AuthorizedHost.xcworkspace \
    --project /absolute/path/AuthorizedHost.xcodeproj \
    --scheme AuthorizedHost \
    --target AuthorizedHost \
    --integration-source /absolute/path/AuthorizedHost/OverlayIntegration.swift \
    --test-destination 'platform=iOS Simulator,name=iPhone 16' \
    --bundle-id com.example.authorizedhost \
    --team-id ABCDE12345 \
    --export-options /absolute/path/ExportOptions.plist \
    --configuration Release \
    --output-dir /absolute/path/to/empty-production-output
  ```

  For a project-only host, set `--container` and `--project` to the same `.xcodeproj`. `--target` may be omitted only when that project contains exactly one iOS application target; multiple app targets fail as ambiguous and require an owner-selected explicit target.

- [ ] **Confirm preflight.** The script must identify the exact app target, resolve iOS 16.0+, match bundle ID and Team ID, detect enabled signing, validate export options, find a real signing identity, and dry-run package linkage before editing the project.
- [ ] **Confirm package linkage.** Product `ExistingIPAOverlay` must appear in the production target's Frameworks phase; host source must import module `ExistingIPAOverlayUI`.
- [ ] **Confirm tests.** The real host scheme must pass on the specified Simulator after package resolution.
- [ ] **Confirm iPhoneOS archive.** The archive must contain exactly one `.app`, a signed arm64 executable, and the exact resource bundle/files above.
- [ ] **Confirm legitimate export.** `xcodebuild -exportArchive` must produce exactly one IPA using the supplied export options. No archive is fabricated and no baseline IPA is recompressed.
- [ ] **Validate Artifact C.** Run the exact command in section 7. A failed validation means Artifact C does not exist for reporting purposes.
- [ ] **Compare deltas.** Inventory the validated export and the frozen control build. Review every changed path against the owner-approved allowlist. Expected package-related deltas include the host executable's static linkage, the new SwiftPM bundle, Xcode-generated metadata/signatures, and provisioning/export metadata. Any unexplained game resource, framework, executable, entitlement, or `libloader` delta blocks release.
- [ ] **Record the actual hash.** Calculate `shasum -a 256 final.ipa`; ensure it matches `final.sha256`.
- [ ] **Store only the real validated export.** Copy/move it to repository `output/` only after approval, then rerun final validation at that final path.
- [ ] **Update records.** Change `FINAL_IPA_STATUS` only after the actual file exists and passes every gate; record exact path, SHA-256, host commit, signing/export method, validation result, and approved delta report.

## 7. Artifact C validation command

The guarded pipeline runs this validation in staging before publishing `final.ipa`. Rerun it on the final stored path:

```bash
python3 ExistingIPAWorkspace/scripts/validate-final-ipa.py output/final.ipa \
  --require-signature \
  --require-provisioning \
  --require-arm64 \
  --require-component ExistingIPAOverlayUI \
  --require-resource-bundle ExistingIPAOverlay_ExistingIPAOverlayUI.bundle \
  --require-bundle-resource Assets.car \
  --require-bundle-resource en.lproj/Localizable.strings \
  --require-bundle-resource id.lproj/Localizable.strings \
  --minimum-ios 16.0 \
  --baseline-ipa 8-ball-pool-i3rby-IPAOMTK.COM.ipa \
  --report-json output/final-validation-report.json \
  --reject-sha256 59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8 \
  --codesign-verify \
  --bundle-id <AUTHORIZED_PRODUCTION_BUNDLE_ID>
```

Expected checks:

1. The path exists, is non-empty, is a valid ZIP, every member passes CRC validation, and there are no duplicate or unsafe extraction paths.
2. There is exactly one `Payload/*.app` with valid `Info.plist`, expected bundle ID, and a declared deployment target of iOS 16.0 or newer.
3. The main executable exists and includes arm64.
4. Package/component evidence and the exact SwiftPM resource bundle are present.
5. `Assets.car` and both EN/ID localization files exist in that bundle.
6. `_CodeSignature/CodeResources` exists and `codesign --verify --deep --strict` succeeds.
7. `embedded.mobileprovision` exists, decodes, is unexpired, and authorizes the exact app bundle ID.
8. The IPA hash is not Artifact A's hash; an exact no-op baseline artifact is rejected.
9. The final SHA-256 is calculated from the actual validated IPA and written beside it.
10. The machine report records SHA-256, architecture, bundle ID, app version/build, signing/provisioning state, embedded component/resource state, and added/modified/removed paths relative to Artifact A.
11. The host-owner control-vs-final inventory delta contains only approved production/package/signing changes; unexplained changes fail handoff.

## 8. Script hard failures and non-actions

`integrate-authorized-host-macos.sh` fails before production when:

- the host project/workspace does not exist or an IPA is supplied as the host;
- a workspace has no explicit app project;
- the named target cannot be found or is not an application target;
- the scheme/configuration cannot resolve the exact target;
- the deployment target is below iOS 16.0 or unresolved;
- bundle ID, Team ID, signing style, export options, signing identity, or provisioning inputs are absent/inconsistent;
- the host-owned presentation source is missing or lacks the required import/view construction;
- Artifact A or the previous accepted local device component no longer matches its authoritative hash;
- package source/tooling or required archive resources are missing;
- archive/export/validation does not produce exactly one valid result;
- an existing final output would be overwritten; or
- the exported IPA is byte-identical to Artifact A.

The scripts never use Artifact A as a build input, never replace/recompress it, never copy or modify `libloader`, never substitute the sample host, never create certificates/profiles, never self-sign, and publish `final.ipa` only after a real Xcode export passes validation.

## 9. Handoff verification

Final repository-side verification completed without rebuilding the already accepted component:

- 29 Python unit tests passed (project configurator, automatic/explicit target identification, host settings, handoff guards, and synthetic final-IPA validation/reporting).
- Source/package/localization/prohibited-capability validation passed.
- Clean sample-host source integration validation passed.
- Previous accepted local device-component validation and ZIP integrity passed; latest Artifact B remains the verified reproducible CI component recorded above.
- Artifact A preservation and committed-blob checks passed.
- Artifact A was explicitly rejected as Artifact C.
- Baseline inspection, full inventory, and overlay inventory regenerated byte-for-byte.
- Deterministic ZIP self-test passed.
- Prototype functional suite passed 45/45 checks.
- All Python compilation, shell syntax, JSON parsing, manifest-contract, documentation-contract, and Git whitespace checks passed.
- Existing macOS/Xcode component, Simulator, lifecycle, device, resource, localization, persistence, sample-host, and two-build reproducibility evidence remains the successful run `37018507081`; it was not rerun because component source is complete and unchanged by this handoff.

Production-only Xcode target resolution, signing, archive, provisioning, export, delta review, and physical-device checks cannot execute until the authorized host/signing package exists; the pipeline now treats their absence as a hard failure.

## 10. Current terminal state

```text
STATE: READY_FOR_HOST
COMPONENT: READY
HOST: WAITING
PRODUCTION HOST: NOT PROVIDED
SIGNING: NOT PROVIDED
ARTIFACT C: NOT PRODUCED
```

The exact remaining input is:

```text
AUTHORIZED_PRODUCTION_XCODE_PROJECT_OR_WORKSPACE + REAL_APP_TARGET + APPROVED_INTEGRATION_POINT + LEGITIMATE_APPLE_SIGNING/PROVISIONING/EXPORT_CONFIGURATION
```

No further host search or production build should run until that actual owner-supplied input is provided.
