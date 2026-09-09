# FAIRNESS + SKEPTICAL READER — ARGO 논문 적용 검토

## 범위·상태

- 최종 통합 결정: **본 파일은 비공개 편집 검토 메모**다. R1의 preprint 발견·서지는 이 메모와 보존 자료에만 남긴다. 공개 원고용 §6에는 R1을 인용하지 않으며 `fairness-application.bib`는 출판된 R2/R3/R4만 포함한다. 비용·정보대칭 규칙은 본 연구의 제안 설계이지 검증된 정리나 선행연구의 ARGO 결과가 아니다.
- 기준일: **2026-09-05 KST**. 시작 시 로컬 시계 `2026-09-05 05:41:22 KST` 확인. 문헌의 발행연도와 이번 열람일을 구분한다.
- 완료: 적용 지침·agent brief·migration state·공유 findings 읽기 → 1차 문헌 4편의 관련 본문 및 서지 확인 → 적용 권고 작성. 추가 탐색은 중단한다.
- 읽기 수준은 **선택 본문 구간 열람**이다. 후속 요구에 따라 공식 PDF 4편과 서지 응답을 `fairness-sources/`에 보존하고 그 bytes에서 관련 구간을 다시 읽었다. 원문 전체 다운로드·텍스트 추출은 전체 정독이 아니다. 상세 범위·SHA256·PDF 페이지·텍스트 행 번호는 `fairness-sources/README.md` 및 `read-scope.json`이 우선한다. 이전 임시 웹 응답과 이번 파일의 byte 일치까지 소급하여 주장하지 않는다. `web.run` 재조회를 시행했으며 빈 응답은 근거에서 제외했다.
- 쓰기 범위는 본 파일과 추가로 승인된 `fairness-sources/`뿐이다. 공유 계획·진행 파일은 root 소유이므로 수정하지 않았다. 원자료 감사, 실험, 통계 계산, 원고·canonical 문서 변경, 재귀 위임은 하지 않았다.
- 현재 증거 경계: **ARGO 효능 결과 없음; Stage 0는 instrument 및 runtime-policy 검사 PASS만; native construction paused**. 숫자 단위는 후속 공유 `findings.md`에 따라 **16 scorer fixtures × 6 checks = 96 evaluations; 통합 인증 과제 0, 인정된 효능 결과 0**으로 구분한다. 본 lane이 원자료를 감사한 수치가 아니며, 96회를 에이전트 과제 수행 횟수로 해석하지 않는다.
- 현행 `docs/argo/agent-brief.md`와 `migration-state.json`은 native construction pause, 빈 native completed slices, oracle의 비-runtime 권한을 확인한다. 기억의 과거 고정 G×C×F 설계·표본수는 현재 설계의 권위로 재사용하지 않았다. pause는 `directly_supported`; 과거 구체 실험 배치는 `near_match_only`; 현 ARGO 효능은 `insufficient`이다.

## 1. 먼저 고칠 핵심 주장

**논문의 대상은 통합 아키텍처이지 기록 stub의 이름 변경이 아니다.** 현재의 허용 기여는 통합 설계, 구현 계보, 평가 계약, 측정기 점검 결과와 남은 검증 조건이다. B2 logging stub을 ARGO prototype으로, receipt PASS를 task performance 또는 SOTA로 승격시키지 않는다. 이는 본 lane의 증거 범위 판정이며 문헌이 ARGO의 상태를 판정했다는 뜻이 아니다.

비교 질문은 두 층으로 나누는 것을 권고한다.

1. **통합 시스템 비교:** 정해진 정보 접근·예산·과제 아래 ARGO 설계 전체가 실행 가능한 비교 시스템과 어떻게 다른가? 내부 검색·메모리·조정·refinement 경로의 차이는 개입에 포함한다.
2. **기전 진단 비교:** 동일한 사실 자료를 제공했을 때 그래프 표현, 조정 또는 refinement 중 명시한 요소가 차이를 만드는가? 여기서만 해당 요소 외의 표현·접근 차이를 더 좁게 통제한다.

