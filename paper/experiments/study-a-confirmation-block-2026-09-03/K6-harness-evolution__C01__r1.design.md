# Experimental Design: Demonstrating Real Harness Gains vs. Task-Fitted Gains

## Research Question
An agent is permitted to rewrite the executable scaffold it runs inside, while the model itself is not changed. How would you show that any measured gain is real rather than fitted to the particular tasks used while rewriting?

## 1. Main Comparison: Real Generalization vs. Overfitting

### 1.1 Core Hypothesis
Measured harness improvements are real (generalizable to held-out tasks) if they transfer across:
- **Different task families** (not all from the same benchmark)
- **Random orderings** of the same task set
- **Distribution shifts** within a domain
- **Multiple independent runs** (variance controlled)

Measured gains are likely **fitted** if they:
- Vanish or degrade when task order is randomized
- Show extreme variance across runs (>5% standard deviation in pass rate)
- Fail to transfer between related task families
- Concentrate improvements only on tasks similar to the optimization set

### 1.2 Experimental Structure: Three-Family Cross-Validation

**Family A (Software Engineering):** SWE-Bench Pro
- Optimization set: 100 tasks (tasks 1–100 by ID)
- Held-out test set: Tasks 101–200 (same domain, held from the start)
- Transfer test set: WebArena (GitHub workflow tasks, ~50 tasks)

**Family B (System Administration):** SCUBA (Salesforce admin tasks)
- Optimization set: 100 tasks (IDs 1–100, default order)
- Held-out test set: Tasks 101–150 (held from the start)
- Transfer test set: Terminal-Bench 2 (~50 command-line admin tasks)

**Family C (Knowledge Work):** GAIA-2
- Optimization set: 100 tasks (IDs 1–100, default order)
- Held-out test set: Tasks 101–200 (held from the start)
- Transfer test set: WebArena (multi-site knowledge tasks, ~50 tasks)

### 1.3 Generalization Conditions

For each family, the agent will be tested under:

**Condition G1: Within-Family Held-Out (default task order)**
- Baseline harness: Measure pass rate on family's held-out test set
- Optimized harness: Rewrite on optimization set, measure on held-out test
- **Generalization signal:** Gain on tasks never seen during optimization

**Condition G2: Within-Family, Randomized Task Order**
- Reshuffle the optimization set (using fixed random seed)
- Re-run harness optimization on reshuffled optimization set
- Measure on held-out test set
- **Generalization signal:** Does gain persist when training signal is scrambled? (cite 2608.18066.txt: shuffled orders cause -4.5% vs +1.5% with curriculum)

**Condition G3: Cross-Family Transfer**
- Optimize harness on Family A's optimization set
- Test on a task from Family B or C (different domain)
- **Generalization signal:** Do domain-agnostic harness improvements transfer? If the harness is truly improved (not task-specific), skills learned on SWE tasks should help on admin tasks.

---

## 2. Ablation Studies

### 2.1 Harness Rewriting Surface (3 ablations)

To isolate what drives the improvement, measure gains by surface:

**Ablation A1: Instructions-Only Rewrite**
- Allow harness rewrites only to procedural instructions (no new skills/tools)
- Measure gain on held-out test set
- **Expected outcome:** If gain is large, harness sophistication (new tools) matters; if minimal, gain is from procedural adjustments

**Ablation A2: Skills-Only Rewrite**
- Allow only new/modified skills (no executable tools, no instruction changes)
- Measure gain on held-out test set
- **Expected outcome:** Tests whether new skills (reusable strategies) or tools (executable code) drive improvement

**Ablation A3: Tools-Only Rewrite**
- Allow only executable tool additions (no skills, no instruction rewrites)
- Measure gain on held-out test set
- **Expected outcome:** Isolates the contribution of new executable capabilities

**Interpretation:** If A1 >> A2 + A3, improvements are mostly procedural/task-specific. If A2 and A3 are comparable, improvements are spread across the harness.

### 2.2 Diagnostic Signal Validation (cited from 2606.05922.txt)

Replicate the ablation from RHO paper (Table 4):

**Ablation B1: Self-Validation Only**
- Disable self-consistency signals during retrospective analysis
- Run optimization and measure held-out test gain
- Expected baseline (from 2606.05922.txt): Without self-consistency, SWE-Bench Pro drops ~0.22 pass rate (Table 4: 0.78 → 0.70)

**Ablation B2: Self-Consistency Only**
- Disable self-validation signals
- Expected baseline: Larger degradation (~0.22 pass rate on SWE-Bench Pro)

**Ablation B3: No Structured Diagnosis (Raw Trajectory)**
- Skip diagnosis step; feed raw trajectories to harness proposal
- Expected baseline: ~0.60 pass rate (from 2606.05922.txt Table 4)

