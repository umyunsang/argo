# Reviewer 4 — skeptical reader

판정: **REVISE_BEFORE_PREREGISTRATION**. 동결 v1의 사전 설계 검토이며 실험 또는 runtime 결함의 관측 보고가 아니다.

현재 v1은 같은 모델·자원 상한에서 이번에 선택한 두 고정 하네스의 bounded ML 산출물 효용을 비교하는 연구로는 유의미하다. 장기 자율연구, 새로운 기제, 모델 품질 개선, 개발 절차 일반화 및 prototype 선택으로 넓히는 연결은 수정해야 한다. 실행 결함이나 실험 실패를 관측한 검토가 아니다.

독립성: 다른 reviewer 보고서·root 종합·과거 memory 파일을 읽거나 동료와 접촉하지 않았다. 일반 시스템 memory 요약과 현재 작업 지침은 노출되었으나 이전 설계 결론을 근거로 사용하지 않았다. 공유 파일시스템은 OS 격리가 아니다. 19개 packet 파일의 SHA-256은 manifest와 모두 일치한다.

## 실질 지적 5개

### R4-01 · HIGH · 장기 연구라는 구성개념에 과제가 노출되는지 판정할 규칙이 없다

**관측:** 90분·12회 dev 평가의 독립 tabular 과제이며, 연구 기억을 과제/run 사이에 공유하지 않는다. 문서 105행은 개발 pilot에서 의존 지평을 기록하고 없으면 bounded experimentation으로 한정한다고 정확히 경고하지만, 무엇을 의존 지평으로 인정하고 최종 과제에서도 발생했는지 판단할 관측 규칙은 없다.

**왜 문제인가:** 하이퍼파라미터 몇 개를 순서대로 비교하는 것만으로 모든 run이 끝나도 H1은 양성일 수 있다. 그때 지속 실행·장거리 근거 복원·정체 후 재계획의 유용성은 검증되지 않는다. 반대로 관련 병목이 발생하지 않은 null은 장기 하네스가 쓸모없다는 반증이 아니다. 이는 현재 제한된 비교의 내부 타당성보다 전체 논문 목적과 실험 사이의 구성개념 간극이다.

**최소 수정:** 주 분석의 명칭과 기본 해석을 bounded iterative ML experimentation으로 먼저 고정한다. 기존 trace에 추가할 소수의 사전 규칙으로 과거 관측이 나중 선택을 바꾼 경우, active context 밖 근거를 복원한 경우, 복구 후 이전의 확정 선택을 보존한 경우를 구분하고 표적 과제에서도 노출 여부를 보고한다. 장기 연구 설계까지 선택하려면 별도 소규모 연속 연구/재개 probe가 필요하다고 명시하되 20개 주 과제를 결과나 노출 여부로 걸러내지 않는다.

**저비용 반증:** 개발 trace에서 후속 실험들이 초기 상태에서 만든 고정 후보 목록과 단순 최고-dev 선택만으로 설명되는지 눈가림 코딩한다. 뒤 결정에 필요한 과거 근거가 현재 문맥에 모두 남아 있고 비국소 복원/연속 의존이 한 번도 없으면 장기 기제 노출은 실패로 기록한다. 이 검토에서는 probe나 모델 run을 실행하지 않았다.

**남은 불확실성:** 12회 안에도 실제로 누적 의존이 생길 수 있다. 자료를 실행하지 않았으므로 노출이 없다고 단정하지 않는다. 개발에서 관측된 의존이 표적 과제에 동일하게 나타난다는 보장도 없다.

