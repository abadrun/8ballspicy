# Build output status

A rebuildable permitted-overlay source component now exists at `../ExistingIPAWorkspace/OverlaySource/` inside the existing-IPA workspace. It is tied to the inspected IPA structure and is not a replacement application. It does not patch or embed the supplied IPA or compiled overlay.

No modified IPA or checksum has been created:

```text
NOT PRODUCED YET — BUILD/SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```

## Produced

- `../ExistingIPAWorkspace/` — preservation records, complete 3,505-entry IPA inventory, integration status, and permitted overlay source.
- `../ExistingIPAWorkspace/OverlaySource/` — iOS 16+ Swift Package with SwiftUI components, local settings persistence, EN/ID localization, assets, tests, resource-bundle metadata reference, and build configuration references.
- `../analysis/EXISTING_IPA_IMPLEMENTATION_REPORT.md` — current existing-IPA verification, complete structure summary, ownership boundary, and integration result.
- `../analysis/OVERLAY_ARCHITECTURE.md` — ORIGINAL GAME / OVERLAY / UNKNOWN separation and VERIFIED / RECONSTRUCTED / INFERRED / NOT REPRODUCIBLE classifications.
- `../inspection/inspect_overlay.py`, `../inspection/inventory_existing_ipa.py`, and their JSON outputs — reproducible overlay and complete archive inventories.
- `release-manifest.json` — machine-readable source-project and no-IPA status.

## Not produced

- `8 Ball Pool Modified.ipa`
- `8 Ball Pool Modified.sha256`

The source project requires Xcode integration into an authorized host, compilation, testing, and legitimate developer signing. This environment has neither Xcode nor a signing/export identity.

The original `8-ball-pool-i3rby-IPAOMTK.COM.ipa` remains unchanged with SHA-256:

```text
59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8
```

## Status correction

`8-ball-pool-modified.ipa` is retained only as a historical no-op repackaging for audit purposes. Its application files are byte-identical to the original IPA and it is **not** a modified release. It must not be installed, published, or described as an integrated device build.

Current verified status:

- `authorizedHostIntegration`: `NOT_DONE`
- `integratedIntoExistingIPA`: `false`
- `deviceBuild`: `NOT_AVAILABLE`
- `finalIPA`: `NOT_PRODUCED`
- `featuresUnlocked`: `NOT_VERIFIED`
- `adsRemoved`: `NOT_VERIFIED`
