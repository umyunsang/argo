# House Price P0 protocol options

**Status:** prospective task-bound design only. The House Price task is selected. User message `f1601306` authorizes applicable terms acceptance, private data download, and the intent to execute a bounded P0 after the exact contract and review are complete. Terms acceptance, download, environment, scorer custody, commands, ORX identities, hard-cap enforcement, and immutable review are not yet complete. Nothing was run in this lane.

This is one integration-feasibility attempt. It is not a B/C/G comparison, an architecture winner, a Kaggle submission, a power analysis, P1/P2 approval, or native ARGO construction.

## Recommended route

Use the following route unless the remaining material choices are changed explicitly:

1. **Controller:** `C0`, the existing non-graph source-backed tree/notebook with compulsory applicability, revalidation, preservation, and capsule obligations.
2. **Outer split:** the source-compatible positional 80/20 generator.
3. **Inner split:** the starter-compatible `train_test_split(test_size=0.25, shuffle=True, stratify=None, random_state=1)` on the public 80% pool, with one exact membership receipt reused by all methods.
4. **Development methods:** complete the 25-field source RF, run one regularized additive mixed-field model, then let their dev receipts select the representation used by one gradient-boosted successor.
5. **Recovery:** freeze that successor decision in a content-addressed capsule, then continue in one fresh controller context. This is one programme continuation, not a second independent start.
6. **Final choice:** the recovered evaluated controller selects one eligible method from public/dev evidence. The root study operator may validate and attest the choice but cannot substitute its own candidate.
7. **Terminal handoff:** refit the selected fixed method once on all public rows, create one `Id,SalePrice` artifact, lock it, and make one external trusted MAE call.
8. **Close:** report the typed feasibility disposition and the complete attempt/launch/lock/scorer/cost census. Do not open `ResearchDone`.

Why `C0`: `B0` leaves the target checks advisory, so a completed trace does not test compulsory integration. `G0` adds graph construction/use before base feasibility is known. `C0` is the smallest existing process that exercises the required gate, preservation, and recovery chain. This is a P0 controller recommendation only. It is not evidence that C is better than B or G.

## One research question

> For this exact House Price development programme, can the C0 compulsory evidence/preservation/capsule process complete a bounded chain in which pinned source structure and each isolated development MAE determine the next representation/model decision, the lineage survives a fresh controller context, and that controller selects one immutable `Id,SalePrice` artifact before a separately trusted external MAE, within fixed caps?

Each transition has one task-specific purpose:

| Transition | Why it matters |
|---|---|
| Pinned source evidence → complete RF R1 | Establish whether the incomplete source scaffold can become a reproducible measured reference. Source shape alone is not performance evidence. |
| RF receipt → additive mixed-field R1 | Test the source-grounded hypothesis that categorical, ordinal, and missing-value structure omitted by the 25-field starter adds useful development information. |
| RF + additive receipts → boosted successor choice | Let real dev evidence choose the successor representation while changing the inductive mechanism. This separates representation value from bagging alone. |
| Successor decision → fresh-context recovery | Test whether content-addressed evidence and a decision capsule are sufficient. Hidden REPL state must not be required. |
| Recovered successor receipt → controller final choice | Test autonomous synthesis of source, validity, dev MAE, and resource evidence. Operator judgment and hidden score are excluded. |
| Locked artifact → external MAE | Test the terminal artifact/scorer handoff without score-based reselection. |

## Exact selected source

The exact task is `snap-stanford/MLAgentBench@5d71205cc20a8e95d43aa7cb7120e89ca3323e31/MLAgentBench/benchmarks/house-price`, derived from Kaggle `home-data-for-ml-course`. It is not `house-prices-advanced-regression-techniques` and does not use the official leaderboard test.

The pinned `prepare.py` resets source row order, writes positions `[0, floor(0.8N))` back as public `train.csv`, makes positions `[floor(0.8N), N)` feature-only `test.csv`, and writes `Id,SalePrice` answers. The starter fixes 25 fields and `random_state=1`, imports RF and MAE, but leaves fit and metrics blank. The source scorer subtracts `SalePrice` positionally and does not validate `Id`; it is not acceptable unchanged.

