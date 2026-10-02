#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo_root"
artifact="8-ball-pool-i3rby-IPAOMTK.COM.ipa"
expected="59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8"

working="$(sha256sum "$artifact" | awk '{print $1}')"
[[ "$working" == "$expected" ]] || { echo "working artifact mismatch: $working" >&2; exit 1; }

committed="$(git cat-file blob "HEAD:$artifact" | sha256sum | awk '{print $1}')"
[[ "$committed" == "$expected" ]] || { echo "committed artifact mismatch: $committed" >&2; exit 1; }

blob="$(git rev-parse "HEAD:$artifact")"
printf 'working artifact: OK (%s)\ncommitted Git object: OK (%s)\nGit blob: %s\n' "$working" "$committed" "$blob"
