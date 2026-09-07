# HousePrice P0 A2 synthetic-combination contract review v2

## Verdict

**SCOPED READY FOR SOURCE/MOCK IMPLEMENTATION.** The five CBR corrections are now concrete and mutually compatible. This does not approve unfinished fixture/acceptance source, a whole-case run, or P0.

Resolution record: `option-a2-combination-contract-resolution-v2.json` SHA-256 `b74ee2f1624a000ea27223442171d8125ebbf9e0c6a8c311e8e5998c37aced18`.

## Finding closure

### CBR-01 — CLOSED

`option-a2-synthetic-capsule-contract-v1.json` defines a separate test-only materializer with exactly 25 source members plus four generated empty initializers. It includes the runtime, driver, fixture, acceptance, `test_bridge.py`, and scorer needed by the synthetic import closure. It explicitly forbids changing production `deployment_assets.RUNTIME_NAMES` or accepting extras/lookalikes. Member FileBindings remain caller-reviewed authority, and the written destination is reread before SourceTree capture.

### CBR-02 — CLOSED

`option-a2-combination-preimport-contract-v1.json` freezes the pre-import execution chain:

1. an externally hashed three-file TCB outside every case/source tree;
2. kernel Python `-B -S` running fixed `case-entry.py` with no argv;
3. stdlib plus a byte-identical sibling `source_closure.py` only;
4. strict 65,536-byte externally hash-bound case config;
5. rederivation of installed Prime, synthetic namespace, and frontend seed before any case import;
6. held namespace directory identity followed by fixed `execve` of kernel `-B -m ...combination_driver --config ... --config-sha256 ...` with exact four-key environment.

The test-only driver CLI supersedes the old no-CLI clause. Production Bridge/gate bootstrap allowlists remain unchanged. Root evidence remains the typed case result/receipt; arbitrary child diagnostics are not authority.

### CBR-03 — CLOSED

`option-a2-fixture-close-contract-v1.json` freezes `FixtureCloseResult`, exact success/error fields, one 2.0-second shared deadline, retained serve/socket/cleanup-thread identities, and cached no-retry repeat semantics. Confirmation requires shutdown completion, both owned threads stopped, socket `fileno()==-1`, no error, and no deadline. Case receipt v2 binds `fixture_close_result`; absence or uncertainty cannot become cleanup success.

### CBR-04 — CLOSED

`option-a2-combination-tool-wire-contract-v2.json` binds the exact seven-key native tool-result shape, fixed call ID/name/action, single text content, false error, and safe timestamp. It freezes the required transformation from strict `PublicResult` BODY to exactly `{"ok":true,"result":parsed}`, then the same sorted compact ASCII encoder used by phase gate. Direct-body hashes, wrapped text, extra fields, or compatibility fallback reject.

### CBR-05 — CLOSED

`option-a2-combination-evidence-limits-v1.json` freezes exact filenames, modes, file counts, and byte ceilings:

- case admission: 65,536 bytes;
- evidence: two files, 1,114,112 bytes total; process 1 MiB and final 65,536 bytes;
- admission plus evidence: three files, 1,179,648 bytes;
- control: two 65,536-byte configs;
- native outputs/gate/provider metadata and whole-case census caps.

Descriptor-relative O_EXCL/no-follow/full-write/fsync/reopen semantics preserve partial evidence and forbid fabricated bindings.

## Cross-contract consistency

- Final case receipt is explicitly superseded from v1 to `argo-house-price-a2-synthetic-combination-case/v2` only to add the typed fixture-close result.
- The synthetic capsule is distinct from the production namespace; the preflight TCB is also outside both.
- Config is reopened unchanged immediately before exec. `-B` prevents namespace bytecode mutation before driver revalidation.
- Frontend seed identity is verified before copy; generated bootstraps/configs/prompts are closed before the runtime frontend SourceTree capture.
- Normal and synthetic process configs still differ only in the two frontend fields; production phase driver is not executed.
- Tool transcript reconstruction now matches phase-gate envelope hashing exactly.
- Strict final native-session SHA/size equality remains deliberate. Any end-of-run append causes a fail-closed mismatch; no implicit prefix rule was introduced.
- Evidence limits fit the final typed receipt without permitting raw predictions, targets, auth, fake ORX state, or source archives.

## Separate unresolved work

`CFX001` is explicitly outside these five corrections. Its fixed second-candidate intent/parent authority repair and the active fixture/acceptance implementations require their own source review. They cannot inherit this contract pass as whole-fixture or whole-case approval.

## Evidence read

- `option-a2-synthetic-capsule-contract-v1.json` — `01984e3b4b0cb7e77e33d3086b6e0ee051df00f108997f303f519a00ce4ac66b`
- `option-a2-combination-preimport-contract-v1.json` — `c085fe254693f8bde65c2e82d320c3121c94c818f40d37ebd55ad1dd4820e668`
- `option-a2-fixture-close-contract-v1.json` — `9ea70be0563bfc69768d87f3629b5d17d3bab2cedb8fd2359c8b6fe2158e7dcb`
- `option-a2-combination-tool-wire-contract-v2.json` — `f294cecc726e5000e80b902667c6ac2855b46671030febaa680b8a7e0d4c4cf6`
- `option-a2-combination-evidence-limits-v1.json` — `c95bc11b8e00bd02addebe6d1f2d5c8db6cbed08bd7f06265d7f1b7322cf404f`

Relevant frozen source anchors read:

- `controller_deployment.py` — `c26c57ce10c1a16026a0ee2d54f7133573f8acfe249e16f78760bd2b7f19812e`
- `deployment_assets.py` — `2087db073f9c10f3cb7264fc1dda1df2e31a7cdfb6671af0fce537720b3faccc`
- `phase_driver.py` — `dc2bf22e7d1a33c52660200b8e25ab90c98cabce91f271befa781e0280cbec77`
- `phase_completion.py` — `4153bb2d4b92d8602211220913309fd73a995de3b0f83cd28107128896c73f98`
- `bridge.py` — `d751075cc258e730e7fe3b1c8a090451df80abbf35ce60167f3d116af229a558`
- `controller-main.ts` — `dbe87f0405f11401d209176d7cff629824e1192e69421d40b818bcfdec297f21`
- `controller-extension.ts` — `8e2ca3351e601b5d4733000dc9c704f0327fdc941851fadbc0d3f59357d2d3fe`
- `a2-frontend-probes/a2-combination-frontend.ts` — `cc03a228690ca176a9ee8970c203ac610b487f79a6a81e077f68c5aba0e73da4`

## Scope

Contract/source read only. No tests, unfinished source treated as final, fake ORX, Git, socket, Prime/Faux execution, process/controller, provider, auth, data, Docker, ORX, P0, worker, npm, or commit.