LF means the number of exact `0x0A` bytes. Every listed source had zero CRLF sequences when read.

| Evidence | Full-file SHA-256 | Bytes | LF | Exact material span |
|---|---:|---:|---:|---|
| `house-price/scripts/prepare.py` | `32f1e4bf49de46818b4bcd98ff1bd407c9ecfd47c96f35ee6e4397603987dba7` | 950 | 23 | L5–L22, excerpt `2826a29d5e35d5133dacce82ac012d9c52d82a57ad5953015d6cdefe67e83d52` |
| `house-price/env/train.py` | `9b264f3821e697c48fd6152b53b5cd55e83f5000e0a52cabf11de7643b700b5b` | 1768 | 40 | L1–L40, excerpt `37ec6aa1fdd934659f87f8e0f7e3af6baf8e89c9f0e3d332e8b9f8b50d4730d6` |
| `house-price/scripts/eval.py` | `610063c5986a5f8674b276db98b97579d481333fdc19563dd1f7b0509b762bb1` | 501 | 16 | L7–L14, excerpt `deb1dcb66460d8505622986ac278b3e39f74b6f95b1a7a161a1be56df1736f86` |
| `house-price/scripts/research_problem.txt` | `9c87fc5edb5067a979042ead668ab5b6f1db96c779d510b6ebcdba26c83fa817` | 429 | 2 | L1–L2, excerpt `7ba670379be617332ef42980180329810fe9bd2a3086285409ab5250f24d6a49` |
| `house-price/scripts/read_only_files.txt` | `899c264a6c0508ceecdf7ecec0c89840be4ff4ad57ee969bac4c1dead1027e74` | 22 | 1 | complete file |
| `house-price/env/data_description.txt` | `356a4670aa688afa8ba44b1365b633fbbac2dae535fe4638532630607d64070d` | 13370 | 523 | structure L81–L108 `1aba7da9300b27afc24e403bda39ca4ad75054ec11cb2a29f66e7503ff7fa55e`; quality/time L152–L178 `baafd54249532eec4098bacc481307b6affd6ead4ded1d3803fb79b2ad1ff569`; sale L499–L523 `37a28801679b29407108d1bfa9800bd14b10743cf4fc1e8def70d8cf4f12eda7` |

No CSV, answer, label, gold, credential, user log, or model payload was read to create this design. Row count, actual fields and values, order, duplicates, missingness, distributions, memberships, and every score remain unobserved.

### Binding records reused

| Record | SHA-256 | LF | Relevant locator |
|---|---:|---:|---|
| `house-price-p0/task-selection-v1.json` | `bd4cc3e982172831d4178570ea36a7670c4a6a3e3efb0f487f50d94c0c18b188` | 56 | L11–L22, excerpt `ba507d25e52a4cd1be2c09d8b78330778c36c769f5075c508de50e4e0078ec32` |
| `house-price-p0/execution-user-authorization-v1.json` | `58fb0d753ff32f483b4317222d01f7c941702ef4f62b923ae515cad0abd8eb7f` | 37 | L2–L37, excerpt `7b85e85e7783ce3e0c15a06e0b76d004aa2bfc0176eb7d949ad0baa106fd7120` |
| `effective-authority-v2.json` | `35334c4c1c4ed9fbc6f10f0902262c2eaef652d70e0021f5737734d1c4622f50` | 48 | L22–L47, excerpt `da9604f5b3aa3e8257cfd1fb08787fd28c216498088ed7be8ea13480d0ec7394` |
| N1–N10 `task-qualification-requirements.json` | `97ba9943c5c4d2c337d54f5d80cb8f2521cdb3deba2ab77c021cbc3d6dad9d60` | 172 | N1 L32–L40; N2–N3 L41–L58; N4–N6 L59–L85; N7–N10 L86–L121 |
| `integration/restored-comparison-intake-v1.json` | `10d3e77257063a61386406f2ea4dbe98f26a3f0ba6b5aad12b85ed1c2c729fd0` | 488 | complete file |
| `integration/restored-candidate-comparison.md` | `6f64a54ffd40f89ffab18ada3d97bc3f1579a173d458e252033034ded5a01562` | 203 | complete file |
| `integration/prime-orx-capabilities.md` | `204c41f9f498507759f365b048704cc37564ae865597a75cc0d0708a10d8c702` | 132 | versions L12–L16; security/capabilities L31–L48; binding L54–L69; no-retry L73–L80 |
| `integration/prime-orx-capabilities.json` | `7852b1a18890412477ace2109ee034be3c110b814909dfc10b698e6c93e8fd91` | 1251 | complete machine record |
| `architecture-selection-record.json` | `9720629cfef7dc51769646792000d8600750a8c3bc6442ae9042153f153e0565` | 117 | C0/B0/G0 L44–L71, excerpt `79df7e4a6384f690fdf5d5a4d1bd952207b22786811f31fb85424340bb7bc31b` |