두 질문을 한 결과표에서 섞지 않는다. 통합 비교만으로 개별 모듈의 인과적 기여나 상승효과를 주장할 수 없고, 내용 고정 진단만으로 실제 검색을 포함한 end-to-end 시스템의 우월성을 주장할 수도 없다. 이 구분은 [R1, R2]에 근거한 **ARGO용 설계 권고**이지 선행연구가 이 설계를 검증했다는 진술이 아니다.

## 2. 1차 문헌의 발견과 적용 한계

| ID | 직접 읽은 근거 | ARGO에 사용할 주장 | 넘어서는 주장 |
|---|---|---|---|
| R1 | Kapoor et al., §2, §3.2, §4, §5 도입·§5.2, §6의 선택 구간; 보존 PDF pp.2–11 중 read-scope에 열거한 행만 | 정확도만으로 architecture gain을 판단하지 않고 비용·재시도·평가 조건을 공개한다. 개발에 노출된 과제로 일반화를 주장하지 않는다. | HumanEval 등에서 얻은 결과를 ARGO 효능으로 전이하거나 모든 refinement가 무효라고 단정하지 않는다. |
| R2 | Yang et al., §4 baselines/metrics/configuration search; §5.1 및 Table 3, pp.5–6 | 같은 기반 모델이어도 검색·편집·관측 창·이력 처리라는 ACI 차이가 평가 결과를 바꿀 수 있다. | 소프트웨어 수정 실험으로 연구 전 과정의 성과를 보증하지 않는다. 논문의 비용 정의는 성공 사례 평균이므로 ARGO의 전체 시도 비용 정의와 혼동하지 않는다. |
| R3 | Zheng et al., §3.3–3.4, pp.4–6; §4는 적용 대상 확인 | 위치·장황성·추론 채점 한계가 있으므로 judge를 진실 판정기로 취급하지 않는다. | 인간 선호 일치가 사실 정확성 검증은 아니다. 특히 self-enhancement는 저자들이 자료만으로 확정할 수 없다고 명시하므로 ‘입증된 보편적 자기편향’이라고 쓰지 않는다. |
| R4 | Pineau et al., §2.5, §4 후반, §5 도입, §6 선택 구간; Appendix Figure 8, p.20은 보존 PDF에서 렌더하여 다시 확인 | 재현 조건과 제외·설정·환경을 공개하고, 체크리스트 이행과 재현 성공을 구분한다. | 저자들도 프로그램의 연구 품질 개선에 결론적 근거가 없다고 제한한다. 따라서 ‘체크리스트/receipt가 성능을 검증한다’는 인용은 부정확하다. |

## 3. 적용 권고 행렬

아래는 **미실시 prospective 권고**다. 반증 확인은 향후 사용자 승인과 실제 통합 runner가 갖춰진 경우의 후보이며 이번 작업에서 실행하지 않았다. 검정식·표본수·유의수준은 통계 lane에 맡긴다.

