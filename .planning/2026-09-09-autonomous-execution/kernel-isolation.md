# Native kernel isolation qualification

Owner: kernel-isolation lane. Scope: four research-local apparatus files and this receipt; no native runtime edits or scientific dataset/model runs.

Plan: (1) inspect installed native protocol and frozen base image [complete]; (2) implement wrapper, shared reservations, private source image [complete]; (3) run focused synthetic protocol, path, resource, cancellation, and snapshot checks [complete]; (4) report exact identities and limitations [complete]. Root owns the active task plan, findings, and progress files.

Live evidence: installed `prime-agent-runtime` 0.1.0 uses protocol 3, stdio host requests and dill snapshots. Base image ID `sha256:cd43d0d8edac942bd67cd097caf08edd2def45016bf011c1635849f15ebc7835` retains Python 3.11.16, scikit-learn 1.6.1, pandas 2.2.3, numpy 1.26.4, scipy 1.14.1. Source owner is `/opt/homebrew/lib/node_modules/prime-agent/dist/prime-agent-runtime`. `docs/CODEX-NAVIGATION-GUIDE.md` is absent. Historical memory was navigation only; current user permission and root's current authorization supersede its design-only launch state.

Interface accepted by root: `PRIME_AGENT_KERNEL_PYTHON` points to the executable wrapper and `ARGO_KERNEL_CONFIG` names host-only JSON. Shared resource pool sums parent, native children and fit leases; kernel defaults 0.5 CPU/512 MiB, episode maximum 2 CPU/8 GiB. Wall times allocated CPU is recorded as a conservative charge separately from measured CPU. Idle kernels do not count as scientific training jobs. No auth, profile, custody or Docker socket mounts.

## Qualified artifact

**PASS: synthetic native kernel isolation.** Final image `sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c`, local tag `argo-study-kernel:20260909`. Build context and logs: `~/.local/share/argo-study-20260909/build-kernel`. Installed eight native Python module hashes equal the original runtime source bytes. Source tree SHA256: `1c0f9322b40f3c052cdd4ab25c123c089bc3575be21c8b90d6feea5e8f6f089a`. All 55 scientific/runtime dependency distributions are version-pinned in `requirements-kernel.txt`; the unchanged native distribution adds `prime-agent-runtime==0.1.0`. Full source, artifact and version identities are in `kernel-isolation.json`.

Final focused test command (from `experiments/argo_study_20260909`):

```sh
ARGO_KERNEL_TEST_IMAGE=sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c python3 -m unittest -v test_kernel_wrapper.py
```

Result: **11/11 passed, 0 skipped, 12.605 seconds**. Covers actual protocol 3, persistent namespace, host-request/reply, snapshot/restore, interrupt then subsequent execution, SIGTERM, wrapper SIGKILL, process-group SIGKILL, absolute deadline, two bind mounts, nonroot, empty capability set, network none, failed external connection, read-only root, actual Docker resource values, mount escape rejection and shared resource admission/accounting. No orphan study containers remained. Separately, the installed Prime `ensureKernelPython({pythonSkills: []})` accepted the wrapper after all 13 actual native readiness/import probes; stderr empty, no live resource leases afterward. Its conservative charge was 3.6417 core-seconds, not measured CPU usage.

## Launch interface

Create three sibling directories below an episode within `~/.local/share/argo-study-20260909`: `workspace/`, `artifacts/`, `control/`. The config must be in `control/`. The exact names and canonical paths are checked; all must belong to the current nonroot host user. Only the first two are mounted. Do not place the episode underneath `custody`, `source`, `test` or another protected area.

```json
{
  "image": "sha256:a70ce9ad201eb7695c4d8e4e7085271cdb09092c173253b002424b9508f9fd8c",
  "workspace": "/Users/um-yunsang/.local/share/argo-study-20260909/episodes/EPISODE/workspace",
  "artifact_root": "/Users/um-yunsang/.local/share/argo-study-20260909/episodes/EPISODE/artifacts",
  "control_dir": "/Users/um-yunsang/.local/share/argo-study-20260909/episodes/EPISODE/control",
  "deadline_epoch": 0,
  "kernel_cpus": 0.5,
  "kernel_memory_bytes": 536870912,
  "episode_cpus": 2,
  "episode_memory_bytes": 8589934592,
  "max_cpu_seconds": 7200,
  "pids_limit": 128,
  "docker": "/opt/homebrew/bin/docker"
}
```

`EPISODE` and `deadline_epoch=0` above are placeholders: substitute the frozen episode path and a real finite future Unix timestamp. The wrapper rejects the placeholder deadline. Export the following only in the research host process:

```sh
PRIME_AGENT_KERNEL_PYTHON=/Users/um-yunsang/argo-paper-orx/experiments/argo_study_20260909/kernel_wrapper.py
ARGO_KERNEL_CONFIG=/Users/um-yunsang/.local/share/argo-study-20260909/episodes/EPISODE/control/kernel.json
```

The native host supplies `RLM_DEPTH`, `RLM_MAX_DEPTH`, `RLM_SESSION_DIR` and `RLM_HARNESS_STATE_DIR`; path values must be under the two allowed mount roots. Ambient credentials and other host environment variables are not forwarded. Global harness state is forced into the episode artifact tree. Both native `-c` readiness calls and `-m rlm.repl` use the same source image and wrapper. Protocol stdout has no wrapper banners.

Public Python API: `load_config(path) -> Config`; `reserve_resources(cfg, name, cpus, memory_bytes, kind="fit", pid=None) -> lease`; `release_resources(cfg, lease, reason="completed", measured_cpu_seconds=None)`; `remaining_seconds(cfg)`; `remaining_cpu_seconds(cfg)`. `kind` can be `kernel`, `fit` or `probe`. Reservations use host-only flock and immutable episode limits. Each caller must poll remaining bounds while active and release only after its process/container is confirmed stopped. Stale leases are not silently reclaimed. The independent bridge owns final-phase reservation and its scientific receipt.

Each wrapper invocation uses an explicit random container name and detached watchdog process. A responsive Docker daemon is checked for positive container absence before releasing its lease. An unavailable daemon produces an UNKNOWN cleanup receipt and keeps the lease reserved. The watchdog entrypoint is reusable by the fit bridge with its explicit owner PID, container name, lease and host-only record containing the Docker CLI PID.

## Limits of this result

No provider request, actual dataset, model fit, scorer execution or complete daemon recovery was exercised here. The native host-request handler and ORX bridge are separate root-owned boundaries. Mount validation cannot discover a trusted host copying hidden data under an innocuous filename; authorized worker-view materialization remains required. The CPU ledger charges wall time times allocated CPUs, including idle kernels and cleanup. Measured CPU stays null unless separately supplied. Runtime packages and source are pinned; the isolated wheel-build backend was resolved during build, so the immutable image ID is execution authority rather than a claim of bit-for-bit image rebuild. Root owns the required repository `npm run check` after concurrent apparatus changes.

Errors resolved: initial broad file listing output was truncated (narrowed subsequent reads); optional navigation guide absent; initial dependency resolution selected two newer transitive packages, which were pinned back to the already installed compatible versions before the final image. Final focused tests and native bootstrap passed.
