# HousePrice Option-A trusted I/O independent final-byte review v2

**Scoped verdict: local revision still required; external launch gates remain open; no P0 launch.**

Reviewed frozen bytes:

- `trusted_io.py` `224766acb3dc1884d1a803d6a911d5c33889e85b2419b17cb9849aab3bd0e5b1`
- `test_trusted_io.py` `293afb5d1266b9fdda99e64e4baf53a89a7f3f01c0ad0391c829fa3e4fdd2e9f`
- `trusted-io-report.json` `7476911bc13cdf166e2e45ae08d988cccac9fa3f4f5707087e771b94056b325d`

All three matched the root-supplied hashes before testing and before this review. The v1 reviews remain unchanged at hashes `182f3a8f...3bcf8b` and `841cd577...f3d36`. I changed no source, test, native, or shared file. I used no real data, provider/auth, ORX run, Docker, paid call, or nested agent.

## V1 disposition

- **HPIO-001 verified fixed:** admission writes a canonical content-addressed private closure before publishing state. Selection loads an admitted stored closure rather than active files. Candidate A remained selectable in a separate interpreter after candidate B and a `final_refit` intent; the private final copy matched A while active source differed. Stored-byte tamper returned `STATE_CORRUPT`.
- **HPIO-002 verified fixed:** the next file receives the remaining aggregate budget. For 8+8+8 bytes under file cap 10 and closure cap 15, the read spy saw `[8]` only and then `LIMIT_EXCEEDED`.
- **HPIO-004 verified fixed:** final identity now derives inside the transaction from stored selection closure/code/receipt/task/environment/protocol plus phase/config/manifests. Different selections produced different identities. A changed selected task made the persisted identity fail after reload.
- **HPIO-005 verified fixed:** bounded snapshot bytes rederive every file hash and framed closure. Forged fields/bytes return `INVALID_VALUE`; admission also compares the complete freshly opened snapshot.
- **HPIO-006 conditionally strengthened:** a live object pins canonical source/state device+inode and rejects later pathname replacement. This cannot witness a wholesale trusted-root replacement before a new process starts. Stable roots/ancestors/mounts across restarts remain an external TCB condition.
- **HPIO-007 verified corrected:** the snapshot test no longer claims T16. The report explicitly leaves actual extension/root T16 evidence open.
- **HPIO-003 remains an external launch condition, not a local code defect:** an arbitrary well-shaped `DevResultReceipt` is still accepted because the type is designed as a trusted-root input. No actual receipt is opened here. Launch evidence must prove that the bridge opens the real eligible receipt at the expected root and constructs the object internally, never from controller/self-attested values.

## New findings

### HPIOV2-001 — MEDIUM: final lock reload accepts inconsistent duplicated config

`lock_final_artifact` copies execution config and both manifest hashes from the refit record (`trusted_io.py:510-512`). `_read_state` cross-checks lock selection, execution identity, run, task, environment, and protocol (`906-923`) but omits these three duplicated fields.

After creating a valid final lock, I replaced only `final_lock.execution_config_sha256` with another valid hash. A new `TrustedIo` instance accepted the state and returned the tampered hash. The durable `FinalArtifactLock` can therefore contradict the final-refit record and the execution identity it carries.

Required fix: compare `lock.execution_config_sha256`, `lock.outer_training_manifest_sha256`, and `lock.hidden_features_manifest_sha256` to the final-refit record during `_read_state`. Add restart regressions for all three.

### HPIOV2-002 — LOW: failed publication leaves unaccounted store directories

`_store_snapshot` creates `.snapshot-*` but has no handled-exception cleanup (`571-592`). A forced mid-store failure left one temporary directory after a later successful admission. Admission also writes/renames a full snapshot before `_write_state` checks `max_state_bytes` (`334-336,926-931`). With `max_state_bytes=400`, four canonical snapshot directories existed while only two admissions fit; two calls returned `LIMIT_EXCEEDED`.

This is resource hygiene, not evidence of duplicate ORX launch. The frozen outer attempt count may bound production exposure, but that bound is external to this module.

Required fix: clean a known private temporary directory after handled pre-rename failure. Preflight state size before storing, or enforce an explicit total snapshot count/byte cap derived from the frozen attempt budget. Define reconciliation for a valid post-rename/pre-state orphan without automatic external-run retry.

## Restart and trust boundary

A live state-root replacement returned `UNSAFE_FILE`. A fresh interpreter after the entire root was replaced re-anchored the new empty directory and created another `PENDING` admission. This is not fixable by an identity stored only inside the replaced root. The deployment must preserve and protect the expected canonical root across restarts, or provide an external identity witness.

A complete content-addressed store written before a handled state-publication failure was verified and reused by a new interpreter. It then published one `PENDING` record. A tampered stored solution was rejected after a separate interpreter started.

Twenty-three tests and these negatives prove local mechanics only. They do not prove actual receipt/artifact provenance, ORX exactly-once execution, root stability, container/scorer custody, or T16.

## Exact validation

Environment: `Python 3.9.6`; `Darwin 25.5.0 arm64`; `/usr/bin/python3`; `os.O_NOFOLLOW=256`; `os.O_DIRECTORY=1048576`.

Disposable exact-copy directory: `/tmp/hp-optiona-independent-audit-v2-gliyfuxk`.

### Compile

```text
$ /usr/bin/python3 -m py_compile trusted_io.py test_trusted_io.py
[exit 0; no output]
```

### Authored 23 tests

