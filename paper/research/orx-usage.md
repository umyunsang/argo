# Autonomous research engine — local CLI usage (verified 2026-09-02)

**Scope:** operating notes for this repository only. Public manuscript prose never names this tool; it says "autonomous research engine".
**Verification:** every line below was produced by running the command locally in this worktree.

## Installed state

| Item | Observed |
|---|---|
| version | `0.1.117` (latest `0.1.118`; upgrade deferred to keep the frozen run contract stable this round) |
| skills | bundled agent skill doc printed by `skill`, with focused modules |
| retrieval primitives | `keyword` (full-text BM25 with snippets), `embedding` (semantic + rerank), `openalex`, `biorxiv` |
| paper fetch | report by default, `--full` for full text; source auto-detected from id |
| experiment ops | `create-experiment`, `exp status|run|cancel|wait|wake`, `runs`, `logs` |

## Cardinal rules taken from the bundled skill

1. A node freezes once a run answers it; edit a child, never the answered ancestor.
2. The run command and environment are a fixed contract, identical on every node; children inherit the command verbatim.
3. Only code varies between nodes.
4. The tree grows as a stacked bush, not a chain.

## Loop used in this project

```
discover keyword/embedding/openalex   # caller owns the search loop; snippets are leads, never claims
paper <id>            # structured report
paper <id> --full     # full text, used only for FULL_PAPER_READ
curl e-print/<id><version>   # exact-version archive, hashed and retained
exp run <node> --backend local ; exp wait <node> ; logs <run-id>
```

Retrieval is run by this session directly and is never delegated.

## Evidence contract enforced on top of the CLI

- A claim needs a retained exact-version source plus a line-anchored locator whose slice and digest re-derive from repository bytes.
- Run evidence is admitted only from an immutable run at a known commit; a local working-tree pass is not run evidence.
- Discovery snippets, report prose, and citation counts support no result.

## Failure observed and fixed this round

Run `3fe2958b-44b6-4760-89fb-f711440c2ae0` failed at commit `b2070ed09` because the local pass depended on working-tree bytes that the repository did not contain. The gate now re-derives every locator from repository bytes, and run `67bec1bc-b8da-47a6-8f49-6a486799f844` passed at commit `c677aeb6e` in a clean checkout.