근거:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L23–L31 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L63–L69 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L103–L107 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-to-prototype-objective.md` L5–L9 · SHA-256 `284aec4307c35bf542c15a19ae073d3f57d755c8794596900049f25493a127d9`

### R4-02 · MEDIUM · R의 선행기제 계승과 검증할 기여를 긍정문으로 특정해야 한다

**관측:** R의 Planner→Investigator→Assessor, artifact/evidence의 다음 loop 전달, 필요한 기록만 노출하는 설명은 HoH의 명시적 역할·상태 전달과 크게 겹친다. HoH는 이미 계획 갱신·근거 전달·warm-start 제거 대조도 보고한다. v1은 결합 자체를 신규성으로 주장하지 않는다고 명시하지만, 무엇을 새로 알게 하는 실험인지의 기여 문장은 아직 넓다.

**왜 문제인가:** R−B가 양성이어도 기존 역할 순환을 ML에 적용한 효용, 더 상세한 연구 지시, 일반적인 추가 검토가 설명일 수 있다. 다섯 논문을 연결했다는 이유로 새로운 기제나 해당 요소들의 필요성이 따라오지는 않는다. B가 자발적으로 같은 전략을 쓸 수 있다는 점은 좋은 대조지만, 그러한 자유만으로 실제 B의 지시 내용이 동등하게 강하다는 보장은 없다.

**최소 수정:** 최소 수정은 기여를 신규 architecture가 아니라, 고정 모델과 자원 상한 아래에서 선행연구에서 가져온 명시적 연구 운영 정책을 강한 모델 주도 정책과 비교하는 통제된 ML 평가로 선언하는 것이다. R의 negative 결과 유지·중단 허용 등 실제로 달라진 규칙을 원문 대응과 함께 짧게 특정한다. 더 강하게 운영 강제의 기제 효과를 말하려면 기존 B 후보 3개 중 하나를 R과 같은 연구 판단 지침을 선택적으로 사용할 수 있는 advice-only 후보로 만들어 내용 차이를 줄인다. 새 주 대조군이나 전체요인 실험은 요구하지 않는다.

**저비용 반증:** 두 후보의 prompt/정책에서 role 명칭을 지우고 동일한 과거 관측 한 묶음에 대해 가능한 다음 행동을 수작업으로 비교한다. 달라지는 것이 같은 내용을 세 차례 호출하도록 하는 것뿐이거나 결정 기준이 구분되지 않으면 근거 활용의 새 기제 주장은 보류하고 package 평가 기여로 남긴다.

**남은 불확실성:** 최종 prompt와 정책은 아직 없으므로 의미 있는 규칙 차이가 구현될 수 있다. 원문 몇 편의 유사성만으로 학계 전체의 신규성 부재를 판정하지 않았으며, 추가 문헌 검색은 이 lane 범위가 아니다.

근거:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L9–L19 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L35–L47 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L51–L57 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt` L299–L337 · SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt` L421–L430 · SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt` L843–L875 · SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`

### R4-03 · MEDIUM · U의 우위는 더 좋은 최종 모델을 만들었다는 명제와 동일하지 않다

**관측:** 주 질문은 더 나은 최종 모델을 만드는가이지만 U는 유효 artifact의 BA와 agent 무효/위반의 0을 합친 효용이다. 성공률과 유효 모델 정확도도 보고하기로 했지만, 어떤 분해 결과에서 어떤 문장을 허용할지 정하지 않았다.

**왜 문제인가:** U = Pr(valid) × E[BA | valid]이므로 모델 품질이 같거나 더 낮아도 제출/규약 준수만 좋아져 주 효용이 커질 수 있다. 예를 들어 두 arm의 유효 모델 BA가 .80으로 같고 유효율이 R 1.00, B .95라면 ΔU=.04이다. 이는 실용적 운영 이익이지만 모델 개선이나 연구 판단 개선의 증거는 아니다. 유효 run만 남긴 BA 차이도 처치 후 선택을 조건화하므로 독립적인 인과효과가 아니다.

**최소 수정:** H1과 주 질문을 예산 내 검증 가능한 최종 산출물 효용으로 일치시킨다. 이미 계획한 유효율·BA 보고를 task별 분해와 실패 유형에 연결하고, U만 양성이면 산출물 효용 개선으로 기술한다. 유효 모델 조건부 BA는 기술 통계로 표시하고, 모델 개선의 인과효과나 근거 기반 판단 개선으로 자동 승격하지 않는 해석 규칙을 사전 고정한다. U를 버리거나 주 분석을 생존 run으로 바꿀 필요는 없다.

**저비용 반증:** 최종 결과 해석 템플릿에 BA 동일/유효율만 상승, 유효율 동일/BA 상승, BA 하락/유효율 상승의 세 가상 표를 대입한다. 첫째나 셋째에도 더 좋은 모델을 만들었다는 문장이 출력되면 해석 규칙이 실패한 것이다.

**남은 불확실성:** 공통 fallback은 이 대체 설명의 빈도를 줄일 수 있다. 실제 무효율과 BA 분포를 보지 않았으므로 운영 이익이 지배할 것이라고 예측하지 않는다.

근거:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L9–L11 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L85–L99 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`

