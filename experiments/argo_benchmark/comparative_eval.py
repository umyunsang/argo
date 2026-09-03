"""Comparative Evaluation Harness for AI Native R&D Agent Architectures.

Benchmarks three architectural paradigms:
1. Minimalist Harness (Pi Paradigm): Stateless bash + 4 primitive tools + flat memory.
2. Expressive Harness (Prime Agent Paradigm): Persistent IPython REPL + unstructured state.
3. Accountable Research Harness (ARGO Composite): Persistent REPL + Typed Context Graph +
   Claim Locking + Popperian Falsifier Loops.

Evaluates on three concrete scientific R&D tasks with deterministic execution oracles:
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
