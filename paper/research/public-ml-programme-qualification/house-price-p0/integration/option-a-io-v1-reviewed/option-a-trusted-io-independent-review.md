# HousePrice Option-A trusted I/O independent final-byte review

**Verdict: BLOCKED — revise and re-review; no P0 launch.**

Reviewed frozen bytes:

- `trusted_io.py` `69b34c17a1fe0883723af8a157980d9801ec406ec69bee47f7a190e8c7ae3ba3`
- `test_trusted_io.py` `89c888e7bf3db5819f472767a15ce31857d6e73d885b155dafdaa076a9d9786e`
- `trusted-io-report.json` `d15c9158bfc3a65534f378cf91af0d20a979328bb970363035bb43b67da166ec`

The hashes matched the parent-supplied values at intake and immediately before this review was written. I modified no implementation, test, native, or shared file. I ran no real data, provider/auth, ORX scientific run, or Docker operation. The original 17 tests pass from an exact disposable copy; this is test reproduction, not security proof.

## Findings

### HPIO-001 — BLOCKER: prior eligible candidates cannot be selected

`admit_intent` records only a closure hash and admission state (`trusted_io.py:314-331,763-770`). It does not persist the opened candidate bytes. `select_final_method` reopens the active source and requires that current closure to equal the selected snapshot (`376-380`). It creates `final-solution.py` only after that check (`388-401`).

Behavior: after admitting candidate A, changing only `intent.json` to `final_refit` made selection of A return `SNAPSHOT_CHANGED`; no candidate bytes existed in private state. A later candidate has the same problem. This violates the approved right to select any eligible prior dev candidate and can change the scientific outcome.

Required fix: persist exact opened `solution.py`, `research.md`, and `intent.json` bytes atomically at dev admission, keyed by the canonical closure. Select a real-receipt-eligible stored closure and copy its stored solution inside one transaction. Do not restore mutable source through multiple writes and do not add a run registry.

### HPIO-002 — HIGH: aggregate closure cap is checked after allocation

`_snapshot_from_fd` reads all three files into a tuple (`524-528`) and only then checks their sum (`529-530`). Three 8-byte files with `max_file_bytes=10` and `max_closure_bytes=15` caused 24 bytes in three `os.read` calls before `LIMIT_EXCEEDED`. An 11-byte individual file under a 10-byte cap caused zero reads, so the per-file pre-read check works.

Required fix: decrement a remaining closure budget and pass `min(max_file_bytes, remaining_budget)` to each descriptor read. Reject from `fstat` before reading the file that crosses the remaining aggregate budget. Account for chunk/join copy overhead in the frozen cap.

### HPIO-003 — LAUNCH GATE: real receipt provenance exists only in the trusted-root assumption

`_permitted_receipt_tuples` checks dataclass type and hash shape only (`572-581`). Selection checks membership in those caller-provided tuples (`382-387`) but opens no receipt. A fabricated receipt tuple selected successfully. The selected code itself remained safe because the method reopened the source and matched the opened code hash.

This is acceptable only as the documented TCB boundary. Before launch, evidence must show that the root bridge opens the actual dev receipt at the expected trusted root, derives receipt/closure/code, checks eligibility, and constructs the internal `DevResultReceipt`. Values must not come from controller JSON or the record being “verified.” The current 17 tests fabricate receipts and cannot prove this.

### HPIO-004 — MEDIUM: final-refit identity omits approved key fields

The addendum requires phase, selection receipt, selected code, task, environment, and execution config. `_final_execution_identity` includes phase, receipt, config, outer-training manifest, and hidden-features manifest (`238-247`), but omits stored code/task/environment/protocol. Two different selections produced the same execution identity when given the same receipt token/config/manifests.

Required fix: derive the identity inside the transaction from stored `FinalSelection` plus typed phase/config/manifests. Include selected code, task, environment, and protocol rather than relying on an unstated transitive receipt binding.

### HPIO-005 — MEDIUM: caller-built Snapshot is not checked for canonical consistency

`_validate_snapshot_shape` checks only four 64-hex strings (`558-570`). It does not recompute file hashes or the framed closure from `Snapshot` bytes. A snapshot with the real closure token but false file hashes and forged bytes was accepted by admission and selection. Selection still copied re-opened current code, so this fixture did not replace final code.

Required fix: bound and rederive all hashes from snapshot bytes, or replace caller-constructible snapshots with private stored records. This should be solved together with HPIO-001.

### HPIO-006 — TCB CONDITION: roots are not pinned

Direct root symlinks, exact-child symlinks, hardlinks, FIFO, and in-place descriptor mutation fail closed. Exact ASCII names and per-file pre-read caps work. However, each operation reopens roots by pathname (`834-838,952-963`). Symlinked ancestors are followed; source-directory replacement was followed; replacing the private state directory allowed another PENDING admission. The code has no no-xdev/mount check. I did not attempt mounts because no privileged operations or Docker were allowed.

This matches the report's explicit trusted-root/same-UID exclusion, but it is not hostile-root resistance. Root integration must prove stable absolute paths and private, non-replaceable ancestors, or the implementation must pin directory FDs/device+inode and state a deliberate mount policy.

### HPIO-007 — MEDIUM: the report's T16 label is not actual T16 evidence

`test_t16_snapshot_hash_is_opened_bytes_not_intent_self_attestation` changes `intent.json` and compares local hashes (`test_trusted_io.py:429-437`). Actual T16 requires extension pre/post byte hash, size, mtime upper bound, loaded absolute source path, prompt/image/argv/tool census, and mismatch blocking. The report's limits section correctly says that evidence is outside this module, but its control table still assigns this unrelated local check to T16.

