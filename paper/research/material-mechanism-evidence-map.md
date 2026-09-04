# 7개 재료 · 기제 · 아암 · 증거 대응표 (Material-Mechanism-Evidence Map)

작성 시각: 2026-09-04T12:15:00+09:00
권한: supervisor instruction-0020 §4 (논문의 구조적 척추이자 프로토타입 설계 지침 근거)

본 문서는 논문에서 다루는 7개 핵심 하네스 재료가 어떤 기제로 구현되고, 선행 문헌의 어떤 근거에 기반하며,
본 벤치마크 실험 아암에서 어떻게 배치되고 관측되었는지를 투명하게 대조한다.
선행 문헌이나 실험 영수증 어느 것으로도 정당화되지 않는 항목은 **"근거 없는 기본값(unjustified default)"**으로 표기한다.

---

## 재료 · 기제 · 아암 · 관측 증거 · 프로토타입 설계 결정 매트릭스

| 재료 (Material) | 기제 노드 (Mechanism ID) | 선행 문헌 근거 (정독 출처 및 Locator) | 본 실험 아암 배치 및 분리 한계 | 본 실험 관측 증거 (Receipts) | 최종 프로토타입 설계 결정 (Design Decision) |
|---|---|---|---|---|---|
| **1. 최소 도구 쉘·파일 하네스** | `mechanism:minimal_tool_coding_harness` | [@primeagent2026], [@solutionhacking2026] (loc: `primeagent_harness_architecture`, `solutionhacking_prompt_leakage`) | **B0 아암에 단독 분리** (clean single difference) | T3: 0.79±0.2036, 만점 21/40; T1' 파일럿: B0 3건 실측 | **채택 (Adopted)**: 모든 에이전트의 불변 기초 실행 환경으로 배치 |
| **2. 영속 REPL 및 실행 상태** | `mechanism:persistent_repl_recursive_harness` | [@autoresearchfail2026], [@multiplerunsorder2026] (loc: `autoresearch_run_limits`, `multipleruns_order_effects`) | **B1 아암에 단독 분리** (B0 대비 REPL 추가) | T3: 0.88±0.1788, 만점 28/40, B1-B0 p=0.0803 (비유의) | **조건부 채택 (Conditional)**: 긴 호흡의 상태 추적에 유익하나 단독 분산 축소는 통계적 미검출 |
| **3. 타입드 연구 문맥 그래프** | `mechanism:typed_research_context_graph` | [@graphengineering2026], [@evidenceledger2026] (loc: `graphengineering_context_nodes`, `evidenceledger_provenance_audit`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `graph_nodes_added` 평균 4.55회 (1~7 범위 변동) | **조건부 채택 (Conditional)**: 감사 가능성 담보의 척추이나 인과적 단독 기여는 관찰적 상관에 한정 |
| **4. 그래프 엔지니어링** | `mechanism:graph_engineering` | [@graphengineering2026], [@claimreplay2026] (loc: `graphengineering_graph_ops`, `claimreplay_deterministic_audit`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `graph_nodes_added` 및 엔티티 타입 강제 | **조건부 채택 (Conditional)**: 정적 무결성 검증에는 필수이나 동적 성능 기여는 미분리 |
| **5. 결정 프로토콜 및 청구 잠금** | `mechanism:failclosed_research_lifecycle` | [@verificationcost2026], [@tokenaccounting2026] (loc: `verificationcost_gate_ratio`, `tokenaccounting_audit_ledger`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `decisions_recorded` 평균 1.68회, `gate_blocks` 평균 0.23회 | **채택 (Adopted)**: 시스템의 자가 오류 4건을 실제로 적발한 감사 가능성 1차 기여의 핵심 |
| **6. 결과 주도 동적 검색** | `mechanism:result_driven_semantic_search` | [@adaptive2024], [@budgetmatched2026] (loc: `adaptiverag_routing_complexity`, `budgetmatched_cost_control`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 동적 도구 세트 호출 관측 | **근거 없는 기본값 (Unjustified Default)**: 실험 데이터상 단독 효과가 분리되지 않았으며 선행 문헌 규격으로만 탑재 |
| **7. 반증 루프 및 피벗** | `mechanism:loop_engineering` | [@selfrefine2023], [@baitbench2026] (loc: `selfrefine_feedback_loop`, `baitbench_adversarial_detection`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | **B2 40편 실측 pivots = 0 (미발화 결함)** | **보류 (Deferred)**: 구현은 정상이나 과제 난이도 미달로 실측 검증 부재, T1' 확증 블록 결과까지 판정 유예 |

---

## 설계 결론 요약
- **완전 채택 (Adopted):** 2개 (최소 도구 하네스, 페일클로즈드 결정/감사 라이프사이클)
- **조건부 채택 (Conditional):** 3개 (영속 REPL, 타입 문맥 그래프, 그래프 엔지니어링)
- **보류 (Deferred):** 1개 (반증 루프 — 실측 미발화로 성능 기여 유보)
- **근거 없는 기본값 (Unjustified Default):** 1개 (결과 주도 동적 검색 — 분리 증거 부재)
