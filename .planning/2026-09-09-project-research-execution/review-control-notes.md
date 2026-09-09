# Review control lane

## Plan
- Inspect authority and agree standalone API — complete.
- Implement blinded packets, evidence-linked quality assessment, freeze and one-use final reservation — complete.
- Run focused negative/boundary fixtures and report apparatus-only scope — complete.

## Findings
- Current `docs/argo/agent-brief.md` and `migration-state.json` preserve the native construction pause. This lane writes only research apparatus.
- Parent owns the active task plan, findings and progress; this file contains this lane's state to avoid overlapping writes.
- Memory registry entry `MEMORY.md:31-39` is a navigation hint only: prior experiment authorization is superseded by the current request. Native construction and research-evidence distinctions were checked live.
- `docs/CODEX-NAVIGATION-GUIDE.md` is absent; no experiment-specific `AGENTS.md` was found. No native code is in scope.
- Anonymous packets omit controller mapping, use opaque candidate/file IDs and fresh round/session IDs. Separate paths and Unix permissions are convenience controls, not same-user worker isolation.
- JSON metadata can be stripped safely in copies; code must retain scientific semantics. Unsupported binary formats or suspicious residual identity/prior-score content must be rejected rather than claimed anonymous.
- AAA checks can validate evidence linkage and review structure, not replace scientific judgment or actual independent execution. Tests are apparatus-only, and cannot confer a research AAA result.

## Progress and verification
- Read planning skill, active parent planning files, root instructions, agent brief and migration state.
- Proposed exact Python API and CLI interface to root. No paid calls or external writes.
- Initial `rg` discovery included absent `.agents`; narrowed discovery to installed skills. All modifications are limited to the three owned paths.
- Initial fixture run failed because macOS temporary-directory paths use the `/var` symlink; fixtures now pass canonical resolved roots while keeping artifact symlink rejection. No scientific run was affected.
- Added strict duplicate-key/non-finite JSON rejection and reproduction scope matching. Final split identity hashes only detect identical data; independent partitioning must also have evaluator evidence.
- Second fixture run exposed a packet-integrity gap: only the selected candidate's artifacts were checked. Assessment now verifies both candidates and rejects extra files/directories (including prior review history) from the fresh supervisor input. Added shared-hardlink rejection.
- Preserved scientific `model` configuration fields while redacting declared producing-model identities. Research configuration is evidence, not producer metadata.
- Focused command: `python3 -m unittest -v test_review.py` from `experiments/project_research`. Scope is apparatus-only; no actual team comparison, independent real reproduction, research AAA, superiority, final evaluation or PI acceptance is claimed.
- Final focused result: **30 tests passed**, 0.447 seconds. No tests, files, reservations or mock AAA results were written into a real campaign; all fixture state used disposable temporary directories.

## Integration interface

`CandidateSpec(candidate_id, team_id, workspace: Path, artifacts: tuple[str, ...], authors: tuple[str, ...], models: tuple[str, ...])` requires exactly two teams, disjoint canonical workspaces and explicit artifacts. Declare every producer identity. `build_blind_round(candidates, output_dir, layer="research_operations", evidence_scope="apparatus_only")` also accepts layer `evaluated_harness`; only actual research uses scope `development_research`. The return value contains paths and a new `supervisor_session_id`. Start that exact fresh supervisor session with only the returned supervisor directory mounted; controller data must remain outside it. Unix modes alone cannot establish same-user isolation.

`assess(assessment, supervisor_dir)` verifies fixed dimensions, the current round/session/layer, fresh-input attestation, artifact SHA-256 and real line locators (`L1` / `L1-L3`). Assessment shape is illustrated by `fixture_assessment` in the focused test. Findings require evidence, impact, minimum fix and recheck. Accepted rebuttals/fixes require current-supervisor acceptance, evidence and recheck evidence. Every dimension PASS plus no unresolved Critical/Major requires an independent reproduction JSON artifact with `kind`, `status`, matching `evidence_scope`, distinct producer/reproducer session IDs, execution ID, command, exit code 0 and environment/input/output SHA-256 digests. Receipt provenance remains the external controller's responsibility.

`freeze_candidate(round_dir, assessment, destination)` snapshots exactly the reviewed raw source bytes and assessment with hashes; one selection ends the round. `verify_freeze(freeze_dir)` detects modified/extra files. `reserve_final_evaluation(freeze_dir, split_receipt, registry_dir)` atomically records one candidate/one held-out split in the persistent controller SQLite registry; candidate, split ID and split hash are unique. Failed/cancelled evaluator attempts remain consumed. Reservations do not execute an evaluator.

The split receipt requires `split_id`, `split_sha256`, `purpose="final_evaluation"`, independent `evaluator_id`, `worker_access=false`, `independent_from_development=true`, nonempty `development_split_sha256`, `custody_evidence`, `independence_evidence`, and matching `evidence_scope`. It carries no hidden rows. The evaluator must verify real partition disjointness and runtime custody; unequal dataset hashes alone do not establish sample disjointness.

CLI: `python3 review.py blind <spec.json> <round-dir>`, `assess <assessment.json> <supervisor-dir>`, `freeze <round-dir> <assessment.json> <destination>`, `reserve-final <freeze-dir> <split-receipt.json> <registry-dir>`. JSON rejection exits 2. Default fixture scope produces only `APPARATUS_PASS` / `APPARATUS_RESERVATION`. Quality, superiority and PI acceptance are independent fields throughout.

## Remaining external integration requirements
- Wire packet-only supervisor launch and producer/evaluator mounts through the measured execution boundary. This module is not an alternate process controller.
- Keep the evaluation registry persistent and evaluator-owned across campaigns; a different empty registry cannot detect earlier use.
- Preserve all rejected/failed candidate workspaces and controller mappings in the research ledger. This module never deletes source candidates.
- Root runs the required repository `npm run check` once after lane integration; focused Python tests are already run here.
