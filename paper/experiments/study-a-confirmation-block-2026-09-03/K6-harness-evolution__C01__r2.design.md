# Experimental Design: Demonstrating Genuine Scaffold Optimization Gains

## Research Question
An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

## Core Problem
When an agent's harness (prompts, tools, skills, workflows) is rewritten using a set of optimization tasks, the risk exists that the updated harness is overfitted to those specific tasks or task distribution. Improvements on the optimization set may not generalize to held-out tasks, especially if the task family has diverse subdomains or if task order introduces hidden prerequisite patterns.

## Main Comparison

**Condition A: Baseline harness**
- Fixed, untrained agent scaffold
- Evaluated on all tasks below

**Condition B: Optimized harness**
- Scaffold rewritten using *only* tasks from $T_{opt}$
- No model weight changes; only text prompts, tool definitions, and executable workflows modified
- Evaluated on held-out test splits

## Experimental Structure

### Task Split Strategy
- **Total task family**: Family of N related but distinct tasks across subdomains (e.g., SWE-Bench categories, or domain boundaries within a broader benchmark)
- **Primary split** (to prevent contamination):
  - $T_{opt}$ (optimization set): 40% of tasks
  - $T_{test}$ (held-out test): 60% of tasks
  
- **Secondary randomization** (to reveal order effects):
  - Shuffle $T_{test}$ into three random orderings (Shuffle-1, Shuffle-2, Shuffle-3)
  - Use default canonical ordering as Control ordering
  
- **Rationale**: Based on evidence/2608.18066.txt, task order induces implicit easy-to-hard curriculum; random orders stress-test generalization and expose fragility.

### Optimization Process (Single Round)
1. Agent receives access to $T_{opt}$ with full trajectories and ground-truth outcomes
2. Self-optimization loop (following RHO pattern from evidence/2606.05922.txt):
   - Select diverse, high-difficulty coreset from $T_{opt}$ (via difficulty scoring + DPP)
   - Re-run coreset tasks in parallel (G rollouts per task) with baseline harness
   - Extract self-validation (within-trajectory correctness) and self-consistency (cross-trajectory agreement) signals
   - Generate N candidate harness edits based on aggregated signals
   - Select best candidate via pairwise self-preference ranking
3. Output: Updated harness $h^*$

### Evaluation Protocol (Three Runs per Condition)
For both Condition A (baseline) and Condition B (optimized):
- **Run 1, Run 2, Run 3**: Independent executions with fresh random seeds
- For each run, evaluate on:
  - $T_{test}$ in Control ordering
  - $T_{test}$ in Shuffle-1 ordering
  - $T_{test}$ in Shuffle-2 ordering
  - $T_{test}$ in Shuffle-3 ordering

## Primary Outcome Metrics

**Main outcome**: Pass rate (binary success on each task), aggregated within each domain/subdomain

**Reported statistics per condition and per ordering**:
1. **Mean pass rate** across 3 runs
2. **Standard deviation** of pass rate across 3 runs
3. **Best-worst gap** (max run – min run), a measure of run-to-run fragility
4. **p-value** from unpaired t-test (Condition B vs. Condition A)

**Primary claim of success**:
- Condition B shows statistically significant gain (p < 0.05) over Condition A on Control ordering
- AND Condition B maintains >50% of that gain under each Shuffle ordering (shuffle-robustness criterion)
- AND Condition B does NOT exhibit >50% increase in variance (fragility bound) from Condition A

## Ablations

### Ablation 1: Information Leakage in Optimization
**Question**: Is the gain driven by genuine scaffold improvements, or by memorization of $T_{opt}$ task patterns in the harness?

**Method**: 
- Condition B1: Optimize as normal on $T_{opt}$
- Condition B2: Optimize on a *shuffled label version* of $T_{opt}$ (relabel all task outcomes randomly)
- Hypothesis: If B1 >> B2, the harness learned genuine patterns; if B1 ≈ B2, the gain is spurious

### Ablation 2: Generalization Beyond Task Domains
**Question**: Does the optimized harness generalize to an entirely separate but related task family?

**Method**:
- Identify a second, non-overlapping task family from the same domain (e.g., a second benchmark, or a later software engineering year)
- Denote as $T_{transfer}$
- Evaluate Condition B (harness optimized on $T_{opt}$) on $T_{transfer}$
- Compare transfer pass rate to Condition A on $T_{transfer}$
- Hypothesis: Genuine improvements transfer; overfitting does not

### Ablation 3: Sensitivity to Optimization Coreset Composition
**Question**: Does the optimized harness depend critically on which tasks were selected for optimization?

