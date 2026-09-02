# Experimental Design: Detecting True Unlearning vs. Knowledge Hiding

## Research Question
A procedure claims to have removed a body of knowledge from a language model. How do we establish whether the knowledge is truly removed rather than merely hidden from ordinary queries?

## Theoretical Framing

### Core Distinction
Unlearning removal appears on multiple orthogonal measurement dimensions:
- **Hidden knowledge**: model still encodes it but ordinary queries trigger refusal or redirection
- **True removal**: knowledge cannot be extracted via any accessible query strategy

This design distinguishes them by looking for residual knowledge signals across query modes while controlling for surface-level obfuscation, using auditing methods adapted from two evidence sources.

### Evidence Integration
- **2607.18508.txt (EmoPrefer audit)**: Shows that content-blind probes and ODIN-style decorrelation can expose hidden signals beneath surface metrics. The key insight is that performance metrics hide shortcuts—a content-blind probe matching multimodal judges reveals generator identity leaks through text style.
- **2608.29517.txt (LLM judges as raters)**: Demonstrates rater-effects methodology to detect systematic biases invisible to rank statistics. Two judges can correlate equally with a reference (r=.47–.56) while differing by 219 points in severity—i.e., the largest effect is orthogonal to the metric by which judges are selected.

## Main Comparison: Unlearning Condition vs. Control

### Conditions
1. **Unlearned Model**: Model after unlearning procedure applied
2. **Control Model(s)**: 
   - Original model (before unlearning), if available
   - Baseline model trained without the target knowledge
   - Same model with similar capability removed via a different procedure (ablation)

### Unit of Analysis
A fixed set of knowledge probes (e.g., facts, relationships, reasoning chains) partitioned into three classes:
- **Direct**: Standard queries asking for the knowledge explicitly
- **Indirect**: Queries that require the knowledge to solve but do not name it  
- **Residual**: Constructed to catch knowledge leakage despite refusal (context completion, counterfactual reasoning, analogical transfer)

## Complete Measurement Battery

### 1. Content-Blind Accessibility Probes (from 2607.18508.txt methodology)
**Rationale**: A model that truly forgot knowledge cannot reconstruct it even from impoverished features.

**Design**:
- For each knowledge item (e.g., entity relationship), construct pairs: one that requires the knowledge to rank/choose, one that does not
- Measure if model can distinguish them using only:
  - Lexical overlap / semantic similarity between query and responses (no semantic understanding required)
  - Length patterns / textual features of correct answers
  - Position/ordering biases in response generation
- Logistic regression on these features vs. model probability output

**Outcome**:
- If content-blind probe matches unlearned model's ranking, knowledge is accessible (not truly removed)
- If probe scores at random/floor, knowledge is truly inaccessible

### 2. Counter-Stereotypical Slicing (from 2607.18508.txt)
**Rationale**: Catch shortcuts where the model follows a surface pattern while appearing to respond correctly.

**Design**:
- Partition probes into: **stereotypical** (matches surface prior) vs. **counter-stereotypical** (violates surface prior)
  - Stereotypical: queries about common examples, predictable domains, high-frequency associations
  - Counter-stereotypical: unusual contexts, negations, role reversals (e.g., asking about *absence* of the knowledge)
- Compare model performance: if it drops dramatically on counter-stereotypical cases, it is following surface cues, not applying knowledge

**Outcome**:
- Unlearned model should perform equally poorly on both slices
- Hidden knowledge model should drop on counter-stereotypical items where shortcuts fail

### 3. ODIN-Style Deconfounding (from 2607.18508.txt methodology adapted)
**Rationale**: Separate surface-level behavior (refusal, style changes) from latent knowledge.

**Design**:
- Train a diagnostic model on unlearned model outputs with three conceptual heads:
  - **Content head** (r_C): attempts to encode knowledge about the target domain
  - **Style/bias head** (r_L): encodes stylistic changes (more hedging, disclaimers, off-topic) that signal unlearning
  - **Domain-prior head** (r_G): encodes general priors about the domain