The integration and parallel copies of the restored comparison and Prime/ORX capability files were byte-identical at read time.

## Outer and inner membership

### Option A — recommended: source positional 80/20

Let `N` be the original raw training row count after `reset_index(drop=True)` and `k=floor(0.8N)`.

- Public development pool: source positions `[0,k)`.
- Hidden assessment: source positions `[k,N)`.
- Preserve source order.
- Before metrics, bind the exact ordered `Id` manifests, feature hashes, hidden-label commitment, `N`, and `k`.

This route preserves the selected MLAgentBench generator. It does **not** establish representativeness. The positional suffix can have order shift, and its labels are reconstructible from a public raw file. Runtime custody and network/cache controls remain necessary.

### Option B — explicit alternative: adapted Id-hash 80/20

Before any outcome or payload-derived distribution review:

1. Canonicalize each unique `Id` as its exact CSV string.
2. Compute `SHA256("ARGO-HP-P0-OUTER-v1|" + Id)`.
3. Sort by digest, then exact `Id` as the tie break.
4. Put the first `floor(0.8N)` rows in public and the remainder in hidden.
5. Bind exact ordered manifests.

This removes dependence on source row order. It also changes the source generator, so the programme must be labelled an adapted ancestry. It does not make public labels secret or prove a representative sample.

**Material decision:** do not silently substitute Option B. The recommended executable route is Option A. Freeze one before metrics or any distribution-based split review.

### Exact inner membership rule

Apply only to the chosen outer public pool, in its current order:

```text
train_test_split(
  rows,
  test_size=0.25,
  train_size=None,
  shuffle=True,
  stratify=None,
  random_state=1,
)
```

Pin the exact scikit-learn version and split code. Generate the ordered inner-train and dev `Id` arrays once before any metric. Record their SHA-256 values, counts, duplicate/missing-ID checks, outer-generator digest, and creation timestamp. Every method uses these exact arrays. No silent re-split is allowed. Exact IDs and counts are currently `null` because no payload was opened.

This entire P0 programme, raw source family, split generator, re-splits, controller exposure, and human exposure are development-only ancestry. Renaming or re-splitting it does not make it eligible for P2. General shared libraries are recorded but are not by themselves the source-family key.

## Concrete method sequence

All train/dev computations are R1. Preprocessing is fit on inner train only. Receipts retain full-precision MAE; the source's rounded console text is not evidence. There is one fixed stochastic seed and no hyperparameter or best-seed archive.

### B0: completed source RF

Use the exact starter list:

`MSSubClass, LotArea, OverallQual, OverallCond, YearBuilt, YearRemodAdd, 1stFlrSF, 2ndFlrSF, LowQualFinSF, GrLivArea, FullBath, HalfBath, BedroomAbvGr, KitchenAbvGr, TotRmsAbvGrd, Fireplaces, WoodDeckSF, OpenPorchSF, EnclosedPorch, 3SsnPorch, ScreenPorch, PoolArea, MiscVal, MoSold, YrSold`.

Fit a median imputer on inner train, then:

```text
RandomForestRegressor(
  n_estimators=100,
  criterion="squared_error",
  max_depth=None,
  min_samples_split=2,
  min_samples_leaf=1,
  max_features=1.0,
  bootstrap=True,
  random_state=1,
  n_jobs=1,
)
```

