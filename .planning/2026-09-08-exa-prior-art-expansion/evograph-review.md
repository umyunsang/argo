# EvoGraph-Mem 원문 검토

검토일: 2026-09-08. 범위: root가 Exa로 선정한 단일 원문의 전체 추출 본문 검토. 추가 검색·코드 검토·실험·native 변경 없음.

## 출처와 읽기 범위

- 논문: Yuxi Qian, Yuxiang Ren, *EvoGraph-Mem: Failure-Aware Editable Graph Memory for Long-Term Language Agents*.
- 원문 식별자: `arXiv:2608.11248v1`; 원문에 표시된 날짜는 2026-08-03. https://arxiv.org/abs/2608.11248v1
- 상태: 공개 preprint. 제공 원문에 동료심사 게재지 표시를 확인하지 못했으며 별도 출판 여부 조회를 수행하지 않았다. 학회 게재 논문으로 승격하지 않는다.
- 검토 파일: `sources/2608.11248v1.txt`.
- SHA-256: `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
- LF: 1,231. 전체 읽기 범위: 1–420, 421–840, 841–1231. 본문·References·Appendix A 포함. 이후 주요 구간에 줄 번호를 붙여 재확인했다.
- `FULL_EXTRACTED_TEXT_READ`; PDF 이미지·도형 자체는 검토하지 않았다. Figure 3에 관한 아래 수치는 도형 판독이 아니라 §4.3의 명시적 문장 근거다.

## 기제와 피드백의 실제 의미

기본 구조는 G-Memory의 query/interaction/insight 계층이다. 새 query의 embedding 유사도 검색 후 이웃 query를 확장하며, insight는 query에 의해 매개되는 관계로 연결된다 (§3.1). 수정 대상은 LLM 가중치가 아닌 외부 insight memory다 [EG-01, EG-02].

insight의 구성은 `(text, positive-query set, negative-query set, active flag)`다. active insight 중 현재 검색된 query subgraph와 positive support가 겹치는 것을 후보로 삼고, `positive-overlap count − λ × negative-overlap count`로 top-B를 정한다 [EG-03]. 여기서 positive/negative evidence는 논문 원문·독립 실험 근거의 진실값이 아니라 해당 insight를 적용한 과거 task query의 효용 귀속이다.

task 종료 후 prompt-constrained LLM이 query, trajectory, final task feedback, retrieved insights를 받아 KEEP/ARCHIVE/REVISE 및 별도 ADD를 결정한다. KEEP은 positive query를 추가한다. ARCHIVE는 negative query를 추가하면서 전체 노드를 비활성화한다. REVISE는 구 노드를 archive하고, 과거 positive set과 현재 query를 계승하되 negative set이 빈 새 노드를 만든다. ADD도 현재 query를 첫 positive evidence로 넣는다. Appendix A는 현재 task 정보만 사용하며 일반화 가능한 insight만 만들도록 지시한다 [EG-04–EG-06].

따라서 positive/negative는 **LLM controller 판단으로 생성되는 task-feedback 기반 label**이며 독립적인 causal attribution이 아니다. task feedback의 구체 oracle, 제공 형식, 판정 오류율, feedback을 모든 baseline에 동일하게 제공했는지는 본문에 충분히 명시되지 않았다. edge 생성은 `Ψ = Resolved`에 제한되지만 ADD/REVISE의 positive 삽입 식에는 같은 성공 조건이 없다 [EG-06].

## 중요한 수식상 미명세: active-negative 경로

다음은 저자 주장이나 구현 버그 확인이 아니라 **명시된 연산들에 대한 조건부 추론**이다 [EG-07].

1. 빈 그래프에서 시작한다고 가정하면 ADD는 negative set이 빈 active 노드만 만든다.
2. KEEP은 기존 negative set을 바꾸지 않는다.
3. negative query를 추가하는 ARCHIVE/REVISE는 동시에 구 노드를 inactive로 바꾼다.
4. REVISE의 새 active 노드는 negative set을 다시 비운다.
5. retrieval은 active 노드만 고려한다.

이 연산만 사용하면 active 노드의 negative set은 계속 비어 있어 conflict penalty가 0에 머물 수 있다. 별도 초기화·reactivation·active-negative 삽입이 존재한다면 달라질 수 있지만 그 경로가 제공 본문에 명세되어 있지 않다. 따라서 negative-aware scoring을 검증된 핵심 성능 원인으로 인용하거나 그대로 도입할 수 없다. 후속 재현에서는 reachable state와 실제 `c > 0` retrieval 빈도를 확인해야 한다. 이번 검토에서는 코드나 실험으로 확인하지 않았다.

REVISE가 기존 positive set을 새 문장에 그대로 넘기는 것도 재검증이 끝났다는 증거는 아니다. ARCHIVE는 현 query에서의 부정 판단으로 전체 노드를 검색에서 제외하므로 task-scoped invalidation과 동일하지 않다. retained edges는 감사 추적을 지원하지만 별도의 version relation이나 종속 결과에 대한 무효화 전파를 구현했다는 근거는 아니다 [EG-05–EG-07].

## 실제 평가와 비교의 한계

| 항목 | 원문에서 확인한 것 | 사용 한계 |
|---|---|---|
| population | PDDL의 Gripper/Barman/Blocksworld/Tyreworld, HotpotQA, FEVER; GPT-4o-mini와 Qwen2.5-7B | 자율 과학 R&D programme·코딩·웹 장기 연구 population이 아니다. task 수, 표본 선정, split, seeds, 실행 순서/길이, cold/warm start가 충분히 보고되지 않았다. |
| metric | PDDL progress rate; HotpotQA/FEVER exact match | 연구 programme의 단일 locked artifact hidden 성과와 다르다. |
| baseline | None, MemoryBank, Voyager, Generative Agents, G-Memory | 같은 두 backbone을 사용한 표는 있으나 retrieval/feedback 접근권, agent scaffolding, 호출 수/토큰 상한, baseline adaptation 상세를 맞췄다는 증거는 부족하다. |
| main result | 모든 표의 task×backbone 셀에서 Ours가 G-Memory보다 높게 보고됨 | 해당 저자 설정의 관측 결과다. 신뢰구간·반복 분산·독립 재현·현재 SOTA는 확인하지 않았다. |
| cost | Ours 6.4M/5.7M, G-Memory 6.2M/5.3M tokens; 무기억 대비 Ours +73.0%/+72.7% | 동일 토큰 예산의 성과 비교가 아니다. compute/storage/latency 전체 회계도 아니다. |

근거: [EG-08–EG-10]. Table 1의 상대 개선율을 절대 percentage-point 개선으로 바꾸지 않는다. 이 수치를 우리 효과크기, power prior, 최소 유용 효과, 표본 수 산출에 사용하지 않는다.

ablation은 `ADD+KEEP`, `ADD+KEEP+ARCHIVE`, `all`이다. graph 유무, 동일 자료의 강한 notebook 대조군, 동일 mandatory checks, `λ=0`, negative scoring 제거를 독립적으로 비교한 실험이 아니다. 따라서 node editing, evidence-aware scoring, graph topology 각각의 인과 기여가 분리되었다고 말할 수 없다 [EG-11].

**명시적 반례:** §4.3은 GPT-4o-mini의 PDDL에서 ADD+KEEP=26%, ADD+KEEP+ARCHIVE=34%, full=31%라고 보고한다. full이 append-only보다 높다는 관측은 맞지만 REVISE를 추가한 full이 항상 최선은 아니다. 이 수치는 저자 본문 보고이며 diagram 재판독·반복시험에 의한 승자 판정이 아니다. 더 복잡한 controller를 기본 승자로 정하지 않을 근거로만 쓴다 [EG-12].

저자가 인정한 한계는 noisy/incomplete task feedback에 의한 유용한 insight의 잘못된 archive·이른 revision, 단순 positive/negative set의 적용 맥락·효용 정도 표현 부족, 세 benchmark 밖 일반화 미검증, graph 유지의 연산·저장 overhead다 [EG-13].

## B/C/G와 프로토타입에 대한 적용

프로젝트 §4의 B/C/G를 확인했다: B는 강한 source-backed tree/notebook과 advisory applicability/revalidation/preservation/recovery, C는 같은 정보·권리 위 mandatory checks, G는 같은 의무·집행 강도 위 graph-mediated traversal/scoped invalidation/continuation이다. `G−C`는 graph-control package의 증분이며 pure topology 추정이 아니다. 현재 P0 C0 feasibility를 arm comparison으로 바꾸지 않는다.

- **B에도 보장할 정보:** 과거 실패, positive/negative 사용 사례, 보관된 원본, 변경 이유, 현재/과거 버전 조회. 논문은 이 정보의 가치를 질문할 근거이며 G만 독점해야 한다는 근거가 아니다.
- **C와 G 공통 연구 의무:** 변경 근거와 적용 범위를 확인하고, 판정 불확실성을 보존하며, 수정 문장이 과거 positive evidence를 계속 만족하는지 재검증한다. controller label을 독립 검증 근거로 승격하지 않는다.
- **G에서만 측정할 추가 기능:** 동일 record로부터 graph가 종속 항목을 찾아 범위별 invalidation/continuation을 제어하는 이득과 비용. EvoGraph-Mem의 global archive/retained edges는 이 기능을 직접 실증하지 않는다.
- **채택 후보:** archive 원본 보존, 수정 계보, operation/feedback provenance, 조회 당시 적용 상태를 prototype 설계 후보로 남긴다. 이들은 graph가 없어도 표현 가능하다. lineage 존재와 유효성은 구분한다.
- **채택 전 반증 항목:** 유효 insight 오비활성화, 다른 task에서만 유효한 insight의 전역 손실, revision 후 과거 지지 근거의 무효 계승, active-negative 도달 가능성, `ARCHIVE` 대 `ARCHIVE+REVISE`의 비용·성과. 프로토타입 채택/구현은 후속 측정과 construction-resume 범위에 따른다.

판정: **연구 질문·ablation 후보·실패 모델에는 directly_supported; 우리 graph-control package 효능·우월성에는 insufficient.** 논문 전체를 G 승리 근거로 사용하지 않는다. 신규성은 이미 제시된 editable graph memory 자체가 아니라 동일 권리·의무의 강한 대조군 아래 장기 연구 의존성 제어의 추가 가치라는 기존 질문을 유지한다.

## Locator

각 줄 번호는 위 SHA가 고정된 추출 파일의 LF 기준이다. machine-readable claim/use-limit은 `evograph-review.json`에 같다.

| ID | 줄 | 근거와 사용 한계 |
|---|---|---|
| EG-01 | 3–5, 92–96 | 제목·저자·버전·외부 memory; peer review 확인 아님 |
| EG-02 | 292–477 | G-Memory 기반 query 검색·이웃 확장·insight 연결; 실제 코드 검토 아님 |
| EG-03 | 478–608 | evidence/state와 scoring; scoring의 유효 작동 실증 아님 |
| EG-04 | 609–657, 1162–1230 | LLM controller 입력·제약·JSON; 독립적 인과 label 아님 |
| EG-05 | 658–758 | archive/revise/add/keep 상태 변경; 수정 결과 재검증 완료 아님 |
| EG-06 | 723–792 | ADD positive, resolved 조건의 edge; dependency invalidation 구현 증거 아님 |
| EG-07 | 527–608, 658–758 | active-negative 불변식 조건부 추론; 코드 버그·실측 실패 단정 금지 |
| EG-08 | 793–861 | population·metric·baseline; R&D programme 외삽 금지 |
| EG-09 | 842–852 | author-reported Table 1; 로컬 재현/SOTA/power prior 금지 |
| EG-10 | 868–884, 931–955 | author-reported token overhead; equal-budget 평가 아님 |
| EG-11 | 956–988 | operation ablations; pure graph/negative scoring 분리 아님 |
| EG-12 | 965–983 | GPT-4o-mini PDDL archive 34 vs full 31; full 항상우월 반례, 실험 승자 아님 |
| EG-13 | 1035–1052 | 저자 인정 한계; 세 benchmark 밖 효능 증거 없음 |