### R4-04 · MEDIUM · 한 번의 개발·선택 계보로 개발 절차 자체의 우위를 일반화할 수 없다

**관측:** B/R 각각 한 개발 계보에서 최대 3후보를 만들고, 네 선택 과제에서 후보당 한 번의 실행으로 한 후보를 선택한다. 이후 반복은 선택된 두 artifact의 배포 반복이다. 문서는 배포 성과라고 제한하면서도 비교 단위를 개발 절차 및 배포 package라고 표현한다.

**왜 문제인가:** 깨끗한 표적 평가는 선택된 두 하네스 사이의 차이는 추정하지만, 다른 생성·선택 계보에서도 R 개발 절차가 더 낫다는 분산은 관측하지 않는다. 우위는 한 번의 후보 생성/선택 운에 의존할 수 있다. 또한 같은 토큰·CPU 상한은 실제 소비량이나 사전 인간 설계 노동까지 같다는 뜻이 아니다. 이는 post-selection leakage가 발생했다는 지적이 아니다.

**최소 수정:** 현재 예산을 유지하면서 추정 대상을 이번 동결·선택된 B와 R의 배포 비교로 명시하고 개발 절차 일반화는 미검증으로 둔다. 후보 생성 입력·실제 소비·사전 수작업 설계/수정의 범위를 기록한다. 배포 비용도 실제 사용량과 상한을 나눠 보고한다. 반복 개발 계보는 일반적인 하네스 개선 절차의 우위를 후속 주장할 때만 필요하다.

**저비용 반증:** 기존 네 selection task의 결과만으로 한 task씩 제외했을 때 선택 ID가 얼마나 바뀌는지 계산해 선택 민감도를 기술한다. 승자가 자주 바뀌면 절차 일반화 문구를 더 강하게 제한한다. 이 검사는 동결 후보를 다시 선택하거나 표적 결과를 이용하는 근거로 사용하지 않는다.

**남은 불확실성:** 반복 개발 없이도 이번 artifact의 실용적인 배포 우위는 발견할 수 있다. 선택 불안정성은 미래 개발 계보 분산의 직접 추정치가 아니며, 문서에 없는 수작업 비용이 실제로 비대칭이라고 단정하지 않는다.

근거:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L51–L57 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L63–L69 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L109–L109 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L8–L17 · SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`

### R4-05 · MEDIUM · null·negative·UNKNOWN 판정이 실제 설계 선택을 어떻게 바꾸는지 빠져 있다

**관측:** 통계 판정과 실패 보존 규칙은 잘 정의되어 있다. 그러나 prototype 항목은 모든 결과에서 같은 가설→실험→근거→다음 선택 시연을 적으며, R이 패배하거나 비슷하지만 더 비싸거나 M2에서 퇴행할 때 채택·수정·축소할 정책을 명시하지 않는다. 현재 objective는 결과가 prototype 설계를 결정해야 한다고 한다.

**왜 문제인가:** 분석 결과를 정직하게 보고해도 모든 결과가 동일한 R 구축으로 이어지면 연구가 설계를 선택하지 못한다. 불확실한 평균을 본 뒤 사후에 비용·진척·복구 이야기를 골라 채택 근거로 삼을 여지도 남는다. 반대로 좁은 과제의 negative 때문에 장기 연구 계열 전체를 폐기하는 것도 정당화되지 않는다.

**최소 수정:** 새 승인 체계 대신 내부 의사결정 표 한 개를 사전 고정한다. R의 효용 우위와 수용 가능한 실제 비용은 해당 과제·모델 범위의 채택 후보, B 우위는 B 중심 단순화, 차이가 작을 때는 사전 정한 유지비/운영 부담 기준, 넓은 CI나 UNKNOWN은 비교 결론 보류와 원인 분리, M2 퇴행은 M1 범위의 제한 채택으로 연결한다. 모든 경우 native 재개는 기존 사용자 승인 조건을 그대로 따른다. 논문에는 측정된 평가 기여와 미해결 장기 질문을 남긴다.

**저비용 반증:** ΔU의 양성/실용적 동등/음성/UNKNOWN, 비용 역전, M2 부호 역전을 담은 가상 결과 다섯 묶음으로 표를 점검한다. 결과가 달라도 전부 같은 R 구현으로 귀결되거나 UNKNOWN이 성공으로 바뀌면 연구→선택 연결이 실패한 것이다.

**남은 불확실성:** 실제 유지비·개입 비용의 우선순위는 아직 정해지지 않았다. 이 검토가 비용 상한이나 construction 재개를 승인하지 않으며, 불확실성을 이유로 본문에 없는 영구 중단을 요구하지 않는다.

근거:

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L89–L101 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L109–L117 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-to-prototype-objective.md` L5–L13 · SHA-256 `284aec4307c35bf542c15a19ae073d3f57d755c8794596900049f25493a127d9`

