# Human-anchored calibration label protocol

**Purpose:** produce the calibration set that makes judged scoring admissible. Until it exists, the selective evaluator admits nothing (`RD-2026-09-02-11B`).
**Required size:** at least 25 flawless labels for a 10 percent risk level at 95 percent confidence, computed from the guarantee rather than chosen (`RD-2026-09-02-11C`). A single labelling error raises the requirement, so the set must be clean rather than merely large.
**Status:** protocol frozen, labels not yet collected.

## What is labelled

The unit is one **(artifact, checklist element)** pair, not a whole artifact. This follows the analytic-rubric form: criteria are judged separately so a single impression cannot spread across a document.

For each pair the labeller answers one question:

> Does this artifact satisfy this element, judged only on what the artifact states?

with exactly one of `satisfied`, `not_satisfied`, `unclear`.

## Sampling

1. Draw pairs from artifacts on the frozen confirmation tasks only. Pilot artifacts are development data and are excluded.
2. Stratify by element so no single element supplies more than one fifth of the set, otherwise the threshold would be calibrated on one criterion.
3. Stratify by condition so the set is not dominated by one arm.
4. Draw with a fixed seed recorded in the label file before any label is written.

## Labeller instructions

- Judge only the artifact text. Do not consult the source study, the withheld target, or the automatic score.
- Do not read the checklist cue patterns. Read the element requirement in words.
- `unclear` is a real answer. Use it when the artifact is ambiguous rather than guessing; `unclear` items are excluded from the calibration set and counted separately.
- Do not revise an earlier label after seeing later items.

## Blinding

The label form shows the artifact text, the element requirement, and nothing else. Condition, task identity, repeat index, and the automatic verdict are withheld. This is what makes the label an anchor rather than a confirmation of the machine.

## Disagreement and quality

- A second labeller repeats a random 20 percent of pairs. Agreement on that overlap is reported before any threshold is computed.
- If overlap agreement is below the risk level being certified, the labels are not clean enough to certify it, and the protocol stops rather than proceeding.
- Every label is written once with a timestamp; corrections append a new record with a reason and never overwrite.

## Use

1. The judge produces a verdict and a confidence for each labelled pair, without seeing the label.
2. The selective evaluator selects the confidence threshold with an upper confidence bound on the error rate, not the empirical rate.
3. If no threshold certifies the risk level, the evaluator reports the required set size instead of a threshold, and judged scoring stays inadmissible.

## Falsifier

If judge errors are concentrated at the top of the confidence range, no threshold rescues the judge and the primary endpoint stays deterministic.
