"""Design-source absorption ledger for the ARGO-ORX harnessed LLM agent.

This module records, for every system whose design this harness absorbs from:

1. which design element is taken from that system (``absorbed_element``),
2. the design requirement that element imposes on this harness
   (``design_requirement``),
3. the harness core or runtime tool where the requirement is implemented
   (``implementation_site``), and
4. whether that implementation has received an executed empirical test
   (``test_status``: TESTED, IMPLEMENTED_UNTESTED or DECLARED_ONLY).

It is a provenance ledger for design decisions, not a scoring harness and not a
decision harness over candidate artifacts: it renders no judgement, of any
source system or of any candidate result. The acceptance rules recorded here are
the rules the source systems themselves publish, and a residual defect is
recorded only as the derivation source of a requirement this harness has to
satisfy.

Counting convention. No system count is written into this file.
``ABSORPTION_ENTRIES`` is the single canonical list, and ``LEDGER.counts()``
derives from it the absorption-table size, the frontier-system size, the
representative-view size and the number of distinct published acceptance
families. An entry belongs to the representative view unless it is an
application-level instance of a family another entry already represents: The AI
Scientist and MLAgentBench are instances of the published ``ACCEPTED`` family
carried by SoL-Pi, OpenAI Agents API and Prime Agent, and are therefore recorded
in the absorption table only. ``LEDGER.validate()`` enforces these invariants at
import time.

The S1 anchors in the mapping section are frozen case inputs to a deductive
specification mapping. They are not measurements taken on any source system, and
no source system was executed locally to produce them.

Instrument section, retained as the verifier basis for Study B. It evaluates
concrete scientific R&D tasks with deterministic execution oracles:
- Task 1: Regularization vs Generalization Frontier (ML Hyperparameter Optimization)
- Task 2: Interaction Representation Contrast (Feature Engineering & Hypothesis Testing)
- Task 3: Pruning vs Quantization Pareto Analysis (Model Compression & Latency Tradeoff)

Metrics:
- Execution Success Rate (deterministic code completion)
- Claim Support Rate (CSR: proportion of report claims supported by execution receipts)
- Hallucination / Unsupported Assertion Rate
- Token Efficiency (useful scientific steps per 10k tokens)
- Autonomous Steering (successful hypothesis pivot upon empirical refutation)
"""
from __future__ import annotations

import collections
import dataclasses
import hashlib
import json
import math
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class BenchmarkTask:
    task_id: str
    name: str
    domain: str
    description: str
    ground_truth_oracle: str  # python code evaluating the result
    primary_metric: str
    falsification_threshold: float


@dataclass
class ArmResult:
    arm_id: str
    task_id: str
    execution_success: bool
    iterations_taken: int
    total_tokens: int
    cost_usd: float
    reported_claims: list[dict]
    verified_claims_count: int
    unsupported_claims_count: int
    claim_support_rate: float
    falsification_detected: bool
    autonomous_pivot_success: bool
    execution_receipt_digest: str


TASKS = [
    BenchmarkTask(
        task_id="RND-01",
        name="Regularization vs Generalization Frontier",
        domain="tabular_ml",
        description=(
            "Evaluate whether L2 regularization (lambda in [0.01, 10.0]) monotonically "
            "improves out-of-fold Brier score over unregularized baseline on noisy classification."
        ),
        ground_truth_oracle="oracle_task1",
        primary_metric="brier_score",
        falsification_threshold=0.005,  # must beat baseline by at least 0.005
    ),
    BenchmarkTask(
        task_id="RND-02",
        name="Interaction Representation Contrast",
        domain="representation_learning",
        description=(
            "Formulate and test whether derived feature interactions (polynomial & multiplicative) "
            "yield statistically significant generalization gains over raw feature representation."
        ),
        ground_truth_oracle="oracle_task2",
        primary_metric="paired_t_stat",
        falsification_threshold=2.0,  # t-statistic must exceed 2.0 (p < 0.05)
    ),
    BenchmarkTask(
        task_id="RND-03",
        name="Structured Pruning vs Quantization Pareto Analysis",
        domain="model_compression",
        description=(
            "Identify the optimal Pareto frontier between parameter sparsity and classification loss "
            "under 4-bit vs 8-bit quantization constraints."
        ),
        ground_truth_oracle="oracle_task3",
        primary_metric="pareto_efficiency",
        falsification_threshold=0.85,
    ),
]


