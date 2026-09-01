#!/usr/bin/env python3
"""Closed-world static and deterministic-build validator for the ARGO thesis."""

import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PROTOCOL_PATH = ROOT / ".orx" / "paper_protocol.json"


def sha256_path(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
    pdf = outdir / "paper.pdf"
    return {
        "name": name,
        "exit_code": proc.returncode,
        "command": cmd,
        "pdf_path": pdf,
        "pdf_sha256": sha256_path(pdf) if pdf.is_file() else None,
        "pdf_bytes": pdf.stat().st_size if pdf.is_file() else None,
        "overfull_boxes": len(re.findall(r"Overfull \\hbox", combined)),
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

    evidence_receipts = {}
    for relpath, expected_sha in cfg.get("evidence_receipts", {}).items():
        p = ROOT / relpath
        actual_sha = sha256_path(p) if p.is_file() else None
        evidence_receipts[relpath] = {
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "verified": actual_sha == expected_sha,
        }
    if not all(x["verified"] for x in evidence_receipts.values()):
        errors.append("evidence receipt or locator identity mismatch")

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

    missing_required = [s for s in cfg["required_substrings"] if s not in text]
    if missing_required:
        errors.append("required disclosure/contract text missing")

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
    if duplicate_bibs or duplicate_labels or missing_bibs or unused_bibs or missing_labels:
        errors.append("citation/reference integrity failure")

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
        "variant": "Revision 4 prospective manuscript baseline",
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
        "evidence_receipts": evidence_receipts,
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
