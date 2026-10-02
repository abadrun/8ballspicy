# Authorized production host integration checklist

## Frozen READY component evidence

- Xcode-tested component source commit: `26755b1f2c8c693ff21673cf3ac3231e3564de5f`
- Successful full component workflow: `37018507081`
- Latest verified iPhoneOS arm64 component SHA-256: `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f`
- Simulator component SHA-256: `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5`
- Baseline Artifact A SHA-256: `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`
- Current integration branch: `arena/01a0fc96-8ballspicy`

Every later handoff commit on this branch contains the READY component lineage. Record `git rev-parse HEAD` immediately before integration and retain it in the final machine-readable report. Do not rebuild the standalone component merely to start host integration; the authorized host rebuilds the package from `ExistingIPAWorkspace/OverlaySource` with its own Xcode toolchain.

## Required owner inputs

Do not leave WAIT state until all of these are real and owner-supplied:

- authorized `.xcodeproj` or `.xcworkspace`;
- real production iOS application target and shared scheme;
- owner-approved source-level presentation point;
- lawful baseline-coexistence authorization and expected-delta allowlist;
- production bundle identifier and configured Apple Team ID;
- installed signing certificate/private key;
- valid provisioning and `ExportOptions.plist`; and
- same-source/configuration pre-integration control archive for delta review.

Without them, the required terminal error is:

```text
ERROR: Production host not supplied. Provide the authorized .xcodeproj/.xcworkspace and legitimate signing/export configuration.
```

## Exact integration checklist

- [ ] Xcode project/workspace supplied
- [ ] production app target identified
- [ ] bundle identifier recorded
- [ ] deployment target verified
- [ ] owner-approved presentation point identified
- [ ] baseline coexistence authorization confirmed
- [ ] ExistingIPAOverlay package added
- [ ] ExistingIPAOverlayUI product linked
- [ ] required resource bundle included
- [ ] host builds successfully
- [ ] unit/UI tests pass
- [ ] iPhoneOS arm64 build succeeds
- [ ] archive succeeds
- [ ] legitimate signing succeeds
- [ ] export succeeds
- [ ] final IPA exists
- [ ] IPA validation succeeds
- [ ] final SHA-256 recorded

`ExistingIPAOverlayUI product linked` above means: link Swift package product `ExistingIPAOverlay` to the app target and verify that host source imports its UI module `ExistingIPAOverlayUI`. Never look for or link a nonexistent product named `ExistingIPAOverlayUI`.

## Execution detail for each checkbox

### 1. Host and target

- [ ] Record the supplied host path, owner, source commit, Xcode version, and clean working-tree state.
- [ ] Run `xcodebuild -list -json` against the supplied container.
- [ ] If the selected `.xcodeproj` contains exactly one `com.apple.product-type.application` target, allow automatic identification.
- [ ] If it contains multiple application targets, stop and pass the owner-selected `--target`; never guess.
- [ ] For a workspace, pass `--project` explicitly. Do not infer among multiple projects.
- [ ] Reject framework, extension, test, sample-host, and unrelated targets.
- [ ] Record the shared production scheme and ensure it resolves the same app target.

Automatic/explicit project target resolution can be checked before production with:

```bash
python3 ExistingIPAWorkspace/scripts/identify-authorized-host-target.py \
  --project /absolute/path/AuthorizedHost.xcodeproj

# Required only when more than one app target exists:
python3 ExistingIPAWorkspace/scripts/identify-authorized-host-target.py \
  --project /absolute/path/AuthorizedHost.xcodeproj \
  --target OwnerSelectedProductionTarget
```

### 2. Identity, deployment, presentation, and coexistence

- [ ] Record the resolved `PRODUCT_BUNDLE_IDENTIFIER`.
- [ ] Confirm `IPHONEOS_DEPLOYMENT_TARGET` is numeric and at least `16.0`.
- [ ] Confirm `SUPPORTED_PLATFORMS` includes `iphoneos`.
- [ ] Confirm the production target already resolves the authorized Team ID and signing style.
- [ ] Add an owner-supplied source file to that exact target; it must import `ExistingIPAOverlayUI` and construct `ExistingIPAOverlayView()` at the approved host lifecycle/UI point.
- [ ] Freeze the owner-approved baseline-coexistence and Artifact A → Artifact C delta allowlist.
- [ ] Do not copy, patch, inject, replace, or modify Artifact A or its accepted baseline `libloader`.

