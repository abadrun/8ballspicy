#!/usr/bin/env bash
# Build deterministic unsigned component archives for Simulator and iPhoneOS.
set -euo pipefail

workspace_root="$(cd "$(dirname "$0")/.." && pwd)"
repo_root="$(cd "$workspace_root/.." && pwd)"
package="$workspace_root/OverlaySource"
derived_root="${DERIVED_DATA_PATH:-$repo_root/.build/ExistingIPAOverlayDerivedData}"
artifact_dir="${ARTIFACT_DIR:-$repo_root/output/components}"
packer="$workspace_root/scripts/create-reproducible-zip.py"

[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS is required" >&2; exit 2; }
for tool in xcodebuild swift python3 file; do
  command -v "$tool" >/dev/null || { echo "ERROR: missing $tool" >&2; exit 2; }
done
[[ -f "$packer" ]] || { echo "ERROR: reproducible ZIP packer is missing" >&2; exit 2; }

mkdir -p "$artifact_dir"
rm -rf "$derived_root"

printf '\n== Toolchain ==\n'
xcodebuild -version
swift --version

if [[ "${SKIP_TESTS:-0}" != "1" ]]; then
  printf '\n== Package tests ==\n'
  swift test --package-path "$package" --parallel
fi

common_settings=(
  CODE_SIGNING_ALLOWED=NO
  CODE_SIGNING_REQUIRED=NO
  COMPILER_INDEX_STORE_ENABLE=NO
  DEBUG_INFORMATION_FORMAT=dwarf
  SWIFT_SERIALIZE_DEBUGGING_OPTIONS=NO
)

build_component() {
  local label="$1" sdk="$2" destination="$3" arch="$4" product_dir="$5" artifact_name="$6"
  local derived="$derived_root/$label"
  printf '\n== %s build (%s) ==\n' "$label" "$arch"
  (
    cd "$package"
    xcodebuild \
      -scheme ExistingIPAOverlay \
      -configuration Debug \
      -destination "$destination" \
      -sdk "$sdk" \
      -derivedDataPath "$derived" \
      ARCHS="$arch" \
      ONLY_ACTIVE_ARCH=YES \
      "${common_settings[@]}" \
      clean build
  )

  local products="$derived/Build/Products/$product_dir"
  [[ -d "$products" ]] || { echo "ERROR: expected products missing: $products" >&2; exit 3; }
  (
    cd "$products"
    find . -type f -print0 | xargs -0 file
  ) > "$artifact_dir/$artifact_name.file-list.txt"
  python3 "$packer" "$products" "$artifact_dir/$artifact_name" --root-name "$product_dir"
}

sim_arch="$(uname -m)"
case "$sim_arch" in
  arm64|x86_64) ;;
  *) echo "ERROR: unsupported macOS runner architecture: $sim_arch" >&2; exit 4 ;;
esac

build_component \
  simulator \
  iphonesimulator \
  'generic/platform=iOS Simulator' \
  "$sim_arch" \
  Debug-iphonesimulator \
  ExistingIPAOverlay-ios-simulator-reproducible.zip

build_component \
  device \
  iphoneos \
  'generic/platform=iOS' \
  arm64 \
  Debug-iphoneos \
  ExistingIPAOverlay-ios-device-reproducible.zip

python3 "$workspace_root/scripts/validate-simulator-component.py" \
  "$artifact_dir/ExistingIPAOverlay-ios-simulator-reproducible.zip"
python3 "$workspace_root/scripts/validate-device-component.py" \
  "$artifact_dir/ExistingIPAOverlay-ios-device-reproducible.zip"

printf '\nDONE: reproducible component archives\n'
cat "$artifact_dir"/*.zip.sha256