The receipt contains train/dev MAE, exact memberships/config, validity, ORX identity/log hashes, wall/CPU/peak RSS/cost, and only permitted aggregate diagnostics. This is a complete source-faithful reference. It is not called strong until measured.

### L1: regularized additive mixed-field family

Use all source-described fields except exact `Id` and `SalePrice`. Freeze the schema before metrics: categorical fields are object/string columns plus `MSSubClass`; remaining fields are numeric.

- Numeric: median imputer + `StandardScaler`.
- Categorical: most-frequent imputer + `OneHotEncoder(handle_unknown="ignore")`.
- Estimator: `Ridge(alpha=10.0, fit_intercept=True, solver="lsqr", tol=1e-4, max_iter=10000)`.

This is mechanism-distinct from RF and tests additive use of source-described fields. It is one fixed candidate, not a search.

### G2: gradient-boosted successor family

After B0 and L1 receipts, the initial evaluated controller must issue one successor decision:

- If L1 is valid and its dev MAE is strictly lower than B0, use L1's all-field mixed representation, with a bounded dense transform.
- Otherwise, use the B0 25-field numeric imputed representation. An invalid L1 remains in the denominator and deterministically selects the numeric branch.

Then run one:

```text
GradientBoostingRegressor(
  loss="absolute_error",
  n_estimators=200,
  learning_rate=0.05,
  max_depth=3,
  min_samples_leaf=5,
  subsample=1.0,
  max_features=None,
  random_state=1,
)
```

This changes the mechanism from bagging and additive linear prediction to stage-wise boosting. The representation branch is the observation-dependent successor decision.

### Recovery and final refit

After D1, write a canonical capsule containing the question, source locators, split/config hashes, B0/L1 receipt IDs, D1 and rationale, remaining caps, and prohibited inputs. Start one fresh controller context with only the frozen controller prompt and capsule/evidence paths. It must re-hash the capsule, enumerate the cited receipts, restate D1, and state the remaining budget before it can request G2.

After the G2 receipt, the **recovered evaluated controller** selects one eligible method it expects to minimize external SalePrice MAE. It must cite source/dev/validity/resource evidence and explain its choice. This is intentionally the controller policy, not automatic archive `argmin` and not root judgment.

The chosen fixed pipeline is then refit once on the full public 80% and emits the only scoreable artifact. No new selection metric is created. A final-refit failure yields no artifact; another candidate cannot replace it.

## Operator/controller boundary and single lock

The root study operator freezes authority and manifests, stages permitted inputs, admits/reconciles launches, validates receipts, administers custody, and writes the immutable lock tuple. The root does **not** rank candidates. The lock must copy the controller's `method_id` and `artifact_id` unchanged. A schema-invalid choice can be rejected, but it cannot be replaced.

The evaluated controller sees public source evidence, inner dev receipts, permitted aggregate diagnostics, resource receipts, and the recovery capsule. It never sees hidden suffix labels, scorer bytes/secrets, the full reconstructible raw labeled file, or external MAE before lock.

The lock binds:

`programme_id, controller_session_id, selection_record_sha256, method_id, artifact_id, ORX project/experiment/run, recorded commit, relative path, SHA-256, size, ordered-Id-manifest SHA-256, config SHA-256, lock time, protocol fingerprint`.

Fallback is **none**. No choice or incomplete lock by deadline means `NO_LOCK`, no scorer call, no numerical efficacy observation, and retention in the full programme denominator. Mutation after lock is rejected. There is no second scorer call or score-based reselection.

## Hidden-data custody: exact minimum

Prime 0.9.2 child sessions, their `session_dir`s, the shared repository cwd, and ORX 0.1.120 local run directories are not a trusted security boundary. They are same-user functional separation. Repository package version 0.9.1 is not evidence for the installed 0.9.2 runtime, and the exact resident daemon build was not independently queried.

A sealed P0 needs, at minimum:

