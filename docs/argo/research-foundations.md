# ARGO research foundations

This is the curated starting set for the ARGO implementation and graduation thesis. Discovery results are candidates. Method or result claims below are included only after the selected source was read, unless marked `ABSTRACT_VERIFIED`.

## Harness substrate

- [Prime Agent: A Self-Improving RLM Harness](https://www.alphaxiv.org/abs/2608.23552) defines the inherited four-level information hierarchy, persistent IPython computation, recursive sessions, daemon continuity, Continual Harness, and long-horizon evaluation substrate. ARGO treats this as its software and research ancestry, not as an external plugin.
- [Recursive Language Models](https://www.alphaxiv.org/abs/2512.24601) treats long prompts as an external environment that a model examines and decomposes programmatically with recursive calls. This entry is currently **`ABSTRACT_VERIFIED` only**; detailed method claims need a focused full read before the thesis uses them.
- [Continual Harness](https://www.alphaxiv.org/abs/2605.09998) performs reset-free online edits to prompts, subagents, skills, and memory from trajectory windows. Its in-episode adaptation motivates ARGO's engine-refine lineage, while the reported risk of preserving harmful shortcuts motivates independent held-out gates and rollback.

## Research design and evidence state

- [The AI Scientist](https://www.alphaxiv.org/abs/2408.06292) demonstrates end-to-end idea, experiment, writing, and review automation, while its reported subtle code errors, positive bias, incomplete controls, and execution risks motivate stronger evidence identity.
- [Towards an AI Co-Scientist](https://www.alphaxiv.org/abs/2502.18864) uses specialized generation, reflection, ranking, proximity, evolution, and meta-review agents to compete hypotheses. ARGO borrows explicit design competition but adds immutable protocols and run evidence.
- [SciAgents](https://www.alphaxiv.org/abs/2409.05556) grounds multi-agent hypothesis generation in a literature-derived knowledge graph. ARGO distinguishes that literature ontology from an operational hypothesis/protocol/run/evidence graph.
- [EviGraph](https://www.alphaxiv.org/abs/2608.04738) makes typed evidence chains operational and repairs downstream dependencies from the earliest weak node. ARGO preserves answered experiment nodes and creates descendant research states rather than rewriting the run that produced evidence.
- [EurekAgent](https://www.alphaxiv.org/abs/2606.13662) frames permissions, artifacts, budgets, and human supervision as environment engineering. ARGO adds scientific-admission and scope logic that a metric-driven environment alone does not provide.

## Experiment lifecycle

- [OpenResearch CLI](https://github.com/alphaXiv/openresearch-cli) is the current lifecycle authority for immutable experiment branches, fixed command/environment, code-only variation, run logs, and a downward experiment tree. ARGO first imports read-only receipts, then migrates only through a capability-gated native boundary.

## Paper evidence rule

Every source record uses the canonical ordered enum in `paper-pipeline-contract.md`. `DISCOVERY_ONLY` and `ABSTRACT_VERIFIED` may motivate a question but cannot support detailed method or result claims.
