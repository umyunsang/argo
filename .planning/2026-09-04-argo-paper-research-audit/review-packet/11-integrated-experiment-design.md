# 11 — Integrated ARGO Experiment Design Synthesis

Status: **DRAFT; NO EXPERIMENT OR SPEND AUTHORIZED**  
Created: 2026-09-04T19:39:02+09:00  
Machine-readable decisions: `11-design-choice-matrix.json`

## Research objective

Under a fixed model, tool surface, corpus snapshot, and resource budget, test whether typed evidence-and-experiment
lineage (`G`), design competition with deterministic admission (`C`), and a bounded falsification/refinement loop (`F`)
improve validity, held-out scientific task outcome, reproducibility, and recovery in long-horizon autonomous R&D.

The contribution is not any substrate component. It is a causally testable composition with preserved research/engine
lineage, evidence admissibility, and recovery.

## Competitive synthesis of design choices

Every selected row has at least two alternatives, a verified source locator or immutable authority span, uncertainty,
a falsifier, and executable acceptance condition.

| choice | alternatives compared | selected | principal evidence | fail/redirect condition |
|---|---|---|---|---|
| D01_FIXED_SUBSTRATE | vary_all, fixed_substrate | **fixed_substrate** | harnessopt_trusted_holdout_boundary, rebench_scaffold_and_time_surface | 고정 manifest 밖 차이가 한 개라도 있으면 인과 대조가 아니다. |
| D02_CAUSAL_MODEL | sxr, b012, gcf | **gcf** | scope_stage_isolation_mechanism, harnessopt_trusted_holdout_boundary | full factorial의 단일요인 semantics를 loader가 증명하지 못하면 fallback removal claim으로 강등한다. |
| D03_G_STATE | no_content, flat_equal, different_graph | **flat_equal** | evigraph_operational_graph, prov_dm_entity_activity, rocrate_profiles_and_prov_coexist | G0/G1 accessible-content multiset hash가 다르면 해당 쌍은 protocol failure다. |
| D04_C_COMPETITION | single, iterative_review, independent_two | **independent_two** | researchagent_iterative_reviewers, researchagent_no_ground_truth_evaluation, coscientist_agent_roles… | 후보 B가 A를 보거나 critic 이전 freeze가 깨지면 C1이 아니다. |
| D05_F_LOOP | one_shot, unbounded_oracle, bounded_nonoracle | **bounded_nonoracle** | popper_conditional_sequential_validity, popper_optional_stopping, openscholar_overediting… | hidden scorer/gold 접근 또는 3회 초과 시 F run은 invalid다. |
| D06_RETRIEVAL | assume_semantic, live_mix, stage_r | **stage_r** | scope_search_counterevidence, paperqa2_litqa_metrics, paperqa2_pipeline_recall_stages… | 어떤 retrieval arm도 precision/unsupported constraint를 못 넘으면 NONE을 선택한다. |
| D07_TASK_SAMPLE | one_task_rollouts, few_tasks, distinct_tasks | **distinct_tasks** | scienceagentbench_task_source_and_count, rebench_scope_and_attempts, rebench_limits_and_hidden_test | 서로 다른 인증 과제가 16개 미만이면 population confirmation을 차단한다. |
| D08_REPEAT_ESTIMAND | best_k, iid_rollouts, task_cluster_itt | **task_cluster_itt** | rebench_best_of_k_allocation, rebench_rollout_estimand, rebench_rare_success_overfit | best seed 선택 또는 rollout을 독립 task로 계수하면 확증 estimand가 무효다. |
| D09_PRIMARY_OUTCOME | llm_judge, valid_execution_one, rule_score_zero_fail | **rule_score_zero_fail** | paperbench_verifier_rubric_granularity, openscholar_judge_agreement, rebench_feasibility_technical_issues | crash/timeout/nonzero/missing/parse가 0·inadmissible이 아니면 Stage 0 실패다. |
| D10_SECONDARY_OUTCOMES | composite, separate | **separate** | paperqa2_precision_accuracy_tradeoff, openscholar_citation_metrics, openscholar_evaluation_limitations | 어떤 주장이 composite 하나만으로 지지되면 보고 계약 실패다. |
| D11_VISIBILITY_RANDOMIZATION | visible_test, fixed_order, blind_counterbalanced | **blind_counterbalanced** | rebench_limits_and_hidden_test, harnessopt_trusted_holdout_boundary, scienceagentbench_contamination_control_label_hiding | scorer가 cell ID를 보거나 F가 final score를 보면 run invalid다. |
| D12_ANALYSIS | iid_seed_test, task_cluster | **task_cluster** | rebench_limits_and_hidden_test, researchclaw_report_scoring_limit | 20 task에서도 +0.10에 80% power가 없으면 확증을 시작하지 않는다. |
| D13_RECOVERY | joint_remove, lp_factorial | **lp_factorial** | corebench_benchmark_target_task_computational_reproduc, rocrate_reexecution_limits, rebench_evaluation_procedure | L0/L1 content equality 또는 동일 P가 깨지면 H7 claim을 차단한다. |
| D14_PROVENANCE_EXPORT | same_graph, separate_layers | **separate_layers** | prov_dm_bundle_provenance, rocrate_profiles_and_prov_coexist, rocrate_workflow_run_boundary | metadata package PASS를 efficacy나 clean rerun으로 사용하면 주장이 무효다. |
| D15_BUDGET_APPROVAL | historical_cap, median_projection, full_envelope | **full_envelope** | harnessopt_trusted_holdout_boundary, rebench_scaffold_and_time_surface | TBD가 하나라도 있거나 승인 record/hash가 없으면 fingerprint와 실행을 차단한다. |

