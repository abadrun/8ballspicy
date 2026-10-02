#!/usr/bin/env bash
# Run package tests, iOS lifecycle tests, and clean sample-host integration tests.
set -euo pipefail

workspace_root="$(cd "$(dirname "$0")/.." && pwd)"
repo_root="$(cd "$workspace_root/.." && pwd)"
package="$workspace_root/OverlaySource"
sample_project="$workspace_root/SampleHost/ExistingIPAOverlaySampleHost.xcodeproj"
sample_scheme="ExistingIPAOverlaySampleHost"
derived_root="${DERIVED_DATA_PATH:-$repo_root/.build/ExistingIPAOverlayTests}"
results_dir="${TEST_RESULTS_DIR:-$repo_root/output/test-results}"
current_phase="startup"

report_failure() {
  local status=$? line="${1:-unknown}"
  set +e
  local diagnostic="phase=$current_phase line=$line exit=$status"
  for log in "$results_dir"/*.log; do
    [[ -f "$log" ]] || continue
    diagnostic+=$'\n\n--- '"$(basename "$log")"$' ---\n'"$(tail -n 60 "$log")"
  done
  local escaped
  escaped="$(printf '%s' "$diagnostic" | tail -c 7000 | python3 -c 'import sys; s=sys.stdin.read(); print(s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A"))')"
  echo "::error title=ExistingIPAOverlay test failure::$escaped"
  exit "$status"
}
trap 'report_failure $LINENO' ERR

[[ "$(uname -s)" == "Darwin" ]] || { echo "ERROR: macOS is required" >&2; exit 2; }
for tool in xcodebuild swift xcrun python3; do
  command -v "$tool" >/dev/null || { echo "ERROR: missing $tool" >&2; exit 2; }
done

python3 "$workspace_root/scripts/validate-sample-host-source.py"
python3 "$package/Tests/validate_source.py"
rm -rf "$derived_root" "$results_dir"
mkdir -p "$derived_root" "$results_dir"

current_phase="native Swift package tests"
printf '\n== Native Swift package tests (Core + UI) ==\n'
swift test --package-path "$package" --parallel --enable-code-coverage \
  2>&1 | tee "$results_dir/swift-test.log"

current_phase="iOS Simulator selection and boot"
printf '\n== Select an available iOS Simulator ==\n'
simulator_id="$(xcrun simctl list devices available -j | python3 -c '
import json, sys
data=json.load(sys.stdin).get("devices", {})
candidates=[]
for runtime, devices in data.items():
    if "iOS" not in runtime:
        continue
    for device in devices:
        if device.get("isAvailable") and device.get("name", "").startswith("iPhone"):
            score=("iPhone 16" in device.get("name", ""), runtime, device.get("name", ""))
            candidates.append((score, device["udid"], device["name"], runtime))
if not candidates:
    raise SystemExit("no available iPhone Simulator")
candidates.sort(reverse=True)
print(candidates[0][1])
')"
echo "Simulator UDID: $simulator_id"
xcrun simctl boot "$simulator_id" >/dev/null 2>&1 || true
xcrun simctl bootstatus "$simulator_id" -b

current_phase="Swift package scheme discovery"
printf '\n== Discover Swift package scheme ==\n'
(
  cd "$package"
  xcodebuild -list -json > "$results_dir/package-schemes.json"
)
package_scheme="$(python3 - "$results_dir/package-schemes.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
schemes=[]
for key in ("workspace", "project"):
    schemes.extend(data.get(key, {}).get("schemes", []))
for preferred in ("ExistingIPAOverlay-Package", "ExistingIPAOverlay"):
    if preferred in schemes:
        print(preferred)
        break
else:
    raise SystemExit(f"no package test scheme in {schemes}")
PY
)"
echo "Package scheme: $package_scheme"

current_phase="iOS Simulator package tests and SwiftUI lifecycle"
printf '\n== iOS Simulator package tests (includes SwiftUI hosting lifecycle) ==\n'
(
  cd "$package"
  xcodebuild \
    -quiet \
    -scheme "$package_scheme" \
    -destination "platform=iOS Simulator,id=$simulator_id" \
    -derivedDataPath "$derived_root/PackageSimulatorTests" \
    -resultBundlePath "$results_dir/PackageSimulatorTests.xcresult" \
    -enableCodeCoverage YES \
    CODE_SIGNING_ALLOWED=NO \
    clean test \
    2>&1 | tee "$results_dir/package-simulator-tests.log"
)

current_phase="clean sample host Simulator build"
printf '\n== Clean sample host: Simulator build ==\n'
xcodebuild \
  -quiet \
  -project "$sample_project" \
  -scheme "$sample_scheme" \
  -destination "platform=iOS Simulator,id=$simulator_id" \
  -derivedDataPath "$derived_root/SampleHostSimulator" \
  CODE_SIGNING_ALLOWED=NO \
  clean build \
  2>&1 | tee "$results_dir/sample-host-simulator-build.log"
simulator_app="$derived_root/SampleHostSimulator/Build/Products/Debug-iphonesimulator/ExistingIPAOverlaySampleHost.app"
python3 "$workspace_root/scripts/validate-sample-host-app.py" "$simulator_app" --platform simulator \
  | tee "$results_dir/sample-host-simulator-validation.log"

current_phase="clean sample host Simulator install and launch"
printf '\n== Clean sample host: Simulator install and launch ==\n'
xcrun simctl install "$simulator_id" "$simulator_app"
xcrun simctl launch --terminate-running-process "$simulator_id" com.example.ExistingIPAOverlaySampleHost \
  | tee "$results_dir/sample-host-launch.log"
sleep 2
xcrun simctl terminate "$simulator_id" com.example.ExistingIPAOverlaySampleHost

current_phase="clean sample host generic iPhoneOS arm64 build"
printf '\n== Clean sample host: generic iPhoneOS arm64 build ==\n'
xcodebuild \
  -quiet \
  -project "$sample_project" \
  -scheme "$sample_scheme" \
  -destination 'generic/platform=iOS' \
  -derivedDataPath "$derived_root/SampleHostDevice" \
  ARCHS=arm64 \
  ONLY_ACTIVE_ARCH=YES \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  clean build \
  2>&1 | tee "$results_dir/sample-host-device-build.log"
device_app="$derived_root/SampleHostDevice/Build/Products/Debug-iphoneos/ExistingIPAOverlaySampleHost.app"
python3 "$workspace_root/scripts/validate-sample-host-app.py" "$device_app" --platform device \
  | tee "$results_dir/sample-host-device-validation.log"

current_phase="deployment target build setting verification"
printf '\n== Deployment target contract ==\n'
xcodebuild \
  -project "$sample_project" \
  -scheme "$sample_scheme" \
  -showBuildSettings \
  -destination 'generic/platform=iOS' \
  | tee "$results_dir/sample-host-build-settings.log"
grep -Eq '^[[:space:]]*IPHONEOS_DEPLOYMENT_TARGET = 16\.0$' "$results_dir/sample-host-build-settings.log" || {
  echo "ERROR: clean sample host deployment target is not iOS 16.0" >&2
  exit 5
}

printf '\nPASS: Core, UI, lifecycle, resources, localization, persistence, and sample-host integration\n'
