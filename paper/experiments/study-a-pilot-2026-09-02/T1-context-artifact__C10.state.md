# Research state (fill every field before writing the design)

decision_id: T1-context-artifact-efficacy-2026

question: Does providing a persistent, human-written project context artifact to a coding agent improve its task success rate on real repository tasks compared to baseline task-only instruction?

alternatives:
  - REJECTED: Within-subject design (same agent, same task, with/without context). Rationale: Tasks are attempted max 3 times per strategy; order effects and learning within a single agent session make this unreliable.
  - REJECTED: Single-vendor comparison only (Claude Code with/without artifact). Rationale: Vendor differences in model capability, context window size, and instruction-following confound the effect of the artifact itself. Two vendors required by constraint.
  - ACCEPTED PRIMARY: Between-subjects design with two vendors (Claude Code + GPT-4 Codex via OpenAI API), random task assignment to context-present vs context-absent condition, stratified by task difficulty.

sampling_frame: >
  Population: Merged pull requests (n≈100) from production Python and TypeScript repositories 
  (minimum GH stars ≥1000, test coverage ≥90%) published to GitHub Archive and archived in BigQuery 
  public dataset, filtered to 2023-2024 timeframe. 
  Unit of analysis: Single PR, treated as one task. 
  Inclusion criteria: PR ≥100 lines added/modified, ≥5 test cases in suite, closed/merged status, 
  no security-sensitive code (credentials, auth tokens, PII). 
  Stratification: Balanced across three difficulty tiers (easy/medium/hard) based on cyclomatic complexity 
  and test count metrics. 
  Sampling procedure: Stratified random sample n=30 tasks total (10 per difficulty tier, 
  15 assigned to context-present condition, 15 to context-absent baseline).

evidence_used:
  - Assumption 1 (verifiable): Claude Code and GPT-4 Codex API exist and are available. Verified: both products active as of 2026.
  - Assumption 2 (partially verified): GitHub Archive contains suitable merged PRs. Verified: BigQuery public dataset contains PR history; spot-checked presence of test suites in sampled repos.
  - Assumption 3 (unverified): Human-written context artifacts improve task success. This is the research hypothesis; no prior pilot data available to validate.
  - Limitation: Context artifact quality not controlled; all artifacts sourced from single human author to minimize variability, but artifact quality spectrum unknown.

falsifier: >
  If the task success rate in the context-present condition (both vendors combined) is equal to or lower than 
  the context-absent baseline at p < 0.05 (two-tailed binomial test), the hypothesis that context artifacts 
  improve coding agent task success is refuted. Secondary falsifier: if context artifact helps one vendor 
  (e.g., Claude Code) but actively harms the other (e.g., Codex), the effect is not generalizable.

stopping_rule:
  - Primary: Collect full n=30 task sample across both conditions and both vendors (max 30 × 2 vendors × 3 attempts = 180 total attempts).
  - Optional early stop (success): If after n=20 tasks, task success rate in context-present ≥70% and context-absent ≤40%, with Fisher's exact p < 0.05, stop and report early.
  - Optional early stop (futility): If after n=20 tasks, task success rates in both conditions are within 10 percentage points (e.g., both ≥50% or both ≤30%), stop and report null finding.
  - Hard stop: If any vendor API becomes unavailable or unplanned outages exceed 10 days cumulative, terminate study and report partial results.
