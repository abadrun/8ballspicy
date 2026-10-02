# CHANGELOG

Every record states: file / component / change / reason / ownership
classification / validation status. Only changes that actually occurred are
listed. The supplied artifacts (`8-ball-pool-i3rby-IPAOMTK.COM.ipa`, `logo.png`,
`.gitattributes`) were NOT modified at any point.

| # | File | Component | Change | Reason | Ownership | Validation |
|---|------|-----------|--------|--------|-----------|------------|
| 1 | `.gitignore` | repo hygiene | **Created** — ignore `inspection/extracted/`, `__pycache__/`, `node_modules/`, `.DS_Store` | keep forensic extractions and tooling deps out of git | user repository | OK (paths ignored; no extraction is tracked) |
| 2 | temporary extraction | forensic workspace | **Extracted** IPA contents to disk (205 MB) | read-only inspection; original IPA untouched | derived from supplied artifact | OK (ZIP extracted cleanly, 3,505 entries; temporary tree removed after inspection) |
| 3 | `inspection/inspect_ipa.py` | tooling | **Created** — dependency-free reproducible inspector (Mach-O load-command parse, cryptid, plist dump, cheat-marker string check, framework inventory) | zero-guessing: every report claim must be re-derivable | new (original work) | OK — exit 0, output matches manual findings |
| 4 | `inspection/INSPECTION_OUTPUT.txt` | evidence | **Created** — captured output of `inspect_ipa.py` | immutable record of machine-checkable findings | generated | OK |
| 5 | `inspection/README.md` | docs | **Created** — what the folder contains, how to reproduce | reproducibility | new | OK |
| 6 | `analysis/INSPECTION_REPORT.md` | documentation | **Created** — full forensic report (identity, DRM indicators, injection mechanism, overlay classification, decision tree) | required by spec §04–§08, §29 | new | OK (all claims traced to script output or recorded commands) |
| 7 | `mr-spicy-ui/prototype/assets/logo-circle-{64,128,256,512}.png` | branding | **Created** — circular RGBA crops derived from `logo.png` (LANCZOS resize + circle mask, no stretch/distort) | header/FAB/pill/avatar integration | derived from supplied `logo.png` | OK (sizes/pixels verified programmatically) |
| 8 | `mr-spicy-ui/prototype/index.html` | prototype | **Created** — overlay component markup: FAB, pill, panel (header, 6 feature circles, 5 sections, footer), 3 modals, toast, demo stage | MR. SPICY neutral UI reference (Outcome C) | new | OK — tag balance, key coverage, IDs, asset refs all checked |
| 9 | `mr-spicy-ui/prototype/css/spicy.css` | design system | **Created** — all design tokens + component styles + RTL logical properties + reduce-motion/transparency + responsive rules | centralized token system (spec §10–§22) | new | OK — braces balanced; consumed by validated prototype |
| 10 | `mr-spicy-ui/prototype/js/spicy-i18n.js` | localization | **Created** — EN/AR tables (104 keys each) + direction map | spec §18 (EN/AR, RTL, no hard-coded strings) | new | OK — key-set equality EN/AR verified |
| 11 | `mr-spicy-ui/prototype/js/spicy-app.js` | app logic | **Created** — state machine, navigation, modals w/ focus trap, settings application, tools simulation, toast, boot guard | spec §24 (UI state model) | new | OK — `node --check`; 45/45 jsdom checks after one robustness fix (single-init guard) |
| 12 | `mr-spicy-ui/swift/*.swift` (11 files) | SwiftUI reference | **Created** — tokens, localization, components, header, circles, modal, home/tools, settings, account/about, overlay state machine, demo app | spec §23 (clean SwiftUI architecture) | new | PARTIAL — structural checks pass (brace/paren balance, init argument order, symbol names); **not compiled** (no Xcode in sandbox) |
| 13 | `mr-spicy-ui/validation/validate-prototype.mjs` | tests | **Created** — 45-check jsdom functional harness | spec §33 validation | new | OK — 45/45 passed |
| 14 | `mr-spicy-ui/validation/README.md` | docs | **Created** — how to run, results, validation boundary | honesty about scope | new | OK |
| 15 | `mr-spicy-ui/README.md` | docs | **Created** — package overview, design-system summary, what it is/is not | spec §10 §38 | new | OK |
| 16 | `mr-spicy-ui/swift/README.md` | docs | **Created** — Xcode integration steps, compile status | integration guidance | new | OK |
| 17 | `output/README.md` | docs | **Created** — explicit statement that no IPA output is produced and why | spec §09, §32 Outcome C | new | OK |
| 18 | `analysis/BEFORE_AFTER_AUDIT.md` | documentation | **Created** — before/after audit with limitations | spec §34 | new | OK |
| 19 | `analysis/CHANGELOG.md` | documentation | **Created** — this file | spec §35 | new | OK |
| 20 | `analysis/FINAL_REPORT.md` | documentation | **Created** — final agent report | spec §37 | new | OK |

