# W3C PROV and RO-Crate Read Note — Boundary for Factor G

Read receipt: `provenance-standards-read-receipt.json` SHA-256 `0ea6b79e1990d2e3ba411abba3ceb707c1a52291b20f73dce563e1a215c0be2b`  
Locators: `provenance-standards-locators.json` SHA-256 `8cd4d105c44333755d0054517acd64e4a84108154b973e95cdfadaf765131ca5`

## Interchange mapping

W3C PROV supplies a domain-agnostic vocabulary:

| ARGO object | PROV mapping |
|---|---|
| protocol, source span, code snapshot, environment manifest, artifact, result | `Entity` |
| retrieval, admission, execution, scoring, research refine, engine refine | `Activity` |
| human, model/API revision, runner, verifier | `Agent` |
| input used by a run | `used` / Usage |
| artifact produced by a run | `wasGeneratedBy` / Generation |
| corrected or refined immutable successor | `wasDerivedFrom` / Derivation |
| actor responsibility | `wasAssociatedWith` / Association |
| named evidence graph snapshot | PROV Bundle, itself an Entity |

The mapping follows `prov_dm_scope`, `prov_dm_entity_activity`, `prov_dm_derivation`, and
`prov_dm_bundle_provenance`. PROV-O supplies an OWL2 encoding (`prov_o_owl_encoding`).

## Packaging mapping

RO-Crate provides the external package, not the internal decision logic. A self-described root JSON-LD graph lists data
and contextual entities (`rocrate_self_described_root`, `rocrate_flat_graph_identifiers`). A profile can require ARGO's
protocol, task, environment, run, artifact and source-span fields. Detailed execution provenance remains a separate
PROV bundle referenced as a crate data entity (`rocrate_profiles_and_prov_coexist`,
`rocrate_workflow_run_boundary`). Transport checksums remain a separate integrity layer
(`rocrate_separation_of_concerns`).

## Non-novelty and non-efficacy boundary

ARGO does not invent Entity/Activity/Agent, provenance bundles, JSON-LD research packages, or workflow-run packaging.
Its testable G mechanism is narrower: immutable typed evidence/experiment lineage, explicit support/contradiction and
separate research/engine lineage under fail-closed admissibility rules. PROV/RO-Crate do not determine whether a claim is
scientifically supported, whether an experiment is causally valid, or whether G improves outcomes.

## Design consequence

Internally keep the richer causal/admissibility graph. Export a versioned RO-Crate profile containing a PROV bundle and
byte hashes. Do not make the exchange format the experiment treatment itself. Profile validation and content
admissibility are separate gates. Because reproducibility levels and dependency decay remain distinct
(`rocrate_reexecution_limits`), a valid crate is not proof of a successful clean rerun.
