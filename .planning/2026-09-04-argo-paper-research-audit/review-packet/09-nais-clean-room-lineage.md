# 09 — NAIS Clean-Room Lineage Plan

Status: **planning only; event artifact does not exist**  
Created: 2026-09-04T15:43:42+09:00

## Separation rule

The thesis harness, Study B code, experiment receipts, prompts, context graph, and this review packet are **not** the
event prototype. No current thesis artifact or local implementation is copied into the event build.

## Start ceremony inside the official window

1. Human records the official start time and event rule version.
2. Create a new empty repository and branch during the event window.
3. Record repository identity, initial commit, machine/environment fingerprint, and participant identities.
4. Add only public OSS dependencies allowed by the event. Record upstream URL, commit/tag, licence, and exact hashes.
5. Generate a lockfile and dependency manifest before custom code.
6. Preserve every build/run commit and artifact digest. Never import from the thesis or Study B workspace.

The signed application concept and public academic sources may guide human design, but no pre-event implementation,
test fixture, generated source, model transcript, or private context state is imported.

## Minimum event path

`sources/problem -> two designs -> deterministic rule admission -> one deterministic execution -> evidence-bound
decision -> one bounded refine step`

Interruption/resume is optional only if rules and time allow. The event path is a qualitative demonstration, not the
sample for causal significance.

## Required provenance manifest

- event start timestamp and rule snapshot;
- repository/branch/commit chain;
- public upstream source and licence for every dependency;
- dependency/environment lock hash;
- build and run commands;
- task/input/scorer hashes;
- model/provider revision and usage where permitted;
- artifact and demo-output hashes;
- participant sign-off that no pre-event implementation was imported.


## Optional standards-based export

If time permits, export the event artifact as an RO-Crate profile whose root lists task, protocol, environment, source,
run and output entities. Store detailed execution lineage as a separate W3C PROV bundle referenced from the crate.
RO-Crate profile validation, file checksum verification, and ARGO claim admissibility remain three separate checks; a
valid metadata package is not evidence of task correctness or efficacy.

## Fail-closed checks

Block publication as an event-built artifact if any file predates the official start without being a declared public
upstream dependency; if a thesis/Study B digest appears; if a dependency lacks licence/source identity; or if a reported
result lacks an event-window run receipt.
