# instruction-0016 §2.4 메커니즘-증거 테이블

작성: 2026-09-04. 16편 전문 정독(VERIFIED_READ) 결과를 메커니즘 arm별로 정리한다.
각 행의 locator는 `paper/sources/claim-locators.json#<id>`이고 excerpt는 원문 인용, excerpt_sha256으로 고정된다.
측정 효과는 논문이 보고한 값이며 본 프로젝트의 로컬 efficacy 주장이 아니다 (source 노드 role: prior_mechanism_or_counterevidence_not_local_efficacy).

## mechanism:minimal_tool_coding_harness — 최소 도구 코딩 하니스 (B1)

### OpenHands: An Open Platform for AI Software Developer Agents (wang2024openhands, arXiv 2407.16741) — source:verified:openhands

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | action space IS code/terminal execution + browsing | — | B1 | abstract | `openhands_action_space_is_code_terminal_execution_brow` |
| 2 | core primitive actions: Python + bash in sandbox | — | B1 | Agent Definition and Implementation | `openhands_core_primitive_actions_python_bash_in_sandbo` |
| 3 | PL-based action space rationale (cites CodeAct) | — | B1 | Agent Definition and Implementation | `openhands_pl_based_action_space_rationale_cites_codeac` |
| 4 | runtime: docker sandbox | — | B1 | Agent Runtime: How Execution of Actions Results in Observations | `openhands_runtime_docker_sandbox` |
| 5 | ACI design claim (inherited from SWE-agent) | — | B1 | Agent Skills: The Extensible Agent-Computer Interface | `openhands_aci_design_claim_inherited_from_swe_agent` |
| 6 | AgentSkills inclusion criteria | — | B1 | Agent Skills: The Extensible Agent-Computer Interface | `openhands_agentskills_inclusion_criteria` |
| 7 | multi-agent delegation | — | B1 | Agent Delegation: Cooperative Multi-agent Interaction | `openhands_multi_agent_delegation` |
| 8 | exact benchmark number: SWE-bench Lite | — | B1 | Software Engineering | `openhands_exact_benchmark_number_swe_bench_lite` |
| 9 | exact benchmark number: HumanEvalFix | — | B1 | HumanEvalFix | `openhands_exact_benchmark_number_humanevalfix` |
| 10 | baseline comparison with shot-count control | SWE-agent's 87.7% HumanEvalFix is 1-shot vs OpenHands 0-shot | B1 | HumanEvalFix | `openhands_baseline_comparison_with_shot_count_control` |
| 11 | contamination/assistance control on SWE-bench | — | B1 | Software Engineering | `openhands_contamination_assistance_control_on_swe_benc` |
| 12 | limitation: long-file editing | — | B1 | Limitations and Future Work | `openhands_limitation_long_file_editing` |
| 13 | eval infrastructure: mocked integration tests | — | B1 | Quality Control: Integration Tests for Agents | `openhands_eval_infrastructure_mocked_integration_tests` |
| 14 | evaluation cost | — | B1 | Quality Control: Integration Tests for Agents | `openhands_evaluation_cost` |
| 15 | provenance: CodeActSWEAgent demo prompt reused from SWE-agent | — | B1 | In-context Demonstration for CodeActSWEAgent | `openhands_provenance_codeactsweagent_demo_prompt_reuse` |

### SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering (yang2024sweagent, arXiv 2405.15793) — source:verified:sweagent

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | action space / ACI definition | — | B1 | The Agent-Computer Interface | `sweagent_action_space_aci_definition` |
| 2 | ACI as abstraction layer | — | B1 | Introduction | `sweagent_aci_as_abstraction_layer` |
| 3 | benchmark number vs baseline (RAG 3.8%) | +8.67pp absolute over prior best RAG baseline on full SWE-bench test set | B1 | Introduction | `sweagent_benchmark_number_vs_baseline_rag_3_8` |
| 4 | ACI ablation vs shell-only baseline | +10.7pp over shell-only agent on SWE-bench Lite | B1 | Introduction | `sweagent_aci_ablation_vs_shell_only_baseline` |
| 5 | exact benchmark numbers | — | B1 | Results | `sweagent_exact_benchmark_numbers` |
| 6 | cost-vs-accuracy tradeoff vs RAG baseline | 6.7-fold resolved-rate improvement at 8-13x inference cost | B1 | Results | `sweagent_cost_vs_accuracy_tradeoff_vs_rag_baseline` |
| 7 | ACI design: guarded search commands | — | B1 | The Agent-Computer Interface | `sweagent_aci_design_guarded_search_commands` |
| 8 | ACI design: bounded file viewer window | — | B1 | The Agent-Computer Interface | `sweagent_aci_design_bounded_file_viewer_window` |
| 9 | ACI design: linting guardrail on edits | — | B1 | ACI Design | `sweagent_aci_design_linting_guardrail_on_edits` |
| 10 | ablation: removing linting hurts | linting guardrail improves Lite resolve rate (no-lint arm 15.0%±3.0) | B1 | Analysis of ACI Design | `sweagent_ablation_removing_linting_hurts` |
| 11 | ACI portability across LMs | — | B1 | Introduction | `sweagent_aci_portability_across_lms` |
| 12 | temporal/contamination control | — | B1 | Results | `sweagent_temporal_contamination_control` |
| 13 | behavioral analysis: failed edits | — | B1 | Breakdowns of Action Sequences | `sweagent_behavioral_analysis_failed_edits` |
| 14 | behavioral analysis: edit recovery | — | B1 | Analysis of Agent Behavior | `sweagent_behavioral_analysis_edit_recovery` |
| 15 | compute budget control | — | B1 | Experimental Setup | `sweagent_compute_budget_control` |
| 16 | limitation: small toolkit | — | B1 | Limitations & Future Work | `sweagent_limitation_small_toolkit` |

## mechanism:persistent_repl_recursive_harness — 영속 REPL/재귀 하니스 (B1)

### Executable Code Actions Elicit Better LLM Agents (wang2024codeact, arXiv 2402.01030) — source:verified:codeact

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | action space IS code execution | — | B1 | abstract | `codeact_action_space_is_code_execution` |
| 2 | multi-turn interpreter in the loop | — | B1 | abstract | `codeact_multi_turn_interpreter_in_the_loop` |
| 3 | headline benchmark number vs JSON/text actions | up to 20% higher success rate than text/JSON action formats | B1 | abstract | `codeact_headline_benchmark_number_vs_json_text_actio` |
| 4 | experimental setup: action-format comparison | — | B1 | CodeAct Shows the Promise as a Strong Tool Use Framework | `codeact_experimental_setup_action_format_comparison` |
| 5 | evaluation metric for action-format study | — | B1 | CodeAct Shows the Promise as a Strong Tool Use Framework | `codeact_evaluation_metric_for_action_format_study` |
| 6 | new benchmark M3ToolEval | — | B1 | Introduction | `codeact_new_benchmark_m3tooleval` |
| 7 | exact number: CodeAct vs text on M3ToolEval | +20.7pp absolute success and 2.1 fewer turns vs text actions (gpt-4-1106-preview) | B1 | CodeAct Gets More Done with Fewer Interactions | `codeact_exact_number_codeact_vs_text_on_m3tooleval` |
| 8 | open vs closed gap on M3ToolEval | — | B1 | CodeAct Gets More Done with Fewer Interactions | `codeact_open_vs_closed_gap_on_m3tooleval` |
| 9 | distinction from single-turn code generation | — | B1 | Comparison with Work that Uses Code Generation for Problem-solving | `codeact_distinction_from_single_turn_code_generation` |
| 10 | training data: CodeActInstruct | — | B1 | abstract | `codeact_training_data_codeactinstruct` |
| 11 | CodeActAgent training setup | — | B1 | CodeActAgent | `codeact_codeactagent_training_setup` |
| 12 | vs AgentInstruct/FireAct baselines | +24% / +119% relative improvement over AgentInstruct / FireAct | B1 | CodeActInstruct: Agent-Environment Interactions | `codeact_vs_agentinstruct_fireact_baselines` |
| 13 | limitation: hallucination | — | B1 | Impact Statement | `codeact_limitation_hallucination` |
| 14 | limitation/safety: sandbox escape risk | — | B1 | Impact Statement | `codeact_limitation_safety_sandbox_escape_risk` |
| 15 | limitation: LLaMA-2 anomaly on M3ToolEval | — | B1 | CodeActAgent Anomaly on M3ToolEval | `codeact_limitation_llama_2_anomaly_on_m3tooleval` |

## mechanism:typed_research_context_graph — 타입 있는 연구 컨텍스트 그래프 (B2)

