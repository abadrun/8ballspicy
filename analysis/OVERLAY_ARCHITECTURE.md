# Overlay Architecture and Clean Reconstruction Record

**Inspection date:** 2026-10-02  
**Method:** read-only ZIP/plist/Mach-O/printable-string inspection  
**Machine-readable inventory:** `inspection/OVERLAY_INVENTORY.json`  
**Reproduction:** `python3 inspection/inspect_overlay.py`

No runtime instrumentation, decryption, binary patching, signing, or IPA rewriting was performed. Static evidence establishes names and relationships, but not every visual or behavioral detail.

## 1. Component boundary

### ORIGINAL GAME — verified

| Component | Evidence |
|---|---|
| `Payload/pool.app` | Sole application bundle in the IPA. |
| Identity | `com.miniclip.8ballpoolmult`, 8 Ball Pool 56.30.0 (5328). |
| Main executable | `Payload/pool.app/pool`, arm64 Mach-O. |
| Game resources | Root-level Cocos layouts, sprites, audio, text plists, and host localization folders. |
| Game/SDK frameworks | AppLovin, Firebase, InMobi, Moloco, FBAudienceNetwork, and other frameworks listed by the existing inspector. |

These files were not copied into or referenced by the clean source project.

### OVERLAY — verified

| Component | Evidence |
|---|---|
| Framework | `Payload/pool.app/Frameworks/libloader.framework`. |
| Binary | `libloader`, 11,493,804 bytes, arm64 Mach-O, SHA-256 `b7f970a8b9faa84b9614055f7966a41975777b360a3abe57ddf5e9b6c71df250`. |
| Relationship to host | Host executable has an `LC_LOAD_DYLIB` for `@executable_path/Frameworks/libloader.framework/libloader`. |
| Bundle files | Binary, `Info.plist`, and `_CodeSignature/CodeResources`; no source or separate asset/localization bundle. |
| Bundle metadata | Identifier `com.appdome.libloader`, version 1.0.0, minimum OS 11.0. |
| UI implementation | UIKit classes and controls are linked/referenced; menu class names are embedded in Objective-C metadata. |

### UNKNOWN — not guessed

- Which obfuscated class owns each behavior beyond the named `GB*` classes.
- Exact class call graph and initialization order.
- Exact colors, dimensions, typography, animations, and every responsive breakpoint.
- Complete key-to-translated-value mapping for every locale.
- Server protocols, runtime responses, and failure-state transitions.
- Which values are authoritative locally versus remotely.
- Runtime appearance on a physical device; the supplied binary was not executed.

## 2. Existing overlay UI structure

### Verified class taxonomy

The binary contains these named UI types:

- `GBModMenu` and `GBModMenuDelegate`
- `GBMenuModule`, `GBMenuVStack`, `GBMenuFixedBox`
- `GBMenuFeatureTile`, `GBMenuChoiceTile`
- `GBMenuFXToggleRow`, `GBMenuMeterRow`, `GBMenuStackedSegmentRow`
- `GBMenuKeyValueRow`, `GBMenuFAQHeader`
- `GBMenuEntitlementCard`, `GBMenuLockStrip`
- `GBPremiumSegment`
- `GBPredictionDrawView`

Initializer signatures verify several component contracts:

- symbol + title + selected state + action;
- title + minimum/maximum/value + action (meter/slider);
- title + items/icons/selected index + action (segmented choice);
- symbol + title + on/off state + target/action (toggle);
- title + value + FAQ action (key/value row);
- stack spacing/insets and fixed-height containers.

### Verified navigation/screens

Localization keys identify five tabs:

1. `tab.prediction`
2. `tab.tuning`
3. `tab.automation`
4. `tab.auto_queue`
5. `tab.account`

Additional verified menu actions include sidebar expand/collapse and reset-all. Header groups include Overlay, Display, Geometry, Effects, Alerts, Mode, Parameters, Timing, Strategy, Stroke, Status, Automation Access, Auto Queue Access, and License.

### Verified controls and feature labels

The compiled overlay includes controls/labels for prediction lines, opponent lines, table outline, pocket rings, end dots, display/line tuning, alerts, collection effects, aim/automation, Auto Play, Auto Queue, account activation, PRO status, free-time/ad grants, account reset, and stream/capture hiding.

The complete recovered localization-key inventory is retained in `inspection/OVERLAY_INVENTORY.json` (317 keys). It is evidence, not executable configuration.

### Configuration and state handling

A printable Objective-C state record provides 60 typed fields. They group into:

- rendering/display: line visibility, offsets, scales, thickness, opacity, graphic mode;
- alerts: scratch and wrong-ball state;
- locale: `useArabic`, `menuLanguage`;
- gameplay automation: aim, autoplay, pocket, break, scan, and humanization fields;
- cosmetic effects: pot/contact/cushion/strike/trail toggles and styles;
- queue automation: enabled state, delay, mode, game type, bet ranges, and tier state.

