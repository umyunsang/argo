# A2 immutable source-validation evidence

Status: **scoped PASS**. This is a source/mock and committed-file validation result, not a live A2 combination or P0 result.

## Validated commits

- Source: `6b5e4cfe83d08b052b0d24b74fa2cc54d5f1d1da` (72 root-owned paths).
- Evidence baseline: `79a9ef3ffb8896457e744bb5c8fea7898066ee4b` (756 proof paths).
- Seven earlier owner commits cover 171 disjoint paths.
- The selected manifest covers 999 paths and 11,605,070 bytes. It does not cover every repository file.

## Completed checks

| Check | Result |
| --- | --- |
| Python mock/file tests | 249 passed: 177 + 57 + 8 + 7 |
| Faux entry/schema mocks | 9 passed; no real provider stream |
| Targeted TypeScript check | Passed |
| `npm run check` | Passed; 953 configured files, no fixes |
| Existing navigation and graph | Passed; 860 nodes, 1,438 edges, 694 document paths |
| Independent committed-file audit | Passed; zero discrepancies |
| Selected hashes before/after checks | All 999 unchanged |
| Clean clone after removing the temporary dependency link | Empty Git status |

The main receipt is `../../option-a2-immutable-validation-v1.json`.
The current checkpoint is `../../option-a2-integration-checkpoint-v24.json`.
The independent report is `independent-manifest-audit.json`, SHA-256
`672c17341a4cc65addee71b8a683fc48d5e6cd96e7856c4c8fbc6001bfbd5008`.

## Qualifications

The first external manifest used three IO basenames. Its correction was a one-to-one mapping within the first owner slot. The old manifest and correction record remain in this directory. No source changed.

The 25-member source freeze includes a scorer that predates this fan-in. Four of the 22 departed-author archive targets also predate the selected manifest. All were verified at the target commit. The first IO commit did not invoke the then-absent hook wrappers; it is not called a hook PASS. The reader's failed first commit and its approved retry remain in the evidence history.

The data-preparer tests used fabricated CSV data with the existing project environment, not the pinned production image. Coverage was not measured. The independent auditor did not rerun tests. `clean-test-verification.json`, the v23 checkpoint and the earlier frontier preserve their audit-pending state; the final receipt and v24 supersede only that state.

Historical logs and description/diff whitespace stay byte-identical. They are not reformatted to make a raw whitespace check pass.

## Not executed or admitted

No actual A2-Faux-C1 combination, real House Price split, evaluated-model call, estimator fit, hidden scoring or P0 launch occurred in this validation. Production OAuth transport and whole-host runtime trust were not qualified. Native ARGO construction remains paused. This evidence does not establish efficacy, `ResearchDone` or manuscript readiness.

Preparation and verification have nonzero costs. Total agent and billing cost is not certified. Existing task/A/A2 approvals remain valid; the latest approval covers the final local validation-record commit only.