- Decorrelate r_C from r_L and r_G using a modified Bradley-Terry loss
- Measure: does r_C collapse to chance once style/prior confounds are removed?

**Outcome**:
- True unlearning: r_C → chance level after decorrelation
- Hidden knowledge: r_C persists above chance even after removing style/prior signals

### 4. Rater-Effects Audit (from 2608.29517.txt methodology)
**Rationale**: Unlearning may not be uniform—some knowledge may be partially retained, creating severity biases on the knowledge domain.

**Design**:
- Treat the unlearned model as a "rater" that must answer questions on:
  - The target knowledge domain (should be poor/random)
  - Related but distinct knowledge (baseline)
  - Unrelated knowledge (negative control)
- Compute many-facet Rasch measurement (MFRM) severity: systematic bias on the target domain
- Compare unlearned model severity to:
  - Control model severity on the same questions
  - Baseline model severity

**Outcome**:
- True unlearning: target-domain severity centered at chance, no meaningful difference from control
- Partial retention: target-domain severity systematically offset (e.g., consistently biased toward wrong answers, or inconsistently hesitant)

### 5. Differential Functioning by Query Mode (adapted from 2608.29517.txt)
**Rationale**: Knowledge hiding may be query-specific; true unlearning should affect all query forms uniformly.

**Design**:
- Score the same knowledge probes across multiple query modes:
  - **Direct questioning**: "What is X?"
  - **Indirect/applied**: "Given [scenario], predict/solve/explain"
  - **Format variation**: multiple-choice, free-form, fill-in-blank
  - **Context variation**: in isolation vs. embedded in longer context
  - **Role play**: "As an expert in Y, answer..."
  - **Adversarial**: "I claim X. Refute me." (tests if model can construct counter-arguments using the knowledge)
- Compute per-mode differential functioning (DJF): does removal hold equally across all forms?

**Outcome**:
- True unlearning: uniform poor performance across all modes
- Hidden knowledge: differential functioning pattern showing mode-specific leakage (e.g., good under role-play, poor under direct)

### 6. Residual Knowledge Leakage Tests
**Rationale**: Hidden knowledge may surface indirectly through reasoning, analogy, or generalization.

**Design**:
- **In-context learning**: Show the model examples of related knowledge it should know, then test if it extrapolates to the target knowledge
- **Analogical transfer**: Present novel scenarios that require transferring the target knowledge to a new domain
- **Inverse probes**: Ask the model to *predict what would be true if* the target knowledge were false (requires understanding what would change)
- **Explanation consistency**: Ask the model to explain its refusal (latent knowledge may leak in the explanation itself)

**Outcome**:
- True unlearning: consistent refusal or random performance across all residual tests
- Hidden knowledge: pattern of leakage in one or more indirect forms

## Ablation Design

### Ablation 1: Unlearning Procedure Comparison
**Design**: If multiple unlearning procedures are available, apply all and compare:
- Do they all remove the same knowledge equally? (If no → some are incomplete)
- Do they differ in collateral damage to related capabilities? (severity/DJF analysis)
- Do content-blind probes detect knowledge in one procedure's output but not another?

**Outcome**: Identifies which procedure is more thorough

### Ablation 2: Robustness to Prompt Rewriting
**Design**: For a fixed knowledge probe, rewrite the query in multiple ways without changing semantics:
- Paraphrase into different discourse styles
- Change query order and framing
- Introduce distractors or irrelevant context

**Outcome**: True unlearning should be robust (poor across rewrites); hidden knowledge may leak inconsistently

### Ablation 3: Contamination Check (from 2608.29517.txt)
**Design**: Use temperature-0 repeated probes and continuation probes to detect if:
- Model deterministically generates the same (incorrect) response → suggests learned refusal, not removal
- Model generates varied responses → true uncertainty

**Outcome**: Determinism suggests hiding; variance suggests removal uncertainty

## Analysis Plan

