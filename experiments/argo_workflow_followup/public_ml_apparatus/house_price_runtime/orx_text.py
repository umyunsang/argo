"""Fail-closed parsers for captured ORX 0.1.120 CLI surfaces. No execution."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
HASH = r"[0-9a-f]{40}"
STATES = {"starting":"QUEUED", "running":"RUNNING", "done":"DONE",
          "failed":"FAILED", "cancelled":"CANCELLED"}
MAX_TEXT_BYTES = 65536


class ParseError(ValueError):
    def __init__(self):
        super().__init__("ORX_OUTPUT_UNRECOGNIZED")


@dataclass(frozen=True)
class CreatedExperiment:
    experiment_id: str
    branch: str
    slug: str


@dataclass(frozen=True)
class LocalLaunch:
    run_id: str
    run_directory: str


@dataclass(frozen=True)
class ExperimentStatus:
    experiment_id: str
    branch: str
    run_id: str | None
    status: str | None
    commit_sha: str | None


@dataclass(frozen=True)
class RunRow:
    run_id: str
    status: str
    commit_prefix: str


@dataclass(frozen=True)
class LogWindow:
    start: int
    end: int
    total: int
    data: bytes
    transport_lf_removed: bool


def _text(value: str) -> str:
    if not isinstance(value, str):
        raise ParseError()
    try:
        if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
            raise ParseError()
    except UnicodeError:
        raise ParseError() from None
    if any(ord(char) < 32 and char != "\n" for char in value):
        raise ParseError()
    return value


def _uuid(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(UUID, value) is None:
        raise ParseError()
    return value


def _same(value: str, expected: str) -> None:
    if value != expected:
        raise ParseError()


def parse_created_experiment(text: str, title: str, command: str) -> CreatedExperiment:
    lines = _text(text).split("\n")
    if len(lines) != 13 or lines[0] not in {"✓ Created local baseline experiment", "✓ Created local child experiment"}:
        raise ParseError()
    fields = {}
    for line in lines[1:6]:
        match = re.fullmatch(r"  (id|title|slug|branch|command): +(.+)", line)
        if match is None or match[1] in fields:
            raise ParseError()
        fields[match[1]] = match[2]
    if set(fields) != {"id", "title", "slug", "branch", "command"}:
        raise ParseError()
    _same(fields["title"], title)
    _same(fields["command"], command)
    slug = fields["slug"]
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) is None:
        raise ParseError()
    _same(fields["branch"], "orx/"+slug)
    if (lines[6] != "" or lines[7] != "To edit it, check out the branch in the project's local clone:" or
            not lines[8].startswith("  cd /") or lines[9] != "  git checkout "+fields["branch"] or
            lines[10] != "  # …edit, then…" or lines[11] != '  git commit -am "<msg>"' or lines[12:] != [""]):
        raise ParseError()
    return CreatedExperiment(_uuid(fields["id"]), fields["branch"], slug)


def parse_local_launch(text: str, experiment_id: str) -> LocalLaunch:
    _uuid(experiment_id)
    match = re.fullmatch(r"✓ Local run started\.\n  dir  (/[^\n]+)\n  run  ("+UUID+r")\n"
                        r"  Follow it with `orx exp wait ("+UUID+r")` or `orx logs ("+UUID+r")`\.\n", _text(text))
    if match is None or match[2] != match[4] or match[3] != experiment_id:
        raise ParseError()
    path = PurePosixPath(match[1])
    if path.name != match[2] or path.parent.name != "local-runs" or ".." in path.parts:
        raise ParseError()
    return LocalLaunch(match[2], match[1])


def parse_experiment_status(text: str, experiment_id: str, title: str, command: str) -> ExperimentStatus:
    _uuid(experiment_id)
    lines = _text(text).split("\n")
    if len(lines) < 7 or lines[-1] != "" or re.fullmatch(re.escape(title)+r"  \((?:idle|running)\)  \[local\]", lines[0]) is None:
        raise ParseError()
    fields = {}
    for line in lines[1:-1]:
        match = re.fullmatch(r"  (id|branch|parent|command|last run|reason|commit): +(.+)", line)
        if match is None or match[1] in fields:
            raise ParseError()
        fields[match[1]] = match[2]
    required = {"id","branch","parent","command","last run"}
    if not required <= set(fields):
        raise ParseError()
    _same(fields["id"], experiment_id)
    _same(fields["command"], command)
    if re.fullmatch(r"orx/[a-z0-9]+(?:-[a-z0-9]+)*", fields["branch"]) is None:
        raise ParseError()
    if fields["parent"] != "— (root experiment)" and re.fullmatch(UUID+r" \(branch orx/[a-z0-9-]+\)", fields["parent"]) is None:
        raise ParseError()
    last = fields["last run"]
    if last == "— (never run)":
        if set(fields) != required:
            raise ParseError()
        return ExperimentStatus(experiment_id,fields["branch"],None,None,None)
    match = re.fullmatch(r"("+UUID+r") \((starting|running|done|failed|cancelled), commit ([0-9a-f]{7}), ran [0-9A-Za-z .]+, updated [0-9A-Za-z .]+\)", last)
    if match is None or "commit" not in fields or re.fullmatch(HASH, fields["commit"]) is None:
        raise ParseError()
    if not fields["commit"].startswith(match[3]) or ("reason" in fields and match[2] != "failed"):
        raise ParseError()
    return ExperimentStatus(experiment_id,fields["branch"],match[1],STATES[match[2]],fields["commit"])


def parse_run_rows(text: str, title: str) -> tuple[RunRow, ...]:
    checked = _text(text)
    if checked == "No runs found.\n":
        return ()
    lines = checked.split("\n")
    if len(lines) < 3 or re.split(r" {2,}",lines[0]) != ["ID","STATUS","EXPERIMENT","COMMIT","DURATION","UPDATED"]:
        raise ParseError()
    if re.fullmatch(r"─+(?:  ─+){5}",lines[1]) is None:
        raise ParseError()
    rows = [];seen = set();reasons = set()
    for line in lines[2:]:
        if not line:
            continue
        reason = re.fullmatch(r"("+UUID+r")  reason: .+",line)
        if reason:
            if reason[1] not in seen or reason[1] in reasons or not any(row.run_id==reason[1] and row.status=="FAILED" for row in rows):
                raise ParseError()
            reasons.add(reason[1]);continue
        parts = re.split(r" {2,}",line)
        if len(parts)!=6:
            raise ParseError()
        run_id,state,row_title,commit,duration,updated=parts
        _uuid(run_id);_same(row_title,title)
        if (run_id in seen or state not in STATES or re.fullmatch(r"[0-9a-f]{7}",commit) is None or
                re.fullmatch(r"[0-9A-Za-z .]+",duration) is None or re.fullmatch(r"[0-9A-Za-z .]+",updated) is None or len(rows)>=5):
            raise ParseError()
        seen.add(run_id);rows.append(RunRow(run_id,STATES[state],commit))
    return tuple(rows)


def parse_log_window(data: bytes, metadata: str) -> LogWindow:
    if not isinstance(data, bytes) or len(data)>1_048_577:
        raise ParseError()
    match = re.fullmatch(r"\[local file\] bytes ([0-9]{1,12})–([0-9]{1,12}) of ([0-9]{1,12})(?: \((?:more below|more above)\))?\n",_text(metadata))
    if match is None:
        raise ParseError()
    start,end,total=map(int,match.groups())
    if not 0 <= start <= end <= total or end-start>1_048_576:
        raise ParseError()
    removed=False
    if len(data)==end-start+1 and data.endswith(b"\n"):
        data=data[:-1];removed=True
    if len(data)!=end-start:
        raise ParseError()
    return LogWindow(start,end,total,data,removed)


def parse_cancel_ack(text: str, run_id: str) -> str:
    _uuid(run_id)
    _same(_text(text),"✓ Cancel requested for run "+run_id+".\n")
    return run_id
