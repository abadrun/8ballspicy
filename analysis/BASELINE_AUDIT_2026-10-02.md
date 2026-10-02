# Baseline Intake Audit — 2026-10-02

This is the pre-change intake record for the existing i3rby-modified artifact. It treats that artifact as **baseline A**, not as an untouched upstream game and not as a substitute for a genuinely integrated final IPA.

## 1. Artifact separation and current status

| Artifact | Role | SHA-256 | Status |
|---|---|---|---|
| A — `8-ball-pool-i3rby-IPAOMTK.COM.ipa` | Existing i3rby-modified baseline | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` | Verified, inventoried, preserved unchanged |
| B — `output/ExistingIPAOverlay-ios-device-build.zip` | Authorized add-on/device component | `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b` | Verified unsigned arm64 `iphoneos` component; **not an IPA** |
| C — final integrated IPA | Authorized host application plus B | — | **NOT PRODUCED** |

A and B are separate inputs. The existence of B is not evidence that C exists.

## 2. Pre-change verification and temporary extraction

The repository was clean before the intake pass. The baseline was hashed first, ZIP-tested, then safely extracted to a system-generated `/tmp/8ballspicy-baseline.*` working directory. The temporary extraction was deleted after inspection; the tracked IPA was never written to.

Reproducible procedure:

```bash
sha256sum 8-ball-pool-i3rby-IPAOMTK.COM.ipa
unzip -t 8-ball-pool-i3rby-IPAOMTK.COM.ipa
work="$(mktemp -d /tmp/8ballspicy-baseline.XXXXXX)"
python3 inspection/inspect_ipa.py \
  8-ball-pool-i3rby-IPAOMTK.COM.ipa \
  --extract-to "$work"
rm -rf "$work"
```

Verified values:

| Property | Value |
|---|---|
| IPA size | 98,576,945 bytes |
| SHA-256 | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` |
| ZIP integrity | Passed; no bad member |
| ZIP entries | 3,505: 3,344 files and 161 directories |
| Extracted file bytes | 205,308,617 |
| Top-level payload | `Payload/` |
| Sole app bundle | `Payload/pool.app` |
| Tracked Git blob | `6011d5cd4c7e61c407964fe949474984325b8253` |

`ExistingIPAWorkspace/Preservation/verify_original.sh` independently verifies both the working file and the committed Git blob against the same SHA-256.

## 3. Application and Info.plist inventory

| Property | Value |
|---|---|
| Display name | 8 Ball Pool |
| Bundle identifier | `com.miniclip.8ballpoolmult` |
| Version / build | 56.30.0 / 5328 |
| Main executable | `Payload/pool.app/pool` |
| Minimum OS | iOS 13.0 |
| App `Info.plist` | XML plist, 66 keys, SHA-256 `84572f30773e74ca2fdd1688631bd5b5ab12c12f629d38504532bc107858dd23` |
| Main executable architecture | arm64 |
| Main executable encryption field | `cryptid = 0` |
| Main load commands | 69 `LC_LOAD_DYLIB` entries |
| Existing overlay load reference | `@executable_path/Frameworks/libloader.framework/libloader` (final load entry) |

Post-upstream indicators in the application plist include:

- `DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"`;
- `NSUserTrackingUsageDescription = "Used to bind your subscription key to this device and protect your activation."`.

The complete key list and selected values are under `applicationInfoPlist` in `ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json`; its per-member entry records the exact plist hash, size, CRC, and classification.

## 4. Embedded code, bundle identifiers, and architectures

The app contains 25 framework bundles, one standalone dylib, and four app extensions. All 31 detected Mach-O binaries have only an **arm64** slice.

| Framework | Bundle identifier | Attribution |
|---|---|---|
| AdSurgeSDK | `com.AdSurge.ADN` | Host-bundled dependency |
| AppLovinSDK | `com.applovin.sdk` | Host-bundled dependency |
| BigoADS | `org.cocoapods.BigoADS` | Host-bundled dependency |
| DTBiOSSDK | `com.a9.pdp.DTBiOSSDK` | Host-bundled dependency |
| FBAudienceNetwork | `com.facebook.FBAudienceNetwork` | Host-bundled dependency |
| FBLPromises | `org.cocoapods.FBLPromises` | Host-bundled dependency |
| FirebaseAnalytics | `org.cocoapods.FirebaseAnalytics` | Host-bundled dependency |
| FirebaseCore | `org.cocoapods.FirebaseCore` | Host-bundled dependency |
| FirebaseCoreExtension | `org.cocoapods.FirebaseCoreExtension` | Host-bundled dependency |
| FirebaseCoreInternal | `org.cocoapods.FirebaseCoreInternal` | Host-bundled dependency |
| FirebaseCrashlytics | `org.cocoapods.FirebaseCrashlytics` | Host-bundled dependency |
| FirebaseInstallations | `org.cocoapods.FirebaseInstallations` | Host-bundled dependency |
| FirebaseRemoteConfigInterop | `org.cocoapods.FirebaseRemoteConfigInterop` | Host-bundled dependency |
| FirebaseSessions | `org.cocoapods.FirebaseSessions` | Host-bundled dependency |
| GoogleAdsOnDeviceConversion | `com.google.ads.GoogleAdsOnDeviceConversion` | Host-bundled dependency |
| GoogleAppMeasurement | `org.cocoapods.GoogleAppMeasurement` | Host-bundled dependency |
| GoogleAppMeasurementIdentitySupport | `org.cocoapods.GoogleAppMeasurementIdentitySupport` | Host-bundled dependency |
| GoogleDataTransport | `org.cocoapods.GoogleDataTransport` | Host-bundled dependency |
| GoogleUtilities | `org.cocoapods.GoogleUtilities` | Host-bundled dependency |
| InMobiSDK | `com.inmobi.InMobiSDK` | Host-bundled dependency |
| MolocoSDK | `com.moloco.ads.sdk.core` | Host-bundled dependency |
| OMSDK_Appodeal | `com.iabtechlab.omsdk` | Host-bundled dependency |
| Promises | `org.cocoapods.Promises` | Host-bundled dependency |
| nanopb | `org.cocoapods.nanopb` | Host-bundled dependency |
| **libloader** | **`com.appdome.libloader`** | **Existing i3rby overlay** |

