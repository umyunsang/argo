"""Trusted accounting and evidence records. ORX owns execution state."""
from __future__ import annotations

import json
import math
import sqlite3
import time
from contextlib import closing, contextmanager
from pathlib import Path

from .contracts import ContractError, canonical, digest, utc_now, validate_record


class AdmissionError(RuntimeError):
    pass


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = path
        with closing(self.connect()) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, kind TEXT, project TEXT, sha TEXT, body TEXT);
                CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, started REAL, wall REAL, cpu REAL);
                CREATE TABLE IF NOT EXISTS charges(id TEXT PRIMARY KEY, project TEXT, phase TEXT, state TEXT, reserved INTEGER, actual INTEGER, receipt TEXT);
                CREATE TABLE IF NOT EXISTS leases(id TEXT PRIMARY KEY, project TEXT, state TEXT, cpus REAL, memory INTEGER, reserved REAL, used REAL, receipt TEXT, exclusive INTEGER);
                CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, body TEXT);
                CREATE TABLE IF NOT EXISTS continuation(project TEXT PRIMARY KEY, checkpoint TEXT, old_model TEXT, new_model TEXT, session TEXT);
            """)
        path.chmod(0o600)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def append(self, record: dict):
        validate_record(record)
        with self.transaction() as db:
            old = db.execute("SELECT sha FROM records WHERE id=?", (record["id"],)).fetchone()
            if old:
                if old["sha"] != digest(record):
                    raise AdmissionError("record is immutable; use a new version")
                return
            if record["type"] == "ResearchContract":
                if db.execute("SELECT 1 FROM projects WHERE id=?", (record["project_id"],)).fetchone():
                    raise AdmissionError("project resources cannot be reset")
                r = record["resources"]
                db.execute("INSERT INTO projects VALUES(?,?,?,?)", (record["project_id"], None, r["wall_seconds"], r["cpu_core_seconds"]))
            elif not db.execute("SELECT 1 FROM projects WHERE id=?", (record["project_id"],)).fetchone():
                raise AdmissionError("unknown project")
            if record["type"] == "Assessment" and (record["quality"] == "AAA" or record["pi_acceptance"] != "PENDING" or record["superiority"] != "NOT_ASSESSED"):
                raise AdmissionError("terminal assessment requires validated review import or PI receipt; raw append forbidden")
            db.execute("INSERT INTO records VALUES(?,?,?,?,?)", (record["id"], record["type"], record["project_id"], digest(record), canonical(record)))

    def event(self, value: dict):
        with self.transaction() as db:
            db.execute("INSERT INTO events(at,body) VALUES(?,?)", (utc_now(), canonical(value)))

    def start_project(self, project: str):
        with self.transaction() as db:
            p = db.execute("SELECT * FROM projects WHERE id=?", (project,)).fetchone()
            if not p:
                raise AdmissionError("unknown project")
            if p["started"] is None:
                db.execute("UPDATE projects SET started=? WHERE id=?", (time.time(), project))
            elif time.time() - p["started"] >= p["wall"]:
                raise AdmissionError("project wall ceiling")

    def reserve_charge(self, request_id: str, project: str, phase: str, upper_krw: int, receipt: dict | None = None):
        caps = {"first_week": 150000, "comparison": 90000, "reserve": 60000}
        if phase not in caps or type(upper_krw) is not int or upper_krw < 0:
            raise AdmissionError("explicit integer KRW bound required")
        self.start_project(project)
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM charges WHERE state='UNKNOWN'").fetchone() or db.execute("SELECT 1 FROM leases WHERE state='UNKNOWN'").fetchone():
                raise AdmissionError("unknown additional charge requires reconciliation")
            if not db.execute("SELECT 1 FROM projects WHERE id=?", (project,)).fetchone():
                raise AdmissionError("unknown project")
            total, subtotal = db.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0), COALESCE(SUM(CASE WHEN phase=? THEN COALESCE(actual,reserved) ELSE 0 END),0) FROM charges", (phase,)).fetchone()
            if total + upper_krw > 300000 or subtotal + upper_krw > caps[phase]:
                raise AdmissionError("monetary ceiling")
            db.execute("INSERT INTO charges VALUES(?,?,?,?,?,?,?)", (request_id, project, phase, "RESERVED", upper_krw, None, canonical(receipt) if receipt else None))

    def settle_charge(self, request_id: str, actual_krw: int | None, receipt: dict):
        if not receipt or (actual_krw is not None and (type(actual_krw) is not int or actual_krw < 0)):
            raise AdmissionError("invalid billing receipt")
        with self.transaction() as db:
            row = db.execute("SELECT * FROM charges WHERE id=?", (request_id,)).fetchone()
            if not row or row["state"] not in ("RESERVED", "UNKNOWN"):
                raise AdmissionError("no unsettled request")
            state = "UNKNOWN" if actual_krw is None or actual_krw > row["reserved"] else "SETTLED"
            db.execute("UPDATE charges SET state=?,actual=?,receipt=? WHERE id=?", (state, actual_krw, canonical(receipt), request_id))

    def admit_compute(self, lease_id: str, project: str, seconds: float, cpus: float = 1, memory_mib: int = 2048, *, exclusive: bool = True):
        if any(isinstance(n, bool) or not isinstance(n, (float, int)) or not math.isfinite(n) or n <= 0 for n in (seconds, cpus, memory_mib)):
            raise AdmissionError("finite positive resource reservation required")
        with self.transaction() as db:
            p = db.execute("SELECT * FROM projects WHERE id=?", (project,)).fetchone()
            if not p:
                raise AdmissionError("unknown project")
            if db.execute("SELECT 1 FROM leases WHERE state='UNKNOWN'").fetchone() or db.execute("SELECT 1 FROM charges WHERE state='UNKNOWN'").fetchone():
                raise AdmissionError("unknown compute usage or active process")
            contract = json.loads(db.execute("SELECT body FROM records WHERE project=? AND kind='ResearchContract'", (project,)).fetchone()[0])
            project_active = db.execute("SELECT COALESCE(SUM(cpus),0),COALESCE(SUM(memory),0) FROM leases WHERE project=? AND state='ACTIVE'", (project,)).fetchone()
            if project_active[0] + cpus > contract["resources"]["cpus"] or project_active[1] + memory_mib > contract["resources"]["memory_mib"]:
                raise AdmissionError("project CPU or memory ceiling")
            active = db.execute("SELECT COALESCE(SUM(cpus),0),COALESCE(SUM(memory),0),COUNT(*),COALESCE(MAX(exclusive),0) FROM leases WHERE state='ACTIVE'").fetchone()
            if active[3] or (exclusive and active[2]) or active[0] + cpus > 4 or active[1] + memory_mib > 4608:
                raise AdmissionError("aggregate compute ceiling or exclusive measurement")
            now = time.time()
            start = p["started"] if p["started"] is not None else now
            used = db.execute("SELECT COALESCE(SUM(COALESCE(used,reserved)),0) FROM leases WHERE project=?", (project,)).fetchone()[0]
            if now - start + seconds > p["wall"] or used + seconds * cpus > p["cpu"]:
                raise AdmissionError("project wall or CPU ceiling")
            db.execute("UPDATE projects SET started=? WHERE id=?", (start, project))
            db.execute("INSERT INTO leases VALUES(?,?,?,?,?,?,?,?,?)", (lease_id, project, "ACTIVE", cpus, memory_mib, seconds * cpus, None, None, int(exclusive)))

    def settle_compute(self, lease_id: str, used_seconds: float | None, receipt: dict):
        if not receipt or not receipt.get("terminal") or not receipt.get("container_absent"):
            used_seconds = None
        if used_seconds is not None and (isinstance(used_seconds, bool) or not isinstance(used_seconds, (float, int)) or not math.isfinite(used_seconds) or used_seconds < 0):
            raise AdmissionError("invalid CPU measurement")
        with self.transaction() as db:
            row = db.execute("SELECT * FROM leases WHERE id=?", (lease_id,)).fetchone()
            if not row or row["state"] not in ("ACTIVE", "UNKNOWN"):
                raise AdmissionError("no unsettled compute reservation")
            state = "UNKNOWN" if used_seconds is None or used_seconds > row["reserved"] else "SETTLED"
            db.execute("UPDATE leases SET state=?,used=?,receipt=? WHERE id=?", (state, used_seconds, canonical(receipt), lease_id))

    def resume(self, checkpoint_id: str, model_id: str, session_id: str, allowed_models: list[str]) -> dict:
        with self.transaction() as db:
            row = db.execute("SELECT body FROM records WHERE id=? AND kind='Checkpoint'", (checkpoint_id,)).fetchone()
            if not row:
                raise AdmissionError("checkpoint missing")
            ck = json.loads(row["body"])
            p = db.execute("SELECT * FROM projects WHERE id=?", (ck["project_id"],)).fetchone()
            if p["started"] is not None and time.time() - p["started"] >= p["wall"]:
                raise AdmissionError("project wall ceiling")
            if not ck["first_hypothesis_observed"]:
                raise AdmissionError("continuity trigger not reached; preserve as unreached")
            if model_id not in allowed_models or model_id == ck["model_id"] or session_id == ck["session_id"]:
                raise AdmissionError("continuity requires new session and alternative allowed model")
            db.execute("INSERT INTO continuation VALUES(?,?,?,?,?)", (ck["project_id"], checkpoint_id, ck["model_id"], model_id, session_id))
            # Existing ORX references are returned for reconciliation; never relaunched here.
            return {"checkpoint": ck, "unavailable_model": ck["model_id"], "model_id": model_id, "session_id": session_id, "orx_action": "RECONCILE_EXISTING_RUNS"}

    def snapshot(self) -> dict:
        with closing(self.connect()) as db:
            return {"records": [json.loads(r[0]) for r in db.execute("SELECT body FROM records ORDER BY rowid")],
                    "charges": [dict(r) for r in db.execute("SELECT * FROM charges")],
                    "compute": [dict(r) for r in db.execute("SELECT * FROM leases")],
                    "events": [{"at": r[0], **json.loads(r[1])} for r in db.execute("SELECT at,body FROM events ORDER BY sequence")],
                    "continuations": [dict(r) for r in db.execute("SELECT * FROM continuation")]}