### A-Mem: Agentic Memory for LLM Agents (xu2025amem, arXiv 2502.12110) — source:verified:a-mem

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | memory construction: each new memory becomes an LLM-generated structured note with contextual description, keywords, tags (plus raw content, timestamp, embed-model metadata per S3.1) | — | B2 | Abstract | `a-mem_memory_construction_each_new_memory_becomes_` |
| 2 | memory op: Link Generation - LLM analyzes candidate nearest neighbors for shared attributes and creates typed links | — | B2 | Abstract | `a-mem_memory_op_link_generation_llm_analyzes_candi` |
| 3 | memory op: Memory Evolution - after insertion, linked neighbors' context/keywords/tags are updated; evolved memory replaces the original in the store | — | B2 | 3.3 Memory Evolution | `a-mem_memory_op_memory_evolution_after_insertion_l` |
| 4 | retrieval: query embedding, cosine top-k over memory store, memories packed into prompt context | — | B2 | 3.4 Retrieve Relative Memory | `a-mem_retrieval_query_embedding_cosine_top_k_over_` |
| 5 | retrieval: linked-box closure - retrieving a memory also fetches memories linked in the same box | — | B2 | S3, Figure 1 caption | `a-mem_retrieval_linked_box_closure_retrieving_a_me` |
| 6 | measured gains on DialSim (audio-oriented F1) | A-Mem F1 3.45 vs LoCoMo 2.55 (+35%) vs MemGPT 1.18 (+192%); no MemGPT-style agentic baseline reported for LoCoMo-set audio variant | B2 | 4.4 Emprical Results (sic) | `a-mem_measured_gains_on_dialsim_audio_oriented_f1` |
| 7 | measured gains: GPT-4o/4o-mini Multi-Hop on LoCoMo | at least 2x better on Multi-Hop; GPT-4o-mini Multi-Hop F1/BLEU-1 45.85/36.67; GPT-4o 39.41/31.23 (Appx B full table) | B2 | 4.4 Emprical Results (sic) | `a-mem_measured_gains_gpt_4o_4o_mini_multi_hop_on_l` |
| 8 | failure cases: with GPT-4o/4o-mini, LoCoMo and MemGPT baselines beat A-Mem on Open Domain and Adversarial categories (simple fact retrieval) | negative for A-Mem on those categories with GPT models | B2 | 4.4 Emprical Results (sic) | `a-mem_failure_cases_with_gpt_4o_4o_mini_locomo_and` |
| 9 | cost: tokens, money, latency per memory operation | ~1,200 tokens/op and <$0.0003/op, 85-93% reduction vs baselines at ~16,900 tokens; end-to-end 5.4s (GPT-4o-mini) vs 1.1s (Llama-3.2-1B) | B2 | 4.4 Emprical Results (sic) | `a-mem_cost_tokens_money_latency_per_memory_operati` |
| 10 | scalability: retrieval latency vs memory count | retrieval 0.31us (1K notes) to 3.70us (1M notes); reported vs ReadAgent 43.62us (1K)/6,682.22us (100K) in Appx C | B2 | 4.7 Scaling Analysis | `a-mem_scalability_retrieval_latency_vs_memory_coun` |
| 11 | ablation: removing Link Generation (LG) and Memory Evolution (ME) modules | substantial degradation largest in Multi Hop and Open Domain; keeping LG+ME matters most for cross-memory reasoning | B2 | 4.5 Ablation Study | `a-mem_ablation_removing_link_generation_lg_and_mem` |
| 12 | eval design: top-k retrieval default k=10, but k adjusted per evaluation category | per-category k tuning (up to 50 for GPT-4o-mini/4o, Appx D) means tuned rows are not a fixed-config comparison | B2 | 4.2 Implementation Details | `a-mem_eval_design_top_k_retrieval_default_k_10_but` |
| 13 | eval design: bound on the per-category tuning - k left at 10 where already SOTA | — | B2 | Appendix D (More hyperparameter analysis) | `a-mem_eval_design_bound_on_the_per_category_tuning` |
| 14 | sensitivity: k in {10..50} plateaus and slightly decreases at high k | — | B2 | 4.6 Hyperparameter Analysis | `a-mem_sensitivity_k_in_10_50_plateaus_and_slightly` |
| 15 | limitation: note/link/evolution quality is bounded by the underlying LLM's capabilities | — | B2 | 6 Limitations | `a-mem_limitation_note_link_evolution_quality_is_bo` |

## mechanism:graph_engineering — 그래프 엔지니어링 (B2)