| 비교 대상 | 반드시 맞출 조건 | 개입이 정당하게 바꿀 수 있는 것 | 공개할 내용 | 회의적 독자의 반론 | 가장 싼 반증 확인 후보 |
|---|---|---|---|---|---|
| 기반 모델·하네스 [R2] | architecture 비교에서는 모델 snapshot, 기본 decoding, 과제·환경·공통 실행 substrate | 사전 명시한 orchestration, 관측 편집, memory/refine 정책. 따라서 시스템 prompt 전체의 동일성을 강요하지 않음 | 조건별 prompt·tool schema·버전·공통/상이 항목과 이유 | 단지 더 좋은 모델이나 기본 editor를 쓴 것 아닌가? | 모델·공통 shell 조건을 맞춘 최소 comparator에서도 방향이 유지되는지 확인 |
| 정보 동등성 — 기전 진단 [R1, R2] | 원문·파일·예제·공개 테스트·초기 사실 및 접근 권한 | 같은 사실의 그래프 조직, 탐색 순서·검색 표현·압축 | 두 조건의 사실 자료 대응표; 추가 annotation의 생성 주체·비용·시점 | 그래프가 아니라 더 많은 정답 정보를 받은 것 아닌가? | 같은 사실·출처를 가진 flat evidence comparator에 주면 이점이 사라지는지 확인 |
| 검색 포함 통합 비교 [R1, R2] | 허용 corpus/도구·시점·접근 권한·상한; offline면 corpus snapshot | 질의 생성, 검색 선택, 재순위화 및 찾아낸 자료 차이 | query/returned document 이력, live web 변동, content-fixed 진단과의 구분 | 우연히 더 유리한 검색 결과가 온 것 아닌가? | content-fixed 진단과 system-level 결과를 구분해 대조; 동일 결과 강제는 검색 기전을 제거함 |
| 자원·개발 노력 [R1] | 사전 정한 자원 상한, timeout·중단 규칙, 비교군에도 허용한 개발 자료·튜닝 한도 | 상한 안에서 호출 수·실제 소비·조기 중단; 실제 소비까지 같게 할 필요 없음 | input/output/cached/reasoning usage의 제공 여부, 모델 호출·검색·계산·총 비용·시간, 가격일, 개발 비용과 평가 비용 분리 | 더 많은 시도나 숨은 튜닝 비용 때문 아닌가? | 같은 상한의 단순 retry comparator를 확인; 실제 소비·실패 비용을 포함하면 결론이 바뀌는지 확인 |
| 기능 보존 comparator [R2] | 작업 완료에 필요한 정상 경로·제출 형식·동일 평가 계약 | 목표 모듈의 기능적으로 유효한 대체: graph→flat memory, refine→단순 retry 등 | 대체 기능·누락 기능; full stack와 ablation의 별도 해석 | 기록을 못 하게 망가뜨린 상대를 이긴 것 아닌가? | comparator가 정상 제출할 수 있는지 먼저 검사. B2가 logging stub이면 성과 비교군·prototype으로 사용하지 않음 |
| 평가자·가시성 [R3] | rubric·judge 버전·reference·응답 표시 정책·사실 검증 자료 | 연구 대상인 산출물 내용은 달라져야 함; 장황성 통제가 기여를 삭제하지 않도록 기능 점수와 분리 | judge에게 보인 입력, 모델/작성자 노출, 순서 처리·불일치·인간 검토의 실제 실시 여부 | 형식·길이·작성자 표식을 선호한 것 아닌가? | 동일 산출물 순서/명칭 교환 및 오류가 알려진 답안에서 판정이 안정적인지 확인 |
| 누출·상태·인간 개입 [R1] | hidden 정답/평가 코드 접근 차단, 동일 초기 상태, 교차 조건 memory 차단, 같은 사람 개입 정책 | 종단 memory가 연구 대상이면 사전 지정한 조건 내부의 학습·이력만 허용 | development/heldout 노출, 검색 가능 정답, 적응에 사용한 피드백, reset·개입 이력 | 이전 과제 정답이나 사람 도움을 기억한 것 아닌가? | 비노출 자료와 clean initial state에서 확인; 사전학습 오염의 완전 부재는 별도 미확인으로 남김 |
| 실행·점수·추적 [R1, R4] | 공통 결과 판정·분모·예외/재실행 정책·평가기 버전 | 실행 경로 및 실제 실패 유형 | 모든 시도의 종료 상태, 실패/중단/미실행 구분, 결과와 receipt 매핑 | 성공 로그만 고르거나 grader crash를 성공으로 셌는가? | 적법한 제출과 누락·오류 제출이 계약대로 구별되는지 확인; 평가기 결함은 실제 task failure와 별도 표기하고 사후 임의 제외 금지 |

**중요한 예외:** 하네스가 바로 개입이면 ‘모든 하네스 동일’은 잘못된 통제다. 공통 substrate와 의도한 차이를 구분해야 한다. 반대로 통합 설계의 이점을 주장하면서 정보 우위·튜닝 우위·기반 모델 차이를 숨기는 것도 허용되지 않는다. 행렬의 공정성은 인구집단별 공정성이 아니라 **비교의 절차적·정보적 동등성**을 뜻한다.

