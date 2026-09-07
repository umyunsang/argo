# HousePrice Option A2 combination-fixture independent review v1

## Decision

**NEEDS ONE P1 REPAIR before the synthetic fixture may run.**

The fixture writes the fixed second solution and parented intent, but it does not bind the second admitted run back to those expected hashes. A self-consistent changed solution/intent pair with `parent_run_id=null` is accepted, marked DONE, reported eligible, and returned in the three sealed trees.

The six supplied mock tests pass. One additional bounded mock-only negative reproduces the cross-binding gap. No real `NativeHarness`, Bridge, Git, socket, fake ORX, controller, provider/auth, Docker, data, or P0 ran.

## Frozen inputs

| File | Bytes | SHA-256 | Root hash match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/combination_fixture.py` | 16993 | `fc89bb22e42b1c7171a645176162863556243578b7d906022e19e3c9d1e25c72` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_combination_fixture.py` | 15201 | `d032b4b0e1ed5c5449fe97e6526e83dce4f7b1eac1a4a9836c08464a95b605b5` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-combination-fixture-report-v1.json` | 7008 | `2bb7e243c231586d6250b00bb61e7031221b9a1c3536d6bf4e69ef6d5831a8b7` | yes |

All three files were read in full. Their archived copies are byte-identical.

Contracts:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-combination-fixture-source-v1.json` — `582f6a67782ec1a2c4825645bbd9aadfb81b1c550760ff8273d2fd46ec41fc61` (4086 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-combination-fixture-output-addendum-v1.json` — `a30991607ef3038e7a257ae430167ed4998a0805b10d7cbdbe9eeaff7780b59b` (1848 bytes)

## Finding

### CFX-001 — P1 — the second run is trusted for its own solution and intent hashes

Locations: `combination_fixture.py:99-119,252-280`; `test_combination_fixture.py:287-305`.

The fixture constructs the correct public literal `SECOND_SOLUTION` and canonical second intent with:

- `solution_sha256 = sha256(SECOND_SOLUTION)`;
- `parent_run_id = first["run_id"]`.

It validates the two `write_solution` response records. But after `_request_run`, it only validates that the returned run, stored binding, and later views agree with each other. It never requires:

```python
second["solution_sha256"] == sha256(SECOND_SOLUTION)
second["intent_sha256"] == sha256(intent_bytes)
```

Line 119 instead seeds `expected` from `second["solution_sha256"]`. The source tree is later captured, but no member-specific comparison binds the captured `solution.py` or `intent.json` bytes to the fixed expected values.

Independent negative control used only the existing fake harness/Bridge. After both correct write responses, the mock changed the actual second solution and intent to a different self-consistent pair with no parent before returning the second run. `prepare_fixture` accepted it:

```text
accepted=('00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000102')
fixed_second_solution_matched=False
second_parent_matched_first=False
self_consistent_hash=True
```

This is not a claim that the reviewed real Bridge currently mutates writes. It shows the root fixture's stated fixed-second-candidate/parent proof is only producer agreement, not independent cross-binding.

Required repair:

1. Compute `second_solution_sha256` and `second_intent_sha256` from the already constructed bytes.
2. Before `mark_done`, require the second run and matched binding to carry both exact hashes.
3. Reopen or otherwise independently bind the final source `solution.py` and `intent.json` bytes before capturing/returning `source_tree`.
4. Add a negative where the second run/binding/views are mutually consistent but differ from the fixed second bytes and parent intent. Require fixed error, one close, and retained base.

## Passing controls

Subject to CFX-001:

- Fresh absent base under a canonical same-owner `0700` parent is required. Existing, non-private, Git-nested, and raw/auth/profile component paths reject before harness construction.
- One `NativeHarness(base, rows=292)` is constructed, its known owned directories are made `0700`, and its production-enabled deployment is written as canonical bounded `O_EXCL` config with file and parent fsync and read-back binding.
- Exactly two `request_R1_run` actions occur. There is no third, final, lock, or cancel action.
- Each returned run has strict fields, UUIDs/hashes and dev phase; one stored binding is matched; RUNNING is observed before `mark_done`.
- Final dev/public views require two distinct expected IDs, rows 292, `valid=true`, MAE `0.000000`, status DONE, zero final attempts, and one remaining opportunity.
- Research is nonempty, bounded, and hash-matching.
- Source, trusted-state, and bridge-state directory identities are private children of the owned base. Three bounded no-symlink `SourceTree` records are captured. Read-only final views must leave all three unchanged.
- Duplicate IDs, missing DONE, missing eligibility, action errors, and config collisions raise only `COMBINATION_FIXTURE_INVALID`, close the harness once, and retain the partial base/evidence.
- Returned `close()` is idempotent and never deletes evidence.

## Report denominator and archive

All three archive files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-combination-fixture-v1` were read in full:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `a2-combination-fixture-report-v1.json` | 7008 | `2bb7e243c231586d6250b00bb61e7031221b9a1c3536d6bf4e69ef6d5831a8b7` |
| `combination_fixture.py.snapshot` | 16993 | `fc89bb22e42b1c7171a645176162863556243578b7d906022e19e3c9d1e25c72` |
| `test_combination_fixture.py.snapshot` | 15201 | `d032b4b0e1ed5c5449fe97e6526e83dce4f7b1eac1a4a9836c08464a95b605b5` |

The report correctly states six mock-only tests and no actual fixture. Its initial stub is an implementation witness: five tests and three negative subcases fail while one ownership rejection passes. It is not evidence that the final source had every important cross-binding mutation test. The report does not include CFX-001's self-consistent drift control.

Dependency bytes still match the report:

| Dependency | SHA-256 | Match |
|---|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py` | `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/grading.py` | `bf8b2deb3f4113c4b3f734928642a37fd84410546bc0c22725e8f495d6ccc0be` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/source_closure.py` | `e4b0b8732d48d2ecbcd57b6d9e01dbf88200ab5e57bf12426d28d22017ae4466` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/staging.py` | `9813081081af6b128a1c91eb06c4ba07fa6c260eee8984c708c3094e3a635800` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_bridge.py` | `5a45ef18dd0486a5b5eb9dccfe1090c1258a3b42fbb2768a63b749bd0ef424c2` | yes |

`test_bridge.py` is a frozen test-only dependency. These identity matches do not turn mock calls into real NativeHarness/Bridge execution.

## Exact executions

### Six supplied mock tests

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture
test_action_error_closes_once_without_deleting_partial_evidence (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_action_error_closes_once_without_deleting_partial_evidence) ... ok
test_config_collision_closes_once_and_preserves_collision (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_config_collision_closes_once_and_preserves_collision) ... ok
test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_duplicate_ids_missing_done_or_missing_eligibility_close_once_and_preserve_base) ... ok
test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_existing_nonprivate_and_nested_git_bases_are_rejected_before_constructor) ... ok
test_success_returns_exact_owned_snapshot_and_idempotent_close (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_success_returns_exact_owned_snapshot_and_idempotent_close) ... ok
test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_fixture.CombinationFixtureTest.test_two_exact_dev_requests_use_current_second_hash_and_no_other_run_actions) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.038s

