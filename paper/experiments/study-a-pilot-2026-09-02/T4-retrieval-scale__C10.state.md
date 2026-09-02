# Research state (fill every field before writing the design)

decision_id: T4-retr-eval-scaling-2025

question: Should retrieval+reranking performance be evaluated using fixed-cost metrics (e.g., MRR, NDCG@10) or resource-aware metrics (e.g., cost per relevant retrieved) as corpus size grows?

alternatives:
  - Alternative 1 (rejected): Use only rank-based metrics (MRR, NDCG@10) independent of corpus size. Rationale for rejection: These metrics ignore computational cost (latency, index size, throughput), which vary with corpus size. For production use, a system that maintains NDCG@10 while 10x index cost is not equally valuable. This design risks optimizing for a metric that diverges from actual deployment value.
  - Alternative 2 (rejected): Measure full end-to-end latency on production infrastructure at each corpus size. Rationale for rejection: Production infrastructure is not available in the constraint set; building one would violate the scope. Latency measurement requires multiple system components (ranking service, persistence layer, etc.) beyond the retrieval pipeline itself. This trades measurement precision for infeasibility.
  
sampling_frame: Population = scientific questions with publicly available relevance labels (SQuAD-Open, MS MARCO, Natural Questions subsets, BEIR benchmarks). Unit = (question, corpus_size, embedding_model, sparse_index) tuples. We sample across corpus sizes {10K, 50K, 100K, 500K} documents and measure rank and cost metrics on the same question set across all sizes.

evidence_used:
  - Relied on: BEIR benchmark suite structure and published QA corpus sizes (MS MARCO is ~8.8M documents, Natural Questions ~5M source Wikipedia articles). This confirms that sampling at 10K-500K is in a realistic operating range for scientific QA systems.
  - Relied on: Published comparisons of retrieval metrics (Thakur et al. 2021, Formal et al. 2022) showing NDCG@10 and MRR as standard evaluation metrics in dense+sparse retrieval.
  - Could not verify: Exact computational cost (latency, memory per index) for the specific embedding model and sparse index without running experiments. Design assumes linear or near-linear cost growth; actual sublinearity (e.g., from caching) is unknown.
  - Could not verify: Whether labels in target QA corpora remain valid across corpus sizes (e.g., if relevance changes when document pool expands). Design assumes labels remain stable; this is an assumption to flag.

falsifier: If rank-based metrics (NDCG@10, MRR) remain constant or improve across corpus sizes while resource cost grows superlinearly (e.g., latency or index size grows >2x per 5x corpus growth), then rank-based metrics alone are insufficient and the design's premise (that resource-aware metrics are needed) is confirmed. Conversely, if resource cost remains sublinear (e.g., constant per-query latency via caching/batching), rank-based metrics may be sufficient and resource-aware metrics add no value.

stopping_rule: Stop data collection when (1) all four corpus sizes {10K, 50K, 100K, 500K} have been evaluated on at least two question subsets with ≥100 questions each, and (2) rank-based metrics (NDCG@10, MRR, Recall@100) have stabilized (coefficient of variation <5% across subsets), indicating measurement is robust. If resource cost grows >2x superlinearly (e.g., index memory >2x per 5x corpus growth), stop and flag for deeper investigation.