### Change NOT made (explicitly)

- **IPA modification / rebranding / re-signing / re-packaging** — NOT DONE
  (blocked: pirated host + compiled cheat overlay; forbidden by spec §06, §08;
  would facilitate infringement and cheat redistribution).
- **Global string replacement (i3rby → MR. SPICY) or image replacement inside
  the IPA** — NOT ATTEMPTED (spec §26, §27).
- **Any gameplay/automation/aim/queue/anti-detection/licensing-bypass
  functionality** — NOT IMPLEMENTED anywhere (spec §06, §08).

## 2026-10-02 continuation

| File / component | Change | Validation |
|---|---|---|
| `inspection/inspect_overlay.py` | Added read-only overlay inventory tool for Mach-O dependencies, named menu classes, localization keys, state fields, resources, and URLs. | Python compilation passed; output deterministic. |
| `inspection/OVERLAY_INVENTORY.json` | Added generated machine-readable overlay inventory. | JSON parsed and regenerated byte-for-byte. |
| `analysis/OVERLAY_ARCHITECTURE.md` | Added ORIGINAL GAME / OVERLAY / UNKNOWN architecture and reconstruction classification. | Findings trace to inventory/static evidence. |
| `ExistingIPAWorkspace/OverlaySource/` | Added iOS 16+ source integration component implementing only permitted menu-shell and local interface preferences. | Structural checks passed; Xcode build unavailable. |
| `output/release-manifest.json` | Updated to record source-project production and no-IPA status. | JSON parse passed. |
| `output/README.md` | Updated current deliverables and signing/export limitation. | Reviewed against repository outputs. |

The original IPA was not modified. No compiled overlay code, proprietary game resources, ads, payment/activation systems, gameplay systems, or capture-evasion functionality were copied into the permitted source component.

## Existing-IPA workspace directive

| File / component | Change | Validation |
|---|---|---|
| `ExistingIPAWorkspace/Preservation/` | Added checksum record, Git-object preservation documentation, and verifier for both working artifact and independently stored tracked blob. | Both hashes equal the required SHA-256. |
| `inspection/inventory_existing_ipa.py` | Added read-only complete archive inventory and strict three-way classification. | Python compilation passed; deterministic output. |
| `ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json` | Added hashes, sizes, CRC, category, and reason for all 3,505 ZIP members. | Regenerated byte-for-byte and JSON parsed. |
| `ExistingIPAWorkspace/OverlaySource/` | Moved/renamed the permitted source package into the existing-IPA workspace; removed any implication that it is a final replacement application. | Source validator passed. |
| `ExistingIPAWorkspace/INTEGRATION_STATUS.md` | Added precise source integration, signing, and authorized-host boundary. | Reviewed against artifact structure. |
| `analysis/EXISTING_IPA_IMPLEMENTATION_REPORT.md` | Added current verification, structure, classification, and implementation report. | Counts and hashes match generated inventories. |

The existing IPA remains the base/reference artifact. No modified IPA or modified-IPA checksum was created.

## Baseline requirement re-verification — 2026-10-02

