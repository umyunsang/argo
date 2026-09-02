# Research state (filled)

decision_id: K5-unlearning-stress-audit-2026

question: 
  Does a purported unlearning procedure produce genuine knowledge removal, or does it merely suppress observable output while preserving hidden access to the targeted knowledge?

alternatives:
  - Alternative 1 (REJECTED): Rely solely on direct querying. If the model refuses or gives null responses to direct questions about the target, assume removal is complete. REJECTED because: the shortcut audit evidence (2607.18508) demonstrates that simple content-blind probes can replicate behavior of full-capability judges; a model could similarly suppress direct access while preserving latent knowledge accessible via extraction or adversarial methods.
  
  - Alternative 2 (REJECTED): Apply unlearning once and accept vendor claims about coverage. REJECTED because: multiple unlearning procedures exist (RFU, SISA, task vectors, etc.) with different assumptions about what "removal" means; without comparing them and testing which knowledge forms they actually affect, we cannot distinguish robust removal from partial suppression.

sampling_frame:
  Population: Language models claimed to have undergone unlearning of a target knowledge domain (e.g., copyrighted works, private information, harmful capabilities). Specifically, we sample from the set of publicly available model variants and documented unlearning artifacts.
  
  Unit of analysis: A single (model, knowledge_form, test_procedure) triplet. Knowledge forms include: (a) factual recall, (b) derived reasoning over facts, (c) latent representation access, (d) in-context retrieval. Test procedures include: (i) direct natural queries, (ii) adversarial/jailbreak prompts, (iii) logit probe access, (iv) generation-based extraction via few-shot examples.
  
  Scope: Accessible via public APIs or released model weights; queries cost-bounded to <$500 per model under test.

evidence_used:
  - 2607.18508.txt: "Style over Substance: A Shortcut Audit" demonstrates that content-blind probes (simple statistical patterns from text features) perform on par with full multimodal judges (65.8% vs 66.8% WAF). This proves that observable behavior can be replicated without the intended mechanism—directly applicable to unlearning where removal (Observable) may differ from knowledge presence (latent). Evidence supports the need for multiple test procedures beyond direct queries.
  - 2608.29517.txt: "LLM Judges as Raters" shows that multiple judges (LLM versions, providers) differ systematically in severity despite correlating equally with a criterion. Implication: when comparing unlearning procedures, we cannot rely on a single evaluation signal; we need a battery of rater effects (severity, consistency, cross-procedure agreement).
  
  Could not verify: Whether the vendor-claimed target knowledge was fully identified before unlearning (scope specification is often opaque). Assumption: we accept stated targets and test them empirically.

falsifier:
  The design is refuted if: across all test procedures (direct queries, adversarial prompts, logit probes, extraction via few-shot), no statistically significant difference is detected between an unlearned model and a control (base model or differently-unlearned variant) on any knowledge form. This would suggest the unlearning procedure had no measurable effect—opposite of the intended finding.

stopping_rule:
  Stop when: (1) at least two independent unlearning procedures have each been tested on at least three knowledge forms with at least four test procedures per form (2 direct + 2 indirect), AND (2) sufficient samples have been collected to detect a 15-percentage-point difference in knowledge recovery (target power = 0.80, two-tailed α = 0.05), AND (3) the leading model in any comparison has been tested for internal consistency (repeated queries to the same model instance yield stable results within 5 percentage points).