def verify_claims_against_receipt(claims: list[dict], receipt_data: dict, tolerance: float = 0.002) -> tuple[int, int]:
    """Deterministically check if assertions in a report match empirical receipt numbers."""
    verified = 0
    unsupported = 0
    for cl in claims:
        metric = cl.get("metric")
        asserted_val = cl.get("value")
        if metric in receipt_data:
            true_val = receipt_data[metric]
            if isinstance(asserted_val, (int, float)) and isinstance(true_val, (int, float)):
                if abs(asserted_val - true_val) <= tolerance:
                    verified += 1
                else:
                    unsupported += 1
            elif str(asserted_val).strip().lower() == str(true_val).strip().lower():
                verified += 1
            else:
                unsupported += 1
        else:
            # Claim asserts a metric not present in the empirical receipt (hallucination)
            unsupported += 1
    return verified, unsupported


def compute_arm_metrics(results: list[ArmResult]) -> dict:
    """Aggregate statistical metrics for an architectural arm across benchmark tasks."""
    if not results:
        return {}
    n = len(results)
    exec_success = sum(r.execution_success for r in results) / n
    total_claims = sum(r.verified_claims_count + r.unsupported_claims_count for r in results)
    total_verified = sum(r.verified_claims_count for r in results)
    csr = total_verified / total_claims if total_claims > 0 else 0.0
    total_unsupported = sum(r.unsupported_claims_count for r in results)
    hallucination_rate = total_unsupported / total_claims if total_claims > 0 else 0.0
    avg_tokens = sum(r.total_tokens for r in results) / n
    avg_cost = sum(r.cost_usd for r in results) / n
    pivot_rate = sum(r.autonomous_pivot_success for r in results) / n

    return {
        "n_tasks": n,
        "execution_success_rate": round(exec_success, 3),
        "total_claims_asserted": total_claims,
        "total_claims_verified": total_verified,
        "claim_support_rate": round(csr, 4),
        "hallucination_rate": round(hallucination_rate, 4),
        "mean_tokens_per_task": round(avg_tokens),
        "mean_cost_usd": round(avg_cost, 4),
        "autonomous_pivot_rate": round(pivot_rate, 3),
    }


# ==============================================================================
# Design-source absorption ledger
# ==============================================================================

# Empirical-test vocabulary. An absorbed element is TESTED only when an executed
# run of this harness exercised the implementation site; a design argument is
# never sufficient to promote an entry into TESTED.
TESTED = "TESTED"
IMPLEMENTED_UNTESTED = "IMPLEMENTED_UNTESTED"
DECLARED_ONLY = "DECLARED_ONLY"
TEST_STATUSES = (TESTED, IMPLEMENTED_UNTESTED, DECLARED_ONLY)

# Published acceptance-rule families. These are the gate categories the source
# systems publish; the entry for this harness records its own family.
ACCEPTED = "ACCEPTED"
REWARDED = "REWARDED"
PRESERVED = "PRESERVED"
PASSED = "PASSED"
PROMOTED = "PROMOTED"
FALSIFIED_AND_OVERTURNED = "FALSIFIED_AND_OVERTURNED"
ACCEPTANCE_RULE_FAMILIES = (
    ACCEPTED,
    REWARDED,
    PRESERVED,
    PASSED,
    PROMOTED,
    FALSIFIED_AND_OVERTURNED,
)

#: Identifier of the entry describing this harness itself.
HARNESS_ENTRY_ID = "argo_orx"


@dataclass(frozen=True)
class AbsorptionEntry:
    """One design-source absorption record.

    ``gate_mechanism`` is the acceptance rule the source system publishes.
    ``absorbed_element``, ``design_requirement``, ``implementation_site`` and
    ``test_status`` are the absorption record: what was taken, what it obliges
    this harness to do, where that is implemented, and whether the
    implementation has been exercised by an executed run.
    """

    id: str
    name: str
    paper_ref: str
    acceptance_family: str  # published acceptance-rule family (gate category)
    representative: bool  # own entry in the representative view
    optimization_target: str
    gate_mechanism: str
    disclosure_level: str
    absorbed_element: str
    design_requirement: str
    implementation_site: str
    test_status: str

    @property
    def tested(self) -> bool:
        """True only when an executed run exercised this implementation site."""
        return self.test_status == TESTED


