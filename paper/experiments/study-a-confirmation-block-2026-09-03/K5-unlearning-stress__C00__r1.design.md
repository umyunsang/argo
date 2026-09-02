# Experimental Design: Detecting Unlearning vs. Knowledge Suppression

## Research Question
Given a model that has undergone an unlearning procedure, can we establish whether knowledge has been truly removed from the model's parameters versus merely hidden from ordinary queries through output filtering, refusal mechanisms, or distribution shift?

## Scientific Hypothesis
An unlearning procedure may produce one of three outcomes:
1. **True Unlearning**: Knowledge is removed from model weights; accuracy drops across all query methods.
2. **Masked Learning**: Knowledge remains encoded but is suppressed by output filters or refusal mechanisms; accuracy drops on direct queries but recovers under adversarial/indirect prompting.
3. **Distribution Shift**: The model's response distribution has shifted but underlying capabilities remain accessible; accuracy recovers through paraphrasing or alternative access patterns.

## Experimental Design Overview

### Main Comparison: Baseline vs. Unlearned Conditions

**Factor 1: Model Version**
- Control: Baseline model (unmodified, or model before unlearning)
- Treatment: Model after unlearning procedure (test multiple procedures if available)

**Factor 2: Query Method (Access Probing)**
- Standard direct queries
- Paraphrased indirect queries
- Multiple-choice format
- Jailbreak/adversarial prompts
- Reasoning-chain prompts
- Comparative questions
- Out-of-distribution rewording
- Encoded/obfuscated queries
- Token-level completion tasks

### Conditions (Factorial Design)

**Main Experimental Conditions:**
1. Baseline + Direct Query
2. Baseline + Paraphrased Query
3. Baseline + Multiple-Choice
4. Baseline + Adversarial Prompt
5. Unlearned Model + Direct Query
6. Unlearned Model + Paraphrased Query
7. Unlearned Model + Multiple-Choice
8. Unlearned Model + Adversarial Prompt
9. Unlearned Model + Reasoning-Chain Query

**Cross-Cutting Factor: Target Knowledge Domain**
Test across multiple knowledge categories to detect domain-specific effects:
- Factual knowledge (specific dates, names, places)
- Conceptual knowledge (relationships, definitions)
- Procedural knowledge (how-to information)
- Semantic associations
- Implicit knowledge (can be inferred but was not directly taught)

### Ablation Studies

**Ablation 1: Prompt Engineering Intensity**
- Minimal prompt (one-shot, direct)
- Medium prompt (few-shot examples, contextual framing)
- Heavy prompt (extensive reasoning, analogies, system role-play)
- Hypothesis: True unlearning should show no improvement; masked learning should show increasing recovery with intensive prompting.

**Ablation 2: Model Confidence vs. Accuracy**
- Track both *whether* the model answers and *how correct* it is
- Hypothesis: Masked learning shows refusal patterns on direct queries but correct answers when forced to respond.

**Ablation 3: Unlearning Procedure Comparison**
- If multiple procedures are available, compare procedures against each other
- Hypothesis: Different procedures have different susceptibility to adversarial probing.

**Ablation 4: Knowledge Specificity**
- Test granular knowledge components vs. holistic concepts
- Example: if procedure targets "specific event E", test knowledge of E, components of E, consequences of E, related events
- Hypothesis: True unlearning affects all related knowledge; suppression-based approaches show selective gaps.

### Measurement Approach

#### Primary Metrics

**1. Knowledge Recall Accuracy**
- Metric: Fraction of correct answers per condition
- Computation: 
  - For direct factual queries: exact match or semantic equivalence (human or LLM-as-judge)
  - For multiple-choice: accuracy on forced-choice
  - For reasoning chains: quality score on whether reasoning demonstrates retained knowledge

**2. Recovery Index**
- Metric: Improvement in accuracy from direct query to best adversarial query
- Formula: `Recovery_Index = (Accuracy_Adversarial - Accuracy_Direct) / Accuracy_Direct`
- Interpretation:
  - Recovery_Index ≈ 0: suggests true unlearning (no hidden knowledge to recover)
  - Recovery_Index > 0.3: suggests masked learning (significant recovery under pressure)

