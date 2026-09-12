
"""Unit tests for evaluator-only execution and custody boundaries."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.project_research.final_evaluation import (
    build_split_receipt,
    disclose,
    locate_candidate_source,
    run_final_evaluation,
    stage_evaluator_root,
)
from experiments.project_research.review import ReviewError, freeze_candidate, build_blind_round, CandidateSpec


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FinalEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp).resolve()

        # Worker wine
        self.worker_wine = self.root / "worker" / "wine"
        self.worker_wine.mkdir(parents=True, mode=0o700)
        self.train_bytes = b"row_id,color,group_id,f1,quality\n1,red,g1,10.0,5\n"
        self.dev_bytes = b"row_id,color,group_id,f1,quality\n2,red,g2,11.0,6\n"
        (self.worker_wine / "train.csv").write_bytes(self.train_bytes)
        (self.worker_wine / "dev.csv").write_bytes(self.dev_bytes)
        worker_manifest = {
            "schema_version": "project-research-worker-wine/v1",
            "files": {
                "train.csv": {"sha256": _sha(self.train_bytes)},
                "dev.csv": {"sha256": _sha(self.dev_bytes)},
            }
        }
        (self.worker_wine / "manifest.json").write_text(json.dumps(worker_manifest))

        # Evaluator wine
        self.evaluator_wine = self.root / "evaluator" / "wine"
        self.evaluator_wine.mkdir(parents=True, mode=0o700)
        self.final_bytes = b"row_id,color,group_id,f1,quality\n3,white,g3,12.0,7\n"
        self.future_bytes = b"row_id,color,group_id,f1,quality\n4,white,g4,13.0,8\n"
        (self.evaluator_wine / "final.csv").write_bytes(self.final_bytes)
        (self.evaluator_wine / "future.csv").write_bytes(self.future_bytes)
        evaluator_manifest = {
            "schema_version": "project-research-evaluator-wine/v1",
            "all_files": {
                "final.csv": {"sha256": _sha(self.final_bytes)},
                "future.csv": {"sha256": _sha(self.future_bytes)},
            }
        }
        (self.evaluator_wine / "manifest.json").write_text(json.dumps(evaluator_manifest))

        # Environment
        self.control_dir = self.root / "control"
        self.control_dir.mkdir(parents=True, mode=0o700)
        (self.control_dir / "environment.json").write_text(json.dumps({
            "image": "sha256:" + "a" * 64
        }))
        (self.control_dir / "model-pool.json").write_text(json.dumps({
            "schema": "research-model-pool/v1",
            "members": [{"id": "model-1", "provider": "test", "status": "QUALIFIED"}]
        }))

        # Store
        self.db_path = self.control_dir / "state.sqlite"
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, started REAL, wall REAL, cpu REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, type TEXT, project TEXT, sha TEXT, body TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY, at TEXT, body TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS leases(id TEXT PRIMARY KEY, project TEXT, state TEXT, cpus REAL, memory INTEGER, reserved REAL, used REAL, receipt TEXT, exclusive INTEGER)")
        conn.execute("INSERT INTO projects VALUES('test-project', 1000.0, 28800.0, 28800.0)")
        conn.commit()
        conn.close()

        # Dummy dispatches & worktrees
        self.dispatches_dir = self.control_dir / "dispatches"
        self.dispatches_dir.mkdir(parents=True, mode=0o700)
        disp1 = self.dispatches_dir / "disp-1"
        disp1.mkdir(parents=True, mode=0o700)
        (disp1 / "launch.json").write_text(json.dumps({"run_id": "run-test-1234"}))
        wt = self.root / "worktree-1"
        wt.mkdir(parents=True, mode=0o700)
        self.candidate_code = b"print('mock candidate running')\n"
        (wt / "candidate.py").write_bytes(self.candidate_code)
        (disp1 / "frozen.json").write_text(json.dumps({"worktree": str(wt)}))

        # Build a valid freeze
        self.freeze_dir = self.build_freeze()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build_freeze(self) -> Path:
        # Create minimal blind round to freeze
        cand1_ws = self.root / "cand1_ws"
        cand2_ws = self.root / "cand2_ws"
        cand1_ws.mkdir()
        cand2_ws.mkdir()
        (cand1_ws / "report.md").write_text("# Report 1\nLine 2\n")
        (cand2_ws / "report.md").write_text("# Report 2\nLine 2\n")

        repro_receipt = {
            "kind": "independent_reproduction",
            "status": "PASS",
            "evidence_scope": "development_research",
            "producer_session_ids": ["sess-1"],
            "reproducer_session_id": "sess-2",
            "execution_id": "run-test-1234",
            "command": ["python", "runner.py"],
            "exit_code": 0,
            "environment_sha256": "3" * 64,
            "input_sha256": [_sha(self.train_bytes), _sha(self.dev_bytes)],
            "output_sha256": ["4" * 64],
            "scope": "mock reproduction",
        }
        (cand1_ws / "reproduction-receipt.json").write_text(json.dumps(repro_receipt))
        (cand2_ws / "reproduction-receipt.json").write_text(json.dumps(repro_receipt))

        round_dir = self.control_dir / "rounds" / "round-1"
        round_info = build_blind_round(
            [
                CandidateSpec("cand-1", "team-1", cand1_ws, ("report.md", "reproduction-receipt.json"), ("auth1",), ("model1",)),
                CandidateSpec("cand-2", "team-2", cand2_ws, ("report.md", "reproduction-receipt.json"), ("auth2",), ("model2",)),
            ],
            round_dir,
            evidence_scope="development_research",
        )
        packet = json.loads((round_dir / "supervisor" / "packet.json").read_text())
        target_cand = packet["candidates"][0]
        cid = target_cand["candidate_id"]
        rep_art = next(a for a in target_cand["artifacts"] if a["file"].endswith(".json"))

        assessment = {
            "candidate_id": cid,
            "round_id": packet["round_id"],
            "supervisor_session_id": round_info["supervisor_session_id"],
            "layer": "research_operations",
            "session_attestation": {"fresh_session": True, "received_only_packet": True, "previous_scores_received": False},
            "dimensions": {
                dim: {"status": "PASS", "rationale": "ok", "evidence": [{"artifact_id": rep_art["artifact_id"], "sha256": rep_art["sha256"], "locator": "L1-L2"}]}
                for dim in ("correctness", "reproducibility", "research_logic", "falsification_and_comparison", "evidence_and_accounting", "claim_scope")
            },
            "findings": [],
            "independent_reproduction_evidence": [{"artifact_id": rep_art["artifact_id"], "sha256": rep_art["sha256"], "locator": "L1-L2"}],
        }
        frozen_dest = self.root / "freezes" / cid
        freeze_candidate(round_dir, assessment, frozen_dest)
        return frozen_dest

    def test_build_split_receipt_validation(self):
        receipt = build_split_receipt(self.evaluator_wine, self.worker_wine, phase="final")
        self.assertEqual(receipt["split_id"], "wine-final")
        self.assertEqual(receipt["split_sha256"], _sha(self.final_bytes))
        self.assertEqual(receipt["purpose"], "final_evaluation")
        self.assertFalse(receipt["worker_access"])

        with self.assertRaises(ReviewError):
            build_split_receipt(self.evaluator_wine, self.worker_wine, phase="invalid_phase")

        # Mismatched hash
        (self.evaluator_wine / "final.csv").write_bytes(b"corrupt")
        with self.assertRaises(ReviewError):
            build_split_receipt(self.evaluator_wine, self.worker_wine, phase="final")

    def test_stage_evaluator_root_custody(self):
        staging_base = self.root / "evaluator" / "staging"
        staged_ws, exec_id, cand_sha, cand_bytes = stage_evaluator_root(
            self.freeze_dir, self.evaluator_wine, self.worker_wine, staging_base, phase="final",
            dispatches_dir=self.dispatches_dir,
        )
        self.assertEqual(exec_id, "run-test-1234")
        self.assertEqual(cand_sha, _sha(self.candidate_code))
        self.assertEqual(cand_bytes, self.candidate_code)

        staged_wine = staged_ws / "wine"
        # dev.csv must be the final.csv bytes!
        self.assertEqual((staged_wine / "dev.csv").read_bytes(), self.final_bytes)
        # future.csv must NOT exist
        self.assertFalse((staged_wine / "future.csv").exists())

    def test_run_final_evaluation_lifecycle_and_refusal(self):
        registry_dir = self.control_dir / "evaluation-registry"

        def mock_runner(snapshot_dir: Path):
            res_dir = self.root / "runs" / "mock-run-1"
            res_dir.mkdir(parents=True, exist_ok=True)
            result_json = {"baseline_model": {"dev_ew_mae": 0.51}, "interaction_model": {"dev_ew_mae": 0.50}}
            return {
                "status": "EXECUTED_UNVALIDATED",
                "exit_code": 0,
                "resources": {"cpu_seconds": 1.5},
                "result": result_json,
                "result_sha256": _sha(json.dumps(result_json).encode()),
            }

        receipt = run_final_evaluation(
            self.freeze_dir,
            registry_dir,
            phase="final",
            root=self.root,
            runner_fn=mock_runner,
            dispatches_dir=self.dispatches_dir,
        )
        self.assertIn("reservation_id", receipt)
        res_id = receipt["reservation_id"]

        # Results receipt written with 0o600
        res_file = self.root / "evaluator" / "results" / f"{res_id}.json"
        self.assertTrue(res_file.is_file())
        self.assertEqual(oct(res_file.stat().st_mode & 0o777), oct(0o600))

        # Repeated run on same reservation must be refused
        with self.assertRaises(ReviewError):
            run_final_evaluation(
                self.freeze_dir,
                registry_dir,
                phase="final",
                root=self.root,
                runner_fn=mock_runner,
                dispatches_dir=self.dispatches_dir,
            )

        # Disclose PI packet
        disc = disclose(res_id, self.root / "evaluator" / "results", self.freeze_dir)
        self.assertEqual(disc["reservation_id"], res_id)
        self.assertEqual(disc["superiority"], "NOT_ASSESSED")
        self.assertEqual(disc["pi_acceptance"], "PENDING")
        self.assertIn("baseline_model", disc["held_out_final_metrics"])


if __name__ == "__main__":
    unittest.main()