**Interpretation:** Validates that the method's internal diagnostic signals are actually responsible for improvements (not just rewriting itself).

---

## 3. Robustness to Task Order Variance (cite 2608.18066.txt)

### 3.1 Multiple Shuffles

Perform the optimization 3 times with:
1. **Default order** (tasks sorted by ID, imposes implicit curriculum; cite 2608.18066.txt Fig. 2)
2. **Shuffle-1** (fixed pseudo-random order)
3. **Shuffle-2** (different fixed pseudo-random order)

**Measurement:**
- For each order, optimize on the 100 tasks
- Measure held-out test pass rate
- Record mean, std dev, and best-worst gap across the 3 orders

**Generalization criterion:**
- Gain should be consistent across orders (std dev < 2%)
- Worst-case degradation should be < 3% vs. no-memory baseline
- If shuffled orders produce degradation (as in 2608.18066.txt: WebArena went from 54.8% → 49.1%), the harness has learned an implicit curriculum, not generalizable skills

### 3.2 Cross-Order Performance Consistency

For each harness generated under a different task order:
- Test it on the held-out set under all three orders
- **Expected outcome:** A truly generalizable harness should perform similarly regardless of which order produced it

---

## 4. Analysis Plan

### 4.1 Primary Outcome: Real Generalization

**Signal 1: Held-Out Gain Without Distribution Shift**
- Baseline: `pass_baseline_heldout` (vanilla harness on held-out test)
- Optimized: `pass_optimized_heldout` (optimized harness on held-out test)
- **Gain:** `Δ = pass_optimized_heldout - pass_baseline_heldout`
- Threshold for "real": Δ > 2% (statistically significant across ≥3 runs)

**Signal 2: Robustness to Task Order**
- Compute gain for each of 3 shuffled task orders
- Report mean gain and standard deviation across orders
- Threshold for "real": std dev(Δ across orders) < 1.5%
- Threshold for "not fitted": degradation under worst shuffle < 2% absolute vs. baseline

**Signal 3: Cross-Family Transfer**
- Measure gain on transfer test set (different task family than optimization)
- Threshold for "real": transfer gain ≥ 50% of within-family gain
- Rationale: if improvements are task-specific, transfer will collapse

### 4.2 Secondary Outcomes: Mechanistic Understanding

**Signal 4: Harness Component Attribution**
- Compare gains under A1 (instructions), A2 (skills), A3 (tools)
- Compute: `contribution_surface = gain_surface / total_gain`
- Report: Which surfaces contribute most? (consistency across families?)

**Signal 5: Diagnostic Signal Necessity**
- Compare full RHO (with B1+B2 signals) vs. ablations (B1 alone, B2 alone, B3 no diagnosis)
- Report: Performance ranking across ablations
- Threshold for necessity: `full_method_gain > ablation_gains by >1% absolute pass rate`

### 4.3 Variance Quantification

**Per condition:**
- Run ≥3 independent optimizations starting from the same baseline
- Record pass rate for each run
- Report: mean ± std dev, best-worst gap, relative variance increase vs. baseline
- Reference: cite 2608.18066.txt Table 1—self-improvement methods increase variance in 71% of cases; our target is < 50% increase

---

## 5. Concrete Resources

### 5.1 Tasks
- **SWE-Bench Pro:** 200 tasks (100 optimization + 100 held-out)
- **SCUBA:** 150 tasks (100 optimization + 50 held-out)
- **GAIA-2:** 200 tasks (100 optimization + 100 held-out)
- **Transfer test sets:** 50 tasks each from related benchmarks
  - WebArena GitHub tasks (for SWE → web transfer)
  - Terminal-Bench 2 (for admin → CLI transfer)
  - WebArena multi-site tasks (for knowledge → web transfer)

### 5.2 Computational Budget

Per family (conservative estimate):
- **Baseline single-run:** 100 tasks × 1 solve = 100 agent calls
- **Optimization phase (N=3 candidates, G=3 rollouts, k=10 coreset):** 10 × 3 × 3 + 3 × 100 = 390 agent calls per family
- **Held-out test:** 100 tasks × 1 solve = 100 agent calls
- **Robustness variants (3 shuffles):** 3 × 390 = 1,170 agent calls per family
- **Ablations (5 ablations):** 5 × 390 = 1,950 agent calls per family
- **Total per family:** ~4,000 agent calls
- **Total across 3 families:** ~12,000 agent calls

### 5.3 Tools & Infrastructure
- **Base agent:** Claude Code agent (GPT-5.5 equivalent) with high reasoning
- **Harness rewriting capability:** Executable workspace with skills, tools, and instructions (markdown + Python scripts)
- **Evaluation:** Automated graders from SWE-Bench Pro, SCUBA, GAIA-2, Terminal-Bench 2
- **Reproducibility:** Fix random seeds for task shuffling; record all harness diffs, all intermediate trajectories, all diagnostic signals

