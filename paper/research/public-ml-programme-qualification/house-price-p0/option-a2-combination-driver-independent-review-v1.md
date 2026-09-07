# HousePrice P0 A2 combination driver independent review v1

## Verdict

**NOT ADMITTED for whole-case freeze or execution.** Exact source/test hashes match and all eight owned Python 3.11 mock tests pass. Admission, typed fixture close, one process call, and bounded evidence writes are implemented in the intended shape. Two root-boundary blockers and one final-evidence integrity gap remain.

Reviewed exact bytes:

- `combination_driver.py` — `2e34562fe47aabedf196b9c6583eb724f30681eff61306bc681a5912c57fe5c3`
- `test_combination_driver.py` — `3bb1b8014d2bd4bbf4825ac823f204f5698c1c8c2876dab8322871a6f47d350d`

## CDRV-01 — BLOCKER — case-root protected-location policy is absent from config and code

The combination source contract requires `case_root` outside raw-data, auth, user-profile, controller, and public roots. `CombinationCaseConfig` and the pre-import case-config encoding contain only the case path and three source trees. `run_case` calls `_new_private_path`, which checks canonical parent ownership/mode and Git ancestry but has no protected-root identities.

A bounded all-effects-mocked probe set `case_root` to a child of a private `user-profile/` directory. Source verification was mocked as in the owned tests. The driver created the case, called the mocked controller once, and returned `VERIFIED_SYNTHETIC_COMBINATION`.

**Correction:** add a required root-owned protected-root policy to `CombinationCaseConfig` and the fixed pre-import config, preferably the already frozen five-role DirectoryIdentity shape. Verify it in the external preflight and again before case creation/final return. Bind it into `case-admission.json` and `case-receipt.json`. Do not infer roles from path names or read protected contents.

## CDRV-02 — BLOCKER — the 160/180-second case budget starts after source verification

`run_case` calls `_verify_sources(config)` before assigning `started = time.monotonic()`. That verification re-traverses the synthetic namespace, frontend seed, and up-to-256-MiB installed Prime tree. Its elapsed time is therefore absent from:

- the pre-controller 160-second stop;
- the final 180-second stop;
- final `elapsed_seconds`, despite the output contract calling it monotonic total.

A bounded mocked-clock probe charged 170 seconds inside source verification. Because the clock baseline was taken afterward, the driver still called the mocked controller and returned verified.

**Correction:** latch the monotonic case start at `run_case` entry, before input/source verification. Check the 160-second ceiling before case admission/fixture and again immediately before the controller. Final elapsed must cover all run_case validation, preparation, controller, acceptance, and cleanup. External pre-import TCB time should remain separately recorded rather than silently folded into zero.

## CDRV-03 — HIGH — a VERIFIED receipt is not closed over its referenced files at publication

The driver obtains `metadata`, `current`, process/gate/config bindings, calls the pure acceptor, closes the fixture, and writes `case-receipt.json`. It does not reopen those FileBindings after acceptance or fsync the metadata's artifact parent. The final receipt can therefore claim verified while referencing a file missing at return.

A bounded mock acceptor deleted only the metadata file after receiving the expectation and returned PASS. The driver returned `VERIFIED_SYNTHETIC_COMBINATION`; its final receipt contained the metadata FileBinding, but that path no longer existed.

**Correction:** after assessment and typed cleanup, before a verified final publication, reopen every referenced FileBinding and rederive its hash/size/mtime under the held directory identities. Recheck source/state trees and gate/session equality as appropriate. Ensure the Faux metadata parent directory is fsynced (or copy the small metadata into the bounded evidence closure). Any missing/changed reference must downgrade to NOT_ADMITTED before final receipt serialization.

## Scoped passes

- Preexisting case root returns `ALREADY_ATTEMPTED` without writes or mocked process call.
- Source mismatch returns before case creation.
- Case admission is O_EXCL before fixture/process work; partial fixture state remains.
- Exactly one synthetic process call receives the same observer's callable guard and the 20-second abort Event.
- Normal config is not executed; synthetic config is a two-frontend-field replacement.
- Typed fixture close is called once. Unconfirmed/partial close forces CLEANUP/CLEANUP_UNCONFIRMED and is bound in receipt v2.
- Rejected assessment retains one process attempt and cannot pass.
- Evidence writer enforces exact names/caps/modes, loops short writes, fsyncs, reopens, retains partial files, and forbids retry.
- The final receipt excludes raw session/data/prediction/auth/fake-ORX payloads.

## Validation

Exact eight-test command:

```text
test_bad_source_fails_before_case_creation (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_bad_source_fails_before_case_creation) ... ok
test_evidence_writer_rejects_caps_completes_short_writes_and_retains_partial (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_evidence_writer_rejects_caps_completes_short_writes_and_retains_partial) ... ok
test_existing_case_cannot_start_or_write (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_existing_case_cannot_start_or_write) ... ok
test_fixture_error_preserves_admission_without_process_or_exception_payload (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_fixture_error_preserves_admission_without_process_or_exception_payload) ... ok
test_one_synthetic_process_uses_guard_and_typed_cleanup_before_receipt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_one_synthetic_process_uses_guard_and_typed_cleanup_before_receipt) ... ok
test_partially_created_fixture_with_unconfirmed_close_is_not_generic_failure (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_partially_created_fixture_with_unconfirmed_close_is_not_generic_failure) ... ok
test_rejected_assessment_retains_one_attempt (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_rejected_assessment_retains_one_attempt) ... ok
test_unknown_cleanup_or_failed_assessment_never_passes (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_driver.CaseDriverTest.test_unknown_cleanup_or_failed_assessment_never_passes) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.056s

OK
```

Three bounded targeted controls:

```json
{
  "case_root_inside_profile": {
    "accepted": true,
    "case_root": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/hp-case-driver-mock-ld6yizyy/user-profile/case",
    "process_calls": 1,
    "status": "VERIFIED_SYNTHETIC_COMBINATION"
  },
  "metadata_missing_at_verified_return": {
    "binding_present": true,
    "file_exists": false,
    "process_calls": 1,
    "status": "VERIFIED_SYNTHETIC_COMBINATION"
  },
  "source_verification_elapsed_excluded": {
    "accepted": true,
    "process_calls": 1,
    "simulated_pre_source_seconds": 170,
    "status": "VERIFIED_SYNTHETIC_COMBINATION"
  }
}
```

Probe source SHA-256: `4d00e2c5e97404a1c733ef94e0b9fe6e422ff4ba75522f6c44d1b9add727245d`. Full source is embedded in the JSON review.

## Dependency scope

Faux frontend, repaired fixture close/deadline/CFX001, acceptance, pre-import TCB, and actual gate/session event order remain separate dependencies. Their declared interfaces were reviewed for coupling, but unfinished or source-only dependency state is not promoted to whole-case evidence. The accidentally collected 11 PhaseDriver tests in the original missing-module phase remain preparation cost, not independent driver coverage.

## Scope

All fixture/environment/controller/Timer/Bridge/Prime/Faux effects were mocked. No actual `prepare_fixture`, `_prepare_environment`, CLI/main, `run_controller`, Timer, Git, socket, Docker, provider, auth, data, ORX, P0, old core suite, npm, commit, or nested worker.
