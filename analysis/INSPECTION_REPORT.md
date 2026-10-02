# INSPECTION REPORT — `8-ball-pool-i3rby-IPAOMTK.COM.ipa`

**Scope:** read-only forensic inspection of the supplied repository artifact.
**Method:** Python 3 (`zipfile`, `plistlib`, `struct`) + `strings`. No modification of any original artifact.
**Reproduction:** `python3 inspection/inspect_ipa.py` (machine-checkable findings, output also saved at `inspection/INSPECTION_OUTPUT.txt`).

---

## 1. Repository inventory

| File | Size | SHA-256 | Role |
|---|---|---|---|
| `.gitattributes` | 66 B | — | Git text-attribute rules |
| `8-ball-pool-i3rby-IPAOMTK.COM.ipa` | 98,576,945 B | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` | Supplied application artifact |
| `logo.png` | 1,172,471 B | `2056971c95da6f04ddf546c8409100604302c3deb5e47a7b29418ed220d44dc9` | MR. SPICY branding candidate |

### `.gitattributes`
Contains exactly:

```
# Auto detect text files and perform LF normalization
* text=auto
```

No Git LFS rules, no merge/ diff drivers, no handling rules for binary assets.
**Decision: no legitimate reason to modify — left untouched.**

### `logo.png`
- Dimensions: **1254 × 1254 px**, square, 1:1 aspect ratio.
- PNG color type 2 — **RGB, no alpha channel**. The background is **solid opaque black** (`#000000` corners).
- Dominant colors: ≈ 85% near-black; ≈ 15% strong red **`#D20D0F`** (center sample `rgb(211,1,2)`).
- The red mark's bounding box (840 × 768 px) is centered on the canvas (bbox center (618, 624) vs canvas center (627, 627)), so circular crops present the mark correctly.
- Quality: clean vector-like edges implied by the quantization profile; no visible compression artifacts in sampled regions.
- **Decision: original preserved untouched.** Derived assets (circular RGBA crops at 512/256/128/64 px) were generated for UI integration — see `mr-spicy-ui/prototype/assets/`.

---

## 2. IPA container structure

- Valid ZIP archive (IPA container). 3,505 entries.
- Top level: `Payload/` only (no `iTunesMetadata.plist`, no `SwiftSupport/`).
- Sole app bundle: **`Payload/pool.app`** (≈ 205 MB uncompressed, 2,913 root entries).

---

## 3. Host application identity — ORIGINAL_APPLICATION (confidence: HIGH)

From `Payload/pool.app/Info.plist`:

| Key | Value |
|---|---|
| `CFBundleIdentifier` | `com.miniclip.8ballpoolmult` |
| `CFBundleDisplayName` / `CFBundleName` | **8 Ball Pool** |
| `CFBundleShortVersionString` | 56.30.0 |
| `CFBundleVersion` | 5328 |
| `AppID` | 543186831 (Miniclip's App Store app id) |
| `MinimumOSVersion` | 13.0 |
| Executable | `pool` — Mach-O arm64 (`cputype 0x0100000C`), 69 `LC_LOAD_DYLIB` commands |

The bundle contains the complete original game payload: Cocos2d-x `.ccbi` layouts, sprite
atlases/plists, 18 `.lproj` localization folders (incl. `ar.lproj`, `de.lproj`, `ru.lproj`, …),
hundreds of `sfx_*.mp3` files, subscription/shop/club UI resources, plus **legitimate
third-party SDK frameworks** (AppLovin, AdSurge, BigoADS, DTBiOSSDK, FBAudienceNetwork,
Firebase*, GoogleAppMeasurement, InMobi, Moloco, OMSDK_Appodeal, Promises, nanopb).

**Classification:** the game content is Miniclip's copyrighted ORIGINAL_APPLICATION.
Confidence HIGH — bundle identifier, AppID, resource volume and SDK set are all consistent
with a genuine App Store build of 8 Ball Pool.

---

## 4. Redistribution / DRM-stripping indicators (confidence: HIGH)

1. **`Info.plist` carries a non-App-Store key:**
   `DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"` — a FairPlay decryption
   service watermark inserted when App Store encryption was removed.
2. **`LC_ENCRYPTION_INFO_64 cryptid = 0`** on the main executable — the binary is decrypted;
   App Store builds have `cryptid = 1`.
3. **`SC_Info/` contains only a `.keep` placeholder** — the FairPlay receipt directory is emptied.
4. **No `embedded.mobileprovision`** — the bundle was re-signed outside the App Store.
5. **`_CodeSignature/CodeResources` (3,400 entries) covers the injected
   `Frameworks/libloader.framework/libloader`** — i.e. the whole bundle was re-signed
   *after* the cheat was injected.
6. **`NSUserTrackingUsageDescription` was replaced** with cheat-licensing text:
   `"Used to bind your subscription key to this device and protect your activation."`
   (The genuine App Store string for this app is an ads/tracking disclosure.)
7. Filename provenance `…-IPAOMTK.COM.ipa` — a third-party IPA distribution site.

**Conclusion:** the artifact is a **DRM-stripped pirated copy** of a commercial App Store
game, re-packaged with an injected payload. Code-signature validation itself could not be
run (Linux sandbox, no `codesign`) — NOT AVAILABLE — but the structural evidence above is
independent and conclusive.

---

## 5. Injection mechanism (confidence: HIGH)

The main executable `pool` loads, as its **final** `LC_LOAD_DYLIB`:

```
@executable_path/Frameworks/libloader.framework/libloader
```

All other 68 load commands are Apple system libraries and the legitimate ad SDKs listed
above; the injected framework was appended last — the standard dylib-injection pattern.

---

## 6. `libloader.framework` — the CUSTOM_OVERLAY (confidence: HIGH)

| Property | Finding |
|---|---|
| Bundle ID | **`com.appdome.libloader`** — disguised to resemble an Appdome (legitimate app-security vendor) framework |
| Binary | Mach-O arm64, **11.49 MB** (very large for a "loader"), `cryptid = 0` |
| Links | UIKit, Foundation, **WebKit + JavaScriptCore**, **StoreKit**, **AdSupport** (IDFA), CoreTelephony, AVFoundation, Security |
| Source code | **NONE inside the artifact** — compiled binary only, with obfuscated Objective-C ivars (`V_x841k84mmkn`, …) |

### 6.1 What it actually implements (string/ symbol evidence)

**Gameplay automation / aim assistance for 8 Ball Pool multiplayer:**
`Aim Mode`, `Aim Strength`, `Auto Play`, `Auto Queue`, `Cushion: Pro banks`, `Cushion Burst`,
`Prediction Lines`, `Opponent Lines`, `Table Outline`, pocket rings, end dots, `Break %`,
`Full Automation: Assist, aim, and Auto Play`, "Caps how fast the cue can move during Assist
and Auto Play", "Humanization, scan mode, aim strength, max speed, and wait time",
"Auto Queue with table, stake, and smart modes".

**Subscription licensing / entitlement commerce:**
`Activate Key`, `Enter subscription key`, `Activate your subscription key here. A key unlocks
Automation and Auto Queue together.`, `Activate PRO to unlock Automation and Auto Queue…`,
`Requires PRO + Auto Queue hour`, key periods (1h/1d/1w/1m/3m/6m/1y), guest reset, session
expiry, `account.tamper`, IDFA device binding (`IDFA required`, `account.idfa_*`), Telegram
sales/support links (`account.buy_telegram`, `access.tg_*`).

**Monetization:** rewarded third-party ad endpoint `https://omg10.com/4/1286848`
("Watch an ad to add time" for free cheat hours).

**Anti-detection:** "Hides lines, menu, and buttons from streams, recordings, and
screenshots." — explicit capture/stream evasion.

**Localization of the overlay:** English + **Indonesian** (e.g. `Auto Play mati`,
`Otomasi penuh: Assist, aim, dan Auto Play`). No Arabic overlay strings.

**UI class taxonomy (mod menu):** `GBModMenu` / `GBModMenuDelegate`, `GBMenuFeatureTile`,
`GBMenuChoiceTile`, `GBMenuEntitlementCard`, `GBMenuFAQHeader`, `GBMenuFXToggleRow`,
`GBMenuMeterRow`, `GBMenuStackedSegmentRow`, `GBMenuKeyValueRow`, `GBMenuLockStrip`,
`GBMenuFixedBox`, `GBMenuModule`, `GBMenuVStack`. Section keys: `AUTOMATION`, `AUTO QUEUE`,
`ACCOUNT` + FAQ, settings, table-overlay tools.

### 6.2 Verdict on the overlay

`libloader.framework` is a **compiled multiplayer-game cheat** (aim assistance, autoplay,
queue automation), with a **paid-subscription licensing system**, rewarded-ad monetization,
and **anti-detection** features — not a neutral UI skin. Its i3rby attribution is confirmed
inside the binary by persistent-domain strings including
`com.i3rby.8poolmod.tg.ad_session_id`, `com.i3rby.autoplay`, and
`com.i3rby.breaklog`; it does not rely only on filename provenance. Obfuscated member names
remain unattributed rather than guessed.

---

## 7. Component classification

| Component | Classification | Confidence |
|---|---|---|
| `Payload/pool.app` game executable + resources (`.ccbi`, atlases, sfx, `*_text.plist`, `*.lproj`) | ORIGINAL_APPLICATION (Miniclip) | HIGH |
| Ad/analytics SDK frameworks (AppLovin, Firebase, InMobi, …) | THIRD_PARTY (bundled by Miniclip) | HIGH |
| `Frameworks/libloader.framework` | **CUSTOM_OVERLAY — multiplayer cheat w/ licensing (injected, DRM-stripped host)** | HIGH |
| `Info.plist` extra keys (`DecryptedBy`, replaced tracking string) | tampered metadata of pirated copy | HIGH |
| `logo.png` | user-supplied branding asset (not part of IPA) | HIGH |
| Obfuscated ivars / encrypted blobs inside libloader | UNKNOWN (not reverse-engineered; no legitimate need) | — |

---

## 8. Decision tree applied (per master specification §29)

- **A. Can the supplied IPA be legitimately adjusted via source/resources?**
  **NO.** The only "custom UI" is a *compiled* cheat binary; the host app is a *pirated,
  DRM-stripped* copy of Miniclip's game. Adjusting the overlay in place = rebranding a
  cheat for redistribution on top of infringing copies — prohibited by the specification
  itself (§06, §08) and by the host app's licensing.
- **B. Authorized source project for the overlay UI?** **NO — NOT AVAILABLE.**
- **C. Is the requested modification dependent on bypassing technical/security
  restrictions?** **YES** ( FairPlay already stripped; producing a modified IPA would
  additionally require re-signing a pirated bundle and patching a compiled cheat).
  → **Not bypassed. Limitation documented.** Legitimate work continues.
- **D. Does the existing component implement multiplayer cheating / unauthorized
  automation?** **YES** (§6.1). → Not improved, not rebranded for distribution, not
  operationalized, not extended.
- **E. Can a standalone legitimate UI demonstration satisfy the remaining design
  objective?** **YES** → build the neutral MR. SPICY UI reference (Outcome C, §32).

---

## 9. Neutral UI concept inventory (extracted for the reference design only)

The following *presentational patterns* are generic UI concepts, extracted without any
cheat semantics and re-specified for legitimate use (settings panels, developer tools,
accessibility panels):

- floating overlay states: closed (bubble) → minimized (pill) → expanded (panel)
- circular feature navigation tiles with active / inactive / disabled states
- row primitives: toggle row, meter/progress row, segmented-choice row, key-value row
- modal sheets with title / subtitle / body / actions
- account presentation with *honest* status (no fabricated entitlements)
- FAQ / about sections; language selection; EN localization (overlay had EN + Indonesian;
  Arabic was required and implemented in the reference from scratch)

**Explicitly NOT carried over:** aim modes, aim strength, prediction/ opponent lines,
cushion/bank controls, auto play, auto queue, table overlays, pocket detection, "hide from
streams/ recordings/ screenshots", subscription-key activation, PRO gating, rewarded-ad
hour grants — i.e. every gameplay-manipulation and cheat-commerce concept.
