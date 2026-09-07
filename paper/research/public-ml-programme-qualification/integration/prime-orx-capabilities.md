# Prime Agent + ORX capability contract (read-only)

**Status:** capability qualified; no scientific run admitted.  
**Scope:** use the existing Prime daemon, `AgentSession`, persistent IPython REPL, `rlm`, `agent_message`, and installed `orx`. Do not add a wrapper, supervisor, run registry, native change, account/credential operation, dependency, or compute call in this lane. An account need is an escalation item, not an automatic task exclusion.

Companion machine record: `prime-orx-capabilities.json` (`sha256:7852b1a18890412477ace2109ee034be3c110b814909dfc10b698e6c93e8fd91`).

## Version and authority pin

| Surface | Observed version / pin | Meaning |
|---|---|---|
| Repository source | HEAD `4cd5d0e6ae7052a0a91682865e1bfabdc64c1d10`; package declares `0.9.1` | All examined tracked native paths matched HEAD. The worktree was otherwise dirty from parallel lanes, so new research records are not identified as committed source. |
| Installed Prime CLI | `0.9.2`; package JSON `sha256:46d8fba9e782d0a9fb3fb43ee35efacbebcfd5828544cbf3cad336be4c3b4841` | This is newer than the repository declaration. Installed source-map contents, not repo version alone, ground current runtime claims. The exact resident daemon build was not separately queried. |
| Current kernel `rlm` | distribution `0.1.0`; module `sha256:8bc9a0e945e3c1ffb9b4b59b730cb9886303a0b0192b69a421aa284e90450ff3` | Its public signatures match the documented callable `rlm`/registry interface. |
| Installed ORX | `0.1.120`; Mach-O arm64 binary `sha256:03097743c44a2562e14d2d22dab783b9a57005d24b5f4b637acc426c92ee6756` | Supersedes the repository's older `orx-usage.md` observation of `0.1.117`. This review pins current help/manual output; it does not infer undocumented guarantees. |
| Effective research authority | `effective-authority-v1.json`, `sha256:9f68eb4074ec25e7b90bf63fffdc6e758e51b33ea6bb0e2a4287f3460ae8cdd2`; correction `666dade1` | Apparatus code/local mocks are approved. Model/train/eval is approved only in principle. No concrete P0 envelope or scientific run is authorized. Native pause remains. Account/auth/terms needs must be proposed to the user, not used alone to reject a task. |

## Access-dependency correction

Latest user correction `666dade1` is: `계정이 필요하면 나한데 요청을해, 제외하지말고 이런 중요한 결정사항은 물어보고 진행해.` (`sha256:3d8c5e6a92b6a425e8c22ebf9814439412c3c581fdcf887babd7fb64344cba36`).

- Do not exclude a scientifically strong task solely because it needs an account, authentication, organization membership, terms acceptance, or paid access.
- Record a secret-free `ACCESS_DEPENDENCY`: provider/service, access kind, scientific value versus available alternatives, official setup/terms reference, expected cost ceiling, data/license constraints, and current status.
- Root must present the task-selection, exclusion, scope, and cost tradeoff. The user confirms the important decision and performs or explicitly authorizes setup.
- This correction does **not** authorize account/credential inspection, login, terms acceptance, secret collection, paid execution, managed compute, ORX state mutation, or native change. Planner records only opaque access receipts, never credential bytes.

## Exact capability table

