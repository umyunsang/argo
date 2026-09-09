import hashlib
import json
import re
import shutil
import stat
import sys
import unicodedata
import zipfile
from pathlib import Path


root = Path(sys.argv[1]).resolve()
plan = root / ".planning/2026-09-05-thesis-two-column-revision"
manuscript = root / "paper/manuscript"
edition = manuscript / "versions/2026-09-05-thesis-boundary"
source_directory = edition / "source"
source_files = {
    "README.md": plan / "source-README.md",
    "thesis-ko.qmd": manuscript / "thesis-ko.qmd",
    "thesis-template.typ": manuscript / "thesis-template.typ",
    "thesis-publication.csl": manuscript / "thesis-publication.csl",
    "references-template.bib": manuscript / "references-template.bib",
}
for figure_path in sorted((root / "paper/figures/thesis-boundary-20260905").glob("*.svg")):
    source_files[f"figures/thesis-boundary-20260905/{figure_path.name}"] = figure_path
assert len(source_files) == 8
assert not edition.exists(), "Preserve existing editions; do not overwrite a previous package."
boundary = json.loads((plan / "qa/boundary-checks.json").read_text())
assert boundary["status"] == "PASS"
assert hashlib.sha256((manuscript / "thesis-boundary-20260905.pdf").read_bytes()).hexdigest() == boundary["pdf_sha256"]
forbidden = re.compile(r"\b(?:ARGO|NAIS|Prime[ -]Agent|OpenResearch|Exa|pi-mono)\b|/Users/|해커톤|프로토타입|마일스톤|로드맵", re.IGNORECASE)
for relative_path, original_path in source_files.items():
    assert not forbidden.search(unicodedata.normalize("NFKC", original_path.read_text())), relative_path
source_directory.mkdir(parents=True)
for relative_path, original_path in source_files.items():
    destination = source_directory / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original_path, destination)
shutil.copy2(manuscript / "thesis-boundary-20260905.pdf", edition / "thesis-boundary-20260905.pdf")
archive_path = edition / "thesis-boundary-20260905-editable.zip"
with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for relative_path in sorted(source_files):
        archive.writestr(relative_path, (source_directory / relative_path).read_bytes())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == set(source_files)
    for entry in archive.infolist():
        assert not entry.is_dir()
        assert stat.S_IFMT(entry.external_attr >> 16) != stat.S_IFLNK
        payload = archive.read(entry)
        assert payload == source_files[entry.filename].read_bytes()
        assert not forbidden.search(unicodedata.normalize("NFKC", payload.decode("utf-8"))), entry.filename
report = {
    "status": "PASS",
    "scope": "Local editable manuscript package, not publication or research reproduction",
    "edition_path": str(edition.relative_to(root)),
    "archive_path": str(archive_path.relative_to(root)),
    "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    "pdf_sha256": boundary["pdf_sha256"],
    "source_file_count": len(source_files),
    "files": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(source_files.items())},
    "zip_crc_valid": True,
    "no_symlinks": True,
    "zip_member_bytes_match_sources": True,
    "internal_policy_planning_and_review_excluded": True,
    "publication_name_and_path_screen_clear": True,
    "fresh_extraction_render": "PENDING_SEPARATE_CHECK",
}
(plan / "qa/package-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: report[key] for key in ("status", "edition_path", "archive_sha256", "source_file_count")}, ensure_ascii=False))
