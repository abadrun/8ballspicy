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
import sys
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


def find_object(text: str, isa: str, comment: str | None = None) -> tuple[int, int, str]:
    pattern = re.compile(r"(?m)^([ \t]*)([A-F0-9]{24}) /\* ([^*]+) \*/ = \{")
    for match in pattern.finditer(text):
        end = object_end(text, match.end() - 1)
        body = text[match.start():end]
        if f"isa = {isa};" not in body:
            continue
        if comment is not None and match.group(3).strip() != comment:
            continue
        return match.start(), end, body
    target = f" named {comment!r}" if comment else ""
    raise ConfigurationError(f"could not find {isa}{target}")


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
    insert_at = body.rfind("};")
    if insert_at < 0:
        raise ConfigurationError(f"could not add {key} to project.pbxproj object")
    addition = f"{indent}{key} = (\n{indent}\t{entry}\n{indent});\n"
    return body[:insert_at] + addition + body[insert_at:]


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
    return text[:root] + f"/* Begin {section} section */\n{object_text}\n{end_marker}\n\n" + text[root:]


def quote_openstep(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./$(){}+\-]+", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


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
    if re.search(rf"productName = {re.escape(product_name)};", original):
        _, _, target_body = find_object(original, "PBXNativeTarget", target)
        if "packageProductDependencies" in target_body and product_name in target_body:
            print(f"ALREADY CONFIGURED: {project} target {target} links {product_name}")
            return
        raise ConfigurationError(
            f"{project} already declares {product_name}, but target {target!r} does not link it; resolve this explicitly"
        )

    package_reference_id = unique_pbx_id(original, f"local-package:{package_path.resolve()}")
    dependency_id = unique_pbx_id(original + package_reference_id, f"product:{product_name}:{target}")
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