| Surface | Available now | Exact contract | Not established |
|---|---|---|---|
| Prime daemon / `AgentSession` | Existing substrate | Prime owns process, session, kernel, child lifecycle, routing, and recovery. Apparatus calls public REPL skills only. | No scientific truth, ORX lifecycle ownership, hard security boundary, or fixed workload cap. |
| Persistent REPL | Yes | Ordinary cells execute serially in one shared namespace. Independent RLM child `AgentSession`s can run concurrently. | Concurrent ordinary cells, immutable namespace, or complete snapshot recovery. |
| `await rlm(prompt, name=..., model=..., thinking=...)` | Yes | Returns only `{rlm_child_id,name,session_dir,model}` after admission. Only `name`, `model`, and `thinking` are accepted options. | Child answer, completion, scientific request ID, ORX run ID, usage, or exactly-once spawn. |
| `await rlm.list_subagents()` | Yes, parent-scoped | Recovers direct children with stable IDs/name/session directory and `running|completed|error`. Use this before any missing-response recovery. | A global registry or proof that an absent child caused no external side effect. |
| `agent_message.send(...)` | Yes, family-scoped | Child explicitly replies to parent. Parent can address the same retained child for follow-up. `delivered`/`queued` is a delivery receipt only. | Scientific acceptance, ORX launch acceptance, or a global agent census. |
| RLM parallelism | Yes, caller-bounded | Current plan permits **at most five direct child lanes plus root**, with no nested delegation. `/rlm-max-depth 1` can prevent child recursion if set and recorded. | Native breadth cap. Prime documents no fixed workload cap; max depth limits generations, not direct-child count. |
| Child file ownership | Procedural only | Give every child an exact disjoint path. Parent verifies bytes and hashes at fan-in. Each child has a unique artifact `session_dir`. | Separate repo worktree or OS isolation. Installed `AgentSession` creates children with the parent's `cwd`. |
| Prime child usage | Partial | Child assistant usage/cost is attributed to the parent turn. | Complete CPU/GPU, ORX, retrieval, filesystem, provider-side, or billing ledger. |
| `orx exp run <expId> --backend local` | Capability present; **not authorized for this P0** | For a locally initialized experiment, ORX runs the recorded commit snapshot in an isolated run directory and a detached ORX supervisor records state/logs. Bundled guide says local project/run commands need no login. This is one path, not a rule excluding account-dependent alternatives. | Security isolation. The local process shares this machine's environment/resources, and the local backend exposes no timeout flag. |
| Frozen ORX identity | Conditional | Before launch, bind exact project ID, experiment ID, recorded commit, and fixed run-command digest from `orx exp status`. Launch committed bytes only. | Stable machine-readable JSON: observed `status`/`runs` help has no `--json`. Any parser must be pinned to `0.1.120`, fixture-tested, and fail closed. |
| ORX status / ID | Yes for ORX records | `orx runs <projectId> --experiment <expId>` is the post-signal source of truth; obtain the run ID there. `orx exp status <expId>` shows the latest run and command. | Arbitrary `external_request_id` lookup, raw provider launch census, or proof that a missing row means no launch. |
| ORX logs | Yes, run-scoped | `orx logs <runId>` with `--head`, `--bytes`, or `--range`; preserve stdout and stderr range metadata. A result needs supporting log bytes. | Status-only evidence or absence inferred from truncated output. |
| ORX artifacts | No general CLI enumeration seen | The task command must emit a machine-readable artifact manifest and expose bytes through a task-certified handoff. Bind `{project,experiment,run,commit,path,sha256,size}`. | General artifact list/fetch, receipt enumeration, or completeness from a type/path name. |
| ORX idempotency | **Not exposed / not verified** | Never retry an uncertain launch automatically. `--force` is forbidden. Without `--force`, the manual says an in-flight run on the same experiment is rejected. | Client-supplied request ID, replay idempotency, or exactly-once execution. The in-flight check is only a concurrency guard. |
| ORX cancellation | Experiment-scoped | Public CLI is `orx exp cancel <expId>`. Use only after `runs/status` shows one unambiguous bound in-flight run, then reconcile. | Public cancel-by-run-ID. If concurrent runs exist, help does not say which run is targeted. |
| Hidden scorer | Not supplied by Prime/ORX local isolation | Keep hidden labels and scorer bytes outside every agent-readable same-user path/process. Planner sees only public task/source receipts plus an opaque scorer contract ID/hash. | Trusted hard gate, scorer custody, or bypass prevention. These remain task-specific certification items. |

