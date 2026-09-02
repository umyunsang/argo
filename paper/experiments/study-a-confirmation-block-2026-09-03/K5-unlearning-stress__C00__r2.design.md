# Experimental Design: Detecting True Knowledge Removal in Unlearned Language Models

## 1. Research Question

**Primary question:** When a procedure claims to remove a body of knowledge from a language model, how can we reliably distinguish between true removal and knowledge hiding (inhibition, suppression, or obfuscation)?

**Null hypothesis (H₀):** Knowledge is merely hidden; the model retains internal representations and can access them under altered query conditions.

**Alternative hypothesis (H₁):** Knowledge is truly removed; the model no longer maintains functional representations of the target domain.

---

## 2. Theoretical Framework

Knowledge can appear removed but remain accessible through:
- **Paraphrasing**: Reformulated questions using synonyms or indirect phrasing
- **Multi-hop reasoning**: Asking for intermediate facts that lead to the target knowledge
- **Adversarial prompting**: Role-playing, hypothetical scenarios, or jailbreak-style prompts
- **Fine-grained probing**: Targeted questions that expose residual semantic structure
- **Cross-domain bridging**: Accessing knowledge through related domains not explicitly in the unlearning target

True removal would show:
- Inability to access knowledge across all prompt variations
- No residual semantic activation related to the target domain
- Consistent performance degradation on downstream tasks requiring the knowledge
- Inability to reconstruct the knowledge through inference chains

---

## 3. Experimental Design

### 3.1 Main Comparison: Conditions

We compare **three model states** on the same evaluation suite:

**Condition A: Original Model (Baseline)**
- The pre-unlearning model that retains all original training knowledge
- Role: Establishes the performance ceiling and confirms tests can measure knowledge presence

**Condition B: Unlearned Model (Procedure 1)**
- First unlearning procedure (e.g., machine unlearning via gradient ascent, RL-based unlearning, etc.)
- Role: Test whether procedure claims actual removal

**Condition C: Unlearned Model (Procedure 2)**
- Second unlearning procedure (different method; e.g., data deletion, fine-tuning, or alternative algorithm)
- Role: Cross-validate findings and determine if removal mechanism generalizes

### 3.2 Ablation: Query Strategy Variation

Within each model state, we apply **four query strategies** to the same underlying questions:

1. **Direct Query (D):** Straightforward, topic-direct question
   - Example: "What is [entity]?" for factual knowledge
   - Baseline access mode

2. **Paraphrased Query (P):** Synonymous rephrasing with altered syntax
   - Example: Rewrite using different vocabulary, question structure
   - Tests if model's response inhibition generalizes

3. **Adversarial Query (A):** Indirect or role-playing approaches
   - Examples: "In fiction, suppose...", "If we ignore safety, what is...", hypothetical scenarios
   - Tests if knowledge is retrievable under altered framing

4. **Probing Query (PR):** Fine-grained, multi-part question targeting latent representations
   - Examples: Ask for attributes, consequences, or relationships related to the target knowledge
   - Tests if residual semantic structure remains even if direct recall fails

### 3.3 Target Knowledge Domain

Choose a well-defined, significant knowledge domain that:
- Is conceptually cohesive (e.g., a specific technical topic, a named entity class, a procedure)
- Has clear, measurable manifestations (factual, reasoning-based, application-based)
- Appears in the original training data with sufficient coverage
- Has both direct questions and decomposable/indirect access paths
- Is not trivially recoverable from general knowledge (e.g., not just "2+2=4")

**Example target:** A specific technical algorithm or process, a controlled narrative/entity class, or a narrow factual domain (e.g., "details of a specific research dataset").

---

## 4. Evaluation Suite

### 4.1 Knowledge Access Tests (Primary Metrics)

For each model state × query strategy combination, measure:

**Test Set T1: Factual Recall**
- Direct factual questions about the target knowledge
- Metrics:
  - **Exact match accuracy:** Whether the model provides the correct fact
  - **Semantic similarity (via embedding cosine distance):** Distance between model response and ground-truth answer
  - **Confidence score:** Model's self-reported confidence in the response (e.g., via log probabilities)