## 타당한 점

- 가중치 고정, 연구 산출물 개선과 하네스 개선 분리, B의 persistent tools·RLM·자율 전략 허용은 적절하다. 연구를 B/C/G나 skill 전이로 축소하지 않는다. (design-v1.md L7–19; design-v1.md L35–47; 위 design SHA와 동일)
- roster를 outcome 이전에 결정하고 별도 개발/선택/평가를 두며, 숨은 평가 결과를 최종 선택 뒤 공개하므로 결과를 보고 좋은 과제를 고르는 주요 경로를 막는다. metadata 이상의 데이터 검증을 완료했다고 주장하지 않는다. (design-v1.md L25–31; design-v1.md L51–57; design-v1.md L73–81; 위 design SHA와 동일)
- agent 실패와 trusted-scorer unknown을 분리하고 비용/실패를 보존하며, 작은 차이·불확실·유해한 결과를 명시한다. 이는 음성 결과를 감추지 않고도 유용한 package 비교를 가능하게 한다. (design-v1.md L85–101; 위 design SHA와 동일)
- 각 역할·retrieval·descendant 비용을 상한에 넣으므로 추가 사고·검색을 무료로 제공하는 설계는 아니다. 같은 상한의 package 효용을 추정할 수 있다. 다만 실제 비용 일치나 순수 근거 활용 기제의 효과는 별개다. (design-v1.md L47–47; design-v1.md L63–67; design-v1.md L99–109; 위 design SHA와 동일)
- SOTA·산업 추천 모델 재현·모든 미래 모델 적용·장기 과학적 발견을 주장하지 않는 경계는 타당하다. 새로운 architecture 없이도 엄격한 통제 비교와 실패 분석은 논문 기여가 될 수 있다. (design-v1.md L23–29; design-v1.md L103–109; 위 design SHA와 동일)

## 읽은 범위와 미확인 범위

아래 FULL_READ는 이 reviewer가 전체 파일을 읽었다는 뜻이다. PRIMARY_SECTION_READ는 보존 원문의 해당 연속 구간만 읽었다는 뜻이며, 원문 전체 읽기나 재현을 뜻하지 않는다. HASH_ONLY는 내용 검토 없이 무결성만 확인했다. 과거 source-evidence의 읽기 표시는 이번 reviewer의 읽기 실적으로 사용하지 않았다.

- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` · L1–117 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` · L1–56 · SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/task-roster.json` · L1–1042 · SHA-256 `e952968e594b2bd32ed10e6b8f9c3c0863f8e856490e41932fd333e3d388c691`
- **HASH_ONLY** `.planning/2026-09-09-research-design-four-reviews/packet-v1/power-sensitivity.json` · content not reviewed · SHA-256 `1b988beb5c3b591c119a10f7351bd60bfa2ad05341b0880930b7e7e0954a4d75`
- **HASH_ONLY** `.planning/2026-09-09-research-design-four-reviews/packet-v1/model-catalog-evidence.json` · content not reviewed · SHA-256 `082338d639597fbb5e6c0605e9be9ae05ed1d7747df3d6a3f7bf513e6dbfe525`
- **HASH_ONLY** `.planning/2026-09-09-research-design-four-reviews/packet-v1/openml-cc18-metadata.json` · content not reviewed · SHA-256 `065752575d30da0f4c0fff06a1bc797b449739028a4962cbcd8cc951105d63e6`
- **HASH_ONLY** `.planning/2026-09-09-research-design-four-reviews/packet-v1/openml-cc18-task-list.json` · content not reviewed · SHA-256 `a45f1a9394167f5882dbeed084f0ec633743f84fb05d4907d68fa2a2c513be6f`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/AGENTS.md` · L1–269 · SHA-256 `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/agent-brief.md` · L1–51 · SHA-256 `9663771bba9aa243f5ea9bc454bf2bf68337ebfee407ed442e8e9f1fb0e1cffe`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-to-prototype-objective.md` · L1–21 · SHA-256 `284aec4307c35bf542c15a19ae073d3f57d755c8794596900049f25493a127d9`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-decision-contract.md` · L1–56 · SHA-256 `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/README.md` · L1–87 · SHA-256 `d9563e13bb61244a5d7f649269196dea194191ecce47603b944f76f6eadb9755`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/decision-record.json` · L1–58 · SHA-256 `1c06fc00e493554d5f07a9490945fc2f284a1880ad3ee040e01b45d357d9fab6`
- **FULL_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/source-evidence.json` · L1–63 · SHA-256 `2665dfcf8e60499ebed10e53c7be3f27b139cf86bb5febcd8ee376a8e962fdde`
- **PRIMARY_SECTION_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt` · L314–430, L620–643, L729–740 · SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`
- **PRIMARY_SECTION_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt` · L110–258, L321–466, L580–705 · SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`
- **PRIMARY_SECTION_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt` · L1–940 · SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`
- **PRIMARY_SECTION_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.23552v1.txt` · L131–305, L412–431, L612–651 · SHA-256 `bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3`
- **PRIMARY_SECTION_READ** `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01622v1.txt` · L179–388, L437–569 · SHA-256 `4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985`

추가 작업 지침 읽기: `AGENTS.md`, `docs/argo/agent-brief.md`, `docs/argo/migration-state.json`, `.planning/2026-09-09-research-design-four-reviews/review-contract.md`, `.planning/2026-09-09-research-design-four-reviews/packet-v1-manifest.json`, `/Users/um-yunsang/.codex/skills/planning-with-files/SKILL.md`.

- No model/training/scoring or recovery experiment was run.
- No full-paper reread claim: only the primary sections in the read-scope manifest were examined; historical FULL_READ labels in source-evidence.json were not reused as reviewer reading authority.
- No PDF rendering, source implementation reproduction, live provider access/billing, isolation, quota enforcement, or independent scorer validation.
- No dataset labels, detailed ancestry/license/split verification, or raw OpenML metadata/task-list semantic audit; those original metadata files were hash checked only.
- No broad novelty literature search or current publication-status verification; missing-literature lookup belongs to reviewer 3.
- No independent rederivation of the randomization test, confidence interval, or power sensitivity; those are outside this skeptical lane.

## 작업 기록

- 완료: 계약·필수 파일 전체 읽기, 19개 해시 검증, 5개 원문 method/evaluation 구간 대조, 5개 지적과 최소 수정 작성.
- 완료: JSON 구조, 5개 지적의 필수 필드, 모든 evidence 경로·SHA·줄 범위·실제 읽기 범위 일치 검사. 모든 저비용 반증은 제안이며 실행하지 않았다.
- 작성 범위: 이 review.md와 review.json 두 파일. 코드·실험·데이터·원본 설계는 변경하지 않았다.
- The named docs/CODEX-NAVIGATION-GUIDE.md was absent.
- Planning-with-files was read and its phased recording adapted inside the assigned report files; shared session catchup and shared plan reads were omitted to preserve review independence and write ownership.
- One batched read and one broad source-navigation output were truncated; mandatory design/protocol/roster content was reread in bounded complete ranges. Findings cite bounded sections actually read.
