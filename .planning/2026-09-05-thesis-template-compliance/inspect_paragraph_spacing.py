#!/usr/bin/env python3
"""Audit ordinary Korean QMD paragraphs against rendered PDF baseline origins."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median
import sys
import unicodedata

import pymupdf


@dataclass(frozen=True)
class SourceBlock:
    index: int
    start_line: int
    end_line: int
    kind: str
    text: str


@dataclass(frozen=True)
class PdfRow:
    index: int
    page: int
    baseline_pt: float
    text: str
    key: str


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def hangul_key(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(character for character in normalized if "\uac00" <= character <= "\ud7a3")


def source_key(text: str) -> str:
    text = re.sub(r"\[[^\]\n]*@[^\]\n]*\]", "", text)
    text = re.sub(r"(?<!\\)\$(?!\$).*?(?<!\\)\$", "", text, flags=re.DOTALL)
    labels = {"fig": "그림", "tbl": "표", "eq": "식"}
    text = re.sub(r"@(fig|tbl|eq)-[\w-]+", lambda match: labels[match[1]], text)
    return hangul_key(text)


def parse_qmd(text: str) -> list[SourceBlock]:
    lines = text.splitlines()
    blocks = []
    cursor = 0
    region = "front_matter"
    while cursor < len(lines):
        stripped = lines[cursor].strip()
        if not stripped:
            cursor += 1
            continue
        start = cursor
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        fence = re.match(r"^(`{3,}|~{3,})", stripped)
        if cursor == 0 and stripped == "---":
            cursor += 1
            while cursor < len(lines) and lines[cursor].strip() != "---":
                cursor += 1
            if cursor == len(lines):
                raise ValueError("Unclosed YAML front matter")
            cursor += 1
            kind = "yaml_metadata"
        elif fence:
            marker = fence[1]
            cursor += 1
            while cursor < len(lines) and not re.fullmatch(rf"{re.escape(marker)}\s*", lines[cursor].strip()):
                cursor += 1
            if cursor == len(lines):
                raise ValueError(f"Unclosed code fence at QMD line {start + 1}")
            cursor += 1
            contents = "\n".join(lines[start:cursor])
            kind = "fenced_code"
            if "#set bibliography" in contents:
                kind = "bibliography_setup"
                region = "bibliography"
        elif stripped.startswith("$$"):
            cursor += 1
            while cursor < len(lines) and not lines[cursor].strip().startswith("$$"):
                cursor += 1
            if cursor == len(lines):
                raise ValueError(f"Unclosed display equation at QMD line {start + 1}")
            cursor += 1
            kind = "display_equation"
        elif heading:
            cursor += 1
            kind = "chapter_heading" if len(heading[1]) == 1 else "section_heading"
            if len(heading[1]) == 1:
                title = heading[2]
                if re.match(r"(?:Abstract|초록)\b", title, re.IGNORECASE):
                    region = "abstract"
                    kind = "abstract_heading"
                elif re.search(r"References|Bibliography|참\s*고\s*문\s*헌", title, re.IGNORECASE):
                    region = "bibliography"
                    kind = "bibliography_heading"
                elif re.match(r"(?:[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+|[IVX]+|\d+)\.", title):
                    region = "body"
                else:
                    raise ValueError(f"Unsupported top-level heading at QMD line {start + 1}")
        else:
            cursor += 1
            while cursor < len(lines) and lines[cursor].strip():
                cursor += 1
            if stripped.startswith("!["):
                kind = "figure_and_caption"
            elif stripped.startswith("|"):
                kind = "table"
            elif stripped.startswith(": "):
                kind = "table_caption"
            elif re.match(r"Keywords?\s*:", stripped, re.IGNORECASE):
                kind = "keywords"
            elif stripped.startswith(("<", ">", ":::", "- ", "* ", "\\", "{{<")):
                raise ValueError(f"Unsupported block at QMD line {start + 1}")
            else:
                kind = "paragraph" if region == "body" else region
        blocks.append(SourceBlock(len(blocks), start + 1, cursor, kind, "\n".join(lines[start:cursor])))
    return blocks


def read_rows(document, font_pt: float, font_prefixes: list[str]):
    rows = []
    skipped = Counter()
    for page_number, page in enumerate(document, 1):
        grouped = defaultdict(list)
        for block in page.get_text("rawdict")["blocks"]:
            for line in block.get("lines", []):
                if abs(line["dir"][0] - 1) > 0.001 or abs(line["dir"][1]) > 0.001:
                    skipped["nonhorizontal_lines"] += 1
                    continue
                for span in line["spans"]:
                    if abs(span["size"] - font_pt) > 0.05:
                        skipped["other_size_spans_including_superscripts"] += 1
                        continue
                    if not span["font"].startswith(tuple(font_prefixes)):
                        skipped["other_font_spans_including_math"] += 1
                        continue
                    for character in span["chars"]:
                        horizontal, baseline = character["origin"]
                        grouped[round(baseline, 2)].append((horizontal, baseline, character["c"]))
        for _, glyphs in sorted(grouped.items()):
            glyphs.sort(key=lambda glyph: glyph[0])
            text = "".join(glyph[2] for glyph in glyphs)
            if not text.strip():
                continue
            rows.append(PdfRow(len(rows), page_number, median(glyph[1] for glyph in glyphs), text, hangul_key(text)))
    return rows, dict(skipped)


def location(row: PdfRow) -> dict:
    return {"row": row.index, "page": row.page, "baseline_pt": row.baseline_pt, "text": row.text[:90]}


def gap(before: PdfRow, after: PdfRow, paragraph_ids: list[str], expected: float, tolerance: float) -> dict:
    measured = after.baseline_pt - before.baseline_pt
    return {
        "paragraph_ids": paragraph_ids,
        "page": before.page,
        "before_row": before.index,
        "after_row": after.index,
        "before_baseline_pt": before.baseline_pt,
        "after_baseline_pt": after.baseline_pt,
        "gap_pt": measured,
        "passes": abs(measured - expected) <= tolerance,
    }


def summarize(measurements: list[dict]) -> dict:
    values = [measurement["gap_pt"] for measurement in measurements]
    return {
        "count": len(values),
        "passing_count": sum(measurement["passes"] for measurement in measurements),
        "failing_count": sum(not measurement["passes"] for measurement in measurements),
        "min_pt": min(values) if values else None,
        "max_pt": max(values) if values else None,
        "median_pt": median(values) if values else None,
        "histogram_pt_rounded_3dp": dict(sorted(Counter(f"{value:.3f}" for value in values).items())),
        "measurements": measurements,
    }


def inspect_pdf(pdf_path: Path, blocks: list[SourceBlock], args, expected_hash: str | None) -> dict:
    payload = pdf_path.read_bytes()
    pdf_hash = sha256(payload)
    if expected_hash and pdf_hash != expected_hash:
        raise ValueError(f"PDF hash mismatch: {pdf_path}; expected {expected_hash}, got {pdf_hash}")
    with pymupdf.open(stream=payload, filetype="pdf") as document:
        page_count = len(document)
        rows, skipped_spans = read_rows(document, args.body_font_pt, args.body_font_prefix)
    text = "".join(row.key for row in rows)
    character_rows = [row.index for row in rows for _ in row.key]
    row_offsets = {}
    text_offset = 0
    for row in rows:
        row_offsets[row.index] = (text_offset, text_offset + len(row.key))
        text_offset += len(row.key)
    paragraph_blocks = [block for block in blocks if block.kind == "paragraph"]
    matches = []
    errors = []
    previous_end = -1
    for paragraph_number, block in enumerate(paragraph_blocks, 1):
        paragraph_id = f"P{paragraph_number:03d}"
        key = source_key(block.text)
        offset = text.find(key) if key else -1
        if offset < 0 or text.find(key, offset + 1) >= 0:
            errors.append({"kind": "unmatched_or_ambiguous_paragraph", "paragraph_id": paragraph_id, "qmd_line": block.start_line})
            continue
        first_row = character_rows[offset]
        last_row = character_rows[offset + len(key) - 1]
        if offset != row_offsets[first_row][0] or offset + len(key) != row_offsets[last_row][1]:
            errors.append({"kind": "partial_edge_row", "paragraph_id": paragraph_id, "qmd_line": block.start_line})
        if first_row <= previous_end:
            errors.append({"kind": "overlapping_or_out_of_order_match", "paragraph_id": paragraph_id})
        previous_end = last_row
        matches.append({"id": paragraph_id, "block": block, "first": first_row, "last": last_row, "key_length": len(key)})
    within = []
    boundaries = []
    page_breaks = []
    structural_transitions = []
    paragraphs = []
    covered_rows = set()
    for matched in matches:
        selected_rows = rows[matched["first"]:matched["last"] + 1]
        covered_rows.update(row.index for row in selected_rows)
        block = matched["block"]
        paragraphs.append({
            "id": matched["id"],
            "qmd_lines": [block.start_line, block.end_line],
            "source_hangul_characters": matched["key_length"],
            "first": location(selected_rows[0]),
            "last": location(selected_rows[-1]),
            "baselines": [{"row": row.index, "page": row.page, "baseline_pt": row.baseline_pt} for row in selected_rows],
        })
        for before, after in zip(selected_rows, selected_rows[1:]):
            if before.page != after.page:
                page_breaks.append({"kind": "within_paragraph", "paragraph_ids": [matched["id"]], "before": location(before), "after": location(after)})
            else:
                within.append(gap(before, after, [matched["id"]], args.expected_spacing_pt, args.tolerance_pt))
    for previous, following in zip(matches, matches[1:]):
        paragraph_ids = [previous["id"], following["id"]]
        interposed = blocks[previous["block"].index + 1:following["block"].index]
        if interposed:
            structural_transitions.append({"paragraph_ids": paragraph_ids, "excluded_blocks": [{"kind": block.kind, "qmd_lines": [block.start_line, block.end_line]} for block in interposed]})
            continue
        before, after = rows[previous["last"]], rows[following["first"]]
        if before.page != after.page:
            page_breaks.append({"kind": "between_paragraphs", "paragraph_ids": paragraph_ids, "before": location(before), "after": location(after)})
            continue
        if after.index != before.index + 1:
            errors.append({"kind": "interposed_pdf_rows_at_ordinary_boundary", "paragraph_ids": paragraph_ids})
            continue
        boundaries.append(gap(before, after, paragraph_ids, args.expected_spacing_pt, args.tolerance_pt))
    within_summary = summarize(within)
    boundary_summary = summarize(boundaries)
    if not within or not boundaries:
        errors.append({"kind": "empty_measurement_coverage"})
    if len(matches) != len(paragraph_blocks):
        errors.append({"kind": "incomplete_source_coverage"})
    if sha256(pdf_path.read_bytes()) != pdf_hash:
        errors.append({"kind": "pdf_changed_during_inspection"})
    coverage_passes = not errors
    if within_summary["failing_count"]:
        errors.append({"kind": "within_paragraph_spacing", "count": within_summary["failing_count"]})
    if boundary_summary["failing_count"]:
        errors.append({"kind": "between_paragraph_spacing", "count": boundary_summary["failing_count"]})
    return {
        "status": "PASS" if not errors else "FAIL",
        "pdf_path": str(pdf_path.resolve()),
        "pdf_sha256": pdf_hash,
        "pdf_page_count": page_count,
        "coverage_passes": coverage_passes,
        "source_paragraph_count": len(paragraph_blocks),
        "matched_paragraph_count": len(matches),
        "covered_body_baseline_count": len(covered_rows),
        "covered_pdf_pages": sorted({rows[row_index].page for row_index in covered_rows}),
        "body_baselines_per_page": dict(sorted(Counter(rows[row_index].page for row_index in covered_rows).items())),
        "source_paragraph_transitions": max(0, len(paragraph_blocks) - 1),
        "structural_transition_exclusions": structural_transitions,
        "page_break_exclusions": page_breaks,
        "pdf_span_filter_counts": skipped_spans,
        "within_paragraph": within_summary,
        "between_paragraphs": boundary_summary,
        "paragraphs": paragraphs,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--qmd", type=Path, required=True)
    parser.add_argument("--output", default="-", help="JSON output path, or - for stdout")
    parser.add_argument("--expect-pdf-sha256")
    parser.add_argument("--negative-pdf", type=Path)
    parser.add_argument("--expect-negative-sha256")
    parser.add_argument("--negative-gap-pt", type=float, default=15.75)
    parser.add_argument("--body-font-pt", type=float, default=10.5)
    parser.add_argument("--expected-spacing-pt", type=float)
    parser.add_argument("--tolerance-pt", type=float, default=0.05)
    parser.add_argument("--body-font-prefix", action="append")
    args = parser.parse_args()
    args.body_font_prefix = args.body_font_prefix or ["AppleMyungjo", "TimesNewRoman"]
    if args.expected_spacing_pt is None:
        args.expected_spacing_pt = 2 * args.body_font_pt
    for value in [args.body_font_pt, args.expected_spacing_pt, args.tolerance_pt, args.negative_gap_pt]:
        if not math.isfinite(value) or value <= 0:
            parser.error("Font size, spacing, negative gap and tolerance must be finite positive numbers")
    if args.expect_negative_sha256 and not args.negative_pdf:
        parser.error("--expect-negative-sha256 requires --negative-pdf")
    output_path = Path(args.output).resolve() if args.output != "-" else None
    protected = [args.pdf, args.qmd, Path(__file__)] + ([args.negative_pdf] if args.negative_pdf else [])
    if output_path and output_path in {filename.resolve() for filename in protected}:
        parser.error("Output must not overwrite an input or this checker")
    try:
        source_payload = args.qmd.read_bytes()
        blocks = parse_qmd(source_payload.decode("utf-8"))
        primary = inspect_pdf(args.pdf, blocks, args, args.expect_pdf_sha256)
        report = {
            "schema": "qmd-korean-paragraph-baseline-review/v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checker_sha256": sha256(Path(__file__).read_bytes()),
            "pymupdf_version": pymupdf.VersionBind,
            "qmd_path": str(args.qmd.resolve()),
            "qmd_sha256": sha256(source_payload),
            "expected_spacing_pt": args.expected_spacing_pt,
            "body_font_pt": args.body_font_pt,
            "tolerance_pt": args.tolerance_pt,
            "body_font_prefixes": args.body_font_prefix,
            "method": "Exact unique full Hangul-prose matching from QMD to PDF character rows; NFKC normalization and Korean cross-reference label expansion. Spacing uses unrounded median glyph baseline origins, not bounding-box gaps or a gap-size selection filter.",
            "limitations": [
                "A layout-identity check for Korean prose, not a scientific, English-text, numerical-content or full-format audit.",
                "Blank-separated QMD body paragraphs beneath numbered chapter headings are supported; ambiguous/unmatched paragraphs and unsupported block constructs fail closed.",
                "Title/front matter, abstract, keywords, all headings, tables, figures/captions, display equations, bibliography and fenced source are excluded by QMD structure.",
                "Inline math and superscript glyphs are not baseline anchors; surrounding ordinary prose remains included.",
                "Cross-page distances are never treated as paragraph-spacing measurements.",
                "Font-prefix and 0.05pt font-size filters select prose glyphs; 0.01pt grouping merges equal baselines before retaining their unrounded origins.",
            ],
            "source_block_counts": dict(sorted(Counter(block.kind for block in blocks).items())),
            "source_exclusions": [{"kind": block.kind, "qmd_lines": [block.start_line, block.end_line]} for block in blocks if block.kind != "paragraph"],
            "primary": primary,
        }
        success = primary["status"] == "PASS"
        if args.negative_pdf:
            negative = inspect_pdf(args.negative_pdf, blocks, args, args.expect_negative_sha256)
            negative_measurements = negative["between_paragraphs"]["measurements"]
            detected = (
                negative["pdf_sha256"] != primary["pdf_sha256"]
                and negative["coverage_passes"]
                and negative["status"] == "FAIL"
                and negative["within_paragraph"]["failing_count"] == 0
                and bool(negative_measurements)
                and all(not measurement["passes"] and abs(measurement["gap_pt"] - args.negative_gap_pt) <= args.tolerance_pt for measurement in negative_measurements)
            )
            report["negative_fixture"] = negative
            report["negative_control"] = {"status": "PASS" if detected else "FAIL", "expected_bad_gap_pt": args.negative_gap_pt, "detected_bad_boundary_count": negative["between_paragraphs"]["failing_count"]}
            success = success and detected
        if sha256(args.qmd.read_bytes()) != report["qmd_sha256"]:
            report["source_changed_during_inspection"] = True
            success = False
        report["status"] = "PASS" if success else "FAIL"
        serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if output_path:
            output_path.write_text(serialized, encoding="utf-8")
        else:
            sys.stdout.write(serialized)
        print(f"{report['status']}: PDF {primary['pdf_sha256']}; paragraphs {primary['matched_paragraph_count']}/{primary['source_paragraph_count']}; within {primary['within_paragraph']['passing_count']}/{primary['within_paragraph']['count']}; boundaries {primary['between_paragraphs']['passing_count']}/{primary['between_paragraphs']['count']}", file=sys.stderr)
        return 0 if success else 1
    except (OSError, ValueError, RuntimeError) as error:
        print(f"INPUT_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
