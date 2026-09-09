# Native SDK episode qualification

Scope: one focused TypeScript fixture and this report. Native source, controller and scientific bridge are read-only. Only synthetic private markers and fake model streams are used; no provider request, actual data, model fit or scorer launch.

Plan: inspect controller/native SDK interfaces [complete]; execute native IPython plus one inline RLM child with a shared fake closure [complete]; qualify cleanup and report configuration/lifecycle/phase defects [complete]. Root retains ownership of the active plan and repository check.

Initial directly inspected risks to resolve with fixtures: native child active-tool sets are copied at spawn; parent `agent.abort()` is distinct from child cancellation; synchronous `dispose()` differs from `disposeAsync()`; assigning a raw stream function after session construction replaces the native semantic-edge wrapper. These are hypotheses until the focused observations below are complete.

Fixture correction: the first run reached completed child work but asserted `getRlmChildRunStatus(id) === "done"` after quiescence. Completed runs are removed from the active-run map; the correct retained lifecycle surface is `listRlmSubagents().subagents[].status === "completed"`. The fixture now uses that public roster. Cleanup ran after the assertion; no real provider was called.

## Result

**PASS: focused synthetic native SDK integration**, one substantive test, 17.527 seconds. Run from `experiments/argo_study_20260909`:

```sh
node --import ../../node_modules/tsx/dist/loader.mjs --test test_native_episode.ts
```

The actual installed `createAgentSession` ran its built-in IPython tool against the qualified Docker interpreter. A host-only synthetic label marker was invisible in both parent and child. Both read the public file, wrote distinct public outputs, retained their own namespace across calls and did not inherit each other's Python variables. The native `rlm.run` host bridge admitted exactly one inline child, which reached the public retained-roster state `completed`.

The child retained the identical underlying fake stream closure, model `openrouter/openai/gpt-5.6-sol`, `high`, shared SettingsManager/ResourceLoader and sequential tool mode. Nine fake stream calls occurred (five parent, four child); global fetch was replaced with a throwing guard, and **zero network/provider requests** were attempted. No real auth file, scientific labels, model, candidate or scorer was used. Two kernel leases were alive before disposal. All leases and explicitly named fixture containers were gone after cleanup.

## Controller findings

1. **Phase transitions require descendant quiescence.** The parent's `prompt()` resolved while its admitted child was still running. The child retained its own tools when the parent's active tools changed, and its delayed synthetic host call observed the new `ASSESSOR` value rather than its admission-time `PLANNER` value. The actual synthetic host guard denied that call. Await `session.waitForRlmQuiescence(...)` before moving to the next phase, under the same deadline cancellation. This prevents phase drift without removing native RLM.
2. **`session.agent.abort()` stops only the parent agent.** The waiting child's AbortSignal remained un-aborted after this call. The public `session.abort()` additionally invokes native descendant cancellation. Use that session-level method for deadline/final cleanup before reconciling shared usage.
3. **Raw stream replacement drops parent native lineage.** The parent had no semantic request ID after assigning the fake stream directly; the child acquired its own ID through the native wrapper. Applying `wrapStreamFnWithSemanticEdges(fakeStream, session.semanticEdges)` produced a parent ID while retaining the same existing recorder and inner stream closure. `session.semanticEdges` is a public getter; no private reflection or new lifecycle authority is needed. Root's live controller now uses this repair.
4. **Synchronous dispose returns before cleanup.** The fixture observed two active kernel leases immediately after `session.dispose()`; positive cleanup completed 260 ms later. Root's controller now awaits `session.disposeAsync()` before meter reconciliation/finalization. The fixture demonstrates the original race; it does not claim synchronous disposal permanently orphaned containers.
5. **Child active-tool display expands to its allowed ceiling.** Parent active tools were `[ipython]`; child active tools were `[ipython, phase_probe]`, matching the allowed ceiling. The disallowed registered `forbidden_probe` never appeared or executed. A delayed allowed `phase_probe` actually ran through the host guard and was denied in `ASSESSOR`. This is a display/subset inheritance difference, not an observed authorization bypass. Keep host guards authoritative.

Current controller SHA and root-fix observations are recorded in the JSON receipt. Root edits occurred concurrently; findings above distinguish the deliberately reproduced earlier behavior from repairs observed in the latest read-only source.

## Configuration and evidence boundaries

The fixture uses one native session family per Node process with its own `workspace`, `artifacts`, unmounted `control/profile`, immutable kernel image and in-memory fake auth. Loader checks found zero ambient skills, prompt templates and AGENTS files. The controller writes kernel settings through process-global environment variables, so separate concurrent episodes must use separate Node processes. This is an execution constraint, not a multi-episode concurrency guarantee from `runEpisode()`.

The actual `run_candidate`/`lock_candidate` bridge was not invoked: phase denial was tested through a synthetic custom tool using the same predicate. Real provider billing, ORX lifecycle, scorer behavior and daemon-mode recovery remain outside this fixture. Root owns the integrated repository check.
