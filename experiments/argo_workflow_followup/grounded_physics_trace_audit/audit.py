#!/usr/bin/env python3
"""Audit aggregate and decision-level evidence in the grounded-physics archive."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clean_reference(reference: str) -> str:
    return re.sub(r":\d+(?:[–-]\d+)?$", "", reference)


def audit(archive_path: Path, manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    raw = archive_path.read_bytes()
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        files = {info.filename for info in infos if not info.is_dir()}
        unsafe = [
            info.filename
            for info in infos
            if PurePosixPath(info.filename).is_absolute()
            or ".." in PurePosixPath(info.filename).parts
        ]
        crc_error = archive.testzip()
        sums = [
            line for line in archive.read("SHA256SUMS").decode().splitlines()
            if line.strip()
        ]
        sum_failures = []
        covered = set()
        for line in sums:
            digest, name = line.split("  ", 1)
            covered.add(name)
            if name not in files or _sha256(archive.read(name)) != digest:
                sum_failures.append(name)
        uncovered = files - {"SHA256SUMS"} - covered

        readme = archive.read("README.md").decode("utf-8", "replace")
        summary = json.loads(
            archive.read("intervention_ledger/anchor_outcomes_summary.json")
        )
        episode = archive.read("intervention_ledger/episode_recount.md").decode(
            "utf-8", "replace"
        )

    rows = []
    for line in episode.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        references = [
            _clean_reference(reference)
            for reference in re.findall(r"`([^`]+)`", cells[3])
        ]
        direct = [
            reference
            for reference in references
            if (
                reference in files
                or (
                    reference.endswith("/")
                    and any(name.startswith(reference) for name in files)
                )
            )
        ]
        lane = next(
            (
                name
                for name in (
                    "Adversarial review", "Distributed grounding",
                    "Falsification", "Within-session debug",
                )
                if name in cells[1]
            ),
            "unknown",
        )
        rows.append(
            {
                "episode": int(cells[0]),
                "marker": cells[1],
                "lane": lane,
                "source_references": references,
                "direct_sources": direct,
            }
        )

    lane_counts = dict(sorted(Counter(row["lane"] for row in rows).items()))
    direct_rows = sum(bool(row["direct_sources"]) for row in rows)
    normalized_readme = " ".join(readme.split())
    raw_published = not (
        "Raw session transcripts are retained in the project archive (not published"
        in normalized_readme
    )
    anchors = summary["anchors"]["final_outcome_counts"]
    checks = {
        "archive_hash": _sha256(raw) == manifest.get("archive_sha256"),
        "archive_size": len(raw) == manifest.get("archive_bytes"),
        "archive_md5": hashlib.md5(raw).hexdigest() == manifest.get("archive_md5"),
        "zip_integrity": crc_error is None and not unsafe,
        "internal_sha256": len(sums) == 125 and not sum_failures and not uncovered,
        "aggregate_summary": (
            summary["anchors"]["n_tracks"] == 7
            and anchors == {"caveat": 3, "pass": 4}
            and summary["fig3B_episodes"]["total_markers"] == 15
            and summary["literature"]["channels"] == 14
            and summary["literature"]["channel_sum"] == 2162
            and summary["literature"]["sessions_in_scaffolding_csv"] == 47
        ),
        "episode_ledger": len(rows) == 15
        and lane_counts
        == {
            "Adversarial review": 7,
            "Distributed grounding": 1,
            "Falsification": 4,
            "Within-session debug": 3,
        },
        "raw_transcript_disclosure": not raw_published,
    }
    findings = {
        "internal_sha256": f"{len(sums) - len(sum_failures)}/{len(sums)}",
        "unsafe_paths": len(unsafe),
        "anchors": {"tracks": 7, "pass": anchors.get("pass"), "caveat": anchors.get("caveat")},
        "catch_episodes": summary["fig3B_episodes"]["total_markers"],
        "episode_lanes": lane_counts,
        "sessions": summary["literature"]["sessions_in_scaffolding_csv"],
        "literature_events": summary["literature"]["channel_sum"],
        "episode_rows": len(rows),
        "episode_rows_with_direct_source_path": direct_rows,
        "episode_rows_without_direct_source_path": len(rows) - direct_rows,
        "episode_source_closure": rows,
        "raw_transcripts_published": raw_published,
        "raw_decision_graph_admissible": raw_published and direct_rows == len(rows),
        "decision": "ADMIT_AGGREGATE_AND_CORRECTION_TAXONOMY__REJECT_RAW_DECISION_GRAPH",
    }
    errors = [name for name, passed in checks.items() if not passed]
    return {"passed": not errors, "checks": checks, "errors": errors, "findings": findings}