```text
$ /usr/bin/python3 test_trusted_io.py
test_hpio001_historical_snapshot_is_private_and_selectable_after_final_intent (__main__.TrustedIoTest) ... ok
test_hpio001_incomplete_private_snapshot_fails_closed_and_remains (__main__.TrustedIoTest) ... ok
test_hpio001_tampered_private_snapshot_cannot_be_selected (__main__.TrustedIoTest) ... ok
test_hpio002_aggregate_cap_rejects_before_second_descriptor_read (__main__.TrustedIoTest) ... ok
test_hpio004_final_identity_changes_with_stored_code_and_task (__main__.TrustedIoTest) ... ok
test_hpio005_forged_snapshot_fields_are_rederived_and_rejected (__main__.TrustedIoTest) ... ok
test_hpio006_anchored_source_and_state_root_replacement_fail_closed (__main__.TrustedIoTest) ... ok
test_snapshot_identity_is_opened_bytes_not_intent_self_attestation (__main__.TrustedIoTest) ... ok
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

----------------------------------------------------------------------
Ran 23 tests in 1.188s

OK
```

### Independent bounded negatives

Script SHA-256: `04c596efbe0c74095213b023eb241ef697569450e208d708a80fb5a454143610`

```text
$ /usr/bin/python3 independent_negative_fixtures_v2.py
aggregate_cap=LIMIT_EXCEEDED;read_sizes=[8]
forged_snapshot=INVALID_VALUE
historical_after_restart=ACCEPTED;selected_a=True;private_copy_a=True;active_is_different=True
stored_byte_tamper_after_restart=STATE_CORRUPT
selection_identity_tamper_after_restart=STATE_CORRUPT
mid_store_failure=UNSAFE_FILE;published_before=False;restart=PENDING;stale_temp_before=1;stale_temp_after=1
publication_failure=LIMIT_EXCEEDED;stored_before=True;state_before=False;restart=PENDING
state_cap_admissions=['ACCEPTED', 'ACCEPTED', 'LIMIT_EXCEEDED', 'LIMIT_EXCEEDED'];persisted_admissions=2;stored_directories=4
live_state_root_replacement=UNSAFE_FILE
new_process_reanchors_replaced_state=PENDING
different_selection_identity=True
final_lock_duplicate_config_tamper=ACCEPTED;returned_tampered=True
fabricated_well_shaped_receipt=ACCEPTED
```

### Separate-interpreter restart cases

Script SHA-256: `38baa7ea410f81c9d1898470a28077c6a036596df70987760341cfc7883f3f0d`

```text
$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py prepare-history /tmp/hp-optiona-independent-audit-v2-gliyfuxk/history-case
prepared_a=dbcfa9490bb81b9db25e59b44fbb6a137881d34c452a81dbf524a0254e003c1c;prepared_b=1756bd26c78aaa0fcccd0eadd000d16f4183cd5e61a6f8b1d1fd9359a7706305
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py select-history /tmp/hp-optiona-independent-audit-v2-gliyfuxk/history-case
restart_selection=62bdb208de6dc6b169a467f646f50ca39e6c203fa6f6732431624d8dec1e77fb;copy_matches=True;active_differs=True
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py prepare-store-tamper /tmp/hp-optiona-independent-audit-v2-gliyfuxk/store-tamper-case
tampered_store=dbcfa9490bb81b9db25e59b44fbb6a137881d34c452a81dbf524a0254e003c1c
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py select-store-tamper /tmp/hp-optiona-independent-audit-v2-gliyfuxk/store-tamper-case
restart_store_tamper=STATE_CORRUPT
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py prepare-publication-failure /tmp/hp-optiona-independent-audit-v2-gliyfuxk/publication-case
publication_failure=LIMIT_EXCEEDED;stored=True;published=False
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py recover-publication /tmp/hp-optiona-independent-audit-v2-gliyfuxk/publication-case
restart_publication_recovery=PENDING;closure=dbcfa9490bb81b9db25e59b44fbb6a137881d34c452a81dbf524a0254e003c1c
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py prepare-root-replacement /tmp/hp-optiona-independent-audit-v2-gliyfuxk/root-replacement-case
root_original_pending=dbcfa9490bb81b9db25e59b44fbb6a137881d34c452a81dbf524a0254e003c1c
[exit 0]

$ cd /tmp/hp-optiona-independent-audit-v2-gliyfuxk && /usr/bin/python3 restart_fixtures_v2.py replace-root-and-restart /tmp/hp-optiona-independent-audit-v2-gliyfuxk/root-replacement-case
replaced_root_restart=PENDING;closure=dbcfa9490bb81b9db25e59b44fbb6a137881d34c452a81dbf524a0254e003c1c
[exit 0]
```

The restart selection uses a synthetic trusted-receipt-shaped tuple. It verifies stored-byte behavior, not HPIO-003 receipt provenance.

Not tested: privileged mount/bind-mount or device creation; real bridge receipt/artifact provenance; ORX; provider/auth; raw data; Docker; generated code; final runner; prediction artifact/scorer; actual T16 extension evidence.

## Required disposition

1. Keep P0 unlaunched and native ARGO construction paused.
2. Fix HPIOV2-001 before treating the final lock as canonical persisted evidence.
3. Resolve or explicitly bound HPIOV2-002 through cleanup/caps and the frozen root attempt limit.
4. Keep HPIO-003, stable-root-across-restart, actual T16, and all remaining bridge/ORX/container/scorer checks as launch gates.
5. Re-run exact authored and independent fixtures on any new hashes.
