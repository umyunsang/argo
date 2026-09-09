# Literature Anchor and Non-Novelty Map

Created: 2026-09-04T15:43:42+09:00  
Status: **internal review map; only FULL_PAPER_READ locators support scientific claims**

| anchor | source | verified locators | allowed role | boundary |
|---|---|---|---|---|
| W3C PROV-DM/O | W3C Recommendations 2013 | prov_dm_scope; prov_dm_entity_activity; prov_dm_derivation; prov_dm_bundle_provenance; prov_o_owl_encoding | generic Entity/Activity/Agent and provenance interchange | no scientific correctness, admissibility, causal validity, or G efficacy |
| RO-Crate | 10.3233/DS-210053 | rocrate_structured_archive; rocrate_self_described_root; rocrate_profiles_and_prov_coexist; rocrate_workflow_run_boundary; rocrate_reexecution_limits | JSON-LD research-object packaging and linked detailed PROV traces | package conformance is not clean rerun or G efficacy |
| RLM | 2512.24601 | rlm_external_environment_definition; rlm_repl_initialization | inherited recursive/programmatic context substrate | self-described mechanism; no ARGO efficacy |
| Prime Agent | 2608.23552 | prime_architecture; prime_information_hierarchy; prime_nanogpt_harness_effect | inherited persistent REPL/daemon/session substrate | system self-description; not independent efficacy evidence |
| Continual Harness | 2605.09998 | continual_refinement_mechanism; continual_component_edits | inherited persistent harness-state refinement | prior mechanism only |
| ResearchAgent | 2404.07738 | researchagent_idea_decomposition; researchagent_citation_graph_survey; researchagent_entity_knowledge_store; researchagent_iterative_reviewers; researchagent_no_ground_truth_evaluation; researchagent_reviewer_scope_limit | staged idea generation, literature/knowledge augmentation, iterative reviewer critique | no independent two-candidate generation or deterministic admission; no ARGO C efficacy |
| Co-Scientist | 2502.18864 | coscientist_agent_roles | design/reviewer competition prior art | does not establish local benefit |
| EviGraph | 2608.04738 | evigraph_operational_graph | typed evidence graph prior art | non-novelty boundary for G |
| SciAgents | 2409.05556 | sciagents_graph_agents | knowledge-graph scientific reasoning prior art | non-novelty boundary for G |
| SCOPE | 2608.03501 | scope_search_counterevidence; scope_stage_isolation_mechanism; scope_stage_isolation_ablation | rule-constrained staged design and counterevidence to search-alone benefit | search access alone is not efficacy |
| OpenScholar | 2411.14199 | openscholar_datastore_cutoff; openscholar_three_retrieval_sources; openscholar_self_feedback_pipeline; openscholar_citation_metrics; openscholar_evaluation_limitations; openscholar_judge_agreement | frozen corpus/index, retrieval-factor separation, citation metric and evaluator limitations | combined system result does not identify local retrieval effect; LLM judge secondary only |
| PaperQA2 | 2409.13740 | paperqa2_litqa_metrics; paperqa2_pipeline_recall_stages; paperqa2_precision_accuracy_tradeoff; paperqa2_question_construction_and_leak; paperqa2_open_source_infrastructure_gap | separate answer precision/accuracy/source recall, stage-wise retrieval recall, leakage and infrastructure boundaries | institutional self-evaluation; local adapter benefit and reproducibility not established |
| HippoRAG | 2405.14831 | hipporag_graph_index_single_step; hipporag_index_construction | graph retrieval method and limitations | retrieval adapter evidence only |
| HarnessOpt-Bench | 2608.06301 | harnessopt_trusted_holdout_boundary | fixed held-out target evaluation and audit boundary | evaluation pattern, not ARGO efficacy |
| POPPER | 2502.09858 | popper_implication_assumption; popper_conditional_sequential_validity; popper_optional_stopping; popper_failed_attempt_not_evidence; popper_type1_not_truth | sequential falsification, stopping, Type-I boundary, and power/error-control distinction | does not establish ARGO F efficacy; assumptions must be proven |
| ScienceAgentBench | 2410.05080 | scienceagentbench_task_source_and_count; scienceagentbench_contamination_control_test_set_removal; scienceagentbench_contamination_control_label_hiding | scientific-task sampling and hidden evaluation | current local environment certification is defective |
| RE-Bench | 2411.15114 | rebench_design_goals_transfer_limit; rebench_environment_score_contract; rebench_human_baseline_heterogeneity; rebench_best_of_k_allocation; rebench_scaffold_and_time_surface; rebench_limits_and_hidden_test | task-level floor/ceiling, fixed resource surfaces, score visibility, best-of-k and transfer boundaries | seven short ML environments do not establish ARGO efficacy or global R&D automation |
| ResearchClawBench | 2606.07591 | researchclaw_hidden_target_rubric; researchclaw_report_scoring_limit | research-process evaluation and report-scoring limit | qualitative design anchor |
| PaperBench | 2504.01848 | paperbench_benchmark_purpose; paperbench_verifier_rubric_granularity | partial-credit replication evaluation | stage-specific, not interchangeable with task outcome |
| CORE-Bench | 2409.11363 | corebench_benchmark_target_task_computational_reproduc; corebench_benchmark_scale_270_tasks_181_task_questions; corebench_difficulty_level_design_information_given_to | reproducibility/recovery capsule candidate | must certify a runnable subset locally |

## Missing full-read anchors — blockers, not citations


## Implementation-only materials

- Pi-style minimal behavior, OpenResearch CLI, and Exa product documentation may document implementation provenance and interfaces internally. They do not establish scientific benefit.
- Exa is one retrieval adapter. Stage R selects a retrieval policy; it does not test whether the product itself improves science.

## Counterevidence that must remain visible

- SCOPE reports that search mode alone does not reliably improve design quality.
- **Do not use the broad claim "current autonomous research systems remain weak"**: it is ungrounded at this scope.
  The allowed narrow statement is that ResearchClawBench's authors identify final-report scoring limits
  (`researchclaw_report_scoring_limit`), while local T1 evidence shows a specific scorer/environment defect.
- The local T1-prime environment failure and reversed crash rule show that benchmark executability is part of measurement certification, not a nuisance to ignore.
