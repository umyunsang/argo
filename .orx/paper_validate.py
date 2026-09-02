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


def canonical_json_sha(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def makefile_dependency_paths(path):
    text = path.read_text(encoding="utf-8", errors="replace").replace("\\\n", "")
    if ":" not in text:
        return []
    rhs = text.split(":", 1)[1]
    tokens = re.findall(r"(?:\\.|[^\s])+", rhs)
    return [
        token.replace("\\ ", " ").replace("\\#", "#").replace("\\:", ":").replace("\\\\", "\\")
        for token in tokens
        if token
    ]


def path_is_within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


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


def public_token_hits(text, patterns):
    hits = []
    for item in patterns:
        matched = line_hits(text, item["pattern"])
        if matched:
            hits.append({"id": item["id"], "hits": matched})
    return hits


def scan_public_sources(cfg):
    gate = cfg["public_output_gate"]
    paths = []
    for relpath in gate.get("source_paths", []):
        path = ROOT / relpath
        if path.is_file():
            paths.append(path)
    for pattern in gate.get("source_globs", []):
        paths.extend(path for path in ROOT.glob(pattern) if path.is_file())
    unique_paths = sorted(set(paths))
    failures = {}
    for path in unique_paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = public_token_hits(text, gate["patterns"])
        if hits:
            failures[str(path.relative_to(ROOT))] = hits
    return unique_paths, failures


def scan_pdf_text(cfg, pdf_path):
    gate = cfg["public_output_gate"]
    extractor = Path(gate["pdf_text_extractor_path"])
    if not extractor.is_file() or sha256_path(extractor) != gate["pdf_text_extractor_sha256"]:
        return None, "PDF text extractor missing or digest mismatch"
    proc = subprocess.run(
        [str(extractor), str(pdf_path), "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
        check=False,
    )
    if proc.returncode != 0:
        return None, "PDF text extraction failed: " + proc.stderr[-500:]
    return public_token_hits(proc.stdout, gate["patterns"]), None


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
    source_dir = tmp / (name + "-source")
    source_dir.mkdir()
    isolated_paper = source_dir / "paper.tex"
    shutil.copy2(str(ROOT / cfg["paper_path"]), str(isolated_paper))
    isolated_paper.chmod(0o444)
    dependency_rules = outdir / "dependencies.mk"
    cmd = [
        tc["binary_path"], "-X", "compile", "-C", "--untrusted",
        "--makefile-rules", str(dependency_rules),
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
        cmd, cwd=str(source_dir), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    dependency_paths = makefile_dependency_paths(dependency_rules) if dependency_rules.is_file() else []
    dependency_violations = []
    source_root = source_dir.resolve()
    allowed_roots = [tmp.resolve(), Path(tc["root"]).resolve()]
    for raw_dependency in dependency_paths:
        dependency = Path(raw_dependency)
        if not dependency.is_absolute():
            dependency = (source_dir / dependency).resolve()
        else:
            dependency = dependency.resolve()
        if path_is_within(dependency, source_root) and dependency != isolated_paper.resolve():
            dependency_violations.append(str(dependency))
        elif not any(path_is_within(dependency, root) for root in allowed_roots):
            dependency_violations.append(str(dependency))
    if not dependency_rules.is_file() or str(isolated_paper.resolve()) not in {
        str((source_dir / Path(x)).resolve()) if not Path(x).is_absolute() else str(Path(x).resolve())
        for x in dependency_paths
    }:
        dependency_violations.append("<missing isolated paper dependency>")
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
        "isolated_input_sha256": sha256_path(isolated_paper),
        "dependency_rules_sha256": sha256_path(dependency_rules) if dependency_rules.is_file() else None,
        "dependency_count": len(dependency_paths),
        "dependency_paths_sha256": canonical_json_sha(sorted(dependency_paths)),
        "dependency_paths": dependency_paths,
        "dependency_violations": sorted(set(dependency_violations)),
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

    public_source_paths, public_source_token_failures = scan_public_sources(cfg)
    if public_source_token_failures:
        errors.append("forbidden public-paper token found in manuscript, bibliography, or figure source")
    gate = cfg["public_output_gate"]
    pdf_text_extractor = Path(gate["pdf_text_extractor_path"])
    pdf_text_extractor_verified = (
        pdf_text_extractor.is_file()
        and sha256_path(pdf_text_extractor) == gate["pdf_text_extractor_sha256"]
    )
    if not pdf_text_extractor_verified:
        errors.append("public-output PDF text extractor identity mismatch")

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
        required_locator_ids.update(expectations.get("required_round3_locator_ids", []))
        required_locator_ids.update(expectations.get("required_round4_locator_ids", []))
        required_locator_ids.update(expectations.get("required_round5_locator_ids", []))
        required_locator_ids.update(expectations.get("required_round6_locator_ids", []))
        required_locator_ids.update(expectations.get("required_round7_locator_ids", []))
        required_locator_ids.update(expectations.get("required_external_code_locator_ids", []))
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
        expected_round3_locator_counts = expectations.get("required_round3_locator_counts", {})
        actual_round3_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round3_locator_counts
        )
        round3_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round3_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round3_locator_counts.items()
            if actual_round3_locator_counts.get(source_id, 0) != expected
        }
        expected_round4_locator_counts = expectations.get("required_round4_locator_counts", {})
        actual_round4_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round4_locator_counts
        )
        round4_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round4_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round4_locator_counts.items()
            if actual_round4_locator_counts.get(source_id, 0) != expected
        }

        expected_round5_locator_counts = expectations.get("required_round5_locator_counts", {})
        actual_round5_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round5_locator_counts
        )
        round5_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round5_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round5_locator_counts.items()
            if actual_round5_locator_counts.get(source_id, 0) != expected
        }
        expected_round6_locator_counts = expectations.get("required_round6_locator_counts", {})
        actual_round6_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round6_locator_counts
        )
        round6_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round6_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round6_locator_counts.items()
            if actual_round6_locator_counts.get(source_id, 0) != expected
        }
        expected_round7_locator_counts = expectations.get("required_round7_locator_counts", {})
        actual_round7_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_round7_locator_counts
        )
        round7_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_round7_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_round7_locator_counts.items()
            if actual_round7_locator_counts.get(source_id, 0) != expected
        }
        expected_external_code_locator_counts = expectations.get("required_external_code_locator_counts", {})
        actual_external_code_locator_counts = collections.Counter(
            x.get("source_id") for x in locators if x.get("source_id") in expected_external_code_locator_counts
        )
        external_code_locator_count_failures = {
            source_id: {"expected": expected, "actual": actual_external_code_locator_counts.get(source_id, 0)}
            for source_id, expected in expected_external_code_locator_counts.items()
            if actual_external_code_locator_counts.get(source_id, 0) != expected
        }

        expected_locator_sources = dict(expectations.get("required_round2_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_round3_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_round4_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_round5_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_round6_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_round7_locator_sources", {}))
        expected_locator_sources.update(expectations.get("required_external_code_locator_sources", {}))
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
        structured_evidence["round3_locator_count_failures"] = round3_locator_count_failures
        structured_evidence["round4_locator_count_failures"] = round4_locator_count_failures
        structured_evidence["round5_locator_count_failures"] = round5_locator_count_failures
        structured_evidence["round6_locator_count_failures"] = round6_locator_count_failures
        structured_evidence["round7_locator_count_failures"] = round7_locator_count_failures
        structured_evidence["external_code_locator_count_failures"] = external_code_locator_count_failures
        structured_evidence["locator_source_failures"] = locator_source_failures
        if (
            len(locators) != expectations["reviewed_locator_count"]
            or reviewed_count != expectations["reviewed_locator_count"]
            or locator_hash_failures
            or missing_locator_ids
            or duplicate_locator_ids
            or round2_locator_count_failures
            or round3_locator_count_failures
            or round4_locator_count_failures
            or round5_locator_count_failures
            or round6_locator_count_failures
            or round7_locator_count_failures
            or external_code_locator_count_failures
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
        required_round2_source_ids = set(expectations.get("required_round2_source_ids", []))
        structured_evidence["round2_bibliography_metadata_record_count"] = round2_metadata_count
        structured_evidence["round2_metadata_source_ids"] = sorted(round2_metadata_source_ids)
        if (
            round2_metadata_count != expectations["round2_bibliography_metadata_record_count"]
            or round2_metadata_source_ids != required_round2_source_ids
        ):
            errors.append("round-2 bibliography metadata identity mismatch")

        round3_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-prior-work-round3-receipt.json").read_text(encoding="utf-8")
        )
        round3_metadata_records = round3_metadata_obj.get("records", [])
        round3_metadata_count = len(round3_metadata_records)
        round3_metadata_source_ids = {x.get("source_id") for x in round3_metadata_records}
        required_round3_source_ids = set(expectations.get("required_round3_source_ids", []))
        structured_evidence["round3_bibliography_metadata_record_count"] = round3_metadata_count
        structured_evidence["round3_metadata_source_ids"] = sorted(round3_metadata_source_ids)
        if (
            round3_metadata_count != expectations["round3_bibliography_metadata_record_count"]
            or round3_metadata_source_ids != required_round3_source_ids
        ):
            errors.append("round-3 bibliography metadata identity mismatch")

        round4_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-foundations-round4-receipt.json").read_text(encoding="utf-8")
        )
        round4_metadata_records = round4_metadata_obj.get("records", [])
        round4_metadata_count = len(round4_metadata_records)
        round4_metadata_source_ids = {x.get("source_id") for x in round4_metadata_records}
        required_round4_source_ids = set(expectations.get("required_round4_source_ids", []))
        structured_evidence["round4_bibliography_metadata_record_count"] = round4_metadata_count
        structured_evidence["round4_metadata_source_ids"] = sorted(round4_metadata_source_ids)
        if (
            round4_metadata_count != expectations["round4_bibliography_metadata_record_count"]
            or round4_metadata_source_ids != required_round4_source_ids
        ):
            errors.append("round-4 bibliography metadata identity mismatch")

        round5_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-adaptive-round5-receipt.json").read_text(encoding="utf-8")
        )
        round5_metadata_records = round5_metadata_obj.get("records", [])
        round5_metadata_count = len(round5_metadata_records)
        round5_metadata_source_ids = {x.get("source_id") for x in round5_metadata_records}
        required_round5_source_ids = set(expectations.get("required_round5_source_ids", []))
        structured_evidence["round5_bibliography_metadata_record_count"] = round5_metadata_count
        structured_evidence["round5_metadata_source_ids"] = sorted(round5_metadata_source_ids)
        if (
            round5_metadata_count != expectations["round5_bibliography_metadata_record_count"]
            or round5_metadata_source_ids != required_round5_source_ids
        ):
            errors.append("round-5 bibliography metadata identity mismatch")

        round6_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-architecture-round6-receipt.json").read_text(encoding="utf-8")
        )
        round6_metadata_records = round6_metadata_obj.get("records", [])
        round6_metadata_count = len(round6_metadata_records)
        round6_metadata_source_ids = {x.get("source_id") for x in round6_metadata_records}
        required_round6_source_ids = set(expectations.get("required_round6_source_ids", []))
        structured_evidence["round6_bibliography_metadata_record_count"] = round6_metadata_count
        structured_evidence["round6_metadata_source_ids"] = sorted(round6_metadata_source_ids)
        if (
            round6_metadata_count != expectations["round6_bibliography_metadata_record_count"]
            or round6_metadata_source_ids != required_round6_source_ids
        ):
            errors.append("round-6 bibliography metadata identity mismatch")

        round7_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-literature-round7-receipt.json").read_text(encoding="utf-8")
        )
        round7_metadata_records = round7_metadata_obj.get("records", [])
        round7_metadata_count = len(round7_metadata_records)
        round7_metadata_source_ids = {x.get("source_id") for x in round7_metadata_records}
        required_round7_source_ids = set(expectations.get("required_round7_source_ids", []))
        version_boundary = round7_metadata_obj.get("version_boundary", {})
        latest_response_path = ROOT / version_boundary.get("latest_response_path", "")
        version_boundary_failures = []
        if (
            version_boundary.get("source_id") != "2607.08665"
            or version_boundary.get("bound_version") != "v1"
            or version_boundary.get("latest_version_at_retrieval") != "v2"
            or not latest_response_path.is_file()
            or latest_response_path.stat().st_size != version_boundary.get("latest_response_bytes")
            or sha256_path(latest_response_path) != version_boundary.get("latest_response_sha256")
        ):
            version_boundary_failures.append("identity_or_bytes")
        else:
            try:
                latest_records = parse_arxiv_atom(latest_response_path)
            except (ET.ParseError, ValueError):
                latest_records = {}
                version_boundary_failures.append("latest_atom_parse")
            if latest_records.get("2607.08665", {}).get("version") != "v2":
                version_boundary_failures.append("latest_version_not_rederived")
        structured_evidence["round7_bibliography_metadata_record_count"] = round7_metadata_count
        structured_evidence["round7_metadata_source_ids"] = sorted(round7_metadata_source_ids)
        structured_evidence["round7_version_boundary_failures"] = version_boundary_failures
        if (
            round7_metadata_count != expectations["round7_bibliography_metadata_record_count"]
            or round7_metadata_source_ids != required_round7_source_ids
            or version_boundary_failures
        ):
            errors.append("round-7 bibliography metadata identity or explicit version boundary mismatch")

        combined_metadata_records = (
            metadata_obj.get("records", []) + round2_metadata_records
            + round3_metadata_records + round4_metadata_records + round5_metadata_records
            + round6_metadata_records + round7_metadata_records
            + json.loads(
                (ROOT / "paper/sources/arxiv-metadata-literature-round8-receipt.json").read_text(encoding="utf-8")
            ).get("records", [])
            + json.loads(
                (ROOT / "paper/sources/arxiv-metadata-literature-round9-receipt.json").read_text(encoding="utf-8")
            ).get("records", [])
            + json.loads(
                (ROOT / "paper/sources/arxiv-metadata-literature-round10-receipt.json").read_text(encoding="utf-8")
            ).get("records", [])
            + json.loads(
                (ROOT / "paper/sources/arxiv-metadata-literature-round14-receipt.json").read_text(encoding="utf-8")
            ).get("records", [])
            + json.loads(
                (ROOT / "paper/sources/arxiv-metadata-literature-round16-receipt.json").read_text(encoding="utf-8")
            ).get("records", [])
        )
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
            ("round3", round3_metadata_obj),
            ("round4", round4_metadata_obj),
            ("round5", round5_metadata_obj),
            ("round6", round6_metadata_obj),
            ("round7", round7_metadata_obj),
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

        original_report_receipts = json.loads(
            (ROOT / "paper/sources/report-receipts.json").read_text(encoding="utf-8")
        )
        original_report_ids = {x.get("source_id") for x in original_report_receipts}
        required_original_report_ids = set(expectations.get("required_original_report_source_ids", []))
        original_report_failures = []
        for receipt in original_report_receipts:
            report_path = ROOT / receipt.get("path", "")
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("bytes")
                or sha256_path(report_path) != receipt.get("sha256")
            ):
                original_report_failures.append(receipt.get("source_id"))
        structured_evidence["original_report_receipt_count"] = len(original_report_receipts)
        structured_evidence["original_report_source_ids"] = sorted(original_report_ids)
        structured_evidence["original_report_failures"] = original_report_failures
        if (
            len(original_report_receipts) != expectations["original_report_receipt_count"]
            or original_report_ids != required_original_report_ids
            or original_report_failures
        ):
            errors.append("original full-read receipt or tracked report mismatch")

        round2_source_receipts = json.loads(
            (ROOT / "paper/sources/prior-work-round2-source-receipts.json").read_text(encoding="utf-8")
        )
        round2_source_receipt_ids = {x.get("source_id") for x in round2_source_receipts}
        round2_report_failures = []
        round2_version_failures = {}
        for receipt in round2_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round2_report_failures.append(source_id)
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            version_check = receipt.get("version_verification", {})
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
                or version_check.get("versioned_artifact_url") != expected_src_url
                or version_check.get("download_sha256") != receipt.get("archive_sha256")
                or version_check.get("matches_retained_archive") is not True
            ):
                round2_version_failures[source_id] = {
                    "expected_version": expected_version,
                    "actual_version": receipt.get("version"),
                }
        structured_evidence["round2_source_receipt_count"] = len(round2_source_receipts)
        structured_evidence["round2_source_receipt_ids"] = sorted(round2_source_receipt_ids)
        structured_evidence["round2_report_failures"] = round2_report_failures
        structured_evidence["round2_source_version_failures"] = round2_version_failures
        if (
            len(round2_source_receipts) != expectations["round2_source_receipt_count"]
            or round2_source_receipt_ids != required_round2_source_ids
            or round2_report_failures
            or round2_version_failures
        ):
            errors.append("round-2 full-read receipt, version, URL, or retained report mismatch")

        round3_source_receipts = json.loads(
            (ROOT / "paper/sources/prior-work-round3-source-receipts.json").read_text(encoding="utf-8")
        )
        round3_source_receipt_ids = {x.get("source_id") for x in round3_source_receipts}
        round3_report_failures = []
        round3_version_failures = {}
        for receipt in round3_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round3_report_failures.append(source_id)
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
            ):
                round3_version_failures[source_id] = {
                    "expected": expected_version,
                    "actual": receipt.get("version"),
                }
        structured_evidence["round3_source_receipt_count"] = len(round3_source_receipts)
        structured_evidence["round3_source_receipt_ids"] = sorted(round3_source_receipt_ids)
        structured_evidence["round3_report_failures"] = round3_report_failures
        structured_evidence["round3_source_version_failures"] = round3_version_failures
        if (
            len(round3_source_receipts) != expectations["round3_source_receipt_count"]
            or round3_source_receipt_ids != required_round3_source_ids
            or round3_report_failures
            or round3_version_failures
        ):
            errors.append("round-3 full-read receipt, version, or retained report mismatch")

        round4_source_receipts = json.loads(
            (ROOT / "paper/sources/foundations-round4-source-receipts.json").read_text(encoding="utf-8")
        )
        round4_source_receipt_ids = {x.get("source_id") for x in round4_source_receipts}
        round4_report_failures = []
        round4_version_failures = {}
        for receipt in round4_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round4_report_failures.append(source_id)
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
            ):
                round4_version_failures[source_id] = {
                    "expected": expected_version,
                    "actual": receipt.get("version"),
                }
        structured_evidence["round4_source_receipt_count"] = len(round4_source_receipts)
        structured_evidence["round4_source_receipt_ids"] = sorted(round4_source_receipt_ids)
        structured_evidence["round4_report_failures"] = round4_report_failures
        structured_evidence["round4_source_version_failures"] = round4_version_failures
        if (
            len(round4_source_receipts) != expectations["round4_source_receipt_count"]
            or round4_source_receipt_ids != required_round4_source_ids
            or round4_report_failures
            or round4_version_failures
        ):
            errors.append("round-4 full-read receipt, version, URL, or retained report mismatch")

        round5_source_receipts = json.loads(
            (ROOT / "paper/sources/adaptive-round5-source-receipts.json").read_text(encoding="utf-8")
        )
        round5_source_receipt_ids = {x.get("source_id") for x in round5_source_receipts}
        round5_report_failures = []
        round5_fulltext_failures = []
        round5_version_failures = {}
        for receipt in round5_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            fulltext_path = ROOT / receipt.get("fulltext_path", "")
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round5_report_failures.append(source_id)
            if (
                not fulltext_path.is_file()
                or fulltext_path.stat().st_size != receipt.get("fulltext_bytes")
                or sha256_path(fulltext_path) != receipt.get("fulltext_sha256")
            ):
                round5_fulltext_failures.append(source_id)
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
            ):
                round5_version_failures[source_id] = {
                    "expected": expected_version,
                    "actual": receipt.get("version"),
                }
        structured_evidence["round5_source_receipt_count"] = len(round5_source_receipts)
        structured_evidence["round5_source_receipt_ids"] = sorted(round5_source_receipt_ids)
        structured_evidence["round5_report_failures"] = round5_report_failures
        structured_evidence["round5_fulltext_failures"] = round5_fulltext_failures
        structured_evidence["round5_source_version_failures"] = round5_version_failures
        if (
            len(round5_source_receipts) != expectations["round5_source_receipt_count"]
            or round5_source_receipt_ids != required_round5_source_ids
            or round5_report_failures
            or round5_fulltext_failures
            or round5_version_failures
        ):
            errors.append("round-5 full-read receipt, version, URL, report, or full-text mismatch")

        round6_source_receipts = json.loads(
            (ROOT / "paper/sources/architecture-round6-source-receipts.json").read_text(encoding="utf-8")
        )
        round6_source_receipt_ids = {x.get("source_id") for x in round6_source_receipts}
        round6_report_failures = []
        round6_fulltext_failures = []
        round6_version_failures = {}
        for receipt in round6_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            fulltext_path = ROOT / receipt.get("fulltext_path", "")
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round6_report_failures.append(source_id)
            if (
                not fulltext_path.is_file()
                or fulltext_path.stat().st_size != receipt.get("fulltext_bytes")
                or sha256_path(fulltext_path) != receipt.get("fulltext_sha256")
            ):
                round6_fulltext_failures.append(source_id)
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
            ):
                round6_version_failures[source_id] = {
                    "expected": expected_version,
                    "actual": receipt.get("version"),
                }
        structured_evidence["round6_source_receipt_count"] = len(round6_source_receipts)
        structured_evidence["round6_source_receipt_ids"] = sorted(round6_source_receipt_ids)
        structured_evidence["round6_report_failures"] = round6_report_failures
        structured_evidence["round6_fulltext_failures"] = round6_fulltext_failures
        structured_evidence["round6_source_version_failures"] = round6_version_failures
        if (
            len(round6_source_receipts) != expectations["round6_source_receipt_count"]
            or round6_source_receipt_ids != required_round6_source_ids
            or round6_report_failures
            or round6_fulltext_failures
            or round6_version_failures
        ):
            errors.append("round-6 full-read receipt, version, URL, report, or full-text mismatch")

        round7_source_receipts = json.loads(
            (ROOT / "paper/sources/literature-round7-source-receipts.json").read_text(encoding="utf-8")
        )
        round7_source_receipt_ids = {x.get("source_id") for x in round7_source_receipts}
        round7_report_failures = []
        round7_fulltext_failures = []
        round7_version_failures = {}
        round7_tex_manifest_failures = []
        round7_locator_manifest_failures = []
        expected_round7_locator_counts = expectations.get("required_round7_locator_counts", {})
        for receipt in round7_source_receipts:
            source_id = receipt.get("source_id")
            report_path = ROOT / receipt.get("report_path", "")
            fulltext_path = ROOT / receipt.get("fulltext_path", "")
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            expected_abs_url = "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
            expected_src_url = "https://arxiv.org/src/%s%s" % (source_id, expected_version)
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or not report_path.is_file()
                or report_path.stat().st_size != receipt.get("report_bytes")
                or sha256_path(report_path) != receipt.get("report_sha256")
            ):
                round7_report_failures.append(source_id)
            fulltext_has_version = False
            if fulltext_path.is_file():
                fulltext_text = fulltext_path.read_text(encoding="utf-8", errors="replace")
                fulltext_has_version = bool(
                    re.search(r"arXiv:%s%s\b" % (re.escape(source_id), re.escape(expected_version or "")), fulltext_text, re.I)
                )
            if (
                not fulltext_path.is_file()
                or fulltext_path.stat().st_size != receipt.get("fulltext_bytes")
                or sha256_path(fulltext_path) != receipt.get("fulltext_sha256")
                or not fulltext_has_version
            ):
                round7_fulltext_failures.append(source_id)
            if (
                receipt.get("version") != expected_version
                or receipt.get("url") != expected_abs_url
                or receipt.get("artifact_url") != expected_src_url
            ):
                round7_version_failures[source_id] = {
                    "expected": expected_version,
                    "actual": receipt.get("version"),
                }
            tex_root = ROOT / receipt.get("extracted_path", "")
            tex_files = receipt.get("tex_files", [])
            if (
                receipt.get("tex_file_count") != len(tex_files)
                or not tex_files
                or any(not (tex_root / relpath).is_file() for relpath in tex_files)
            ):
                round7_tex_manifest_failures.append(source_id)
            if (
                len(receipt.get("claim_locator_ids", [])) != expected_round7_locator_counts.get(source_id)
                or set(receipt.get("claim_locator_ids", []))
                != {
                    x.get("claim_locator_id")
                    for x in locators
                    if x.get("source_id") == source_id
                }
            ):
                round7_locator_manifest_failures.append(source_id)
        structured_evidence["round7_source_receipt_count"] = len(round7_source_receipts)
        structured_evidence["round7_source_receipt_ids"] = sorted(round7_source_receipt_ids)
        structured_evidence["round7_report_failures"] = round7_report_failures
        structured_evidence["round7_fulltext_failures"] = round7_fulltext_failures
        structured_evidence["round7_source_version_failures"] = round7_version_failures
        structured_evidence["round7_tex_manifest_failures"] = round7_tex_manifest_failures
        structured_evidence["round7_locator_manifest_failures"] = round7_locator_manifest_failures
        if (
            len(round7_source_receipts) != expectations["round7_source_receipt_count"]
            or round7_source_receipt_ids != required_round7_source_ids
            or round7_report_failures
            or round7_fulltext_failures
            or round7_version_failures
            or round7_tex_manifest_failures
            or round7_locator_manifest_failures
        ):
            errors.append("round-7 full-read receipt, version, URL, report, full-text, TeX, or locator mismatch")

        round4_locator_source_failures = []
        for locator in locators:
            if locator.get("source_id") not in required_round4_source_ids:
                continue
            source_path = ROOT / locator.get("source_file", "")
            source_lines = (
                source_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if source_path.is_file()
                else []
            )
            start_line = locator.get("line_start", 0)
            end_line = locator.get("line_end", 0)
            observed_excerpt = (
                "\n".join(source_lines[start_line - 1:end_line])
                if 0 < start_line <= end_line <= len(source_lines)
                else None
            )
            if (
                not source_path.is_file()
                or sha256_path(source_path) != locator.get("source_file_sha256")
                or observed_excerpt != locator.get("excerpt")
            ):
                round4_locator_source_failures.append(locator.get("claim_locator_id"))
        structured_evidence["round4_locator_source_failures"] = round4_locator_source_failures
        if round4_locator_source_failures:
            errors.append("round-4 tracked locator source file, hash, or line slice mismatch")

        adaptive_locator_source_ids = required_round5_source_ids | required_round6_source_ids | required_round7_source_ids | set(
            expectations.get("required_external_code_locator_counts", {})
        )
        adaptive_locator_source_failures = []
        for locator in locators:
            if locator.get("source_id") not in adaptive_locator_source_ids:
                continue
            source_path = ROOT / locator.get("source_file", "")
            source_lines = (
                source_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if source_path.is_file()
                else []
            )
            start_line = locator.get("line_start", 0)
            end_line = locator.get("line_end", 0)
            observed_excerpt = (
                "\n".join(source_lines[start_line - 1:end_line])
                if 0 < start_line <= end_line <= len(source_lines)
                else None
            )
            if (
                not source_path.is_file()
                or sha256_path(source_path) != locator.get("source_file_sha256")
                or observed_excerpt != locator.get("excerpt")
            ):
                adaptive_locator_source_failures.append(locator.get("claim_locator_id"))
        structured_evidence["adaptive_locator_source_failures"] = adaptive_locator_source_failures
        if adaptive_locator_source_failures:
            errors.append("adaptive tracked locator source file, hash, or line slice mismatch")

        global_locator_failures = {}
        for locator in locators:
            locator_id = locator.get("claim_locator_id")
            source_path = ROOT / locator.get("source_file", "")
            if not source_path.is_file():
                global_locator_failures[locator_id] = "source file absent from repository"
                continue
            if sha256_path(source_path) != locator.get("source_file_sha256"):
                global_locator_failures[locator_id] = "source file digest mismatch"
                continue
            source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
            start_line = locator.get("line_start", 0)
            end_line = locator.get("line_end", 0)
            if not 0 < start_line <= end_line <= len(source_lines):
                global_locator_failures[locator_id] = "line range outside source"
                continue
            if "\n".join(source_lines[start_line - 1:end_line]) != locator.get("excerpt"):
                global_locator_failures[locator_id] = "line slice differs from excerpt"
        structured_evidence["global_locator_source_failures"] = global_locator_failures
        structured_evidence["global_locator_verified_count"] = len(locators) - len(global_locator_failures)
        if global_locator_failures:
            errors.append("claim locator source bytes are not re-derivable from the repository")

        restoration_obj = json.loads(
            (ROOT / "paper/sources/legacy-source-restoration-receipt.json").read_text(encoding="utf-8")
        )
        restoration_failures = []
        for entry in restoration_obj.get("restored_files", []):
            restored_path = ROOT / entry.get("path", "")
            if not restored_path.is_file() or sha256_path(restored_path) != entry.get("sha256"):
                restoration_failures.append(entry.get("path"))
        restoration_verification = restoration_obj.get("locator_verification", {})
        if (
            restoration_verification.get("verified_from_bytes")
            != restoration_verification.get("locator_count")
            or restoration_verification.get("locator_count", 0) > len(locators)
        ):
            restoration_failures.append("locator_verification_count")
        structured_evidence["legacy_restoration_failures"] = restoration_failures
        if restoration_failures:
            errors.append("legacy source restoration receipt does not match retained bytes")

        correction_obj = json.loads(
            (ROOT / "paper/sources/report-corrections.json").read_text(encoding="utf-8")
        )
        corrections = correction_obj.get("corrections", [])
        correction_ids = [x.get("correction_id") for x in corrections]
        required_correction_ids = set(expectations.get("required_report_correction_ids", []))
        required_correction_statuses = expectations.get("required_report_correction_statuses", {})
        correction_source_receipts = round3_source_receipts + round4_source_receipts
        correction_receipts_by_id = {x.get("source_id"): x for x in correction_source_receipts}
        correction_failures = []
        for correction in corrections:
            correction_id = correction.get("correction_id")
            source_id = correction.get("source_id")
            report_path = ROOT / correction.get("report_path", "")
            source_path = ROOT / correction.get("authoritative_source_file", "")
            report_lines = (
                report_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if report_path.is_file()
                else []
            )
            source_lines = (
                source_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if source_path.is_file()
                else []
            )
            report_line_number = correction.get("report_line", 0)
            observed_report_line = (
                report_lines[report_line_number - 1]
                if 0 < report_line_number <= len(report_lines)
                else None
            )
            source_start = correction.get("authoritative_line_start", 0)
            source_end = correction.get("authoritative_line_end", 0)
            observed_source_excerpt = (
                "\n".join(source_lines[source_start - 1:source_end])
                if 0 < source_start <= source_end <= len(source_lines)
                else None
            )
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            receipt_version = correction_receipts_by_id.get(source_id, {}).get("version")
            if (
                correction.get("status") != required_correction_statuses.get(correction_id)
                or correction.get("version") != expected_version
                or receipt_version != expected_version
                or not report_path.is_file()
                or sha256_path(report_path) != correction.get("report_sha256")
                or observed_report_line != correction.get("report_value")
                or not source_path.is_file()
                or sha256_path(source_path) != correction.get("authoritative_source_file_sha256")
                or observed_source_excerpt != correction.get("authoritative_excerpt")
                or hashlib.sha256((observed_source_excerpt or "").encode("utf-8")).hexdigest()
                != correction.get("authoritative_excerpt_sha256")
                or correction.get("authoritative_value", "") not in (observed_source_excerpt or "")
            ):
                correction_failures.append(correction_id)
        linked_correction_ids = {
            correction_id
            for receipt in correction_source_receipts
            for correction_id in receipt.get("report_correction_ids", [])
        }
        correction_source_ids = required_round3_source_ids | required_round4_source_ids
        expected_correction_ids_by_source = {
            source_id: sorted(
                correction.get("correction_id")
                for correction in corrections
                if correction.get("source_id") == source_id
            )
            for source_id in correction_source_ids
        }
        receipt_correction_ids_by_source = {
            receipt.get("source_id"): sorted(receipt.get("report_correction_ids", []))
            for receipt in correction_source_receipts
        }
        correction_ownership_failures = {
            source_id: {
                "expected": expected_ids,
                "actual": receipt_correction_ids_by_source.get(source_id, []),
            }
            for source_id, expected_ids in expected_correction_ids_by_source.items()
            if receipt_correction_ids_by_source.get(source_id, []) != expected_ids
        }
        structured_evidence["report_correction_ids"] = sorted(correction_ids)
        structured_evidence["report_correction_failures"] = correction_failures
        structured_evidence["report_correction_ownership_failures"] = correction_ownership_failures
        if (
            set(correction_ids) != required_correction_ids
            or len(correction_ids) != len(set(correction_ids))
            or set(required_correction_statuses) != required_correction_ids
            or linked_correction_ids != required_correction_ids
            or correction_ownership_failures
            or correction_failures
        ):
            errors.append("report correction identity, version, linkage, source slice, or rejected-value mismatch")

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

        matrix_facets = {
            row.get("facet") for row in matrix_rows if row.get("record_type") == "facet_evidence"
        }
        required_facets = set(expectations.get("required_evidence_facets", []))
        structured_evidence["evidence_matrix_facets"] = sorted(matrix_facets)
        structured_evidence["missing_evidence_facets"] = sorted(required_facets - matrix_facets)
        structured_evidence["unexpected_evidence_facets"] = sorted(matrix_facets - required_facets)
        if matrix_facets != required_facets:
            errors.append("evidence matrix facet coverage mismatch")

        all_matrix_round2_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round2_source_ids
        )
        matrix_round2_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round2_source_ids
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
            for source_id in required_round2_source_ids
            if all_matrix_round2_counts.get(source_id, 0) != 1
            or matrix_round2_counts.get(source_id, 0) != 1
        }
        structured_evidence["matrix_round2_source_ids"] = sorted(matrix_round2_ids)
        structured_evidence["matrix_round2_count_failures"] = matrix_round2_count_failures
        if matrix_round2_ids != required_round2_source_ids or matrix_round2_count_failures:
            errors.append("round-2 evidence matrix source identity, admission fields, or uniqueness mismatch")

        all_matrix_round3_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round3_source_ids
        )
        matrix_round3_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round3_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        matrix_round3_ids = set(matrix_round3_counts)
        expected_round3_matrix_counts = expectations.get("required_round3_matrix_counts", {})
        matrix_round3_count_failures = {
            source_id: {
                "expected": expected,
                "all_rows": all_matrix_round3_counts.get(source_id, 0),
                "admitted_rows": matrix_round3_counts.get(source_id, 0),
            }
            for source_id, expected in expected_round3_matrix_counts.items()
            if all_matrix_round3_counts.get(source_id, 0) != expected
            or matrix_round3_counts.get(source_id, 0) != expected
        }
        structured_evidence["matrix_round3_source_ids"] = sorted(matrix_round3_ids)
        structured_evidence["matrix_round3_count_failures"] = matrix_round3_count_failures
        if matrix_round3_ids != required_round3_source_ids or matrix_round3_count_failures:
            errors.append("round-3 evidence matrix source identity, admission fields, or expected facet-link count mismatch")

        all_matrix_round4_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round4_source_ids
        )
        matrix_round4_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round4_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        expected_round4_matrix_counts = expectations.get("required_round4_matrix_counts", {})
        matrix_round4_count_failures = {
            source_id: {
                "expected": expected,
                "all_rows": all_matrix_round4_counts.get(source_id, 0),
                "admitted_rows": matrix_round4_counts.get(source_id, 0),
            }
            for source_id, expected in expected_round4_matrix_counts.items()
            if all_matrix_round4_counts.get(source_id, 0) != expected
            or matrix_round4_counts.get(source_id, 0) != expected
        }
        structured_evidence["matrix_round4_source_ids"] = sorted(matrix_round4_counts)
        structured_evidence["matrix_round4_count_failures"] = matrix_round4_count_failures
        if set(matrix_round4_counts) != required_round4_source_ids or matrix_round4_count_failures:
            errors.append("round-4 evidence matrix source identity, admission fields, or expected facet-link count mismatch")

        all_matrix_round5_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round5_source_ids
        )
        matrix_round5_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round5_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        expected_round5_matrix_counts = expectations.get("required_round5_matrix_counts", {})
        matrix_round5_count_failures = {
            source_id: {
                "expected": expected,
                "all_rows": all_matrix_round5_counts.get(source_id, 0),
                "admitted_rows": matrix_round5_counts.get(source_id, 0),
            }
            for source_id, expected in expected_round5_matrix_counts.items()
            if all_matrix_round5_counts.get(source_id, 0) != expected
            or matrix_round5_counts.get(source_id, 0) != expected
        }
        structured_evidence["matrix_round5_source_ids"] = sorted(matrix_round5_counts)
        structured_evidence["matrix_round5_count_failures"] = matrix_round5_count_failures
        if set(matrix_round5_counts) != required_round5_source_ids or matrix_round5_count_failures:
            errors.append("round-5 evidence matrix source identity, admission fields, or expected facet-link count mismatch")

        all_matrix_round6_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round6_source_ids
        )
        matrix_round6_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round6_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        expected_round6_matrix_counts = expectations.get("required_round6_matrix_counts", {})
        matrix_round6_count_failures = {
            source_id: {
                "expected": expected,
                "all_rows": all_matrix_round6_counts.get(source_id, 0),
                "admitted_rows": matrix_round6_counts.get(source_id, 0),
            }
            for source_id, expected in expected_round6_matrix_counts.items()
            if all_matrix_round6_counts.get(source_id, 0) != expected
            or matrix_round6_counts.get(source_id, 0) != expected
        }
        structured_evidence["matrix_round6_source_ids"] = sorted(matrix_round6_counts)
        structured_evidence["matrix_round6_count_failures"] = matrix_round6_count_failures
        if set(matrix_round6_counts) != required_round6_source_ids or matrix_round6_count_failures:
            errors.append("round-6 evidence matrix source identity, admission fields, or expected facet-link count mismatch")

        all_matrix_round7_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round7_source_ids
        )
        matrix_round7_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round7_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("source_kind") == "paper"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        expected_round7_matrix_counts = expectations.get("required_round7_matrix_counts", {})
        matrix_round7_count_failures = {
            source_id: {
                "expected": expected,
                "all_rows": all_matrix_round7_counts.get(source_id, 0),
                "admitted_rows": matrix_round7_counts.get(source_id, 0),
            }
            for source_id, expected in expected_round7_matrix_counts.items()
            if all_matrix_round7_counts.get(source_id, 0) != expected
            or matrix_round7_counts.get(source_id, 0) != expected
        }
        structured_evidence["matrix_round7_source_ids"] = sorted(matrix_round7_counts)
        structured_evidence["matrix_round7_count_failures"] = matrix_round7_count_failures
        if set(matrix_round7_counts) != required_round7_source_ids or matrix_round7_count_failures:
            errors.append("round-7 evidence matrix source identity, admission fields, or expected facet-link count mismatch")

        round8_metadata_obj = json.loads(
            (ROOT / "paper/sources/arxiv-metadata-literature-round8-receipt.json").read_text(encoding="utf-8")
        )
        round8_metadata_records = round8_metadata_obj.get("records", [])
        required_round8_source_ids = set(expectations.get("required_round8_source_ids", []))
        round8_source_receipts = json.loads(
            (ROOT / "paper/sources/literature-round8-source-receipts.json").read_text(encoding="utf-8")
        )
        round8_failures = []
        if {x.get("source_id") for x in round8_metadata_records} != required_round8_source_ids:
            round8_failures.append("metadata_identity")
        if {x.get("source_id") for x in round8_source_receipts} != required_round8_source_ids:
            round8_failures.append("receipt_identity")
        expected_round8_locator_counts = expectations.get("required_round8_locator_counts", {})
        for receipt in round8_source_receipts:
            source_id = receipt.get("source_id")
            expected_version = expectations.get("required_bibliography_metadata_versions", {}).get(source_id)
            report_path = ROOT / receipt.get("report_path", "")
            fulltext_path = ROOT / receipt.get("fulltext_path", "")
            if (
                receipt.get("reading_level") != "FULL_PAPER_READ"
                or receipt.get("version") != expected_version
                or receipt.get("url") != "https://arxiv.org/abs/%s%s" % (source_id, expected_version)
                or not report_path.is_file()
                or sha256_path(report_path) != receipt.get("report_sha256")
                or not fulltext_path.is_file()
                or sha256_path(fulltext_path) != receipt.get("fulltext_sha256")
                or len(receipt.get("claim_locator_ids", []))
                != expected_round8_locator_counts.get(source_id)
            ):
                round8_failures.append(source_id)
        matrix_round8_counts = collections.Counter(
            row.get("source_id", "").removeprefix("alphaxiv:")
            for row in matrix_rows
            if row.get("source_id", "").removeprefix("alphaxiv:") in required_round8_source_ids
            and row.get("record_type") == "facet_evidence"
            and row.get("screening_status") == "recorded_full_read"
            and row.get("current_evidence_level") == "FULL_PAPER_READ"
        )
        if dict(matrix_round8_counts) != expectations.get("required_round8_matrix_counts", {}):
            round8_failures.append("matrix_counts")
        decision_ledger_obj = json.loads(
            (ROOT / "paper/research/autonomous-research-decision-ledger.json").read_text(encoding="utf-8")
        )
        required_fields = {
            "decision_id", "question", "alternatives", "reviewed_locators",
            "rationale", "decision", "expected_effect_and_risk", "falsifier",
        }
        round8_decisions = decision_ledger_obj.get("round8_decision_records", [])
        known_locator_ids = {x.get("claim_locator_id") for x in locators}
        for record in round8_decisions:
            if not required_fields.issubset(record.keys()):
                round8_failures.append("decision_fields:" + str(record.get("decision_id")))
            if not set(record.get("reviewed_locators", [])) <= known_locator_ids:
                round8_failures.append("decision_locator:" + str(record.get("decision_id")))
        if len(round8_decisions) != expectations.get("round8_decision_record_count", 0):
            round8_failures.append("decision_count")
        structured_evidence["round8_failures"] = round8_failures
        if round8_failures:
            errors.append("round-8 source, matrix, or six-field decision record mismatch")

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

        research_design_text = (ROOT / "paper/research/research-design.md").read_text(encoding="utf-8")
        research_design_sections = re.findall(r"^## (\d+)\. ", research_design_text, re.M)
        comparable_block_match = re.search(
            r"### Comparable experiments by hypothesis\n(.*?)\n## 12\.",
            research_design_text,
            re.S,
        )
        comparable_counts = collections.Counter(
            re.findall(r"^\| (H-[A-E]) \|", comparable_block_match.group(1), re.M)
            if comparable_block_match else []
        )
        required_comparable_counts = expectations.get("research_design_comparable_counts", {})
        research_design_failures = []
        if research_design_sections != [str(i) for i in range(1, 13)]:
            research_design_failures.append("section_order")
        if dict(comparable_counts) != required_comparable_counts:
            research_design_failures.append("comparable_counts")
        if (
            "**Status:** preregistration-ready design" not in research_design_text
            or "Agent-Orchestrated Adaptive RAG `2606.05658` FULL" not in research_design_text
            or "H-E (deferred)" not in research_design_text
            or "R-ROUTING-DEFER" not in research_design_text
        ):
            research_design_failures.append("status_or_round7_decision")

        capability_text = (ROOT / "paper/research/capability-map.md").read_text(encoding="utf-8")
        capability_rows = re.findall(r"^\| ([1-9])\. [^|]+\|", capability_text, re.M)
        area9_rows = [x for x in capability_text.splitlines() if x.startswith("| 9. Routing /")]
        capability_failures = []
        if len(capability_rows) != expectations["capability_map_row_count"]:
            capability_failures.append("row_count")
        if len(area9_rows) != expectations["capability_map_area9_row_count"]:
            capability_failures.append("area9_row_count")
        if not all("FULL" in row and ("design only" in row or "follow-up" in row) for row in area9_rows):
            capability_failures.append("area9_phase_or_evidence")

        differentiation_text = (
            ROOT / "paper/research/coding-harness-differentiation-matrix.md"
        ).read_text(encoding="utf-8")
        differentiation_failures = []
        for token in ("2608.06867", "2607.08665v1", "2608.00685", "2607.09600v2"):
            if token not in differentiation_text:
                differentiation_failures.append(token)

        round7_retrieval_obj = json.loads(
            (ROOT / "paper/research/literature-round7-retrieval-record.json").read_text(encoding="utf-8")
        )
        selected_round7_ids = {
            source_id
            for loop in round7_retrieval_obj.get("loops", [])
            for source_id in loop.get("selected_full_reads", [])
        }
        round7_retrieval_failures = []
        if len(round7_retrieval_obj.get("loops", [])) != expectations["round7_retrieval_loop_count"]:
            round7_retrieval_failures.append("loop_count")
        if round7_retrieval_obj.get("manual_loop_count") > round7_retrieval_obj.get("manual_loop_cap", 0):
            round7_retrieval_failures.append("manual_loop_cap")
        if round7_retrieval_obj.get("full_read_count") != expectations["round7_retrieval_full_read_count"]:
            round7_retrieval_failures.append("full_read_count")
        if selected_round7_ids != required_round7_source_ids:
            round7_retrieval_failures.append("selected_source_identity")
        if "discovery snippets were not used as claims" not in round7_retrieval_obj.get("selection_rule", ""):
            round7_retrieval_failures.append("snippet_boundary")

        structured_evidence["research_design_sections"] = research_design_sections
        structured_evidence["research_design_comparable_counts"] = dict(comparable_counts)
        structured_evidence["research_design_failures"] = research_design_failures
        structured_evidence["capability_map_row_count"] = len(capability_rows)
        structured_evidence["capability_map_area9_row_count"] = len(area9_rows)
        structured_evidence["capability_map_failures"] = capability_failures
        structured_evidence["differentiation_round7_failures"] = differentiation_failures
        structured_evidence["round7_retrieval_failures"] = round7_retrieval_failures
        if (
            research_design_failures
            or capability_failures
            or differentiation_failures
            or round7_retrieval_failures
        ):
            errors.append("round-7 research design, capability map, differentiation, or retrieval record mismatch")

        context_graph_obj = json.loads((ROOT / "paper/context-graph.json").read_text(encoding="utf-8"))
        context_nodes = context_graph_obj.get("nodes", [])
        context_edges = context_graph_obj.get("edges", [])
        context_node_ids = [x.get("id") for x in context_nodes]
        context_edge_ids = [x.get("id") for x in context_edges]
        context_node_id_set = set(context_node_ids)
        context_duplicate_node_ids = sorted(k for k, v in collections.Counter(context_node_ids).items() if v > 1)
        context_duplicate_edge_ids = sorted(k for k, v in collections.Counter(context_edge_ids).items() if v > 1)
        context_endpoint_failures = [
            edge.get("id")
            for edge in context_edges
            if edge.get("source") not in context_node_id_set or edge.get("target") not in context_node_id_set
        ]
        context_kind_counts = collections.Counter(x.get("kind") for x in context_nodes)
        context_relations = {x.get("relation") for x in context_edges}
        required_context_nodes = set(expectations.get("context_graph_required_node_ids", []))
        required_context_relations = set(expectations.get("context_graph_required_relations", []))
        context_missing_nodes = sorted(required_context_nodes - context_node_id_set)
        context_missing_relations = sorted(required_context_relations - context_relations)
        context_unexpected_relations = sorted(context_relations - required_context_relations)
        context_projection_hash_failures = {}
        projection_inputs = context_graph_obj.get("projection_inputs", {})
        expected_projection_paths = expectations.get("context_graph_projection_paths", {})
        expected_projection_keys = set(expected_projection_paths)
        expected_projection_keys.update(key[:-5] + "_sha256" for key in expected_projection_paths)
        context_projection_key_failures = {
            "missing": sorted(expected_projection_keys - set(projection_inputs)),
            "unexpected": sorted(set(projection_inputs) - expected_projection_keys),
            "wrong_paths": {
                key: {"expected": relpath, "actual": projection_inputs.get(key)}
                for key, relpath in expected_projection_paths.items()
                if projection_inputs.get(key) != relpath
            },
        }
        for key, relpath in projection_inputs.items():
            if not key.endswith("_path"):
                continue
            digest_key = key[:-5] + "_sha256"
            if digest_key not in projection_inputs:
                continue
            path = ROOT / relpath
            actual_digest = sha256_path(path) if path.is_file() else None
            if actual_digest != projection_inputs.get(digest_key):
                context_projection_hash_failures[relpath] = {
                    "expected": projection_inputs.get(digest_key),
                    "actual": actual_digest,
                }
        context_text = json.dumps(context_graph_obj, ensure_ascii=False, sort_keys=True)
        context_forbidden_patterns = [pattern for pattern in cfg["forbidden_regexes"] if re.search(pattern, context_text)]
        context_unexpected_results = [
            x.get("id")
            for x in context_nodes
            if x.get("kind") == "evaluation" and x.get("result_status") != "UNEXECUTED"
        ]
        context_nodes_sha256 = canonical_json_sha(sorted(context_nodes, key=lambda x: x.get("id", "")))
        context_edges_sha256 = canonical_json_sha(sorted(context_edges, key=lambda x: x.get("id", "")))
        actual_source_metadata = {
            node.get("source_id"): {
                "version": node.get("version"),
                "bibliography_key": node.get("bibliography_key"),
                "evidence_level": node.get("evidence_level"),
            }
            for node in context_nodes
            if node.get("kind") == "source"
        }
        context_source_metadata_failure = (
            actual_source_metadata != expectations.get("context_graph_source_metadata", {})
        )
        graph_correction_ids_by_source = {
            node.get("source_id"): sorted(node.get("report_correction_ids", []))
            for node in context_nodes
            if node.get("kind") == "source" and node.get("source_id") in correction_source_ids
        }
        context_correction_ownership_failures = {
            source_id: {
                "expected": expected_ids,
                "actual": graph_correction_ids_by_source.get(source_id, []),
            }
            for source_id, expected_ids in expected_correction_ids_by_source.items()
            if graph_correction_ids_by_source.get(source_id, []) != expected_ids
        }
        graph_locator_ids = [
            locator_id
            for node in context_nodes
            if node.get("kind") in {"source", "source_code"}
            for locator_id in node.get("claim_locator_ids", [])
        ]
        context_locator_failures = {
            "missing": sorted(set(locator_ids) - set(graph_locator_ids)),
            "unexpected": sorted(set(graph_locator_ids) - set(locator_ids)),
            "duplicates": sorted(k for k, v in collections.Counter(graph_locator_ids).items() if v > 1),
        }
        expected_trigger_adjacency = expectations.get("context_graph_evaluation_trigger_adjacency", {})
        actual_trigger_adjacency = {
            evaluation_id: sorted(
                edge.get("target")
                for edge in context_edges
                if edge.get("source") == evaluation_id and edge.get("relation") == "on_outcome"
            )
            for evaluation_id in expected_trigger_adjacency
        }
        context_trigger_adjacency_failures = {
            evaluation_id: {
                "expected": expected_targets,
                "actual": actual_trigger_adjacency.get(evaluation_id, []),
            }
            for evaluation_id, expected_targets in expected_trigger_adjacency.items()
            if actual_trigger_adjacency.get(evaluation_id, []) != expected_targets
        }
        structured_evidence["context_graph_node_count"] = len(context_nodes)
        structured_evidence["context_graph_edge_count"] = len(context_edges)
        structured_evidence["context_graph_node_kind_counts"] = dict(context_kind_counts)
        structured_evidence["context_graph_duplicate_node_ids"] = context_duplicate_node_ids
        structured_evidence["context_graph_duplicate_edge_ids"] = context_duplicate_edge_ids
        structured_evidence["context_graph_endpoint_failures"] = context_endpoint_failures
        structured_evidence["context_graph_missing_nodes"] = context_missing_nodes
        structured_evidence["context_graph_missing_relations"] = context_missing_relations
        structured_evidence["context_graph_unexpected_relations"] = context_unexpected_relations
        structured_evidence["context_graph_projection_hash_failures"] = context_projection_hash_failures
        structured_evidence["context_graph_projection_key_failures"] = context_projection_key_failures
        structured_evidence["context_graph_forbidden_patterns"] = context_forbidden_patterns
        structured_evidence["context_graph_unexpected_results"] = context_unexpected_results
        structured_evidence["context_graph_nodes_sha256"] = context_nodes_sha256
        structured_evidence["context_graph_edges_sha256"] = context_edges_sha256
        structured_evidence["context_graph_source_metadata_failure"] = context_source_metadata_failure
        structured_evidence["context_graph_correction_ownership_failures"] = context_correction_ownership_failures
        structured_evidence["context_graph_locator_failures"] = context_locator_failures
        structured_evidence["context_graph_trigger_adjacency_failures"] = context_trigger_adjacency_failures
        if (
            context_graph_obj.get("schema_version") != "argo-paper-context-graph/v1"
            or len(context_nodes) != expectations["context_graph_node_count"]
            or len(context_edges) != expectations["context_graph_edge_count"]
            or dict(context_kind_counts) != expectations["context_graph_node_kind_counts"]
            or context_graph_obj.get("literature_facets") != expectations["context_graph_literature_facets"]
            or context_graph_obj.get("authority", {}).get("literature_role")
            != expectations["context_graph_literature_role"]
            or context_graph_obj.get("authority", {}).get("result_driven_refresh") is not True
            or context_nodes_sha256 != expectations["context_graph_nodes_sha256"]
            or context_edges_sha256 != expectations["context_graph_edges_sha256"]
            or context_source_metadata_failure
            or context_correction_ownership_failures
            or any(context_locator_failures.values())
            or context_trigger_adjacency_failures
            or context_duplicate_node_ids
            or context_duplicate_edge_ids
            or context_endpoint_failures
            or context_missing_nodes
            or context_missing_relations
            or context_unexpected_relations
            or context_projection_hash_failures
            or any(context_projection_key_failures.values())
            or context_forbidden_patterns
            or context_unexpected_results
        ):
            errors.append("context graph identity, topology, authority, projection, or outcome-state mismatch")

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

    external_tex_pattern = (
        r"\\(?:@@input|input|include|includegraphics|lstinputlisting|verbatiminput|"
        r"bibliography|addbibresource|openin|openout|read|newread|newwrite|write18|"
        r"special|pdfximage|XeTeXpicfile|includepdf|IfFileExists|InputIfFileExists|"
        r"csname|catcode|scantokens|char|lccode|uccode|lowercase|uppercase|"
        r"escapechar|endlinechar|everyjob)\b|\\begin\{filecontents\*?\}|\^\^"
    )
    external_tex_inputs = line_hits(clean, external_tex_pattern)
    if external_tex_inputs:
        errors.append("external or dynamically constructed TeX dependency is outside the closed paper scan")

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
    first_citation_order = list(dict.fromkeys(cites))
    bibliography_order_mismatch = bibs != first_citation_order
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
        or bibliography_order_mismatch
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

    top_level_sections = re.findall(r"\\section\{([^}]+)\}", clean)
    required_top_level_sections = cfg.get("structured_expectations", {}).get(
        "required_top_level_sections", []
    )
    section_order_mismatch = top_level_sections != required_top_level_sections

    summary_path = ROOT / "paper/korean-summary.txt"
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else ""
    summary_parts = re.split(r"\n\s*키워드\s*:\s*", summary_text.strip(), maxsplit=1)
    korean_summary_text = summary_parts[0].strip() if summary_parts else ""
    keywords = [x.strip() for x in summary_parts[1].split(",") if x.strip()] if len(summary_parts) == 2 else []
    summary_char_count = len(korean_summary_text)
    summary_limit = cfg.get("structured_expectations", {}).get("korean_summary_max_chars", 500)
    keyword_limit = cfg.get("structured_expectations", {}).get("keywords_max", 5)
    summary_format_failures = []
    if not summary_path.is_file():
        summary_format_failures.append("Korean summary file missing")
    if not korean_summary_text or summary_char_count > summary_limit:
        summary_format_failures.append("Korean summary length invalid")
    if not keywords or len(keywords) > keyword_limit:
        summary_format_failures.append("keyword count invalid")

    official_format_failures = []
    required_static_patterns = {
        "A4 article": r"\\documentclass\[11pt,a4paper\]\{article\}",
        "single column": r"\\documentclass\[11pt,a4paper\]\{article\}",
        "numeric citations": r"\\usepackage\[numbers,sort&compress\]\{natbib\}",
        "double-spaced draft": r"\\linespread\{1\.6\}",
        "Roman chapters": r"\\renewcommand\{\\thesection\}\{\\Roman\{section\}\}",
        "Arabic sections": r"\\renewcommand\{\\thesubsection\}\{\\arabic\{subsection\}\}",
    }
    for label, pattern in required_static_patterns.items():
        if not re.search(pattern, clean):
            official_format_failures.append(label)
    if re.search(r"\btwocolumn\b", clean, re.IGNORECASE):
        official_format_failures.append("two-column mode forbidden")

    if section_order_mismatch:
        errors.append("official thesis top-level section order mismatch")
    if summary_format_failures:
        errors.append("official Korean summary or keyword requirement mismatch")
    if official_format_failures:
        errors.append("official thesis static format requirement mismatch")

    tc_errors, tc_summary = verify_toolchain(cfg)
    errors.extend(tc_errors)
    builds = []
    deterministic = False
    output_pdf_sha = None
    pdf_token_failures = {}
    pdf_text_extraction_errors = {}
    if not tc_errors:
        with tempfile.TemporaryDirectory(prefix="argo-paper-orx-") as td:
            tmp = Path(td)
            shutil.copytree(Path(cfg["toolchain"]["root"]) / "home", tmp / "home")
            (tmp / "xdg-cache").mkdir()
            (tmp / "config").mkdir()
            first = compile_once(cfg, tmp, "build1")
            second = compile_once(cfg, tmp, "build2")
            for build in (first, second):
                if not build["pdf_path"].is_file():
                    continue
                pdf_hits, pdf_error = scan_pdf_text(cfg, build["pdf_path"])
                if pdf_error:
                    pdf_text_extraction_errors[build["name"]] = pdf_error
                elif pdf_hits:
                    pdf_token_failures[build["name"]] = pdf_hits
            if pdf_text_extraction_errors:
                errors.append("generated PDF text extraction failed")
            if pdf_token_failures:
                errors.append("forbidden public-paper token found in generated PDF text")
            builds = [
                {k: v for k, v in b.items() if k not in ("pdf_path", "log_tail", "dependency_paths")}
                for b in (first, second)
            ]
            deterministic = bool(first["pdf_sha256"] and first["pdf_sha256"] == second["pdf_sha256"])
            output_pdf_sha = first["pdf_sha256"]
            expected_paper_sha256 = hashlib.sha256(raw).hexdigest()
            for b in (first, second):
                if b["isolated_input_sha256"] != expected_paper_sha256:
                    errors.append("isolated compiler input differs from validated paper bytes")
                if b["dependency_violations"]:
                    errors.append("compiler dependency escaped the isolated source/toolchain roots: " + ", ".join(b["dependency_violations"][:10]))
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
        "public_output_gate": {
            "scanned_sources": [str(path.relative_to(ROOT)) for path in public_source_paths],
            "source_token_failures": public_source_token_failures,
            "pdf_text_extractor_verified": pdf_text_extractor_verified,
            "pdf_text_extraction_errors": pdf_text_extraction_errors,
            "pdf_token_failures": pdf_token_failures,
        },
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
            "first_citation_order": first_citation_order,
            "bibliography_order_mismatch": bibliography_order_mismatch,
            "top_level_sections": top_level_sections,
            "section_order_mismatch": section_order_mismatch,
            "korean_summary_char_count": summary_char_count,
            "keywords": keywords,
            "summary_format_failures": summary_format_failures,
            "official_format_failures": official_format_failures,
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