Prime's daemon command journal uses `clientId + commandId` and deliberately does not replay an uncertain mutation. That protection belongs to Prime's public daemon command boundary. `RlmRunRequest` has only `prompt`, `kwargs`, and optional cell source, and `orx exp run --help` exposes no client request ID. Do not transfer the daemon's idempotency claim to RLM or ORX.

## One-run binding contract

This is a request/receipt protocol, not another lifecycle registry. ORX remains the run authority.

1. **Freeze `RunIntent`.** The parent writes canonical bytes and a digest. Required bindings are: public task/description/source/license/ancestry receipts; protocol fingerprint; ORX `0.1.120` binary digest; project/experiment ID; recorded commit; fixed command and environment digests; artifact-handoff digest; opaque scorer contract digest; latest authority digest; selection/missingness/retry rules; and a numeric phase-budget digest.
2. **Fail-closed preflight.** Any null or mismatch blocks. Current task values for P0 task, project, experiment, metric, MUE, scorer, numeric budget, and exact execution approval are still null.
3. **Admit one execution child.** Use a deterministic unique child name derived from the request digest. Record the Prime spawn handle. Other RLM lanes stay read-only. The handle proves admission only.
4. **Request once.** The child re-hashes the request and invokes exactly one frozen command, eventually `orx exp run <expId> --backend local`, with no `--force`. It retains raw stdout/stderr/exit bytes.
5. **Reconcile into ORX identity.** Query `orx runs <projectId> --experiment <expId>` and `orx exp status <expId>`. Bind only one unambiguous matching run and recorded commit. Otherwise set `UNKNOWN/BLOCKED`; do not repeat.
6. **Monitor without a second supervisor.** Use one of `orx exp wake` or `orx exp wait`. After any signal, re-read `orx runs`; the manual says wait is not the source of truth. Do not tight-poll or use `sleep`.
7. **Import terminal evidence.** Read and hash sufficient run-log ranges. Validate effective configuration, final metric/summary, and the task artifact manifest. Status alone is not evidence.
8. **Bind artifact bytes.** Verify `project_id`, `experiment_id`, `run_id`, recorded commit, relative path, SHA-256, and size. Artifact retrieval/handoff must have task-specific certification because general artifact enumeration is absent.
9. **Parent locks one artifact.** The root selects from public/dev evidence, writes the exact single-artifact lock, and verifies bytes again. Children may recommend candidates but do not own the final lock. No mutation or hidden-score reselection is allowed.
10. **Score behind the trusted boundary.** Submit only the opaque locked artifact after separate scorer/run authorization. Import a typed score receipt; do not expose hidden labels.

### Immutable phase budget

A run request must numerically fix: allowed child names; max direct children; max depth; model/thinking per lane; all-descendant model-call/token ceilings; parent turn/wall limits; source retrievals; ORX launches and repairs; exact backend; CPU/GPU/step or task self-time bound; deadline; currency ceiling; artifact count; scorer calls; and human-intervention rule.

For this qualification fan-out, the only fixed concurrency value is five children plus root/no nesting. It is a planning limit, not a hard runtime gate. For a future local P0, ORX's lack of a local `--timeout` means the task command needs its own certified stop bound. Do not call the campaign bounded until that is tested.

## Missing-response rule: never duplicate execution

