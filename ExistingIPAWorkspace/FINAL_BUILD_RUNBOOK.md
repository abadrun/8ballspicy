# Authorized host final-build command

Run only after the authorized host project, its host-owned overlay integration
source, and legitimate Apple signing/provisioning inputs have been supplied.

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
  --output-dir "$PWD/output"
```

For a project container rather than a workspace, set both `--container` and
`--project` to the authorized `.xcodeproj` path. The command verifies the frozen
component checksum, links the local `ExistingIPAOverlay` package to the named
host target, requires a host-owned `ExistingIPAOverlayView` reference, runs host
tests, archives for generic iOS, exports `output/final.ipa`, validates it, and
writes `output/final.sha256`.