Standalone dylib:

- `Payload/pool.app/Frameworks/libswift_Concurrency.dylib` — arm64.

App extension bundle identifiers:

- `com.miniclip.8ballpoolmult.notificationContent`;
- `com.miniclip.8ballpoolmult.notificationService`;
- `com.miniclip.8ballpoolmult.poolWidget`;
- `com.miniclip.8ballpoolmult.PooliMessage`.

The machine inventory contains all **43** discovered bundle identifiers, including framework privacy/resource bundles, along with every binary path, slice, size, and SHA-256.

## 5. Resources

The bundle has 16 `.bundle` resource containers and 17 direct host localization directories (`ar`, `de`, `eng`, `es`, `fr`, `hi`, `id`, `it`, `ja`, `ko`, `kor`, `pt-BR`, `pt-PT`, `pt`, `ru`, `tr`, `vi`). Dominant file types are:

| Type | Files | Uncompressed bytes |
|---|---:|---:|
| PNG | 1,326 | 21,880,414 |
| plist | 819 | 26,601,718 |
| Cocos `.ccbi` | 688 | 1,713,020 |
| MP3 | 142 | 5,009,425 |
| `.strings` | 83 | 26,833 |
| atlas | 45 | 77,305 |
| JSON | 42 | 2,058,390 |
| nib | 23 | 127,583 |
| skeleton data | 23 | 731,906 |
| privacy manifests | 18 | 29,875 |

Every archive member—not only these summaries—is listed with its exact hash and classification in `ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json`.

## 6. Exact existing i3rby modification boundary

### Wholly attributable overlay members

The five archive entries wholly classified as `EXISTING_OVERLAY` are:

1. `Payload/pool.app/Frameworks/libloader.framework/`;
2. `Payload/pool.app/Frameworks/libloader.framework/Info.plist`;
3. `Payload/pool.app/Frameworks/libloader.framework/libloader`;
4. `Payload/pool.app/Frameworks/libloader.framework/_CodeSignature/`;
5. `Payload/pool.app/Frameworks/libloader.framework/_CodeSignature/CodeResources`.

The binary is an 11,493,804-byte arm64 Mach-O. Although its framework bundle ID is `com.appdome.libloader`, the binary contains direct i3rby persistent-domain markers:

- `com.i3rby.8poolmod.autoqueue.tiercode.v1`;
- `com.i3rby.8poolmod.tg.ad_session_id`;
- `com.i3rby.8poolmod.tg.ad_session_scope`;
- `com.i3rby.autoplay` and `com.i3rby.autoplay.debug`;
- `com.i3rby.breaklog` and `com.i3rby.breaklog.debug`.

This gives high-confidence attribution independently of the IPA filename.

### Mixed or post-injection members

These are part of the modified baseline but are not classified as wholly i3rby-owned:

- `Payload/pool.app/pool` — original host executable plus the injected `libloader` load command;
- `Payload/pool.app/Info.plist` — host metadata plus redistribution/overlay licensing changes;
- `Payload/pool.app/_CodeSignature/CodeResources` — post-injection signature manifest covering `libloader.framework`;
- `Payload/pool.app/SC_Info/.keep` and its directory — redistribution placeholder after FairPlay metadata removal.

These remain `UNKNOWN`/mixed in the inventory rather than being falsely attributed in full. The other 3,494 structural entries are outside the injected overlay and are labeled `ORIGINAL_GAME` only in the structural sense; that label does **not** assert pristine or lawful provenance.

## 7. Behavior and preservation boundary

Static evidence identifies the existing overlay as a compiled multiplayer-game modification with aim/prediction, Auto Play/Auto Queue, capture-evasion, rewarded-ad grants, and paid/server-backed entitlement behavior. The baseline contains vendor session and licensing flows, including `com.i3rby.*` state.

Preserving the baseline means retaining its bytes as the reference artifact and documenting its behavior. It does **not** authorize defeating its PRO licensing, rewarded-ad grants, server authorization, tamper checks, anti-cheat, or multiplayer protections. No such bypass was attempted.

## 8. Delta and build decision

Changes made in this pass are limited to inspection tooling, generated inventory, and documentation. Delta from A:

- application files changed: **0**;
- application files added/removed: **0**;
- baseline SHA-256 before/after: **unchanged**;
- component B integrated into A: **no**;
- no-op recompressed IPA produced: **no**;
- final IPA C produced: **no**.

No authorized host Xcode project/workspace or legitimate Apple signing configuration exists in the repository. Therefore source-level host integration, signing, archive/export, and physical-device validation remain blocked. Binary injection into the compiled third-party bundle is not used as a substitute.
