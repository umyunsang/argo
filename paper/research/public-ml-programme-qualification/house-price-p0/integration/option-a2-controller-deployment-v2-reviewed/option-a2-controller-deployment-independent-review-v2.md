# HousePrice P0 A2 controller deployment independent review v2

## Verdict

**SCOPED PASS for A2CD-I1–I3.** No remaining local finding was found in the repaired producer. This is not live deployment or P0 admission. `actual_P0` remains `false`.

Reviewed exact bytes:

- `controller_deployment.py` — `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`
- `test_controller_deployment.py` — `88b4c0a4712ef89733f9b0d44b1e92297e3c3e2ca8d36b5cd59c72dd593f756b`

The v1 review is unchanged. Bridge A2BR-I1–I6 remains closed.

## Closure

### A2CD-I1 — closed

`controller-extension.closure.json` is now an exact sibling manifest. It binds:

- the original extension `FileSeal`;
- the runtime binding `FileSeal`;
- the original bridge bootstrap full `PathIdentity`.

Frontend and process production reopen the manifest and bootstrap. They require the original path, SHA-256, size, mtime ceiling, device, inode, UID, mode `0700`, and runtime binding command. The independent bootstrap replacement was rejected and created no frontend output.

No ordinary extension binding or frontend deployment key changed. The existing `frontend_closure_manifest` asset carries this binding-provenance manifest. Full frontend `SourceTree` verification remains separate caller authority.

### A2CD-I2 — closed

`_capture_binding` now validates the supplied authority before capture, compares the captured path/hash/size and original mtime ceiling, and serializes the original ceiling rather than refreshed entitlement. Process production applies this to `process_exec`, node, controller main, and frontend deployment, then revalidates before and after publication.

The independent after-read `controller_main` mutation reached `capture_path_identity`, was rejected, and produced no process config. The source suite also covers node, deployment, and process-exec mutation.

### A2CD-I3 — closed

Frontend deployment is restricted to a direct child of `artifact_root` and cannot be in cwd/profile/session/tmp. Process config must be outside all five sealed roots and the asset/bootstrap/process-exec parent directories. Post-publication checks verify that successful writes did not invalidate original seals.

Independent frontend-in-tmp and process-in-profile attempts were rejected without output. The profile case left the original frontend valid. The normal positive control preserved empty session/tmp.

## Failing-first and green evidence

The repaired archive contains two direct red stages and two green stages:

- `01-I1-I3-red.log` — `472badd8a5751df2e2221e92d8a49ec1eb466c8c3f9fa0ca6b4507b335ce3f15`
- `02-extended-read-capture-red.log` — `877bdaf06b18c585fbc9fb2ad23519ba7df022a5dfe535a9e19c6402270c848f`
- `03-eleven-green.log` — `a89b3e3c408faae0d9372d38859cd39a6fa926469aacb8f705c0a3c7e7b07ecc`
- `04-thirteen-green.log` — `6eb3c07474a33a025065a5c52f89d9b2b7ae54fa16030456ab839236c6412feb`

The red stages falsify bootstrap substitution, file re-sealing, and self-mutating output locations before repair. The final snapshots match the reviewed hashes.

Independent exact-copy results under approved kernel Python 3.11:

- Full source suite: **13/13 pass**, 1.210 s.
- Bounded independent I1–I3 probes: all prior negatives rejected; normal publication positive control passed.

## Exact evidence

External temporary root: `/tmp/argo-a2-controller-deployment-rereview-20260907T235516`

- Source manifest — `d5e44b71d507c37ec1bb3d9ee3f8e7f643843ed22007c0b8af8a29f1d603a069`
- 13-test command — `989e3ec35dd18c277c459bc37115bdb44a024b12288b73be7693c8016b0a26a6`
- 13-test stderr — `8972bc3682c6c3aa457bd6112d69ed83884ddb09c9a29f172b4dc0bae7760a25`; stdout empty `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Independent probe source — `8138860303440d78f069e5ee3e8058f9ccc22ba7b23cdd53463487b88a22a354`
- Independent probe stdout — `951cff0dcafd6c1644d67e85f02cc9f2b53aa979ddf7f89ded04a6bdbcc46ec1`; stderr empty `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

`unittest -v` wrote its full output to stderr.

## Held dependencies

The exact temporary run held:

- `controller_process.py` — `135a3e28291ea8e7db3b85cdd4fda05124113baaeb0d1a1335a905bc5bdd3f33`
- `deployment_assets.py` — `e0a881f75cbb48a051028c1d64896ec8dbcfe6657a3411119e39627c4392e9ac`
- `phase_gate.py` — `94c43549e17ed453b9b7ada622957f74aff0530b33d8d6df095c4aae1bc631ba`
- `bridge.py` — `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558`

The concurrent bridge one-boolean-predicate repair is unrelated to controller deployment producer/read semantics and was not reviewed. DA001 and changing driver/completion sources were also excluded.

## Execution boundary

No native/provider/auth content/process/bootstrap/main/controller/Docker/ORX/task data/model/P0 execution occurred. Only exact source copies and synthetic private producer inputs were used.
