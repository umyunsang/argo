# EviGraph v2 원문 검토: 신규 자료가 아닌 읽기 깊이 확장

**판정:** EviGraph v2는 ARGO의 광범위한 graph·repair·gating 신규성을 더 좁힌다. 현재 B/C/G의 강한 대조군·동일 의무·동일 예산 비교는 유지할 연구 질문이지만, 그 비교가 끝나기 전에는 ARGO의 효능이나 신규성을 입증한 것으로 쓸 수 없다.

원문: [EviGraph: Evidence-Guided Autonomous Research Agents, arXiv v2](https://arxiv.org/abs/2608.04738v2). 제공된 `sources/2608.04738v2.txt`의 LF 1–2770 전체를 이번 세션에 읽었다. SHA-256: `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`. References·prompt·orchestration·evaluation appendix까지 포함한다. PDF 도표의 시각 검증, 코드 검증, 실행 재현은 하지 않았다. 기존 receipt부터 v2였고 locator 1개가 있었으므로 새 논문/새 버전 발견으로 세지 않는다. 세부 주장 15개의 LF 범위·사용 한계·읽기 기록은 `evigraph-review.json`에 있다. 이 자료는 arXiv preprint이며 학회 게재 확인으로 쓰지 않는다.

## 직접 겹치는 기제

| 기제 | 원문 LF | 연구 설계에 미치는 영향 |
|---|---|---|
| Problem→Gap→Hypothesis→Experiment→Finding→Claim의 typed operational graph; 여러 실험/근거가 한 claim을 지지하는 분기·병합 | 211–340 | 연구 과정을 typed graph로 연결하는 것만으로 신규성을 주장할 수 없다. |
| 가장 이른 weak root를 찾고 content-dependent descendants만 삭제·재생성; contextual reachability와 실제 content dependency를 구별 | 395–434, 1816–1857, 2035–2050 | 범위 무효화와 영향받는 부분만 고치는 제어도 직접 선행기제다. |
| staged atomic repair, 기록 기반 실행, 기존 valid-chain 보존, weak-root 수 기반 rollback; append-only graph/parent hash와 비용·execution reference | 2025–2034, 2112–2177 | checkpoint·provenance·실패 복구를 G의 고유 신규 기제로 둘 수 없다. |
| prior graph/성공 repair trace는 advisory로만 회수하고 현재 run의 finding/claim/value를 다시 검증 | 588–593, 2159–2177 | 과거 연구를 참조하되 현재 근거를 요구하는 절차도 이미 제안돼 있다. |
| negative result는 hypothesis를 반박한다는 이유로 weak로 취급하지 않으며 finding과 scoped negative claim을 보존 | 1755–1760 | 부정 결과 보존 자체는 신규성이 아니다. 조건·실패 유형·재사용 적합성의 별도 가설과 구별해야 한다. |
| schema·provenance·acyclicity 검증, 최소 1개 retained claim 및 required deliverables, provenance map 기반 writer/reviewer gate | 1092–1118, 1643–1653, 2180–2374 | 일반 검증 의무와 논문 생성 gate 역시 선행기제다. |

다만 문서에 적힌 제어 규약과 실제 실험에서 효과가 분리 검증됐다는 것은 다르다. 대표 사례는 최초 repair가 성공한 cold start여서 rollback과 long-term retrieval을 실제로 사용하지 않았다. 논문도 이를 명시한다(LF 934–955, 2715–2735).

## 결과와 비교의 정확한 범위

전체 시스템 비교는 AutoResearchClaw와 NanoResearch를 대상으로 하며, 25 ARC-Bench-ML task와 20 NanoResearch task를 쓴다. 공통 qwen-3.6-plus backbone, sandbox, per-experiment time budget을 명시한다(LF 599–649). CSR은 27%→37.85%로 **10.85%p 증가, 상대 40.19% 증가**다. EDC 87.73%는 NanoResearch의 96.15%보다 낮고 alignment도 NanoResearch보다 낮다. 모든 지표 최고로 기술하면 안 된다(LF 655–702).

저자들은 component coupling을 이유로 일반적인 component ablation 대신 qualitative mapping과 사례를 제시한다(LF 703–736). 따라서 aggregate 차이에서 graph topology, hypothesis filtering, repair, writer gate, rollback, memory 각각의 효과를 분리할 수 없다. 이는 논문이 효과가 없다는 증거도, 두 대조군이 본질적으로 약하다는 판정도 아니다. ARGO에서 필요한 strong persistent tree/notebook, 동일 정보·의무·집행 강도의 직접 비교가 이 논문에 제시되지 않았다는 한계다.

예산도 공정하게 읽어야 한다. Appendix는 planning/model/tool/retry 비용을 모든 시스템에 같은 정책으로 계산한다고 명시한다(LF 2060–2072). “비용 회계가 없다”는 비판은 틀리다. 그러나 실제 total cap·소비량·반복 수·seed·hardware 등의 값은 run manifest로 보완하도록 되어 있고, 이번에 읽은 본문만으로 그 값이 확인되지는 않는다(LF 2388–2395, 2478–2494). Point estimate를 지역 실험의 효과크기나 power prior로 옮기지 않는다.

## 평가 독립성: 이미 있는 장치와 남은 확인

Reliability protocol은 system identity/field name을 가리고, 각 시스템의 artifact를 같은 record class로 정규화하며, bare graph support label을 근거로 인정하지 않는다. Extraction 설정·숫자 matching rule을 사전 고정하고 occurrence-based denominator를 유지한다(LF 2396–2422, 2570–2618). 따라서 이 평가를 unblinded 또는 graph의 자기선언만 검사하는 평가라고 비판하면 안 된다.

Claim/value extraction과 supported/match 판정은 LLM-mediated다. Native ARC score에는 두 independent agent reviewer가 있지만, 이것이 모든 reliability 판단의 독립 인간 검증이나 다른 모델 검증을 뜻하지 않는다(LF 1062–1075, 2375–2387, 2619–2714). 실제 evaluator/extractor revision, human calibration, agreement, manifest, uncertainty interval은 이번 본문 검토로 확인되지 않았다. Raw counts를 aggregate와 함께 내도록 규약은 정하지만 Table 4 자체에는 ratio만 있다. 외부 artifact가 없다고 단정하지 않는다.

내부 readiness는 retained current-run graph claim을 대상으로 하고 CSR은 prior-work·method·implicit proposition 등을 포함한 manuscript 추출 claim을 대상으로 한다(LF 565–577, 634–649, 2434–2445). CSR 37.85%가 readiness 정의와 즉시 논리 모순이라고 쓸 수 없다. 서로 다른 claim population과 evaluator 오류를 구별하는 검증이 필요하다.

## 현재 B/C/G에 남는 연구 질문

기준은 `paper/research/autonomous-thesis-to-prototype-20260908/README.md` §4와 `decision-record.json`이다. B는 강한 persistent source-backed tree/notebook과 advisory 연구 점검을 갖고, C는 같은 정보·권리 아래 점검을 의무화한다. G는 C와 같은 의무·집행 강도에서 graph-mediated dependency traversal·범위 무효화·continuation을 제공한다. 모든 조건의 공통 safety/authority/measurement 규칙은 유지한다.

- **C−B:** 의무 절차의 효과와 비용. 검증·복구·근거 접근을 B에서 제거하여 유리한 비교를 만들지 않는다.
- **G−C:** graph-control package의 추가 가치. 순수 topology 효과나 위 표 기제의 발명으로 해석하지 않는다.
- **검증할 residual:** 강한 비graph 대조군의 자체 dependency check도 허용한 상태에서, 사전 선택한 단일 final artifact의 독립 hidden 성과와 전체 비용을 비교한다. 대조군에 없는 근거·복구·scheduler·writer 품질을 G에만 추가하지 않는다.

실제 연구 기여의 후보는 이 조건을 만족하는 비교 결과와 적용 범위다. EviGraph보다 좋다는 주장, graph의 본질적 우위, 성공 프로토타입은 아직 관측되지 않았다. 현재 P0는 C0 feasibility이며 이 리뷰는 동결 실험·정본 원고·native 구현을 바꾸지 않는다.