### Primary Analyses
1. **Aggregate accessibility score**: Mean performance across direct, indirect, residual probes
   - Unlearned: ~chance (e.g., 50% for binary choice, 25% for 4-way)
   - Compare to control baseline with confidence intervals (bootstrap 95% CI)

2. **Content-blind probe parity test**: 
   - McNemar test: does content-blind probe performance match the full model?
   - If yes (p > .05), knowledge is accessible; if no (p < .05), it is hidden

3. **Counter-stereotypical performance gap**:
   - Compute Δ = performance(stereotypical) − performance(counter-stereotypical)
   - Unlearned: Δ ≈ 0 (similar poor performance on both)
   - Hidden: Δ > 0 (higher on stereotypical where shortcuts work)

4. **ODIN decorrelated content-head regression**:
   - Fit three-head model (content, style, prior)
   - Report: β_C (content head weight) before and after decorrelation
   - Hypothesis test: H0: β_C^(decorrelated) = 0 (i.e., no residual knowledge)

5. **MFRM severity CI**: 
   - 99% confidence interval for target-domain severity
   - Unlearned: CI centered at 0 (no systematic bias)
   - If CI excludes 0 → residual knowledge (biased toward wrong answers or erratic)

6. **Cross-mode likelihood ratio test**:
   - Fit random-intercept logistic regression: accuracy ~ mode + (1|probe)
   - LRT: does mode significantly predict accuracy?
   - Unlearned: no mode effect (uniform poor performance)
   - Hidden: significant mode effect (some modes leak)