1. A distinct OS security principal or remote scoring service/VM owns the original full labels, suffix labels, and any scorer secret bytes.
2. The evaluated controller, all Prime/RLM children, and the ORX training process have no read/traverse permission to those paths.
3. They also lack inherited credentials, container socket, `ptrace`/process-inspection rights, writable mount or symlink routes, readable backups/caches, and a network route that can fetch the reconstructible full labeled file during the attempt.
4. Training receives only public prefix labels and suffix features.
5. A narrow one-way scorer ingress accepts exactly one content-addressed locked artifact and returns only a typed aggregate receipt.
6. That boundary independently enforces protocol/task/artifact identity, deadline, expected ordered IDs, and one-call policy, and records actor exposure.
7. Exact-controller negative access tests pass before the controller starts. A file hash proves identity, not secrecy.

If this protection is unavailable, an `OPEN_CUSTODY_FUNCTIONAL_ONLY` P0 can still measure the source→R1→decision→recovery→lock mechanics, gate/capsule behavior, and latency/cost/failure census. It cannot support an independently hidden MAE, non-leakage, blinding, P1/P2 admission, or architecture efficacy claim. If the full endpoint requires independent scoring, close `BLOCKED_HIDDEN_CUSTODY` even if an open-custody diagnostic MAE is computed. Never call an agent-readable same-user file “sealed.”

## Artifact and scorer contract

The one artifact is UTF-8 CSV with exact ordered columns `Id,SalePrice`. It must contain the exact ordered hidden-feature `Id` strings, preserve leading zeros, and have no extra, missing, reordered, or duplicate IDs. `SalePrice` values must be valid finite numbers. Negative finite predictions remain mathematically valid; no unstated model rule clips them.

Planning parser ceilings are 100,000 rows, 16 MiB, 64 UTF-8 bytes per `Id`, 64 UTF-8 bytes per prediction field, and exactly two columns. Freeze exact arithmetic/parser/rounding code and its environment hash before launch.

The metric is:

```text
MAE = sum_i abs(prediction(Id_i) - hidden_SalePrice(Id_i)) / N
```

It is in original SalePrice dollar units, lower is better. There is no log transform, ranking, Kaggle submission, or LLM judge.

Return one of `SCORED`, `ARTIFACT_INVALID`, `SCORER_ERROR`, `LOCK_MISMATCH`, or `NOT_CALLED`. An artifact-caused schema/ID/nonfinite failure is `ARTIFACT_INVALID`. Bad reference/contract/service state is `SCORER_ERROR`. Neither returns a number. A valid receipt binds the opaque scorer contract, artifact lock, ordered-ID manifest, expected/submitted/aligned counts, status/reason, MAE only when scored, arithmetic policy, scorer code/environment digest, and time. It returns no labels or per-row residuals.

Static mocks can certify parser/math behavior, mutation rejection, one-call state transitions, fail-closed null/mismatch handling, capsule serialization, and census typing. They cannot certify OS secrecy, network denial, absence of direct launch, real task compatibility, runtime sufficiency, model quality, complete billing, or `ResearchDone`.

## Proposed resource stages

No task runtime, RAM, cost, failure rate, or power calibration exists. The read-only inventory reports 8 logical CPUs, 16 GiB shared RAM, Python 3.14.5, dependencies absent, and no selected backend. These are host facts, not workload fit.

### Q0: small non-efficacy probe

Run only after its own exact approval if it performs model fits:

- deterministic synthetic schema-only table;
- 256 rows and at most 8 levels per categorical field;
- generated target; no task CSV, hidden labels, hidden scorer, or network;
- one ORX launch, no retry;
- 1 logical CPU, 2 GiB RAM, 0 GPU;
- 300 s task self-time, 600 s stage wall time;
- 100 MiB output, 0 model calls, 0 scorer calls, 0 external currency spend.

Purpose: test frozen environment imports, resource/self-time enforcement, the three pipeline paths, ORX log/receipt handoff, and strict mock artifact/scorer behavior. A pass does not predict full-data resources or efficacy and does not admit P0. The real P0 still needs the final immutable contract review; the already granted task/data/P0 intent need not be requested again.

### Recommended P0 planning ceiling

