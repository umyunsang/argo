# HousePrice P0 A2 Faux entry independent review v2

## Decision

**SCOPED PASS. FEF-001 is closed.** This releases only the repaired Faux source anchor to the acceptor. It does not admit a live combination case or P0. `actual_combination=false`; `actual_P0=false`.

Reviewed exact bytes:

- `a2-combination-frontend.ts` — `4c9b73b8d759fd0dd0061c84dd28a658452eaed6175fda4ba23ff4b60e6b09d6`
- `test-a2-combination-frontend.ts` — `3704e2483e33a5f6e1ad430ae38075936659a1b88b19bcd9831842a4ae4ff776`
- `a2-combination-frontend-report-v2.json` — `c8a536d040f5b8c8fdbf1bbf9ffd360926985e14debfec26ede3cf21127d8620`

## FEF-001 closure

`EXPECTED_SCHEMA_SHA256` is fixed to the independent root authority `553e00b05207cc51eaf80d3d58ff480279319990ce620409ea52a1e4d281ad61`. It is not derived from either observed provider Context.

Before each response, the entry:

1. requires the exact ordered six tool names;
2. maps every tool's complete JSON-visible `name`, `description`, and `parameters`;
3. recursively sorts object keys while preserving array order;
4. rejects nonfinite and non-JSON values;
5. hashes the full canonical array and compares it to the pinned authority.

After mocked main returns, both observations must exist, be identical, and independently hash to the authority before postflight or metadata. Metadata records only the pinned authority hash.

The canonical payload file is 1,891 bytes and hashes to the same `553e00...` value. The root receipt is `320a4cf4465890e6d48c7ebcce728de73da9b6577e7b1003bbd02f113f7314ec`.

## Required negative matrix

All four formerly missing identical-wrong controls now reject before a response:

- `read_solution.path.type` changed to `number`;
- `write_solution.required` reordered;
- `request_R1_run.description` changed;
- `read_public_result.parameters` receives an extra schema keyword.

The existing controls also reject a seventh tool, fewer/more than two calls, wrong model/tools, and an API-key flag. Registration always unregisters.

## Exact validation

Only the two authorized commands ran.

Nine mocks:

```text
node node_modules/tsx/dist/cli.mjs experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/test-a2-combination-frontend.ts
```

Result: **9/9 passed**.

Targeted typecheck:

```text
node node_modules/typescript/bin/tsc --ignoreConfig --noEmit --skipLibCheck --module NodeNext --moduleResolution NodeNext --target ES2022 --allowImportingTsExtensions --types node experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/a2-combination-frontend.ts experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime/a2-frontend-probes/test-a2-combination-frontend.ts
```

Result: pass with empty stdout/stderr.

Evidence root: `/tmp/argo-a2-faux-entry-rereview-20260908T012437`

- Nine-test command — `ecd4f8d75dca71bec1904ae3fa36b5ca5d9345e8f8c20d19174129a398752f6a`
- Nine-test stdout — `28e62d3d0e8cf192d451b5a79a8bd1839ce692033c44484f2b508c421bf54827`
- Nine-test stderr — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Typecheck command — `6c4699668dae6fa6abe2ce97f2d48a8a889b520e8e855dc4996987a1f0bc2e4e`
- Typecheck stdout/stderr — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The archived red directly reproduces the four schema failures. Its source/test/report snapshots and final green/typecheck logs match their recorded hashes.

## Preserved limits

- `publicMain`, default `registerFauxProvider`, and Faux stream were not called. The unit uses injected mocks and pure response constructors.
- This schema authority is derived from reviewed extension mock registration, not an actual provider-wire capture. The future acceptor must compare real Context evidence again.
- The call-count guard remains post-return, not a synchronous third-request ceiling. No third response or fallback exists.
- Synthetic response IDs and metadata are not OAuth, provider, native-usage, or execution authority.
- Production controller, extension, deployment, and bootstrap files stayed unchanged.

## Execution boundary

No public Main, default Faux registration/stream, Bridge, process, fixture, Git, socket, ORX, Docker, provider, auth, raw data, model, combination case, or P0 executed. No source file was edited.
