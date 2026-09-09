# Scoring apparatus lane

Status: complete for this bounded lane. Host 25/25 and existing container 25/25 synthetic tests pass. No actual dataset or private label was read; no scientific run was launched.

Plan completed: canonical train-only preprocessing and fit/predict identity; strict private-label scoring; final-lock/refit state utilities; focused synthetic validation and environment report.

The root owns task_plan.md, findings.md and progress.md. This lane owns only `experiments/argo_study_20260909/scoring.py`, `test_scoring.py` and this report pair.

Live findings: host Python 3.14.5, scikit-learn 1.9.0, NumPy 2.4.6, pandas 3.0.5. Existing container Python 3.11.16, scikit-learn 1.6.1, NumPy 1.26.4, pandas 2.2.3, SciPy 1.14.1, joblib 1.4.2. No dependency installation occurred. The data lane specifies CSV target `class`, public-schema class IDs 0..K-1, blank missing values, categorical string preservation and metadata column lists. The navigation guide referenced in the supplied global instructions is absent.

Implementation: numeric train-median imputation preserves all-missing columns with zero; one-hot categories comprise train-observed strings and the reserved missing sentinel; unknown strings map to all-zero. The fixed RF100 explicitly pins every effective model parameter. `canonical_config(metadata)` and `fit(X, y, config)` produce a `FittedArtifact` with `predict(X)` and a manifest binding source, config, public class mapping, seed, environment, preprocessing and learned-state hashes. `read_training_csv`/`read_features_csv` preserve real `NA` strings and blank missing values. The fit helper intentionally implements only the baseline; the sandbox runner owns arbitrary candidate training.

The independent private-label scorer validates exactly one finite integral class-ID vector before any private file read and returns only status plus scalar balanced accuracy. All malformed private-file conditions collapse to `TRUSTED_SCORING_UNAVAILABLE`, which the controller must retain as UNKNOWN. Prediction defects raise label-independent contract errors. Selection utilities require verified candidate identity, preserve the default at deadline, prevent a second different lock, and consume the one refit allowance before launch with an unchanged recipe hash.

Validation command: `python3 -m unittest test_scoring -v`, from `experiments/argo_study_20260909`. Tests cover missing/unseen features, train-only medians, complete RF parameters, deterministic predictions, joblib round trips, fitted/config/manifest mutation rejection, strict prediction and private-label failures, multiclass BA against sklearn, default/explicit lock, recipe preservation and spent refit attempts. Final test times: host 1.817 s; container 1.853 s.

Container: `argo-house-price-p0:py311-cpu-065c4ef38370`, image ID `sha256:cd43d0d8edac942bd67cd097caf08edd2def45016bf011c1635849f15ebc7835`. Only the two synthetic code files were mounted read-only. Network disabled; read-only root; UID/GID 65534; two CPU, 1 GiB memory, 128 PID limit; temporary scratch was a tmpfs. This run validates scorer compatibility, not the complete episode isolation boundary.

Errors resolved: pickle bytes changed after a legitimate joblib round trip, so identity now hashes normalized learned state; NumPy dtype and sklearn 1.6.1's remainder UserList required explicit canonical encoding. A Docker Entrypoint inspection template was unsupported; exact image ID was retrieved separately. No failures were converted into PASS without a subsequent passing focused run.

Memory retrieval classification: the prior experiment hold is a near-match navigation hint superseded for this study by current explicit execution authorization. Current construction pause and scope were verified from repository authority.

Handoff limitations: the controller must atomically persist transitions, enforce feedback/resource admission, isolate generated code and deserialization, control outer-train refit custody, and withhold hidden results until all final locks. Environment hashes intentionally prevent cross-version artifact reuse; successful tests in both environments do not assert identical fitted artifacts across versions. Root runs repository `npm run check` after integration. File hashes and exact environment details are in `scoring-report.json`.