ABSORPTION_ENTRIES: tuple[AbsorptionEntry, ...] = (
    AbsorptionEntry(
        id="sol_pi",
        name="SoL-Pi",
        paper_ref="NVIDIA Labs Repository (2026)",
        acceptance_family=ACCEPTED,
        representative=True,
        optimization_target="Tokens/cost optimization under a predeclared capability floor",
        # The published rule accepts a run that terminates cleanly with exit code 0.
        gate_mechanism="Capability floor (non-empty steps, exit code 0)",
        disclosure_level="Tool and execution logs",
        absorbed_element=(
            "Pre-declared minimal progression condition: a task may not advance unless a "
            "declared completion floor is met."
        ),
        design_requirement=(
            "Progression must be contract-gated, so that an unsatisfied progression contract "
            "blocks the next step instead of being reported at the end. A clean exit code and "
            "intact capability floors are necessary but not sufficient: the same floor is "
            "satisfied by a leaky result, so the contract needs an invariant check behind it."
        ),
        implementation_site=(
            "Core 1 Self-Steering Engine (progression contract and goal re-injection); "
            "no typed runtime tool."
        ),
        test_status=TESTED,
    ),
    AbsorptionEntry(
        id="openai_agents_api",
        name="OpenAI Agents API",
        paper_ref="Commercial Platform (2026)",
        acceptance_family=ACCEPTED,
        representative=True,
        optimization_target="Turn orchestration & session handoffs",
        gate_mechanism="Turn/session outcome status: turn.completed / .failed / .cancelled and environment connection states",
        disclosure_level="Standard API traces",
        absorbed_element=(
            "Multi-agent session orchestration and execution-state tracking."
        ),
        design_requirement=(
            "Execution state must be tracked outside the model's context so that a session can "
            "be resumed and audited after the fact. A judge that reads the apparent error "
            "reduction cannot separate a real gain from a leaked one, so the tracked state is "
            "only useful if it carries the split that produced each number."
        ),
        implementation_site=(
            "Core 1 Self-Steering Engine (session persistence and execution-state tracking); "
            "delegation and handoff have no runtime site."
        ),
        test_status=IMPLEMENTED_UNTESTED,
    ),
    AbsorptionEntry(
        id="prime_agent",
        name="Prime Agent",
        paper_ref="Hierarchical Supervisor (2026)",
        acceptance_family=ACCEPTED,
        representative=True,
        optimization_target="Long-horizon goal continuation",
        gate_mechanism="Root model self-critique & metric check",
        disclosure_level="Session history & model reflections",
        absorbed_element=(
            "Persistent REPL execution substrate and the supervising review loop."
        ),
        design_requirement=(
            "Reasoning must run as inline execution against a structured record, with a "
            "supervising check over the numbers. The check cannot be an arithmetic check alone: "
            "arithmetic agreement is satisfied by a leaky metric, so the comparison must be "
            "re-derived under a leakage-invariant split before it is allowed to steer."
        ),
        implementation_site=(
            "Core 3 Scientific Reasoning Core (inline ipython execution, structured read/write "
            "records, supervisor review of the recorded numbers)."
        ),
        test_status=TESTED,
    ),
    AbsorptionEntry(
        id="the_ai_scientist",
        name="The AI Scientist",
        paper_ref="Lu et al. (arXiv:2408.06292)",
        acceptance_family=ACCEPTED,
        representative=False,  # instance of the ACCEPTED family; not its own paradigm
        optimization_target="Full-lifecycle autonomous scientific discovery (idea to paper)",
        gate_mechanism="LLM automated peer review score threshold",
        disclosure_level="Generated LaTeX PDF and review logs",
        absorbed_element=(
            "Full-lifecycle loop skeleton: ideation, experiment and write-up as one autonomous "
            "progression."
        ),
        design_requirement=(
            "The harness must own an end-to-end progression skeleton rather than a single-shot "
            "task loop. An automated reviewer that grades text and apparent metrics raises its "
            "own ceiling instead of lowering it, so the skeleton must never be the gate that "
            "admits a result."
        ),
        implementation_site=(
            "Core 1 Self-Steering Engine (loop skeleton); the write-up stage has no runtime site."
        ),
        test_status=IMPLEMENTED_UNTESTED,
    ),
    AbsorptionEntry(
        id="mlagentbench",
        name="MLAgentBench",
        paper_ref="Huang et al. (arXiv:2310.03302)",
        acceptance_family=ACCEPTED,
        representative=False,  # instance of the ACCEPTED family; not its own paradigm
        optimization_target="Autonomous ML engineering on validation sets",
        gate_mechanism="Validation score monotonic improvement",
        disclosure_level="Execution logs and submitted code diffs",
        absorbed_element=(
            "Per-task deterministic oracle and score-based grading of an experiment."
        ),
        design_requirement=(
            "Every experiment must be graded by a deterministic per-task oracle rather than by "
            "the agent's own report. A monotone validation-score improvement on record-level "
            "splits is not sufficient evidence of a gain, because the same monotone improvement "
            "is produced by producer-group leakage."
        ),
        implementation_site=(
            "Core 3 Scientific Reasoning Core (deterministic oracle scoring substrate; "
            "exercised across the executed Study B episodes)."
        ),
        test_status=TESTED,
    ),
    AbsorptionEntry(
        id="meta_harness",
        name="Meta-Harness / Self-Harness",
        paper_ref="arXiv:2603.28052 / 2606.09498",
        acceptance_family=REWARDED,
        representative=True,
        optimization_target="Bi-level harness mutation: argmax_H E[r(tau, x)]",
        gate_mechanism="Validation metric reward r(tau, x)",
        disclosure_level="Harness source diffs",
        absorbed_element=(
            "Comparison-based improvement procedure over harness configurations."
        ),
        design_requirement=(
            "Harness variants must be compared on a fixed basis before any variant is adopted. A "
            "validation metric must never be wired straight into the improvement signal: an "
            "apparent error drop rewards whichever mutation exploits the leakage, so the metric's "
            "methodological validity has to be refuted before the metric is used as a reward."
        ),
        implementation_site=(
            "Core 4 Decision & Pivot Mechanism (version-comparison discipline; no runtime reward "
            "loop is wired to a metric)."
        ),
        test_status=IMPLEMENTED_UNTESTED,
    ),
    AbsorptionEntry(
        id="scroll",
        name="SCROLL",
        paper_ref="Alibaba Qwen (arXiv:2608.21690)",
        acceptance_family=PRESERVED,
        representative=True,
        optimization_target="Context-as-an-Environment lossless retrieval",
        gate_mechanism="Rule verifier + LLM QA check",
        disclosure_level="Append-only event stream",
        absorbed_element=(
            "Lossless, append-only context and environment preservation model."
        ),
        design_requirement=(
            "Accumulated context and environment state must be preserved without loss, and typed "
            "so that preserved state stays refutable. Lossless preservation alone keeps a "
            "refuted result available on equal footing, so the state handler must carry node "
            "types (gap, hypothesis, decision, experiment, claim, receipt) that record what each "
            "preserved item is."
        ),
        implementation_site=(
            "Core 2 Environment & Context Handler (components.TypedContextGraph; runtime tools "
            "graph_add and graph_query — the record path graph_add was exercised in the executed "
            "full-harness episodes, the retrieval path graph_query fired zero times)."
        ),
        test_status=TESTED,
    ),
    AbsorptionEntry(
        id="harnessdev",
        name="HarnessDev",
        paper_ref="arXiv:2609.01437",
        acceptance_family=PASSED,
        representative=True,
        optimization_target="Benchmark task score co-evolution",
        gate_mechanism="Pre-keyed benchmark suite unit tests",
        disclosure_level="Tool test outcomes",
        absorbed_element=(
            "Harness construction with unit-test-based self-verification."
        ),
        design_requirement=(
            "The harness must verify itself against executable tests rather than against its own "
            "description. A pre-keyed suite cannot grade a discovery that has no key, so "
            "self-verification must be paired with a domain oracle covering the case the keys "
            "do not reach."
        ),
        implementation_site=(
            "Core 4 Decision & Pivot Mechanism (self-verification discipline; harness test "
            "suites under experiments/study_b/harness, which no executed episode invokes)."
        ),
        test_status=IMPLEMENTED_UNTESTED,
    ),
    AbsorptionEntry(
        id="recevolve",
        name="RecEvolve",
        paper_ref="arXiv:2609.01622",
        acceptance_family=PROMOTED,
        representative=True,
        optimization_target="Domain recursive skill self-evolution",
        gate_mechanism="Offline metric improvement threshold: delta >= epsilon",
        disclosure_level="Skill code registry",
        absorbed_element=(
            "Pre-registered threshold as the promotion decision rule."
        ),
        design_requirement=(
            "A threshold must be registered before the experiment it governs runs. A crossing on "
            "its own must not promote anything to a baseline: an apparent delta that clears the "
            "registered epsilon is still reversed by the grouped result, so promotion must "
            "require a leakage-invariant re-derivation."
        ),
        implementation_site=(
            "Core 4 Decision & Pivot Mechanism (components.DecisionProtocol / FalsificationLoop; "
            "runtime tools threshold_register and loop_evaluate, both exercised in the executed "
            "full-harness episodes)."
        ),
        test_status=TESTED,
    ),
    AbsorptionEntry(
        id=HARNESS_ENTRY_ID,
        name="This Work (ARGO-ORX)",
        paper_ref="This harness (design-source absorption ledger, 2026)",
        acceptance_family=FALSIFIED_AND_OVERTURNED,
        representative=True,
        optimization_target="Counterfactual Falsification Robustness",
        gate_mechanism="Layer 2 Custody Holdout + Layer 3 Roberts et al. Group Isolation",
        disclosure_level="Cryptographic receipt chain & compute/prompt confounds",
        absorbed_element=(
            "Integration of the absorbed elements above, plus a self-falsification subsystem "
            "placed inside the decision core rather than outside the harness."
        ),
        design_requirement=(
            "The decision core must be able to refute the harness's own result before that result "
            "is used for anything: a single-use custody holdout on a split the development "
            "session never saw, and a group-blocked counterfactual re-derivation that can show an "
            "apparent gain to be an artifact of producer-group leakage."
        ),
        implementation_site=(
            "All four cores; the self-falsification subsystem sits inside Core 4 Decision & Pivot "
            "Mechanism (custody holdout and group-blocked counterfactual re-derivation)."
        ),
        test_status=TESTED,
    ),
)


