#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  archive-authorized-host-macos.sh \
    --container /path/to/AuthorizedHost.xcworkspace \
    --scheme AuthorizedHost \
    --team-id APPLE_TEAM_ID \
    --export-options /path/to/ExportOptions.plist \
    [--configuration Release] [--output-dir /path/to/output]

The authorized host project must already link ExistingIPAWorkspace/OverlaySource
as a local Swift package and present ExistingIPAOverlayView from host-owned source.
EOF
  exit 2
}

container=""; scheme=""; team=""; export_options=""; configuration="Release"; output_dir=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --container) container="$2"; shift 2 ;;
    --scheme) scheme="$2"; shift 2 ;;
    --team-id) team="$2"; shift 2 ;;
    --export-options) export_options="$2"; shift 2 ;;
    --configuration) configuration="$2"; shift 2 ;;
    --output-dir) output_dir="$2"; shift 2 ;;
    *) usage ;;
  esac
done
[[ -n "$container" && -n "$scheme" && -n "$team" && -n "$export_options" ]] || usage
[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS is required" >&2; exit 2; }
for tool in xcodebuild codesign security; do command -v "$tool" >/dev/null || { echo "ERROR: missing $tool" >&2; exit 2; }; done
[[ -e "$container" ]] || { echo "ERROR: host container not found: $container" >&2; exit 2; }
[[ -f "$export_options" ]] || { echo "ERROR: export options not found: $export_options" >&2; exit 2; }

repo_root="$(git rev-parse --show-toplevel)"
workspace_root="$repo_root/ExistingIPAWorkspace"
output_dir="${output_dir:-$repo_root/output}"
archive_path="$repo_root/.build/AuthorizedHost.xcarchive"
export_path="$repo_root/.build/AuthorizedHostExport"
validator="$workspace_root/scripts/validate-exported-ipa.py"

bash "$workspace_root/Preservation/verify_original.sh"
rm -rf "$archive_path" "$export_path"
mkdir -p "$output_dir" "$export_path"

flag=-project
[[ "$container" == *.xcworkspace ]] && flag=-workspace

xcodebuild "$flag" "$container" -scheme "$scheme" -resolvePackageDependencies
xcodebuild "$flag" "$container" \
  -scheme "$scheme" \
  -configuration "$configuration" \
  -destination 'generic/platform=iOS' \
  -archivePath "$archive_path" \
  DEVELOPMENT_TEAM="$team" \
  CODE_SIGN_STYLE=Automatic \
  archive

codesign --verify --deep --strict --verbose=2 "$archive_path/Products/Applications/"*.app
xcodebuild -exportArchive \
  -archivePath "$archive_path" \
  -exportPath "$export_path" \
  -exportOptionsPlist "$export_options"

ipa_count="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | wc -l | tr -d ' ')"
[[ "$ipa_count" == "1" ]] || { echo "ERROR: expected exactly one exported IPA, found $ipa_count" >&2; exit 3; }
exported_ipa="$(find "$export_path" -maxdepth 1 -type f -name '*.ipa' -print | head -n 1)"
final="$output_dir/$(basename "$exported_ipa")"
cp -p "$exported_ipa" "$final"
python3 "$validator" "$final" --require-signature
shasum -a 256 "$final" > "$final.sha256"
printf 'DONE: %s\n' "$final"
cat "$final.sha256"
