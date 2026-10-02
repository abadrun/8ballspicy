#!/usr/bin/env bash
# Build/export only an owner-supplied authorized iOS host.
# This script never patches, injects into, recompresses, replaces, or exports the
# preserved baseline IPA and never creates signing identities or profiles.
set -euo pipefail

readonly BASELINE_IPA_SHA256="59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8"
readonly ACCEPTED_COMPONENT_SHA256="c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b"
readonly MINIMUM_IOS="16.0"
readonly RESOURCE_BUNDLE="ExistingIPAOverlay_ExistingIPAOverlayUI.bundle"

usage() {
  cat >&2 <<'EOF'
Usage:
  integrate-authorized-host-macos.sh \
    --container /path/to/AuthorizedHost.xcodeproj-or-xcworkspace \
    --scheme AuthorizedHost \
    --integration-source /path/to/host-owned/OverlayIntegration.swift \
    --test-destination 'platform=iOS Simulator,name=iPhone 16' \
    --bundle-id com.example.authorizedhost \
    --team-id ABCDE12345 \
    --export-options /path/to/ExportOptions.plist \
    [--project /path/to/AuthorizedHost.xcodeproj] \
    [--target AuthorizedHost] \
    [--configuration Release] [--output-dir /empty/output/directory]

--container must be an owner-supplied authorized Xcode project or workspace,
never an IPA. For a workspace, --project identifies the authorized app project.
Omit --target only when that project contains exactly one iOS application
target; multiple app targets are rejected as ambiguous.

The production target must already resolve to iOS 16.0+, the exact bundle ID
and Team ID supplied above, enabled code signing, and an application product.
The host-owned source must import ExistingIPAOverlayUI and construct
ExistingIPAOverlayView. ExportOptions.plist must contain the same teamID and a
real export method. A valid installed Apple code-signing identity is mandatory.

On success only, this script writes a new output/final.ipa, final.sha256, and
final-validation-report.json after the exported IPA has passed structure,
arm64, resources, signature, provisioning, bundle identity, deployment-target,
component-evidence, and Artifact-A file-delta recording.
EOF
  exit 2
}