class DesignSourceAbsorptionLedger:
    """Provenance ledger over the canonical absorption entries.

    Every count exposed here is derived from the entries; none is stored. The
    ledger refuses to be constructed with duplicate identifiers, and
    :meth:`validate` refuses to accept an entry set whose acceptance families,
    test statuses or absorption fields are inconsistent.
    """

    def __init__(self, entries: Iterable[AbsorptionEntry]) -> None:
        self._entries: tuple[AbsorptionEntry, ...] = tuple(entries)
        self._index: dict[str, AbsorptionEntry] = {e.id: e for e in self._entries}
        if len(self._index) != len(self._entries):
            raise ValueError("absorption ledger contains duplicate system identifiers")

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __getitem__(self, system_id: str) -> AbsorptionEntry:
        return self._index[system_id]

    @property
    def entries(self) -> tuple[AbsorptionEntry, ...]:
        return self._entries

    @property
    def absorption_table(self) -> tuple[AbsorptionEntry, ...]:
        """The full absorption table: every recorded system, harness included."""
        return self._entries

    @property
    def representative_view(self) -> tuple[AbsorptionEntry, ...]:
        """Entries that carry their own row in the representative view."""
        return tuple(e for e in self._entries if e.representative)

    @property
    def collapsed_entries(self) -> tuple[AbsorptionEntry, ...]:
        """Entries folded into an acceptance family another entry represents."""
        return tuple(e for e in self._entries if not e.representative)

    @property
    def acceptance_families(self) -> tuple[str, ...]:
        """Distinct published acceptance-rule families, in declaration order."""
        return tuple(dict.fromkeys(e.acceptance_family for e in self._entries))

    def family_representatives(self) -> dict[str, tuple[str, ...]]:
        """Representative entry ids per published acceptance family."""
        return {
            family: tuple(
                e.id for e in self._entries if e.acceptance_family == family and e.representative
            )
            for family in self.acceptance_families
        }

    def by_test_status(self) -> dict[str, tuple[str, ...]]:
        """Entry ids grouped by empirical-test status."""
        return {
            status: tuple(e.id for e in self._entries if e.test_status == status)
            for status in TEST_STATUSES
        }

    def untested(self) -> tuple[AbsorptionEntry, ...]:
        """Entries whose implementation site has no executed empirical test."""
        return tuple(e for e in self._entries if not e.tested)

    def counts(self) -> dict[str, int]:
        """Derive every system count from the canonical entry list.

        ``absorption_table`` is the full table, ``frontier_systems`` excludes the
        entry for this harness, ``representative_view`` drops the entries folded
        into a family another entry already represents, and
        ``acceptance_families`` is the number of distinct published gate
        categories.
        """
        harness_entries = [e for e in self._entries if e.id == HARNESS_ENTRY_ID]
        return {
            "absorption_table": len(self.absorption_table),
            "frontier_systems": len(self.absorption_table) - len(harness_entries),
            "representative_view": len(self.representative_view),
            "acceptance_families": len(self.acceptance_families),
        }

    def validate(self) -> None:
        """Raise ValueError unless the ledger is internally consistent."""
        if not self._entries:
            raise ValueError("absorption ledger is empty")

        for entry in self._entries:
            if entry.test_status not in TEST_STATUSES:
                raise ValueError(f"{entry.id}: unknown test status {entry.test_status!r}")
            if entry.acceptance_family not in ACCEPTANCE_RULE_FAMILIES:
                raise ValueError(f"{entry.id}: unknown acceptance family {entry.acceptance_family!r}")
            for field_name in ("absorbed_element", "design_requirement", "implementation_site"):
                if not getattr(entry, field_name).strip():
                    raise ValueError(f"{entry.id}: empty {field_name}")

        represented = {
            family: self.family_representatives()[family] for family in self.acceptance_families
        }
        for family, reps in represented.items():
            if not reps:
                raise ValueError(f"acceptance family {family} has no representative entry")
        for entry in self.collapsed_entries:
            if entry.acceptance_family not in represented:
                raise ValueError(
                    f"{entry.id} is collapsed but its family {entry.acceptance_family!r} is unrepresented"
                )
        if not self[HARNESS_ENTRY_ID].representative:
            raise ValueError("this harness must appear in the representative view")


