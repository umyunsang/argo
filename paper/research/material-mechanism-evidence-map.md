# 7개 재료 · 기제 · 계획서 5축 · 아암 · 증거 대응표 (Material-Mechanism-Evidence Map)

작성 시각: 2026-09-04T12:35:00+09:00
권한: supervisor instruction-0020 §4 & instruction-0022 §2 (졸업논문 계획서 5축 프레임 반영)

본 문서는 최종 제출된 졸업논문 계획서(`졸업논문_계획서_엄윤상.pdf`, 방법 1항)의 5대 도출 축(행동·기억·구조·설계·검증)과
논문의 7대 핵심 하네스 재료, 선행 참고문헌, 실험 아암 배치, 관측 증거 및 최종 프로토타입 설계를 1:1로 대응시킨다.
선행 문헌이나 실험 영수증 어느 것으로도 정당화되지 않는 항목은 **"근거 없는 기본값(unjustified default)"**으로 표기한다.

---

## 5대 축 · 재료 · 기제 · 아암 · 관측 증거 · 프로토타입 설계 결정 매트릭스

| 계획서 도출 축 | 재료 (Material) | 기제 노드 (Mechanism ID) | 핵심 참고문헌 및 선행 근거 (정독 출처 및 Locator) | 본 실험 아암 배치 및 분리 한계 | 본 실험 관측 증거 (Receipts) | 최종 프로토타입 설계 결정 (Design Decision) |
|---|---|---|---|---|---|---|
| **행동 (Action)** | **1. 최소 도구 쉘·파일 하네스** | `mechanism:minimal_tool_coding_harness` | **[1] SWE-agent** [@yang2024sweagent], **[2] CodeAct** [@wang2024executable], [@primeagent2026] (loc: `primeagent_harness_architecture`) | **B0 아암에 단독 분리** (clean single difference) | T3: 0.79±0.2036, 만점 21/40; T1' 파일럿: B0 실측 $0.0450 | **채택 (Adopted)**: 모든 에이전트의 불변 기초 실행 환경으로 배치 |
| **행동 (Action)** | **2. 영속 REPL 및 실행 상태** | `mechanism:persistent_repl_recursive_harness` | **[2] CodeAct** [@wang2024executable], [@autoresearchfail2026] (loc: `autoresearch_run_limits`) | **B1 아암에 단독 분리** (B0 대비 REPL 추가) | T3: 0.88±0.1788, 만점 28/40, B1-B0 p=0.0803 (비유의) | **조건부 채택 (Conditional)**: 긴 호흡의 상태 추적에 유익하나 단독 분산 축소는 통계적 미검출 |
| **기억 (Memory)** | **3. 타입드 연구 문맥 그래프** | `mechanism:typed_research_context_graph` | **[3] A-Mem** [@xu2025amem], [@evidenceledger2026] (loc: `evidenceledger_provenance_audit`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `graph_nodes_added` 평균 4.55회 (1~7 범위 변동) | **조건부 채택 (Conditional)**: 감사 가능성 담보의 척추이나 인과적 단독 기여는 관찰적 상관에 한정 |
| **구조 (Structure)** | **4. 그래프 엔지니어링** | `mechanism:graph_engineering` | **[4] Graph of Thoughts** [@besta2024graph], [@graphengineering2026] (loc: `graphengineering_context_nodes`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `graph_nodes_added` 및 엔티티 타입 강제 | **조건부 채택 (Conditional)**: 정적 무결성 검증에는 필수이나 동적 성능 기여는 미분리 |
| **검증 (Verification)** | **5. 결정 프로토콜 및 청구 잠금** | `mechanism:failclosed_research_lifecycle` | **[6] Self-Authored Verification** [@guo2026selfauthored], [@verificationcost2026] (loc: `verificationcost_gate_ratio`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 `decisions_recorded` 평균 1.68회, `gate_blocks` 평균 0.23회 | **채택 (Adopted)**: 시스템의 자가 오류 4건을 실제로 적발한 감사 가능성 1차 기여의 핵심 |
| **설계 (Design)** | **6. 반증 루프 및 피벗** | `mechanism:loop_engineering` | **[5] ADAS** [@hu2025automated], [@baitbench2026] (loc: `baitbench_adversarial_detection`) | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | **B2 40편 실측 pivots = 0 (미발화 결함)** | **보류 (Deferred)**: 구현은 정상이나 과제 난이도 미달로 실측 검증 부재, T1' 확증 블록 결과까지 판정 유예 |
| **(계획서 5축 밖 추가 구성요소)** | **7. 결과 주도 동적 검색** | `mechanism:result_driven_semantic_search` | **계획서 5축 밖 추가 구성요소**; 선행 채택 근거: Adaptive-RAG [@adaptive2024] & Self-RAG [@selfrag2023] | **B2 아암에 복합 묶임** (독립 절제 미승인 한계) | B2 내 동적 도구 세트 호출 관측 | **근거 없는 기본값 (Unjustified Default)**: 실험 데이터상 단독 효과가 분리되지 않았으며 선행 문헌 규격으로만 탑재 |

---

## 계획서 5축 및 추가 구성요소 명세

1. **행동 (Action) 축:** SWE-agent[1]와 CodeAct[2]의 연구는 에이전트 인터페이스가 LLM 성능을 크게 좌우함을 보였다. 본 연구는 쉘 기반 최소 도구(`minimal_tool_coding_harness`, B0)와 영속 REPL(`persistent_repl_recursive_harness`, B1)로 구현하여 통제된 단일 차이로 분리 검증하였다.
2. **기억 (Memory) 축:** A-Mem[3]은 에이전트 기억의 구조화 필요성을 입증했다. 본 연구는 연구 전주기의 아티팩트와 주장을 방향성 그래프로 엮는 타입드 문맥 그래프(`typed_research_context_graph`)로 구체화하였다.
3. **구조 (Structure) 축:** Graph of Thoughts[4]는 선형 체인을 넘어선 비순환 그래프 기반 조율을 제안했다. 본 연구는 노드 타입과 스키마 유효성을 강제하는 그래프 엔지니어링(`graph_engineering`)으로 승계하였다.
4. **검증 (Verification) 축:** Self-Authored Verification(Guo et al., 2026)[6]은 에이전트가 스스로 검증기를 작성할 때 자기기만과 휴리스틱 편향이 발생함을 밝혔다. 본 연구는 이에 대응하여 외부에서 주입되는 페일클로즈드 수명주기 게이트(`failclosed_research_lifecycle`)를 설계하였다.
5. **설계 (Design) 축:** ADAS[5]는 에이전트 아키텍처의 자동 탐색을 제안했다. 본 연구는 반증 피벗 기제(`loop_engineering`)를 B2에 탑재함과 동시에, 자동 탐색(AutoML)과 대비되는 사전등록 절제 연구의 비교 우위를 Ⅴ장에서 논증한다.
6. **계획서 5축 밖 추가 구성요소 (결과 주도 동적 검색):** 계획서의 5축 도출 프레임에 직접 포함되지 않는 추가 기능으로, 과제 복잡도에 따라 검색을 적응적으로 호출하는 선행 연구(Adaptive-RAG, Self-RAG)에 근거하여 탑재되었다. 그러나 본 실험에서 단독 기여가 분리 검증되지 않았으므로 **"근거 없는 기본값"**으로 투명하게 표기한다.