| Item | Hard ceiling proposal |
|---|---:|
| Programme attempts / independent repeats | 1 / 0 |
| Controller contexts | 2: initial + one fresh continuation, same unit |
| Retained direct RLM children / max depth | 3 / 1 |
| Controller model calls / input+output tokens | 10 / 120,000 |
| Network source retrievals | 0 |
| Dev candidate evaluations | 3: RF, Ridge, boosted tree |
| Core R1 ORX launches | 4: three dev + one final refit |
| Repair R1 launches / total ORX launches | 1 / 5 |
| Hidden scorer calls / locked artifacts | 1 / 1 |
| CPU / RAM / GPU per run | 4 logical / 8 GiB / 0 |
| Task self-time per run / campaign wall | 1,200 s / 10,800 s |
| Total output | 1 GiB |
| Incremental billed currency | USD 15 |
| Human scientific interventions after start | 0 |

A strict alternative removes the repair slot: total ORX launches 4, model calls 8, tokens 80,000, campaign wall 7,200 s, and USD 10. It has cleaner failure semantics but one known integration defect closes the attempt.

These numbers are planning caps, not predicted needs or evidence of power. The three development evaluations come from the baseline plus two mechanism-distinct families. The fourth core launch is the one final refit. This is not the predecessor's 4/2/1 template.

At most one repair is allowed only after a uniquely bound terminal failure and before the first valid dev metric. It may correct a pinned import/version/path/manifest/serialization defect. It cannot change split, features, estimator family/parameters, or selection rule. Preserve the failed receipt and consume the slot. Poor metric, timeout/resource exhaustion, hidden score, no-lock, scorer error, or uncertain launch is not repairable in P0.

`--force` is forbidden. An uncertain RLM/ORX launch is never retried or replaced. Reconcile by deterministic child name and exact ORX project/experiment/commit. Zero, multiple, or mismatched candidates remain `UNKNOWN/BLOCKED`.

ORX local has no launch timeout flag. The task command or another already certified boundary must hard-enforce self-time, CPU, RAM, tokens, and currency. Prime usage accounting is partial. If a proposed hard cap cannot be enforced and observed, preflight blocks rather than calling the campaign bounded. Use Prime and the existing ORX supervisor only; do not add a supervisor or lifecycle registry.

## Unit, outcome, missingness, and census

The unit is **one assigned HP-P0 programme attempt**. Candidate R1s and two controller contexts are nested events. Two same-task contexts or starts are not independent observations, do not give `n=2`, and do not estimate reliability or variance.

The terminal task outcome is the external SalePrice MAE of the one controller-selected locked artifact, observed only for scorer status `SCORED`. The feasibility endpoint is a typed process disposition, not a favorable MAE threshold:

- `FEASIBLE_SEALED_END_TO_END`
- `OPEN_CUSTODY_FUNCTIONAL_ONLY`
- `BLOCKED_PRELAUNCH`
- `INFEASIBLE_WITHIN_CAP`
- `UNKNOWN_BLOCKED`
- `SCORER_MISSING_OR_ERROR`

A sealed success requires certified custody; valid B0, L1, and G2 R1 receipts; the observation-dependent D1; successful fresh-context recovery; controller-owned final choice; valid final refit and lock; one valid external score receipt; a complete census; and no cap exceedance. It remains descriptive P0 evidence.

| Case | Denominator and numerical treatment |
|---|---|
| No choice/lock by deadline | Retain attempt; `NO_LOCK`; scorer not called; MAE missing; no baseline fallback. |
| Invalid artifact | Retain attempt; `ARTIFACT_INVALID`; no replacement or MAE. |
| Scorer reference/contract/service error | Retain locked attempt; `SCORER_ERROR`; no MAE or imputation. |
| Uncertain launch/result | Retain attempt; `UNKNOWN_BLOCKED`; reconcile only; no automatic retry or fabricated failure. |
| Valid poor model | Retain actual MAE. It is a scientific outcome, not invalidity. |
| Right-censored at cap | Retain observed state, censor time, cause, and cost; no complete-case deletion or arbitrary utility floor. |

