# Build output

## Produced artifact

`ExistingIPAOverlay-ios-device-build.zip` is a real, unsigned Swift package component build produced on a GitHub-hosted macOS 15 runner with Xcode. It was built for the generic `iphoneos` destination, not Simulator.

- Workflow: [36972725882](https://github.com/abadrun/8ballspicy/actions/runs/36972725882)
- Job: `110729927269`
- Swift package tests: passed
- Device build: passed
- Device validation: passed by `../ExistingIPAWorkspace/scripts/validate-device-component.py`
- Product directory: `Debug-iphoneos`
- Architecture: `arm64`
- Size: `354246` bytes
- SHA-256: `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`

The ZIP contains the compiled arm64 object products, Swift modules, and processed resource bundle for `ExistingIPAOverlay`. It is a **component build**, not an IPA, and is deliberately unsigned because it has no host application, provisioning profile, or Apple signing identity.

The accepted local ZIP above remains unchanged. Full readiness workflow [37018507081](https://github.com/abadrun/8ballspicy/actions/runs/37018507081) also produced byte-reproducible Simulator and iPhoneOS arm64 component archives as Actions artifact `ExistingIPAOverlay-reproducible-builds` (ID `11231528753`):

- Simulator SHA-256: `9b6c20bc5113c6aa0930c0d1702377a6e087b2001f14f25e25dff55af1cfdbe5`
- Device SHA-256: `3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f`

They passed two-clean-build byte comparison and independent component validation. They are additional unsigned components, not replacements for the accepted ZIP and not IPAs.

## Host and signing boundary

The repository was checked on the current branch, all remote branches, repository paths, and available Actions artifacts. No authorized Xcode host project or workspace for `pool.app` exists. `mr-spicy-ui/swift/` is explicitly a neutral standalone reference source, not an authorized host project for the supplied third-party game. The component was therefore not injected into `Payload/pool.app`, and the original IPA was not modified.

A signed IPA still requires an authorized host `.xcodeproj` or `.xcworkspace`, source-level integration, entitlements, provisioning, a developer signing identity, archive/export, and device launch validation. No IPA is claimed or produced here.

The previous `8-ball-pool-modified.ipa` no-op repackaging and its checksum were removed from `output/`; they were never a modified release.

## Reproducible checks

```bash
python3 ExistingIPAWorkspace/scripts/validate-device-component.py \
  output/ExistingIPAOverlay-ios-device-build.zip
sha256sum output/ExistingIPAOverlay-ios-device-build.zip
unzip -t output/ExistingIPAOverlay-ios-device-build.zip
```
