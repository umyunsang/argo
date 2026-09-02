#!/usr/bin/env python3
"""Apply fail-closed, byte-preserving paragraph patches to an HWPX file."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

HEADER = "Contents/header.xml"
SECTION = "Contents/section0.xml"
MIMETYPE = b"application/hwp+zip"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_archive(infos: list[zipfile.ZipInfo]) -> None:
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        raise ValueError("HWPX contains duplicate member names")
    if not names or names[0] != "mimetype" or infos[0].compress_type != zipfile.ZIP_STORED:
        raise ValueError("HWPX mimetype must be the first uncompressed member")
    for info in infos:
        parts = Path(info.filename).parts
        mode = info.external_attr >> 16
        if info.filename.startswith(("/", "\\")) or ".." in parts or "\\" in info.filename:
            raise ValueError(f"unsafe HWPX member path: {info.filename}")
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlink member is not allowed: {info.filename}")
    for required in ("mimetype", HEADER, SECTION):
        if required not in names:
            raise ValueError(f"missing HWPX member: {required}")


def unique_match(pattern: str, text: str, label: str, flags: int = 0) -> re.Match[str]:
    matches = list(re.finditer(pattern, text, flags))
    if len(matches) != 1:
        raise ValueError(f"expected one {label}, found {len(matches)}")
    return matches[0]


def patch_header(header: str, style: dict[str, object]) -> str:
    base_id = re.escape(str(style["baseId"]))
    new_id = str(style["newId"])
    horizontal = str(style["horizontal"])
    if not new_id.isdecimal() or horizontal not in {"LEFT", "RIGHT", "CENTER", "JUSTIFY"}:
        raise ValueError("invalid paragraph style specification")
    if re.search(rf'<hh:paraPr id="{re.escape(new_id)}"(?=\s|>)', header):
        raise ValueError(f"paragraph style {new_id} already exists")

    collection = unique_match(
        r'<hh:paraProperties\b[^>]*\bitemCnt="(?P<count>\d+)"[^>]*>',
        header,
        "paragraph-style collection",
    )
    base = unique_match(
        rf'<hh:paraPr id="{base_id}"(?=\s|>).*?</hh:paraPr>',
        header,
        f"base paragraph style {style['baseId']}",
        re.DOTALL,
    )
    base_text = base.group(0)
    if base_text.count('horizontal="JUSTIFY"') != 1:
        raise ValueError("base paragraph style has an unexpected alignment")
    clone = base_text.replace(
        f'id="{style["baseId"]}"', f'id="{new_id}"', 1
    ).replace('horizontal="JUSTIFY"', f'horizontal="{horizontal}"', 1)

    opening = collection.group(0)
    count = int(collection.group("count"))
    if header.count("<hh:paraPr ") != count:
        raise ValueError("paragraph-style itemCnt does not match the archive")
    updated_opening = opening.replace(f'itemCnt="{count}"', f'itemCnt="{count + 1}"', 1)
    header = header[: collection.start()] + updated_opening + header[collection.end() :]
    closing = "</hh:paraProperties>"
    if header.count(closing) != 1:
        raise ValueError("unexpected paragraph-style collection closing tag")
    return header.replace(closing, clone + closing, 1)


def patch_section(
    section: str,
    patches: list[dict[str, object]],
    default_style_id: str,
    available_style_ids: set[str],
) -> tuple[str, list[str], int, dict[str, str]]:
    paragraph_ids = [str(patch["paragraphId"]) for patch in patches]
    if not paragraph_ids or len(paragraph_ids) != len(set(paragraph_ids)):
        raise ValueError("patch paragraph IDs must be non-empty and unique")

    removed_line_segments = 0
    applied_styles: dict[str, str] = {}
    for patch in patches:
        paragraph_id = str(patch["paragraphId"])
        target_style_id = str(patch.get("styleId", default_style_id))
        if target_style_id not in available_style_ids:
            raise ValueError(
                f"paragraph {paragraph_id} requests unknown style {target_style_id}"
            )
        match = unique_match(
            rf'<hp:p id="{re.escape(paragraph_id)}"(?=\s|>).*?</hp:p>',
            section,
            f"paragraph {paragraph_id}",
            re.DOTALL,
        )
        paragraph = match.group(0)
        if paragraph.count('paraPrIDRef="0"') != 1:
            raise ValueError(f"paragraph {paragraph_id} has an unexpected paragraph style")

        expected = f"<hp:t>{html.escape(str(patch['expectedText']), quote=False)}</hp:t>"
        replacement = f"<hp:t>{html.escape(str(patch['text']), quote=False)}</hp:t>"
        if paragraph.count(expected) != 1:
            raise ValueError(f"paragraph {paragraph_id} text precondition failed")
        paragraph = paragraph.replace(
            'paraPrIDRef="0"', f'paraPrIDRef="{target_style_id}"', 1
        )
        paragraph = paragraph.replace(expected, replacement, 1)
        paragraph, removed = re.subn(
            r"<hp:linesegarray>.*?</hp:linesegarray>", "", paragraph, count=1, flags=re.DOTALL
        )
        if removed != 1:
            raise ValueError(f"paragraph {paragraph_id} has an unexpected line-segment layout")
        removed_line_segments += removed
        applied_styles[paragraph_id] = target_style_id
        section = section[: match.start()] + paragraph + section[match.end() :]

    return section, paragraph_ids, removed_line_segments, applied_styles


def apply_patch(input_path: Path, output_path: Path, spec_path: Path) -> dict[str, object]:
    input_bytes = input_path.read_bytes()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("schemaVersion") != "argo-hwpx-paragraph-patch/v1":
        raise ValueError("unsupported patch schemaVersion")
    if sha256(input_bytes) != spec["preconditions"]["inputSha256"]:
        raise ValueError("inputSha256 precondition failed")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("input and output paths must differ")

    with zipfile.ZipFile(io.BytesIO(input_bytes), "r") as source:
        infos = source.infolist()
        validate_archive(infos)
        if source.read("mimetype") != MIMETYPE:
            raise ValueError("unexpected HWPX mimetype")
        members = {info.filename: source.read(info.filename) for info in infos}

    header = members[HEADER].decode("utf-8")
    section = members[SECTION].decode("utf-8")
    style = spec["paragraphStyle"]
    header = patch_header(header, style)
    available_style_ids = set(re.findall(r'<hh:paraPr id="(\d+)"(?=\s|>)', header))
    section, patched_ids, removed_line_segments, applied_styles = patch_section(
        section,
        spec["patches"],
        str(style["newId"]),
        available_style_ids,
    )
    members[HEADER] = header.encode("utf-8")
    members[SECTION] = section.encode("utf-8")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as target:
        for info in infos:
            target.writestr(info, members[info.filename])
    output_bytes = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(output_bytes), "r") as check:
        validate_archive(check.infolist())
        ET.fromstring(check.read(HEADER))
        ET.fromstring(check.read(SECTION))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.{os.getpid()}.tmp")
    try:
        temporary_path.write_bytes(output_bytes)
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return {
        "schemaVersion": "argo-hwpx-paragraph-patch-receipt/v1",
        "input": str(input_path),
        "inputSha256": sha256(input_bytes),
        "output": str(output_path),
        "outputSha256": sha256(output_bytes),
        "paragraphStyle": style,
        "patchedParagraphIds": patched_ids,
        "paragraphStyles": applied_styles,
        "removedLineSegmentArrays": removed_line_segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = apply_patch(args.input, args.output, args.spec)
    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        UnicodeError,
        zipfile.BadZipFile,
        ET.ParseError,
    ) as error:
        if args.input.resolve() != args.output.resolve():
            args.output.unlink(missing_ok=True)
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
