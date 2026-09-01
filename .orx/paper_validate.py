#!/usr/bin/env python3
"""Closed-world static and deterministic-build validator for the ARGO thesis."""

import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PROTOCOL_PATH = ROOT / ".orx" / "paper_protocol.json"


def sha256_path(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_space(value):
    return " ".join((value or "").split())


def parse_arxiv_atom(path):
    atom = "{http://www.w3.org/2005/Atom}"
    root = ET.parse(str(path)).getroot()
    records = {}
    for entry in root.findall(atom + "entry"):
        id_url = normalize_space(entry.findtext(atom + "id"))
        match = re.search(r"(\d{4}\.\d{4,5})(v\d+)$", id_url)
        if not match:
            raise ValueError("unrecognized arXiv Atom entry id: " + id_url)
        source_id, version = match.groups()
        if source_id in records:
            raise ValueError("duplicate arXiv Atom entry: " + source_id)
        records[source_id] = {
            "version": version,
            "title": normalize_space(entry.findtext(atom + "title")),
            "authors": [normalize_space(x.findtext(atom + "name")) for x in entry.findall(atom + "author")],
            "published": normalize_space(entry.findtext(atom + "published")),
        }
    return records


def strip_comments(text):
    out = []
    for line in text.splitlines():
        kept = []
        i = 0
        while i < len(line):
            if line[i] == "%":
                backslashes = 0
                j = i - 1
                while j >= 0 and line[j] == "\\":
                    backslashes += 1
                    j -= 1
                if backslashes % 2 == 0:
                    break
            kept.append(line[i])
            i += 1
        out.append("".join(kept))
    return "\n".join(out)


def line_hits(text, pattern):
    rx = re.compile(pattern)
    return [
        {"line": i, "text": line.strip()[:240]}
        for i, line in enumerate(text.splitlines(), 1)
        if rx.search(line)
    ]


def verify_toolchain(cfg):
    tc = cfg["toolchain"]
    manifest_path = Path(tc["manifest_path"])
    binary_path = Path(tc["binary_path"])
    errors = []
    if not manifest_path.is_file():
        return ["toolchain manifest missing: %s" % manifest_path], None
    if sha256_path(manifest_path) != tc["manifest_sha256"]:
        errors.append("toolchain manifest digest mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not binary_path.is_file() or sha256_path(binary_path) != tc["binary_sha256"]:
        errors.append("tectonic binary missing or digest mismatch")
    root = Path(tc["root"])
    bad_files = []
    for item in manifest.get("files", []):
        p = root / item["path"]
        if not p.is_file() or p.stat().st_size != item["bytes"] or sha256_path(p) != item["sha256"]:
            bad_files.append(item["path"])
    if bad_files:
        errors.append("toolchain file mismatch: " + ", ".join(bad_files[:10]))
    return errors, {
        "version": tc["version"],
        "binary_sha256": tc["binary_sha256"],
        "manifest_sha256": tc["manifest_sha256"],
        "verified_file_count": len(manifest.get("files", [])),
        "bundle_cache_key": tc["bundle_cache_key"],
    }


def link_or_copy(src, dst):
    try:
        os.link(str(src), str(dst))
    except OSError:
        shutil.copy2(str(src), str(dst))


def compile_once(cfg, tmp, name):
    tc = cfg["toolchain"]
    outdir = tmp / name
    outdir.mkdir()
    cmd = [
        tc["binary_path"], "-X", "compile",
        "--keep-logs", "--keep-intermediates", "--outdir", str(outdir), "paper.tex",
    ]
    env = {
        "HOME": str(tmp / "home"),
        "XDG_CACHE_HOME": str(tmp / "xdg-cache"),
        "XDG_CONFIG_HOME": str(tmp / "config"),
        "LANG": "C",
        "LC_ALL": "C",
        "TZ": "UTC",
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "SOURCE_DATE_EPOCH": cfg["source_date_epoch"],
    }
    proc = subprocess.run(
        cmd, cwd=str(ROOT), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    texts = [proc.stdout]
    for filename in ("paper.log", "driver.log"):
        p = outdir / filename
        if p.is_file():
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    combined = "\n".join(texts)
    combined_lines = combined.splitlines()
    overfull_details = [
        "\n".join(combined_lines[i:i + 4])[:1000]
        for i, line in enumerate(combined_lines)
        if "Overfull \\hbox" in line
    ]
    pdf = outdir / "paper.pdf"
    return {
        "name": name,
        "exit_code": proc.returncode,
        "command": cmd,
        "pdf_path": pdf,
        "pdf_sha256": sha256_path(pdf) if pdf.is_file() else None,
        "pdf_bytes": pdf.stat().st_size if pdf.is_file() else None,
        "overfull_boxes": len(re.findall(r"Overfull \\hbox", combined)),
        "overfull_details": overfull_details,
        "undefined_citations": len(re.findall(r"Citation .* undefined|undefined citations", combined, re.I)),
        "undefined_references": len(re.findall(r"Reference .* undefined|undefined references", combined, re.I)),
        "log_tail": combined[-4000:],
    }


def main():
    cfg = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    paper = ROOT / cfg["paper_path"]
    errors = []
    if not paper.is_file():
        print(json.dumps({"status": "FAIL", "errors": ["paper missing"]}, indent=2))
        return 1
    raw = paper.read_bytes()
    text = raw.decode("utf-8")
    clean = strip_comments(text)

    receipt_expectations = cfg.get("evidence_receipts")
    evidence_receipts = {}
    if not receipt_expectations:
        errors.append("mandatory evidence receipt set is missing or empty")
    else:
        for relpath, expected_sha in receipt_expectations.items():
            p = ROOT / relpath
            actual_sha = sha256_path(p) if p.is_file() else None
            evidence_receipts[relpath] = {
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "verified": actual_sha == expected_sha,
            }
        if not all(x["verified"] for x in evidence_receipts.values()):
            errors.append("evidence receipt or locator identity mismatch")

    structured_evidence = {}
    expectations = cfg.get("structured_expectations")
    if not expectations:
        errors.append("mandatory structured evidence expectations are missing or empty")
    else:
        locator_obj = json.loads((ROOT / "paper/sources/claim-locators.json").read_text(encoding="utf-8"))
        locators = locator_obj.get("locators", [])
        locator_ids = [x.get("claim_locator_id") for x in locators]
        reviewed_count = sum(x.get("status") == "REVIEWED_SUPPORTS_SCOPED_MANUSCRIPT_CLAIM" for x in locators)
        locator_hash_failures = [
            x.get("claim_locator_id")
            for x in locators
            if hashlib.sha256(x.get("excerpt", "").encode("utf-8")).hexdigest() != x.get("excerpt_sha256")
        ]
        required_locator_ids = set(expectations.get("required_round2_locator_ids", []))
        missing_locator_ids = sorted(required_locator_ids - set(locator_ids))
        duplicate_locator_ids = sorted(k for k, v in collections.Counter(locator_ids).items() if v > 1)
        expected_round2_locator_counts = expectations.get("required_round2_locator_counts", {})
        actual_round2_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round2_locator_counts
        )
        round2_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round2_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round2_locator_counts.items()
            if actual_round2_locator_counts.get(source_id, 0) != expected
        }
        expected_locator_sources = expectations.get("required_round2_locator_sources", {})
        actual_locator_sources = {x.get("claim_locator_id"): x.get("source_id") for x in locators}
        locator_source_failures = {
            locator_id: {"expected": source_id, "actual": actual_locator_sources.get(locator_id)}
            for locator_id, source_id in expected_locator_sources.items()
            if actual_locator_sources.get(locator_id) != source_id
        }
        structured_evidence["locator_count"] = len(locators)
        structured_evidence["reviewed_locator_count"] = reviewed_count
        structured_evidence["locator_excerpt_hash_failures"] = locator_hash_failures
        structured_evidence["missing_required_locator_ids"] = missing_locator_ids
        structured_evidence["duplicate_locator_ids"] = duplicate_locator_ids
        structured_evidence["round2_locator_count_failures"] = round2_locator_count_failures
        structured_evidence["locator_source_failures"] = locator_source_failures
        if (
            len(locators) != expectations["reviewed_locator_count"]
            or reviewed_count != expectations["reviewed_locator_count"]
            or locator_hash_failures
            or missing_locator_ids
            or duplicate_locator_ids
            or round2_locator_count_failures
            or locator_source_failures
        ):
            errors.append("claim-locator identity, embedded excerpt hash, source map, count, or recorded review mismatch")

        metadata_obj = json.loads((ROOT / "paper/sources/arxiv-metadata-receipt.json").read_text(encoding="utf-8"))
        metadata_count = len(metadata_obj.get("records", []))
        structured_evidence["bibliography_metadata_record_count"] = metadata_count
        if metadata_count != expectations["bibliography_metadata_record_count"]:
            errors.append("bibliography metadata record count mismatch")

        round2_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-prior-work-round2-receipt.json").read_text(encoding="utf-8")
        )
        round2_metadata_records = round2_metadata_obj.get("records", [])
        round2_metadata_count = len(round2_metadata_records)
        round2_metadata_source_ids = {x.get("source_id") for x in round2_metadata_records}
        required_source_ids = set(expectations.get("required_round2_source_ids", []))
        structured_evidence["round2_bibliography_metadata_record_count"] = round2_metadata_count
        structured_evidence["round2_metadata_source_ids"] = sorted(round2_metadata_source_ids)
        if (
            round2_metadata_count != expectations["round2_bibliography_metadata_record_count"]
            or round2_metadata_source_ids != required_source_ids
        ):
            errors.append("round-2 bibliography metadata identity mismatch")

        combined_metadata_records = metadata_obj.get("records", []) + round2_metadata_records
        combined_metadata_ids = [x.get("source_id") for x in combined_metadata_records]
        duplicate_metadata_ids = sorted(k for k, v in collections.Counter(combined_metadata_ids).items() if v > 1)
        metadata_versions = {}
        for record in combined_metadata_records:
            version = record.get("version")
            if not version:
                match = re.search(r"(v\d+)$", record.get("id_url", ""))
                version = match.group(1) if match else None
            metadata_versions[record.get("source_id")] = version
        expected_metadata_versions = expectations.get("required_bibliography_metadata_versions", {})
        metadata_version_failures = {
            source_id: {"expected": version, "actual": metadata_versions.get(source_id)}
            for source_id, version in expected_metadata_versions.items()
            if metadata_versions.get(source_id) != version
        }
        unexpected_metadata_ids = sorted(set(metadata_versions) - set(expected_metadata_versions))
        missing_metadata_ids = sorted(set(expected_metadata_versions) - set(metadata_versions))
        structured_evidence["combined_bibliography_metadata_record_count"] = len(combined_metadata_records)
        structured_evidence["duplicate_metadata_ids"] = duplicate_metadata_ids
        structured_evidence["metadata_version_failures"] = metadata_version_failures
        structured_evidence["unexpected_metadata_ids"] = unexpected_metadata_ids
        structured_evidence["missing_metadata_ids"] = missing_metadata_ids
        if (
            len(combined_metadata_records) != len(expected_metadata_versions)
            or duplicate_metadata_ids
            or metadata_version_failures
            or unexpected_metadata_ids
            or missing_metadata_ids
        ):
            errors.append("combined bibliography source or version identity mismatch")

        metadata_receipt_failures = {}
        for receipt_name, receipt_obj in (
            ("original", metadata_obj),
            ("round2", round2_metadata_obj),
        ):
            response_path = ROOT / receipt_obj.get("response_path", "")
            receipt_errors = []
            if not response_path.is_file():
                receipt_errors.append("response missing")
                atom_records = {}
            else:
                if response_path.stat().st_size != receipt_obj.get("response_bytes"):
                    receipt_errors.append("response byte count mismatch")
                if sha256_path(response_path) != receipt_obj.get("response_sha256"):
                    receipt_errors.append("response digest mismatch")
                try:
                    atom_records = parse_arxiv_atom(response_path)
                except (ET.ParseError, ValueError) as exc:
                    receipt_errors.append("Atom parse failure: " + str(exc))
                    atom_records = {}
            expected_atom_records = {}
            for record in receipt_obj.get("records", []):
                version = record.get("version")
                if not version:
                    match = re.search(r"(v\d+)$", record.get("id_url", ""))
                    version = match.group(1) if match else None
                expected_atom_records[record.get("source_id")] = {
                    "version": version,
                    "title": normalize_space(record.get("title")),
                    "authors": [normalize_space(x) for x in record.get("authors", [])],
                    "published": normalize_space(record.get("published")),
                }
            if atom_records != expected_atom_records:
                receipt_errors.append("Atom metadata differs from parsed receipt records")
            if receipt_errors:
                metadata_receipt_failures[receipt_name] = receipt_errors
        structured_evidence["metadata_receipt_failures"] = metadata_receipt_failures
        if metadata_receipt_failures:
            errors.append("bibliography metadata receipt, Atom bytes, or parsed fields mismatch")

        source_receipts = json.loads(
            (ROOT / "paper/sources/prior-work-round2-source-receipts.json").read_text(encoding="utf-8")
        )
        source_receipt_ids = {x.get("source_id") for x in source_receipts}
        report_failures = []
        for receipt in source_receipts:
            report_path = ROOT / receipt.get("report_path", "")
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                report_failures.append(receipt.get("source_id"))
        structured_evidence["round2_source_receipt_count"] = len(source_receipts)
        structured_evidence["round2_source_receipt_ids"] = sorted(source_receipt_ids)
        structured_evidence["round2_report_failures"] = report_failures
        if (
            len(source_receipts) != expectations["round2_source_receipt_count"]
            or source_receipt_ids != required_source_ids
            or report_failures
        ):
            errors.append("round-2 full-read receipt or retained report mismatch")

        with (ROOT / "paper/evidence-matrix.csv").open(newline="", encoding="utf-8") as f:
            matrix_rows = list(csv.DictReader(f))
        matrix_record_type_counts = collections.Counter(row.get("record_type") for row in matrix_rows)
        expected_record_type_counts = expectations.get("evidence_matrix_record_type_counts", {})
        structured_evidence["evidence_matrix_csv_rows"] = len(matrix_rows)
        structured_evidence["evidence_matrix_record_type_counts"] = dict(matrix_record_type_counts)
        if (
            len(matrix_rows) != expectations["evidence_matrix_csv_rows"]
            or dict(matrix_record_type_counts) != expected_record_type_counts
        ):
            errors.append("evidence matrix row or record-type count mismatch")

        all_matrix_round2_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_source_ids
        )
        matrix_round2_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        matrix_round2_ids = set(matrix_round2_counts)
        matrix_round2_count_failures = {
            source_id: {
                "all_rows": all_matrix_round2_counts.get(source_id, 0),
                "admitted_rows": matrix_round2_counts.get(source_id, 0),
            }
            for source_id in required_source_ids
            if all_matrix_round2_counts.get(source_id, 0) != 1 or matrix_round2_counts.get(source_id, 0) != 1
        }
        structured_evidence["matrix_round2_source_ids"] = sorted(matrix_round2_ids)
        structured_evidence["matrix_round2_count_failures"] = matrix_round2_count_failures
        if matrix_round2_ids != required_source_ids or matrix_round2_count_failures:
            errors.append("round-2 evidence matrix source identity, admission fields, or uniqueness mismatch")

        component_names = [row.get("component") for row in matrix_rows if row.get("component")]
        duplicate_components = sorted(k for k, v in collections.Counter(component_names).items() if v > 1)
        structured_evidence["duplicate_components"] = duplicate_components
        if duplicate_components:
            errors.append("duplicate contribution ledger component rows")
        actual_tags = {row.get("component"): row.get("contribution_tag") for row in matrix_rows if row.get("component")}
        tag_failures = {
            component: {"expected": tag, "actual": actual_tags.get(component)}
            for component, tag in expectations["required_component_tags"].items()
            if actual_tags.get(component) != tag
        }
        structured_evidence["component_tag_failures"] = tag_failures
        if tag_failures:
            errors.append("contribution ledger classification mismatch")

    forbidden = []
    for pattern in cfg["forbidden_regexes"]:
        hits = line_hits(clean, pattern)
        if hits:
            forbidden.append({"pattern": pattern, "hits": hits})
    if forbidden:
        errors.append("forbidden test-instance/domain identifiers or fingerprint terms found")

    claim_hits = []
    for pattern in cfg["forbidden_claim_regexes"]:
        hits = line_hits(clean, pattern)
        if hits:
            claim_hits.append({"pattern": pattern, "hits": hits})
    if claim_hits:
        errors.append("possible unexecuted-result claim wording found")

    external_tex_inputs = sorted(set(re.findall(r"\\(?:input|include)\{([^}]+)\}", clean)))
    if external_tex_inputs:
        errors.append("external TeX input/include is outside the closed paper scan")

    missing_required = [s for s in cfg["required_substrings"] if s not in clean]
    if missing_required:
        errors.append("required disclosure/contract text missing from uncommented paper")

    brace_depth = 0
    brace_min = 0
    escaped = False
    for ch in clean:
        if ch == "\\" and not escaped:
            escaped = True
            continue
        if ch == "{" and not escaped:
            brace_depth += 1
        elif ch == "}" and not escaped:
            brace_depth -= 1
            brace_min = min(brace_min, brace_depth)
        escaped = False
    if brace_depth != 0 or brace_min < 0:
        errors.append("unbalanced braces")

    begins = re.findall(r"\\begin\{([^}]+)\}", clean)
    ends = re.findall(r"\\end\{([^}]+)\}", clean)
    env_delta = collections.Counter(begins)
    env_delta.subtract(ends)
    env_delta = {k: v for k, v in env_delta.items() if v}
    if env_delta:
        errors.append("unbalanced environments")

    cites = []
    for match in re.finditer(r"\\cite[tp]?\{([^}]+)\}", clean):
        cites.extend(x.strip() for x in match.group(1).split(","))
    bibs = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", clean)
    labels = re.findall(r"\\label\{([^}]+)\}", clean)
    refs = re.findall(r"\\(?:ref|eqref|pageref|autoref)\{([^}]+)\}", clean)
    duplicate_bibs = sorted(k for k, v in collections.Counter(bibs).items() if v > 1)
    duplicate_labels = sorted(k for k, v in collections.Counter(labels).items() if v > 1)
    missing_bibs = sorted(set(cites) - set(bibs))
    unused_bibs = sorted(set(bibs) - set(cites))
    missing_labels = sorted(set(refs) - set(labels))
    expected_bib_keys = set(cfg.get("required_bibliography", {}))
    unexpected_bibs = sorted(set(bibs) - expected_bib_keys)
    absent_required_bibs = sorted(expected_bib_keys - set(bibs))
    if (
        duplicate_bibs
        or duplicate_labels
        or missing_bibs
        or unused_bibs
        or missing_labels
        or unexpected_bibs
        or absent_required_bibs
    ):
        errors.append("citation/reference integrity or closed bibliography failure")

    bibliography_failures = {}
    for key, required in cfg["required_bibliography"].items():
        start = re.search(r"\\bibitem(?:\[[^\]]*\])?\{" + re.escape(key) + r"\}", clean)
        if not start:
            bibliography_failures[key] = ["bibitem missing"]
            continue
        next_item = re.search(r"\\bibitem", clean[start.end():])
        end = start.end() + next_item.start() if next_item else len(clean)
        entry = clean[start.start():end]
        absent = [s for s in required if s not in entry]
        if absent:
            bibliography_failures[key] = absent
    if bibliography_failures:
        errors.append("bibliographic author/title/version mismatch")

    tc_errors, tc_summary = verify_toolchain(cfg)
    errors.extend(tc_errors)
    builds = []
    deterministic = False
    output_pdf_sha = None
    if not tc_errors:
        with tempfile.TemporaryDirectory(prefix="argo-paper-orx-") as td:
            tmp = Path(td)
            shutil.copytree(Path(cfg["toolchain"]["root"]) / "home", tmp / "home")
            (tmp / "xdg-cache").mkdir()
            (tmp / "config").mkdir()
            first = compile_once(cfg, tmp, "build1")
            second = compile_once(cfg, tmp, "build2")
            builds = [{k: v for k, v in b.items() if k not in ("pdf_path", "log_tail")} for b in (first, second)]
            deterministic = bool(first["pdf_sha256"] and first["pdf_sha256"] == second["pdf_sha256"])
            output_pdf_sha = first["pdf_sha256"]
            for b in (first, second):
                if b["exit_code"] != 0 or not b["pdf_sha256"]:
                    errors.append("LaTeX compilation failed in " + b["name"] + ": " + b["log_tail"][-1000:])
                if b["undefined_citations"] or b["undefined_references"]:
                    errors.append("compiled document has unresolved citations/references")
                if b["overfull_boxes"] > cfg["max_overfull_boxes"]:
                    errors.append("compiled document has overfull boxes")
            if cfg["require_deterministic_pdf"] and not deterministic:
                errors.append("repeated fixed-environment PDF builds differ")
            if not errors and first["pdf_path"].is_file():
                shutil.copy2(str(first["pdf_path"]), str(ROOT / cfg["output_pdf"]))

    result = {
        "schema_version": "argo-thesis-paper-validation-result/v1",
        "status": "PASS" if not errors else "FAIL",
        "variant": cfg.get("variant", "unspecified paper variant"),
        "paper": {
            "path": cfg["paper_path"],
            "bytes": len(raw),
            "lines": len(text.splitlines()),
            "regex_words": len(re.findall(r"\b[\w'-]+\b", text)),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "anonymization": {"forbidden_pattern_count": len(cfg["forbidden_regexes"]), "violations": forbidden},
        "result_claim_scan": {"violations": claim_hits},
        "required_text_missing": missing_required,
        "external_tex_inputs": external_tex_inputs,
        "evidence_receipts": evidence_receipts,
        "structured_evidence": structured_evidence,
        "evidence_scope_note": cfg.get("evidence_scope_note"),
        "latex_static": {
            "brace_depth": brace_depth,
            "brace_minimum": brace_min,
            "environment_delta": env_delta,
            "citation_count": len(cites),
            "bibitem_count": len(bibs),
            "missing_bibitems": missing_bibs,
            "unused_bibitems": unused_bibs,
            "duplicate_bibitems": duplicate_bibs,
            "unexpected_bibitems": unexpected_bibs,
            "absent_required_bibitems": absent_required_bibs,
            "missing_labels": missing_labels,
            "duplicate_labels": duplicate_labels,
            "bibliography_failures": bibliography_failures,
        },
        "toolchain": tc_summary,
        "builds": builds,
        "deterministic_pdf": deterministic,
        "pdf_sha256": output_pdf_sha,
        "errors": errors,
    }
    print("ARGO_PAPER_VALIDATION_RESULT")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