### 3. Package and resources

- [ ] Add local package path `ExistingIPAWorkspace/OverlaySource`.
- [ ] Link package product `ExistingIPAOverlay` in the production app target's Frameworks phase.
- [ ] Compile host import `ExistingIPAOverlayUI`.
- [ ] Confirm SwiftPM places this exact bundle at the app root:

```text
ExistingIPAOverlay_ExistingIPAOverlayUI.bundle/
  Info.plist
  Assets.car
  en.lproj/Localizable.strings
  id.lproj/Localizable.strings
```

- [ ] Confirm `CFBundlePackageType = BNDL` and bundle deployment target is iOS 16.0 or newer.
- [ ] Do not manually rename/copy the resource bundle and do not put loose component objects into `Frameworks/`.

### 4. Build, test, archive, sign, and export

Use the explicit owner inputs. `--target` may be omitted only for a project with exactly one application target:

```bash
bash ExistingIPAWorkspace/scripts/integrate-authorized-host-macos.sh \
  --container /absolute/path/AuthorizedHost.xcworkspace \
  --project /absolute/path/AuthorizedHost.xcodeproj \
  --target OwnerSelectedProductionTarget \
  --scheme AuthorizedProductionScheme \
  --integration-source /absolute/path/AuthorizedHost/OverlayIntegration.swift \
  --test-destination 'platform=iOS Simulator,name=iPhone 16' \
  --bundle-id com.example.authorizedhost \
  --team-id ABCDE12345 \
  --export-options /absolute/path/ExportOptions.plist \
  --configuration Release \
  --output-dir /absolute/path/to/new/empty/output
```

The guarded pipeline must:

- [ ] resolve the real app target unambiguously;
- [ ] validate deployment, bundle ID, Team ID, signing style, export options, and installed signing identity before editing;
- [ ] dry-run package linkage before applying it;
- [ ] resolve packages and run the real host's unit/UI test scheme;
- [ ] archive generic iPhoneOS and verify arm64/resource contents;
- [ ] use only legitimate owner-supplied signing/provisioning/export inputs;
- [ ] export exactly one new IPA;
- [ ] reject an IPA equal to Artifact A's SHA-256;
- [ ] validate in staging before publishing outputs; and
- [ ] refuse to overwrite any existing final output.

### 5. Final outputs and report

Successful production creates new files in the chosen output directory; it never replaces Artifact A:

```text
final.ipa
final.sha256
final-validation-report.json
```

`final-validation-report.json` must record:

- actual IPA SHA-256 and size;
- Mach-O architectures, including arm64;
- production bundle identifier;
- `CFBundleShortVersionString` and `CFBundleVersion`;
- minimum iOS version;
- signing manifest presence, strict `codesign` result, and provisioning result;
- embedded `ExistingIPAOverlayUI` evidence;
- exact SwiftPM resource-bundle status and required members; and
- added, modified, and removed file paths relative to Artifact A, with counts and Artifact A SHA-256.

Then:

- [ ] Compare every recorded delta to the owner-approved allowlist and same-source pre-integration control archive.
- [ ] Reject unexplained changes to baseline executables, frameworks, resources, entitlements, or `libloader`.
- [ ] Re-run `validate-final-ipa.py` on the stored `output/.../final.ipa`.
- [ ] Verify `final.sha256` equals a fresh `shasum -a 256` calculation.
- [ ] Update `analysis/PRODUCTION_MANIFEST.json` from `READY_FOR_HOST` only after all checks pass.
- [ ] Record host commit, integration commit, Xcode version, app identity/version/build, signing/export method, final path/hash, validation report path, and approved delta report.

## Stop conditions

Stop without Artifact C if any host, target, integration, coexistence, deployment, resource, test, architecture, archive, signing, provisioning, export, validation, hash, or delta check fails. Never bypass licensing, advertising/reward authorization, server authorization, DRM, anti-cheat, multiplayer controls, or any protected third-party mechanism.