Relabel it as a local snapshot control. Leave T16 open until the extension/root lane produces the required receipt.

## Control disposition

- **T07 partial pass under TCB:** flat ASCII enum, absolute/traversal/NUL/confusable denial, final-component nofollow, regular/single-link checks, FIFO rejection, per-file cap, in-place mutation detection, and atomic same-directory replace. Aggregate cap and root anchoring fail/are conditional as above. Unknown JSON properties belong to bridge validation.
- **T09 local pass under TCB:** cooperating processes produce one PENDING admission; restart preserves uncertainty; stale lock fails closed. This is not external ORX exactly-once, and state-root substitution is excluded.
- **T14 partial pass for the current active candidate:** current opened solution bytes are copied before source-tool freeze. Later tool writes return `FINALIZED`; a direct source-path change did not alter the private copy. Final runner integration must consume that copy. Prior-candidate selection and actual receipt/artifact provenance remain open.
- **Typed final phase:** an arbitrary `"development"` phase returned `INVALID_VALUE`. One PENDING final-refit fence and bound-run requirement are present, subject to the identity finding.
- **T16 not tested here:** no extension load/pre-post/loaded-path evidence exists in these files.

## Exact validation

Environment: `Python 3.9.6`; `Darwin 25.5.0 arm64`; `os.O_NOFOLLOW=256`; `os.O_DIRECTORY=1048576`.

Disposable directory: `/tmp/hp-optiona-independent-audit-hh04v0bc`. It contains exact copies of the two source files with the reviewed hashes.

### Compile

```text
$ /usr/bin/python3 -m py_compile trusted_io.py test_trusted_io.py
[exit 0; no output]
```

### Authored tests

```text
$ /usr/bin/python3 test_trusted_io.py
test_t07_descriptor_identity_detects_fixture_swap_during_read (__main__.TrustedIoTest) ... ok
test_t07_naive_prefix_control_and_flat_name_rejection (__main__.TrustedIoTest) ... ok
test_t07_size_and_expected_hash_controls (__main__.TrustedIoTest) ... ok
test_t07_symlink_hardlink_and_fifo_controls (__main__.TrustedIoTest) ... ok
test_t07_write_rejects_existing_unsafe_target (__main__.TrustedIoTest) ... ok
test_t09_crash_stale_transaction_lock_fails_closed (__main__.TrustedIoTest) ... ok
test_t09_distinct_immutable_closures_can_be_admitted (__main__.TrustedIoTest) ... ok
test_t09_final_refit_is_one_fence_across_processes_and_restart (__main__.TrustedIoTest) ... ok
test_t09_parallel_processes_admit_one_and_only_one (__main__.TrustedIoTest) ... ok
test_t09_reload_pending_admission_is_uncertain_not_retried (__main__.TrustedIoTest) ... ok
test_t14_final_lock_binds_trusted_inputs_and_is_single_use (__main__.TrustedIoTest) ... ok
test_t14_final_lock_detects_final_code_fixture_mutation (__main__.TrustedIoTest) ... ok
test_t14_final_refit_requires_selection_binding_and_bound_run (__main__.TrustedIoTest) ... ok
test_t14_parallel_select_write_cannot_mutate_selected_code (__main__.TrustedIoTest) ... ok
test_t14_selection_requires_matching_permitted_receipt_and_freezes_writes (__main__.TrustedIoTest) ... ok
test_t14_stale_snapshot_cannot_select_mutated_bytes (__main__.TrustedIoTest) ... ok
test_t16_snapshot_hash_is_opened_bytes_not_intent_self_attestation (__main__.TrustedIoTest) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.350s

OK
```

### Independent bounded fixtures

Script SHA-256: `2c9c6fab978f70419e95948439b9001b42e3c234a489014a3a6ecb4ea9665c60`

Cases: pre-read individual cap; aggregate read-count cap; direct root symlink; ancestor symlink; source-root replacement; state-root replacement; prior selection after final intent; malformed snapshot/fabricated receipt; source copy after freeze; arbitrary final phase; identity across different selections.

```text
$ /usr/bin/python3 independent_negative_fixtures.py
individual_oversize=LIMIT_EXCEEDED;os_read_calls=0;bytes_read=0
aggregate_oversize=LIMIT_EXCEEDED;closure_cap=15;os_read_calls=3;bytes_read=24
direct_root_symlink=UNSAFE_FILE
symlinked_ancestor=ACCEPTED;solution_sha256=62bdb208de6dc6b169a467f646f50ca39e6c203fa6f6732431624d8dec1e77fb
source_root_replacement_followed=True
state_root_replacement_second_pending=True
prior_candidate_after_final_intent=SNAPSHOT_CHANGED;persisted_candidate_bytes=False
malformed_snapshot_admit=PENDING;fabricated_receipt_select=ACCEPTED;selected_opened_code=True
post_selection_tool_write=FINALIZED;private_copy_unchanged=True
arbitrary_final_phase=INVALID_VALUE
different_selected_code=True;different_task=True;same_execution_identity=True
```

Not tested: privileged mount/bind-mount or device-node creation; real root bridge/receipt; ORX lifecycle; provider/auth; raw data; Docker; generated code; final runner; prediction artifact/scorer; actual T16 extension evidence.

## Required disposition

1. Do not approve these frozen bytes for launch.
2. Fix HPIO-001 and HPIO-002. Align identity and snapshot canonicality. Correct T16 traceability.
3. Prove real receipt derivation and trusted-root deployment in the root integration lane.
4. Rerun the authored suite and the independent negatives on the new hashes.
5. Keep P0 unlaunched and native ARGO construction paused.
