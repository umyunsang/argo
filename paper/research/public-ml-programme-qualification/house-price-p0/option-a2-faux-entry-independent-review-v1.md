# HousePrice Option A2 Faux entry independent review v1

## Decision

**NEEDS ONE P1 REPAIR before the synthetic combination capsule.**

The wrapper enforces six ordered tool names and exact property-name sets, but not the exact six tool schemas it claims. Stable drift in property types, required fields, descriptions, or other parameter keywords is hashed and published instead of rejected.

The five mock tests and targeted TypeScript check pass. This remains test-only source review, not actual Prime/Faux/provider/process/P0 evidence.

## Frozen inputs

| File | Bytes | SHA-256 | Match |
|---|---:|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/a2-combination-frontend.ts` | 9580 | `cc03a228690ca176a9ee8970c203ac610b487f79a6a81e077f68c5aba0e73da4` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/test-a2-combination-frontend.ts` | 10852 | `09e3b30e3adf0580ca18ef1c6eccdf6d6215810ddaa29c45b0655b9172aab7fa` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/a2-combination-frontend-report-v1.json` | 8901 | `82801c0e4bda39ade4d458a8fa5a73411a821bd55fdbb8bf39217ba7dc0964d2` | yes |

Both TypeScript files and the report were read in full. Archived copies are byte-identical.

Contracts/design read:

- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-faux-entry-source-scope-v1.json` — `d8f2aec3147d059c470b56cd9b0c5dc0878c909e518cd959866530323a7fdff3` (2301 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-combination-design-v1/a2-production-combination-design-v1.md` — `8a53de03d1af328ed97e5d7afbc8758c80db57c04ce8de31fdf7d7899481b011` (16743 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-combination-design-v1/a2-production-combination-design-v1.json` — `7157b0f45f21dd9d134c63d46040703f7f42ca3f03120740a530aa5f61d957b4` (25223 bytes)
- `paper/research/public-ml-programme-qualification/house-price-p0/option-a2-combination-design-disposition-v1.json` — `5e26cc730bf8ef84eaa4819d7ab5bc77268329f90d73953d48014fdbe383db` (3271 bytes)

## Finding

### FEF-001 — P1 — “exact six schemas” validates only names and top-level property names

Locations: `a2-combination-frontend.ts:80-105,238-258`; `test-a2-combination-frontend.ts:35-59,196-219`.

`canonicalToolSchema` checks six tools in fixed order, names, string descriptions, parameter `type: object`, `additionalProperties: false`, and exact top-level property names. It does not compare the complete observed schema to an independently fixed expected value/hash. It does not validate property value schemas, required lists, description contents, or extra parameter keywords. It only requires both observed schema serializations to equal each other.

Thus identical drift on both calls, such as `read_solution.path.type = "number"`, a missing/changed `required`, or a changed description, passes. Line 257 hashes that observed drift and publishes the hash. The hash records the observation but is not independent schema authority.

The positive fixture itself omits `required` and still passes. The only schema negative adds a seventh tool; it does not change an existing property type or required set.

Required repair:

1. Bind an exact canonical six-schema value or lower-case SHA-256 derived independently from the reviewed controller-extension schema.
2. Compare each complete observed schema to it before any response or metadata publication.
3. Add negatives for property-type drift, required-set drift, description/extra-keyword drift, and two identical-but-wrong calls.
4. Keep the observed hash as evidence, but not as its own admission check.

No extra mutation ran because the instruction allowed only the exact five-test and targeted typecheck commands. The acceptance path is direct in the frozen source and positive fixture.

## Passing controls

- Two fixed unique response IDs and exactly two response factories.
- First response is one `read_public_result({})` tool request; second is fixed bounded text.
- Main args remain unchanged and exactly one test-only factory is appended.
- Fixed model/six-tool CLI value; exact `--api-key`/`--provider` rejected before registration; no env/auth fallback read.
- One fixed provider/model; registration always unregistered.
- Fewer/more call counts, remaining responses, differing observed schemas, or argument mutation fail before metadata.
- Direct-entry module-path guard prevents unit import execution.
- Fixed test-only metadata fields, 4096-byte cap, fixed-name `O_EXCL | O_NOFOLLOW`, `0600`, full-write loop, and file fsync.

## Qualification limits

- Public Main was imported but mocked and never called. Default Faux registration/stream did not run.
- Provider hook used a mock `ExtensionAPI`; `PreparedControllerMain` was a minimal typed mock.
- Default metadata writer was not executed; a sink was injected. Artifact-root identity/census remain capsule evidence.
- A third call is detected post hoc after `callMain`; this is not a hard pre-request limit. Public Faux has no third queued response and no fallback.
- Synthetic IDs are not genuine Codex provenance. Positive native four-category usage remains future capsule evidence.
- CD1–CD4 remain in force. No actual combination is authorized.

## Archived evidence

All three files under `paper/research/public-ml-programme-qualification/house-price-p0/integration/option-a2-faux-entry-v1` were read in full:

| File | Bytes | SHA-256 |
|---|---:|---|
| `a2-combination-frontend-report-v1.json` | 8901 | `82801c0e4bda39ade4d458a8fa5a73411a821bd55fdbb8bf39217ba7dc0964d2` |
| `a2-combination-frontend.ts.snapshot` | 9580 | `cc03a228690ca176a9ee8970c203ac610b487f79a6a81e077f68c5aba0e73da4` |
| `test-a2-combination-frontend.ts.snapshot` | 10852 | `09e3b30e3adf0580ca18ef1c6eccdf6d6215810ddaa29c45b0655b9172aab7fa` |

The producer report honestly records five mocks, a corrected test typecheck iteration, and no runtime combination. It has no failing-first schema-property mutation for FEF-001.

Held hashes still match:

| Dependency | SHA-256 | Match |
|---|---|---|
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller-main.ts` | `dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/controller-extension.ts` | `8e2ca3351e601b5d4733000dc9c704f0327fdc941851fadbc0d3f59357d2d3fe` | yes |
| `experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/deployment_assets.py` | `2087db073f9c10f3cb7264fc1dda1df2e31a7cdfb6671af0fce537720b3faccc` | yes |

These identify dependencies; the mock did not exercise production behavior.

## Exact executions

```text
$ node node_modules/tsx/dist/cli.mjs experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/test-a2-combination-frontend.ts
PASS mocked main receives unchanged args and exactly one additional test-only factory
PASS schema drift fails before metadata and always unregisters
PASS fewer than two provider calls fails without fallback
PASS more than two provider calls fails without another response or fallback
PASS prepared binding rejects provider or tool changes before Faux registration
{"total":5,"failures":0}
EXIT_CODE=0
```

```text
$ node node_modules/typescript/bin/tsc --ignoreConfig --noEmit --skipLibCheck --module NodeNext --moduleResolution NodeNext --target ES2022 --allowImportingTsExtensions --types node experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/a2-combination-frontend.ts experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/test-a2-combination-frontend.ts

EXIT_CODE=0
```

The targeted typecheck produced no stdout/stderr.

## External conditions

1. Future capsule must independently bind the actual reviewed six-schema authority, entry, prepared args, extension, session, metadata path, and artifact census.
2. One emitted public-read request is not proof public Main executed the real tool.
3. Metadata is not native usage authority; native session must verify both IDs and all four categories.
4. No actual publicMain/default Faux/stream/process/Bridge/fake ORX/Git/socket/Docker/provider/auth/data/P0 ran.
5. Combination clearance, OAuth, immutable closure, and P0 remain blocked.
