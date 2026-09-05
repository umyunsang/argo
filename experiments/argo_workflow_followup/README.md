# ARGO workflow follow-up instrumentation

Status: scorer and one historical multi-hop replay semantics are validated at zero model cost. OS-level runner isolation is not validated. No task pack, model episode, or OpenResearch project is admitted.

`decision_sufficiency.py` keeps four objects separate:

1. exact routing of affected decisions;
2. claim-relative evidence sufficiency;
3. decision correctness when a hidden choice oracle exists;
4. the external end-to-end task outcome.

A correct route alone cannot pass. Missing or conflicting evidence returns `INCONCLUSIVE`. A stale version, over-broad route, wrong choice, malformed packet, or hidden-oracle access returns `INVALID`. Confirmatory success additionally requires the independently supplied task outcome.

`probe_discoveryworld.py` is a zero-cost source probe. It tests only a pinned local DiscoveryWorld install. It does not run an LLM. The proposed comparison remains blocked until a text-only, separately sandboxed runner, correction/handoff event pack, deterministic gold, immutable environment, exact resource envelope, and explicit approval exist.

Run the scorer tests:

```bash
python3 experiments/argo_workflow_followup/test_decision_sufficiency.py
```

Run one DiscoveryWorld probe with the external repository's isolated interpreter:

```bash
~/.cache/argo-research/DiscoveryWorld/.venv/bin/python   experiments/argo_workflow_followup/probe_discoveryworld.py   --scenario Proteomics --difficulty Easy --seed 0 --thread-id 918280
```

## Historical multi-hop pipeline falsifier

`historical_multihop/` replays the actual corrected-B2 protocol repair. Its gold choice predates this instrument in the byte-pinned audit and B3 closure. The typed conjunctive rule changes five nodes across a four-edge `claim → decision → action → result` path and preserves two descriptive nodes. A deliberately coarse ANY-support comparator incorrectly promotes the invalid endpoint. This is one pipeline falsifier, not a policy-efficacy result or an independent population.

```bash
python3 experiments/argo_workflow_followup/historical_multihop/test_historical_multihop.py
python3 experiments/argo_workflow_followup/historical_multihop/test_isolation_command.py
```

Do not run `historical_multihop/run_isolated.py` again under the current authority. Both Docker attempts failed before launch because a macOS logical temporary path was not daemon-visible. The one allowed infrastructure retry is consumed. The path is prospectively resolved and passes pure command tests, but end-to-end isolation remains `FIXED_UNVALIDATED`.
