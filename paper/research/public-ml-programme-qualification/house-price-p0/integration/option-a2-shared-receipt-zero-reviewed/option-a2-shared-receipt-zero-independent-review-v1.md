# HousePrice Option A2 shared receipt-zero independent review v1

## Decision

**SCOPED PASS: the shared exact-integer-zero gap is resolved.**

`_valid_prior_process_receipt` now accepts only `type(returncode) is int` and value `0`. The focused regression passes for integer zero and rejects boolean, float, null, string, list, mapping, and missing values. No new finding was identified in this one-predicate scope.

This is not broad Bridge or P0 readiness. The original Bridge 21-test/Faux-ORX suite was intentionally not run. No lifecycle request, process, provider, auth, data, Docker, ORX, native change, source edit, npm, commit, or actual P0 was used.

## Frozen inputs

| File | Bytes | SHA-256 | Validation match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/bridge.py` | 127776 | `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/test_prior_process_receipt_types.py` | 1368 | `46e836c47e0278efee815e220bb5cf8e76ec29ff4b32b090e5341e01b986d9bf` | yes |

Scope and validation:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-shared-receipt-zero-repair-v1.json` — `be651a3dbd5c9dd0f949f719fe495e2ff1a9c17622ca08dfa7db7286123f30bb` (816 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-shared-receipt-zero-validation-v1.json` — `8fc714067a4a98a386a4e0fb3a015382a4ff16770371adee2b7118ee96a475fb` (1209 bytes)

The new Bridge file and focused test were read in full. The archived old Bridge was also read in full. The only Bridge byte delta is:

```diff
-            value.get("returncode") != 0 or type(value.get("started_monotonic_ns")) is not int or
+            type(value.get("returncode")) is not int or value["returncode"] != 0 or
+            type(value.get("started_monotonic_ns")) is not int or
```

## Shared helper closure

Location: `bridge.py:1951-1963`.

The type check is evaluated before indexed access. Therefore a missing value safely returns `False`; it does not raise `KeyError`. Python booleans and floats no longer compare equal to accepted zero because their exact types are not `int`.

The helper still requires the existing exact receipt keys/schema/authority/status/terminal reason, strict monotonic times, clean resource/census/cleanup fields, canonical session directory, and session-file containment. Those controls are unchanged.

## Continuation caller

Location: `bridge.py:1884-1891`.

`_verify_context_checkpoint` reopens the prior process receipt from the handoff `FileBinding`, decodes it, and directly calls `_valid_prior_process_receipt`. A boolean/float/missing/nonzero return code now makes the helper return `False`, and the caller raises `UNCERTAIN_NO_AUTOMATIC_RETRY` before context admission. No caller bypass or alternate zero comparison was introduced.

The already-reviewed local `phase_completion.py` remains at `4153bb2d4b92d8602211220913309fd73a995de3b0f83cd28107128896c73f98` and independently checks exact integer zero. This shared fix closes other helper callers rather than replacing that local defense.

## Failing-first and green evidence

All five archive files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-shared-receipt-zero-v1` were read in full:

| Archive file | Bytes | SHA-256 |
|---|---:|---|
| `01-false-float-red.log` | 2592 | `421d22122ba2c52a1d4deb33b3a6db3a77243796ce3457875aee493c828f6ecb` |
| `02-int-zero-green.log` | 323 | `fe1956a5de69af121dae24df9d488c8658c1a15f97bfd7781fbe560edd3c2c98` |
| `bridge-pre-zero-guard.py.snapshot` | 127724 | `979c84adc265541c816a01eca39ec775eaa6374a7bc4495a2366b6ca6eefdd03` |
| `bridge.py.snapshot` | 127776 | `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558` |
| `test_prior_process_receipt_types.py.snapshot` | 1368 | `46e836c47e0278efee815e220bb5cf8e76ec29ff4b32b090e5341e01b986d9bf` |

- The old-source RED is behavioral: `False` and `0.0` both returned `True` and failed their `assertFalse` subtests.
- The repaired one-test GREEN accepts true integer `0` and rejects `False`, `True`, `0.0`, `None`, `"0"`, list, mapping, and missing.
- Old/new Bridge snapshots match the validation's before/after hashes. The focused test snapshot matches the reviewed test.

## Exact independent execution

```text
$ /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -m unittest -v experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_prior_process_receipt_types
test_only_exact_integer_zero_proves_success (experiments.argo_workflow_followup.public_ml_apparatus.house_price_runtime.test_prior_process_receipt_types.PriorReceiptTypeTest.test_only_exact_integer_zero_proves_success) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
EXIT_CODE=0
```

Result: 1/1 focused Python 3.11 mock/file test passed. It called only the shared predicate against a fabricated complete receipt/session fixture. It did not call the Bridge lifecycle, completion publication, gate evaluator, provider, process, ORX, or Docker.

## Scope limits

1. This review covers only exact `returncode` typing and the direct continuation-checkpoint caller.
2. It does not re-review the rest of the 127,776-byte Bridge or supersede prior Bridge reviews.
3. Root-bound receipt/session `FileBinding` values remain caller authority; a self-consistent model-provided receipt is not accepted provenance.
4. Driver, completion, deployment, namespace, full integration, OAuth/provider/data/ORX/Docker, immutable production receipts, and actual P0 remain separate gates.
5. Live P0 remains held.