### AgentSquare: Automatic LLM Agent Search in Modular Design Space (shang2024agentsquare, arXiv 2410.06153) — source:verified:agentsquare

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | what is automated: agent architecture search over Planning/Reasoning/Tool Use/Memory modules | — | RD-90A | abstract | `agentsquare_what_is_automated_agent_architecture_search_` |
| 2 | method: module evolution + recombination search | — | RD-90A | abstract | `agentsquare_method_module_evolution_recombination_search` |
| 3 | evaluation acceleration: LLM-as-surrogate predictor for cheap screening | — | RD-90A | abstract | `agentsquare_evaluation_acceleration_llm_as_surrogate_pre` |
| 4 | headline measured gain across six benchmarks | +17.2% avg vs best-known human designs | RD-90A | abstract | `agentsquare_headline_measured_gain_across_six_benchmarks` |
| 5 | predictor cost vs full evaluation | 0.025% of full-evaluation cost | RD-90A | experiments (performance predictor) | `agentsquare_predictor_cost_vs_full_evaluation` |
| 6 | ablation: module evolution and recombination both contribute | recombination contributes more than evolution | RD-90A | experiments (ablation) | `agentsquare_ablation_module_evolution_and_recombination_` |

### Graph of Thoughts: Solving Elaborate Problems with Large Language Models (besta2024graph, arXiv 2308.09687) — source:verified:graphofthoughts

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | core argument: arbitrary-graph thought structure beyond CoT/ToT trees | — | B1-B2-T1/T2-reverify | S1 Introduction | `graphofthoughts_core_argument_arbitrary_graph_thought_struct` |
| 2 | limitation of Tree-of-Thought approaches that GoT targets | — | B1-B2-T1/T2-reverify | S1 Introduction | `graphofthoughts_limitation_of_tree_of_thought_approaches_tha` |
| 3 | mechanism: thoughts as graph vertices, dependencies as edges, enabling aggregation | — | B1-B2-T1/T2-reverify | S9 Conclusion | `graphofthoughts_mechanism_thoughts_as_graph_vertices_depende` |

