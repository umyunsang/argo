# Research state (fill every field before writing the design)

decision_id: K3-rubric-shift-agreement-test

question: 
Does editing a rubric change the agreement between human raters and an automatic rater (a real effect), or does it only change measurement noise (no true effect)?

alternatives:
1. REJECTED—Use a single rater panel with pre/post design. Reason: cannot separate within-rater drift and fatigue from rubric effect; confounds historical order with rubric variant.
2. REJECTED—Compare agreement by subsampling humans randomly after rubric change. Reason: loses power if sample is small, and introduces selection bias if humans self-select which rubric variant to use.

sampling_frame: 
All items scored under both rubric variants; human raters sampled from an existing fixed pool. The unit of comparison is (item, human-rater, automatic-rater) triples, nested within rubric variant. The population is the set of all items that could be scored under either rubric variant using the available automatic rater and human pool.

evidence_used:
- Assumption: the automatic rater's output is stable and deterministic across runs on the same item.
- Assumption: human raters can reliably apply both rubric variants without systematic forgetting or cross-contamination.
- Could not verify: the extent to which humans have pre-existing familiarity with either rubric variant, which could bias agreement scores.
- Could not verify: whether the automatic rater was trained on data that overlaps with the items being scored.

falsifier:
If the automatic rater shows systematically higher or lower agreement with humans under both rubric variants (i.e., the agreement rank-order is the same but magnitudes differ), and that difference can be entirely explained by noise (e.g., variance in human rating behavior), then the design's premise—that rubric change has a detectable effect on agreement—is refuted.

stopping_rule:
Stop collecting ratings when one of the following holds:
(1) All items available in the pool have been rated by all sampled humans under both variants.
(2) The posterior credible interval for the difference in agreement (variant A vs variant B) excludes zero with 95% confidence and we have at least 30 item–rater pairs per variant.
(3) We have collected 100 item–rater–variant observations and the posterior includes zero; we declare no detectable difference.