**Method**:
- Condition B3a: Optimize using coreset selected by difficulty + diversity (DPP)
- Condition B3b: Optimize using coreset selected randomly from $T_{opt}$
- Condition B3c: Optimize using coreset selected by difficulty alone (no diversity)
- Hypothesis: DPP-based selection produces more robust harnesses; random or difficulty-only selection produces more fragile ones

## Analysis Plan

### Primary Analysis
For each condition and ordering:
1. Compute pass rate per run
2. Compute mean, SD, best-worst gap
3. Aggregate across 3 runs for t-test (unpaired, two-tailed)
4. Report 95% CI for mean pass rate

### Secondary Analysis
1. **Breakdown by task domain**: Separately report results for each task subdomain within $T_{test}$ to identify whether gains concentrate in certain domains or generalize uniformly
2. **Task difficulty stratification**: Partition $T_{test}$ into easy (pass rate >70% baseline), medium (40-70%), and hard (<40%), and report separate pass rates to see whether gains are concentrated on specific difficulty bands (sign of fitting)
3. **Order effect quantification**: For each condition, compute the "order sensitivity" as $	ext{max}(	ext{pass}_{Control}, 	ext{pass}_{Shuffle-1}, 	ext{pass}_{Shuffle-2}) - 	ext{min}(\cdots)$; smaller is better (less fragile)
4. **Variance amplification check**: Report the ratio $	ext{SD}_{Condition B} / 	ext{SD}_{Condition A}$ per domain; if >1.5, flag as concerning

### Statistical Reporting
- Report all p-values and 95% CIs
- Use Benjamini-Hochberg correction if testing multiple task domains
- Report effect sizes (Cohen's d or pass-rate difference with CI)
- Explicitly report best-run and worst-run results, not just mean

## Concrete Resources

**Task Source**: A task family with natural subdomain structure (e.g., SWE-Bench Pro with per-tool or per-project categories; WebArena with per-site splits; or a coding competition with per-category problems)

**Benchmark Size**: At least 200 total tasks (120 in $T_{opt}$, 80 in $T_{test}$) to ensure statistical power

**Optimization Budget**: 
- Coreset size: k = 10–15 tasks
- Group rollout: G = 3–4 parallel rollouts per task
- Candidate harnesses: N = 3–5 candidates
- Expected agent calls: ~(k × G) + (N × k) = ~60–80 calls for optimization

**Computation**: Running each of 3 runs × 4 orderings on baseline + optimized harness, with statistical tests

## Outcome Metrics Summary

| Metric | Condition A (Baseline) | Condition B (Optimized) | Success Criterion |
|--------|----------------------|----------------------|------------------|
| Mean pass rate (Control) | — | — | B > A, p < 0.05 |
| SD pass rate (Control) | σ_A | σ_B | σ_B / σ_A < 1.5 |
| Best-worst gap (Control) | — | — | B < 10pp |
| Pass rate (Shuffle avg) | — | — | B – A > 50% of (B_control – A_control) |
| Pass rate ($T_{transfer}$) | — | — | B > A on new domain |
| Coreset sensitivity | — | SD(Condition B3a,b,c) | B3a SD < 2 × B3b SD |

## Uncertainty Quantification

- **Monte Carlo confidence intervals**: Bootstrap resampling over 3 runs to estimate 95% CI for each metric
- **Variance inflation**: Compute the ratio $\sigma_B / \sigma_A$ and its CI to quantify whether self-optimization amplifies noise (per evidence/2608.18066.txt finding)
- **Effect-size uncertainty**: Report Cohen's d with 95% CI for Condition B vs. Condition A
- **Order effect uncertainty**: Report min/max pass rates across orders and their ranges to visualize fragility

## How This Design Addresses the Research Question

1. **Prevents contamination**: $T_{opt}$ and $T_{test}$ are disjoint; optimization has no direct access to test tasks
2. **Detects overfitting**: If gain exists on Control ordering but vanishes on Shuffle orderings, the harness has learned task-distribution patterns, not generalizable skills
3. **Quantifies robustness**: Variance metrics and best-worst gap reveal whether gains are fragile (high variance/gap) or robust (low variance/gap)
4. **Isolates genuine scaffold effects**: Ablation on randomized outcomes separates harness generalization from statistical noise or task memorization
5. **Tests beyond training distribution**: Transfer ablation forces the harness to prove it learned principles, not task-specific heuristics

## Citations to Evidence
- **evidence/2606.05922.txt** (RHO): Guides the self-optimization mechanism (coreset selection, self-validation/consistency, best-of-N proposal)
- **evidence/2608.18066.txt** (Fragility): Motivates multiple-run evaluation, task order randomization, and variance monitoring to detect hidden fragility in self-improving systems
