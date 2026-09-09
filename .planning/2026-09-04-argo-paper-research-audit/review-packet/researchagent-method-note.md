# ResearchAgent Full-Read Method Note — Boundary for Factor C

Source: Baek et al., *ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models*, NAACL 2025 / arXiv:2404.07738.  
Read receipt: `researchagent-full-read-receipt.json` SHA-256 `7e45f3f07a47bb9748eb470a0611009151db0305756374a118ab7b6e313e89df`  
Locators: `researchagent-locators.json` SHA-256 `413248ac0e7c7aca60cde8a0f0b77dc96c06d3cbe374c0b6ca6924371e7e2acf`

## What transfers

ResearchAgent decomposes a research idea into problem, method, and experiment design
(`researchagent_idea_decomposition`), retrieves citation-linked papers and external entities
(`researchagent_citation_graph_survey`, `researchagent_entity_knowledge_store`), and uses ReviewingAgents to iteratively
revise the single generated proposal (`researchagent_iterative_reviewers`). These are prior art for staged design,
knowledge augmentation, and critique.

## What does not transfer

It does **not** independently generate two candidates. One ResearchAgent proposal is repeatedly revised after reviewer
feedback. It does not use a condition-blind deterministic ADMIT/REVISE/BLOCK predicate; open-ended ideas have no ground
truth and are evaluated with GPT-4 plus domain experts (`researchagent_no_ground_truth_evaluation`). Its knowledge
ablation removes references/entities rather than testing candidate competition (`researchagent_knowledge_ablation`).
Therefore it cannot establish efficacy of ARGO factor C.

## Consequence for C1

C1 must add and test three properties not supplied by this prior work:

1. two generators run in isolated fresh contexts and cannot observe each other;
2. both candidates freeze before any critic sees them;
3. a preregistered deterministic admission predicate selects or blocks, while preserving the rejected alternative.

A model critic may explain a defect but cannot override the predicate. Candidate independence is itself a manipulation
check, not a prompt assertion.

## Refinement and evaluation limits

ResearchAgent reports diminishing evaluation-score gains after three review iterations
(`researchagent_refinement_saturation`), but this is model/judge/task specific and does not validate ARGO's F cap. The
paper also states that 15 ReviewingAgents with five criteria per idea part may miss domain perspectives
(`researchagent_reviewer_scope_limit`). Human-induced criteria use ten annotated pairs per criterion
(`researchagent_human_induced_criteria`), so model-based agreement is a scoped calibration result, not a deterministic
scientific oracle.
