# PaperQA2 Full-Read Method Note — Stage R Metrics and Reproducibility Boundary

Source: Skarlinski et al., *Language agents achieve superhuman synthesis of scientific knowledge*, arXiv:2409.13740.  
Read receipt: `paperqa2-full-read-receipt.json` SHA-256 `11500d79278f301c7f20a7186a36dcd8f5783c441e3dff0c058c491adbdc7b3c`  
Locators: `paperqa2-locators.json` SHA-256 `918d2bcd6dcb7d880fd704adee430ee2be696932d031603419e7499e462a9861`

## Metric decomposition that transfers

LitQA2 separates precision (correct among answered), accuracy (correct over all questions), DOI attribution recall, and
explicit abstention (`paperqa2_litqa_metrics`). PaperQA2 further exposes recall after search, top-k ranking, RCS, and
final attribution (`paperqa2_pipeline_recall_stages`). Stage R therefore reports answer correctness and each retrieval
stage separately; final answer quality cannot stand in for retrieval recall.

Citation support is also local: blinded experts judge whether a statement is cited and supported by its cited source,
uncited, or cited but unsupported (`paperqa2_citation_support_labels`, `paperqa2_blinded_citation_grading`). This maps to
ARGO citation precision and unsupported-claim rate without asserting global truth.

## Selection consequence

Context depth can trade precision against accuracy, citation traversal can improve DOI recall without a clearly
significant accuracy gain, and small RCS models can underperform no RCS (`paperqa2_precision_accuracy_tradeoff`). Stage R
must not maximize recall alone. Eligibility protects citation precision and unsupported-claim rate; selection then uses
the lower confidence bound of answer accuracy, with recall as a tie-break.

## Split and leakage consequence

The paper added 101 questions after most engineering changes to compare against the original 147
(`paperqa2_new_question_split`), while its supplement also reports that public indexing contaminated a later human
comparison (`paperqa2_question_construction_and_leak`). ARGO freezes development and evaluation literature tasks before
policy outcomes and never reuses indexed answers as a held-out claim.

## Non-transfer and provenance boundary

The public package does not include all full-text search, citation traversal, or bespoke server infrastructure used for
the reported experiments (`paperqa2_open_source_infrastructure_gap`). Model, tool list, top-k, parser, chunking, overlap,
and temperatures are treatment-relevant configuration fields (`paperqa2_tool_config_surface`). Therefore PaperQA2 is a
method/evaluation anchor, not evidence that a local adapter improves science. Stage R must pin the actual corpus,
provider, index, and runner bytes it evaluates.
