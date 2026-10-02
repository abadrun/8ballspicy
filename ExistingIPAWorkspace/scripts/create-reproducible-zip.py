#!/usr/bin/env python3
"""Create a deterministic ZIP and a content manifest from one build directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
EXCLUDED_NAMES = {".DS_Store", "__MACOSX"}


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def entry(name: str, mode: int, directory: bool = False) -> zipfile.ZipInfo:
    if directory and not name.endswith("/"):
        name += "/"
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = ((0o040755 if directory else mode) & 0xFFFF) << 16
    info.flag_bits |= 0x800
    return info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--root-name")
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        raise SystemExit(f"ERROR: input build directory does not exist: {source}")
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        raise SystemExit("ERROR: output ZIP must be outside the input directory")

    root_name = args.root_name or source.name
    if not root_name or "/" in root_name or "\\" in root_name:
        raise SystemExit("ERROR: root name must be one path component")

    paths = sorted(
        (
            path for path in source.rglob("*")
            if not any(part in EXCLUDED_NAMES for part in path.relative_to(source).parts)
        ),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    members = []
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=output.name, suffix=".tmp", dir=output.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr(entry(root_name, 0o755, directory=True), b"")
            for path in paths:
                relative = path.relative_to(source).as_posix()
                archive_name = f"{root_name}/{relative}"
                if path.is_symlink():
                    raise SystemExit(f"ERROR: symbolic link is not permitted in reproducible artifact: {relative}")
                if path.is_dir():
                    archive.writestr(entry(archive_name, 0o755, directory=True), b"")
                    continue
                data = path.read_bytes()
                source_mode = path.stat().st_mode
                mode = 0o755 if source_mode & 0o111 else 0o644
                archive.writestr(entry(archive_name, mode), data)
                members.append(
                    {
                        "path": archive_name,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "sizeBytes": len(data),
                    }
                )
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    archive_hash = sha256(output)
    manifest = {
        "schemaVersion": 1,
        "archive": output.name,
        "sha256": archive_hash,
        "sizeBytes": output.stat().st_size,
        "root": root_name,
        "zipTimestamp": "1980-01-01T00:00:00Z",
        "memberCount": len(members),
        "members": members,
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    output.with_suffix(output.suffix + ".sha256").write_text(f"{archive_hash}  {output.name}\n")
    print(f"archive={output}")
    print(f"sha256={archive_hash}")
    print(f"members={len(members)}")


if __name__ == "__main__":
    main()
