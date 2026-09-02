# Coding-agent harness architecture differentiation matrix

**Status:** preliminary; only cells with a source id and read level support a comparison. Blank or `not established` cells are not negative claims. Product lineage and implementation migration are excluded from the public paper.

## Source classes

- **Own lineage source:** Prime Agent `2608.23552` (`FULL_PAPER_READ`). A separate pi paper has not yet been confirmed; official-document fallback is pending a focused search.
- **Concept-origin or direct mechanism sources:** RLM `2512.24601`, MemGPT `2310.08560`, ReAct `2210.03629`, Code as Agent Harness `2605.18747`, Scroll `2608.21690`, LLMRouter `2608.06867`, resample/reroute `2607.08665v1`, controlled orchestration `2608.00685`, and Agora `2607.09600v2` (all `FULL_PAPER_READ`).
- **Contrast harness/system sources:** Dive into Claude Code `2604.14228`, LongHorizon-Harness `2608.01964`, Scroll `2608.21690` (all `FULL_PAPER_READ`). SWE-agent/OpenHands and another coding-harness primary source remain pending.

## Matrix

| Axis | pi / Prime Agent lineage | Concept source | Claude Code contrast | LongHorizon contrast | Scroll contrast | Current comparison status |
|---|---|---|---|---|---|---|
| Programming-mediated context management | Prime Agent `2608.23552` FULL: persistent programmatic context substrate | RLM `2512.24601` FULL; MemGPT `2310.08560` FULL; Scroll `2608.21690` FULL | Dive `2604.14228` FULL: multi-layer compaction and file memory | `2608.01964` FULL: compact audited task state outside fresh executor contexts | `2608.21690` FULL: append-only history, persistent Python namespace, printed working projections | Supported comparison: programmatic recoverable state versus compaction and audited summaries; no local effect claim |
| Executable code / IPython-style primary action interface | Prime Agent `2608.23552` FULL: code-mediated action and computation | Code as Agent Harness `2605.18747` FULL; ReAct `2210.03629` FULL; Scroll `2608.21690` FULL | Dive `2604.14228` FULL: shell/file/service tool loop; not established as persistent IPython | `2608.01964` FULL: preserves native backend loops; code interface not isolated | `2608.21690` FULL: CodeAct-style exec and controlled capability object | Partial comparison; matched code-action versus JSON/tool-call experiment still absent |
| Persistent process, session, goal, heartbeat, schedule | Prime Agent `2608.23552` FULL covers daemon/session continuity at high level; feature-specific paper evidence incomplete | LoopsBench `2608.00267` FULL supports persistent objectives, progress criteria, work distribution, and regression obligations | Dive `2604.14228` FULL: single CLI loop and append-oriented session storage; goal/schedule semantics not established | `2608.01964` FULL: repeated manager–executor–auditor rounds with external task state | Scroll `2608.21690` FULL: persistent session environment, not an autonomous scheduler | Incomplete; feature-specific own/public source and failure-recovery experiment needed |
| Recursive LM delegation | Prime Agent `2608.23552` FULL: recursive RLM sessions | RLM `2512.24601` FULL | Dive `2604.14228` FULL supports subagent delegation but not recursive subproblem-sized LM routing | Fresh-context roles in `2608.01964` FULL; recursive LM semantics not established | not established | Supported distinction only for recursion versus generic delegation; routing effect untested |
| Session tree, minimal tools, skills, approval | Prime Agent `2608.23552` FULL at architectural level | Code as Agent Harness `2605.18747` FULL; ReAct `2210.03629` FULL | Dive `2604.14228` FULL: permissions, skills/plugins/hooks, subagents, session storage | `2608.01964` FULL: role separation and read-only audit | `2608.21690` FULL: fail-closed capability surface, not a full coding harness | Partial; exact minimal-tool/session-tree differentiation needs own and contrast primary sources |
| Dynamic model/workflow routing | feature-specific own/public source not verified; current substrate permits model choice but effect is unestablished | LLMRouter `2608.06867`, resample/reroute `2607.08665v1`, controlled orchestration `2608.00685`, Agora `2607.09600v2` FULL: task/budget/verifier/backbone/workflow dependence | not established | interchangeable backends in `2608.01964` FULL, but task-conditioned selection not isolated | multi-backbone evaluation in `2608.21690` FULL, not routing | Concept/mechanism evidence complete; own/contrast behavior and matched H-E effect remain unestablished |

## Permitted public summary

The current literature supports only a generic statement: coding-agent harnesses differ in how they manage context, authorize actions, persist task state, delegate work, and expose extensibility. The proposed system selects a programmatic, persistent, capability-bounded context substrate and evaluates its research-state layer separately. It does not claim uniqueness until own-source, concept-source, and contrast-source evidence is complete for an axis.

## Missing evidence

1. Confirm whether pi has an archival paper or technical report distinct from Prime Agent; otherwise record official-document substitutions by axis.
2. Full-read primary SWE-agent and OpenHands sources as direct coding-harness contrasts.
3. Pin official provider/model capability and fallback specifications if product behavior enters the comparison.
4. Matched experiments for persistent code action, daemon recovery, recursive delegation, and dynamic routing.
