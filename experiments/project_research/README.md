# Project research apparatus

This directory implements the [authorized project research programme](../../paper/research/project-research-20260909/README.md). It is research apparatus, not a native ARGO migration. Previous apparatus remains intact.

Use the pinned Linux arm64 image recorded in the private `control/environment.json`. Dependency pins and original-source receipts are in [domains](domains/README.md). Local scientific input, final/future custody, sessions, billing, ORX worktrees and raw outputs live below `~/.local/share/argo-project-research-20260909/`; none is a public repository dataset.

ORX project `4d54d8cb-64b6-4091-a739-85cf18a15d94` uses the same fixed `/opt/homebrew/bin/python3 runner.py` for every committed node. `dispatch.py` freezes source/spec and submits once, `orx_adapter.py` reconciles exact run IDs. Repeated identical submissions attach to the existing intent. Ambiguous creation/launch requires reconciliation; a new attempt must name a new prospective decision. Existing failure records remain.

```sh
# From the repository root, after inspecting a concrete private node specification:
python3 -m experiments.project_research.dispatch --spec /absolute/private/node-spec.json --title development-domain-attempt

# Regenerate the read-only local dashboard:
python3 -m experiments.project_research.dashboard \
  --root /Users/um-yunsang/.local/share/argo-project-research-20260909 \
  --output .planning/2026-09-09-project-research-execution/dashboard.html
```

`programme.py` creates 12 initial and18 later **planned** contracts once; invoking it again cannot reset budgets or clocks. The shared SQLite store reserves total/phase KRW and aggregate/project CPU/memory before work. Unknown usage blocks new work. Kernel and scientific containers share the same store; exclusive performance leases exclude new kernels. ORX retains process state; this store records authority, evidence and resources.

`campaign_controller.ts` uses the installed Prime SDK and native REPL/RLM through `kernel_launcher.py`. The controller supplies sterile resources and only scoped host tools, snapshots/closes kernels before a scientific ORX action, then reopens its native transcript. It refuses unqualified routes and unreconciled model usage. Available registry entries or successful fixture tests do not qualify billing or live recovery.

Model access is through the installed Prime provider registry. Subscription routes (`openai-codex`, `anthropic`) are admitted only with a trusted included-allowance snapshot before each request and a fresh one after; extra usage disabled and the cumulative extra-credit counter unchanged evidences zero additional charge. SDK cost estimates never settle a charge. The Anthropic usage endpoint rate-limits bursts, so a 240 s trusted observation cache is reused and `reconcile_subscription` settles any request left UNKNOWN by a 429.

`team_runner.py` runs one independent team's research → experiment → reproduction roles sequentially: each role is a fresh native session; a completed role's conclusion and workspace files are copied into the next role's `inbox-from-<role>/` with hashes. Teams never receive each other's inbox. `python3 -m experiments.project_research.team_runner <campaign_id> <team>`.

Candidate scripts run as nonroot in a read-only, networkless container with explicit public input and writable output only. They write `/output/result.json`. Generic candidate exit0 is `EXECUTED_UNVALIDATED`; trusted development recipes emit typed observations. Neither status grants AAA, a final score, superiority or PI acceptance. Kernel-generated work cannot modify controller, evaluator or limits through its mounted filesystem. The trusted host SDK/bridge remains part of the boundary.

`review.py` builds fresh anonymous two-team packets, validates fixed six-dimensional judgments, freezes accepted source bytes, and reserves independent final data. Default fixture scope cannot produce research AAA. The supervisor must actually receive only its packet; distinct host directories alone do not prove that. The central evaluator registry must persist across comparisons. Every final result and PI decision is separately recorded.

The common/B/H/P prompts preserve identical tool/model rights. P policy text is not proof of independent team or blind-supervisor execution; that needs real orchestration receipts. Live retrieval, actual model handoff, independent final evaluation and the multiweek campaign programme must each be validated before their corresponding success claims.

Verification: focused Python test modules in this directory, native SDK controller fixture tests, separate strict TypeScript checking, and repository `npm run check`. Domain tests are deliberately small integrity/numerical fixtures. Only actual ORX development records count as the first real research measurements. See [first report](../../paper/research/project-research-20260909/first-report.md) for current results and remaining work.
