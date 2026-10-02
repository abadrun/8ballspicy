# Build output

## Produced artifact

`ExistingIPAOverlay-ios-device-build.zip` is a real, unsigned Swift package component build produced on a GitHub-hosted macOS 15 runner with Xcode. It was built for the generic `iphoneos` destination, not Simulator.

- Workflow: [36972215349](https://github.com/abadrun/8ballspicy/actions/runs/36972215349)
- Job: `110728374128`
- Swift package tests: passed
- Device build: passed
- Device validation: passed by `../ExistingIPAWorkspace/scripts/validate-device-component.py`
- Product directory: `Debug-iphoneos`
- Architecture: `arm64`
- Size: `354250` bytes
- SHA-256: `f30c228a23e2496aab4b2cb55ce17ae9b00425737b75ebb14cc804b587d31043`

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