| File / component | Change from baseline A | Validation |
|---|---|---|
| `8-ball-pool-i3rby-IPAOMTK.COM.ipa` | **No byte change.** Re-hashed before and after; safely extracted to a temporary `/tmp` workspace for intake inspection. | Working file and committed blob both equal `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`; ZIP test passed. |
| `inspection/inspect_ipa.py` | Added real, path-traversal-guarded `--extract-to` support and direct `com.i3rby.*` marker reporting; corrected direct-host localization discovery. | Python compilation passed; temporary extraction produced 3,344 files / 205,308,617 bytes; default report regenerated. |
| `inspection/inventory_existing_ipa.py` | Expanded generated schema to include all bundle IDs, application plist metadata, 25 frameworks, standalone dylibs, app extensions, resource bundles/types, all Mach-O slices, and exact/mixed i3rby boundaries. | Python compilation passed; deterministic regeneration passed; 3,505 entries, 43 bundle IDs, 31 arm64 Mach-O binaries. |
| `ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json` | Regenerated from the expanded read-only inventory tool. No application payload was changed. | JSON parsed; expected checksum/count/classification assertions passed. |
| `inspection/INSPECTION_OUTPUT.txt` | Regenerated to include direct i3rby attribution markers and corrected 17-directory host localization list. | Regenerated successfully from the preserved baseline. |
| `analysis/BASELINE_AUDIT_2026-10-02.md` | Added explicit A/B/C distinction, temporary extraction record, full structural summary, modification ownership boundary, and zero-IPA-delta decision. | Cross-checked against generated inventory, preservation verifier, and device-component validator. |
| `analysis/INSPECTION_REPORT.md` | Corrected an older statement that i3rby appeared only in filename provenance; the binary contains direct `com.i3rby.*` evidence. | Confirmed against `libloader` bytes and generated inventories. |
| `analysis/EXISTING_IPA_IMPLEMENTATION_REPORT.md`, `inspection/README.md`, `ExistingIPAWorkspace/README.md` | Updated inventory/extraction scope and artifact status references. | Documentation values cross-checked against machine outputs. |

Artifact B remains the separate verified unsigned component with SHA-256 `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`. Artifact C remains **NOT PRODUCED** because an authorized host source project and legitimate signing configuration are absent. No no-op IPA was created.

## Implementation-path analysis — 2026-10-02

| File / component | Change | Validation |
|---|---|---|
| `analysis/IMPLEMENTATION_PLAN.md` | Added the precise B product/API analysis, source-level integration mechanism, coexistence boundary, C delta allowlist, signing requirements, and single immediate blocker. | Cross-checked against `Package.swift`, Swift source, compiled module/object markers, resource metadata, and integration scripts. |
| `ExistingIPAWorkspace/scripts/configure-authorized-host-package.py` | Completed Xcode project wiring: package product dependency plus `PBXBuildFile` in the target's `PBXFrameworksBuildPhase`; added strict partial-state detection and idempotence. | Three parser-fixture tests pass; no host project was created or claimed. |
| `ExistingIPAWorkspace/scripts/test_configure_authorized_host_package.py` | Added temporary parser-data tests for dry run, complete linkage, idempotence, and missing-Frameworks-phase rejection. | 3/3 tests pass on Linux. |
| `ExistingIPAWorkspace/scripts/integrate-authorized-host-macos.sh` | Corrected host import contract to compiled module `ExistingIPAOverlayUI`; requires an actual `ExistingIPAOverlayView(...)` construction; final validation now checks static module and exact resource bundle. | Shell syntax passed; source/module names verified in Artifact B. |
| `ExistingIPAWorkspace/scripts/validate-device-component.py` | Requires both arm64 objects/modules, absence of an app payload, the public view marker, and exact SwiftPM resource metadata. | Artifact B passes with entry point `ExistingIPAOverlayUI.ExistingIPAOverlayView`. |
| `ExistingIPAWorkspace/scripts/validate-final-ipa.py` | Added app-root SwiftPM resource-bundle validation and clarified static-link component evidence. | Positive resource/component check passed on known baseline structures; validator correctly rejects Artifact A as C. |
| `ExistingIPAWorkspace/OverlaySource/README.md`, `BUILD_RUNBOOK.md`, `FINAL_BUILD_RUNBOOK.md`, `INTEGRATION_STATUS.md` | Corrected product-vs-module naming and documented static linking, resource copying, and the immediate host-source blocker. | Documentation grep and script/source cross-check passed. |