| Observation | Required action |
|---|---|
| `rlm()` result/handle missing | Query `rlm.list_subagents()` by deterministic name in the same parent. If found, reuse it. If absent, keep admission `UNKNOWN`; do not auto-spawn a second execution child. |
| Child completed without explicit reply | Read only its owned receipt file and registry status, then follow up in the same retained child. Prime can emit `completed_without_reply`. Do not respawn or delete early. |
| ORX launch output missing | Enter `RECONCILING`; query exact project+experiment. Bind one matching run only. Zero, multiple, or commit mismatch stays `UNKNOWN/BLOCKED` for human/task-specific recovery review. |
| `orx exp wait` timeout | It means no observed change, not run failure. Re-read `runs/status`; do not refill or relaunch from timeout alone. |
| Terminal state but truncated/incomplete log | Read more byte ranges. Keep the outcome `NOT_OBSERVED` until supporting bytes exist. |
| Cancellation needed | Confirm exactly one bound in-flight run; call `orx exp cancel <expId>`; then reconcile terminal state. Multiple candidates block because no public cancel-by-run-ID was observed. |

## What can be used immediately

Under the current authority and this user's operational instruction:

- use Prime RLM for disjoint public-source and source-code qualification lanes;
- write task-local apparatus/spec files and run only bounded static/mock/synthetic fixtures in the approved roots;
- create a prospective content-addressed `RunIntent` with unavailable scientific fields left blocked;
- keep public task descriptions and source receipts in the planner; keep hidden labels/scorer outside it.
- record account/auth/terms/cost needs as `ACCESS_DEPENDENCY`; root proposes the tradeoff and asks the user rather than excluding the task.

Do **not** now run or mutate ORX (`up`, project edits, experiment creation, launch, cancel), run a scientific task model/train/eval or hidden scorer, inspect account/credential state, log in, accept terms, pay, install anything, use managed compute, publish, or change Prime native code.

**Feasibility conclusion:** the installed CLI can support a small local task without an ORX login and without Prime native edits. That is one capability, not a task-selection constraint or current readiness. Account-dependent candidates remain eligible through the `ACCESS_DEPENDENCY` flow. Every real run still needs the relevant access decision, a locally initialized ORX experiment, task-specific certification of task/data/license/ancestry, fixed command/environment, artifact handoff, hidden scorer custody, metric/MUE/selection/missingness, numerical resource envelope, and exact user approval.

## Minimal adapter obligations

1. Validate one immutable request and phase-budget digest; fail closed.
2. Treat account/auth/terms as `ACCESS_DEPENDENCY`: root proposes the task/scope/cost tradeoff and asks the user; never auto-exclude or auto-login.
3. Assign exactly one execution lane; all other children remain read-only.
4. Call the existing CLI once without `--force`; never supervise ORX yourself.
5. Preserve raw CLI bytes and bind ORX-owned identity/status/logs into one content-addressed receipt. Do not redefine lifecycle state.
6. Require a task-certified artifact manifest/handoff; re-hash bytes at lock and scorer ingress.
7. Keep final selection with the parent and hidden evaluation with the trusted scorer.
8. Keep ambiguity as `UNKNOWN/BLOCKED`; prohibit automatic retry, replacement, and score fabrication.
9. Report ORX-recorded coverage and partial usage only. Never claim exactly-once, full direct-launch coverage, hard-gate enforcement, security isolation, or complete billing.

## Evidence and commands

Key exact source receipts:

