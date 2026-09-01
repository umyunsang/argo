# Autonomous research-decision contract

ARGO may choose research questions, hypotheses, conditions, variables, controls, methods, metrics, falsifiers, and stop rules. Autonomy means owning the reasoning process, not generating arbitrary choices.

## Required decision record

Every consequential research choice is immutable once its experiment starts and contains:

```text
id and timestamp
active objective and human authority boundary
problem and unresolved gap
choice being made
candidate alternatives from at least two distinct mechanisms
primary-source and full-paper evidence for each alternative
counterevidence and negative prior work
assumptions and identifiability conditions
population, unit of analysis, data provenance, and split
intervention, matched control, variables, and isolated difference
estimand and metric
measurement implementation and uncertainty method
falsifier, guardrails, stop rule, and reopen condition
expected information gained under positive, null, negative, and failed-execution outcomes
compute, time, license, safety, and opportunity costs
independent critique
selected alternative and causal rationale
rejected alternatives and why they lost
remaining uncertainty
protocol fingerprint and code parent
```

## Selection sequence

1. **Authority:** Is the action within the agent's authority? External transmission, spending, risky tools, submission, and final conclusions remain human-owned.
2. **Legality and ethics:** Block illegal, unlicensed, privacy-violating, or academically misleading designs.
3. **Identifiability:** Can the available observations distinguish the claim from its null and major confounders?
4. **Evidence:** At least one primary/full-read source must support the mechanism. Discovery snippets only open a search.
5. **Competition:** Compare mechanism-distinct designs, not cosmetic hyperparameter variants.
6. **Comparability:** Freeze data, split, target, estimand, baseline, metric, aggregation, code, environment, pretrained resources, and deployment identity.
7. **Information value:** Prefer the design whose possible outcomes most reduce an important uncertainty per unit cost, subject to validity and safety.
8. **Independent attack:** A separate critic tries to break assumptions, leakage controls, falsifiers, and claimed isolation.
9. **Preregistration:** Freeze the selected design and decision rule before outcome evidence is visible.
10. **Assimilation:** Results update only their measured scope. Execution failure updates engineering state, not the scientific hypothesis.

## Prohibited shortcuts

- selecting a method only because it is recent, popular, or produces a larger local score;
- treating citation count, model confidence, or agent vote as evidence of local efficacy;
- changing metric, split, baseline, or stop rule after seeing results without opening a new design;
- globally closing a family from a scoped negative experiment;
- writing a result or thesis claim that lacks an immutable artifact and protocol identity;
- silently converting an inherited mechanism into an original contribution.

## Paper linkage

The final paper does not reconstruct rationale from memory. Its problem formulation, hypotheses, methods, ablations, limitations, and discussion are rendered from these records and their evidence graph. If a choice has no record, the paper must label it exploratory or omit the claim.
