# Existing IPA Workspace

This workspace is anchored to the repository's existing source artifact:

```text
8-ball-pool-i3rby-IPAOMTK.COM.ipa
SHA-256 59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8
```

The IPA remains the reference/base application. This workspace does not create a replacement game or rename an unmodified IPA as a modified product.

## Contents

- `Preservation/` — checksum, Git-object preservation procedure, and verifier for the unchanged IPA.
- `Inventory/IPA_FILE_INVENTORY.json` — schema-v2 inventory of all 3,505 ZIP members plus bundle IDs, frameworks, dylibs, resources, plists, architectures, and i3rby attribution evidence.
- `OverlaySource/` — maintainable source for permitted overlay UI and local settings only. This is an integration source component, not a standalone application or final IPA.
- `INTEGRATION_STATUS.md` — exact build/integration boundary and remaining developer actions.
- `../analysis/BASELINE_AUDIT_2026-10-02.md` — pre-change temporary-extraction record and explicit baseline/component/final-artifact distinction.

## Existing application structure

```text
Payload/
└── pool.app/                              ORIGINAL GAME container
    ├── pool                               UNKNOWN/mixed: game executable + injected load command
    ├── Info.plist                         UNKNOWN: host metadata includes overlay changes
    ├── Frameworks/
    │   ├── libloader.framework/           EXISTING OVERLAY
    │   ├── libswift_Concurrency.dylib     ORIGINAL GAME bundled dependency
    │   └── 24 other framework bundles     ORIGINAL GAME bundled dependencies
    ├── PlugIns/                           ORIGINAL GAME extensions
    ├── *.lproj/                           ORIGINAL GAME localization
    ├── game layouts/images/audio/data     ORIGINAL GAME resources
    ├── _CodeSignature/                    UNKNOWN: generated after injection
    └── SC_Info/                           UNKNOWN: redistribution placeholder
```

`ORIGINAL_GAME` means structurally attributable to the host bundle and outside the injected overlay. It does not claim that every byte has pristine provenance. Mixed or post-injection components are classified `UNKNOWN` rather than guessed.

## Current result

The IPA remains preserved and unmodified. No FairPlay, signing, provisioning, entitlement, server, anti-cheat, gameplay, or capture-evasion change was attempted. The repository and remote branches were checked for an authorized host Xcode project/workspace; none exists. The neutral `mr-spicy-ui/swift` demo source is not a host for `pool.app`.

The permitted package was built and validated on a GitHub-hosted macOS 15 runner for a real generic iOS device target. The device component is available at `../output/ExistingIPAOverlay-ios-device-build.zip` with SHA-256 `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`. It is unsigned and is not an IPA. It was not injected into the third-party bundle.

A signed IPA still requires an authorized host source project, source-level integration, provisioning, an Apple signing identity, archive/export, and device launch validation. Those inputs are not present.
