# Long-horizon contract witnesses

**Evidence class: `LOCAL_OFFLINE_SPECIFICATION`.**

These are illustrative, engineered specifications for a literature synthesis.
They are not benchmark task outcomes, statistical evidence, evidence of TREE or
TYPED efficacy, or a reproduction of any paper. Passing tests show only that this
small validator implements the stated examples. They do not validate a native
runtime, a model, or an autonomous research system.

## Run

From the repository root, use the documented research-oracle interpreter:

```text
python3 -B experiments/argo_workflow_followup/long_horizon_contract_witnesses/test_witnesses.py -v
```

The only runtime dependencies are Python standard-library modules. The test reads
local JSON. There is no network, model call, external code execution, private
instance data, or DiscoveryWorld access. `-B` prevents bytecode cache writes.
No native runtime change is part of this catalogue.

## Eight required boundaries

Each ID below is an entry in `fixtures/catalogue.json`.

| ID | Engineered evidence | Required decision |
| --- | --- | --- |
| `bytes_recoverable_not_exposed` | Archived bytes match the original digest, but exposed byte spans omit the required span. | Recoverability is true; exposure and eligibility are false. |
| `reachable_wrong_scope` | All graph references resolve and the verifier is reachable, but its scope is syntax, not robustness. | Closure and reachability cannot authorize the claim. |
| `cached_wrong_artifact_version` | Cached bytes match, but artifact and version identifiers differ. | Reject cache reuse. |
| `negative_unchanged_context` | A negative observation is bound to the same prior and current context. | Preserve the exclusion. |
| `negative_relevant_change` | The dataset regime changes on a declared relevant key. | Require recheck, not permanent blacklist or automatic acceptance. |
| `negative_irrelevant_change` | Only display mode changes; dataset and metric stay fixed. | Preserve the prior exclusion. |
| `historical_best_survives_correction` | A correction withdraws the initially preferred archive member. | Preserve historical best and history; shrink the eligible set. |
| `inferred_workspace_not_original` | Inferred workspace bytes equal the expected bytes, but provenance is inferred. | Do not promote the files to original replay. |

There are 12 additional controls. They include allowed exposure, correctly scoped
verification, exact cache reuse, unchanged archive eligibility, and original-file
replay. Other controls isolate a wrong digest, artifact, version, unbound negative
observation, missing graph node, or changed replay bytes. `fixtures/malformed.json`
contains 14 missing/malformed evidence cases. They must raise `ValueError`, not
silently authorize a decision. The suite has 10 test methods and 34 fixture cases.

## Contract and trust limits

- `validator.validate(record)` takes `kind` and `evidence`. It never reads fixture
  IDs or expected answers. It returns decisions without mutating the input.
- Evidence fields are exact. Missing or unknown fields, missing provenance,
  malformed hex, invalid spans, and empty replay inventories fail closed.
- Byte integrity is calculated from embedded hex bytes with SHA-256. The original
  digests are fixture trust anchors, not authenticated source receipts.
- Exposure means union coverage of a half-open required byte interval. It does
  not mean that an agent attended to or understood those bytes.
- Graph closure means that all supplied edge endpoints and the named claim and
  verifier exist. Scope matching is exact membership of the required scope token.
  Neither the graph nor that token proves that a real verifier was run or was sound.
- Cache reuse here requires exact artifact ID, version, and byte digest. This is a
  narrow identity specification, not a full cache policy or result truth check.
- Negative observations bind the prior context by SHA-256 of sorted, compact JSON.
  Context values are nonempty strings. Relevant keys are a supplied, reviewed
  policy, not learned by the validator. Equal context schemas are required. A new
  or removed context key requires a new relevance review. `exclude` means only
  exclusion under the current scoped context. `recheck` records no future outcome.
- Archive `priority` values 2 and 1 are arbitrary ordering labels, not measured
  scores. The historical-best label uses maximum `(priority, id)` across the
  supplied archive. Corrections apply to a copied eligibility map in list order.
  The original entries and historical ordering stay unchanged.
- Replay eligibility checks only the supplied file inventory and provenance labels.
  It does not authenticate those labels or establish inventory completeness. Inferred
  provenance blocks original replay even when the byte digest matches.

## Observed red/green receipt

`test_receipt.json` records the command, source/fixture hashes, stub text, and short
observed outputs. The failing-first stub returned `{}` for every input: 10 methods
ran and 34 assertions failed, including subtests (exit 1). After implementation,
the same test file and fixtures passed all 10 methods (exit 0). Python code plus
tests total 244 lines. No effectiveness measurement is inferred from these counts.

The delegated worker ran only the targeted Python test. After delegation, the
root agent independently reran it (10/10, exit 0) and reported a passing
repository-wide `npm run check` (exit 0): 953 files checked, no fixes applied,
installer render passed, and browser smoke passed. These root-reported checks
are recorded separately from the worker's observed red/green outputs.
