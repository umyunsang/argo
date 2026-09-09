# RE-Bench Full-Read Method Note — Stage 1 Unit, Budget, and Transfer Boundaries

Source: Wijk et al., *RE-Bench: Evaluating frontier AI R&D capabilities of language model agents against human experts*, arXiv:2411.15114.  
Read receipt: `rebench-full-read-receipt.json` SHA-256 `48edddcdf4754dfbf3d1adb0d98681628dbb793924aa2ce209749a08559eea44`  
Locators: `rebench-locators.json` SHA-256 `ed449d6765accee0718dc54edf897c0f8e89635ae2a9c03137a631613a810dfc`

## Evaluation design that transfers

RE-Bench validates environments for feasibility, a low floor, high ceiling, and technical issues before capability
interpretation (`rebench_feasibility_technical_issues`). It exposes a starting solution, timestamped scorer, hidden
reference solution, and continuous normalized score (`rebench_environment_score_contract`). ARGO Stage 0 similarly
requires a deliberately degraded baseline that runs, a known-valid output, score headroom, stable scorer, and explicit
issue classification before any treatment episode.

## Unit and budget boundary

RE-Bench shows that one long run and best-of-k short runs are different allocation policies under the same total time
budget (`rebench_best_of_k_allocation`, `rebench_rollout_estimand`). ARGO's estimand is the mean intention-to-run score
across the **scheduled** seeds nested within task-cell, not the best seed. Best-of-k is not a confirmatory outcome. The
task remains the population unit.

Model scaffold, scoring access, wall time, token throughput, hardware and API-pause handling are part of the treatment
surface (`rebench_scaffold_and_time_surface`, `rebench_evaluation_procedure`). G/C/F cells therefore receive identical
hard token/tool/time/cost caps and score visibility. F cannot inspect the hidden official score during refinement.

## Reliability and overfitting boundary

Agents try many more solutions and rare noisy successes can dominate; rerunning one selected solution produced a lower
score in the authors' example (`rebench_rare_success_overfit`). RE-Bench also identifies visible test-score overfitting
and recommends hidden test scores (`rebench_limits_and_hidden_test`). ARGO keeps validation diagnostics non-oracle,
computes the held-out scorer once after stopping, and reports every attempted run in reliability. No best-run selection.

## Transfer limit

Seven short, cleanly defined ML environments do not represent months-long, interacting R&D projects
(`rebench_design_goals_transfer_limit`, `rebench_limits_and_hidden_test`). Human baseline averages also vary by expert
source and experience (`rebench_human_baseline_heterogeneity`). ARGO uses RE-Bench as an evaluation-pattern anchor, not
as evidence that G/C/F improve performance or that the resulting harness automates R&D globally.
