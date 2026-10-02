# Authorized production-host build command

The authoritative production checklist, immutable hashes, package/resource contract, expected Artifact C checks, and delta-review requirements are in:

```text
analysis/PRODUCTION_HANDOFF.md
analysis/HOST_INTEGRATION_CHECKLIST.md
analysis/PRODUCTION_MANIFEST.json
```

Run only after the authorized production host project, its host-owned presentation source, owner-approved baseline-coexistence contract, and legitimate Apple signing/provisioning/export inputs have been supplied.

```bash
bash ExistingIPAWorkspace/scripts/integrate-authorized-host-macos.sh \
  --container /absolute/path/to/AuthorizedHost.xcworkspace \
  --project /absolute/path/to/AuthorizedHost.xcodeproj \
  --scheme AuthorizedHost \
  --target AuthorizedHost \
  --integration-source /absolute/path/to/AuthorizedHost/OverlayIntegration.swift \
  --test-destination 'platform=iOS Simulator,name=iPhone 16' \
  --bundle-id com.example.authorizedhost \
  --team-id ABCDE12345 \
  --export-options /absolute/path/to/ExportOptions.plist \
  --configuration Release \
  --output-dir /absolute/path/to/empty-production-output
```

For a project container rather than a workspace, set both `--container` and `--project` to the authorized `.xcodeproj` path. `--target` may be omitted only when that project contains exactly one iOS application target; multiple candidates fail as ambiguous.

The pipeline fails before editing when the actual app target, resolved iOS 16+ settings, bundle ID, Team ID, signing configuration, export intent, host-owned presentation source, or installed signing identity is absent. It then links local package product `ExistingIPAOverlay`, runs the host tests, archives iPhoneOS, verifies the exact `ExistingIPAOverlay_ExistingIPAOverlayUI.bundle` resources, legitimately exports one IPA, validates signature/provisioning/arm64/component/deployment/bundle identity, rejects an Artifact-A no-op, records every file delta relative to Artifact A, and only then atomically publishes `final.ipa`, `final.sha256`, and `final-validation-report.json` to a new output path.

It does not patch, inject into, recompress, replace, or export Artifact A; does not copy or modify `libloader`; does not use the sample host as production; and does not fabricate signing.
