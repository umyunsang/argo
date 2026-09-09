"""Synthetic preparation fixtures; no real custody data, model, ORX or Docker run."""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

import kernel_wrapper
import prepare_episode as prep


PARENT = "11111111-1111-4111-8111-111111111111"


class EpisodePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.study = self.root / "study"
        self.code = self.root / "flat-code"
        self.corpus = self.root / "retained-corpus"
        self.custody = self.study / "custody/task_37"
        self.auth = self.root / "profile/auth.json"
        for directory in (self.custody, self.code / "prompts", self.corpus, self.auth.parent, self.study / "orx-project"):
            directory.mkdir(parents=True, mode=0o700)
        self.auth.write_text("NEVER_READ_OR_COPY_AUTH_MARKER")
        self.train = b"x,kind,class\n1,alpha,0\n,beta,1\n"
        (self.custody / "inner_train.csv").write_bytes(self.train)
        for name in ("dev_y.csv", "test_y.csv", "test_X.csv", "dev_X.csv", "outer_train.csv", "row_identity.json"):
            (self.custody / name).write_text("FORBIDDEN_PRIVATE_VALUE_" + name)
        (self.custody / "source").mkdir()
        (self.custody / "source/dataset.arff").write_text("ORIGINAL_SOURCE_PRIVATE_VALUE")
        self.metadata = {
            "schema": "argo-study-data-custody/v1", "task_id": 37, "data_id": 37, "data_version": 1,
            "allocation": "development", "target_column": "class", "feature_columns": ["x", "kind"],
            "numeric_columns": ["x"], "categorical_columns": ["kind"], "class_mapping": ["negative", "positive"],
            "classes": [0, 1], "row_counts": {"inner_train": 2, "dev": 10, "test": 10},
            "files_sha256": {"inner_train.csv": prep.digest(self.train)}, "source_notes": ["PRIVATE_METADATA_MARKER"],
        }
        self.summary = self.root / "custody-summary.json"
        self.update_metadata()
        for name in prep.CODE_FILES:
            (self.code / name).write_text("synthetic code identity " + name + "\n")
        prompt_hashes = {}
        for name in ("common.md", "B0.md", "R0.md"):
            data = ("synthetic prompt " + name + "\n").encode()
            (self.code / "prompts" / name).write_bytes(data)
            prompt_hashes[name] = prep.digest(data)
        (self.code / "prompts/manifest.json").write_text(json.dumps({"files": prompt_hashes}))
        anchors = []
        for number, name in enumerate(("Prime", "HoH", "Scroll", "HarnessDev", "RecEvolve")):
            filename = f"source-{number}.txt"
            text = f"METHOD {name} A\nMETHOD {name} B\nEVALUATION_VALUES_MUST_NOT_BE_COPIED\n"
            (self.corpus / filename).write_text(text)
            anchors.append(prep.Anchor(name, filename, prep.digest(text.encode()), 1, 2))
        self.locations = prep.Locations(self.study, self.summary, self.corpus, self.auth, tuple(anchors))

    def tearDown(self):
        self.temporary.cleanup()

    def update_metadata(self):
        data = prep.json_bytes(self.metadata)
        (self.custody / "metadata.json").write_bytes(data)
        self.summary.write_bytes(prep.json_bytes({"tasks": [{"task_id": 37, "status": "PREPARED",
            "custody_path": str(self.custody), "metadata_sha256": prep.digest(data)}]}))

    def prepare(self, **changes):
        arguments = {"episode_id": "synthetic-b0", "arm": "B", "candidate_id": "B0", "task_id": 37,
                     "parent_experiment_id": PARENT, "code_root": self.code, "locations": self.locations, "now": 2_000_000_000}
        arguments.update(changes)
        return prep.prepare_episode(**arguments)

    def test_only_public_training_schema_and_task_enter_worker(self):
        original_open = os.open
        read_paths = []

        def observed_open(path, flags, *args, **kwargs):
            path = Path(path)
            if flags & (os.O_WRONLY | os.O_RDWR) == 0:
                read_paths.append(path)
                self.assertNotEqual(path, self.auth)
                if path.is_relative_to(self.custody):
                    self.assertIn(path.name, {"metadata.json", "inner_train.csv"})
            return original_open(path, flags, *args, **kwargs)

        with mock.patch.object(prep.os, "open", side_effect=observed_open):
            result = self.prepare()
        config_path = Path(result["config_path"])
        config = json.loads(config_path.read_text())
        workspace = Path(config["workspace"])
        self.assertEqual(sorted(path.name for path in workspace.iterdir()), ["TASK.md", "inner_train.csv", "public.json"])
        self.assertEqual((workspace / "inner_train.csv").read_bytes(), self.train)
        public = json.loads((workspace / "public.json").read_text())
        self.assertEqual(set(public), set(prep.PUBLIC_KEYS))
        self.assertNotIn("row_counts", public)
        self.assertNotIn("source_notes", public)
        self.assertFalse((workspace / "solution.py").exists())
        self.assertIn("host calls initialize", (workspace / "TASK.md").read_text())
        self.assertIn("def fit(train_X, train_y, frozen_config)", (workspace / "TASK.md").read_text())
        self.assertEqual(list((workspace.parent / "artifacts").iterdir()), [])
        for path in workspace.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)
        for name in ("workspace", "artifacts", "control"):
            self.assertEqual(stat.S_IMODE((workspace.parent / name).stat().st_mode), 0o700)
        self.assertNotIn(self.auth, read_paths)
        all_created_text = "\n".join(path.read_text() for path in workspace.parent.rglob("*") if path.is_file())
        self.assertNotIn("FORBIDDEN_PRIVATE_VALUE", all_created_text)
        self.assertNotIn("NEVER_READ_OR_COPY_AUTH_MARKER", all_created_text)
        self.assertNotIn("PRIVATE_METADATA_MARKER", all_created_text)
        self.assertNotIn("ORIGINAL_SOURCE_PRIVATE_VALUE", all_created_text)
        self.assertNotIn("EVALUATION_VALUES_MUST_NOT_BE_COPIED", all_created_text)

    def test_combined_configuration_matches_current_controller_bridge_and_kernel(self):
        result = self.prepare()
        cfg = json.loads(Path(result["config_path"]).read_text())
        kernel_path = Path(cfg["kernel_config"])
        with mock.patch.object(kernel_wrapper, "STUDY_ROOT", self.study):
            kernel = kernel_wrapper.load_config(kernel_path)
        self.assertEqual(kernel.deadline_epoch, 2_000_005_400)
        self.assertEqual(kernel.episode_cpus, 2)
        self.assertEqual(kernel.episode_memory_bytes, 8 * 1024**3)
        self.assertEqual(kernel.max_cpu_seconds, 7200)
        self.assertEqual(kernel.image, prep.IMAGE)
        self.assertTrue(Path(cfg["private_artifact_dir"]).is_relative_to(kernel.control_dir))
        self.assertEqual(Path(cfg["metadata"]), self.custody / "metadata.json")
        self.assertEqual(cfg["token_limit"], 80000)
        self.assertEqual(cfg["family_limit"], 1500000)
        self.assertEqual(cfg["family_usd_limit"], 45)
        self.assertEqual(cfg["fixed_command"], prep.FIXED_COMMAND)
        self.assertEqual(cfg["projectId"], prep.PROJECT_ID)
        self.assertEqual(cfg["parent_experiment_id"], PARENT)
        tree = ast.parse((Path(__file__).parent / "scientific_bridge.py").read_text())
        bridge_fields = next({field.target.id for field in node.body if isinstance(field, ast.AnnAssign)}
                             for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "EpisodeConfig")
        self.assertTrue(bridge_fields.issubset(cfg))
        receipt = json.loads(Path(result["receipt_path"]).read_text())
        self.assertEqual(receipt["config_sha256"], prep.digest(Path(result["config_path"]).read_bytes()))
        self.assertEqual(receipt["code_sha256"]["controller.ts"], prep.digest((self.code / "controller.ts").read_bytes()))

    def test_policy_and_ledger_are_selected_by_arm_with_identical_corpus(self):
        b = json.loads(Path(self.prepare()["config_path"]).read_text())
        r = json.loads(Path(self.prepare(episode_id="synthetic-r0", arm="R", candidate_id="R0")["config_path"]).read_text())
        self.assertEqual(Path(b["family_ledger"]).name, "B.json")
        self.assertEqual(Path(r["family_ledger"]).name, "R.json")
        self.assertEqual(Path(r["policy_prompt"]).read_text(), "synthetic prompt R0.md\n")
        self.assertEqual(Path(b["common_prompt"]).read_bytes(), Path(r["common_prompt"]).read_bytes())
        self.assertEqual(set(b["corpus"]), set(r["corpus"]))
        for key in b["corpus"]:
            self.assertEqual(Path(b["corpus"][key]).read_bytes(), Path(r["corpus"][key]).read_bytes())
            self.assertTrue(Path(b["corpus"][key]).is_relative_to(Path(b["kernel_config"]).parent))

    def test_no_overwrite_preserves_existing_episode_and_user_files(self):
        result = self.prepare()
        episode = Path(result["config_path"]).parent.parent
        (episode / "workspace/user-note.txt").write_text("preserve")
        before = {str(path.relative_to(episode)): prep.digest(path.read_bytes()) for path in episode.rglob("*") if path.is_file()}
        with self.assertRaisesRegex(prep.PreparationError, "EPISODE_EXISTS_REFUSE_OVERWRITE"):
            self.prepare()
        after = {str(path.relative_to(episode)): prep.digest(path.read_bytes()) for path in episode.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_metadata_and_training_hash_mismatches_reject_before_output(self):
        (self.custody / "metadata.json").write_text("{}")
        with self.assertRaisesRegex(prep.PreparationError, "METADATA_HASH_MISMATCH"):
            self.prepare()
        self.update_metadata()
        (self.custody / "inner_train.csv").write_bytes(self.train + b"9,gamma,0\n")
        with self.assertRaisesRegex(prep.PreparationError, "TRAIN_HASH_MISMATCH"):
            self.prepare()
        self.assertFalse((self.study / "episodes").exists())

    def test_train_header_rejects_unapproved_row_identifier_column(self):
        data = b"row_id,x,kind,class\n1,2,alpha,0\n2,3,beta,1\n"
        (self.custody / "inner_train.csv").write_bytes(data)
        self.metadata["files_sha256"]["inner_train.csv"] = prep.digest(data)
        self.update_metadata()
        with self.assertRaisesRegex(prep.PreparationError, "TRAIN_HEADER_MISMATCH"):
            self.prepare()
        self.assertFalse((self.study / "episodes").exists())

    def test_method_source_and_prompt_hashes_are_checked(self):
        source = self.corpus / self.locations.anchors[0].filename
        original = source.read_bytes()
        source.write_bytes(b"changed source")
        with self.assertRaisesRegex(prep.PreparationError, "CORPUS_SOURCE_HASH_MISMATCH"):
            self.prepare()
        source.write_bytes(original)
        (self.code / "prompts/B0.md").write_text("changed policy")
        with self.assertRaisesRegex(prep.PreparationError, "PROMPT_HASH_MISMATCH"):
            self.prepare()
        self.assertFalse((self.study / "episodes").exists())

    def test_identity_and_path_boundary_rejections(self):
        for changes, code in [({"episode_id": "../escape"}, "INVALID_EPISODE_ID"),
                              ({"task_id": 3}, "DEVELOPMENT_TASK_REQUIRED"),
                              ({"arm": "R", "candidate_id": "B0"}, "ARM_CANDIDATE_MISMATCH"),
                              ({"parent_experiment_id": "not-a-uuid"}, "INVALID_PARENT_EXPERIMENT_ID")]:
            with self.subTest(changes=changes), self.assertRaisesRegex(prep.PreparationError, code):
                self.prepare(**changes)
        link = self.root / "code-link"
        link.symlink_to(self.code, target_is_directory=True)
        with self.assertRaisesRegex(prep.PreparationError, "NONCANONICAL_OR_SYMLINK_PATH"):
            self.prepare(code_root=link)
        self.assertFalse((self.study / "episodes").exists())

    def test_cli_emits_only_paths_and_hashes_for_synthetic_inputs(self):
        output = io.StringIO()
        arguments = ["prepare", "--episode-id", "cli-fixture", "--arm", "B", "--candidate-id", "B0",
                     "--task-id", "37", "--parent-experiment-id", PARENT, "--code-root", str(self.code)]
        with mock.patch.object(prep, "default_locations", return_value=self.locations), contextlib.redirect_stdout(output):
            code = prep.main(arguments)
        self.assertEqual(code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["status"], "PREPARED_NOT_LAUNCHED")
        self.assertEqual(len(result["config_sha256"]), 64)
        self.assertNotIn("alpha", output.getvalue())
        self.assertNotIn("NEVER_READ_OR_COPY_AUTH_MARKER", output.getvalue())


if __name__ == "__main__":
    unittest.main()
