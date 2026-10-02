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
- `../analysis/PRODUCTION_HANDOFF.md` — authoritative production contract and Artifact C validation requirements.
- `../analysis/HOST_INTEGRATION_CHECKLIST.md` — immediate authorized-host integration checklist.
- `../analysis/PRODUCTION_MANIFEST.json` — machine-readable authoritative handoff hashes/status.
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

The permitted package passed the full readiness pipeline on a GitHub-hosted macOS 15 runner: native and Simulator tests, SwiftUI lifecycle, resources/localization/persistence, clean sample-host build/install/launch, Simulator and generic iPhoneOS arm64 builds, policy scans, and two-build byte reproducibility. Canonical readiness hashes are `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5` (Simulator) and `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f` (device). See `../analysis/COMPONENT_READINESS_2026-10-02.md`.

The earlier accepted device component remains unchanged at `../output/ExistingIPAOverlay-ios-device-build.zip`, SHA-256 `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`. All component outputs are unsigned, are not IPAs, and were not injected into the third-party bundle.

A signed IPA still requires an authorized production host source project, source-level integration, lawful permission for required baseline coexistence, provisioning, an Apple signing identity, archive/export, and device launch validation. Those inputs are not present.
