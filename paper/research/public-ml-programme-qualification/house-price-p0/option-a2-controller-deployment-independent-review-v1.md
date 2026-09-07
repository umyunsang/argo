# HousePrice P0 A2 controller deployment producer independent review

## Verdict

**NOT ADMITTED.** The exact source-only producer has two blocker provenance defects and one high-severity self-mutation defect. `actual_P0` remains `false`.

Reviewed exact bytes:

- `controller_deployment.py` — `c57a768535a1242a215858c1ccb0ffe0d7fc71a01b3ef792f5e63f625a71b044`
- `test_controller_deployment.py` — `eea93bac60559d12596800e30c7f188ee64e014fdad152cfc6cbdbe7fad606ee`

Bridge A2BR-I1–I6 remains closed. DA001 bootstrap implementation and changing process-driver/completion sources were not reviewed.

## Findings

### A2CD-I1 — BLOCKER — bootstrap executable identity is not durable

`write_extension_binding` opens `bridge_bootstrap` and checks an executable bit (`controller_deployment.py:94-100`), but writes only its path to `bridge.command`. `ASSET_KEYS` omits the bootstrap. `_prepare_frontend_deployment` (`116-145`) accepts any absolute command from the binding and never reopens it or compares it to an approved bootstrap identity.

Bounded reproduction: the real helper created a binding, then the synthetic bootstrap changed from SHA-256 `c663f847...` to `7eff4bcf...`. `write_frontend_deployment` still succeeded, and its asset map contained no bootstrap seal.

Required: bind bootstrap path, SHA-256, bytes, mtime ceiling, private owner/mode, and executable status. Revalidate it during frontend and process production. Require `bridge.command` to equal the sealed path.

### A2CD-I2 — BLOCKER — process production re-seals a file changed after validation

`write_process_config` validates deployment and asset bytes at `198-207`, then independently calls `capture_path_identity` while constructing the controller config at `209-215`. It never requires the captured identity to equal the frontend deployment seal or the supplied `process_exec` binding.

A deterministic synthetic race changed `controller_main` only after its last `_data` read. Process production succeeded. The frontend deployment still bound SHA-256 `aeace2d6...`, while the generated process config authorized `9951b65e...`.

Required: atomically reopen and compare every captured process identity with its existing deployment/FileBinding authority. Bind the exact frontend deployment bytes that were parsed. Add mutation-between-read-and-capture tests for `controller_main`, deployment, node, and `process_exec`.

### A2CD-I3 — HIGH — allowed output paths can invalidate freshly sealed directories

Frontend preparation requires only that the deployment be below `artifact_root` (`151-155`). It does not exclude the sealed-empty `session_dir` or `temporary_dir`. Writing deployment into `temporary_dir` succeeded with `must_be_empty=true`; immediate `_revalidate_frontend_deployment` then rejected it.

Process production rejects only `artifact_root` and descendants (`202`). Writing `process.json` into the sealed profile succeeded, introduced a forbidden profile entry, and immediately invalidated the frontend deployment.

Required: reject outputs in any directory whose seal/policy the write changes. Frontend deployment must not be inside session/tmp. Process config must not be inside artifact/session/tmp/profile/cwd. Assert post-publication revalidation.

## Verified controls

The exact temporary copy passed all six requested synthetic tests under the approved Python 3.11 kernel. Independent false controls also confirmed:

- unexpected frontend schema field rejected;
- `HOME` injection into the eight-key environment rejected;
- static `controller_main` byte tampering rejected with no process config;
- unknown assets, enabled retries, stale session/tmp, replaced profile inode, artifact-contained process config, and overwrite rejected;
- synthetic `auth.json` contents were guarded against `os.open`; only names/metadata were observed.

The four archived red/green logs and all snapshots were read in full and matched the validation receipt. The directory-reseal defect proven by `03-directory-reseal-red.log` is closed, but that fix does not cover file re-sealing or output self-mutation.

## Evidence

External exact-copy root: `/tmp/argo-a2-controller-deployment-review-20260907T232841`

- Source manifest — `afcb7d51f73b70d1a6215f33f41cac4b9db538ea2d24a14e0dab99dbee0fc37b`
- Six-test command — `98384a3b6a44a49787a3671a5c37950c8d11f7edc92d085591729fc1f7ce073f`
- Six-test stderr — `97f8940ba530cf1bf4800feccbd0cfa4239a407ad84e87ff93361a0b8dcc2cd9`; stdout empty `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Negative-probe source — `d62e71c4cb0f5d85cb931e5fcd4b8dac63c5548938bee9285bd3d70624dc663c`
- Negative-probe stdout — `ae33ed7a22cd8253a670c927d4d92a9cd31ec79e41136341473467dcc97d02f7`; stderr empty `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

Archived log hashes:

- `01-stub-red.log` — `5b9574e886409c828b860e37233ecf3941e81c7f632ad5ae9a1eaf12754bd893`
- `02-initial-green.log` — `84a3597ae7417a7f753e1e7358fe4c3e0e7f960a32fc4ab63cbbed47da826fcb`
- `03-directory-reseal-red.log` — `69d4a537fcf1a59c67e2da7f35b7340d31c53457403b2c598bdce1b7aab696a2`
- `04-directory-reseal-green.log` — `6c4a9d054887768f84415ca5d64fcaee08534ea02889733f02646fd70ecf0dee`

`unittest -v` wrote full test output to stderr.

## Mutable dependency boundary

The held test copy used `deployment_assets.py` SHA-256 `bad8dd3555c745474bc678d5c3cc9eab66fcde874293f4687e4583f4327f9f09`. The live file later changed to `e0a881f75cbb48a051028c1d64896ec8dbcfe6657a3411119e39627c4392e9ac` under separately owned work. The only imported helpers are byte-identical:

- `_new_private_path` — `bf71c3702e0487b4c651194a08877d0aa0749c118c06f0b0d66b138a69d9d998`
- `_write_new` — `3317bba0e08c3b0acccc3681fc5d4c7dc1d4b32d6d7a19ff20946bd92dce5818`

No unrelated DA001 code was inspected or reviewed.

## Execution boundary

No real bootstrap, main, controller, ORX, Docker, auth content, task data, provider, model, or P0 execution occurred. Only synthetic files and pure producer calls were used.
