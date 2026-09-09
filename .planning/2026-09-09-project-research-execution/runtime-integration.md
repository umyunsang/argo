# Runtime integration audit and adapter

Scope: research apparatus only. No native changes, old experiment edits, new jobs,
model requests, credential updates or external publication were performed here.
The active root plan owns new project registration, budgets and actual research.

## Plan and progress

- Complete: current repository instructions, Prime controller/meter/kernel wrapper,
  ORX bundled guides and live local surfaces read.
- Complete: thin ORX adapter plus focused checkpoint recovery tests.
- Complete: live read-only status and complete-log transport verification on one
  predecessor run. This is apparatus evidence, not a new research result.
- Root integration: create new private project, commit fixed runner, resource
  accounting, worker/model controls, genuine experiments and independent review.

## Current executable authority

- ORX 0.1.120: `/Users/um-yunsang/.local/bin/orx`.
- Prime 0.9.2: `/opt/homebrew/bin/prime-agent` and
  `/opt/homebrew/lib/node_modules/prime-agent/dist/index.js`.
- Node `/opt/homebrew/bin/node`, Python `/opt/homebrew/bin/python3`, Docker
  `/opt/homebrew/bin/docker`.
- Local dashboard `http://127.0.0.1:4837` is live. Its current frontend confirms
  `POST /api/projects` with `{name,path,createFolder:false,requireNewFolder:false,
  initializeGit:true,githubSyncEnabled:false,locale:"en"}`. Registration was not
  invoked by this lane.
- Read-only JSON routes are `/api/projects`,
  `/api/projects/<id>/experiments`, `/api/projects/<id>/runs`, and
  `/api/runs/<id>/log?offset=0`. Logs return base64 bytes, eof and nextOffset.
- Fixed command: `/opt/homebrew/bin/python3 runner.py`. All candidate differences
  belong to committed code/config. `orx exp run <experimentId> --backend local`
  launches an immutable committed snapshot and returns immediately. ORX owns the
  detached supervisor, lifecycle and persisted output. The local backend has no
  timeout/image/flavor flag, so the fixed runner must enforce its container limits.
- The earlier study project `c9443332-b7f0-40db-9f5d-68b7cf4f4bff` has three
  terminal runs and no in-flight run. It remains historical evidence.

## Minimal integration API

```python
from pathlib import Path
from orx_adapter import OrxAdapter

adapter = OrxAdapter(project_id, "/opt/homebrew/bin/python3 runner.py")
result = adapter.attach_or_run(experiment_id, committed_sha,
                             Path(private_control_dir) / "orx-intent.json",
                             permit_launch=True)
```

The caller must use a canonical unmounted control path, provide a committed
experiment, and authorize resources before this call. Default `permit_launch`
is false. For launch the adapter verifies experiment ownership, fixed command,
branch commit and existing run history. It writes/fsyncs a durable submission
intent before calling ORX, never uses `--force`, and attaches exact project,
experiment, commit and run identity. Existing run IDs remain authoritative after
session replacement. Ambiguous submission, changed identity, missing history or
multiple matching runs block fresh dispatch; failure/cancellation stays visible.
The adapter does not create experiments, pick research branches, schedule compute,
implement worker budgets or certify a scientific result from status alone.

Verification: `python3 -m unittest -v test_orx_adapter.py` from
`experiments/project_research`: 10/10 passed. Coverage includes lost response,
new-process unknown intent, late run appearance, terminal failure retention,
changed commit/run ID, lost checkpoint and fixed-command boundary. Live transport
read old run `f048a379-3742-4330-b25c-1abd16039e60`, commit
`20caa6de760e93e93392928f34904d3235549f22`, 680 log bytes SHA256
`da00210e97139655636a2f58cbb551a06b30fdf7825763f8f7dd790f62276230`.

## Container and native kernel reuse

Verified local immutable image:
`sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c`.
Docker VM currently reports 4 CPUs and 6198034432 bytes RAM. No research
container was live during inspection; an unrelated LiveKit service remains live.
Do not stop unrelated services.

The old wrapper is fully inspected and qualified by predecessor records, but its
hardcoded root and per-episode pool are not the new aggregate 4 CPU/4.5 GiB policy.
It accepts only old-root workspace/artifacts/control siblings. Adapt it in new
research apparatus for `~/.local/share/argo-project-research-20260909`; do not
modify old evidence. New global resource admission must cover all kernels and
scientific containers. Serialize performance runs and scientific jobs by default.

Use the image with no network, read-only root, no capabilities, no-new-privileges,
nonroot UID/GID, explicit CPU/memory/PID limits, bounded tmpfs and explicit binds.
Worker kernel sees only its own writable workspace and session artifacts. Supply
public development inputs via read-only binds; keep evaluator, hidden final and
followup splits, budget/intent/controller files, provider auth and original source
evidence outside every worker mount. A trusted host scorer gets its own isolated
view. Do not expose Docker socket or general host shell to a worker.

Native integration uses `PRIME_AGENT_KERNEL_PYTHON=<new local wrapper>` and
`ARGO_KERNEL_CONFIG=<private config>`, with one Node process per session family.
The old controller already demonstrates native persistent `ipython`, inline RLM,
host tools, SessionManager, abort and dispose. Its fixed B/R phase loop, fixed
OpenRouter binding and old model meter are superseded and cannot execute B/P
project research unchanged. New orchestration should retain the native SDK and
replace those research-local policies only.

## Model candidates and billability

Installed native `openai-codex` registry includes exact `gpt-5.5`, `gpt-5.6-sol`,
`gpt-5.6-terra`, `gpt-5.6-luna`, through `openai-codex-responses` at
`https://chatgpt.com/backend-api`. Prime OAuth metadata exists and expires
1789727935202. This verifies route registration and auth metadata, not a fresh
successful request, live model availability, usage completeness or invoiced cost.

Claude CLI `/Users/um-yunsang/.local/bin/claude` is 2.1.263. Its read-only auth
status reports loggedIn=true, authMethod=claude.ai, apiProvider=firstParty and
subscriptionType=max. No identifying fields are retained here. Prime anthropic
OAuth is expired (1788777148437), so it is not a qualified common native route.
Its registry contains claude-opus-4-6, claude-opus-4-7 and claude-sonnet-4-6;
the separate CLI subscription is a prospective UNQUALIFIED candidate until exact
runtime/model identity and usage/overage behavior are qualified. No auth repair or
provider request was made.

Historical paid setup is not zero and is not a new current expenditure. Old
model-meter records include an unknown/reserved setup incident. Preserve that
separate provenance; do not seed the new KRW ledger by copying old caps or estimated
USD reserves. Existing subscription access does not establish zero additional
charge when overage behavior is unknown. The root owns explicit prospective
subscription-only admission and provider usage recording.

## Evidence classification and limitations

Current CLI/API/code/image observations are directly_supported. Old memory's
native pause and ORX wait caveat match current rules. Old task counts, budget caps,
fixed-model policies and experiment_authorized=false are near_match_only or
superseded by current user intent; they were not reused as authority.

`docs/CODEX-NAVIGATION-GUIDE.md` is absent. Initial large combined output was
truncated; relevant controller, wrapper, meter and adapter dependencies were
subsequently read in bounded full-file reads. Live API availability is required for
the adapter; if it disappears, submission stops. Focused tests use fake transport,
and live validation is read-only. Root owns required `npm run check` after all
concurrent code changes, complete new-launch validation and independent review.