## 4. 현재 원고에 적용할 skeptical-reader claim audit

이 표는 사용자 제공 증거 경계를 이용한 문장 심사이며 raw artifact 감사 결과가 아니다.

| 예상 주장 | 판정·대체 문구 | 강한 주장을 위해 아직 필요한 것 |
|---|---|---|
| ‘ARGO가 연구 성능을 높였다’ | 기각. ‘통합 설계의 평가 조건을 제안하였다’ | 실제 통합 시스템·유효 comparator의 과제 수행 결과 |
| ‘16 tasks / 96 fixtures로 ARGO를 검증하였다’ | 범위 축소. ‘Stage 0 측정기·runtime-policy 점검을 수행하였다’ | task-runner 통합 검증과 효능 평가는 별개 |
| ‘B2 ARGO prototype’ | 기각. ‘기록 동작을 점검하는 B2 stub’ | 실제 구현 계보·통합된 의사결정 및 수행 경로 |
| ‘graph receipts로 SOTA 달성’ | 기각. ‘실행·출처 추적 자료’ | 동일 benchmark/version/protocol의 실제 비교 성과; 경쟁 결과 조사 |
| ‘다중 에이전트의 독립적 검증’ | 미실시라면 기각. ‘역할을 분리한 검토 구조’ | 누가 무엇에서 격리되었는지; 공유 모델·자료·기억 공개 |
| ‘context graph가 논문 근거의 진실성을 보증’ | 기각. ‘주장과 근거를 추적 가능하게 연결’ | 원문 함의 확인과 결과 재검증; 스키마 적합성만으로 부족 |
| ‘재현 가능성이 확보되었다’ | 조건부. ‘재현에 필요한 자료·절차를 제시하였다’ | 명시된 환경·코드·데이터로 제3자가 목표 결과를 다시 얻은 기록 |

반론에 답하는 순서: **무엇을 만들었는가 → 무엇이 실제 실행되었는가 → 무엇을 어떤 기준으로 확인했는가 → 대안 설명은 무엇인가 → 그 범위에서만 무엇을 주장하는가.** 결론에서 향후 실험을 과거형으로 바꾸지 않는다. artifact 행정 성공과 과학적 결론 사이에는 직접적인 함의 관계가 없다. [R4를 참고한 본 검토의 작성 규칙]

## 5. 실시 사실을 요구하는 용어 가드

| 표현 | 사용 전에 필요한 실시 증거 | 현재 사용할 안전한 표현 |
|---|---|---|
| randomization / 무작위화 | 무엇을 무작위 배정했는지, 생성 방법·순서·적용 기록. seed 설정이나 judge의 확률적 생성은 배정 무작위화가 아님 | ‘실행 순서 무작위화를 계획한다’ 또는 실제 고정 순서 명시 |
| blind / 눈가림 | 가린 대상, 가린 정보, 시점·해제 절차·실패 가능성. 파일명 익명화만으로 전체 평가가 blind인 것은 아님 | ‘평가 시 조건명 비공개를 계획한다’; 실제 수행 전에는 ‘blind evaluation’ 금지 |
| independent / 독립 | 통계적 독립, 별도 실행, 별도 평가자 중 의미를 명시하고 해당 근거 제시 | ‘별도 세션’, ‘역할 분리’; 같은 기반 모델 여러 번 호출을 독립 검증이라 하지 않음 |
| causal / 인과적 | 개입·비교·배정 및 교란 통제의 실제 구현과 분석의 식별 가정. planned control만으로 causal result 아님 | ‘차이의 원인을 구분하기 위한 설계’; 현재 인과 효과는 미검증 |
| validated / 검증된 | 대상·검사·기준·버전·통과 범위를 함께 제시 | ‘Stage 0의 특정 instrument/runtime-policy 검사 통과’; ‘validated ARGO’ 금지 |