**3. Confidence Mismatch Score**
- Metric: Divergence between model confidence (log-probabilities) and actual accuracy
- Computation: For each response, extract log-probabilities of generated tokens; compare to correctness
- Hypothesis: Masked models show high confidence on refused answers; truly unlearned models show low confidence uniformly

**4. Knowledge Component Degradation Profile**
- Metric: Accuracy across related knowledge components
- Computation: Organize test questions into knowledge graphs; measure which components degrade together
- Interpretation: Uniform degradation suggests true unlearning; selective degradation suggests targeted suppression

#### Secondary Metrics

**5. Latency and Refusal Rate**
- Metric: Time to generate response; frequency of explicit refusals
- Hypothesis: Masked learning shows higher refusal rate and latency on direct queries

**6. Semantic Similarity to Baseline Responses**
- Metric: BLEU, BERTScore, or embedding-space cosine similarity of model responses between baseline and unlearned versions
- Hypothesis: True unlearning produces distinct response distributions; masked learning produces similar response semantics with added refusals

**7. Transferability Test**
- Metric: Can knowledge from unlearned model be extracted to construct the original knowledge?
- Hypothesis: Masked learning allows reconstruction; true unlearning makes reconstruction impossible

### Analysis Plan

#### Step 1: Descriptive Analysis
- Report accuracy tables: rows = model version, columns = query method, cells = accuracy ± 95% CI
- Report response latencies and refusal rates by condition
- Visualize recovery index distributions

#### Step 2: Hypothesis Testing
- **Test A: Main Effect of Model Version**
  - Null: Accuracy is the same between baseline and unlearned
  - Method: Paired t-test or Wilcoxon signed-rank test across all query methods
  
- **Test B: Interaction Effect (Model × Query Method)**
  - Null: Query method effect is independent of model version
  - Method: Two-way ANOVA or mixed-effects model with random intercept per knowledge domain
  
- **Test C: Recovery Pattern Significance**
  - Null: Recovery Index is not significantly > 0
  - Method: One-sample t-test on recovery indices, with Benjamini-Hochberg FDR correction across knowledge domains

#### Step 3: Pattern Classification
- Fit a simple decision tree or rule-based classifier to assign each model to a category:
  - **True Unlearning**: Accuracy drops uniformly (>80% drop across methods), Recovery Index ≈ 0
  - **Masked Learning**: Accuracy recovers substantially (Recovery Index > 0.3), high refusal rates on direct queries
  - **Distribution Shift**: Moderate recovery (0 < Recovery Index < 0.3), no high refusal rates, but response semantics diverge from baseline

#### Step 4: Uncertainty Quantification
- Report 95% confidence intervals on all accuracy estimates (binomial proportion CI)
- Perform bootstrap resampling (n=1000) on recovery indices to estimate standard error
- Conduct sensitivity analysis: recalculate key metrics under different human annotation criteria for correctness

### Concrete Resources

#### 1. Models Required
- **Baseline Model**: Publicly available LLM (e.g., Llama 2, Mistral, Phi, or equivalent)
- **Unlearned Variant(s)**: Model(s) output by unlearning procedure(s) targeting specific knowledge
  - If multiple procedures available, test 2-3 variants
  - Procedure examples: SISA, machine unlearning, targeted prompt masking, weight pruning-based unlearning

