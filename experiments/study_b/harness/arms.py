"""Arm definitions. Each ablation differs from B2 by exactly one component."""
from __future__ import annotations
from dataclasses import dataclass
from .components import (DecisionProtocol, FalsificationLoop, FlatNotes,
                         ResultDrivenSearch, TypedContextGraph)

ARM_IDS = ("B0", "B1", "B2", "B2-G", "B2-P", "B2-R", "B2-L")


@dataclass
class ArmConfig:
    arm_id: str
    persistent_repl: bool
    typed_graph: bool
    decision_protocol: bool
    result_driven_search: bool
    falsification_loop: bool
    recursive_subcalls: bool

    def build(self, corpus=None):
        return {
            "state": TypedContextGraph() if self.typed_graph else FlatNotes(),
            "protocol": DecisionProtocol(enabled=self.decision_protocol),
            "search": ResultDrivenSearch(enabled=self.result_driven_search, corpus=corpus or {}),
            "loop": FalsificationLoop(enabled=self.falsification_loop),
        }


_FULL = dict(persistent_repl=True, typed_graph=True, decision_protocol=True,
             result_driven_search=True, falsification_loop=True, recursive_subcalls=True)

ARMS = {
    "B0":   ArmConfig("B0", persistent_repl=False, typed_graph=False, decision_protocol=False,
                      result_driven_search=False, falsification_loop=False, recursive_subcalls=False),
    "B1":   ArmConfig("B1", persistent_repl=True, typed_graph=False, decision_protocol=False,
                      result_driven_search=False, falsification_loop=False, recursive_subcalls=True),
    "B2":   ArmConfig("B2", **_FULL),
    "B2-G": ArmConfig("B2-G", **{**_FULL, "typed_graph": False}),
    "B2-P": ArmConfig("B2-P", **{**_FULL, "decision_protocol": False}),
    "B2-R": ArmConfig("B2-R", **{**_FULL, "result_driven_search": False}),
    "B2-L": ArmConfig("B2-L", **{**_FULL, "falsification_loop": False}),
}

ABLATION_OF = {"B2-G": "typed_graph", "B2-P": "decision_protocol",
               "B2-R": "result_driven_search", "B2-L": "falsification_loop"}


def single_component_difference(a: str, b: str) -> list[str]:
    """Fields that differ between two arms."""
    x, y = ARMS[a], ARMS[b]
    return [f for f in ("persistent_repl", "typed_graph", "decision_protocol",
                        "result_driven_search", "falsification_loop", "recursive_subcalls")
            if getattr(x, f) != getattr(y, f)]
