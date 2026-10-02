# Existing IPA Implementation Report

**Directive date:** 2026-10-02

**Reference artifact:** `8-ball-pool-i3rby-IPAOMTK.COM.ipa`

## 1. Verification and preservation

| Property | Verified value |
|---|---|
| Size | 98,576,945 bytes |
| SHA-256 | `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8` |
| Container | ZIP/IPA |
| ZIP members | 3,505 |
| Tracked Git blob | `6011d5cd4c7e61c407964fe949474984325b8253` |

The IPA was opened read-only. Its working-tree checksum and separately stored committed Git object are verified by `ExistingIPAWorkspace/Preservation/verify_original.sh`. No duplicate 95 MB artifact was added to the patch because the Git object is already an independently recoverable untouched copy.

## 2. Existing structure

- Payload: `Payload/`
- Application bundle: `Payload/pool.app`
- Identity: 8 Ball Pool 56.30.0 (5328), `com.miniclip.8ballpoolmult`
- Main executable: `Payload/pool.app/pool`, arm64, 69 `LC_LOAD_DYLIB` entries
- Standalone bundled dylib: `Frameworks/libswift_Concurrency.dylib`
- Framework entries: 26, including 24 host framework bundles, the injected `libloader.framework`, and the standalone Swift dylib entry
- Host localization directories: 17 (`ar`, `de`, `eng`, `es`, `fr`, `hi`, `id`, `it`, `ja`, `ko`, `kor`, `pt-BR`, `pt-PT`, `pt`, `ru`, `tr`, `vi`)
- Other resources: Cocos layouts, property lists, sprites/images, audio, fonts, JSON/data, bundles, and plug-ins

The complete member-by-member inventory—not a sample—is `ExistingIPAWorkspace/Inventory/IPA_FILE_INVENTORY.json`. Each entry records path, directory flag, uncompressed and compressed size, CRC32, uncompressed SHA-256, classification, and classification reason.

## 3. Strict ownership classification

### ORIGINAL GAME

3,494 structural entries, 110,720,943 uncompressed bytes. This category includes host resources, localizations, plug-ins, and bundled dependencies outside the injected overlay.

`ORIGINAL_GAME` means structurally attributable to the host bundle. It does not claim pristine provenance for every byte.

### EXISTING OVERLAY

5 entries, 11,496,935 uncompressed bytes:

- `Payload/pool.app/Frameworks/libloader.framework/`
- its `Info.plist`
- its 11,493,804-byte arm64 `libloader` binary
- framework signature directory and `CodeResources`

The host executable loads it through `@executable_path/Frameworks/libloader.framework/libloader`.

### UNKNOWN

6 entries, 83,090,739 uncompressed bytes:

- the main executable, because it is original-game code with an added overlay load command;
- host `Info.plist`, because it includes post-build redistribution/overlay changes;
- host `_CodeSignature/CodeResources`, because it covers the injected framework;
- `SC_Info/` and its placeholder, because provenance cannot be treated as original;
- any mixed/post-injection component that cannot be attributed without guessing.

## 4. Frameworks and dependencies

Host framework entries are listed in full in the JSON inventory and include AdSurgeSDK, AppLovinSDK, BigoADS, DTBiOSSDK, FBAudienceNetwork, Firebase components, Google measurement/utilities components, InMobiSDK, MolocoSDK, OMSDK_Appodeal, Promises, nanopb, and others.

The existing overlay links Objective-C/Foundation/CoreFoundation, UIKit/QuartzCore/CoreGraphics, AdSupport, AVFoundation, CoreTelephony, MobileCoreServices, Security, SystemConfiguration, CoreMedia, CFNetwork, JavaScriptCore, WebKit, StoreKit, zlib, libc++, libSystem, Swift Core, and Swift Foundation.

Detailed overlay UI/state/configuration/localization findings remain in `OVERLAY_ARCHITECTURE.md` and `inspection/OVERLAY_INVENTORY.json`.

## 5. Source implementation tied to this IPA

The previously separate source scaffold was moved under:

```text
ExistingIPAWorkspace/OverlaySource/
```

It is now explicitly an integration component associated with the existing IPA, not a replacement application. There is no application target, alternate game, or renamed IPA. The package reproduces permitted menu-shell and local interface settings patterns only.

It excludes game process access, gameplay prediction, aim assistance, Auto Play, Auto Queue, account manipulation, ads, subscriptions, payment, activation, identifiers, networking, and capture/detection evasion.

## 6. Integration boundary

The existing IPA is a compiled app bundle, not an authorized host Xcode source project. Inserting a new executable component into it would change signed bytes and require binary injection/load-command changes plus new provisioning and signing. Those operations were not performed.

The maintainable package can only be integrated through an authorized source-level host build. Required steps are recorded in `ExistingIPAWorkspace/INTEGRATION_STATUS.md`.

## 7. Validation performed

- Original working IPA SHA-256 verification
- Committed Git-blob SHA-256 verification
- All 3,505 ZIP members read and hashed
- Complete inventory regenerated and JSON-parsed
- Existing overlay inventory regenerated deterministically
- Swift source structural validation
- EN/ID localization key parity
- Excluded dependency/functionality checks
- plist parsing
- release manifest JSON parsing
- Git whitespace validation

Xcode compilation and iOS runtime testing were not possible because the environment has no Xcode or Swift toolchain.

## 8. Output

No modified IPA, modified checksum, signature, installation result, or export result exists.

```text
NOT PRODUCED YET — BUILD/SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```
