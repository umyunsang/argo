"""Check original bytes and exact scholarly locators, never efficacy."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(root, bundle):
    root, bundle = Path(root), Path(bundle)
    errors = []
    def bound_path(relative):
        path = root / relative
        resolved = path.resolve()
        if resolved != root.resolve() and root.resolve() not in resolved.parents:
            raise ValueError("OUTSIDE_ROOT")
        return path
    def check_file(relative, expected):
        try:
            path = bound_path(relative)
            if not path.is_file() or sha(path) != expected:
                errors.append("FILE:" + relative)
        except (ValueError, OSError, TypeError):
            errors.append("FILE:" + str(relative))
    try:
        receipts = json.loads((bundle / "source-receipts.json").read_text())
        locators = json.loads((bundle / "claim-locators.json").read_text())
        matrix = json.loads((bundle / "benchmark-matrix.json").read_text())
        design = json.loads((bundle / "research-design-amendment.json").read_text())
        paper_ids = [item["paper_id"] for item in receipts["papers"]]
        if len(paper_ids) != len(set(paper_ids)):
            errors.append("DUPLICATE_PAPERS")
        for item in receipts["papers"]:
            for file in item["files"]:
                check_file(file["path"], file["sha256"])
        ids = [item["id"] for item in locators["locators"]]
        if len(ids) != len(set(ids)) or locators.get("unresolved"):
            errors.append("LOCATOR_IDS")
        for item in locators["locators"]:
            if item["paper_id"] not in paper_ids:
                errors.append("LOCATOR_PAPER:" + item["id"])
            check_file(item["text_path"], item["text_sha256"])
            check_file(item["pdf_path"], item["pdf_sha256"])
            text_path = bound_path(item["text_path"])
            if not text_path.is_file():
                continue
            text = text_path.read_text()
            lines = text.split("\n")
            lo, hi = item["line_start"], item["line_end"]
            if type(lo) is not int or type(hi) is not int or not 1 <= lo <= hi <= len(lines):
                errors.append("LOCATOR_RANGE:" + item["id"])
                continue
            if "\n".join(lines[lo-1:hi]) != item["exact_excerpt"]:
                errors.append("LOCATOR_QUOTE:" + item["id"])
            page = "\n".join(lines[:lo-1]).count("\f") + 1
            if item["pdf_page"] not in {page, page + 1}:
                errors.append("LOCATOR_PAGE:" + item["id"])
        for row in matrix["rows"]:
            if row["paper_id"] not in paper_ids or not set(row["claim_ids"]) <= set(ids):
                errors.append("MATRIX_BINDING:" + row["paper_id"])
        if matrix.get("local_reproduction") is not False:
            errors.append("REPRODUCTION_CLAIM")
        if design["execution"].get("authorized") is not False or design["execution"].get("model_calls_authorized") != 0:
            errors.append("EXECUTION_AUTHORITY")
        if design["inference"].get("no_best_of_k_for_primary") is not True:
            errors.append("SELECTION_POLICY")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("SCHEMA_OR_READ:" + type(exc).__name__)
    return {"passed": not errors, "errors": errors, "scope": "file identities, exact excerpts, references and declared authority only"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.root, args.bundle)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