Artifacts A and B were not modified. No IPA was generated.

## Component readiness pipeline — 2026-10-02

| File / component | Change | Validation |
|---|---|---|
| `OverlaySource/Tests/ExistingIPAOverlayCoreTests/` | Expanded settings, Codable, malformed-data, reset, storage isolation, and real isolated-`UserDefaults` coverage. | Passed natively and against iOS Simulator. |
| `OverlaySource/Tests/ExistingIPAOverlayUITests/` | Added localization/resource, view-model persistence, reduced-motion/expansion, SwiftUI body, and hosting-controller lifecycle coverage. | Passed natively and against iOS Simulator. |
| `SampleHost/` | Added a clean iOS 16 SwiftUI consumer of local package product `ExistingIPAOverlay` and module `ExistingIPAOverlayUI`. It is not Artifact C. | Simulator build/install/launch and generic iPhoneOS arm64 build passed. |
| `scripts/test-overlay-macos.sh` and validators | Added complete package/host lifecycle tests, app/component validation, deployment checks, and actionable CI diagnostics. | Full workflow passed. |
| `scripts/create-reproducible-zip.py` and `build-overlay-macos.sh` | Added fixed-metadata ZIPs, per-member manifests, SHA-256 sidecars, and exclusion of volatile IDE-only `.swiftsourceinfo`. | Two clean builds were byte-identical. |
| `.github/workflows/build-overlay.yml` | Added macOS test, clean-host, dual-build reproducibility, policy, validation, evidence, and hash-reporting gates. | Run `37018507081`, job `110875251387`: PASS. |
| `analysis/COMPONENT_READINESS_2026-10-02.md` | Recorded exact tests, canonical hashes, authorized-host consumption steps, and requested final status fields. | Cross-checked against successful CI annotations and artifact metadata. |

Canonical reproducible hashes: Simulator `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5`; iPhoneOS arm64 `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f`. The accepted Artifact B remains unchanged at `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`. Artifact C and a final IPA were not produced.

## Production handoff readiness — 2026-10-02

| File / component | Change | Validation |
|---|---|---|
| `analysis/PRODUCTION_HANDOFF.md` | Added the authoritative input contract, exact package/resource/signing procedure, deterministic production checklist, expected Artifact C checks, delta-review gate, and explicit non-actions. | Cross-checked against integration and final-IPA validator behavior. |
| `analysis/PRODUCTION_MANIFEST.json` | Added deterministic machine-readable baseline/component hashes and host/signing/final status. | JSON parsed; exact required keys/values asserted. |
| `scripts/validate-authorized-host-settings.py` | Added resolved-Xcode-settings validation for exact app target, product type, iPhoneOS support, iOS 16+, bundle ID, Team ID, signing style, and enabled signing. | Nine unit tests pass. |
| `scripts/integrate-authorized-host-macos.sh` | Reordered all non-mutating preflight before project edits; added explicit host/target/deployment/signing/export/resource/output/no-op guards and validate-before-publish staging. | Shell syntax and five handoff-guard tests pass; no production host was supplied or used. |
| `scripts/validate-final-ipa.py` | Added deployment floor, required bundle-member, rejected-hash, static SwiftPM resource evidence, duplicate-member, and safe-extraction checks. | Five synthetic IPA validator tests pass. |
| `FINAL_BUILD_RUNBOOK.md` | Pointed production execution to the authoritative handoff and documented hard gates/non-actions. | Command/options checked against script usage. |

Artifact A, Artifact B, and baseline `libloader` were not modified. No host was substituted, no signing was fabricated, and no IPA was produced.
