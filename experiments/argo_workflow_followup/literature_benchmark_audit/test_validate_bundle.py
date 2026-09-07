"""Hand-authored negative controls for literature provenance checks."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from validate_bundle import sha, validate

HERE = Path(__file__).resolve().parent

class Tests(unittest.TestCase):
    def fixture(self, root):
        bundle = root / "bundle"
        bundle.mkdir()
        source = root / "source.txt"
        source.write_text("alpha\nbeta\n", encoding="utf-8")
        pdf = root / "source.pdf"
        pdf.write_bytes(b"%PDF-fixture")
        def put(name, obj):
            (bundle / name).write_text(json.dumps(obj), encoding="utf-8")
        put("source-receipts.json", {"papers": [{"paper_id": "p", "version": "v1", "files": [{"path": "source.txt", "sha256": sha(source)}]}]})
        put("claim-locators.json", {"locators": [{"id": "L", "paper_id": "p", "text_path": "source.txt", "text_sha256": sha(source), "pdf_path": "source.pdf", "pdf_sha256": sha(pdf), "line_start": 1, "line_end": 1, "exact_excerpt": "alpha", "pdf_page": 1}], "unresolved": []})
        put("benchmark-matrix.json", {"rows": [{"paper_id": "p", "claim_ids": ["L"]}], "local_reproduction": False})
        put("research-design-amendment.json", {"execution": {"authorized": False, "model_calls_authorized": 0}, "inference": {"no_best_of_k_for_primary": True}})
        return bundle
    def run_case(self, mutate=None):
        with tempfile.TemporaryDirectory(dir=HERE) as name:
            root = Path(name)
            bundle = self.fixture(root)
            if mutate:
                mutate(root, bundle)
            return validate(root, bundle)
    def test_valid(self):
        self.assertTrue(self.run_case()["passed"])
    def test_source_drift(self):
        result = self.run_case(lambda root, bundle: (root / "source.txt").write_text("changed"))
        self.assertFalse(result["passed"])
    def test_false_quote(self):
        def mutate(root, bundle):
            path = bundle / "claim-locators.json"
            value = json.loads(path.read_text())
            value["locators"][0]["exact_excerpt"] = "invented"
            path.write_text(json.dumps(value))
        self.assertFalse(self.run_case(mutate)["passed"])
    def test_missing_locator(self):
        def mutate(root, bundle):
            path = bundle / "benchmark-matrix.json"
            value = json.loads(path.read_text())
            value["rows"][0]["claim_ids"] = ["missing"]
            path.write_text(json.dumps(value))
        self.assertFalse(self.run_case(mutate)["passed"])
    def test_absent_file_fails(self):
        self.assertFalse(self.run_case(lambda root, bundle: (root / "source.txt").unlink())["passed"])
    def test_authority_escalation_fails(self):
        def mutate(root, bundle):
            path = bundle / "research-design-amendment.json"
            value = json.loads(path.read_text())
            value["execution"]["authorized"] = True
            path.write_text(json.dumps(value))
        self.assertFalse(self.run_case(mutate)["passed"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
