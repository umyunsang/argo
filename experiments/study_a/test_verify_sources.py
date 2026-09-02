#!/usr/bin/env python3
"""Failing-first fixtures for source verification."""
from __future__ import annotations

import hashlib
import io
import json
import pathlib
import sys
import tarfile
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import verify_sources as vs  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + ((" :: " + detail) if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def write_claims(tmp: pathlib.Path, source_rel: str, text: str, start: int, end: int,
                 file_digest=None, excerpt_digest=None) -> pathlib.Path:
    src = tmp / source_rel
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(text, encoding="utf-8")
    lines = text.splitlines()
    excerpt = "\n".join(lines[start - 1:end])
    claims = tmp / "claims.json"
    claims.write_text(json.dumps({"locators": [{
        "claim_locator_id": "L", "source_id": "S", "source_file": source_rel,
        "source_file_sha256": file_digest or hashlib.sha256(src.read_bytes()).hexdigest(),
        "line_start": start, "line_end": end,
        "excerpt_sha256": excerpt_digest or hashlib.sha256(excerpt.encode()).hexdigest(),
    }]}), encoding="utf-8")
    return claims


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        original_root = vs.ROOT
        vs.ROOT = tmp
        try:
            good = write_claims(tmp, "a/b.tex", "one\ntwo\nthree\n", 2, 2)
            check("a matching locator verifies", vs.verify_claim_locators(good)["ok"] is True)

            bad_file = write_claims(tmp, "a/c.tex", "one\ntwo\n", 1, 1, file_digest="0" * 64)
            r = vs.verify_claim_locators(bad_file)
            check("a changed file digest fails", r["ok"] is False and r["file_failures"])

            bad_exc = write_claims(tmp, "a/d.tex", "one\ntwo\n", 1, 1, excerpt_digest="0" * 64)
            r2 = vs.verify_claim_locators(bad_exc)
            check("an excerpt that no longer hashes fails",
                  r2["ok"] is False and r2["excerpt_failures"])

            shifted = write_claims(tmp, "a/e.tex", "one\ntwo\nthree\n", 2, 2)
            (tmp / "a/e.tex").write_text("inserted\none\ntwo\nthree\n", encoding="utf-8")
            r3 = vs.verify_claim_locators(shifted)
            check("a line shift is caught, not silently re-read", r3["ok"] is False)

            missing = write_claims(tmp, "a/f.tex", "x\n", 1, 1)
            (tmp / "a/f.tex").unlink()
            check("a missing source file fails",
                  vs.verify_claim_locators(missing)["ok"] is False)

            check("an incomplete record is reported, not skipped silently",
                  vs.verify_archive({"source_id": "S"}, fetch=False)["status"] == "INCOMPLETE_RECORD")
            check("offline mode reports offline rather than verified",
                  vs.verify_archive({"source_id": "S", "artifact_url": "u",
                                     "archive_sha256": "d",
                                     "tex_files_repository_paths": ["a/b.tex"]},
                                    fetch=False)["status"] == "OFFLINE")
        finally:
            vs.ROOT = original_root

    print("ALL PASS" if not FAILURES else "FAILURES: " + ", ".join(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
