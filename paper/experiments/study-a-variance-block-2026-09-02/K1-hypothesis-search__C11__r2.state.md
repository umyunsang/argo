# Research state (fill every field before writing the design)

decision_id: K1-hypothesis-search-design

question: 
Does organizing an autonomous agent's attempts as a hypothesis tree with propagated 
insight beat a flat queue of attempts on held-out artifact optimization?

alternatives:
1. REJECTED: Linear single-agent optimization (pure gradient descent or greedy local search 
   without structure). Rationale: Cannot scale to large attempt budgets, and prior work 
   (2608.01913) shows agents need structured search strategies and evidence management; 
   a pure gradient baseline would not generalize across diverse tasks.

2. REJECTED: Hybrid tree + flat scheduling (mixing tree and queue). Rationale: Would 
   confound the comparison by introducing boundary effects between the two organizing 
   principles. The hypothesis asks for a clean contrast, and prior work on experimental 
   design (2608.03501) emphasizes stage isolation to separate effects.

3. REJECTED: History-free greedy (independent attempts with no carryover of insights). 
   Rationale: Would not isolate the effect of propagated insight; it would measure only 
   the value of structure, not the value of learning from prior attempts. 2607.09195 shows 
   that belief updates from evidence are crucial, not just attempt tracking.

sampling_frame:
Population: Autonomous agent artifact optimization tasks grounded in real published work, 
spanning diverse scientific domains (at least 5 domains from ResearchClawBench or similar, 
e.g., materials science, computational chemistry, machine learning, neuroscience, physics).

Unit of analysis: Single agent run on a single task, constrained by fixed compute and 
workspace budget (same budget for every arm). Each unit consists of:
  - One task prompt (hidden target known to evaluator only)
  - One attempt sequence (either tree-organized or queue-organized) 
  - One final artifact (code, report, figure, or prediction)
  - Outcome judgment at task level (held-out rubric-based evaluation)

Sample size: Minimum 30 runs per arm per task (30 × 2 arms × 5+ tasks = 300+ runs minimum) 
to meet paired resolution targets (α=0.05, power=0.8) for small-to-medium effects, following 
2605.30315 guidance on underpowered LLM evaluations. Allocation between tree and flat is 1:1 
(simple randomization, stratified by task).

evidence_used:
1. HEP protocol (2607.09195): Demonstrates that explicit hypothesis-test-evidence-belief 
   cycles with externalized belief state and audit trail improve agent reasoning on open-ended 
   tasks (materials science). Justifies using a tree structure with belief propagation as 
   treatment arm. However, did not test on held-out artifact optimization; scope was 
   materials-science research with computational tools.

2. Search agent diagnosis (2608.01913): Shows that retrieval recall (cumulative gold-evidence 
   coverage) predicts accuracy far better than search effort; useful evidence appears early, 
   and continued searching is often wasteful; redundant queries mark failure. Justifies 
   holding compute budget constant and measuring evidence saturation as a secondary outcome; 
   also supports early-stopping signals in queue baseline. Could NOT verify whether tree 
   structure helps exploit this saturation better than a queue.

3. Autonomous research benchmarks (2606.07591, 2608.03501): Establish multi-domain rubric 
   design and redline mechanisms for evaluating open-ended research outputs. Justifies using 
   hidden-target design, expert-curated rubrics, and severity redlines in our evaluation to 
   avoid LLM judge blind spots. However, benchmarks evaluate end-to-end pipeline quality, 
   not attempt organization; we adapt their rubric discipline but change the manipulation.

4. LLM judge audit (2608.29517): Shows judge severity spans 219 points on a 1000-scale; 
   version shifts reach 133 points; outcome-only judges miss silent faults. Justifies 
   cross-calling calibration, trajectory-level (not outcome-only) evaluation via rubric 
   on attempt sequence, and pinning judge version. Could NOT verify whether severity 
   effects would be equal across tree vs. flat arms.

5. Trajectory-level judge blind spots (2609.00038): Outcome-only evaluation catches 84% 
   of loud faults but 45% of silent ones; step rubrics catch 77% with zero false alarms. 
   Justifies evaluating the attempt sequence (log of hypothesis evolution, queries, 
   revisions) via rubric, not final artifact alone. This is critical because tree structure 
   may help reasoning without affecting final answer quality equally for all tasks.

6. Paired resolution diagnostics (2605.30315): Many LLM leaderboard comparisons are 
   unresolved at (α, 1−β)=(0.05, 0.8); inversion of hypothesis-testing framework is needed. 
   Justifies pre-registering resolution target, reporting q=N/N* ratio, and stopping rule. 
   Could NOT verify minimum effect size for tree vs. flat on artifact optimization; used 
   conservative (small-to-medium) target.

7. Variance components (2607.13304): LLM non-determinism arises from within-prompt resampling, 
   prompt paraphrase, model identity, and language. Justifies holding model, language, and 
   prompt fixed; treating within-arm variance carefully; and designing replication budget 
   (K>1 per cell). Could NOT separately isolate which components dominate for our task domain.

falsifier:
Observation: Tree arm (hypothesis-tree-organized attempts) shows no significant advantage 
over flat-queue arm in held-out rubric-based artifact quality, AND the tree-arm attempt 
sequences are not rated higher on adherence to hypothesis-test-evidence-belief cycle (as 
judged by trajectory rubric) than flat-arm sequences. This would refute the premise that 
organizing attempts as a tree with propagated insight beats a queue, because it would imply 
that structure has no measurable effect on either outcome or reasoning process.

Additionally, if tree-arm runs hit compute budget much earlier (e.g., average 20% of budget 
remaining vs. flat-arm 5%) and achieve worse final artifacts, it would suggest the tree 
incurs overhead (bookkeeping, belief updates) that outweighs insight benefits in this domain, 
falsifying the core hypothesis that propagated insight improves optimization.

stopping_rule:
1. Fixed sample size: Collect N=30 complete runs per arm per task (300+ total runs across 5+ 
   tasks), stratified random allocation. Do not add more runs based on p-values (no peeking).

2. Interim monitor (informational only, non-binding): After collecting 50% of target runs 
   (N≈150), compute provisional effect estimates and resolution ratio (q=N/N*) following 
   2605.30315. If q<0.4 (severely underpowered for observed effect), alert investigator but 
   continue to fixed N. Do not adjust N mid-stream.

3. Quality gates (pre-registered):
   - If >20% of runs fail to complete (e.g., OOM, timeout, malformed output), investigate 
     root cause and pause collection until fixed (infrastructure issue).
   - If judge agreement (inter-rater or within-judge retest k≥2) drops below κ=0.60 on a 
     task rubric, retrain/recalibrate judge before scoring new runs (as per 2608.29517).

4. Falsifier detection: If after 50% of runs, effect estimates cross zero with high confidence 
   and trajectory rubric also shows no tree advantage, may stop early and report null result 
   with N~150, noting underpowered design. This is a decision point for the investigator, not 
   automatic; reasoning and raw data remain open.

5. Documentation: Log all interim peeks, quality-gate decisions, any sample-size or protocol 
   changes, and raw attempt logs (timestamps, queries, hypothesis evolution) for reproducibility 
   and post-hoc transparency (following 2608.29517 audit discipline).