**Test Set T2: Multi-hop Reasoning**
- Questions requiring inference chains that pass through target knowledge
- Metrics:
  - **Task completion rate:** Can the model successfully chain reasoning?
  - **Intermediate accuracy:** Are intermediate steps correct?
  - **Final answer accuracy:** Is the end result correct?

**Test Set T3: Attribute/Relation Extraction**
- Targeted probes for specific attributes, relationships, or consequences of the target knowledge
- Metrics:
  - **Attribute recall rate:** Number of correct attributes retrieved
  - **Structured knowledge recovery:** Can we reconstruct a knowledge graph of the domain from responses?

**Test Set T4: Downstream Application**
- Tasks that depend on the target knowledge but ask it indirectly
- Examples: summarization, comparison, or prediction tasks that require understanding the target domain
- Metrics:
  - **Task accuracy:** Performance on the downstream task
  - **Degradation vs. original:** Performance delta relative to Condition A

### 4.2 Knowledge Hiding Detection Tests (Secondary Metrics)

**Test Set T5: Explicit Refusal and Linguistic Markers**
- Measure whether the unlearned model explicitly refuses to answer or shows signs of knowledge-hiding behavior
- Metrics:
  - **Refusal rate:** Proportion of responses that contain explicit refusals
  - **Defensive language frequency:** Count of safety disclaimers, hedges, or deflection phrases
  - **Pattern consistency:** Does the model always refuse a specific topic or only under certain conditions?

**Test Set T6: Semantic Activation (Latent Space Probing)**
- Use model internals (if accessible; otherwise use perturbation tests) to detect residual semantic structure
- Metrics:
  - **Classifier accuracy on hidden layers:** Can a simple classifier distinguish target-domain representations from baseline?
  - **Representation norm distance:** Distance of model activations for target-domain queries vs. control queries
  - **Causal intervention results:** Do targeted interventions in hidden layers restore knowledge access?

**Test Set T7: Paraphrase Consistency**
- Measure whether unlearned models show inconsistent behavior across paraphrased versions of the same question
- Metrics:
  - **Inconsistency rate:** Proportion of question pairs where the model gives contradictory answers to semantically equivalent queries
  - **Stability score:** Jaccard similarity or BLEU score of responses to paraphrase pairs

---

## 5. Analysis Plan

### 5.1 Primary Analysis: Knowledge Removal Detection

**Step 1: Establish Baseline (Condition A)**
- Confirm that direct and indirect access methods retrieve the knowledge in the original model
- Document ground-truth performance levels for all test sets
- Verify test suite validity

**Step 2: Compare Unlearned Models to Baseline**
- For each test set and query strategy, compute performance gap between unlearned models (B, C) and original (A)
- Quantify: $\Delta_{	ext{Access}} = 	ext{Performance}_{	ext{Original}} - 	ext{Performance}_{	ext{Unlearned}}$
- Measure: What fraction of knowledge access is lost across all conditions?

**Step 3: Assess Pattern Across Query Strategies**
- Cross-tabulate results by strategy (D, P, A, PR)
- **True removal hypothesis:** Large $\Delta$ across all strategies; knowledge gap is uniform
- **Hiding hypothesis:** Small $\Delta$ for direct queries, but significant knowledge leakage under paraphrase, adversarial, or probing strategies

**Step 4: Cross-Model Comparison (Procedure 1 vs. 2)**
- Compare performance drops between the two unlearning procedures
- Identify whether removal is procedure-specific or robust
- Quantify: Agreement between procedures on which knowledge is removed vs. retained

### 5.2 Secondary Analysis: Ablation and Mechanism

**Step 5: Query Strategy Sensitivity**
- Test whether performance on unlearned models depends significantly on query strategy
- Interaction analysis: Does procedure type (B vs. C) interact with strategy type (D, P, A, PR)?
- If unlearning is method-robust, we expect interaction effects to be small

**Step 6: Fine-Grained Retention Analysis**
- For sub-components of the target knowledge (e.g., different facts, different reasoning steps), measure which are removed and which remain
- Quantify partial unlearning: What fraction of the target knowledge domain is actually removed vs. retained?