Close counts for screened eligibility, assigned attempts, controller contexts, R1 requests/allows/denials, launch requests, bound run IDs, terminal runs, valid dev results, decisions, recovery attempts/passes, final choices/refits, artifact manifests/locks, scorer requests/receipts, and numerical scores.

Record per-event latency for intent→gate, gate→launch request, request→run-ID binding, binding→terminal, terminal→log import, dev result→decision, fresh context→recovery attestation, artifact→lock, lock→score, and programme start→disposition.

Record gate requests/allows/denials, stale/null/mismatch rejections, R2 violations, unclassifiable actions, observed bypass attempts, and the authoritative coverage denominator. “0 bypasses” is allowed only if an independent boundary observes the complete declared surface. Otherwise report `NOT_OBSERVED`.

Record model calls and observable input/output/cache tokens, ORX launches, wall/CPU, peak RSS, GPU seconds, disk bytes, billed currency, operator minutes, interventions, right-censoring, custody status, and UNKNOWN duration. Missing telemetry is `NOT_OBSERVED`, not zero. One programme has no sampling CI, treatment-effect estimate, population reliability estimate, or power claim.

## MUE timing

P0 has no numerical MUE. Its MAE is descriptive, and feasibility uses the typed chain requirements above.

Before any P1 arm-labelled contrast is calculated or revealed, the root operator must document P0 exposure, propose the task MUE, obtain user/domain-owner approval, and obtain independent timing review. An outcome-independent option is:

```text
MUE_MAE_USD = DeltaC / (H * V)
```

`DeltaC` is precommitted incremental control cost over a decision horizon, `H` is the precommitted number of house predictions, and `V` is externally justified currency value per one-dollar reduction of absolute error per prediction. These inputs come from an operational value plan, not observed P0/P1 MAE or apparent headroom. If the inputs are unavailable, keep numeric MUE `null` and prohibit a material-benefit confirmation claim.

## Minimum executable contracts still required

Before launch, freeze and hash:

- exact data/terms/access and development-only ancestry receipts;
- chosen outer and exact inner memberships;
- exact task code, config, baseline/candidate/final-refit code, prompts, and controller model/thinking;
- Python/platform/architecture, pandas/numpy/scikit-learn and transitive environment image/lock, BLAS identities, and thread settings;
- no-install and no-network policy during the attempt;
- ORX 0.1.120 project, experiment, recorded commit, fixed argv/cwd/env/input/output, and log/artifact handoff for every R1;
- hard self-time/CPU/RAM/token/currency enforcement receipt;
- trusted preparer/scorer principal, denial tests, one-call boundary, scorer code/environment/arithmetic policy;
- selection prompt, no-fallback lock rule, invalid/missing/retry/repair rule, and full census schema;
- immutable task-bound review receipt and final protocol fingerprint.

Proposed deterministic thread settings are `PYTHONHASHSEED=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and `NUMEXPR_NUM_THREADS=1`. Exact environment versions remain `null`; no dependency was installed or imported here.

## Decisions and remaining gaps

Already approved and not to be requested again at the same scope: task choice, applicable terms/data-access category, and bounded P0 execution intent.

Still explicit:

1. Freeze positional source split (recommended) or adapted Id-hash split.
2. Freeze `C0` (recommended), `B0`, or `G0` as the P0 controller. This is not an empirical architecture selection.
3. Provide a distinct-UID/remote hidden boundary for the sealed endpoint, or accept only `OPEN_CUSTODY_FUNCTIONAL_ONLY` with reduced claims.
4. Accept or modify the proposed resource ceiling and certify that it is hard-enforced. A material paid/backend increase needs new approval.
5. Root must finish the already authorized terms acceptance and private download receipts without exposing credentials or payload.
6. Root must complete code/scorer/environment/command binding and independent immutable review. Therefore there is no launch from this document.

At a terminal disposition, wall cap, launch cap, repair cap, loss of custody, unresolved launch identity, or consumed scorer call, stop. Preserve every attempted and unselected R1 receipt and all costs. Do not restart, silently replace, open P1/P2, select an architecture, resume native construction, or mark `ResearchDone` from P0 alone.
