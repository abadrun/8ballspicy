#!/usr/bin/env python3
"""Link the local ExistingIPAOverlay Swift package to an authorized Xcode app target.

This tool only edits the project.pbxproj supplied with --project. It rejects IPA
containers and does not touch the supplied third-party application archive.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path


class ConfigurationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def object_end(text: str, opening_brace: int) -> int:
    """Return the exclusive end of one OpenStep object record."""
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening_brace, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                if index + 1 >= len(text) or text[index + 1] != ";":
                    raise ConfigurationError("malformed project.pbxproj object terminator")
                return index + 2
    raise ConfigurationError("unterminated project.pbxproj object")


OBJECT_PATTERN = re.compile(r"(?m)^([ \t]*)([A-F0-9]{24}) /\* ([^*]+) \*/ = \{")


def iter_objects(text: str):
    for match in OBJECT_PATTERN.finditer(text):
        end = object_end(text, match.end() - 1)
        yield match.group(2), match.group(3).strip(), match.start(), end, text[match.start():end]


def find_object(text: str, isa: str, comment: str | None = None) -> tuple[int, int, str]:
    for _, object_comment, start, end, body in iter_objects(text):
        if f"isa = {isa};" not in body:
            continue
        if comment is not None and object_comment != comment:
            continue
        return start, end, body
    target = f" named {comment!r}" if comment else ""
    raise ConfigurationError(f"could not find {isa}{target}")


def find_object_by_id(text: str, object_id: str, isa: str | None = None) -> tuple[int, int, str]:
    for candidate_id, _, start, end, body in iter_objects(text):
        if candidate_id != object_id:
            continue
        if isa is not None and f"isa = {isa};" not in body:
            raise ConfigurationError(f"object {object_id} is not a {isa}")
        return start, end, body
    raise ConfigurationError(f"could not find project object {object_id}")


def array_object_ids(body: str, key: str) -> list[str]:
    match = re.search(rf"(?ms)^([ \t]*){re.escape(key)} = \(\n(.*?)^\1\);", body)
    if not match:
        return []
    return re.findall(r"\b[A-F0-9]{24}\b", match.group(2))


def target_frameworks_phase(text: str, target_body: str) -> tuple[str, int, int, str]:
    for phase_id in array_object_ids(target_body, "buildPhases"):
        try:
            start, end, body = find_object_by_id(text, phase_id)
        except ConfigurationError:
            continue
        if "isa = PBXFrameworksBuildPhase;" in body:
            return phase_id, start, end, body
    raise ConfigurationError("target has no PBXFrameworksBuildPhase; cannot link the package product")


def project_indentation(body: str) -> str:
    match = re.search(r"(?m)^([ \t]+)isa =", body)
    if not match:
        raise ConfigurationError("could not determine project.pbxproj indentation")
    return match.group(1)


def add_array_entry(body: str, key: str, entry: str) -> str:
    """Idempotently add an object reference to an OpenStep array property."""
    if entry.split()[0] in body:
        return body
    indent = project_indentation(body)
    array = re.compile(rf"(?ms)^([ \t]*){re.escape(key)} = \(\n.*?^\1\);\n")
    match = array.search(body)
    if match:
        close_at = match.end() - len(f"{match.group(1)});\n")
        return body[:close_at] + f"{indent}\t{entry}\n" + body[close_at:]
    closing = re.search(r"(?m)^[ \t]*};\s*$", body)
    if not closing:
        raise ConfigurationError(f"could not add {key} to project.pbxproj object")
    addition = f"{indent}{key} = (\n{indent}\t{entry}\n{indent});\n"
    return body[:closing.start()] + addition + body[closing.start():]


def replace_object(text: str, start: int, end: int, replacement: str) -> str:
    return text[:start] + replacement + text[end:]


def unique_pbx_id(text: str, seed: str) -> str:
    occupied = set(re.findall(r"\b[A-F0-9]{24}\b", text))
    counter = 0
    while True:
        candidate = hashlib.sha1(f"{seed}:{counter}".encode()).hexdigest()[:24].upper()
        if candidate not in occupied:
            return candidate
        counter += 1


def add_section_object(text: str, section: str, object_text: str) -> str:
    end_marker = f"/* End {section} section */"
    if end_marker in text:
        return text.replace(end_marker, object_text + "\n" + end_marker, 1)
    root = text.find("\trootObject =")
    if root < 0:
        raise ConfigurationError("could not locate rootObject in project.pbxproj")
    objects_end = text.rfind("\n\t};", 0, root)
    if objects_end < 0:
        raise ConfigurationError("could not locate the end of the project objects dictionary")
    section_text = f"\n/* Begin {section} section */\n{object_text}\n{end_marker}\n"
    return text[:objects_end] + section_text + text[objects_end:]


def quote_openstep(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./$(){}+\-]+", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def target_product_dependency(text: str, target_body: str, product_name: str) -> str | None:
    for dependency_id in array_object_ids(target_body, "packageProductDependencies"):
        try:
            _, _, body = find_object_by_id(text, dependency_id, "XCSwiftPackageProductDependency")
        except ConfigurationError:
            continue
        if re.search(rf"(?m)^\s*productName = {re.escape(product_name)};", body):
            return dependency_id
    return None


def product_build_file(text: str, dependency_id: str) -> str | None:
    for object_id, _, _, _, body in iter_objects(text):
        if "isa = PBXBuildFile;" not in body:
            continue
        if re.search(rf"\bproductRef\s*=\s*{dependency_id}\b", body):
            return object_id
    return None


def configure(project: Path, target: str, package_path: Path, apply: bool) -> None:
    if project.suffix != ".xcodeproj":
        raise ConfigurationError("--project must name an authorized .xcodeproj directory")
    pbxproj = project / "project.pbxproj"
    if not pbxproj.is_file():
        raise ConfigurationError(f"project.pbxproj not found: {pbxproj}")
    package_manifest = package_path / "Package.swift"
    if not package_manifest.is_file():
        raise ConfigurationError(f"local ExistingIPAOverlay package not found: {package_manifest}")

    original = pbxproj.read_text(encoding="utf-8")
    product_name = "ExistingIPAOverlay"
    _, _, original_target_body = find_object(original, "PBXNativeTarget", target)
    _, _, _, original_frameworks_body = target_frameworks_phase(original, original_target_body)
    existing_dependency_id = target_product_dependency(original, original_target_body, product_name)
    if existing_dependency_id:
        existing_build_file_id = product_build_file(original, existing_dependency_id)
        framework_file_ids = array_object_ids(original_frameworks_body, "files")
        if existing_build_file_id and existing_build_file_id in framework_file_ids:
            print(f"ALREADY CONFIGURED: {project} target {target} links {product_name}")
            return
        raise ConfigurationError(
            f"{project} target {target!r} has a partial {product_name} package reference but no complete Frameworks link; resolve this explicitly"
        )
    if re.search(rf"productName = {re.escape(product_name)};", original):
        raise ConfigurationError(
            f"{project} already declares {product_name} for another target; add it to {target!r} explicitly"
        )

    package_reference_id = unique_pbx_id(original, f"local-package:{package_path.resolve()}")
    dependency_id = unique_pbx_id(original + package_reference_id, f"product:{product_name}:{target}")
    build_file_id = unique_pbx_id(
        original + package_reference_id + dependency_id,
        f"build-file:{product_name}:{target}",
    )
    relative_path = os.path.relpath(package_path.resolve(), project.resolve().parent)

    project_start, project_end, project_body = find_object(original, "PBXProject")
    project_body = add_array_entry(
        project_body,
        "packageReferences",
        f"{package_reference_id} /* {product_name} */ ,",
    )
    updated = replace_object(original, project_start, project_end, project_body)

    target_start, target_end, target_body = find_object(updated, "PBXNativeTarget", target)
    target_body = add_array_entry(
        target_body,
        "packageProductDependencies",
        f"{dependency_id} /* {product_name} */ ,",
    )
    updated = replace_object(updated, target_start, target_end, target_body)

    _, frameworks_start, frameworks_end, frameworks_body = target_frameworks_phase(updated, target_body)
    frameworks_body = add_array_entry(
        frameworks_body,
        "files",
        f"{build_file_id} /* {product_name} in Frameworks */ ,",
    )
    updated = replace_object(updated, frameworks_start, frameworks_end, frameworks_body)

    package_object = (
        f"\t\t{package_reference_id} /* {product_name} */ = {{\n"
        "\t\t\tisa = XCLocalSwiftPackageReference;\n"
        f"\t\t\trelativePath = {quote_openstep(relative_path)};\n"
        "\t\t};"
    )
    dependency_object = (
        f"\t\t{dependency_id} /* {product_name} */ = {{\n"
        "\t\t\tisa = XCSwiftPackageProductDependency;\n"
        f"\t\t\tpackage = {package_reference_id} /* {product_name} */;\n"
        f"\t\t\tproductName = {product_name};\n"
        "\t\t};"
    )
    build_file_object = (
        f"\t\t{build_file_id} /* {product_name} in Frameworks */ = {{\n"
        "\t\t\tisa = PBXBuildFile;\n"
        f"\t\t\tproductRef = {dependency_id} /* {product_name} */;\n"
        "\t\t};"
    )
    updated = add_section_object(updated, "PBXBuildFile", build_file_object)
    updated = add_section_object(updated, "XCLocalSwiftPackageReference", package_object)
    updated = add_section_object(updated, "XCSwiftPackageProductDependency", dependency_object)

    if not apply:
        print(f"DRY RUN: would link {product_name} into {project} target {target}")
        return
    temporary = pbxproj.with_suffix(".pbxproj.existingipaoverlay.tmp")
    temporary.write_text(updated, encoding="utf-8")
    os.replace(temporary, pbxproj)
    print(f"CONFIGURED: linked {product_name} into {project} target {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--package-path", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="write the authorized host project; without this flag only validate")
    args = parser.parse_args()
    try:
        configure(args.project.resolve(), args.target, args.package_path.resolve(), args.apply)
    except ConfigurationError as error:
        fail(str(error))


if __name__ == "__main__":
    main()