이 가드는 단어를 지우는 규칙이 아니라 **실시 사실과 주장 범위를 연결하는 규칙**이다. 문헌의 저자가 수행한 randomization, anonymization, human agreement 측정을 ARGO 연구도 수행한 것처럼 전용하지 않는다. [R3, R4]

## 6. 공개 원고용 한국어 문단 — 출판 문헌만 인용

### 연구 대상·현재 성과

본 연구는 증거 관리, 실행 추적 및 반복적 검토를 결합하는 ARGO의 통합 아키텍처를 연구 대상으로 삼는다. 다만 2026년 9월 5일 현재 확보된 결과는 Stage 0의 측정기 및 runtime-policy 점검에 한정되며, 통합 ARGO의 과제 수행 효능을 입증하지 않는다. B2는 기록 동작을 점검하는 stub이므로 ARGO 프로토타입의 성능 결과로 제시하지 않는다. 네이티브 구현은 중단 상태이며 설계 검증 이후 별도 승인에 따라 진행한다.

다음 문단은 **방법 장의 설계 원칙 또는 한계 장에 사용할 문안**이다. ARGO에서 이미 공정 비교를 수행했다는 결과 문장이 아니다. 본문 인용은 간접 인용이며, 문헌의 직접 관찰과 본 연구의 적용 권고를 구분한다. 대응하는 완성 BibTeX는 `fairness-sources/fairness-application.bib`에 있다.

### 비용과 비교 질문 — 방법 장

본 연구는 과제 성과와 자원 사용을 함께 비교하기 위해 조건별 자원 상한과 중단 규칙을 사전에 명시하고 실제 소비량은 별도로 보고하는 평가 설계를 제안한다. 상한을 맞추는 것은 실제 비용을 동일하게 만들겠다는 뜻이 아니다. 호출 수와 제공되는 사용량 정보, 평가 시점의 가격, 실행 시간 및 실패한 시도의 비용을 함께 공개하고, 설계·튜닝 비용과 과제 실행 비용도 구분하고자 한다. 이는 추가 계산이나 개발 노력을 아키텍처의 기여와 구별하기 위한 제안이며, 이미 수행한 비교나 공정성을 보장하는 정리로 제시하지 않는다.

적용 지위: **본 연구의 제안 설계**. 공개 원고에서 이 규칙의 근거로 R1을 인용하지 않는다. 통합 효용 비교에서 달러 비용을 다루는 것과 계산량을 통제하는 기전 진단을 혼동하지 않는다.

### 정보대칭과 그래프의 기여 — 방법 장

본 연구는 동일한 정보에 접근할 기회와 실제로 제공된 정보 내용의 동일성을 구분하는 비교 설계를 제안한다. 검색을 포함한 통합 시스템 비교에서는 허용 자료군, 접근 권한, 자료의 기준 시점과 자원 상한을 맞추되, 검색 질의와 선택된 문서의 차이는 시스템의 동작으로 남겨 두고자 한다. 반면 그래프 표현의 기여를 진단하는 비교에서는 같은 사실·관계·출처를 갖는 평면형 자료를 비교 조건에 제공하도록 설계한다. 그래프에만 정답 단서나 사람이 추가한 관계 주석이 포함된다면 그 차이를 순수한 표현 효과로 해석하지 않는다. 관계 주석의 생성 주체·시점·비용을 공개하고, 각 비교가 답하려는 질문을 명시할 계획이다.

적용 지위: **그래프/평면형 정보대칭은 본 연구의 제안 설계**이며 선행연구가 보증한 통제 정리가 아니다. 모델이 새로 생성한 관계까지 개입에 포함하면 ‘순수 표현 효과’가 아니라 ‘표현 및 관계 생성 정책의 결합 효과’를 묻는 비교가 된다. 공개 원고에서 비용·정보 매칭에 R1 또는 R2를 권위 인용처럼 붙이지 않는다.

### 하네스 차이와 해석 가능한 개입 — 방법 장

