#!/usr/bin/env bash
set -euo pipefail

workspace_root="$(cd "$(dirname "$0")/.." && pwd)"
repo_root="$(cd "$workspace_root/.." && pwd)"
package="$workspace_root/OverlaySource"
derived_data="${DERIVED_DATA_PATH:-$repo_root/.build/ExistingIPAOverlayDerivedData}"
artifact_dir="${ARTIFACT_DIR:-$repo_root/output/components}"

[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS is required" >&2; exit 2; }
for tool in xcodebuild swift ditto; do
  command -v "$tool" >/dev/null || { echo "ERROR: missing $tool" >&2; exit 2; }
done

bash "$workspace_root/Preservation/verify_original.sh"
mkdir -p "$derived_data" "$artifact_dir"

printf '\n== Toolchain ==\n'
xcodebuild -version
swift --version

if [[ "${SKIP_TESTS:-0}" != "1" ]]; then
  printf '\n== Package tests ==\n'
  swift test --package-path "$package" --parallel
fi

printf '\n== iOS Simulator build ==\n'
(
  cd "$package"
  xcodebuild \
    -scheme ExistingIPAOverlay \
    -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath "$derived_data" \
    CODE_SIGNING_ALLOWED=NO \
    clean build
)

products="$derived_data/Build/Products/Debug-iphonesimulator"
[[ -d "$products" ]] || { echo "ERROR: expected build products not found at $products" >&2; exit 3; }
artifact="$artifact_dir/ExistingIPAOverlay-ios-simulator-build.zip"
rm -f "$artifact"
ditto -c -k --sequesterRsrc --keepParent "$products" "$artifact"
shasum -a 256 "$artifact" > "$artifact.sha256"

printf '\nDONE: %s\n' "$artifact"
cat "$artifact.sha256"
