# Exa 추가 선행연구: 대조군·반례·평가 타당성

2026-09-08 · 내부 연구 갱신 · 신규 효능 실험 없음

## 추가 조사가 필요했던 이유와 실제 수행

Exa 연결 복구 다음에는 실제 문헌 확장이 필요했다. 직전 세 원문 검토만으로는 강한 tree 대조군, graph 유지의 부정적 결과, 실제 수행과 benchmark 점수의 관계를 충분히 비교하지 못했다.

복구한 Exa MCP로 **네 주제 검색을 실행해 31개 결과 레코드**를 회수하고, 기존 source receipt·metadata·claim locator 색인의 **154개 source ID**와 대조했다. 제목·버전·publisher 중복을 구분해 10개 후보를 선정했다. 그중 **새로 색인에서 확인하지 못했던 3편과 기존 EviGraph의 심화 재검토 1편**, 총 4편의 전체 추출 본문을 읽었다. Exa는 발견을, OpenResearch CLI는 지정 버전의 전체 본문 회수를 담당했다. 검색 스니펫은 상세 주장 근거로 사용하지 않았다.

이 세 편의 신규성은 이번에 감사한 색인에 없었다는 뜻이며, 과거 모든 대화나 다른 임시 파일에서 한 번도 언급되지 않았다는 뜻이 아니다. EviGraph v2는 기존 버전이고 이번에 새 버전을 찾은 것이 아니다. 공개 preprint와 동료심사 게재를 구분하며 이번 네 편을 확정 학회 게재 논문으로 표기하지 않는다.

## 원문으로 확인한 네 가지 판단