container=""; project=""; scheme=""; target=""; integration_source=""; test_destination=""
bundle_id=""; team=""; export_options=""; configuration="Release"; output_dir=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --container) [[ $# -ge 2 ]] || usage; container="$2"; shift 2 ;;
    --project) [[ $# -ge 2 ]] || usage; project="$2"; shift 2 ;;
    --scheme) [[ $# -ge 2 ]] || usage; scheme="$2"; shift 2 ;;
    --target) [[ $# -ge 2 ]] || usage; target="$2"; shift 2 ;;
    --integration-source) [[ $# -ge 2 ]] || usage; integration_source="$2"; shift 2 ;;
    --test-destination) [[ $# -ge 2 ]] || usage; test_destination="$2"; shift 2 ;;
    --bundle-id) [[ $# -ge 2 ]] || usage; bundle_id="$2"; shift 2 ;;
    --team-id) [[ $# -ge 2 ]] || usage; team="$2"; shift 2 ;;
    --export-options) [[ $# -ge 2 ]] || usage; export_options="$2"; shift 2 ;;
    --configuration) [[ $# -ge 2 ]] || usage; configuration="$2"; shift 2 ;;
    --output-dir) [[ $# -ge 2 ]] || usage; output_dir="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage ;;
  esac
done

[[ -n "$container" ]] || {
  echo "ERROR: Production host not supplied. Provide the authorized .xcodeproj/.xcworkspace and legitimate signing/export configuration." >&2
  exit 2
}
[[ -n "$scheme" ]] || { echo "ERROR: authorized production scheme is required (--scheme)" >&2; exit 2; }
[[ -n "$integration_source" ]] || { echo "ERROR: host-owned presentation source is required (--integration-source)" >&2; exit 2; }
[[ -n "$test_destination" ]] || { echo "ERROR: an iOS Simulator test destination is required (--test-destination)" >&2; exit 2; }
[[ -n "$bundle_id" ]] || { echo "ERROR: authorized production bundle identifier is required (--bundle-id)" >&2; exit 2; }
[[ -n "$team" ]] || { echo "ERROR: legitimate Apple Team ID is required (--team-id)" >&2; exit 2; }
[[ -n "$export_options" ]] || { echo "ERROR: legitimate export configuration is required (--export-options)" >&2; exit 2; }

case "$container" in
  *.xcodeproj|*.xcworkspace) ;;
  *.ipa) echo "ERROR: an IPA cannot be used as a host; supply an authorized Xcode project/workspace" >&2; exit 2 ;;
  *) echo "ERROR: --container must be an authorized .xcodeproj or .xcworkspace" >&2; exit 2 ;;
esac
[[ -e "$container" ]] || { echo "ERROR: authorized host container does not exist: $container" >&2; exit 2; }

if [[ -z "$project" ]]; then
  [[ "$container" == *.xcodeproj ]] || {
    echo "ERROR: --project is required to identify the app target when --container is a workspace" >&2
    exit 2
  }
  project="$container"
fi
[[ "$project" == *.xcodeproj && -d "$project" && -f "$project/project.pbxproj" ]] || {
  echo "ERROR: authorized host project is missing or invalid: $project" >&2
  exit 2
}
script_dir="$(cd "$(dirname "$0")" && pwd)"
target_identifier="$script_dir/identify-authorized-host-target.py"
[[ -f "$target_identifier" ]] || { echo "ERROR: application-target identification tool is missing" >&2; exit 2; }
command -v python3 >/dev/null || { echo "ERROR: required production tool is missing: python3" >&2; exit 2; }
if [[ -n "$target" ]]; then
  target="$(python3 "$target_identifier" --project "$project" --target "$target")"
else
  target="$(python3 "$target_identifier" --project "$project")"
  printf 'AUTO-IDENTIFIED PRODUCTION APP TARGET: %s\n' "$target"
fi
[[ -f "$integration_source" ]] || { echo "ERROR: host-owned integration source is missing: $integration_source" >&2; exit 2; }
[[ -f "$export_options" ]] || { echo "ERROR: ExportOptions.plist is missing: $export_options" >&2; exit 2; }
[[ "$team" =~ ^[A-Z0-9]{10}$ ]] || { echo "ERROR: Apple Team ID must be exactly 10 uppercase letters/digits" >&2; exit 2; }
[[ "$bundle_id" =~ ^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$ ]] || { echo "ERROR: bundle identifier is not a resolved reverse-DNS identifier" >&2; exit 2; }
[[ "$bundle_id" != "com.example.ExistingIPAOverlaySampleHost" ]] || {
  echo "ERROR: the repository sample host is test evidence, not an authorized production host" >&2
  exit 2
}

# Path/input failures above are intentionally reported even on non-macOS hosts.
[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS with Xcode is required after host-input preflight" >&2; exit 2; }
for tool in xcodebuild codesign security shasum unzip python3; do
  command -v "$tool" >/dev/null || { echo "ERROR: required production tool is missing: $tool" >&2; exit 2; }
done

repo_root="$(git rev-parse --show-toplevel)"
workspace_root="$repo_root/ExistingIPAWorkspace"
package_root="$workspace_root/OverlaySource"
component="$repo_root/output/ExistingIPAOverlay-ios-device-build.zip"
baseline="$repo_root/8-ball-pool-i3rby-IPAOMTK.COM.ipa"
output_dir="${output_dir:-$repo_root/output}"
archive_path="$repo_root/.build/AuthorizedHost.xcarchive"
export_path="$repo_root/.build/AuthorizedHostExport"
settings_path="$repo_root/.build/AuthorizedHost-build-settings.json"
final="$output_dir/final.ipa"
final_hash="$output_dir/final.sha256"
final_report="$output_dir/final-validation-report.json"
validation_report="$export_path/final-validation-report.json"
validator="$workspace_root/scripts/validate-final-ipa.py"
configurator="$workspace_root/scripts/configure-authorized-host-package.py"
host_settings_validator="$workspace_root/scripts/validate-authorized-host-settings.py"
project_resolved="$(cd "$(dirname "$project")" && pwd)/$(basename "$project")"
final_resolved="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$final")"
baseline_resolved="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$baseline")"
[[ "$final_resolved" != "$baseline_resolved" ]] || {
  echo "ERROR: final output path resolves to Artifact A; baseline overwrite is forbidden" >&2
  exit 2
}
case "$project_resolved" in
  "$workspace_root/SampleHost"/*)
    echo "ERROR: ExistingIPAWorkspace/SampleHost is never a production host" >&2
    exit 2
    ;;
esac

[[ -f "$baseline" ]] || { echo "ERROR: preserved baseline IPA is missing; production is blocked" >&2; exit 3; }
actual_baseline_sha="$(shasum -a 256 "$baseline" | awk '{print $1}')"
[[ "$actual_baseline_sha" == "$BASELINE_IPA_SHA256" ]] || {
  echo "ERROR: preserved baseline IPA checksum changed; production is blocked" >&2
  exit 3
}
[[ -f "$component" ]] || { echo "ERROR: accepted device component is missing: $component" >&2; exit 3; }
actual_component_sha="$(shasum -a 256 "$component" | awk '{print $1}')"
[[ "$actual_component_sha" == "$ACCEPTED_COMPONENT_SHA256" ]] || {
  echo "ERROR: accepted component checksum changed; production is blocked" >&2
  exit 3
}
unzip -tqq "$component"
[[ -f "$package_root/Package.swift" ]] || { echo "ERROR: ExistingIPAOverlay package source is missing" >&2; exit 3; }
[[ -f "$validator" && -f "$configurator" && -f "$host_settings_validator" ]] || {
  echo "ERROR: production validation tooling is incomplete" >&2
  exit 3
}

# The host owner must supply the presentation point; this script never invents it.
grep -Eq '^[[:space:]]*import[[:space:]]+ExistingIPAOverlayUI([[:space:]]|$)' "$integration_source" || {
  echo "ERROR: host presentation source does not import ExistingIPAOverlayUI" >&2
  exit 4
}
grep -Eq 'ExistingIPAOverlayView[[:space:]]*\(' "$integration_source" || {
  echo "ERROR: host presentation source does not construct ExistingIPAOverlayView" >&2
  exit 4
}

# Validate export intent before any project mutation. No signing data is generated.
python3 - "$export_options" "$team" <<'PY'
import plistlib, sys
from pathlib import Path
path, expected_team = Path(sys.argv[1]), sys.argv[2]
try:
    value = plistlib.loads(path.read_bytes())
except Exception as error:
    raise SystemExit(f"ERROR: ExportOptions.plist is invalid: {error}")
if not isinstance(value, dict):
    raise SystemExit("ERROR: ExportOptions.plist root must be a dictionary")
method = value.get("method")
if not isinstance(method, str) or not method.strip():
    raise SystemExit("ERROR: ExportOptions.plist has no explicit export method")
team = value.get("teamID")
if team != expected_team:
    raise SystemExit(f"ERROR: ExportOptions.plist teamID {team!r} does not match authorized team {expected_team!r}")
style = value.get("signingStyle", "automatic")
if style not in {"automatic", "manual"}:
    raise SystemExit("ERROR: ExportOptions.plist signingStyle must be automatic or manual")
if style == "manual" and not value.get("provisioningProfiles"):
    raise SystemExit("ERROR: manual ExportOptions.plist requires provisioningProfiles")
print(f"VALID EXPORT OPTIONS: method={method} signingStyle={style} teamID={team}")
PY

# Confirm the supplied target exists and can receive the product without writing.
python3 "$configurator" --project "$project" --target "$target" --package-path "$package_root"

build_flag=(-project "$container")
[[ "$container" == *.xcworkspace ]] && build_flag=(-workspace "$container")
mkdir -p "$repo_root/.build"
if ! xcodebuild "${build_flag[@]}" \
  -scheme "$scheme" \
  -configuration "$configuration" \
  -destination 'generic/platform=iOS' \
  -showBuildSettings -json > "$settings_path"; then
  echo "ERROR: Xcode could not resolve the supplied production scheme/target/configuration" >&2
  exit 4
fi
python3 "$host_settings_validator" \
  --build-settings "$settings_path" \
  --target "$target" \
  --minimum-ios "$MINIMUM_IOS" \
  --bundle-id "$bundle_id" \
  --team-id "$team"

# Require an existing legitimate signing identity before changing the project.
if ! security find-identity -v -p codesigning | grep -Eq '[1-9][0-9]* valid identities found'; then
  echo "ERROR: signing configuration is absent: no valid Apple code-signing identity is installed" >&2
  exit 5
fi

mkdir -p "$output_dir"
[[ ! -e "$final" && ! -e "$final_hash" && ! -e "$final_report" ]] || {
  echo "ERROR: final output already exists; use an empty output directory to prevent silent replacement: $output_dir" >&2
  exit 5
}

# Read-only baseline verification plus explicit package linkage. No baseline IPA
# or libloader bytes are read as integration inputs or modified by this script.
bash "$workspace_root/Preservation/verify_original.sh"
python3 "$configurator" --project "$project" --target "$target" --package-path "$package_root" --apply

rm -rf "$archive_path" "$export_path"
mkdir -p "$export_path"
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
  archive

apps=("$archive_path"/Products/Applications/*.app)
[[ ${#apps[@]} -eq 1 && -d "${apps[0]}" ]] || {
  echo "ERROR: archive does not contain exactly one production application bundle" >&2
  exit 6
}
archive_app="${apps[0]}"
resource="$archive_app/$RESOURCE_BUNDLE"
for required in \
  "$resource/Info.plist" \
  "$resource/Assets.car" \
  "$resource/en.lproj/Localizable.strings" \
  "$resource/id.lproj/Localizable.strings"; do
  [[ -f "$required" ]] || {
    echo "ERROR: required ExistingIPAOverlay resource is missing from archive: $required" >&2
    exit 6
  }
done
codesign --verify --deep --strict --verbose=2 "$archive_app"

xcodebuild -exportArchive \
  -archivePath "$archive_path" \
  -exportPath "$export_path" \
  -exportOptionsPlist "$export_options"

ipa_count="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | wc -l | tr -d ' ')"
[[ "$ipa_count" == "1" ]] || {
  echo "ERROR: export did not produce exactly one IPA (found $ipa_count)" >&2
  exit 7
}
exported_ipa="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | sort | head -n 1)"
exported_sha="$(shasum -a 256 "$exported_ipa" | awk '{print $1}')"
[[ "$exported_sha" != "$BASELINE_IPA_SHA256" ]] || {
  echo "ERROR: exported IPA is byte-identical to Artifact A; refusing a no-op production claim" >&2
  exit 7
}

# Validate the export in staging. Only a validated real export is atomically
# installed at output/final.ipa, so failures cannot leave a reported final IPA.
python3 "$validator" "$exported_ipa" \
  --require-signature \
  --require-provisioning \
  --require-arm64 \
  --require-component ExistingIPAOverlayUI \
  --require-resource-bundle "$RESOURCE_BUNDLE" \
  --require-bundle-resource Assets.car \
  --require-bundle-resource en.lproj/Localizable.strings \
  --require-bundle-resource id.lproj/Localizable.strings \
  --minimum-ios "$MINIMUM_IOS" \
  --baseline-ipa "$baseline" \
  --report-json "$validation_report" \
  --reject-sha256 "$BASELINE_IPA_SHA256" \
  --codesign-verify \
  --bundle-id "$bundle_id"

temporary_final="$output_dir/.final.ipa.tmp"
temporary_hash="$output_dir/.final.sha256.tmp"
temporary_report="$output_dir/.final-validation-report.json.tmp"
trap 'rm -f "$temporary_final" "$temporary_hash" "$temporary_report"' EXIT
cp "$exported_ipa" "$temporary_final"
printf '%s  final.ipa\n' "$exported_sha" > "$temporary_hash"
cp "$validation_report" "$temporary_report"
mv "$temporary_final" "$final"
mv "$temporary_hash" "$final_hash"
mv "$temporary_report" "$final_report"
trap - EXIT

printf 'FINAL IPA PRODUCED AND VALIDATED: %s\n' "$final"
printf 'VALIDATION REPORT: %s\n' "$final_report"
cat "$final_hash"
