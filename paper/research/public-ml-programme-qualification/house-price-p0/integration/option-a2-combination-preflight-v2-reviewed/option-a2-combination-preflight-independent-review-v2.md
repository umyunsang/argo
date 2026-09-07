# HousePrice P0 A2 combination preflight independent review v2

## Decision

**SCOPED PASS. CDRV01 is closed.** No new finding was found in the exact preflight v2 slice. This does not admit a combination case or P0. `actual_combination=false`; `actual_P0=false`.

Reviewed exact bytes:

- `combination_preflight.py` — `724727bb4a1924f026939b78094701735861f0d48e3dd35219b4cf524f1463c6`
- `test_combination_preflight.py` — `9f5868a13b9872e7a4fa23197ade30cb6aa681e2d1e7186c9a8534a2dd44851a`
- `a2-combination-preflight-report-v2.json` — `5a39bac4a526118953d27b65919a203cff5794e42084f805270d349f4d78a186`

The v1 independent review remains unchanged.

## CDRV01 closure

The trusted preflight now requires config schema `argo-house-price-a2-combination-case-config/v2` and one exact `protected_roots` object with these roles:

- `raw`
- `auth`
- `profile`
- `controller`
- `public`

Each role is exactly `{path, device, inode}`. Device and inode require non-boolean bounded integers.

Before layout or any tree verification, the preflight:

1. resolves each protected path canonically;
2. opens it with `O_DIRECTORY | O_NOFOLLOW`;
3. matches held `fstat` and named `lstat` to the supplied device/inode and current UID;
4. retains all five descriptors.

`case_root` cannot equal, contain, or be contained by any protected role. The roles may overlap one another, including all five sharing one identity.

After all three tree/member checks and the final identical config read, every held descriptor and named path is revalidated. All five protected descriptors and the namespace descriptor close before the mocked `execve`.

The implementation never opens or enumerates protected contents. Completeness and provenance of the five role identities remain external root authority.

## Negative and compatibility controls

The eight tests establish:

- schema v1 rejection before trees/exec;
- missing role, boolean device, and wrong inode rejection;
- protected profile ancestry rejection with no denied/default case root;
- five overlapping roles open as five descriptors, revalidate, close, and reach only mocked exec;
- all six prior TCB/config/tree/member/interpreter/fixed-entry controls remain green.

## Exact validation

```text
cd /Users/um-yunsang/argo-paper-orx/experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime && /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -S -m unittest -v test_combination_preflight
```

Result: **8/8 passed**, 0.056 s.

Evidence root: `/tmp/argo-a2-preflight-v2-rereview-20260908T014043`

- Command — `b6b77e7ce431724a4791f41e5e75cda29b514b41580de7b6bb92de70f75cb66c`
- Full stderr — `4ce48f0dfb53cf6b29c28b20c9ba4c1a446c46c12e4426b0f5a61955e2ab2b96`
- Stdout — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty; `unittest -v` wrote to stderr)

The archived v2 source, test, and report copies match the requested hashes. The archived failing-first output exercises the old parser against the v2 protected-root tests before the final eight-test green.

## External authority

Root must supply the true complete five protected identities. This source validates directory identity, ownership, stability, and case ancestry only. It does not inspect protected contents. The external interpreter/TCB byte authority stated in the v1 review remains required.

## Execution boundary

No actual case, driver, process, Prime, Faux, fixture, NativeHarness, Git, socket, provider, auth content, raw data, ORX, Docker, model, or P0 executed. `fchdir`/`execve` were mocked on the success path. No source, test, or driver file was edited.