---

## 6. Outcome Metrics & Uncertainty Quantification

### 6.1 Primary Metrics

| Metric | Definition | Success Criterion | Uncertainty Measure |
|--------|------------|------------------|----------------------|
| **Held-out Generalization Gain** | `Δ_heldout = pass_opt - pass_baseline` on held-out test | > 2% absolute | 95% CI from ≥3 runs (t-test) |
| **Order Robustness** | std dev of `Δ` across 3 task shuffles | < 1.5% | Reported explicitly |
| **Transfer Efficiency** | `(gain_transfer / gain_within-family) × 100%` | > 50% | Reported as ratio ± bootstrapped 95% CI |
| **Variance Amplification** | `std(pass_optimized) / std(pass_baseline)` | < 1.5× | Reported per family |

### 6.2 Secondary Metrics

| Metric | Definition | Purpose |
|--------|------------|---------|
| **Component Attribution** | Contribution per surface (instructions/skills/tools) | Understand which harness levers drive improvement |
| **Diagnostic Necessity** | Gain under full RHO vs. each ablated diagnostic | Validate that signals (self-validation, self-consistency) matter |
| **Long-Horizon Effect** | Separate gain on short-horizon vs. long-horizon tasks | Detect if improvements are brittle (only short tasks) |

### 6.3 Uncertainty Quantification

**Across-run variance:**
- Run each optimization ≥3 times independently
- Report mean, std dev, 95% CI (t-distribution with n-1 df)
- If std dev > 2% absolute, flag as high-variance method

**Task order variance:**
- Shuffle-1, Shuffle-2, Default order
- Report mean gain, std dev across 3 orders
- If std dev > 1.5%, harness is order-sensitive

**Transfer uncertainty:**
- Bootstrap 95% CI on transfer gain by sampling tasks with replacement
- Report point estimate ± CI

---

## 7. How to Distinguish Real Gains from Fitted Gains

### 7.1 Red Flags (Likely Overfitted)

1. **Gain vanishes or reverses under shuffled task order** (cite 2608.18066.txt: -4.5% degradation under shuffle vs. +1.5% under default)
2. **Variance explodes** (std dev increases >50%, or best-worst gap >5% absolute; cite 2608.18066.txt Table 1: variance increased in 71% of cases)
3. **Transfer gain is <30% of within-family gain** (harness learned task-specific patterns)
4. **All gain concentrated in instructions** (procedural, not general) or **all in tools** (environment-specific)
5. **Ablation B3 (no structured diagnosis) gives nearly same gain** (diagnostic signals don't matter; rewriting itself is doing the work)

### 7.2 Green Flags (Likely Real)

1. **Consistent gain across default and shuffled orders** (>50% of original gain survives shuffle; cite 2608.18066.txt: healthy methods maintain gain under order change)
2. **Variance controlled** (std dev < 1.5%, best-worst gap < 3%)
3. **Transfer gain > 50% of within-family gain** (improvements generalize to related domain)
4. **Multiple harness surfaces contribute** (balanced mix of instruction, skill, tool improvements)
5. **Diagnostic ablations matter significantly** (Ablations B1, B2 degrade performance by >1% each)

---

## 8. Reporting and Transparency

### 8.1 Required Outputs

1. **Main results table:** Δ (held-out gain) ± 95% CI for each family, condition, and variant
2. **Robustness table:** Gains under Default, Shuffle-1, Shuffle-2 orders; std dev and best-worst gap
3. **Transfer matrix:** Pass rates on each transfer test set; transfer efficiency ratios
4. **Ablation results:** Gains for A1 (instructions), A2 (skills), A3 (tools), B1–B3 (diagnostic signals)
5. **Variance summary:** std dev and best-worst gap for baseline and optimized, per family
6. **Harness diffs:** Full diffs showing what changed in instructions, skills, tools for each family

### 8.2 Replicability

- Fix random seeds for all task shuffles (record them)
- Record all harness proposals (all N candidates), not just the chosen one
- Archive all intermediate trajectories, diagnostic signals, and coreset selections
- Publish prompts for solver, difficulty judge, diagnostic analyzer, harness proposer, and ranker (following 2606.05922.txt Appendix B structure)

---

## 9. Summary

This design tests whether harness improvements are **generalizable** (robust to task order, transferable across families, persistent across runs) or **fitted** (order-dependent, family-specific, high variance). By combining held-out evaluation, robustness to shuffling (cite 2608.18066.txt), cross-family transfer, and ablations of both the harness surface and the optimization method, we can distinguish real gains from task-fitted gains with high confidence.
