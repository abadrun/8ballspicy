#!/usr/bin/env python3
"""Exhaustive GitHub, Git-history, archive, and macOS/Xcode host discovery.

This script is intentionally read-only except for its JSON report. It never
creates signing material, alters an app binary, or treats the repository sample
host as a production host.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import plistlib
import re
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any

REPO = os.environ.get("GH_REPO", "abadrun/8ballspicy")
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
OUTPUT = Path(os.environ.get("DISCOVERY_REPORT", "analysis/FINAL_EXECUTION_DISCOVERY.json"))

FILE_PATTERNS = [
    "*.xcodeproj",
    "*.xcworkspace",
    "project.pbxproj",
    "Package.swift",
    "Podfile",
    "Cartfile",
    "*.xcconfig",
    "*.entitlements",
    "*.mobileprovision",
    "*.xcarchive",
    "*.ipa",
    "*.dSYM",
    "ExportOptions.plist",
    "Info.plist",
]
SEARCH_STRINGS = [
    "PBXProject",
    "PBXNativeTarget",
    "XCBuildConfiguration",
    "PRODUCT_BUNDLE_IDENTIFIER",
    "CODE_SIGN",
    "DEVELOPMENT_TEAM",
    "PROVISIONING_PROFILE",
    "archive",
    "xcodebuild",
]
ARCHIVE_SUFFIXES = (".zip", ".ipa", ".tar", ".tgz", ".tar.gz", ".xcarchive.zip")
SIGNING_SUFFIXES = (".mobileprovision", ".p12", ".cer")
TEXT_LIMIT = 8 * 1024 * 1024


def run(command: list[str], *, check: bool = True, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{stderr}")
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8", errors="replace")


def command_record(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return {
        "command": command,
        "exitCode": result.returncode,
        "output": result.stdout.decode("utf-8", errors="replace").strip(),
    }


def gh_json(endpoint: str) -> Any:
    return json.loads(run(["gh", "api", endpoint]))


def paged(endpoint: str, key: str | None = None) -> list[Any]:
    separator = "&" if "?" in endpoint else "?"
    values: list[Any] = []
    page = 1
    while True:
        response = gh_json(f"{endpoint}{separator}per_page=100&page={page}")
        batch = response.get(key, []) if key else response
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected paginated response for {endpoint}")
        values.extend(batch)
        if len(batch) < 100:
            return values
        page += 1


def git_lines(*args: str) -> list[str]:
    return str(run(["git", *args])).splitlines()


def matched_file_patterns(name: str) -> list[str]:
    normalized = name.replace("\\", "/")
    lower = normalized.lower()
    base = lower.rsplit("/", 1)[-1]
    matches: list[str] = []
    if ".xcodeproj/" in lower or lower.endswith(".xcodeproj"):
        matches.append("*.xcodeproj")
    if ".xcworkspace/" in lower or lower.endswith(".xcworkspace"):
        matches.append("*.xcworkspace")
    if base == "project.pbxproj":
        matches.append("project.pbxproj")
    if base == "package.swift":
        matches.append("Package.swift")
    if base == "podfile":
        matches.append("Podfile")
    if base == "cartfile":
        matches.append("Cartfile")
    if lower.endswith(".xcconfig"):
        matches.append("*.xcconfig")
    if lower.endswith(".entitlements"):
        matches.append("*.entitlements")
    if lower.endswith(".mobileprovision"):
        matches.append("*.mobileprovision")
    if ".xcarchive/" in lower or lower.endswith(".xcarchive"):
        matches.append("*.xcarchive")
    if lower.endswith(".ipa"):
        matches.append("*.ipa")
    if ".dsym/" in lower or lower.endswith(".dsym"):
        matches.append("*.dSYM")
    if base == "exportoptions.plist":
        matches.append("ExportOptions.plist")
    if base == "info.plist":
        matches.append("Info.plist")
    return sorted(set(matches))


def is_production_container(name: str) -> bool:
    lower = name.lower().replace("\\", "/")
    is_container = (
        lower.endswith(".xcodeproj/project.pbxproj")
        or lower.endswith(".xcworkspace/contents.xcworkspacedata")
        or lower.endswith(".xcodeproj")
        or lower.endswith(".xcworkspace")
    )
    return is_container and "samplehost" not in lower and "sample-host" not in lower


def is_signing_input(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(SIGNING_SUFFIXES) or lower.endswith("exportoptions.plist")


def archive_kind(data: bytes) -> str | None:
    stream = io.BytesIO(data)
    if zipfile.is_zipfile(stream):
        return "zip"
    stream.seek(0)
    try:
        with tarfile.open(fileobj=stream, mode="r:*"):
            return "tar"
    except tarfile.TarError:
        return None


def scan_archive_bytes(
    data: bytes,
    label: str,
    aggregate: dict[str, Any],
    *,
    depth: int = 0,
) -> None:
    if depth > 6:
        aggregate["failures"].append({"container": label, "error": "nested archive depth exceeded"})
        return
    kind = archive_kind(data)
    if kind is None:
        aggregate["failures"].append({"container": label, "error": "not a readable ZIP/TAR archive"})
        return
    aggregate["archiveCount"] += 1
    try:
        if kind == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                bad = archive.testzip()
                if bad:
                    raise RuntimeError(f"ZIP CRC failure at {bad}")
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    name = f"{label}!/{info.filename}"
                    aggregate["memberCount"] += 1
                    patterns = matched_file_patterns(info.filename)
                    if patterns:
                        aggregate["patternMatchCount"] += 1
                        if len(aggregate["patternMatches"]) < 2000:
                            aggregate["patternMatches"].append(
                                {"path": name, "patterns": patterns}
                            )
                    if is_production_container(info.filename):
                        aggregate["productionContainers"].append(name)
                    if is_signing_input(info.filename):
                        aggregate["signingInputs"].append(name)
                    lower = info.filename.lower()
                    if lower.endswith(ARCHIVE_SUFFIXES):
                        scan_archive_bytes(archive.read(info), name, aggregate, depth=depth + 1)
        else:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                for info in archive.getmembers():
                    if not info.isfile():
                        continue
                    name = f"{label}!/{info.name}"
                    aggregate["memberCount"] += 1
                    patterns = matched_file_patterns(info.name)
                    if patterns:
                        aggregate["patternMatchCount"] += 1
                        if len(aggregate["patternMatches"]) < 2000:
                            aggregate["patternMatches"].append(
                                {"path": name, "patterns": patterns}
                            )
                    if is_production_container(info.name):
                        aggregate["productionContainers"].append(name)
                    if is_signing_input(info.name):
                        aggregate["signingInputs"].append(name)
                    lower = info.name.lower()
                    if lower.endswith(ARCHIVE_SUFFIXES):
                        extracted = archive.extractfile(info)
                        if extracted is not None:
                            scan_archive_bytes(extracted.read(), name, aggregate, depth=depth + 1)
    except (OSError, RuntimeError, tarfile.TarError, zipfile.BadZipFile) as error:
        aggregate["failures"].append({"container": label, "error": str(error)})


def new_archive_aggregate() -> dict[str, Any]:
    return {
        "archiveCount": 0,
        "memberCount": 0,
        "patternMatchCount": 0,
        "patternMatches": [],
        "productionContainers": [],
        "signingInputs": [],
        "failures": [],
    }


def find_mac_candidates(roots: list[Path]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    inspected: list[str] = []
    errors: list[dict[str, str]] = []
    skip_names = {".git", "node_modules", ".cache", "Caches"}
    for root in roots:
        expanded = root.expanduser()
        inspected.append(str(expanded))
        if not expanded.exists():
            continue
        try:
            for current, directories, files in os.walk(expanded, followlinks=False):
                directories[:] = [name for name in directories if name not in skip_names]
                current_path = Path(current)
                for directory in directories:
                    candidate = current_path / directory
                    patterns = matched_file_patterns(candidate.name)
                    if patterns:
                        entries.append({"path": str(candidate), "patterns": patterns, "kind": "directory"})
                for filename in files:
                    candidate = current_path / filename
                    patterns = matched_file_patterns(candidate.name)
                    if patterns:
                        entries.append({"path": str(candidate), "patterns": patterns, "kind": "file"})
        except OSError as error:
            errors.append({"root": str(expanded), "error": str(error)})
    unique = {item["path"]: item for item in entries}
    return {"rootsInspected": inspected, "matches": sorted(unique.values(), key=lambda item: item["path"]), "errors": errors}


def main() -> None:
    if str(run(["uname", "-s"])).strip() != "Darwin":
        raise SystemExit("ERROR: final execution discovery must run on macOS")
    if not os.environ.get("GH_TOKEN"):
        raise SystemExit("ERROR: GH_TOKEN is required")

    repo_info = gh_json(f"repos/{REPO}")
    branches = paged(f"repos/{REPO}/branches")
    tags = paged(f"repos/{REPO}/tags")
    pulls = paged(f"repos/{REPO}/pulls?state=all&sort=created&direction=asc")
    workflows = paged(f"repos/{REPO}/actions/workflows", "workflows")
    workflow_runs = paged(f"repos/{REPO}/actions/runs", "workflow_runs")
    artifacts = paged(f"repos/{REPO}/actions/artifacts", "artifacts")
    caches = paged(f"repos/{REPO}/actions/caches", "actions_caches")
    releases = paged(f"repos/{REPO}/releases")

    pull_records = []
    for pull in pulls:
        number = pull["number"]
        files = paged(f"repos/{REPO}/pulls/{number}/files")
        commits = paged(f"repos/{REPO}/pulls/{number}/commits")
        pull_records.append(
            {
                "number": number,
                "state": pull["state"],
                "merged": pull.get("merged_at") is not None,
                "title": pull["title"],
                "headRef": pull["head"]["ref"],
                "headSHA": pull["head"]["sha"],
                "baseRef": pull["base"]["ref"],
                "mergeCommitSHA": pull.get("merge_commit_sha"),
                "files": sorted(item["filename"] for item in files),
                "commitSHAs": [item["sha"] for item in commits],
            }
        )

    release_records = []
    release_asset_scan = new_archive_aggregate()
    release_asset_download_failures = []
    with tempfile.TemporaryDirectory(prefix="final-release-assets-") as temporary:
        release_root = Path(temporary)
        for release in releases:
            assets = []
            for asset in release.get("assets", []):
                record = {
                    "id": asset["id"],
                    "name": asset["name"],
                    "size": asset["size"],
                    "url": asset["url"],
                }
                assets.append(record)
                target = release_root / str(asset["id"])
                result = subprocess.run(
                    [
                        "gh", "api", "-H", "Accept: application/octet-stream",
                        f"repos/{REPO}/releases/assets/{asset['id']}",
                    ],
                    stdout=target.open("wb"), stderr=subprocess.PIPE, check=False,
                )
                if result.returncode:
                    release_asset_download_failures.append({
                        "id": asset["id"],
                        "name": asset["name"],
                        "error": result.stderr.decode("utf-8", errors="replace"),
                    })
                elif asset["name"].lower().endswith(ARCHIVE_SUFFIXES):
                    scan_archive_bytes(
                        target.read_bytes(),
                        f"release-asset:{asset['id']}:{asset['name']}",
                        release_asset_scan,
                    )
            release_records.append(
                {
                    "id": release["id"],
                    "tagName": release["tag_name"],
                    "draft": release["draft"],
                    "prerelease": release["prerelease"],
                    "assets": assets,
                }
            )

    object_rows = git_lines("rev-list", "--objects", "--all")
    commit_shas = git_lines("rev-list", "--all")
    ref_records = [
        {"ref": line.split("\t", 1)[0], "sha": line.split("\t", 1)[1]}
        for line in git_lines("for-each-ref", "--format=%(refname)%09%(objectname)", "refs/heads", "refs/remotes", "refs/tags")
    ]
    historical_pattern_paths = []
    historical_string_matches = []
    historical_archives: dict[str, tuple[str, str]] = {}
    seen_blob_strings: set[str] = set()
    for row in object_rows:
        object_id, separator, path = row.partition(" ")
        if not separator:
            continue
        patterns = matched_file_patterns(path)
        if patterns:
            historical_pattern_paths.append({"path": path, "object": object_id, "patterns": patterns})
        if path.lower().endswith(ARCHIVE_SUFFIXES):
            historical_archives.setdefault(object_id, (object_id, path))
        if object_id in seen_blob_strings:
            continue
        seen_blob_strings.add(object_id)
        try:
            size = int(str(run(["git", "cat-file", "-s", object_id])).strip())
        except (RuntimeError, ValueError):
            continue
        if size > TEXT_LIMIT:
            continue
        data = run(["git", "cat-file", "blob", object_id], binary=True)
        if b"\x00" in data[:8192]:
            continue
        text = data.decode("utf-8", errors="ignore")
        matched = [needle for needle in SEARCH_STRINGS if needle.lower() in text.lower()]
        if matched:
            historical_string_matches.append(
                {"path": path, "object": object_id, "strings": matched}
            )

    git_archive_scan = new_archive_aggregate()
    for object_id, path in historical_archives.values():
        data = run(["git", "cat-file", "blob", object_id], binary=True)
        scan_archive_bytes(data, f"git:{object_id}:{path}", git_archive_scan)

    artifact_scan = new_archive_aggregate()
    artifact_download_failures = []
    artifact_records = []
    with tempfile.TemporaryDirectory(prefix="final-actions-artifacts-") as temporary:
        temporary_root = Path(temporary)
        for artifact in artifacts:
            record = {
                "id": artifact["id"],
                "name": artifact["name"],
                "sizeBytes": artifact["size_in_bytes"],
                "expired": artifact["expired"],
                "workflowRunId": artifact.get("workflow_run", {}).get("id"),
                "digest": artifact.get("digest"),
            }
            artifact_records.append(record)
            target = temporary_root / f"{artifact['id']}.zip"
            result = subprocess.run(
                ["gh", "api", f"repos/{REPO}/actions/artifacts/{artifact['id']}/zip"],
                stdout=target.open("wb"),
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode:
                artifact_download_failures.append(
                    {
                        "id": artifact["id"],
                        "name": artifact["name"],
                        "error": result.stderr.decode("utf-8", errors="replace"),
                    }
                )
                continue
            scan_archive_bytes(target.read_bytes(), f"artifact:{artifact['id']}:{artifact['name']}", artifact_scan)

    run_log_failures = []
    run_log_matches = []
    current_run_id = int(os.environ.get("GITHUB_RUN_ID", "0"))
    run_log_exclusions = []
    with tempfile.TemporaryDirectory(prefix="final-actions-logs-") as temporary:
        temporary_root = Path(temporary)
        for workflow_run in workflow_runs:
            run_id = workflow_run["id"]
            if run_id == current_run_id:
                run_log_exclusions.append({
                    "runId": run_id,
                    "reason": "CURRENT_IN_PROGRESS_RUN_LOG_IS_NOT_YET_DOWNLOADABLE",
                })
                continue
            target = temporary_root / f"{run_id}.zip"
            result = subprocess.run(
                ["gh", "api", f"repos/{REPO}/actions/runs/{run_id}/logs"],
                stdout=target.open("wb"),
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode:
                run_log_failures.append(
                    {"runId": run_id, "error": result.stderr.decode("utf-8", errors="replace")}
                )
                continue
            try:
                with zipfile.ZipFile(target) as archive:
                    bad = archive.testzip()
                    if bad:
                        raise RuntimeError(f"log ZIP CRC failure at {bad}")
                    for info in archive.infolist():
                        if info.is_dir() or info.file_size > 64 * 1024 * 1024:
                            continue
                        text = archive.read(info).decode("utf-8", errors="ignore")
                        strings = [needle for needle in SEARCH_STRINGS if needle.lower() in text.lower()]
                        file_tokens = [pattern for pattern in FILE_PATTERNS if pattern.lower().replace("*", "") in text.lower()]
                        if strings or file_tokens:
                            run_log_matches.append(
                                {
                                    "runId": run_id,
                                    "member": info.filename,
                                    "strings": strings,
                                    "filePatternTokens": file_tokens,
                                }
                            )
            except (OSError, RuntimeError, zipfile.BadZipFile) as error:
                run_log_failures.append({"runId": run_id, "error": str(error)})

    home = Path.home()
    runner_temp = Path(os.environ.get("RUNNER_TEMP", "/tmp"))
    mac_roots = [
        WORKSPACE,
        runner_temp,
        home / "Library/Developer/Xcode/Archives",
        home / "Library/Developer/Xcode/DerivedData",
        home / "Library/MobileDevice/Provisioning Profiles",
        Path("/Library/MobileDevice/Provisioning Profiles"),
        Path("/Volumes"),
    ]
    mac_files = find_mac_candidates(mac_roots)
    mac_production_containers = [
        item["path"]
        for item in mac_files["matches"]
        if is_production_container(item["path"])
        and str(WORKSPACE / "ExistingIPAWorkspace/SampleHost") not in item["path"]
    ]
    mac_signing_files = [item["path"] for item in mac_files["matches"] if is_signing_input(item["path"])]

    xcode = {
        "version": command_record(["xcodebuild", "-version"]),
        "sdks": command_record(["xcodebuild", "-showsdks"]),
        "selectedDeveloperDirectory": command_record(["xcode-select", "-p"]),
        "iphoneOSSDKVersion": command_record(["xcrun", "--sdk", "iphoneos", "--show-sdk-version"]),
        "iphoneOSSDKPath": command_record(["xcrun", "--sdk", "iphoneos", "--show-sdk-path"]),
    }
    signing = {
        "defaultKeychain": command_record(["security", "default-keychain", "-d", "user"]),
        "userKeychains": command_record(["security", "list-keychains", "-d", "user"]),
        "codeSigningIdentities": command_record(["security", "find-identity", "-v", "-p", "codesigning"]),
        "provisioningProfilePaths": sorted(mac_signing_files),
    }
    valid_identity_match = re.search(
        r"(\d+) valid identities found", signing["codeSigningIdentities"]["output"], re.IGNORECASE
    )
    valid_identity_count = int(valid_identity_match.group(1)) if valid_identity_match else 0

    current_workspace_archives = new_archive_aggregate()
    for path in WORKSPACE.rglob("*"):
        if not path.is_file() or ".git" in path.parts or not path.name.lower().endswith(ARCHIVE_SUFFIXES):
            continue
        scan_archive_bytes(path.read_bytes(), f"workspace:{path.relative_to(WORKSPACE)}", current_workspace_archives)

    production_candidates = sorted(set(
        [item["path"] for item in historical_pattern_paths if is_production_container(item["path"])]
        + git_archive_scan["productionContainers"]
        + artifact_scan["productionContainers"]
        + current_workspace_archives["productionContainers"]
        + mac_production_containers
    ))
    production_candidates = [
        item for item in production_candidates
        if "samplehost" not in item.lower() and "sample-host" not in item.lower()
    ]
    signing_candidates = sorted(set(
        git_archive_scan["signingInputs"]
        + artifact_scan["signingInputs"]
        + current_workspace_archives["signingInputs"]
        + mac_signing_files
    ))

    fsck = command_record(["git", "fsck", "--full", "--no-reflogs", "--unreachable"])
    workflow_records = [
        {"id": item["id"], "name": item["name"], "path": item["path"], "state": item["state"]}
        for item in workflows
    ]
    workflow_run_records = [
        {
            "id": item["id"],
            "name": item["name"],
            "event": item["event"],
            "status": item["status"],
            "conclusion": item["conclusion"],
            "headBranch": item["head_branch"],
            "headSHA": item["head_sha"],
            "createdAt": item["created_at"],
        }
        for item in workflow_runs
    ]

    report = {
        "schemaVersion": 1,
        "state": "COMPONENT_READY_FOR_PRODUCTION",
        "result": "HOST_FOUND" if production_candidates else "HOST_NOT_FOUND",
        "repository": {
            "nameWithOwner": repo_info["full_name"],
            "defaultBranch": repo_info["default_branch"],
            "headCommit": str(run(["git", "rev-parse", "HEAD"])).strip(),
            "branches": [{"name": item["name"], "sha": item["commit"]["sha"]} for item in branches],
            "tags": [{"name": item["name"], "sha": item["commit"]["sha"]} for item in tags],
            "refs": ref_records,
            "commitCount": len(commit_shas),
            "commits": commit_shas,
            "reachableObjectPathCount": len(object_rows),
            "fsck": fsck,
            "hiddenTopLevelPaths": sorted(
                path.name for path in WORKSPACE.iterdir() if path.name.startswith(".")
            ),
        },
        "pullRequests": pull_records,
        "githubActions": {
            "workflows": workflow_records,
            "runs": workflow_run_records,
            "runLogDownloadFailures": run_log_failures,
            "runLogExclusions": run_log_exclusions,
            "runLogMatchCount": len(run_log_matches),
            "runLogMatches": run_log_matches,
            "artifacts": artifact_records,
            "artifactDownloadFailures": artifact_download_failures,
            "artifactArchiveScan": artifact_scan,
            "caches": [
                {"id": item["id"], "key": item["key"], "ref": item["ref"], "sizeBytes": item["size_in_bytes"]}
                for item in caches
            ],
        },
        "releases": {
            "items": release_records,
            "assetDownloadFailures": release_asset_download_failures,
            "assetArchiveScan": release_asset_scan,
        },
        "historicalSearch": {
            "filePatterns": FILE_PATTERNS,
            "searchStrings": SEARCH_STRINGS,
            "matchingHistoricalPaths": historical_pattern_paths,
            "matchingTextBlobs": historical_string_matches,
            "gitArchiveScan": git_archive_scan,
        },
        "workspaceArchiveScan": current_workspace_archives,
        "macosDiscovery": {
            "xcode": xcode,
            "signing": signing,
            "validCodeSigningIdentityCount": valid_identity_count,
            "filesystem": mac_files,
            "mounts": command_record(["mount"]),
            "sampleProjectInspection": command_record([
                "xcodebuild", "-list", "-json", "-project",
                "ExistingIPAWorkspace/SampleHost/ExistingIPAOverlaySampleHost.xcodeproj",
            ]),
        },
        "classification": {
            "productionHostCandidates": production_candidates,
            "signingInputCandidates": signing_candidates,
            "sampleHost": "ExistingIPAWorkspace/SampleHost/ExistingIPAOverlaySampleHost.xcodeproj",
            "sampleHostStatus": "AUTHORIZED_TEST_ONLY_NOT_PRODUCTION",
            "historicalNoOpIPA": {
                "path": "output/8-ball-pool-modified.ipa",
                "gitBlob": "1b1558ca090e9aa01b7bdb0d0b548c1e13a00534",
                "status": "REJECTED_PAYLOAD_IDENTICAL_TO_BASELINE",
            },
        },
        "verifiedBuildEvidence": {
            "macOSWorkflowRun": 37065736048,
            "macOSWorkflowJob": 111032957210,
            "componentBuild": "PASS",
            "componentSHA256": "3c01a9d55ae91b2e632ea63a6ddabcce74d3bf94562c7fd7134be9db9e0ecd3f",
            "sampleHostBuild": "PASS",
            "sampleHostArchive": "PASS_UNSIGNED_TEST_ONLY",
            "reproducibility": "PASS",
            "validation": "PASS",
            "handoffPath": "output/ExistingIPAOverlay-mac-production-handoff.zip",
            "handoffSHA256": "1bbec431e921ae7c53e489ba7a4fb6cb459936af0d14814e997da4965c516ebc",
        },
        "baseline": {
            "path": "8-ball-pool-i3rby-IPAOMTK.COM.ipa",
            "sha256": "59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8",
            "preservedUnchanged": True,
        },
        "finalIPA": {"status": "NOT_PRODUCED", "path": None, "sha256": None},
        "missingInputs": {
            "productionHost": (
                "OWNER_SUPPLIED_AUTHORIZED_PRODUCTION_XCODE_PROJECT_OR_WORKSPACE + "
                "REAL_APP_TARGET_AND_SHARED_SCHEME + OWNER_APPROVED_SOURCE_LEVEL_PRESENTATION_POINT + "
                "LAWFUL_BASELINE_COEXISTENCE_AUTHORIZATION_AND_DELTA_ALLOWLIST"
            ),
            "signing": (
                "APPLE_TEAM_ID + VALID_APPLE SIGNING CERTIFICATE AND PRIVATE KEY + "
                "VALID PROVISIONING CONFIGURATION + EXPORT_OPTIONS_PLIST"
            ),
        },
    }

    baseline = WORKSPACE / report["baseline"]["path"]
    baseline_hash = hashlib.sha256(baseline.read_bytes()).hexdigest()
    if baseline_hash != report["baseline"]["sha256"]:
        raise SystemExit(f"baseline hash mismatch: {baseline_hash}")
    handoff = WORKSPACE / report["verifiedBuildEvidence"]["handoffPath"]
    handoff_hash = hashlib.sha256(handoff.read_bytes()).hexdigest()
    if handoff_hash != report["verifiedBuildEvidence"]["handoffSHA256"]:
        raise SystemExit(f"handoff hash mismatch: {handoff_hash}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    summary = {
        "defaultBranch": repo_info["default_branch"],
        "branches": len(branches),
        "tags": len(tags),
        "commits": len(commit_shas),
        "pullRequests": len(pulls),
        "workflowRuns": len(workflow_runs),
        "workflowRunLogsDownloaded": len(workflow_runs) - len(run_log_failures) - len(run_log_exclusions),
        "workflowRunLogsExcludedCurrentInProgress": len(run_log_exclusions),
        "artifacts": len(artifacts),
        "artifactsDownloaded": len(artifacts) - len(artifact_download_failures),
        "releases": len(releases),
        "releaseAssets": sum(len(item["assets"]) for item in release_records),
        "productionHostCandidates": len(production_candidates),
        "signingInputCandidates": len(signing_candidates),
        "validCodeSigningIdentities": valid_identity_count,
        "result": report["result"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("::notice title=Final GitHub and Mac discovery::" + " ".join(f"{key}={value}" for key, value in summary.items()))

    failures = []
    if artifact_download_failures:
        failures.append("Actions artifact downloads")
    if artifact_scan["failures"]:
        failures.append("Actions artifact archive scans")
    if run_log_failures:
        failures.append("workflow run log downloads/scans")
    if release_asset_download_failures or release_asset_scan["failures"]:
        failures.append("release asset downloads/scans")
    if git_archive_scan["failures"]:
        failures.append("historical Git archive scans")
    if current_workspace_archives["failures"]:
        failures.append("workspace archive scans")
    if production_candidates:
        failures.append("production host candidate requires immediate owner review")
    if signing_candidates or valid_identity_count:
        failures.append("signing input candidate requires immediate owner review")
    if failures:
        raise SystemExit("incomplete or actionable discovery: " + ", ".join(failures))


if __name__ == "__main__":
    main()