SWE-agent의 소프트웨어 수정 실험은 검색·편집 인터페이스와 이력 처리의 설계 차이를 평가 대상으로 다루었다. [@yang2024sweagent] 이를 참고하여 본 연구는 공통 실행 기반과 의도적으로 변경한 기능을 분리하여 기술하고, 비교 시스템이 과제를 완료할 수 있는 정상 경로를 유지하도록 설계하고자 한다. 연구 대상이 통합 하네스이므로 모든 내부 구성을 동일하게 고정하지는 않는다. 다만 통합 시스템 간 차이를 확인하더라도 그 결과만으로 그래프, 조정 또는 반복 검토 중 어느 구성요소가 원인인지 단정하지 않으며, 개별 기여와 구성요소 간 상호작용은 별도 진단의 대상으로 남긴다.

적용 근거: R2 §4의 Baselines·Configuration search, p.5; §5.1 및 Table 3, pp.5–6. 인용은 첫 문장의 선행 실험 범위에 붙인다. 이후 기능 보존·기여 분리 규칙은 ARGO용 제안이며, R2의 소프트웨어 수정 성과를 연구 전 과정의 성과로 일반화하지 않는다.

### LLM 평가자의 역할과 추론 한계 — 평가 방법·한계 장

LLM 평가자는 설명의 명료성이나 응답 간 선호를 비교하는 보조 수단으로 사용할 수 있으나, 그 판정을 과학적 사실의 확인과 동일시해서는 안 된다. 선행연구에서는 응답 위치와 장황성의 영향, 그리고 평가자가 풀 수 있는 문제에서도 제시된 답안에 의해 오판하는 사례가 보고되었다. 따라서 본 연구는 산출물의 사실·계산·과제 계약 적합성 확인과 표현에 대한 평가를 분리하는 방식을 제안한다. 판정의 일관성이 높아졌다는 사실만으로 정확성이 확보되었다고 해석하지 않으며, 사용한 평가 모델·rubric·참조 자료와 판정 불일치를 공개해야 한다. 눈가림, 순서 교환 또는 인간 검토가 실제로 수행되지 않았다면 이를 완료된 평가 절차로 기술하지 않는다. [@zheng2023judge]

적용 근거: R3 §3.3–3.4, pp.4–6; §4 도입·§4.1, p.7. 인간 선호와의 일치가 과학적 정답 검증이라는 뜻은 아니다. 이 문헌은 자기선호 편향을 확정하지 못했다고 명시하므로 ‘모든 LLM 평가자의 자기편향이 입증되었다’는 표현도 금지한다.

### 누출·기억·사람의 개입 — 방법 장

본 연구는 평가 과제 사전 노출, 조건 사이에 공유된 기억 및 사람의 교정이 비교 해석을 흐릴 가능성에 대비하여, 개발 자료와 평가 자료를 구분하고 각 조건의 초기 상태와 허용한 피드백·개입 범위를 명시하는 평가 설계를 제안한다. 지속적 기억이 연구 대상인 경우에는 그 사용 자체를 제거하기보다 허용되는 축적 범위를 사전에 정의하고, 다른 비교 조건이나 비공개 정답으로부터의 정보 유입과 구별하고자 한다. 이러한 절차는 평가 시점의 누출 가능성을 줄이려는 제안이며, 실제 누출 방지 검사 완료나 기반 모델의 사전학습 오염 부재를 입증하지 않는다.

적용 지위: clean state·교차 조건 기억 통제는 **본 연구의 제안 설계**다. 공개 문안에서 preprint를 근거로 사용하지 않으며, 실제 수행한 검사로 기술하지 않는다.

### 추적 가능성과 효능의 경계 — 한계·결론 장

Pineau 등은 재현성을 위한 보고 체크리스트를 제시하면서도 해당 프로그램이 과학적 품질을 개선했다는 결론적 근거는 확보하지 못했다고 밝혔다. [@JMLR:v22:20-303] 본 연구에서도 원문 보존·해시·주장별 위치 기록을 근거 확인의 수단으로 사용하되, 이를 인용의 함의 정확성이나 시스템 효능의 자동 보증으로 취급하지 않는다. 현재의 측정기·정책 점검, 향후 통합 실행 검증, 과제 수행 효능 및 외부 비교 성과를 서로 다른 증거 단계로 기술한다. 현 단계에서는 ARGO의 우월성이나 개별 모듈의 인과적 효과를 결론으로 제시하지 않고, 판단에 필요한 비교 조건과 남은 검증 범위를 명시한다.