**Step 7: Downstream Task Impact**
- Measure model utility on tasks requiring the target knowledge
- Compare utility degradation between procedures
- Assess trade-offs: Does unlearning incur collateral damage on unrelated tasks?

### 5.3 Uncertainty Quantification

**Confidence Intervals:**
- For each metric, compute 95% CI via bootstrap sampling (resample test items with replacement, recompute metrics)
- Report mean ± CI for all key performance measurements

**Statistical Tests:**
- Paired t-test or Wilcoxon signed-rank test (depending on data distribution) to compare Condition A vs. B and A vs. C on each test set
- Repeated-measures ANOVA to test effects of query strategy within each model condition
- Interaction tests to assess whether procedure type moderates query-strategy effects

**Effect Size:**
- Report Cohen's d or Hedges' g for all pairwise comparisons
- Interpret: Small effect (d < 0.2), medium (0.2 ≤ d < 0.8), large (d ≥ 0.8)

**Sensitivity Analysis:**
- Vary test-suite parameters (e.g., difficulty level of questions, number of hops in reasoning chains) and recompute results
- Document robustness: Do conclusions hold under parameter variation?

---

## 6. Concrete Resources

### 6.1 Models

- **Original model:** The base model before unlearning (e.g., a public LLM checkpoint)
- **Unlearned instances:** Two models subjected to different unlearning procedures
- **Access method:** Query via API (if available) or local inference

### 6.2 Data and Knowledge Base

- **Target knowledge:** Curated set of facts, reasoning chains, and application scenarios from the target domain
  - Minimum: 20–50 ground-truth facts or scenarios for direct recall testing
  - Reasoning chains: 10–20 multi-hop scenarios
  - Paraphrases: 3–5 reformulations per core question
  - Adversarial variants: 2–3 alternative phrasings or framing per question
  
- **Control set:** Unrelated facts and tasks (same volume as target knowledge) to verify no collateral damage

- **Test suite size:** Recommend 100–200 distinct queries across all test sets and strategies to enable reliable statistical inference

### 6.3 Evaluation Infrastructure

