# Experimental Design: Orchestration Cost–Accuracy Trade-off

## 1. Research Question and Frame

**Question**: At what accuracy improvement threshold does multi-call orchestration (e.g., planning + refinement loops) become cost-justified compared to single-pass inference, across open-weight and closed-source model backbones?

**Sampling Frame**: 
- **Population**: Reasoning tasks from MMLU-Pro (general multi-step reasoning) and HumanEval (code synthesis), both with published difficulty annotations or baseline pass rates.
- **Unit**: Single task instance.
- **Sample size and composition**: 80 total tasks—40 from MMLU-Pro and 40 from HumanEval, stratified by difficulty quartile (10 items per quartile per benchmark). Stratification ensures accuracy and cost differences are observable across the full range of task difficulty where orchestration utility may vary.

## 2. Main Comparison and Conditions

**Primary comparison**: Single-pass inference vs. orchestrated inference (plan + execute + refine).

### Condition 1: Single-pass (Baseline)
- **Process**: Model receives task and generates response in one call.
- **Prompt**: Standard task description with any domain-specific formatting (no optimization preference, applied uniformly across all backbones).
- **Tokens consumed**: Input tokens (task + context) + output tokens (single response).

### Condition 2: Orchestrated (Treatment)
- **Process**: Model receives task → generates explicit plan or reasoning steps → refines or validates initial response based on plan.
- **Prompt**: Same base task + structured instruction requesting intermediate planning (applied uniformly).
- **Tokens consumed**: Input (task) + output (plan) + input (refined prompt referencing plan) + output (refined response), plus any auxiliary tokens for parsing or validation.