적용 근거: R4 §2.5, pp.5–6; §4 후반, p.10; §6, pp.12–13 및 Figure 8, p.20. 인용은 첫 문장의 프로그램 보고에 붙이며, 이후 ARGO 증거 단계 구분은 본 연구의 판단이다. 해시는 보존 bytes의 동일성만 검사하며 읽기·함의·재현·효능의 증명은 아니다.

## 7. 서지·원문·열람 위치 — 공개용 3편 / 비공개 참고 1편

공개 원고용 BibTeX는 `fairness-sources/fairness-application.bib`의 R2/R3/R4 **3개 레코드만** 사용한다. 공식 `.bib` 응답 자체를 보존했으며 인용 키 및 제목 대소문자 보호용 중괄호만 편집했다. 아래 R1 레코드는 비공개 편집 이력 보존용이며 공개 원고·참고문헌으로 가져오지 않는다. 최종 저널판을 확인했다고 주장하지 않는다.

### R1 — Kapoor et al. — PRIVATE EDITORIAL ONLY / 공개 인용 제외

- 확인 버전: arXiv **2407.01502v1**, 제출 2024-07-01; arXiv DOI `10.48550/arXiv.2407.01502`.
- 공개 상태: 이 파일에서 인용·정독한 것은 arXiv v1이다. OpenReview 검색에는 TMLR accepted 기록이 있으나 직접 페이지는 browser-verification으로 막혔다. **TMLR 최종판과 v1의 본문 일치·최종 서지는 미확인**이므로 아래 레코드는 저널판을 가장하지 않는다.
- 원문: https://arxiv.org/html/2407.01502v1 ; 메타데이터: https://arxiv.org/abs/2407.01502v1
- 보존 PDF locator: §2, pp.2–4; §3.2, pp.5–6; §4의 §4.1 이전 본문, pp.6–7; §5 도입, pp.7–8; §5.2, pp.9–10; §6 선택 구간, pp.10–11. 정확한 행 범위는 `fairness-sources/read-scope.json` 참조. 그 사이의 모든 페이지나 §4.1 전체를 읽었다고 소급하지 않는다.

```bibtex
@misc{kapoor2024agents,
  title = {AI Agents That Matter},
  author = {Sayash Kapoor and Benedikt Stroebl and Zachary S. Siegel and Nitya Nadgir and Arvind Narayanan},
  year = {2024},
  eprint = {2407.01502},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2407.01502},
  url = {https://arxiv.org/abs/2407.01502v1},
  note = {Version 1, submitted 1 July 2024}
}
```

### R2 — Yang et al.

- 공개 상태: **NeurIPS 2024, Main Conference, Advances in Neural Information Processing Systems 37**의 출판 논문. 공식 페이지가 DOI `10.52202/079017-1601`을 제시한다.
- 서지: https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html
- 원문: https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf
- 정독 locator: §4 Baselines, Metrics, Configuration search, p.5; §5.1 Analysis of ACI Design 및 Table 3, pp.5–6. ‘같은 모델’과 ‘같은 인터페이스’가 다른 통제임을 뒷받침하는 범위로만 인용한다.

```bibtex
@inproceedings{yang2024sweagent,
  title = {{SWE-agent}: Agent-Computer Interfaces Enable Automated Software Engineering},
  author = {John Yang and Carlos E. Jimenez and Alexander Wettig and Kilian Lieret and Shunyu Yao and Karthik Narasimhan and Ofir Press},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {37},
  pages = {50528--50652},
  year = {2024},
  doi = {10.52202/079017-1601},
  url = {https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html}
}
```

### R3 — Zheng et al.

