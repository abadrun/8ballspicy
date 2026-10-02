#!/usr/bin/env bash
# Archive an authorized iOS host only after its owner supplies legitimate signing inputs.
# This script does not inspect, patch, inject, or repackage the supplied third-party IPA.
set -euo pipefail

readonly COMPONENT_SHA256="c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b"

usage() {
  cat >&2 <<'EOF'
Usage:
  archive-authorized-host-macos.sh \
    --container /path/to/AuthorizedHost.xcodeproj-or-xcworkspace \
    --scheme AuthorizedHost \
    --target AuthorizedHost \
    --integration-source /path/to/host-owned/OverlayIntegration.swift \
    --test-destination 'platform=iOS Simulator,name=iPhone 16' \
    --bundle-id com.example.authorizedhost \
    --team-id APPLE_TEAM_ID \
    --export-options /path/to/ExportOptions.plist \
    [--project /path/to/AuthorizedHost.xcodeproj] \
    [--configuration Release] [--output-dir /path/to/output]

--container must be an authorized Xcode project or workspace. When it is a
workspace, --project identifies the authorized app project to configure.

The host-owned --integration-source must already import ExistingIPAOverlay and
reference ExistingIPAOverlayView. The script links the local Swift package to
--target, runs the host tests, archives iphoneos, exports output/final.ipa,
validates the signed IPA, and writes output/final.sha256.
EOF
  exit 2
}

container=""; project=""; scheme=""; target=""; integration_source=""; test_destination=""
bundle_id=""; team=""; export_options=""; configuration="Release"; output_dir=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --container) container="$2"; shift 2 ;;
    --project) project="$2"; shift 2 ;;
    --scheme) scheme="$2"; shift 2 ;;
    --target) target="$2"; shift 2 ;;
    --integration-source) integration_source="$2"; shift 2 ;;
    --test-destination) test_destination="$2"; shift 2 ;;
    --bundle-id) bundle_id="$2"; shift 2 ;;
    --team-id) team="$2"; shift 2 ;;
    --export-options) export_options="$2"; shift 2 ;;
    --configuration) configuration="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ -n "$container" && -n "$scheme" && -n "$target" && -n "$integration_source" && -n "$test_destination" ]] || usage
[[ -n "$bundle_id" && -n "$team" && -n "$export_options" ]] || usage
[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS is required" >&2; exit 2; }
for tool in xcodebuild codesign security shasum unzip python3; do
  command -v "$tool" >/dev/null || { echo "ERROR: missing $tool" >&2; exit 2; }
done

case "$container" in
  *.xcodeproj|*.xcworkspace) ;;
  *) echo "ERROR: --container must be an authorized .xcodeproj or .xcworkspace, never an IPA" >&2; exit 2 ;;
esac
[[ -e "$container" ]] || { echo "ERROR: host container not found: $container" >&2; exit 2; }
[[ -f "$integration_source" ]] || { echo "ERROR: host-owned integration source not found: $integration_source" >&2; exit 2; }
[[ -f "$export_options" ]] || { echo "ERROR: export options not found: $export_options" >&2; exit 2; }

if [[ -z "$project" ]]; then
  [[ "$container" == *.xcodeproj ]] || { echo "ERROR: --project is required when --container is a workspace" >&2; exit 2; }
  project="$container"
fi
[[ "$project" == *.xcodeproj && -d "$project" ]] || { echo "ERROR: --project must be an authorized .xcodeproj directory" >&2; exit 2; }

repo_root="$(git rev-parse --show-toplevel)"
workspace_root="$repo_root/ExistingIPAWorkspace"
package_root="$workspace_root/OverlaySource"
component="$repo_root/output/ExistingIPAOverlay-ios-device-build.zip"
output_dir="${output_dir:-$repo_root/output}"
archive_path="$repo_root/.build/AuthorizedHost.xcarchive"
export_path="$repo_root/.build/AuthorizedHostExport"
final="$output_dir/final.ipa"
validator="$workspace_root/scripts/validate-final-ipa.py"
configurator="$workspace_root/scripts/configure-authorized-host-package.py"

[[ -f "$component" ]] || { echo "ERROR: verified device component is missing: $component" >&2; exit 2; }
actual_component_sha="$(shasum -a 256 "$component" | awk '{print $1}')"
[[ "$actual_component_sha" == "$COMPONENT_SHA256" ]] || {
  echo "ERROR: verified component checksum mismatch; host integration is blocked" >&2
  exit 3
}
unzip -tqq "$component"
[[ -f "$package_root/Package.swift" ]] || { echo "ERROR: ExistingIPAOverlay package source is missing" >&2; exit 2; }

# Do not manufacture a host integration point. It must be supplied by the
# authorized host owner and explicitly reference the package product.
grep -Fq "import ExistingIPAOverlay" "$integration_source" || {
  echo "ERROR: host integration source does not import ExistingIPAOverlay" >&2
  exit 4
}
grep -Fq "ExistingIPAOverlayView" "$integration_source" || {
  echo "ERROR: host integration source does not reference ExistingIPAOverlayView" >&2
  exit 4
}

# The preservation check is read-only and prevents accidentally using a changed
# third-party baseline as a substitute for an authorized host.
bash "$workspace_root/Preservation/verify_original.sh"
python3 "$configurator" --project "$project" --target "$target" --package-path "$package_root" --apply

build_flag=(-project "$container")
[[ "$container" == *.xcworkspace ]] && build_flag=(-workspace "$container")

# Confirm a real signing identity exists before any archive/export work. No
# identity, certificate, profile, or provisioning data is created by this script.
if ! security find-identity -v -p codesigning | grep -Eq '[1-9][0-9]* valid identities found'; then
  echo "ERROR: no legitimate Apple code-signing identity is installed" >&2
  exit 5
fi

mkdir -p "$output_dir" "$export_path"
rm -rf "$archive_path" "$export_path"

xcodebuild "${build_flag[@]}" -scheme "$scheme" -resolvePackageDependencies
xcodebuild "${build_flag[@]}" \
  -scheme "$scheme" \
  -configuration Debug \
  -destination "$test_destination" \
  test
xcodebuild "${build_flag[@]}" \
  -scheme "$scheme" \
  -configuration "$configuration" \
  -destination 'generic/platform=iOS' \
  -archivePath "$archive_path" \
  DEVELOPMENT_TEAM="$team" \
  PRODUCT_BUNDLE_IDENTIFIER="$bundle_id" \
  archive

apps=("$archive_path"/Products/Applications/*.app)
[[ ${#apps[@]} -eq 1 && -d "${apps[0]}" ]] || {
  echo "ERROR: archive does not contain exactly one application bundle" >&2
  exit 6
}
codesign --verify --deep --strict --verbose=2 "${apps[0]}"

xcodebuild -exportArchive \
  -archivePath "$archive_path" \
  -exportPath "$export_path" \
  -exportOptionsPlist "$export_options"

ipa_count="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | wc -l | tr -d ' ')"
[[ "$ipa_count" == "1" ]] || { echo "ERROR: expected exactly one exported IPA, found $ipa_count" >&2; exit 7; }
exported_ipa="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | head -n 1)"
rm -f "$final" "$final.sha256"
cp -p "$exported_ipa" "$final"

python3 "$validator" "$final" \
  --require-signature \
  --require-provisioning \
  --require-arm64 \
  --require-component ExistingIPAOverlay \
  --codesign-verify \
  --bundle-id "$bundle_id"
shasum -a 256 "$final" > "$final.sha256"
printf 'DONE: %s\n' "$final"
cat "$final.sha256"
