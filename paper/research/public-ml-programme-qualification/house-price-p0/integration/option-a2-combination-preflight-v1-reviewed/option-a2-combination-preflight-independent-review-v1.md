# HousePrice P0 A2 combination preflight independent review

## Verdict

**SCOPED PASS.** No local source/mock defect was found in the exact preflight slice. This does not admit a real combination case or P0. `actual_combination=false`; `actual_P0=false`.

Reviewed exact bytes:

- `combination_preflight.py` — `b8847e13347299b96deb1ca695a5a82c2b5d6a4b651bd1372b1a4561e52229ce`
- `test_combination_preflight.py` — `e34f3387a0638b51937e7498b56785c977c0fc4e95f254a6127a0804642df40e`
- `a2-combination-preflight-report-v1.json` — `3f1a1c4a18455bada55e010c797d03ec8ec1ba68fb573e929f5ddb5418830362`

## Verified boundary

- The preflight imports only the standard library and sibling `source_closure.py` (`e4b0b8732d48d2ecbcd57b6d9e01dbf88200ab5e57bf12426d28d22017ae4466`). It has no case import, dynamic import, `importlib`, `sys.path` mutation, or `PYTHONPATH` dependency.
- The generated entry uses only `sys`, `pathlib.Path`, and `execute_preflight`. It embeds the fixed absolute config path/hash and rejects extra argv before invoking the preflight.
- The local interpreter check requires exact `sys.executable`, `-B`, and `-S`, then verifies only symlink/executable/`pyvenv.cfg` shape and stability.
- Config bytes are nofollow-read, single-link, owner-private, mode `0600`, size/digest bound, duplicate/NaN rejected, exact-schema parsed, and reopened unchanged before exec.
- Namespace, frontend seed, and installed Prime trees are pairwise disjoint and rederived before any case import. Fixed fixture, acceptance, and Faux members are hash-checked. The driver remains bound by the namespace tree.
- Namespace root device/inode/owner/mode are checked through an opened directory descriptor. `fchdir` uses that descriptor, which is closed before the mocked exec.
- The child request is exactly the approved kernel, `-B`, fixed `-m` driver, fixed config path/hash, and the four fixed `LANG`/`LC_ALL`/`PATH`/`TZ` variables.
- Exception failures emit only `COMBINATION_PREFLIGHT_INVALID`, return 2, and create no case root. `BaseException` is not claimed handled.

## Independent negative controls

Two additional mock controls passed:

1. A config change on the final reopen returned 2, emitted only the fixed error, made zero exec calls, and left `case_root` absent.
2. A wrong interpreter stopped before any tree verification or exec, emitted only the fixed error, and left `case_root` absent.

## Validation

Exact required command, from the runtime directory with no `PYTHONPATH` or `sys.path` manipulation:

```text
cd /Users/um-yunsang/argo-paper-orx/experiments/argo_workflow_followup/public_ml_apparatus/house_price_runtime && /Users/um-yunsang/.prime/agent/kernel-venv/bin/python -B -S -m unittest -v test_combination_preflight
```

Result: **6/6 passed**, 0.035 s.

Evidence root: `/tmp/argo-a2-combination-preflight-review-20260908T010023`

- Command — `b6b77e7ce431724a4791f41e5e75cda29b514b41580de7b6bb92de70f75cb66c`
- Full stderr — `962e463d7d1754fab1a54d7e38d09661ccf7c71068a0c37b7ec34f87af571346`
- Stdout — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty; `unittest -v` wrote to stderr)
- Negative-control command — `4aaac8b2d80c08cbb868143c5e459f8f3fbb9e5fc696f12725eb1a272345671c`
- Negative-control stdout — `06af523da2b6e3571b8057da143386d7d383db44a9b5a504886909e86489beb8`
- Negative-control stderr — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty)

The archived source, test, and report copies match the requested hashes.

## Required external authority

The local interpreter checks are not byte or link-chain identity proof. Before any real command, root must independently bind the invocation link chain, resolved kernel bytes, `pyvenv.cfg`, preflight bytes, sibling `source_closure.py`, and generated entry. The accepted private-root/no-concurrent-same-UID-mutator assumption remains explicit.

## Execution hold

No real `execve`, combination case, Prime, Faux, fixture, NativeHarness, Git, socket, provider, auth, Docker, ORX, task data, process, model, or P0 was executed. Success-path `execve` and `fchdir` were mocked.