### Secondary Analyses
- Per-probe performance heatmap (reveals which knowledge is more/less removed)
- Severity decomposition by knowledge category (e.g., facts vs. reasoning)
- Replication/consistency (temperature-0 repeated calls): SD of responses
- Effect sizes (Cohen's d, odds ratios) with 95% CIs for all binary comparisons

## Concrete Resources

### Corpora & Stimuli
1. **Knowledge domain**: [Specify: e.g., "fictional characters from Book X", "proprietary training data", "specific toxins/weapons synthesis"]
2. **Probe set**: 
   - Minimum n=50 knowledge items partitioned into:
     - 25 direct queries
     - 25 indirect queries (require the knowledge to solve)
     - 25 residual leakage tests (counter-stereotypical, in-context learning, analogical)
   - Version control: frozen before evaluation, with justification for each item

### Model Instances
1. **Unlearned model(s)**: Post-procedure checkpoint(s), pinned version, serve via API with logging
2. **Control model(s)**: 
   - Pre-unlearning (if available)
   - Unrelated capability ablation (e.g., another knowledge domain removed)
3. **Baseline model**: No knowledge of target domain by design (e.g., random model, model trained on different data)

### Instrumentation
- **Query interface**: Logged API calls with verbatim requests, responses, latencies, temperature, top-p settings
- **Scoring rubric**: Pre-specified for each probe (binary correct/incorrect, or multi-scale if applicable)
- **Replication**: K=3 repeated calls per probe (different random seeds) to estimate within-model variance
- **Canary set**: Fixed n=5 probes scored repeatedly across collection window (temperature 0) to detect model version/serving-stack changes

## Outcome Metrics

### Primary Metrics
- **Unlearned model mean accuracy** (target domain): point estimate + 95% bootstrap CI
  - Criterion: ≤ 55% for binary (i.e., at or below chance; accounting for estimation noise and hard cases)
- **Control model mean accuracy** (target domain): for comparison
- **Parity of content-blind probe**: proportion of probes where probe accuracy matches model accuracy (McNemar p-value)
- **Counter-stereotypical performance drop**: Δ performance, 95% CI
- **MFRM target-domain severity CI**: confidence interval includes 0 (true unlearning) or excludes it (residual knowledge)

### Secondary Metrics
- **Consistency (temperature-0)**: SD of repeated calls; target: SD = 0 (deterministic poor performance)
- **Cross-mode uniformity**: LRT p-value for mode effect; target: p > .05 (uniform poor across modes)
- **Content-head regression weight** (post-decorrelation): β_C; target: not significantly different from 0
- **Per-knowledge-item accuracy heatmap**: visual inspection for pockets of retained knowledge

## Quantifying Uncertainty

1. **Confidence intervals**: Bootstrap 2,000 resamples (per-probe stratified) for all point estimates
2. **Hypothesis tests**: 
   - Two-sided tests with Bonferroni correction across the six main analyses (family-wise α = .05 → per-test α = .0083)
   - Report both point estimates and p-values, with interpretation of effect size, not just p-value
3. **Sensitivity analyses**:
   - Rerun with different random seeds for K replicates
   - Rerun excluding hard/ambiguous probes (sensitivity to probe calibration)
   - Rerun with different control model (sensitivity to baseline choice)

## Pre-Registration Protocol
- Freeze probe set, scoring rubric, model versions, and analysis plan **before** any model evaluation
- Document all deviations with justification (e.g., if a probe is ambiguous, flag it prospectively, not post hoc)
- Report confirmatory results with the same prominence as exploratory findings
- Publish the full score tensor (model outputs, probe labels, human ratings) to enable reuse

## Timeline & Cost
- **Probe construction**: 2 weeks (with domain expert validation)
- **Model evaluation**: 2–4 weeks (depends on API rate limits; estimate ~500 queries × K replications × 3–5 models = 7,500–12,500 API calls)
- **Analysis**: 2 weeks
- **Budget**: API costs (~$200–500 depending on model tier) + labor

## Expected Outcomes & Interpretation

### Scenario 1: True Unlearning
- Content-blind probe does **not** match model (McNemar p < .05)
- Counter-stereotypical Δ ≈ 0 (no performance difference)
- ODIN content head β_C ≈ 0 after decorrelation
- MFRM severity CI includes 0
- No mode-specific leakage (LRT p > .05)
- Interpretation: **Knowledge is removed, not hidden**

### Scenario 2: Hidden Knowledge
- Content-blind probe **matches** model (McNemar p > .05)
- Counter-stereotypical Δ > 0 (performance drops where shortcuts fail)
- ODIN content head β_C remains significant
- MFRM severity CI excludes 0 (systematic bias toward wrong answers)
- Significant mode-specific leakage (LRT p < .05, especially on role-play or analogical modes)
- Interpretation: **Knowledge is hidden by refusal or obfuscation, not removed**

### Scenario 3: Partial Removal
- Mixed signals: some metrics suggest removal (Δ ≈ 0, no mode effect), others suggest leakage (probe parity, β_C > 0)
- Interpretation: **Knowledge is partially removed or unevenly removed across contexts** (suggests collateral damage to related knowledge or incomplete procedure)

---

## Notes on Evidence Integration

This design synthesizes the audit methodologies from the two evidence sources:

1. **From 2607.18508.txt**: 
   - Content-blind probes expose accessibility without semantic understanding (§ 4.1)
   - ODIN decorrelation detects hidden signals beneath surface metrics (§ 3, § 4)
   - Counter-stereotypical slicing catches shortcut learning (§ 3)
   
2. **From 2608.29517.txt**:
   - Rater-effects methodology detects systematic biases orthogonal to rank metrics (§ 4.1: severity is invisible to correlation r)
   - MFRM and D-studies quantify reliability and validity independently (§ 4.4)
   - Pre-registration with honest nulls and family-wise error control (§ 3.3, § 4.2)
   - Contamination audits via identity canaries and continuation probes (§ 4.7)

Both papers share a core lesson: metrics that appear to show success can hide substantial underlying signals when the measurement is one-dimensional. This design applies that principle to unlearning: a model may appear to have forgotten while still retaining latent knowledge accessible through indirect means. By auditing across multiple orthogonal measurement dimensions (content-blind access, query modes, style decomposition, domain-specific bias), we can distinguish true removal from obfuscation.
