# HousePrice P0 A2 synthetic capsule independent review v1

## Verdict

**NOT ADMITTED as the synthetic capsule producer.** Exact source/test hashes match and all six Python 3.11 filesystem tests pass. Exact membership, normal tamper controls, partial retention, and production allowlist isolation are sound. One API/contract blocker and one late destination-integrity gap remain.

Reviewed exact bytes:

- `combination_capsule.py` — `6308ec12dfda04675dfb857ece8bf2fb72f9f816d27ea72c149fb5c2e8dd2c56`
- `test_combination_capsule.py` — `9abfc339bf2912bc5b51258c5b60868de281c3758afa9ccf3679e1e6bda7a198`

## SCAP-01 — BLOCKER — protected-root policy cannot be enforced by the frozen API

The contract says the destination must be outside raw-data, auth, profile, controller, and public roots “supplied by root.” The frozen API is only:

```text
materialize_synthetic_capsule(destination, members)
```

It receives no protected-root identities. `_new_private_path` can enforce canonical absent path, owner/mode, and no Git ancestor, but it cannot distinguish an otherwise private profile/raw/control directory.

A bounded filesystem probe created a private `profile/` directory outside Git and materialized `profile/synthetic`. The function accepted it and returned a 29-file tree.

**Correction:** either add exact root-owned `protected_roots`/path-policy input with DirectoryIdentity checks and pairwise non-overlap, or explicitly move this rule to a separately frozen caller precondition and remove the claim that the materializer enforces it. The current text and API cannot both be true.

## SCAP-02 — HIGH — a same-size late destination mutation can be sealed as the returned tree

Each copied source is reopened immediately after `_write_new`, which catches write-time corruption. After that loop, the code syncs directories and calls `capture_tree`. It checks only counts, symlink count, and total bytes against the sources. It does not compare the final captured member digests to the original source bindings.

A bounded omission probe mutated the first copied file to different bytes of the same length immediately before the real final `capture_tree`. Materialization succeeded, `destination_matches_source=false`, and the returned SourceTree sealed the mutated destination digest.

**Correction:** after all writes and before returning, re-open every destination member relative to a held root, compare exact bytes/hash/size against the original FileBinding/data, verify the four initializers are still empty, then capture and revalidate the tree without an intervening mutation window. At minimum, derive and compare the expected destination tree digest from the held source bytes/modes rather than accepting counts/total alone. Add this exact post-copy same-size mutation control.

## Scoped passes

- `EXACT_MEMBERS` equals the contract's 25 paths; no missing, extra, duplicate, or lookalike path is accepted.
- Four package initializers are generated empty; source members cannot replace them.
- Source FileBindings are opened through the bounded no-follow reader; source symlinks/hash mismatch reject.
- Destination writes are no-replace mode 0600 under mode-0700 directories; copied bytes are immediately reopened.
- Caps are 25 sources, 1 MiB/file, 8 MiB total, 160 entries, depth 8, path 4096.
- Existing/partial destinations remain and cannot be reused automatically.
- Production `materialize_namespace` still rejects `test_bridge.py`; no production global allowlist changed.
- No copied Python source was imported or executed.

## Validation

Exact six-test command:

```text
test_destination_is_private_outside_git_and_copied_bytes_are_reopened (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_destination_is_private_outside_git_and_copied_bytes_are_reopened) ... ok
test_exact_capsule_has_twenty_five_sources_and_four_empty_initializers (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_exact_capsule_has_twenty_five_sources_and_four_empty_initializers) ... ok
test_missing_extra_duplicate_and_hash_tampered_sources_fail_before_destination (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_missing_extra_duplicate_and_hash_tampered_sources_fail_before_destination) ... ok
test_production_allowlist_is_not_broadened_by_synthetic_copy (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_production_allowlist_is_not_broadened_by_synthetic_copy) ... ok
test_symlink_source_is_rejected_and_partial_copy_cannot_be_reused (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_symlink_source_is_rejected_and_partial_copy_cannot_be_reused) ... ok
test_tampered_destination_bytes_and_unlisted_extra_entry_do_not_get_sealed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_tampered_destination_bytes_and_unlisted_extra_entry_do_not_get_sealed) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.077s

OK
```

Two bounded omission controls:

```json
{
  "late_destination_tamper": {
    "accepted": true,
    "destination_matches_source": false,
    "destination_sha256": "7b2fda42ecb82a84ece2091dd515b793de27379fa29e389f1b6e0c0407584adf",
    "returned_tree_sha256": "e5d73aaf6ceec9a726b78687e2d39a249d5a3c0a82a9fcdf17bb220bedbc2b34",
    "source_sha256": "e71824fd58b73edaa4f08c24f06eda96d922530db18634d634291e00cfa906ad"
  },
  "protected_profile_parent": {
    "accepted": true,
    "destination": "/private/var/folders/yx/hh120pwn38g8vm2l1gsljd640000gn/T/capsule-review-q6czmk10/profile/synthetic",
    "tree_files": 29
  }
}
```

Probe source SHA-256: `12792f28837808f2b4569b30a052c70dae961bcac4fc8f512cd756223803ac5b`. Full source is embedded in the JSON review.

## Scope

Filesystem synthetic only. No copied-source import, real fixture, Git, socket, Prime/Faux, process, ORX, Docker, provider, auth contents, data, scoring, P0, npm, commit, or nested worker.
