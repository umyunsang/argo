"""The five composable harness components under test.

Each component is a small object with an explicit on/off switch so an ablation arm
differs from B2 by exactly one component. Nothing here calls a model; the model
interface lives in model.py and is injected.
"""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TypedContextGraph:
    """Typed research state. Ablated in B2-G, replaced by FlatNotes."""
    enabled: bool = True
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)

    def add(self, node_id: str, kind: str, **fields):
        if not self.enabled:
            raise RuntimeError("graph disabled")
        if node_id in self.nodes and self.nodes[node_id].get("immutable"):
            raise RuntimeError(f"node {node_id} is immutable and may not be rewritten")
        self.nodes[node_id] = {"kind": kind, **fields}
        return node_id

    def link(self, src, rel, dst):
        if src not in self.nodes or dst not in self.nodes:
            raise RuntimeError("edge endpoint missing")
        self.edges.append({"source": src, "relation": rel, "target": dst})

    def seal(self, node_id: str):
        self.nodes[node_id]["immutable"] = True

    def render(self) -> str:
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, sort_keys=True)


@dataclass
class FlatNotes:
    """Unstructured replacement used by B2-G and B0/B1."""
    enabled: bool = True
    lines: list = field(default_factory=list)

    def add(self, node_id: str, kind: str, **fields):
        self.lines.append(f"{kind}:{node_id} " + " ".join(f"{k}={v}" for k, v in fields.items()))
        return node_id

    def link(self, src, rel, dst):
        self.lines.append(f"{src} -{rel}-> {dst}")

    def seal(self, node_id):  # no immutability in flat notes
        return None

    def render(self) -> str:
        return "\n".join(self.lines)


@dataclass
class DecisionProtocol:
    """Six-field decision records plus claim locking. Ablated in B2-P."""
    enabled: bool = True
    records: list = field(default_factory=list)
    REQUIRED = ("question", "alternatives", "rationale", "decision",
                "expected_effect_and_risk", "falsifier")

    def record(self, **fields):
        if not self.enabled:
            return None
        missing = [f for f in self.REQUIRED if not fields.get(f)]
        if missing:
            raise ValueError(f"decision record missing fields: {missing}")
        self.records.append(fields)
        return len(self.records) - 1

    def lock_claims(self, report: str, receipt: dict, rel_tol: float = 0.05,
                    abs_floor: float = 1e-6):
        """Return claims whose numbers are not backed by the receipt.

        Tolerance is RELATIVE with a small absolute floor. An absolute tolerance is
        fail-open: when the quantity itself is about the size of the tolerance, a
        claim can be off by twenty per cent and still pass.
        """
        if not self.enabled:
            return {"checked": False, "unsupported": []}
        flat = _flatten(receipt)
        unsupported = []
        for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]{1,40})\s*[=:]\s*(-?\d+\.?\d*)", report):
            key, val = m.group(1).strip().lower(), float(m.group(2))
            hit = [v for k, v in flat.items() if k.lower().endswith(key)]
            cands = [float(h) for h in hit if _num(h)]
            if not cands or all(abs(h - val) > max(abs_floor, rel_tol * abs(h)) for h in cands):
                unsupported.append({"claim": m.group(0).strip(), "key": key})
        return {"checked": True, "unsupported": unsupported}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif _num(obj):
        out[prefix] = obj
    return out


@dataclass
class ResultDrivenSearch:
    """Re-queries as a function of the current result state. Ablated in B2-R."""
    enabled: bool = True
    corpus: dict = field(default_factory=dict)
    queries: list = field(default_factory=list)

    def query(self, state_summary: str, k: int = 3):
        if not self.enabled:
            return []
        self.queries.append(state_summary)
        toks = set(re.findall(r"[a-z]{4,}", state_summary.lower()))
        scored = [(len(toks & set(re.findall(r"[a-z]{4,}", v.lower()))), kk)
                  for kk, v in self.corpus.items()]
        return [kk for s, kk in sorted(scored, reverse=True)[:k] if s > 0]


@dataclass
class FalsificationLoop:
    """Preregistered thresholds with a retry/pivot policy. Ablated in B2-L."""
    enabled: bool = True
    max_iterations: int = 3
    thresholds: dict = field(default_factory=dict)
    history: list = field(default_factory=list)

    def preregister(self, **thresholds):
        if not self.enabled:
            return {}
        self.thresholds = dict(thresholds)
        return self.thresholds

    def judge(self, observed: dict):
        """Return (should_continue, reason). One pass only when disabled."""
        if not self.enabled:
            self.history.append({"iteration": 1, "verdict": "single_pass_no_threshold"})
            return False, "loop disabled: single pass"
        it = len(self.history) + 1
        failed = [k for k, thr in self.thresholds.items()
                  if k in observed and _num(observed[k]) and observed[k] < thr]
        verdict = "falsified" if failed else "met"
        self.history.append({"iteration": it, "verdict": verdict, "failed": failed})
        if verdict == "met":
            return False, "thresholds met"
        if it >= self.max_iterations:
            return False, f"budget exhausted after {it} iterations; unresolved: {failed}"
        return True, f"falsified on {failed}; pivoting"
