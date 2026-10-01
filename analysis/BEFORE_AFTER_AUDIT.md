# BEFORE / AFTER AUDIT

## BEFORE

### Repository contents (as supplied)

| File | Size | SHA-256 |
|---|---|---|
| `.gitattributes` | 66 B | — (`* text=auto` only; no LFS; no reason to modify) |
| `8-ball-pool-i3rby-IPAOMTK.COM.ipa` | 98,576,945 B | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` |
| `logo.png` | 1,172,471 B | `2056971c95da6f04ddf546c8409100604302c3deb5e47a7b29418ed220d44dc9` (1254×1254, RGB, red mark `#D20D0F` on solid black, no alpha) |

### IPA architecture (discovered, not assumed)

- ZIP container, 3,505 entries → `Payload/pool.app` (~205 MB uncompressed).
- Host app: **Miniclip 8 Ball Pool 56.30.0 (5328)**, `com.miniclip.8ballpoolmult`,
  arm64, App Store AppID 543186831 — the full original game (Cocos2d-x `.ccbi`
  layouts, atlases, 18 `.lproj` localizations incl. Arabic, legitimate ad/analytics
  SDKs: AppLovin, AdSurge, BigoADS, DTBiOSSDK, FBAudienceNetwork, Firebase*,
  GoogleAppMeasurement, InMobi, Moloco, OMSDK_Appodeal, Promises, nanopb).
- Piracy indicators: `DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"`
  in Info.plist; `LC_ENCRYPTION_INFO_64 cryptid = 0` (FairPlay stripped);
  `SC_Info/` emptied; no provisioning profile; bundle re-signed after injection
  (CodeResources covers libloader); `NSUserTrackingUsageDescription` replaced
  with cheat-licensing text; filename provenance IPAOMTK.COM.

### Overlay architecture (discovered)

- Injection: final `LC_LOAD_DYLIB` of `pool` →
  `@executable_path/Frameworks/libloader.framework/libloader`.
- `libloader.framework`: ID `com.appdome.libloader` (disguised), 11.49 MB arm64
  Mach-O, links UIKit/WebKit/JavaScriptCore/StoreKit/AdSupport/CoreTelephony.
