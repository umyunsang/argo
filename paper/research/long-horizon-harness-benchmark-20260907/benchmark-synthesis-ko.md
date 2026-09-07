# 장기 지평 에이전트 연구 벤치마킹과 연구 고도화

내부 연구 결정 자료 · 2026-09-07 · 원문 기반 비교 · 새 효능 실험 미실행

## 1. 결론: 같은 방향이지만, 같은 기여로 쓰지 않는다

여덟 연구는 언어모델의 단발성 답변을 넘어 **외부 상태·실행·피드백을 통해 누적 작업을 수행한다**는 방향을 공유한다. 그러나 발전 대상이 다르다. Prime Agent와 Scroll은 실행·컨텍스트 기질, HoH는 소프트웨어 산출물, SkillZip은 절차 라이브러리, RecEvolve는 추천모델, Metaⁿ은 생성된 개선 계층, HarnessDev는 재사용 하네스의 평가, Terminal-Universe는 환경·학습 데이터와 학습된 가중치를 다룬다. 이를 하나의 성능 순위나 “자율성 점수”로 합치면 비교 대상이 바뀐다.

우리 연구는 이 기제들을 모두 새로 구현하거나 독창적이라 주장하지 않는다. 주 비교는 **동일한 강한 evidence-aware result tree와 원문 접근권을 가진 두 조건에서, exact-version dependency 제어가 추가로 필요한가**이다. 범위는 근거 교정 이후의 다음 실험 선택, 선택적 재검증, 무관한 결과 보존, fresh-context 인계이다. 이 질문은 아직 행동 효능으로 입증되지 않았다.

## 2. 연구별 채택·제한

| 연구 | 채택할 요소 | 그대로 주장하거나 도입하지 않을 것 |
|---|---|---|
| Prime Agent | 영속 REPL/세션, 명시적 비동기 handle, 원문 이력, root+descendant 비용 귀속 | 별도 런타임 중복 구현, 자기반성을 자동 과학 검증으로 취급 |
| Harness-of-Harness | 산출물 A와 증거 E 분리, 작은 완결 증분, 단일 작성자, 고정 후보의 읽기 전용 QA | 새 기능을 매번 강제, QA 역할 분리를 오류 독립성으로 간주, 실패 실행 대체로 분모 삭제 |
| HarnessDev | creator/executor 구분, 후보 동결, feedback/held-out 분리, 작동한 경로와 선언된 코드 구분 | 새로운 단일 평가 지표라고 축소, public system reference를 동일 모델 대조군이라고 주장 |
| Scroll | 원문 주소가 남는 eviction, locate→materialize→compute→expose, query-time 재접근 | 원문 보존을 완전 검색·의미 충분성 보장으로 확장 |
| SkillZip (2608.05604) | section 계약, occurrence별 출처, port/의존성/검증 경로, 가역 expansion, 조건별 macro demotion | 구조 보존을 의미 동치·검증기 정확성으로 승격, 다른 동명 SkillZip과 혼용 |
| RecEvolve | 가설–비평–구현–학습–평가, 중앙 지식과 격리된 실행, 부정 결과의 조건부 재사용 | 실패 가설 영구 금지, 작은 proxy에서 개선되면 전체 학습도 개선된다고 추정 |
| Metaⁿ | 고정 개선 인터페이스, 실행 trace와 그 trace를 만든 코드의 공동 진단, 후보 계보 | 고정 Ω가 전체 시스템 안정성을 증명한다는 해석, archive-best를 단일 배포 정책 성능으로 사용 |
| Terminal-Universe | observed/inferred 파일 구분, 원과제 미해결 초기상태, 다중 라운드 요구 변경·회귀검사 | 합성 복원을 원환경 재현으로 주장, 학습용 성공 선별을 연구 결과 분모에 적용 |