- **LLM API or local inference setup** with ability to query the three model states
- **Response collection system:** Automated script to submit queries and log responses with timestamps and metadata
- **Embedding model** for semantic similarity metrics (e.g., a sentence-BERT variant or the model's own embeddings if accessible)
- **Parsing/annotation tools** to evaluate response correctness (manual annotation recommended for high-stakes domains)
- **Statistical software:** Python (scipy, statsmodels) or R for analysis and visualization

### 6.4 Compute Budget

- Estimate: ~1000–3000 model queries (3 conditions × 4 strategies × ~100–200 test items)
- If using a large model, budget for inference time and API costs
- Latent-space probing (if attempted) requires internal access to model activations; budget accordingly

---

## 7. Outcome Metrics and Success Criteria

### 7.1 Primary Outcome: Knowledge Removal Status

**Metric 1: Knowledge Access Drop (KAD)**
$$	ext{KAD}_{	ext{Procedure}} = rac{1}{|S|} \sum_{s \in S} \left( 	ext{Accuracy}_{	ext{Original}}(s) - 	ext{Accuracy}_{	ext{Unlearned}}(s) ight)$$

where $S$ is the set of all test queries across all strategies.

- **Interpretation:**
  - KAD > 0.7: Strong evidence of knowledge removal (>70% performance drop)
  - 0.3 < KAD ≤ 0.7: Moderate evidence (knowledge partially removed or hidden)
  - KAD ≤ 0.3: Weak evidence; knowledge likely retained or easily recoverable

**Metric 2: Query-Strategy Robustness (QSR)**
$$	ext{QSR} = 1 - rac{	ext{StdDev}(	ext{Accuracy across strategies})}{	ext{Mean}(	ext{Accuracy across strategies})}$$

- **Interpretation:**
  - QSR > 0.8: Robust removal (consistent across query strategies, suggests true removal)
  - QSR ≤ 0.5: Non-robust (high variance suggests knowledge remains accessible under some strategies, indicates hiding)

**Metric 3: Cross-Procedure Agreement (CPA)**
$$	ext{CPA} = 	ext{Correlation}(	ext{Knowledge Access Drop}_{	ext{Proc1}}, 	ext{Knowledge Access Drop}_{	ext{Proc2}})$$

- **Interpretation:**
  - CPA > 0.7: High agreement (removal is procedure-robust)
  - CPA ≤ 0.3: Low agreement (procedures remove different subsets; findings not generalizable)

### 7.2 Secondary Outcomes: Mechanism and Trade-offs

**Metric 4: Latent Leakage Rate (LLR)**
- Proportion of latent probes (T6) that successfully recover knowledge despite explicit refusal
- **Interpretation:** High LLR suggests knowledge is hidden rather than removed

**Metric 5: Collateral Damage (CD)**
- Performance drop on control tasks (unrelated to target knowledge)
- **Interpretation:** High CD suggests unlearning harms general model capability

**Metric 6: Partial Unlearning Ratio (PUR)**
- Fraction of target-knowledge sub-components that show KAD > 0.5
- **Interpretation:** PUR = 1 indicates full removal; PUR < 0.5 indicates substantial retention

---

## 8. Interpretation Framework

### Scenario 1: True Knowledge Removal (H₁ Supported)
- **Evidence:**
  - KAD > 0.7 across all procedures
  - QSR > 0.8 (robust across query strategies)
  - CPA > 0.7 (agreement between procedures)
  - LLR < 0.2 (low latent leakage)
  - PUR ≈ 1 (comprehensive removal)

### Scenario 2: Knowledge Hiding / Suppression (H₀ Supported)
- **Evidence:**
  - KAD large for direct queries (T1) but small for paraphrased/adversarial (T2, T3)
  - QSR < 0.5 (high variance across strategies)
  - LLR > 0.6 (significant latent knowledge remains)
  - Explicit refusals on direct queries but informative responses on paraphrased versions

### Scenario 3: Partial/Incomplete Removal (Mixed Evidence)
- **Evidence:**
  - Moderate KAD (0.3–0.7)
  - CPA moderate (0.4–0.7)
  - Procedural differences in which sub-components are removed
  - Interpretation: Procedure successfully removes some but not all knowledge

---

## 9. Reporting and Deliverables

1. **Summary table:** Performance on each test set (T1–T7) across conditions (A, B, C) and strategies (D, P, A, PR)
2. **Statistical results:** Point estimates, 95% CIs, and p-values for all comparisons
3. **Visualization:** Heatmaps of query strategy × condition performance; box plots of key metrics
4. **Robustness checks:** Sensitivity analyses varying test-suite parameters
5. **Qualitative analysis:** Examples of responses from each condition; analysis of linguistic markers and failure modes
6. **Conclusion:** Which hypothesis (true removal vs. hiding) is best supported, with confidence levels

---

## 10. Limitations and Open Questions

- **Model access constraints:** If model internals are not accessible, latent-space probing (T6) becomes limited; mitigation via behavioral perturbation tests
- **Domain-specific validity:** Results generalize only to the target knowledge domain; replication across domains recommended
- **Procedural fairness:** Different unlearning procedures may have different design trade-offs; interpretation requires domain expertise
- **Adversarial prompting limits:** Adversarial strategies may be blocked by safety measures unrelated to unlearning; distinguish explicit safety guardrails from knowledge removal

---

## 11. Timeline and Effort Estimate

- **Data preparation:** 1–2 weeks (curate target knowledge, generate paraphrases, annotate ground truth)
- **Query execution:** 1–2 weeks (depends on model access and API rate limits)
- **Analysis and interpretation:** 1–2 weeks
- **Total:** 3–6 weeks, depending on parallelization and iteration

---

## Conclusion

This design provides a multi-faceted approach to distinguish true knowledge removal from hiding by:
1. Probing knowledge accessibility through multiple query strategies
2. Comparing multiple unlearning procedures to identify robust vs. procedure-specific effects
3. Testing both direct access and latent representations
4. Quantifying uncertainty via bootstrapping and statistical testing
5. Establishing clear success criteria aligned with the research question

The design is falsifiable, replicable, and actionable—enabling evidence-based conclusions about the efficacy of unlearning procedures.
