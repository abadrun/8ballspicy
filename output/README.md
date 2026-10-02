# Build output

## Produced artifact

`ExistingIPAOverlay-ios-device-build.zip` is a real, unsigned Swift package component build produced on a GitHub-hosted macOS 15 runner with Xcode. It was built for the generic `iphoneos` destination, not Simulator.

- Workflow: [36971984879](https://github.com/abadrun/8ballspicy/actions/runs/36971984879)
- Job: `110727667475`
- Swift package tests: passed
- Device build: passed
- Device validation: passed by `../ExistingIPAWorkspace/scripts/validate-device-component.py`
- Product directory: `Debug-iphoneos`
- Architecture: `arm64`
- Size: `354250` bytes
- SHA-256: `ec0a0affd2c24413f3c053a58ec02c3eec3654700887d6c5777a5fcf087e7c05`

The ZIP contains the compiled arm64 object products, Swift modules, and processed resource bundle for `ExistingIPAOverlay`. It is a **component build**, not an IPA, and is deliberately unsigned because it has no host application, provisioning profile, or Apple signing identity.

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
