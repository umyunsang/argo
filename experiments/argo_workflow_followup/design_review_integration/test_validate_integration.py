"""Bounded negative fixtures for research-design integration."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from validate_integration import sha, validate

HERE = Path(__file__).resolve().parent

class Tests(unittest.TestCase):
    def fixture(self, root):
        def put(path, value):
            (root / path).write_text(json.dumps(value))
        (root / "root.md").write_text("Research direction")
        (root / "design.md").write_text("Prospective design")
        (root / "material.md").write_text("DiscoveryPort; PaperService is downstream")
        (root / "packet.json").write_text("{}")
        reports = []
        for i in range(5):
            name = f"review{i}.json"
            put(name, {"packet_sha256": sha(root/"packet.json"), "findings": [{"id": f"F{i}"}]})
            reports.append({"json_path": name, "json_sha256": sha(root/name)})
        put("intake.json", {"packet_sha256": sha(root/"packet.json"), "reports": reports})
        put("responses.json", {"findings": [{"finding_id": f"F{i}"} for i in range(5)]})
        put("study.json", {"status": "DESIGN_REVISED_PREREGISTRATION_INCOMPLETE", "execution": {"authorized": False, "native_runtime_changes": False, "new_model_calls": 0}, "primary": {"outcome": "single selected artifact", "no_archive_or_best_seed": True}})
        put("completion.json", {"research_status": "NOT_COMPLETE", "writing_allowed": False, "publication_allowed": False, "prototype_build_authorized": False})
        put("next.json", {"research_review_integration": {"path": "study.json", "sha256": sha(root/"study.json")}})
        put("handoff.json", {"entrypoint": {"path": "root.md", "sha256": sha(root/"root.md")}, "active_documents": [{"path": "design.md", "sha256": sha(root/"design.md")}], "acyclic_binding": {"next_sha256": sha(root/"next.json")}, "active_chain": {"current_node_ids": ["root", "design"], "current_edge_ids": ["e"]}})
        put("graph.json", {"nodes": [{"id": "root", "evidence": "root.md", "sha256": sha(root/"root.md")}, {"id": "design", "evidence": "design.md", "sha256": sha(root/"design.md")}], "edges": [{"id": "e", "source": "root", "target": "design"}]})
        bindings = {k: {"path": path, "sha256": sha(root/path)} for k, path in {"root":"root.md", "design":"design.md", "material":"material.md", "packet":"packet.json", "intake":"intake.json", "responses":"responses.json", "study":"study.json", "completion":"completion.json"}.items()}
        put("contract.json", {"bindings": bindings, "navigation": {"next":"next.json", "handoff":"handoff.json", "graph":"graph.json"}, "required_nodes":["root","design"]})
        return root / "contract.json"
    def run_case(self, mutation=None):
        with tempfile.TemporaryDirectory(dir=HERE) as td:
            root = Path(td)
            contract = self.fixture(root)
            if mutation: mutation(root)
            return validate(root, contract)
    def mutate(self, root, path, fn, rebind=False):
        p = root/path
        value = json.loads(p.read_text())
        fn(value)
        p.write_text(json.dumps(value))
        if rebind:
            c = root/"contract.json"
            obj = json.loads(c.read_text())
            for binding in obj["bindings"].values():
                if binding["path"] == path: binding["sha256"] = sha(p)
            c.write_text(json.dumps(obj))
    def test_good(self): self.assertTrue(self.run_case()["passed"])
    def test_source_drift(self): self.assertFalse(self.run_case(lambda r: (r/"root.md").write_text("drift"))["passed"])
    def test_missing_role(self): self.assertFalse(self.run_case(lambda r: self.mutate(r,"intake.json",lambda x:x["reports"].pop(),True))["passed"])
    def test_unanswered_finding(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"responses.json",lambda x:x["findings"].pop(),True))["passed"])
    def test_review_packet_drift(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"review1.json",lambda x:x.update(packet_sha256="bad")))["passed"])
    def test_stale_active_node(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"graph.json",lambda x:x["nodes"][1].update(sha256="bad")))["passed"])
    def test_dangling_edge(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"graph.json",lambda x:x["edges"][0].update(target="missing")))["passed"])
    def test_writing_early(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"completion.json",lambda x:x.update(writing_allowed=True),True))["passed"])
    def test_execute_early(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"study.json",lambda x:x["execution"].update(authorized=True),True))["passed"])
    def test_stale_next(self): self.assertFalse(self.run_case(lambda r:self.mutate(r,"next.json",lambda x:x.update(extra=True)))["passed"])
    def test_absent_file(self): self.assertFalse(self.run_case(lambda r:(r/"material.md").unlink())["passed"])

if __name__ == "__main__": unittest.main(verbosity=2)