| 읽은 원문 | 확인된 내용 | 설계에 미치는 영향 |
|---|---|---|
| [Arbor: Tree Search as a Cognition Layer for Autonomous Agents](https://www.alphaxiv.org/abs/2606.12563) | tree가 공동 작업 상태이며 실패 진단·검증 조건·Critic 제약이 다음 탐색을 바꾼다. no-DFS 조건에는 단일 agent와 복구 경로 부재가 함께 들어간다. | tree를 단순 보관함으로 취급하지 않는다. 모든 조건의 기본 복구와 측정 유효성을 보장한다. 해당 ablation을 topology만의 인과효과로 읽지 않는다. |
| [EvoGraph-Mem](https://www.alphaxiv.org/abs/2608.11248) | 실패 피드백에 따라 insight를 보관·수정한다. GPT-4o-mini PDDL에서 보관 기능까지 포함한 조건은 34%, 전체 controller는 31%로 저자가 보고한다. | 더 복잡한 수정 기능을 기본 승자로 정하지 않는다. scope, 원본 보존, 수정 뒤 과거 근거의 재검증과 추가 비용을 확인한다. |
| [Life After Benchmark Saturation](https://www.alphaxiv.org/abs/2606.26158) | 정답 grade, 실제 계산, 사전 산출물에서 답을 읽는 경로, 반복성·비용을 별도로 조사한다. 자율 완료와 독립 검증된 정확성은 다르다. | 단일 최종 산출물의 독립 점수를 유지하며 생성 경로·총비용·반복성을 함께 해석한다. 정당한 부분 계산을 무조건 invalid로 처리하지 않는다. |
| [EviGraph](https://www.alphaxiv.org/abs/2608.04738) | typed evidence graph, 의미상 영향을 받는 후속 부분의 재생성, 유효 근거 보존·rollback, scoped negative claim이 이미 명세돼 있다. | 범위별 무효화·실패 보존·graph 기반 연구 제어 자체를 새 기여로 주장하지 않는다. 같은 근거·의무를 가진 강한 대조군 대비 실용적 증분이 남은 질문이다. |

각 주장은 `source-evidence.json`의 원문 SHA와 `reviews/`의 LF locator에 연결돼 있다. 보고된 숫자는 저자 결과이며 로컬 재현값·SOTA·효과크기 prior가 아니다.

### 이름과 논문을 구분

`2606.12563`은 AMD 연구진의 **Arbor: Tree Search as a Cognition Layer for Autonomous Agents**다. 기존 corpus의 `2606.11926`은 **Toward Generalist Autonomous Research via Hypothesis-Tree Refinement**다. 서로 다른 저자와 연구이므로 Arbor라는 이름으로 서지·코드·효과를 합치지 않는다. 후자는 이번에 metadata와 기존 원문 hash를 확인한 자료이며 이번 네 편의 완독 수에 포함하지 않는다. [두 번째 Arbor의 공식 식별자](https://www.alphaxiv.org/abs/2606.11926)

## 현재 B/C/G 설계에 반영할 내용

1. **공통 측정 검증과 연구 의무를 분리한다.** B/C/G 모두에 authority·budget·identity·측정 조건·최종 독립 채점의 동일한 경계를 둔다. B는 강한 근거 기반 tree/notebook과 advisory 연구 점검, C는 같은 정보·권리 위 compulsory applicability/revalidation/preservation, G는 같은 의무와 집행 강도 위 graph-mediated 제어다. G의 효과를 크게 보이게 하려고 B/C의 기본 검증이나 복구를 제거하지 않는다.
2. **최초 기제 주장을 줄이고 실증 질문을 구체화한다.** typed graph, scoped invalidation, 근거 기반 재개·복구는 선행 기제다. 질문은 동일 조건에서 G−C가 최종 hidden 성과와 비용에 추가 가치를 주는가다. 순수 topology 효과나 최초의 능동 연구 제어라는 주장은 하지 않는다.
3. **기억 수정은 근거를 자동 승계하지 않는다.** EvoGraph-Mem의 positive/negative 기록은 LLM이 task feedback을 해석한 효용 label이다. 독립 검증값이 아니다. 수정 문장이 옛 positive evidence를 계승할 수 있는지와 한 task의 실패로 다른 task에 유효한 지식까지 사라지는지를 확인할 필요가 있다.
4. **성공 선언·최종 점수·수행 증거·비용을 별도로 기록한다.** 기존 primary single-lock/hidden scoring을 유지한다. 누락 비용은 0으로 만들지 않고, 반복성이 높다는 이유만으로 정확하다고 하지 않는다. 근거 없는 전체 pipeline 강제도 하지 않는다.

이는 선행연구에서 도출한 설계 해석과 후속 specification 요구다. **현재 House Price P0의 동결된 명령·예산·평가 규칙·시작 승인, 실제 실행 상태를 변경하지 않는다.** 새 arm이나 추가 실제 학습도 시작하지 않았다.

## 과장하지 말아야 할 반례의 범위

EviGraph는 평가에서 시스템명 등을 가리고 입력을 정규화하는 절차, 숫자·분모 판정 규칙과 공통 비용 회계 정책을 서술한다. 이를 무조건 자기 채점 또는 비용 회계 부재라고 비판하지 않는다. 다만 실제 evaluator revision, 동일 total cap와 실측 전체 비용, 반복 분산을 이 읽기만으로 확보한 것은 아니다. component ablation은 결합된 구조라는 이유로 분리하지 않아 matched C/G의 증분을 대신 답하지 못한다. [EviGraph](https://www.alphaxiv.org/abs/2608.04738)

EvoGraph-Mem의 명시된 ADD/KEEP/ARCHIVE/REVISE만을 빈 graph에서 적용한다고 가정하면, negative feedback을 받은 노드가 비활성화되어 active 노드의 negative set은 계속 빌 수 있다. 그러면 negative penalty가 작동할 경로가 불명확하다. 이는 **명시된 수식에 대한 조건부 추론**이며 실제 구현 버그나 재현 실패가 아니다. 다른 초기화·재활성화 경로가 있으면 달라질 수 있다. 구현을 채택하기 전에 명세와 도달 가능한 상태를 확인할 항목으로 남긴다. [EvoGraph-Mem](https://www.alphaxiv.org/abs/2608.11248)

CORE-Bench 후속 연구의 targeted-fix/rewrite 비교는 관측적이고, 사후 최선 scaffold oracle은 실제 배포된 라우터가 아니다. scaffold별 timeout·retry·버전도 다르다. 따라서 그 숫자로 우리 정책의 예상 향상률을 정하지 않는다. 필요한 계산을 실제 수행한 정당한 부분 재현과 사전 정답 산출물을 읽는 shortcut을 구별하는 Table 8의 경계도 보존한다. [Life After Benchmark Saturation](https://www.alphaxiv.org/abs/2606.26158)

## 프로토타입에 연결할 좁은 후속 작업

| 후속 산출물 | 검증할 내용 | 결과가 설계를 바꾸는 방식 |
|---|---|---|
| 공통 baseline/관측 명세 | 모든 조건이 같은 원문·실패·복구·기본 측정 검증에 접근하는가 | 정보 부족으로 약해진 대조군을 제외하고 공정한 package 비교를 구성한다. |
| 변경·보관·재검증 사례 | 수정된 claim의 과거 근거, 한정된 실패의 적용 범위, 보존된 원본과 active 상태 | 불필요하거나 손실을 일으키는 수정 기능은 축소하고 측정된 기능만 구현에 넘긴다. |
| final-artifact 진단 기록 | 독립 score, 생성 lineage, 실패 포함 비용, 누락, 반복성과 task별 차이 | node 수나 agent 선언 대신 실제 과제 성과와 비용으로 prototype 구성을 선택한다. |

이 항목은 기존 연구→실험→논문→프로토타입 연쇄를 구체화한다. 새로운 일반 승인 체계나 모든 기능을 넣는 전체요인 실험을 추가하지 않는다. native construction과 manuscript writing의 기존 조건은 그대로다.

## 산출물과 탐색 중단 지점

- `source-evidence.json`: Exa 검색·선정·원문 버전·hash·읽기 범위 및 corpus delta.
- `reviews/`: 네 원문 검토와 기존 corpus 감사. discovery와 full read를 분리한다.
- `decision-update.json`: 이전 설계 기록을 덮어쓰지 않는 후속 해석.
- `context-graph.json`: 새 원문→반례/기제→후속 설계의 내부 연구 연결. native graph가 아니다.

이번 검색은 세 부족한 축에서 실제 대조군과 반례를 확보했으므로 추가 문구 변형 검색은 하지 않았다. 보유 후보 AIRA/AIRA2, Negative Knowledge, FIRE-Bench 등은 후속 질문이 생길 때 읽을 수 있게 남겼다. 이들의 검색 요약을 상세 주장으로 승격하지 않았다. 논문 전체의 선행연구 완결이나 SOTA 달성을 선언하는 단계는 아니다.