- Content (strings/symbols): `GBModMenu` + `GBMenu*` mod-menu class taxonomy;
  `Aim Mode`, `Aim Strength`, `Auto Play`, `Auto Queue`, `Cushion: Pro banks`,
  `Prediction Lines`, `Opponent Lines`, `Table Outline`, pocket rings, break %,
  humanization/max-speed; subscription licensing (`Activate Key`, PRO tiers,
  1h…1y periods, IDFA device binding, Telegram sales), rewarded-ad endpoint
  `https://omg10.com/4/1286848`, and anti-detection ("Hides lines, menu, and
  buttons from streams, recordings, and screenshots"). Localized EN + Indonesian.

### Existing branding / UI categories

- Host app branding: 8 Ball Pool / Miniclip throughout (untouched).
- Overlay UI categories (concepts only, not implemented as functionality):
  overlay states; feature tiles; toggle / meter / segmented / key-value rows;
  entitlement card; FAQ; account/activation; language.
- Existing limitations: no source code anywhere in the artifact; compiled,
  obfuscated, re-signed binary; DRM already stripped; cheat functionality
  inseparable from the overlay's feature set.

## AFTER

### Actual permitted changes

**To the supplied artifacts: none.** The IPA, `logo.png` and `.gitattributes`
are byte-for-byte untouched (verified by SHA-256 / git status after all work).

### MR. SPICY visual system (new, standalone)

- Centralized token system in two mirrored sources:
  `mr-spicy-ui/prototype/css/spicy.css` and `mr-spicy-ui/swift/SpicyTheme.swift`
  (surfaces, brand gradient from the logo red `#D20D0F`, ink, lines, states,
  4 pt spacing, radii, shadows, type scale, control metrics, motion durations).
- Overlay component: closed (FAB) → minimized (pill) → expanded (panel) states;
  header (logo + wordmark + subtitle + settings/minimize/close); six feature
  circles (Home, Tools, Settings, Language, Account, About) with
  active/inactive/disabled states; grouped rows (toggle, slider, segmented,
  meter, key-value); modals (language, sign-in, reset) with scrim, focus
  management and actions; toast; honest demo-mode/account presentation.
- Logo integration: derived circular RGBA crops at 64/128/256/512 px
  (`mr-spicy-ui/prototype/assets/`); original preserved at repo root.

### Localization / RTL

- Complete EN + AR string tables (104 keys each) in `spicy-i18n.js` and
  `SpicyLocalization.swift`; UI reads strings only from tables.
- True RTL mirroring via `dir` + CSS logical properties / SwiftUI
  `layoutDirection`; chevrons and directional icons flip; Arabic typography
  rules (no letter-spacing, increased line height); language switch is instant
  and includes aria labels.

### Responsive behavior

- Device-width simulation (compact 375 / regular 430), fluid panel width
  `min(360px, 100% − spacing)`, scrollable content with max height, safe-area
  padding (`env(safe-area-inset-*)`), small-screen and short-screen media
  queries, landscape consideration, no fixed single-screen assumption.

### Accessibility

- Roles/labels on all controls (`role=switch/dialog/radio/group`, `aria-label`,
  `aria-current`, `aria-modal`, `aria-live` toast/log), focus management and
  focus trap in modals, Escape handling, ≥44 px targets, visible focus rings,
  contrast-checked palette, Reduce Motion (system media query **and** manual
  toggle), Reduce Transparency, Dynamic-Type-style text scaling. Works in both
  EN and AR.

### Files created

```
.gitignore
inspection/inspect_ipa.py
inspection/INSPECTION_OUTPUT.txt
inspection/README.md
analysis/INSPECTION_REPORT.md
analysis/BEFORE_AFTER_AUDIT.md
analysis/CHANGELOG.md
analysis/FINAL_REPORT.md
mr-spicy-ui/README.md
mr-spicy-ui/prototype/index.html
mr-spicy-ui/prototype/css/spicy.css
mr-spicy-ui/prototype/js/spicy-i18n.js
mr-spicy-ui/prototype/js/spicy-app.js
mr-spicy-ui/prototype/assets/logo-circle-{64,128,256,512}.png
mr-spicy-ui/swift/README.md
mr-spicy-ui/swift/SpicyTheme.swift
mr-spicy-ui/swift/SpicyLocalization.swift
mr-spicy-ui/swift/SpicyComponents.swift
mr-spicy-ui/swift/SpicyFeatureCircle.swift
mr-spicy-ui/swift/SpicyHeaderView.swift
mr-spicy-ui/swift/SpicyModalView.swift
mr-spicy-ui/swift/SpicyHomeView.swift
mr-spicy-ui/swift/SpicySettingsView.swift
mr-spicy-ui/swift/SpicyAccountView.swift
mr-spicy-ui/swift/SpicyOverlayView.swift
mr-spicy-ui/swift/SpicyDemoApp.swift
mr-spicy-ui/validation/validate-prototype.mjs
mr-spicy-ui/validation/README.md
output/README.md
```

### Files modified

None of the supplied files. (`.gitignore` is a new file, not a modification.)

### Files intentionally untouched

- `8-ball-pool-i3rby-IPAOMTK.COM.ipa` — preserved as evidence/inputs (hash
  recorded above and re-verified after all work).
- `logo.png` — original branding asset preserved; only derived crops were created.
- `.gitattributes` — plain LF-normalization rules; no legitimate reason to change.
- Everything inside the IPA — no extraction-based modification, no re-packaging,
  no re-signing, no binary patching, no string/asset replacement.

## LIMITATIONS

- The overlay UI exists only as a compiled, obfuscated, re-signed binary inside
  a pirated app: **no source exists** and no legitimate modification path exists.
- Producing a modified IPA would require re-signing a pirated bundle and
  rebranding a multiplayer cheat — **prohibited and not attempted**.
- Code-signature validation (`codesign`) could not be run (Linux sandbox) —
  NOT AVAILABLE; structural DRM indicators were used instead.
- The SwiftUI reference was **not compiled** (no Xcode in the sandbox).
- The prototype was validated functionally (jsdom, 45/45 checks) but **not
  pixel-rendered** (browser CDNs blocked in the sandbox); no screenshots and no
  on-device testing were performed.
- The overlay's internals beyond surface inspection (obfuscated symbols,
  encrypted payloads, network protocol) were deliberately **not**
  reverse-engineered — no legitimate need, and deeper cheat analysis is out of scope.