근거: [Prime Agent](https://www.alphaxiv.org/abs/2608.23552) §§2–3; [HoH](https://www.alphaxiv.org/abs/2609.01481) §§3–5/부록 A–B; [HarnessDev](https://www.alphaxiv.org/abs/2609.01437) §§3–6; [Scroll](https://www.alphaxiv.org/abs/2608.21690) §§2–4; [SkillZip](https://www.alphaxiv.org/abs/2608.05604) §§3–5; [RecEvolve](https://www.alphaxiv.org/abs/2609.01622) §§3–6; [Metaⁿ](https://www.alphaxiv.org/abs/2608.24735) §§2–4; [Terminal-Universe](https://www.alphaxiv.org/abs/2609.04148) §§3–7. 저장 원문/해시/라인은 `source-receipts.json`, `claim-locators.json`, 다섯 독립 audit에 보존했다.

## 3. 과장하지 않아야 할 성과와 반례

### 3.1 장기간 동작과 일반적 과제 성공은 다르다

Prime Agent는 7일 Factorio 사례에서 196개 중 24개 기술을 완료했다고 보고한다. 다른 trace에서는 자원 생성 편법이 재사용 skill로 보존됐다. nanoGPT에서는 최종 기록의 하네스 차이가 실험 잡음에 비해 작다고 명시한다. 그러므로 긴 실행·하위 agent 수·refine 횟수는 설명 변수이지 효능의 대체 점수가 아니다. ARC 외부 기준값과의 차이도 동일 조건의 하네스 인과효과로 읽지 않는다. [원문 §§3.1, 3.3, 3.5](https://www.alphaxiv.org/abs/2608.23552)

HoH의 3-pass 비교는 중요하다. GameCraft 45과제에서 HoH 71.52/8.41M tokens, Vanilla Continuation 58.24/6.33M이다. 점수 차이 13.28이 있지만 동일 token 예산은 아니다. HoH@2는 64.84/5.67M으로 VC@3보다 높은 점수와 낮은 평균 token을 보여 준다. 다만 이것도 무작위화된 동일 총비용 실험과 같지는 않다. 70-loop FPS는 한 프로젝트의 사례이며, 81개 issue 중 65개 종료·16개 미해결·17개 재개방과 사람의 network/API 복구를 함께 보고한다. [원문 Tables 2–3, §§5.1–5.2](https://www.alphaxiv.org/abs/2609.01481)

HoH abstract의 52.25%는 이질적인 세 benchmark의 상대 변화 평균이다. FrontierSWE는 reward가 아니라 비교 pool에 의존하는 dominance가 사용되며, 최대 82.86%는 35→64의 상대 증가(+29 percentage points)이다. 이 값들을 우리 연구의 예상 향상률로 사용하지 않는다. 부록 B.2는 infrastructure/transport 실패 시 대체 실행을 허용하므로 총 launch 수와 valid-run 수를 구분해야 한다. [원문 Table 1, Appendix B.2/B.7](https://www.alphaxiv.org/abs/2609.01481)

### 3.2 보존–노출–충분성–유효성의 네 단계

Scroll의 불변조건은 제거된 history가 주소로 복구 가능하다는 것이다. 원기록이 모두 있어도 잘못된 검색 축과 표본 노출 때문에 필요한 근거를 놓칠 수 있으며, 부록에는 그 사례가 있다. LOCA256K의 가까운 같은-backbone 비교는 Scroll 86.7 대 CodeAct 85.3이다. 37.4-point headline은 다른 공개 시스템 기준과의 차이다. [원문 §§2.4, 4.1, Appendix D](https://www.alphaxiv.org/abs/2608.21690)

SkillZip의 Proposition 1은 non-conflicting motif와 전체/비포함 occurrence 조건에서 **기록된 구조**를 복원한다. 원문도 semantic guarantee가 아님을 명시한다. DPR 99.2%, verifier reachability 98.7%는 검증기 실행 성공이나 모든 의미의 보존이 아니다. 계약 추출의 exact match 84.6%, 복구 필요율 14.8%도 함께 고려한다. 우리 연구는 graph 경로 유무, 필요한 근거 노출, 현재 조건에 대한 충분성, 독립 결과를 별도 측정한다. [원문 Proposition 1, Tables 2–3, Appendix B/D](https://www.alphaxiv.org/abs/2608.05604)

### 3.3 개선 기록은 유지하되, 승인된 근거는 줄어들 수 있어야 한다

Metaⁿ의 fixed Ω는 개선 연산의 정체성을 고정한다. 하지만 생성된 계층의 간섭과 depth-3 퇴행을 막는 일반 안정성 정리는 아니다. per-task archive 최대는 고정 관측값을 보존하면 단조 증가하지만, 단일 chain이나 새 과제의 router가 그 최대를 달성한다는 뜻은 아니다. 우리 연구에서는 이력을 삭제하지 않되, source나 verifier가 무효화되면 **현재 채택 가능한 결과 집합은 감소**할 수 있어야 한다. [원문 §§2.3–2.4, 3.3 및 Appendix G](https://www.alphaxiv.org/abs/2608.24735)

HarnessDev의 held-out 결과와 feedback 점수는 분리된다. 동일 Gemini 실행 모델의 진화 비교에서는 네 lineage 중 하나만 held-out 개선을 보였다. 64번 변화 중 feedback/held-out 방향 일치는 34번이고, 선언한 최종 버전이 held-out 최선인 것은 2/9였다. 한 lineage/cell이라는 한계가 있으므로 이 비율을 일반 확률로 쓰지 않는다. [원문 §4.3, Table 6, §6.1](https://www.alphaxiv.org/abs/2609.01437)

### 3.4 부정 결과를 기억하되 재검토 가능 조건을 남긴다

RecEvolve는 41개 완료 실험을 약 이틀에 5개 thread로 수행했다고 보고한다. NDCG@50 0.4796→0.5751은 상대 +19.9124%이며, live satisfaction +3.77%는 저자 보고다. 모델 상세·반복·online 표본수와 불확실성이 충분히 공개되지 않아 독립 재현이나 일반 효과로 바꿀 수 없다. batch 8k→1k로 in-batch negatives가 줄어든 편법은 사람이 발견했다. 과거 실패를 재탐색하는 현상도 보고한다. 따라서 실패 기록에는 실패 이유와 적용 조건, 재개방을 정당화하는 변경을 함께 둔다. [원문 Tables 1–2, §§5.2–5.6](https://www.alphaxiv.org/abs/2609.01622)

### 3.5 환경 복원과 학습 데이터 선별은 별도 증거층이다

Terminal-Universe의 reconstruction은 명시적으로 lossy다. 보이지 않은 파일은 completion agent가 생성한다. 37,273개는 과제 조건부 sufficiency 판단을 통과한 환경이지 원환경과 bit/behavior 동치인 환경 수가 아니다. Qwen3.5-27B SFT 후 TB2.1 46.2→58.1과 MT@4 6.3→20.1은 학습 효과이며 frozen harness 비교가 아니다. 동일 teacher가 과제·해법·검증기를 생성한다는 오류 상관 한계도 남는다. 연구 원장에서는 실패 suffix를 자르지 않는다. 학습용 선별본만 별도 lineage로 만들 수 있다. [원문 §§3.1, 3.3, 5, 7 및 Appendix B](https://www.alphaxiv.org/abs/2609.04148)

## 4. 연구 구조에 적용하는 최소 변경

### 4.1 다섯 상태를 구별한다

- **원자료 L:** 읽은 출처와 실행 기록의 불변 이력. 기존 관측은 삭제하지 않는다.
- **산출물 A:** 현재 후보 코드·설계·출력. revision으로 구분한다.
- **절차 계약 C:** 입력, 적용 조건, source version, resource, effect, verifier, output, 재검토 조건.
- **채택 가능 근거 K:** 현재 과제·버전·검증 조건을 만족하는 기록만 포함한다. 교정 후 줄어들 수 있다.
- **작업 뷰 V:** token 예산 안에 노출한 부분. source address와 미충족 의무를 함께 남긴다.

이 구분은 선행 기제의 문헌 기반 재구성이다. “다섯 상태” 자체를 독창성이나 성능 결과로 주장하지 않는다. 탐색·압축·재귀 정책은 K의 유효성을 스스로 승인하지 못한다. 원문이 없거나 scope가 불분명하면 UNDETERMINED/INCONCLUSIVE로 남긴다.

### 4.2 주 비교를 더 강하게 만든다

TREE와 TYPED 모두에 영속 원문 접근, 결과/insight tree, HoH형 preservation/gap records, source version과 applicability facts, 동일 first record와 candidate pool, 동일 critique/refine 기회를 제공한다. TREE에도 explicit freshness checklist와 직접 의존성 검사를 작성할 권리를 준다. TYPED의 유일한 추가 처리는 등록된 exact-version/applicability traversal과 선택적 재검증 제어다. 양쪽 모두 같은 source를 볼 수 있으므로 “정보를 더 줘서 이긴” 설명을 차단한다.

첫 비교에서는 Scroll형 eviction, SkillZip macro compression, Metaⁿ depth, 모델 교체, 학습, task synthesis를 동시에 켜지 않는다. 이것들을 함께 바꾸면 어떤 기제가 효과를 냈는지 알 수 없다. 관련 기제는 공통 기질로 고정하거나 별도 후속 ablation으로 분리한다.

### 4.3 결정적 시험: 늦은 계약 변경 뒤의 최소 정당화된 재검증

하나의 실제적인 연구 과제에서 경쟁 가설을 평가하고 결과를 얻은 뒤, 관련 verifier/source 적용 조건이 변경된다. 기존 성공 중 일부는 새 조건에서 사용할 수 없고, 독립 결과는 남는다. 과거 실패도 (a) 같은 조건이면 재실행하지 않아야 하고, (b) 관련 조건 변경이면 재검토할 수 있어야 한다. 무관한 이름·날짜 변경은 재개방을 유발하면 안 된다. 필요한 원문 일부를 active view 밖으로 보내되 양쪽의 복구 권리는 같게 둔다.

주 endpoint는 기존 workflow decision-contract success를 유지한다. 별도로 회수 가능성, 노출된 근거 충분성, 잘못된 승인/보류, 과잉·부족 철회, 부정 가설 반복/잘못된 영구 억제, 보존 회귀, fresh-context next-action correctness, 최종 독립 과제 성과와 총비용을 보고한다. 과제군/원환경 계보로 split하고 seed·중간 결과·round를 독립 표본으로 세지 않는다. 후보 생성기와 scorer는 treatment label을 보지 않는다.

### 4.4 반증·중단·채택

TYPED 이점이 동일 근거/총예산에서 사라지거나, TREE의 명시적 checklist로 재현되거나, 무관한 결정까지 철회하거나, 부족한 근거를 승인하면 typed 자동 제어의 필요성은 약해진다. 정밀한 null이면 더 단순한 TREE를 선택한다. 압축과 깊이의 추가는 주 결과가 해당 병목을 드러낸 경우에만 검토한다. 표본수·최소 실용효과·hard budget·독립 gold가 없는 지금은 사전등록 완료나 실행 준비로 표시하지 않는다.

## 5. 현재 적용과 남은 한계

이번 변경은 `benchmark-matrix.json`, `research-design-amendment.json`, `claim-locators.json`, 논문용 보충 문안에 반영한다. 보호된 QMD와 과거 exports는 변경하지 않는다. 네이티브 구축 재개, World/agent/model 실행, 외부 제출·배포를 허가하지 않는다. 기존 font qualification은 정확한 host/runtime 다섯 font 호출의 호환성만 지지한다. 현재 integrated TREE/TYPED 효능 근거는 없다.

공개 구현 확인: Prime Agent, Scroll branch, Metaⁿ의 선택 파일을 commit으로 고정했다. HoH 공개 tree는 README와 미디어 중심이고 HoH-lite는 coming soon이다. SkillZip graph/RecEvolve/Terminal-Universe의 공식 구현은 원문 및 제한된 검색에서 식별하지 못했다. 코드를 찾지 못한 것과 존재하지 않는 것은 다르다. 다운로드한 코드는 실행하지 않았다.

## 6. 논문 작성 반영

서론은 “자율화가 완성되었다”가 아니라 “검증 가능한 장기 실행을 위한 외부 상태·운영 구조가 중요한 연구 대상이 되었다”로 쓴다. 관련 연구는 기능별 배열보다 **발전 대상과 보장 범위**로 조직한다. 방법은 원문 보존과 의미 충분성, 구조적 closure와 실제 결과, feedback 최선과 held-out 성능을 구분한다. 결과에는 완료한 검증의 실제 범위만 싣는다. 새 문헌은 별도 보충 자료이며 기존 원고 cutoff·인용 번호·정본을 자동 갱신하지 않는다.
