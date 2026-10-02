#!/usr/bin/env bash
# Backwards-compatible entry point for the authorized-host integration pipeline.
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
exec "$script_dir/integrate-authorized-host-macos.sh" "$@"
