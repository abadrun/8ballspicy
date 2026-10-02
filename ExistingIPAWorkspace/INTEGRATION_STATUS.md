# Existing IPA integration status

## Base artifact — verified and preserved

- File: `8-ball-pool-i3rby-IPAOMTK.COM.ipa`
- SHA-256: `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`
- ZIP entries: 3,505
- Payload: `Payload/`
- App bundle: `Payload/pool.app`
- Main executable: `Payload/pool.app/pool`
- Existing overlay: `Payload/pool.app/Frameworks/libloader.framework/libloader`

The working artifact and the separately stored tracked Git blob are both checked by `Preservation/verify_original.sh`.

## Work tied to the existing IPA

1. Every archive member is recorded in `Inventory/IPA_FILE_INVENTORY.json` with uncompressed SHA-256, size, compression size, CRC, category, and classification reason.
2. Main and overlay Mach-O linked-library inventories are recorded.
3. Framework, standalone dylib, localization, resource, executable, signature, and overlay boundaries are recorded.
4. Existing overlay UI classes, state fields, localization keys, dependencies, configuration patterns, and unknowns are documented in `../analysis/OVERLAY_ARCHITECTURE.md`.
5. Permitted overlay menu-shell and local-settings source is maintained in `OverlaySource/` as a Swift Package, not as another application.

## Why the source is not inserted into the current IPA

The available base is a compiled, signed app bundle rather than an authorized Xcode host project. Adding or replacing executable code in it would necessarily:

- alter signed bundle bytes;
- invalidate the existing code signature;
- require a new provisioning/signing operation;
- require binary injection or load-command modification if no host source is available.

Those operations are not performed. The package can only become part of a legitimate final product when an authorized developer has the host application's source-level build, entitlements, provisioning, and signing identity.

## Required developer path

1. Obtain an authorized source-level project for the host application, or a host integration target supplied by its owner.
2. Open `OverlaySource/Package.swift` in Xcode 15+ and run its tests.
3. Link the `ExistingIPAOverlay` product from the authorized host source project.
4. Present `ExistingIPAOverlayView` through a host-owned integration point.
5. Build and test on a simulator/device using the host owner's entitlements.
6. Archive, sign, and export using the legitimate Apple Developer team.
7. Compare the produced app's structure and behavior against the reference inventory without copying prohibited overlay systems.
8. Only then generate an IPA checksum and release manifest for that actual output.

## Current build result

- Swift/Xcode compilation: unavailable in this Linux environment.
- Host integration: unavailable because authorized host source is absent.
- Signing/export: unavailable.
- Modified IPA: not created.
- Modified IPA checksum: not created.

```text
NOT PRODUCED YET — BUILD/SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```