#: The single canonical ledger. Import-time validation keeps the counts, the
#: families and the test statuses from drifting apart silently.
LEDGER = DesignSourceAbsorptionLedger(ABSORPTION_ENTRIES)
LEDGER.validate()


# ==============================================================================
# S1 specification mapping: what each published acceptance rule leaves open
# ==============================================================================

# S1 anchors, fixed. The case is the wine producer-group leakage discovery: the
# candidate looks better than the unified baseline on a naive split, is worse
# than the grouped baseline once producer groups are blocked, and changes sign on
# a custody holdout. Every value below is a frozen case input, not a measurement
# of any source system and not a judgement passed on any candidate.
S1_CANDIDATE_STRATEGY = "color_stratified_gbt"

# Published rule consequences under S1, per system. These state what the
# system's own acceptance rule does with this case, and are the residual defects
# from which this harness's design requirements are derived. They are not
# judgements rendered by this ledger.
S1_RULE_CONSEQUENCE = {
    "sol_pi": "Task completed with exit code 0; predeclared capability floor intact.",
    "openai_agents_api": "turn.completed emitted normally; platform scope governs orchestration, without an epistemic validation gate over scientific output.",
    "prime_agent": "Supervisor checks arithmetic: 0.5183 < 0.5245 satisfies goal improvement criterion.",
    "the_ai_scientist": "LLM automated reviewer grades paper text and apparent SOTA metric with ceiling effect.",
    "mlagentbench": "Validation metric monotonic improvement accepted; lacks cluster-blocked oracle.",
    "meta_harness": "Apparent MAE drop yields positive reward; harness updates to exploit group leakage.",
    "scroll": "Trajectory logged sequentially in append-only event stream; environment model preserves state without domain falsification gate.",
    "harnessdev": "Pre-keyed test suite passes; lacks domain oracle for un-keyed wine grouping.",
    "recevolve": "Delta (0.5245 - 0.5183 = 0.0062) >= epsilon (0.005); permanently replaces baseline.",
    HARNESS_ENTRY_ID: (
        "Layer 2 Custody Holdout + Layer 3 Roberts et al. Group-Blocked CV: the apparent gain is "
        "an artifact of {leakage_pct}% group leakage, and the custody holdout exposes the sign "
        "reversal and the un-reproduced baseline metrics."
    ),
}


