# Build output status

A clean, rebuildable source project now exists at `../CleanOverlay/`. It is an independent Swift Package and does not patch or embed the supplied IPA or compiled overlay.

No modified IPA or checksum has been created:

```text
NOT PRODUCED YET — SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```

## Produced

- `../CleanOverlay/` — iOS 16+ Swift Package with SwiftUI components, local settings persistence, EN/ID localization, assets, tests, example Info.plist, and build configuration references.
- `../analysis/OVERLAY_ARCHITECTURE.md` — ORIGINAL GAME / OVERLAY / UNKNOWN separation and VERIFIED / RECONSTRUCTED / INFERRED / NOT REPRODUCIBLE classifications.
- `../inspection/inspect_overlay.py` and `../inspection/OVERLAY_INVENTORY.json` — reproducible static binary inventory.
- `release-manifest.json` — machine-readable source-project and no-IPA status.

## Not produced

- `8 Ball Pool Modified.ipa`
- `8 Ball Pool Modified.sha256`

The source project requires Xcode integration into an authorized host, compilation, testing, and legitimate developer signing. This environment has neither Xcode nor a signing/export identity.

The original `8-ball-pool-i3rby-IPAOMTK.COM.ipa` remains unchanged with SHA-256:

```text
59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8
```
