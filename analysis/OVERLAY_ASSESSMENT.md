# Existing IPA and Overlay Assessment

**Date:** 2026-10-02  
**Input:** `8-ball-pool-i3rby-IPAOMTK.COM.ipa`  
**Inspection mode:** read-only

## Result

The input is a valid ZIP/IPA container containing `Payload/pool.app`, identified as 8 Ball Pool 56.30.0 (build 5328), bundle identifier `com.miniclip.8ballpoolmult`.

The existing overlay is `Payload/pool.app/Frameworks/libloader.framework`. It is loaded by the app executable through:

```text
@executable_path/Frameworks/libloader.framework/libloader
```

The framework is an 11,493,804-byte compiled arm64 Mach-O binary. No overlay source project or editable source files are present in the repository or IPA.

Static inspection finds overlay-owned strings and classes for:

- `GBModMenu` and `GBMenu*` UI classes;
- aim assistance, prediction lines, Auto Play, and Auto Queue;
- subscription-key activation and PRO gating;
- a rewarded-ad endpoint;
- hiding overlay elements from captures/streams.

The host executable has `cryptid = 0`, the IPA includes a `DecryptedBy` marker, and only a placeholder remains under `SC_Info`. These are consistent with a FairPlay-stripped, redistributed app bundle. The IPA has no `embedded.mobileprovision`.

## Modification decision

No binary patch, license/activation bypass, ad-gating bypass, re-signing, or IPA repackaging was performed.

The requested change would require altering a compiled multiplayer-cheat binary to bypass its paid activation controls and redistributing it inside a DRM-stripped third-party game. There is also no authorized overlay source in the repository on which to make a normal source-level configuration change.

If the overlay owner supplies an authorized source project, a safe implementation path is to remove the overlay's monetization modules at source level, make its legitimate non-gameplay features available through ordinary configuration, build with the owner's signing identity, and test against an authorized host application. Gameplay automation, anti-detection, and third-party entitlement bypasses would remain out of scope.

## Output status

```text
NOT PRODUCED YET — BUILD/SIGNING/EXPORT REQUIRES DEVELOPER ACTION
```

The following requested artifacts were **not** created because no legitimate build/package process produced them:

- `8 Ball Pool Modified.ipa`
- `8 Ball Pool Modified.sha256`

`output/release-manifest.json` records this status without claiming a build.

## Continuation

A subsequent clean-room, source-level reconstruction of legitimate UI and local-configuration patterns is now available under `CleanOverlay/`. It does not change the findings above and is not a reconstruction of gameplay, activation, advertising, or anti-detection behavior. See `OVERLAY_ARCHITECTURE.md` for the detailed evidence and reconstruction classification.

## Reproduction

Run:

```bash
python3 inspection/inspect_ipa.py
```

Source IPA SHA-256:

```text
59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8
```