### From Local to Global: A Graph RAG Approach to Query-Focused Summarization (edge2024local, arXiv 2404.16130) — source:verified:graphrag

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | GraphRAG pipeline: LLM-built two-stage graph index with entity knowledge graph and community summaries | — | B1-B2-T1/T2-reverify | abstract | `graphrag_graphrag_pipeline_llm_built_two_stage_graph_` |
| 2 | map-reduce answering over community summaries | — | B1-B2-T1/T2-reverify | S1 Introduction | `graphrag_map_reduce_answering_over_community_summarie` |
| 3 | reported outcome vs conventional RAG baseline | substantial improvements in comprehensiveness and diversity of generated answers over a conventional RAG baseline (authors' claim) | B1-B2-T1/T2-reverify | abstract | `graphrag_reported_outcome_vs_conventional_rag_baselin` |

## mechanism:loop_engineering — 반복 루프 엔지니어링 (B1/RD-90A)

### Automated Design of Agentic Systems (hu2025adas, arXiv 2408.08435) — source:verified:adas

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | what is automated: agentic system design (prompts, tool use, workflows, combinations) | — | RD-90A | abstract | `adas_what_is_automated_agentic_system_design_prom` |
| 2 | search space: agents expressed in code, discovered by a meta agent | — | RD-90A | abstract | `adas_search_space_agents_expressed_in_code_discov` |
| 3 | search-space expressiveness rationale | theoretically unbounded search space | RD-90A | abstract | `adas_search_space_expressiveness_rationale` |
| 4 | algorithm: Meta Agent Search (meta agent writes agent code conditioned on an archive) | — | RD-90A | abstract | `adas_algorithm_meta_agent_search_meta_agent_write` |
| 5 | measured gains vs state-of-the-art hand-designed baselines | +13.6 F1 DROP; +14.4% MGSM | RD-90A | Experiments (Reasoning and Problem-Solving Domains) | `adas_measured_gains_vs_state_of_the_art_hand_desi` |
| 6 | cross-domain transfer gains | +25.9% GSM8K, +13.2% GSM-Hard | RD-90A | Experiments (Generalization and transferability) | `adas_cross_domain_transfer_gains` |
| 7 | transfer claim across domains and models | — | RD-90A | abstract | `adas_transfer_claim_across_domains_and_models` |

### AFlow: Automating Agentic Workflow Generation (zhang2024aflow, arXiv 2410.10762) — source:verified:aflow

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | what is automated: agentic workflow generation as search over code-represented graphs | — | RD-90A | abstract | `aflow_what_is_automated_agentic_workflow_generatio` |
| 2 | method: MCTS with execution feedback over code workflows | — | RD-90A | abstract | `aflow_method_mcts_with_execution_feedback_over_cod` |
| 3 | headline measured gain across six benchmark datasets | +5.7% vs state-of-the-art baselines | RD-90A | abstract | `aflow_headline_measured_gain_across_six_benchmark_` |
| 4 | cost-effectiveness: smaller executors with searched workflows beat GPT-4o | GPT-4o-mini-class executors surpass GPT-4o at 4.55% cost | RD-90A | abstract | `aflow_cost_effectiveness_smaller_executors_with_se` |
| 5 | gains split by baseline type | +5.7% vs manual, +19.5% vs automated workflow generation | RD-90A | introduction (contributions) | `aflow_gains_split_by_baseline_type` |
| 6 | absolute average across six datasets | 80.3% average | RD-90A | experiments (main results, GPT-4o-mini executor) | `aflow_absolute_average_across_six_datasets` |
| 7 | transfer caveat: workflows are model-specific | negative transfer of workflows across executor models | RD-90A | experiments (workflow transfer to other models) | `aflow_transfer_caveat_workflows_are_model_specific` |

### DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines (khattab2023dspy, arXiv 2310.03714) — source:verified:dspy

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | what is automated: LM pipelines expressed as declarative text-transformation graphs | — | RD-90A | abstract | `dspy_what_is_automated_lm_pipelines_expressed_as_` |
| 2 | compiler optimizes pipelines (prompts/demonstrations) against a metric | — | RD-90A | abstract | `dspy_compiler_optimizes_pipelines_prompts_demonst` |
| 3 | self-bootstrapped pipelines vs standard few-shot prompting for GPT-3.5 and Llama2-13b-chat | >25% (GPT-3.5), >65% (Llama2-13b-chat) | RD-90A | abstract | `dspy_self_bootstrapped_pipelines_vs_standard_few_` |
| 4 | compiled open/small models (770M T5, Llama2-13b-chat) vs expert GPT-3.5 prompt chains | — | RD-90A | abstract | `dspy_compiled_open_small_models_770m_t5_llama2_13` |
| 5 | measured GSM8K gains from module composition | 4-20% -> 49-88% accuracy | RD-90A | GSM8K case study results | `dspy_measured_gsm8k_gains_from_module_composition` |
| 6 | multi-hop retrieval module wins on HotPotQA | — | RD-90A | HotPotQA case study results | `dspy_multi_hop_retrieval_module_wins_on_hotpotqa` |
| 7 | compiled 770M T5-Large multi-hop result | 39.3% answer EM, 46.0% passage accuracy (dev) | RD-90A | HotPotQA case study results | `dspy_compiled_770m_t5_large_multi_hop_result` |
| 8 | label efficiency: only final-output supervision needed | — | RD-90A | programming model / metrics | `dspy_label_efficiency_only_final_output_supervisi` |

### Self-Refine: Iterative Refinement with Self-Feedback (madaan2023selfrefine, arXiv 2303.17651) — source:verified:selfrefine

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | loop core: the same model M that generated the output provides feedback on it | — | B2 | 2 Method | `selfrefine_loop_core_the_same_model_m_that_generated_th` |
| 2 | feedback design: multi-aspect natural-language feedback that is actionable and specific, with numerical scores per aspect (S2, Fig 1) | aspect scores enable selecting a best output when quality trades off across iterations | B2 | 2 Method | `selfrefine_feedback_design_multi_aspect_natural_languag` |
| 3 | refinement prompt: appends history of prior feedback and outputs (up to 3 for most tasks) | — | B2 | 2 Method | `selfrefine_refinement_prompt_appends_history_of_prior_f` |
| 4 | stop condition: fixed timestep t, or the LLM extracts a stopping indicator from its own feedback text | — | B2 | 2 Method | `selfrefine_stop_condition_fixed_timestep_t_or_the_llm_e` |
| 5 | eval design: max 4 feedback-refine iterations; FEEDBACK and REFINE are few-shot prompts even for instruction-tuned models (ChatGPT, GPT-4) | — | B2 | 3 Evaluation | `selfrefine_eval_design_max_4_feedback_refine_iterations` |
| 6 | headline gain across 7 tasks | ~20% absolute average improvement over direct generation, no training/RL/fresh data; single LLM plays generator+feedback+refiner | B2 | Abstract | `selfrefine_headline_gain_across_7_tasks` |
| 7 | measured gain: Code Optimization (PIE, % programs optimized) with GPT-4 | 27.3 -> 36.0 (+8.7 absolute); text-davinci-003 14.8->23.0 (+8.2); gpt-3.5-turbo 23.9->27.5 (+3.6) | B2 | 3.2 Results | `selfrefine_measured_gain_code_optimization_pie_programs` |
| 8 | measured gain: Dialogue Response Generation (GPT-4 preference score) | GPT-4 25.4 -> 74.6 (+49.2); main-table deltas: sentiment reversal +21.6/+31.8/+32.4, code readability +13.9/+35.4/+28.8, acronym +14.8/+10.0/+25.6, Constrained Gen (coverage %) +9.0/+23.0/+30.0 for davinci/chatgpt/GPT-4 | B2 | 3.2 Results | `selfrefine_measured_gain_dialogue_response_generation_g` |
| 9 | range of gains over direct generation | 5-40% absolute on 7 tasks | B2 | 1 Introduction | `selfrefine_range_of_gains_over_direct_generation` |
| 10 | code-model gains | up to +13% absolute with Codex (code-davinci-002) | B2 | 1 Introduction | `selfrefine_code_model_gains` |
| 11 | failure case: math reasoning barely improves because feedback cannot detect subtle errors | GSM8K solve rate: davinci 64.1->64.1 (0), chatgpt 74.8->75.0, GPT-4 92.9->93.1 (+0.2 each); not statistically significant per Wilson-CI table | B2 | 3.2 Results | `selfrefine_failure_case_math_reasoning_barely_improves_` |
| 12 | failure mechanism on GSM: feedback says everything looks good for most instances | ChatGPT feedback reports 'everything looks good' on 94% of instances | B2 | 3.2 Results | `selfrefine_failure_mechanism_on_gsm_feedback_says_every` |
| 13 | external correctness signal substitutes for self-feedback on math | GSM with oracle feedback: davinci +4.8 (64.06->68.9), chatgpt +1.4 (74.8->76.2), GPT-4 +0.7 (92.9->93.8) | B2 | Appendix: Using Oracle Feedback | `selfrefine_external_correctness_signal_substitutes_for_` |
| 14 | failure case: weaker models cannot run the loop (cannot follow feedback/refine formats; repeats output or hallucinates) | Vicuna-13B unusable for Self-Refine with the same prompts; authors attribute to conversation-tuning vs instruction-following | B2 | 4 Analysis | `selfrefine_failure_case_weaker_models_cannot_run_the_lo` |
| 15 | ablation: Self-Refine feedback vs generic feedback vs no feedback (iterative refine only) | Code Optimization 27.5 -> 26.0 (generic) -> 24.8 (none); acronym 56.4 -> 54.0 -> 48.0 | B2 | 4 Analysis | `selfrefine_ablation_self_refine_feedback_vs_generic_fee` |
| 16 | ablation: sentiment transfer collapses without specific feedback | 43.2 -> 31.2 (generic feedback) -> 0 (no feedback) | B2 | 4 Analysis | `selfrefine_ablation_sentiment_transfer_collapses_withou` |
| 17 | failure taxonomy from 70 manually analyzed samples (35 success/35 failure; codeopt + GSM): feedback quality dominates | of failures: 33% error mislocated by feedback, 61% inappropriate fix suggested, 6% refiner implementing good feedback wrongly; in successes refiner coped with partially incorrect feedback in 33% of cases | B2 | 4 Analysis | `selfrefine_failure_taxonomy_from_70_manually_analyzed_s` |
| 18 | iteration curve: diminishing returns after early iterations (averaged over 3 base LLMs) | y0->y3: Code Opt 22.0->28.8, Sentiment Rev 33.9->36.8, Constrained Gen 29.0->49.7; most of the delta lands in y0->y1 | B2 | 4 Analysis | `selfrefine_iteration_curve_diminishing_returns_after_ea` |
| 19 | non-monotonic quality on multi-aspect tasks (e.g., acronym): one aspect improves while another declines | — | B2 | 4 Analysis | `selfrefine_non_monotonic_quality_on_multi_aspect_tasks_` |
| 20 | control: refinement vs just sampling k=4 outputs from ChatGPT (1-vs-k evaluation) | Self-Refine outputs still preferred by humans over all k=4 initial samples | B2 | 4 Analysis | `selfrefine_control_refinement_vs_just_sampling_k_4_outp` |
| 21 | eval design: blind A/B preference judged by the paper's authors, 150 examples per dataset | A-Mem-style preference rates: Sentiment Transfer 75.00% vs Direct 21.43%, Acronym 44.59% vs 12.16% (43.24% either), Response Gen 47.58% vs 19.66% | B2 | Appendix: Human Evaluation | `selfrefine_eval_design_blind_a_b_preference_judged_by_t` |
| 22 | eval design: GPT-4 used as proxy human judge for preference tasks; code readability scored by GPT-4-estimated fraction of appropriately named variables | — | B2 | 3.1 Metrics | `selfrefine_eval_design_gpt_4_used_as_proxy_human_judge_` |
| 23 | judge fidelity: GPT-4-pref vs human-pref correlation | 82% sentiment reversal, 68% acronym, 71% dialogue response | B2 | 3.1 Metrics | `selfrefine_judge_fidelity_gpt_4_pref_vs_human_pref_corr` |
| 24 | significance: Wilson CIs (99% stated in text, table caption says 95%) | nearly all GPT-4 gains significant; ChatGPT 4/7 tasks; davinci 3/7; GSM gains not significant | B2 | Appendix: Statistical Confidence Intervals | `selfrefine_significance_wilson_cis_99_stated_in_text_ta` |
| 25 | mixed-refine: small initialization model + larger feedback/refine model | GSM: Vicuna-13b 24.18% -> 40.5% with ChatGPT as feedback/refine | B2 | Appendix: Evaluation of Vicuna-13b | `selfrefine_mixed_refine_small_initialization_model_larg` |
| 26 | limitation: requires strong few-shot/instruction-following; closed models only; English-only datasets | — | B2 | 6 Limitations and Discussion | `selfrefine_limitation_requires_strong_few_shot_instruct` |

## mechanism:failclosed_research_lifecycle — fail-closed 연구 라이프사이클 (T1/T2)

### CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark (siegel2024corebench, arXiv 2409.11363) — source:verified:corebench

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | benchmark target task: computational reproducibility of published studies | — | B1-B2-T1/T2-reverify | abstract | `corebench_benchmark_target_task_computational_reproduc` |
| 2 | benchmark scale: 270 tasks, 181 task questions, three levels | — | B1-B2-T1/T2-reverify | S2 CORE-Bench: Evaluating agents on computational reproducibility | `corebench_benchmark_scale_270_tasks_181_task_questions` |
| 3 | difficulty-level design: information given to the agent | — | B1-B2-T1/T2-reverify | S2 CORE-Bench: Evaluating agents on computational reproducibility | `corebench_difficulty_level_design_information_given_to` |

### MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering (chan2024mlebench, arXiv 2410.07095) — source:verified:mlebench

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | task_source_and_count | — | T1/T2 | Abstract | `mlebench_task_source_and_count` |
| 2 | human_baselines | medal thresholds (bronze/silver/gold) derived from leaderboard percentiles | T1/T2 | Abstract | `mlebench_human_baselines` |
| 3 | main_results | pass@1 16.9%; large headroom remains | T1/T2 | Abstract | `mlebench_main_results` |
| 4 | task_construction_test_split_reconstruction | private test labels absent locally; distribution similarity checked via example-submission score parity | T1/T2 | S2.1 Dataset Curation | `mlebench_task_construction_test_split_reconstruction` |
| 5 | plagiarism_control | — | T1/T2 | S2.3 Setup | `mlebench_plagiarism_control` |
| 6 | contamination_probe_result | no systematic inflation detected; probe limited to GPT-4o | T1/T2 | S4.1 Familiarity with top solutions | `mlebench_contamination_probe_result` |
| 7 | resource_scaling_attempts | — | T1/T2 | S1 Introduction | `mlebench_resource_scaling_attempts` |
| 8 | resource_scaling_time | — | T1/T2 | S1 Introduction | `mlebench_resource_scaling_time` |
| 9 | contamination_evidence_memorization | — | T1/T2 | S6 Limitations (footnote) | `mlebench_contamination_evidence_memorization` |

### PaperBench: Evaluating AI's Ability to Replicate AI Research (starace2025paperbench, arXiv 2504.01848) — source:verified:paperbench

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | benchmark_purpose | — | T1/T2 | Abstract | `paperbench_benchmark_purpose` |
| 2 | task_source_and_construction | — | T1/T2 | Abstract | `paperbench_task_source_and_construction` |
| 3 | verifier_rubric_granularity | — | T1/T2 | S3.1 Rubrics | `paperbench_verifier_rubric_granularity` |
| 4 | verifier_rubric_granularity_cost_bound | — | T1/T2 | S3.1 Rubrics | `paperbench_verifier_rubric_granularity_cost_bound` |
| 5 | llm_judge_validation | judge F1 0.83 vs human graders; chosen for main results | T1/T2 | S4.2 Evaluating Judges with JudgeEval | `paperbench_llm_judge_validation` |
| 6 | main_results_and_human_baseline | best agent Claude 3.5 Sonnet (New); 21.0% replication score | T1/T2 | Abstract | `paperbench_main_results_and_human_baseline` |
| 7 | human_baseline_scaling | human PhD baseline crosses above best agent between 12h and 48h checkpoints | T1/T2 | S5.4 Human Baseline Performance | `paperbench_human_baseline_scaling` |
| 8 | contamination_risk_acknowledged | — | T1/T2 | S7 Limitations | `paperbench_contamination_risk_acknowledged` |
| 9 | benchmark_variant_accessibility | code development only; skips code execution for verification | T1/T2 | S2.6 PaperBench Code-Dev | `paperbench_benchmark_variant_accessibility` |

### ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery (chen2024scienceagentbench, arXiv 2410.05080) — source:verified:scienceagentbench

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | task_source_and_count | — | T1/T2 | Abstract | `scienceagentbench_task_source_and_count` |
| 2 | contamination_control_test_set_removal | guards against data loaders matching memorized download artifacts; rationale: some automatic data loaders otherwise fail success criteria | T1/T2 | S2.2 Data Collection | `scienceagentbench_contamination_control_test_set_removal` |
| 3 | contamination_control_label_hiding | — | T1/T2 | S2.2 Data Collection | `scienceagentbench_contamination_control_label_hiding` |
| 4 | verifier_design_gold_program_reproduction | — | T1/T2 | S9.2 Details about Success Criteria | `scienceagentbench_verifier_design_gold_program_reproduction` |
| 5 | verifier_design_programmatic | — | T1/T2 | S2.3 Evaluation | `scienceagentbench_verifier_design_programmatic` |
| 6 | verifier_design_llm_figure_judge | 3 GPT-4o samples averaged per figure for stability | T1/T2 | S2.3 Evaluation | `scienceagentbench_verifier_design_llm_figure_judge` |
| 7 | verifier_rubric_stages | rubrics used for human evaluation only; LLM-judge automation left as future work | T1/T2 | S2.3 Evaluation | `scienceagentbench_verifier_rubric_stages` |
| 8 | main_results | best agent Claude-3.5-Sonnet (self-debug); +1.9 points from expert knowledge | T1/T2 | Abstract | `scienceagentbench_main_results` |
| 9 | main_results_headroom | 42.2% SR at >10x cost; large headroom remains (57.8% unsolved) | T1/T2 | Abstract | `scienceagentbench_main_results_headroom` |
| 10 | license | rasterio and matminer repos identified as copyrighted; licenses cited in appendix | T1/T2 | S5 Conclusion | `scienceagentbench_license` |

## mechanism:result_driven_semantic_search — 결과 기반 의미 검색 (T1/T2)

### DiscoveryBench: Towards Data-Driven Discovery with Large Language Models (majumder2024discoverybench, arXiv 2407.01725) — source:verified:discoverybench

| # | 주장(topic) | 측정 효과 | grounds | 섹션 | locator |
|---|---|---|---|---|---|
| 1 | task_source_and_count | — | T1/T2 | Abstract | `discoverybench_task_source_and_count` |
| 2 | synthetic_task_construction | — | T1/T2 | Abstract | `discoverybench_synthetic_task_construction` |
| 3 | main_results_headroom | best system (gpt-4-preview-0125 based, Reflexion Oracle) 24.5% on real subset; large headroom | T1/T2 | Abstract | `discoverybench_main_results_headroom` |
| 4 | verifier_design_llm_alignment | outcome-based, faceted (context/variable/relation) GPT-4 judging; multiple discovery paths allowed | T1/T2 | S4.3 Evaluation | `discoverybench_verifier_design_llm_alignment` |
| 5 | contamination_probe_design | — | T1/T2 | S5.1 Discovery Agents | `discoverybench_contamination_probe_design` |
| 6 | contamination_probe_result | no strong memorization signal for GPT-4o; Llama-3 result inconclusive | T1/T2 | S5.2 Main Results | `discoverybench_contamination_probe_result` |
| 7 | license | dataset ODC-BY; code Apache 2.0 (GitHub/HF release) | T1/T2 | S7 FAQs | `discoverybench_license` |
| 8 | construction_cost | explains why real subset is small (264 tasks incl. derived variants) | T1/T2 | S4.1 \real: Collecting data-driven hypotheses in the wild | `discoverybench_construction_cost` |
| 9 | oracle_feedback_value | 24.5% vs 15.5% on real subset (Table) | T1/T2 | S5.2 Main Results | `discoverybench_oracle_feedback_value` |