def s1_case_anchors(
    naive_cv_mae: float,
    group_isolated_cv_mae: float,
    holdout_mae_diff: float,
    unified_baseline_mae: float = 0.5245,
    group_isolated_baseline_mae: float = 0.5179,
    materiality_epsilon: float = 0.005,
) -> dict:
    """Derive the S1 quantities and check that the anchors stay consistent.

    Raises ValueError if the supplied anchors no longer describe the S1 case:
    group blocking must not improve on the naive split, the naive split must look
    better than the unified baseline, the grouped result must not look better
    than the grouped baseline, and the apparent gain must clear the materiality
    epsilon. This is what keeps the mapping below from being read off
    mutually inconsistent numbers.
    """
    leakage_delta = group_isolated_cv_mae - naive_cv_mae
    apparent_gain = unified_baseline_mae - naive_cv_mae
    if group_isolated_cv_mae <= naive_cv_mae:
        raise ValueError("S1 anchors do not describe leakage: grouping does not worsen the error")
    if naive_cv_mae >= unified_baseline_mae:
        raise ValueError("S1 anchors do not describe the case: the naive split is not apparent gain")
    if group_isolated_cv_mae < group_isolated_baseline_mae:
        raise ValueError("S1 anchors do not describe the case: the grouped result beats its baseline")
    if apparent_gain < materiality_epsilon:
        raise ValueError("S1 anchors do not clear the materiality epsilon")

    return {
        "candidate_strategy": S1_CANDIDATE_STRATEGY,
        "naive_cv_mae": naive_cv_mae,
        "group_isolated_cv_mae": group_isolated_cv_mae,
        "holdout_mae_diff": holdout_mae_diff,
        "unified_baseline_mae": unified_baseline_mae,
        "group_isolated_baseline_mae": group_isolated_baseline_mae,
        "materiality_epsilon": materiality_epsilon,
        "leakage_delta": leakage_delta,
        "apparent_gain_over_unified_baseline": apparent_gain,
        "leakage_pct": round(leakage_delta / group_isolated_cv_mae * 100, 2),
    }


