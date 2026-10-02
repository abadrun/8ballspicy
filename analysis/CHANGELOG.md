# CHANGELOG

Every record states: file / component / change / reason / ownership
classification / validation status. Only changes that actually occurred are
listed. The supplied artifacts (`8-ball-pool-i3rby-IPAOMTK.COM.ipa`, `logo.png`,
`.gitattributes`) were NOT modified at any point.

| # | File | Component | Change | Reason | Ownership | Validation |
|---|------|-----------|--------|--------|-----------|------------|
| 1 | `.gitignore` | repo hygiene | **Created** — ignore `inspection/extracted/`, `__pycache__/`, `node_modules/`, `.DS_Store` | keep the 205 MB forensic extraction and tooling deps out of git | user repository | OK (paths ignored, extraction present on disk) |
| 2 | `inspection/extracted/` | forensic workspace | **Extracted** IPA contents to disk (205 MB, gitignored) | read-only inspection; original IPA untouched | derived from supplied artifact | OK (zip extracted cleanly, 3,505 entries) |
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