### Model Backbones Tested
1. **Claude 3.5 Sonnet** (closed-source, Anthropic API; verified cost via anthropic.com pricing).
2. **GPT-4o** (closed-source, OpenAI API; verified cost via openai.com pricing).
3. **Llama 3.1-70B** (open-weight, HF transformers or vLLM; inferred cost via token counts and vLLM throughput, no per-call API charge).
4. **Mistral Large 2** (available via Mistral API or open-weight; tested via Mistral's API with published pricing).

## 3. Ablation: Orchestration Depth

**Purpose**: Determine whether 2-step orchestration (plan + refine) is more cost-effective than single-pass, and whether adding a third step (verify/second refine) improves accuracy enough to warrant additional cost.

**Ablation conditions**:
- **Depth=1**: Single-pass (same as Condition 1).
- **Depth=2**: Plan + Refine (same as Condition 2).
- **Depth=3**: Plan + Execute + Verify (model generates plan, attempts solution, then checks against plan and makes final refinement).

This ablation isolates whether additional orchestration steps reduce cost-per-point-accuracy or plateau.

## 4. Outcome Metrics

### Primary Metrics
1. **Accuracy**: Fraction of tasks on which the model's final response is correct.
   - For MMLU-Pro: match against official answer key (multiple choice → exact match).
   - For HumanEval: pass@1 (does the generated code pass all test cases?).

2. **Token Cost**: Total tokens consumed (input + output) × per-token rate.
   - For API models: tokens × official published rate.
   - For open-weight models: tokens × estimated marginal cost (e.g., vLLM GPU hours / tokens generated).

3. **Cost-per-accuracy-point**: Token cost ÷ accuracy (or as a function of accuracy, e.g., "token cost required to reach 80% accuracy").

### Secondary Metrics
1. **Inference time** (where available from API responses or measured on vLLM).
2. **Confidence interval width** on accuracy (95% CI, computed via Clopper-Pearson binomial intervals per condition/backbone).
3. **Cost variance**: Standard deviation of token consumption across items (some tasks may require more refinement).

## 5. Analysis Plan

### Main Analysis
For each backbone:
1. Compute accuracy and token cost for each item under Condition 1 (single-pass) and Condition 2 (orchestrated).
2. Calculate delta accuracy (orchestrated − single-pass) and delta cost (orchestrated − single-pass).
3. Report by difficulty quartile: accuracy, cost, and Δ both within stratification groups and across all 40 items.

### Visualization
- **Scatter plot**: X-axis = delta cost, Y-axis = delta accuracy, one point per backbone, faceted by benchmark.
- **Table**: Accuracy and token cost by condition, backbone, benchmark, and difficulty quartile.
- **Cost-sensitivity curve**: Plot accuracy achieved vs. token budget (e.g., "at 3× single-pass cost, what accuracy is achieved?") for each backbone.

### Statistical Test
Paired comparison (within backbone, within benchmark):
- **Null hypothesis**: Orchestrated accuracy − Single-pass accuracy = 0.
- **Test**: McNemar's test (for binary correctness) or paired t-test on per-item token consumption.
- **Interpretation**: Report p-value and 95% CI on delta for each backbone/benchmark pair.

### Threshold Analysis (Core Question)
For each backbone:
1. Identify the accuracy improvement (Δ) achieved by orchestration.
2. Identify the token cost multiplier (orchestration cost / single-pass cost).
3. Evaluate: Is Δ accuracy large enough (relative to cost multiplier) to justify orchestration?
   - **Decision rule**: If Δ accuracy > 5 percentage points *and* cost multiplier < 2.5, orchestration is justified.
   - **Report**: For each backbone/benchmark, state whether orchestration meets this threshold.

### Ablation Analysis
Compare Depth=1, 2, 3 using the same metrics. Rank by cost-effectiveness (accuracy gain per token).

## 6. Resources and Implementation

### Datasets
- **MMLU-Pro**: 12,332 items with difficulty tags; obtain via Hugging Face `mmlu-pro` dataset (https://huggingface.co/datasets/MMLU-Pro/MMLU-Pro). Sample 40 items stratified by published difficulty.
- **HumanEval**: 164 coding problems; obtain via Hugging Face `openai_humaneval` dataset or OpenAI's canonical fork. Sample 40 items stratified by baseline pass rate.

### Models
- **Claude 3.5 Sonnet**: Via Anthropic API (requires API key; cost per token: $3/million input, $15/million output tokens as of 2025).
- **GPT-4o**: Via OpenAI API (cost: $5/million input, $15/million output tokens as of 2025).
- **Llama 3.1-70B**: Run locally via vLLM (requires GPU; estimated cost ~$0.70/million tokens on A100 GPU at ~150 tokens/sec).
- **Mistral Large 2**: Via Mistral API (cost: $2/million input, $6/million output tokens as of 2025).

### Automation
- **Evaluation harness**: Python script using `anthropic`, `openai`, and `transformers` libraries to:
  - Load sampled items from HF datasets.
  - Run each item through each condition (single-pass, orchestrated) for each backbone.
  - Parse responses and compare to ground truth.
  - Log tokens consumed and cost.
  - Generate tables and plots.

## 7. Uncertainty Quantification

### Confidence Intervals
Report 95% Clopper-Pearson binomial CI on accuracy for each condition, backbone, and benchmark.

### Variance Analysis
Report standard error of cost (token consumption) per condition, accounting for variability across items.

### Sensitivity Analysis
For the main decision rule ("orchestration justified if Δ accuracy > 5% and cost < 2.5×"):
- Re-run analysis with thresholds varied to ±2 percentage points and ±0.5× cost multiplier.
- Report how conclusions change if thresholds shift (e.g., "justified under thresholds 3–7% accuracy and 2–3× cost").

### Stratified Reporting
Accuracy and cost metrics are reported separately for each difficulty quartile, allowing readers to assess whether conclusions hold across task difficulty.

## 8. Design Rationale and Limitations

### Why These Benchmarks?
- **MMLU-Pro** represents broad reasoning across knowledge domains.
- **HumanEval** isolates code synthesis, a task where multi-step reasoning (plan-then-code) is known to help.
- Together, they span reasoning and generation tasks, broadening the inference beyond either alone.

### Why These Backbones?
- **Claude 3.5 Sonnet** and **GPT-4o** are representative closed-source, frontier models with known cost structures.
- **Llama 3.1-70B** and **Mistral Large 2** represent deployable open-weight and API-accessible alternatives.

### Limitations (Cannot Verify or Control)
1. **Prompt sensitivity**: Single-pass and orchestrated prompts may have unequal "room to improve" if one is more awkwardly phrased; mitigated by uniform prompt templates, but optimal prompts per strategy would differ.
2. **Orchestration strategy**: The design fixes a simple (plan + refine) strategy; other orchestration methods (e.g., multi-agent debate, chain-of-thought variants) may have different cost–accuracy profiles. This design is specific to the named strategy.
3. **Inference infrastructure**: Actual cost and latency depend on deployment (API calls vs. local GPU). Design uses published rates and vLLM benchmarks, which are stable but may not reflect production load.
4. **Generalization beyond sampled benchmarks**: Results may not transfer to domains (e.g., long-form writing, retrieval-augmented generation) beyond MMLU-Pro and HumanEval.

## 9. Deliverables

1. **Accuracy and cost tables** by condition, backbone, benchmark, and difficulty quartile.
2. **Cost–accuracy scatter plots** and sensitivity curves.
3. **Statistical tests** (McNemar/paired t-test) with p-values and 95% CIs.
4. **Threshold analysis summary**: For each backbone, state whether orchestration meets the decision rule and what the cost–accuracy trade-off implies.
5. **Ablation results**: Cost-effectiveness ranking of Depth=1, 2, 3.
6. **Code and reproducibility log**: Scripts to rerun the full pipeline, logged token counts and costs, sampled item IDs for auditability.

## 10. Success Criteria (Falsifier)

The design is refuted if:
- Single-pass inference achieves >98% of orchestrated accuracy *and* costs <1.5× the token budget of orchestrated inference across both benchmarks and all four model backbones.

If this criterion is not met, orchestration is cost-justified (under the sampled frame), and the design will quantify the threshold at which cost-effectiveness breaks down by difficulty or backbone.