`NSUserDefaults` selectors (`boolForKey:`, `integerForKey:`, `arrayForKey:`, `setBool:forKey:`, `setInteger:forKey:`, and `setObject:forKey:`) verify local preference storage exists. Exact key-to-field persistence mapping is unknown. Notification names verify event-based updates for Auto Queue cancellation/tier changes. Timers, display links, operation queues, and notification center references verify asynchronous state handling, but their precise transitions are not recoverable from static evidence alone.

### Localization

- English UI text is verified.
- Indonesian UI text is verified through numerous complete translated labels and descriptions.
- Portuguese and Turkish phrases are present, but static evidence does not establish complete locale coverage or key mapping.
- `useArabic` and Arabic-related selector names are present, but a complete Arabic string table was not recovered.

The clean project therefore ships **English and Indonesian only**. This is a conservative reconstruction, not a claim that those were the original binary's only runtime languages.

### Resources

The framework directory contains no standalone images, storyboards, nibs, asset catalogs, or `.lproj` folders. UIKit, SF Symbols/system images, programmatic layers, gradients, labels, switches, sliders, and stack views are referenced. Exact programmatic artwork cannot be recovered reliably from printable strings.

## 3. Dependencies and relationships

The overlay links 22 libraries/frameworks:

- Objective-C runtime, Foundation, CoreFoundation;
- UIKit, QuartzCore, CoreGraphics;
- AdSupport, AVFoundation, CoreTelephony, MobileCoreServices;
- Security, SystemConfiguration, CoreMedia, CFNetwork;
- JavaScriptCore, WebKit, StoreKit;
- zlib, libc++, libSystem;
- Swift Core and Swift Foundation.

Static symbols also reference Network/Security/CryptoKit operations. The rewarded-ad URL `https://omg10.com/4/1286848` is present. These dependencies belong to the compiled overlay and are **not** dependencies of the clean reconstruction.

Relationship summary:

```text
pool executable (original game)
  └─ LC_LOAD_DYLIB → libloader.framework (injected overlay)
       ├─ GBModMenu / GBMenu* UIKit UI
       ├─ GBPredictionDrawView and gameplay-facing systems
       ├─ UserDefaults / notifications / timers
       ├─ network, cryptography, account and activation systems
       └─ WebKit/StoreKit/AdSupport and rewarded-ad flow
```

## 4. Clean source reconstruction

Location: `CleanOverlay/`

The new project is an independent Swift Package for iOS 16+. It does not import, embed, patch, or communicate with the original game or `libloader`.

### Reconstructed

- floating closed button and expanded panel state;
- header, status badge, close control, sidebar, and scrollable content region;
- reusable module/card, feature tile, toggle row, meter row, segmented row, and key/value row components;
- local appearance/preferences/language/about screens;
- local JSON settings persistence and reset;
- English and Indonesian localizations;
- dark layered visual treatment inferred from the available UIKit/layer/component evidence;
- Swift Package, tests, example host plist, and Debug/Release xcconfig references.

### Verified basis

- menu component taxonomy and component input shapes;
- tabbed/sidebar structure and expand/collapse actions;
- English and Indonesian text presence;
- local preference persistence;
- use of UIKit controls, layers, gradients, SF Symbols/system images, scroll views, and stack views.

### Inferred

- exact reconstructed color palette, spacing, corner radii, panel size, and animations;
- mapping the legitimate clean screens to the recovered sidebar/card structure;
- local-only status semantics.

These choices are intentionally labeled as inferred because static binary strings do not establish pixel-accurate values.

### Not reproducible from available source

- pixel-identical original rendering;
- original proprietary assets or animations;
- original server/account/activation behavior;
- advertisements, subscription commerce, entitlement locks, device binding, or key activation;
- gameplay reading/drawing, prediction, aim assistance, Auto Play, Auto Queue, alerts derived from gameplay, or account reset;
- capture/stream hiding or other anti-detection behavior;
- original obfuscated implementation and runtime hooks.

## 5. Excluded functionality

Feature names that directly describe gameplay manipulation are retained only in this forensic document and inventory. They are not controls in the new source project. The clean project has:

- no game process access;
- no gameplay APIs or memory hooks;
- no network client;
- no ads or WebKit;
- no payment, StoreKit, subscriptions, keys, or activation;
- no identifiers or device binding;
- no screen-capture behavior;
- no original game resources.

## 6. Build status

The package is structured for Xcode 15+ (`Package.swift`, iOS 16 platform, products, resources, and XCTest target). This Linux environment has no Swift toolchain or Xcode, so compilation, simulator testing, signing, and export are unavailable here. Repository-level structural validation is recorded separately.

```text
NOT PRODUCED YET — SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```