#### 2. Test Dataset Construction
- **Source**: Collect ~200-500 questions across the targeted knowledge domain
- **Design**: 
  - Stratify by knowledge type: factual (40%), conceptual (30%), procedural (20%), implicit (10%)
  - Obtain human consensus labels for correct answers (2+ annotators, Cohen's κ > 0.75)
  - For each base question, generate 3-5 variants: paraphrase, multiple-choice (4 options), adversarial, reasoning-chain prompts
  - Ensure variants test the same underlying knowledge, not different knowledge

#### 3. Evaluation Infrastructure
- **Inference API or Local Deployment**: Ability to query models with controlled sampling (temperature, top-p)
- **Scoring System**: 
  - Automated scoring for multiple-choice (exact match)
  - LLM-as-judge for open-ended answers (use reference model, e.g., GPT-4, with predefined rubric)
  - Human spot-check of ~50 disagreements between automated and human judges
- **Logging**: Record all queries, raw model outputs, logits/probabilities, latency, confidence metrics

#### 4. Compute Requirements
- ~2-4 hours GPU time (if using local inference) or API credits for ~10,000 model queries
- Storage: ~100 MB for raw results, processed datasets, logs
- Analysis tooling: Python (scikit-learn, scipy, pandas), optional: R for statistical tests

### Outcome Metrics Summary

| Metric | Threshold for True Unlearning | Threshold for Masked Learning | Measurement Method |
|--------|-------------------------------|-------------------------------|-------------------|
| Overall Accuracy Drop | > 80% | 20-50% | Paired t-test |
| Recovery Index | < 0.10 | > 0.30 | Bootstrap CI |
| Refusal Rate on Direct | Similar to baseline | > 50% higher than baseline | Proportion test |
| Knowledge Component Consistency | Uniform degradation | Selective gaps | Correlation of component scores |
| Confidence-Accuracy Correlation | Weakly negative (refusal signals non-knowledge) | Positive on refused answers | Spearman ρ |
| Response Semantic Similarity | Low (< 0.6 BERTScore) | High (> 0.8 BERTScore) | Embedding comparison |

### Uncertainty Quantification Strategy

1. **Confidence Intervals**: Report 95% binomial CIs on all accuracy estimates using Clopper-Pearson method
2. **Bootstrap Resampling**: Resample test questions (with replacement) n=1000 times; report bootstrap SE and percentile CIs on recovery indices
3. **Sensitivity Analysis**:
   - Vary human evaluation criteria (strict vs. lenient correctness judgment)
   - Remove outlier query methods; recalculate metrics
   - Subgroup analysis by knowledge domain and specificity
4. **Power Analysis**: Pre-register expected effect size (e.g., 40% accuracy drop) and desired power (0.80); report achieved power post-hoc
5. **Multiple Comparisons Correction**: Apply Benjamini-Hochberg FDR correction (α = 0.05) across all hypothesis tests

### Expected Outcomes

**Scenario A: True Unlearning**
- Accuracy collapses uniformly (>70% drop) across direct, paraphrased, and adversarial queries
- Recovery Index ≈ 0 ± 0.05
- Refusal rates similar to baseline
- Response semantics diverge significantly
- Conclusion: Knowledge is removed; no evidence of hidden recovery pathways

**Scenario B: Masked Learning**
- Accuracy drops 30-50% on direct queries but recovers 40-70% under adversarial prompting
- Recovery Index > 0.30
- High refusal rates on direct queries; lower on indirect
- Response semantics remain similar to baseline
- Conclusion: Knowledge is suppressed by output filter; still accessible to adversarial queries

**Scenario C: Distribution Shift**
- Moderate accuracy drop (20-40%) that persists across query methods
- Recovery Index 0.10-0.25
- Low refusal rates; different response patterns (e.g., hedging, disclaimers)
- Partial semantic divergence from baseline
- Conclusion: Model's capability has shifted; unlearning is incomplete or unstable

### Reproducibility & Documentation

- **Pre-registration**: Protocol registered prior to data collection (e.g., OSF)
- **Code & Data Availability**: Release evaluation code, test dataset (with license), and results on GitHub
- **Ablation Notebook**: Interactive Jupyter notebook showing sensitivity analyses
- **Failure Case Documentation**: Record and analyze unexpected results, edge cases
- **Replication Notes**: Document exact model versions, API parameters, hardware, and random seeds

---

## Timeline & Checkpoints

1. **Week 1**: Dataset construction, baseline data collection, annotation agreement validation
2. **Week 2**: Unlearned model testing, adversarial query generation, result aggregation
3. **Week 3**: Analysis, statistical testing, sensitivity checks, report writing
4. **Week 4**: Ablation studies, documentation, artifact release

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM-as-judge correlation with human judges is low | Include human spot-check, use multiple reference models, establish rubric inter-rater agreement first |
| Unlearning procedure is unstable across runs | Test multiple model checkpoints if available; average results if procedure is stochastic |
| Query method variance exceeds model version effects | Use stratified sampling by domain; apply mixed-effects model to account for query method variance |
| Insufficient test set size for high-confidence estimates | Start with conservative sample size (~300 questions); conduct power analysis and expand if needed |
| Knowledge domain definition is ambiguous | Pilot test on small sample; establish clear scope and get annotator agreement before full evaluation |

