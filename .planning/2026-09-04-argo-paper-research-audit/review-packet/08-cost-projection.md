# 08 — Full-factorial and Fallback Cost Projection

Status: **resource-anchor inventory only; total envelope TBD; no spend authorized**  
Created: 2026-09-04T15:43:42+09:00

## Resource anchor identity

Manifest `resource-anchor-manifest.json`, SHA-256 `df749a08c67deea582399be79023ef35b392167b70968fbaf6394b2519502e13`, contains **53/53** paths and byte hashes
(5 pilots + 48 block receipts). These receipts are quarantined for efficacy but retain observed resource values.
Median anchor: $0.078, 170,859 tokens, 83.8s per legacy episode.
Observed maximum: $0.325709, 1,413,997 tokens, 281.9s.

| design | phase | tasks | cells | episodes | legacy median anchor | legacy observed-max anchor |
|---|---:|---:|---:|---:|---:|---:|
| FULL_8_CELL | development_excluded | 4 | 8 | 96 | $7.49 / 16,402,464 tok / 2.2 h | $31.27 / 135,743,712 tok / 7.5 h |
| FULL_8_CELL | confirmation_min | 12 | 8 | 288 | $22.46 / 49,207,392 tok / 6.7 h | $93.80 / 407,231,136 tok / 22.6 h |
| FULL_8_CELL | confirmation_max | 20 | 8 | 480 | $37.44 / 82,012,320 tok / 11.2 h | $156.34 / 678,718,560 tok / 37.6 h |
| FIVE_ARM_FALLBACK | development_excluded | 4 | 5 | 60 | $4.68 / 10,251,540 tok / 1.4 h | $19.54 / 84,839,820 tok / 4.7 h |
| FIVE_ARM_FALLBACK | confirmation_min | 12 | 5 | 180 | $14.04 / 30,754,620 tok / 4.2 h | $58.63 / 254,519,460 tok / 14.1 h |
| FIVE_ARM_FALLBACK | confirmation_max | 20 | 5 | 300 | $23.40 / 51,257,700 tok / 7.0 h | $97.71 / 424,199,100 tok / 23.5 h |

These figures are **not treatment-adjusted approval costs**. C1 creates exactly two independent candidates rather than
one. F1 permits one to three rounds rather than one. Their joint variable workload is structurally 2–6× a one-candidate
one-shot path before the identical per-cell hard cap truncates work. The 53 legacy receipts do not measure this workload.

## Complete stage envelope status

| stage | episodes | token/time/cost status |
|---|---:|---|
| Stage 0 measurement certification | 0 model episodes | dependency/image setup cost and time **TBD** |
| Stage R retrieval policy | TBD | task count, provider/version, query budget, tokens, time, cost **TBD** |
| Stage 1 development | 96 | G/C/F-adjusted upper envelope **TBD** |
| Stage 1 FULL confirmation | 288–480 | G/C/F-adjusted upper envelope **TBD** |
| Stage 2 L×P recovery factorial | 216–360 | legacy cost anchor $16.85–$28.08; observed-max anchor $70.35–$117.26; certified runtime **TBD** |
| contingency | — | 20% × all measured stage upper envelopes; **TBD** |
| **human approval total** | **TBD** | **BLOCKED** |

No paid episode is allowed until all TBD cells have measured ranges and the human approves the exact subtotal plus 20%
contingency. The historical $48.47 cap is not carried forward.

If FULL is unaffordable after the disjoint-pilot power simulation, the only fallback is FULL, -G, -C, -F, and G0C0F0.
It permits leave-one-mechanism-out removal statements only; no interaction or optimum claim.