def s1_specification_mapping(
    candidate_strategy: str,
    naive_cv_mae: float,
    group_isolated_cv_mae: float,
    holdout_mae_diff: float,
) -> dict[str, dict]:
    """Map each published acceptance rule onto S1 as a design requirement.

    The S1 case supplies the observation, and each entry of the ledger supplies
    the requirement this harness must satisfy because of what its source
    system's published acceptance rule does with that observation. The mapping
    is deductive over the recorded rules; it is not an evaluation of the source
    systems, nothing here is executed against them, and no system is ranked.

    S1 anchors, fixed as case inputs:
    - Wine color stratification with 5.04% - 17% group leakage
    - Apparent naive CV: 0.5183 (looks superior to unified baseline 0.5245)
    - Group-isolated CV: 0.5406 (worse than unified baseline 0.5179)
    - Holdout diff: +0.000117 (reversed from frozen -0.0012)

    Every system in the absorption table receives one record, so the caller can
    read the requirement and its implementation site together with the published
    rule that produced it.
    """
    if candidate_strategy != S1_CANDIDATE_STRATEGY:
        raise ValueError(f"unknown S1 candidate strategy {candidate_strategy!r}")

    anchors = s1_case_anchors(naive_cv_mae, group_isolated_cv_mae, holdout_mae_diff)
    harness_note = S1_RULE_CONSEQUENCE[HARNESS_ENTRY_ID].format(leakage_pct=anchors["leakage_pct"])

    mapping: dict[str, dict] = {}
    for entry in LEDGER:
        consequence = S1_RULE_CONSEQUENCE[entry.id]
        mapping[entry.id] = {
            "system_name": entry.name,
            "paper_ref": entry.paper_ref,
            "published_acceptance_rule": entry.gate_mechanism,
            "published_rule_consequence_under_s1": (
                harness_note if entry.id == HARNESS_ENTRY_ID else consequence
            ),
            "absorbed_element": entry.absorbed_element,
            "design_requirement": entry.design_requirement,
            "implementation_site": entry.implementation_site,
            "test_status": entry.test_status,
            "s1_anchors": anchors,
        }
    return mapping