- Installed Prime `docs/rlm-runtime.md` is byte-identical to repo `packages/coding-agent/docs/rlm-runtime.md`, `sha256:66295567f8c61be445f100dbcd90509034a6c954124c51fe91a2f598f42151f6`; admission-vs-answer is lines 23–32 (`excerpt sha256:b723c5af3bbd5acf4f56bb854e3fd1c0fb9e6198efac0b846699d1bf9fbf98a0`), shared-REPL concurrency is lines 90–109 (`54ede4a095858e98bfb9594b2356b4e3e427003c1dced65078f5d9f419d3b723`), and registry/follow-up is lines 157–177 (`35450ed3ca25e76283445589ec77e1e71a87d2b07b97a8779a7d834f66ef0948`).
- Installed `dist/core/rlm-runtime.js.map`, `sha256:13a13a205e5064c8c974d34873924fc35929184a32af0ad13e957a9cd21068b2`, embeds source `sha256:87669b9a83e38561724046dbe0bdbc6ac6d01e55356c2cf80e6fdcaca1afc4ce`; lines 8–20 contain the request and four-field handle (`excerpt sha256:5f57638ef86f526a8ae07dfd811c36fbe832709385eea37e68908b09029a775d`).
- Installed `dist/core/agent-session.js.map`, `sha256:64e13f1ba0adf96c308d487da21769698e859d515d34074c65d6817dfc31cc90`, embeds source `sha256:d20e5b91387944993d48dad976a90fed5c0e74188ee4dbc615f240ecf58da219`; lines 9633–9673 show shared parent `cwd` (`excerpt sha256:cc43df7f1da7e48f973259d939876676f81e13881549cc23d9c7c5ccb80eae49`), and lines 10692–10699 plus 10942–10949 show detached execution and admission handle (`900726f1dc05511458ff4bde8dbc76e2d683d21c71aa720819287db37a89ad46`, `5422eab8ab73bd8f77cef1308f082cb2b78d1378b9e2754b128a2ff2808787c5`).
- `packages/coding-agent/src/modes/daemon/command-recovery-journal.ts`, lines 44–52, `sha256:e3cdec9da73b2befee4ef5d843dece43e741bcd16a5932d003f47a5a3114e0ab`, says a missing result is uncertain and never replayed (`excerpt sha256:621a1f178160ca74c33c19f01ef40ac1b7ec6f4b5f866d07eaa9df50fc1ac414`).
- Existing `source-contract-checks.json`, `sha256:8625d3e9be6787f11442d5a919c2a67ffeec8b7bd5b1bc7ef793a2bba2f1974e`, already concluded there is no verified external idempotency/exactly-once guarantee. This lane updates the installed ORX pin and defines the concrete no-duplicate protocol rather than repeating the generic review.

Read-only commands all exited 0 unless stated:

| Command | Outcome / full output SHA-256 |
|---|---|
| `git rev-parse HEAD` | `4cd5d0e6ae7052a0a91682865e1bfabdc64c1d10` |
| `prime-agent --version` | `prime-agent 0.9.2`; `f34248c2449a022d41c918d1e995ad85859a1e9f0e6f89d0af23ae4a55519f71` |
| `orx --version` | `orx 0.1.120`; `ec29866828163f902cc3e1b042919ffb6117e1cd1d23fb87159755c175898967` |
| `orx skill` | bundled current guide read; `6003c2b45c28b7c207bb7f4cd18dc8b976b4be3c6c2af1268aa4495f9f54e723` |
| `orx skill compute` | commit snapshot, fixed command, no-`--force` in-flight guard, wait/wake rules; `85e0a8c88d8e820b3e89d840f6c60f67925b576ebc4dc4e64cffbd91e152a6da` |
| `orx skill compute/local` | local detached runner, shared resources, no timeout flag, isolated run directory; `6ba6f018fb80bbb92d37f23bfc7b48b1d1c8f2e8511a12c53f2cf9ffcea53588` |
| `orx skill evidence` | logs/ranges and evidence requirements; `1a13fac78c80f6ef59f62c0cf7525fd332773ef177f4028985883ccd4ffaf271` |
| `orx exp run/status/cancel/wait/wake --help`, `orx runs --help`, `orx logs --help`, `orx project view --help` | Help only. Exact outputs and hashes are in the JSON companion. No `--json`, client request ID, cancel-by-run-ID, artifact enumeration, or receipt-enumeration flag was observed. |
| `file`, `codesign -dv`, SHA-256 over the ORX binary | Mach-O arm64, ad hoc linker signature, binary hash above. Static binary-string hits were treated as non-authoritative and did not upgrade any capability. |

No ORX account/credential lookup or operational project/experiment/run command was issued; only version/help/skill/manual calls were used. No ORX store record contents were read or mutated. No scientific run, child spawn, native edit, install, test, or commit occurred in this lane.