## Complete staged design

### Stage 0 — measurement certification

Run the 45 fixtures in `stage0-certification-spec.json` in a clean environment. They cover seed propagation, task
identity, all evaluator failure states, environment parity, exact cell loading, one-factor manipulation, resource caps,
condition blinding, OS-level oracle isolation, receipt provenance, stale/orphan run detection, floor/ceiling, and issue
responsibility. The current meta-validator checks the specification only. No treatment episode is admissible until the
actual runner passes every fixture with exact reason codes.

### Stage R — retrieval-policy selection

On development-only literature tasks, compare NONE, SEMANTIC_VECTOR, and CITATION_ENTITY_GRAPH over one materialized,
hashed corpus. Retrieval is the only varied surface; reranker, generation, feedback, attribution, and budgets are fixed.
Eligibility protects citation precision and cited-but-unsupported rate. Select the largest lower confidence bound for
answer accuracy, then source recall, cost, latency, and arm ID. Freeze the winner before Stage 1 outcomes.

### Stage 1 — scientific-task factorial

- **Population:** executable scientific-computing tasks from one pinned release.
- **Development:** exactly four tasks, one from each of four deterministically selected domain strata; permanently
  excluded from confirmation.
- **Confirmation:** 12–20 distinct hidden tasks across those domains.
- **Treatments:** all eight G×C×F cells from `02-treatment-manifest.json`.
- **Repeats:** at least three unique rollout IDs per task-cell. `environment_seed` is verified for controllable RNGs; provider model sampling is explicitly unseeded.
- **Reference:** G0C0F0 under the same backbone, tools, content, environment and maximum resources.
- **Order:** sealed within-task counterbalancing.
- **Visibility:** F sees only non-oracle protocol-validity `V[r]`; official scorer runs after stopping.
- **Primary outcome:** condition-blind official normalized task score, intention-to-run. Fatal violations and
  agent-caused/evaluator failures score zero.
- **No best-of-k:** all scheduled rollout IDs contribute to the task-cell mean.

### Stage 2 — recovery factorial

Use 6–10 disjoint certified reproducibility capsules and three interruption points. Cross typed lineage (`L`) with
checkpoint/recovery package (`P`). H7 uses `L1P1-L0P1`; `L1P1-L0P0` is combined-package secondary evidence only.
Require L0/L1 content equality at each P level, capsule-cluster intervals, and final-quality noninferiority margin -0.05.

### Stage 3 — qualitative integrated cases

Keep three end-to-end cases for external-validity demonstration only. They are not the causal sample. Any event-built
artifact begins inside its official window from allowed public sources under `09-nais-clean-room-lineage.md`.

## Hypotheses and tests

H1–H5 estimate marginal G/C/F and GC/GF task-level contrasts. H6 requires FULL to exceed all seven preregistered cells
by +0.10 on `RA[t,c]=S[t,c]×P[t,c]^3`. H7 uses Stage 2 L1P1-L0P1. Apply Holm over 13 superiority contrasts; handle H7
quality as an intersection noninferiority requirement. Primary intervals are task- or capsule-cluster bootstrap 95%;
mixed effects are secondary.

The +0.10 interpretation is one extra success per ten only for a binary equally weighted endpoint. For graded scores it
is a 0.10 mean normalized-score change.

## Power, budget, and stopping

Use only the four development tasks for cluster-preserving power and cost simulation. Require at least 80% power at
+0.10 with 12–20 tasks. If FULL is unaffordable, request approval for the five-arm FULL/-G/-C/-F/G0C0F0 fallback and
limit claims to removal impacts. The total human envelope must cover Stage 0/R/1/2 upper ranges plus 20% contingency.
No historical cap is inherited automatically.

Stop before or during execution on any seal, task, environment, scorer, oracle, provenance, manipulation, or hard-cap
failure. Infrastructure receives at most one blinded retry; the original remains in reliability. Confirmatory outcomes
cannot reopen the protocol. A protocol defect found without outcome visibility creates a new fingerprint and disjoint
sample.

## Interpretation ceiling

Even a positive result permits only: **best observed among the eight preregistered configurations under the evaluated
task distribution and budget.** It does not support SOTA, global optimality, product superiority, or full automation of
real-world R&D.

## Current admission decision

`BLOCK`: Stage 0 runner is uncertified; 16 distinct tasks are not certified; Stage R is unrun; cell loaders have no
receipts; power and treatment-adjusted cost are unknown; no human envelope is approved; protocol fingerprint is null.
