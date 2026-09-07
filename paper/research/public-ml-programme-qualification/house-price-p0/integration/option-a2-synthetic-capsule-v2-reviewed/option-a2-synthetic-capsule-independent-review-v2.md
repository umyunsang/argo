# HousePrice P0 A2 synthetic capsule independent review v2

## Verdict

**SCOPED PASS for the synthetic filesystem materializer; not whole-case or P0 admission.** Exact repaired hashes match. SCAP-01 and SCAP-02 are closed. All 11 Python 3.11 tests and the same two independent counterexamples pass.

Reviewed exact bytes:

- `combination_capsule.py` — `434aed7b76fafc228e902996ac455624cb6f60acd8cda58d5f478cf994bd9b11`
- `test_combination_capsule.py` — `472f48d2a68bdd08d1f0d7285de9e474bbe5bd0910a3f744036ce213d0d035b3`

## Finding disposition

### SCAP-01 — CLOSED

The API now requires `protected_roots=CapsuleProtectedRoots(raw, auth, profile, controller, public)`. All five fields must be valid existing DirectoryIdentity values. Each root is opened with `O_DIRECTORY|O_NOFOLLOW`; held and named directory type/owner/device/inode are checked before destination creation and again before return. Destination equality and either-direction ancestry with every protected role reject. Protected roles may overlap each other, as the contract permits, and their contents are never enumerated or opened.

The same profile-parent counterexample now rejects before creating the destination.

### SCAP-02 — CLOSED

The materializer retains all 25 opened source byte strings and independently derives the exact `argo-source-tree/v1` recipe digest for:

- 25 mode-0600 regular source files;
- four empty mode-0600 initializers;
- four fixed mode-0700 package directories.

It holds the destination root identity, recursively compares the exact entry set/bytes/modes/owner/single-link and descriptor/name identities, reopens original source bindings, requires the captured tree digest and root identity to match the independent recipe, repeats exact recipe verification after capture, runs `verify_tree`, and rechecks root/protected identities. Counts and total bytes are no longer accepted as sufficient provenance.

The same same-size mutation immediately before capture now rejects and retains the partial destination.

## Scoped controls

- Exact 25-member allowlist and four generated empty initializers remain unchanged.
- Missing, extra, duplicate, lookalike, hash-tampered, symlink, late initializer, root replacement, extra entry, and source/destination mutation paths reject.
- Required policy, bool/inode misuse, changed protected root, and all five destination overlaps reject.
- Production `materialize_namespace` remains unchanged and still rejects test-only `test_bridge.py`.
- Existing caps, modes, full writes, directory sync, partial retention, and no-retry behavior remain.
- No protected-root contents or copied Python modules are read as payload/imported/executed.

## Validation

Exact 11-test command:

```text
test_destination_is_private_outside_git_and_copied_bytes_are_reopened (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_destination_is_private_outside_git_and_copied_bytes_are_reopened) ... ok
test_exact_capsule_has_twenty_five_sources_and_four_empty_initializers (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_exact_capsule_has_twenty_five_sources_and_four_empty_initializers) ... ok
test_late_initializer_or_destination_root_change_does_not_pass_final_recipe (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_late_initializer_or_destination_root_change_does_not_pass_final_recipe) ... ok
test_late_same_size_destination_tamper_is_not_resealed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_late_same_size_destination_tamper_is_not_resealed) ... ok
test_missing_extra_duplicate_and_hash_tampered_sources_fail_before_destination (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_missing_extra_duplicate_and_hash_tampered_sources_fail_before_destination) ... ok
test_production_allowlist_is_not_broadened_by_synthetic_copy (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_production_allowlist_is_not_broadened_by_synthetic_copy) ... ok
test_protected_directory_contents_are_never_read (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_protected_directory_contents_are_never_read) ... ok
test_protected_profile_is_not_a_valid_capsule_parent (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_protected_profile_is_not_a_valid_capsule_parent) ... ok
test_required_protected_identities_reject_missing_changed_or_overlapping_destinations (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_required_protected_identities_reject_missing_changed_or_overlapping_destinations) ... ok
test_symlink_source_is_rejected_and_partial_copy_cannot_be_reused (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_symlink_source_is_rejected_and_partial_copy_cannot_be_reused) ... ok
test_tampered_destination_bytes_and_unlisted_extra_entry_do_not_get_sealed (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_combination_capsule.SyntheticCapsuleTest.test_tampered_destination_bytes_and_unlisted_extra_entry_do_not_get_sealed) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.190s

OK
```

Same two independent counterexamples:

```json
{
  "late_same_size_tamper": {
    "partial_destination_retained": true,
    "rejected": true
  },
  "protected_profile_parent": {
    "destination_created": false,
    "rejected": true
  }
}
```

Probe source SHA-256: `e42aac614b36b159e614219fadce6334ae7e931654f05f53b465524e1179a087`; full source is embedded in the JSON review.

## Remaining boundary

Root still owns completeness/correctness of the five protected identities and all approved source FileBinding hashes. This materializer is not atomic execution or hostile same-UID protection. Partial destinations remain terminal. CFX001, pre-import TCB, driver/fixture/acceptance implementation, combined closure, and explicit one-case clearance remain separate.

## Scope

Synthetic filesystem only. No copied-source import, real repository materialization, fixture, Git, socket, Prime/Faux, process, provider, auth content, data, ORX, Docker, P0, npm, commit, or nested worker.
