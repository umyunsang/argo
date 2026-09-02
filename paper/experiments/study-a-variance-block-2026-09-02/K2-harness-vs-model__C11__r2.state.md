# Research state (fill every field before writing the design)

decision_id: K2-harness-vs-model confound isolation

question:
  When a system's harness improves (better task structure, tool config, evaluation method),
  how much of the measured performance gain comes from the harness itself versus from the 
  model receiving a better-optimized prompt for the new harness?

alternatives:
  1. PROMPT IMPROVEMENT ONLY: Keep the harness fixed, only improve the prompt text.
     Rationale: Establishes a lower bound on improvement from prompt optimization alone.
     Rejection reason: Doesn't isolate harness contribution.
  
  2. HARNESS IMPROVEMENT WITHOUT PROMPT RE-OPTIMIZATION: Apply new harness but lock prompt 
     to original wording.
     Rationale: Would show pure harness effect but is unfair—the prompt was written for 
     the old harness.
     Rejection reason: Confounds harness quality with prompt-harness misalignment.
  
  3. SEQUENTIAL OPTIMIZATION (rejected): Optimize harness first, then prompt second.
     Rejection reason: Cannot disentangle temporal order effects; improvements from phase 2 
     are ambiguous about harness vs. prompt contribution.

sampling_frame:
  Population: Distinct task instances that a system must solve (e.g., Q&A, code generation, 
             retrieval-and-summarize tasks). Sampled from held-out evaluation set.
  Unit: (task instance, harness variant, prompt variant) triplet
  Fixed factors: Model identity (same across all conditions)
  Varied factors: Harness version (baseline vs. improved), Prompt version (baseline vs. improved)
  Blocking/stratification: By task domain and complexity level (using 2608.01913's retrieval-gap 
                          detection to identify hard vs. easy instances)
  Evaluation held outside: All scoring runs outside candidate workspace (per constraints)

evidence_used:
  - 2609.00038 (Mohammadi): Outcome-only judges miss 55% of silent faults; 
    step-rubric evaluation required for trajectory inspection.
    Implication: We must evaluate both final answer AND reasoning trajectory.
  
  - 2608.03501 (Liu et al., OptED): Stage isolation (separate high-level planning from 
    low-level configuration) improves LLM experimental design quality.
    Implication: Explicitly separate harness design choices from prompt optimization choices.
  
  - 2605.30315 (Kotawala): Paired evaluation designs meet resolution targets where unpaired 
    designs fail. Resolution ratio q=N/N* quantifies whether comparison is resolved.
    Implication: Use paired (within-task) allocation; pre-compute N* needed for target 
    effect size.
  
  - 2607.13304 (Zatuchin): LLM response variance partitions into within-prompt resampling, 
    prompt paraphrase, model identity, and query language; different sources require 
    different allocations per generalizability theory.
    Implication: Allocate resampling budget using variance components, not fixed rules.
  
  - 2608.01913 (Liu et al., search agents): Decompose failures into retrieval gaps and 
    utilization gaps; effort doesn't predict quality.
    Implication: Harness evaluation must separate evidence-availability issues from 
    evidence-utilization issues.

  - 2606.07591 (ResearchClawBench): Rubric scoring for autonomous agent tasks works but 
    hidden-target issues remain.
    Implication: Use explicit rubric; acknowledge that rubric ceiling may not capture 
    true agent capability.

falsifier:
  If prompt improvement (harness held fixed) is NOT statistically significantly smaller 
  than harness improvement (prompt re-optimized), then the harness change is not proven 
  to add value—it merely opens room for better prompts. This would falsify the claim that 
  "the harness itself improves the system."

stopping_rule:
  Stop when BOTH conditions hold:
  1. Collected n ≥ N*, where N* is the paired sample size required to detect target effect 
     size (δ ≥ 5 percentage points) at (α, 1−β) = (0.05, 0.80) under the observed 
     correlation between harness and prompt improvements (per 2605.30315 resolution framework).
  2. The 95% confidence interval for (Δ_harness − Δ_prompt) excludes zero, OR it straddles 
     zero but margin-of-error is ≤ 2 percentage points.