- 공개 상태: **NeurIPS 2023, Datasets and Benchmarks Track, Advances in Neural Information Processing Systems 36** 출판 논문. 후속 보존한 공식 BibTeX에서 DOI `10.52202/075280-2020`과 pp.46595–46623을 확인하여 아래에 보완했다.
- 서지: https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html
- 원문: https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf
- 정독 locator: §3.3 Limitations, pp.4–6; §3.4 Addressing limitations, p.6; §4 도입부, p.7. 위치 교환은 이 논문이 실제 수행한 방법이지 ARGO의 완료 절차가 아니다. self-enhancement 비확정 문장은 p.5에 있다.

```bibtex
@inproceedings{zheng2023judge,
  title = {Judging {LLM-as-a-Judge} with {MT-Bench} and {Chatbot Arena}},
  author = {Lianmin Zheng and Wei-Lin Chiang and Ying Sheng and Siyuan Zhuang and Zhanghao Wu and Yonghao Zhuang and Zi Lin and Zhuohan Li and Dacheng Li and Eric P. Xing and Hao Zhang and Joseph E. Gonzalez and Ion Stoica},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {36},
  year = {2023},
  pages = {46595--46623},
  doi = {10.52202/075280-2020},
  url = {https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html}
}
```

### R4 — Pineau et al.

- 공개 상태: **Journal of Machine Learning Research 22(164):1–20, 2021** 출판 논문. 공식 BibTeX에는 DOI가 없어 생략했다.
- 서지: https://jmlr.org/papers/v22/20-303.html ; BibTeX: https://jmlr.org/papers/v22/20-303.bib
- 원문: https://jmlr.org/papers/volume22/20-303/20-303.pdf
- 보존 PDF locator: §2.5, pp.5–6; §4 후반·§5 도입, p.10; §6 선택 구간, pp.12–14의 첫 행까지. 핵심 제한 문장은 p.12이다. Appendix Figure 8, p.20은 보존 PDF에서 만든 `R4-p20-figure8.png`를 이번에 실제 열람했다. 그림 전체 시각 확인은 Figure 8 하나뿐이며 모든 표·그림의 시각 검증을 뜻하지 않는다.

```bibtex
@article{JMLR:v22:20-303,
  author = {Joelle Pineau and Philippe Vincent-Lamarre and Koustuv Sinha and Vincent Lariviere and Alina Beygelzimer and Florence d'Alche-Buc and Emily Fox and Hugo Larochelle},
  title = {Improving Reproducibility in Machine Learning Research(A Report from the NeurIPS 2019 Reproducibility Program)},
  journal = {Journal of Machine Learning Research},
  year = {2021},
  volume = {22},
  number = {164},
  pages = {1--20},
  url = {http://jmlr.org/papers/v22/20-303.html}
}
```

## Root 통합 메모

1. 본문에 즉시 반영할 것: 현재 성과의 한정, B2 명칭 수정, 비교 질문의 두 층, 실시 사실 없는 방법 용어 제거.
2. 방법 장에 prospective로 둘 것: 공정성 행렬과 조건별 disclosure. 이를 실제 수행 완료표로 바꾸지 않는다.
3. 결과 장에서 분리할 것: instrument/policy checks / 통합 runner 검증 / 과제 효능 / 외부 비교 성과. 앞 단계 PASS는 뒤 단계의 증거가 아니다.
4. 문헌 연결은 주장 함의와 원문 위치를 보존하되, 이 노트의 citation mapping을 native context-graph 통합 완료로 서술하지 않는다.
5. 최종 서지 결정: 공개 인용 키는 `yang2024sweagent`, `zheng2023judge`, `JMLR:v22:20-303`만 사용한다. R1은 출판 문헌만 사용한다는 사용자 결정에 따라 공개 원고·참고문헌에서 제외한다. 비용·정보 매칭은 본 연구의 제안 설계로 기술하며, R1 발견은 이 비공개 편집 메모에만 남긴다.

완료 판정: **문헌 기반 작성·비교 설계 권고 완료; ARGO 효능·prototype·SOTA·독립 재현은 확인 또는 승인하지 않음.**
