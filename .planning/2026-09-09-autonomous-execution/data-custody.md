# Development data custody lane

Owner: execution_data_custody. Scope: development tasks 37, 146820, 31, 146821 only. No selection/test-task inspection; no training, LLM or scoring launch. Root owns integration and repository checks.

Plan: (1) verify primary metadata and licenses, (2) implement exact-byte download and split custody with synthetic tests, (3) prepare the four authorized development datasets and report only counts/hashes/status.

Current: phase 1 in progress. Read project AGENTS, agent brief, migration state, design v2, protocol v2, and development-only roster rows. Applied planning-with-files under the root-owned active plan. Python 3.14 environment already has pandas, numpy, scipy, sklearn, pytest, requests; openml package absent and not required yet. No installation.

Authority: current execution authorization supersedes prior design-only memory for this study. Old G/C/F design is near_match_only and is not reused. Current construction pause is directly_supported by live files.

Fixed split: OpenML repeat 0/fold 0 outer train/test; stratified 80/20 inner split, seed 20260909. Original data/split bytes and all row identities remain in private custody outside the repository. Do not print labels or data rows. Public class schema may be recorded only from source metadata/header.

Navigation note: requested docs/CODEX-NAVIGATION-GUIDE.md is absent. Project AGENTS applies; no narrower experiment AGENTS found.

Primary metadata verified: task 37 -> data 37 v1; task 146820 -> data 40983 v2; task 31 -> data 31 v1; task 146821 -> data 40975 v3. OpenML reports public visibility and licence `Public` for each. UCI CC BY 4.0 independently verified for Wilt (285; DOI 10.24432/C5KS4M), German Credit (144; DOI 10.24432/C5NC77), Car Evaluation (19; DOI 10.24432/C5JP48). Pima diabetes legacy UCI URL is unavailable; UCI dataset 34 is a different diabetes time-series dataset and its license is inapplicable. Preserve the exact OpenML `Public` statement without asserting CC0/CC BY for Pima. Local research download uses the public OpenML distribution; no redistribution is performed.

Source discrepancy: Wilt UCI headline says 4889, but its own file description says 4339 train + 500 test = 4839, matching OpenML roster. Study retains the fixed OpenML 4839 rows and split, not the original UCI split. No silent row correction.

CSV interface coordinated with scorer: no index; features in source order then target `class`; class IDs 0..K-1 from public ARFF header order. Metadata includes target_column, feature_columns, numeric_columns, categorical_columns, feature_dtypes, class_mapping public source-label list, classes integer IDs, n_classes, row_counts, source_hashes. Empty CSV field is missing; categorical readers must disable default NA-token coercion. Preserve source zeros and nominal levels.

Phase 2 complete: implemented `experiments/argo_study_20260909/data_custody.py` and `test_data_custody.py`. Nine synthetic integrity tests passed (`python3 -m unittest -v test_data_custody.py`, from the experiment directory): fixed split row order, header-driven class encoding, nominal NA preservation, overlap/range/duplicate rejection, absent classes, out-of-schema labels, row/missing-count mismatch, exact missing preservation, roster/version exclusion, source URL boundaries, file permissions and deterministic/no-overwrite exports. These are synthetic preparation tests, not worker/scorer isolation certification or scientific outcomes.

Phase 3 complete: all four actual development datasets prepared without learning or scoring. Environment Python 3.14.5, numpy 2.4.6, pandas 3.0.5, scipy 1.18.1, sklearn 1.9.0 (exact runtime values also in private metadata).

| Task | Source rows | Inner train | Dev | Outer train | Outer test |
|---|---:|---:|---:|---:|---:|
| 37 | 768 | 552 | 139 | 691 | 77 |
| 146820 | 4839 | 3484 | 871 | 4355 | 484 |
| 31 | 1000 | 720 | 180 | 900 | 100 |
| 146821 | 1728 | 1244 | 311 | 1555 | 173 |

Private task roots: `/Users/um-yunsang/.local/share/argo-study-20260909/custody/task_<task_id>/`. Each contains six requested CSVs, metadata.json, row_identity.json, source_receipts.json and source/ (original ARFF, complete OpenML split ARFF, original data/task metadata bytes, and applicable UCI page bytes). Custody directories 0700 and data files 0600. Original OpenML source MD5 matched for all four; SHA256 source and export hashes rechecked after materialization. Public summary `data-custody.json` records safe counts, source/metadata hashes, provenance, licensing qualification and validation only. No label rows or row identities in public notes or tool output.

Handoff constraint: mount only worker-allowed inner_train.csv and a curated public schema into research workers. Do not expose custody source/ pages, row_identity.json, dev/test labels, outer_train.csv or test_X.csv to workers. Source metadata/pages can contain historical benchmark references and stay outside episode corpus. Same-UID permissions are custody hygiene only; root must establish process/container isolation separately. Generated finalizer consumes outer_train.csv only after artifact lock. All labels are contiguous integer IDs according to public header schema; do not infer a new mapping from any later split.

Lane stop condition met: four development preparations complete and nine synthetic preparation tests pass. No selection/test tasks inspected or downloaded. No model training, scoring or LLM calls; no packages installed; no native code changes. Root owns npm check and all scientific launch decisions.