OK
EXIT_CODE=0
```

### Independent bounded current-intent control

Fixture: `/tmp/hp-a2-combination-fixture-review-ka86olu5/current_intent_control.py` — `9301ae2c86c3f3ee21862106a8acd8a7b2c10f9904d3f3f539cb699068124b24` (2224 bytes).

```text
$ PYTHONPATH=/Users/um-yunsang/argo-paper-orx /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B /tmp/hp-a2-combination-fixture-review-ka86olu5/current_intent_control.py
accepted=('00000000-0000-0000-0000-000000000101', '00000000-0000-0000-0000-000000000102')
fixed_second_solution_matched=False
second_parent_matched_first=False
self_consistent_hash=True
EXIT_CODE=0
```

The control patched both `NativeHarness` and `load_bridge_from_config` with existing fake classes. It made no real Git/socket/fake-ORX/Bridge/process call. Complete source is preserved in the JSON report.

## External conditions and nonclaims

1. Root must bind the real reviewed Bridge/test-harness/source identities. Self-consistent run/binding/view fields are not independent authority for fixed seed bytes.
2. The three returned trees cover source/trusted/bridge state only. Future acceptance rederives them after the one model read and separately binds other fixture roots/output.
3. This fixture source is excluded from the production namespace. A later root clearance is separate authority.
4. FEF-001 remains open in the Faux entry until the independent expected schema hash `553e...` and repaired bytes are reviewed.
5. No actual fixture, NativeHarness, Git, socket, fake ORX, Bridge, provider/auth, Docker, controller, data, score, or P0 ran. Live P0 remains held.
