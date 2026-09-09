# 방법론·통계 독립 검토

판정: **REVISION_REQUIRED**. 연구 목적과 B/R package 비교는 유지 가능하다. 아래 4개는 고정 v1의 수정 가능한 사전 설계 문제다. 실행된 실험·P0·native 구현의 오류 판정이 아니다.

## 실질 지적

### MS-01 · HIGH · 고정된 20개 과제 평균에 대한 판정을 task 재표집 CI에 맡긴다

근거:
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L27–31; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. 과제를 outcome 이전에 고정하고 유한 benchmark 평균을 대상으로 정함
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L95–101; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. task 평균 차이, task-cluster bootstrap 및 CI 기반 실용 판정
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L30–38; SHA256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`. task bootstrap95%10k가 판정용 interval로 재기록됨

문제: 20개 task와 split을 고정한 평균 효과의 불확실성은 반복 episode 및 실제 배정 절차에서 생긴다. task를 replacement로 뽑는 bootstrap은 task 구성 자체를 바꾸며, 과제별 효과 이질성도 변동으로 포함한다. 이 분포를 고정 suite의 평균효과에 대한 95% CI라고 부를 coverage 근거는 제시되지 않았다. task 수를 독립 n으로 세는 것과 어떤 모집단/무작위성에 대해 CI를 만드는 것은 다른 문제다. 단순한 불확실성 요약이라면 가능하지만 그 lower/upper를 +/−0.02 채택·유해성·작은 차이 판정에 직접 쓰면 문제다. 항상 반보수적이라는 주장이 아니라, advertised estimand에 대해 판정 오차가 정당화되지 않았다는 지적이다.

최소 수정: 고정 suite 평균을 유지하고 stochastic episode/배정에 조건부인 평균효과 CI를 사전에 정한다. 예를 들어 80 episodes 수는 유지한 채 각 task의 fresh 4 slots 중 2개를 R에 배정하는 설계를 명시하면, task별 두 arm 표본분산을 사용한 보수적 Neyman 분산 Vhat = sum_t(s_Rt^2/2 + s_Bt^2/2)/20^2를 출발점으로 삼을 수 있다. 작은 표본 CI의 분포 가정·보수성·coverage 확인 범위는 명시해야 하며 자동 exact로 부르지 않는다. 현재 두 bundle에 한 번 배정하는 방식을 유지하려면 그 배정에 맞는 별도의 분산/CI 근거가 필요하다. task bootstrap은 과제 구성 민감도로 별도 보고하고 실용 판정에서 분리한다. 또는 task 모집단 estimand로 명시적으로 변경하되 현재의 finite-suite 문구와 표집 근거도 함께 고쳐야 한다.

저비용 반증/검사: 실험 전 작은 고정 outcome 표로 검토한다. task별 효과가 서로 다르지만 각 task 안의 모든 반복이 결정적인 상황에서 task bootstrap은 계속 넓어지는 반면 고정 suite 평균에는 episode 잡음이 없다. 반대로 task별 관측 평균은 같고 arm 내 반복 편차만 큰 표에서는 task bootstrap은 폭 0이 된다. 제안한 interval이 어떤 불확실성을 반영하는지 이 두 표로 구분한다. 이 검토에서는 해당 모의 실험을 실행하지 않았다.

남은 불확실성: 실제 episode 분산·실패 혼합분포·task 효과 이질성은 전혀 관측하지 않았다. 현재 CI가 실자료에서 과도하게 넓거나 좁을지는 단정하지 않는다. 제안한 분산 예시도 배정과 독립성 가정을 먼저 확정해야 한다.

### MS-02 · MEDIUM · exact sign-flip의 sharp null과 주 가설의 평균효과 null을 구분하지 않는다

근거:
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L9–11; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. H1은 M1에서 평균 U의 R 우위임
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L69–69; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. task마다 두 fresh bundle의 B/R 배정 제안
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L95–99; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. 2^20 exact label assignments와 confirmatory comparison 연결
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L31–36; SHA256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`. exact paired block sign-flip로 명시

문제: task마다 두 bundle의 라벨을 하나의 공정한 coin으로 교환한다는 해석이면 2^20 sign-flip은 그 배정 공간과 일치한다. 이 점 자체를 오류로 보지 않는다. 그러나 이 절차의 유한표본 exact 귀무가설은 모든 배정 단위에서 처치가 결과를 바꾸지 않는 sharp null이다. 과제·episode의 양/음 효과가 상쇄되어 평균만 0인 weak null과 같지 않다. 현재 H1은 평균효과이며 이질 효과를 금지하지 않는다. 별도 정당화 없이 exact p를 평균효과 검정의 exact 유의성으로 옮길 수 없다. MS-01의 CI 문제와 별개로 검정의 귀무가설을 명시해야 한다.

최소 수정: assignment unit을 task 안의 사전 생성 bundle, task를 block으로 명시하고 배정표를 고정한다. 현 sign-flip p는 Fisher sharp-null 결과라고 명시한다. 평균효과 및 MUE 판정은 MS-01에서 선택한 평균효과 interval에 맡긴다. 평균 0을 검정하는 별도 studentized 절차를 채택할 경우에도 유한표본 exact라고 부르지 말고 가정/근사 범위를 기록한다. 배정 방식을 바꾸면 permutation 공간도 같은 문서에서 함께 바꾼다.

저비용 반증/검사: 귀무가설 단위 점검: 일부 task/episode는 양의 효과, 다른 것은 음의 효과를 갖고 전체 평균만 0인 potential-outcome 표를 만든다. 이 표는 H0_mean을 만족하지만 H0_sharp를 만족하지 않는다. 이를 swap하여 만든 분포가 실제 배정 분포와 같다고 추론할 수 없는 이유를 분석 함수 설명에 적는다. coverage 검사가 필요하면 승인된 사전 통계 fixture에서 sharp-null과 zero-average heterogeneous-null을 따로 확인한다. 이번에는 이 fixture를 실행하지 않았다.

남은 불확실성: 실제 이질 효과가 얼마나 큰지 알 수 없다. 현 sign-flip이 실제 데이터에서 false positive를 냈다고 주장하지 않는다. 원저자가 sharp null만 검정할 의도였다면 문구와 평균효과 판정의 역할 분리로 수정된다.

### MS-03 · MEDIUM · 후보 선택의 유효 산출물 평균과 실패=0 endpoint가 다른 승자를 만들 수 있다

근거:
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L51–57; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. 후보를 선택 과제마다 한 번 실행한 뒤 유효 산출물의 U 평균으로 선택
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L85–91; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. primary U는 agent 원인 실패를 0으로 포함하고 모든 배정을 유지

문제: 55줄은 유효 산출물의 U 평균을 최대화한다고 쓰고, 87줄의 U는 agent 실패까지 0으로 포함한다. 선택에서 성공 run만 남기면 실제 목표인 배정당 효용을 최대화하지 않는다. 동일한 네 선택 과제에서 후보 A가 [0.95,0,0,0], 후보 B가 [0.80,0.80,0.80,0.80]이면 valid-only 평균은 A를, 전체 U 평균은 B를 고른다. 따라서 두 구현 모두 현재 문구를 따랐다고 주장하면서 다른 B/R 후보를 동결할 수 있다. 최종 held-out 비교가 자동으로 누수되었다는 뜻은 아니며, 선택 절차의 목적과 재현성이 불명확하다는 문제다.

최소 수정: 선택 점수를 정확히 U_selection = sum(U on all 4 assigned selection tasks)/4로 쓰고 agent failure=0, scorer unknown은 선택 보류라는 기존 원칙을 그대로 적용한다. 성공 artifact만의 평균은 보조 값이라고 분리한다. 동률 및 token tie-break는 이 전체 분모 점수에만 적용한다.

저비용 반증/검사: 위 두 후보의 4-element 표와 all-failed 후보를 선택 규칙에 넣었을 때 B가 선택되고 all-failed도 분모 4로 남는지 확인한다. 이는 모델·데이터가 필요 없는 선택 규칙 단위 예시이며 이번에는 실행하지 않았다.

남은 불확실성: 의도가 이미 모든 U를 포함하는 평균이었다면 한 문장 명료화로 해소된다. 현재는 실제 selector 코드가 없으므로 valid-only 구현 결함을 관측한 것이 아니다.

### MS-04 · MEDIUM · worker의 dev 접근과 12회 dev 평가 상한 사이의 자료 경계가 빠져 있다

근거:
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L31–35; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. 내부 train/dev 분할 및 공통 자료·코드 도구 접근
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L63–65; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. dev score 최대 12회를 자원 상한으로 제안
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L73–77; SHA256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`. worker mount는 train/dev와 corpus, 명시적 label 차단은 test에만 있음
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L18–28; SHA256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`. dev_calls 12가 배포 조건으로 고정

문제: 제안된 mount가 dev features와 labels를 모두 제공하는지 불명확하다. 제공한다면 자유로운 REPL/생성 코드는 trusted score 호출 없이 dev 예측과 balanced accuracy를 반복 계산하거나 dev label을 학습에 섞을 수 있다. 따라서 12번의 dev feedback이라는 조건은 broker 호출 카운터만으로 집행되지 않는다. 최종 outer test labels를 숨긴 설계는 여전히 별개로 유효할 수 있으므로 이 지적을 최종 test 누수의 관측으로 확대하지 않는다. 문제는 동일하게 제한한 연구 기회와 dev 근거의 의미가 구현에 따라 달라진다는 점이다.

최소 수정: worker에는 inner-train X/y와 dev X만 주고 dev y는 trusted evaluator에 둔다. candidate의 고정 code/prediction을 evaluator가 받아 scalar/허용 진단을 돌려주며, dev label을 소비하는 모든 요청을 12회 ledger에 포함시키는지 실패 요청까지 포함한 계수 규칙을 명시한다. outer-train 전체 refit에서 dev y를 쓰는 것은 최종 lock 후 trusted finalizer의 한 번 작업으로 구분한다. dev y 공개가 의도라면 12회를 공식 scorer 호출 상한으로 한정하고 모든 내부 dev 평가가 제한되었다는 표현을 제거한다.

저비용 반증/검사: 승인된 apparatus fixture에서 worker view만 사용해 두 후보의 dev BA를 로컬 계산할 수 있는지와 13번째 dev-label 소비 요청이 막히는지 확인한다. 외부 네트워크/credentials나 실제 benchmark labels 없이 가짜 자료로 충분하다. 이번 검토에서는 이 실행 검사를 수행하지 않았다.

남은 불확실성: mount와 scorer 구현은 아직 제출되지 않았다. 이미 dev y가 비공개인 apparatus를 만들 예정이라면 데이터 접근 표 한 항목과 계수 규칙으로 해소된다. 실제 무단 평가나 정보 유출을 관측하지 않았다.

## 타당한 설계 요소

- B에도 같은 persistent substrate, 자료, 도구, 위임 권리를 주고 R의 추가 role/context 비용을 포함한다. 효과를 전체 운영 package로 한정하므로 개별 graph 효과라고 과해석하지 않는다.
- 개발/선택/평가 task를 분리하고 평가 전에 하네스를 고정한다. public-data 사전학습 노출을 완전히 제거했다고 주장하지 않는다. selection noise 자체는 held-out 평가 누수가 아니다.
- U는 accuracy와 유효 산출물 제공 확률을 결합한 operational utility라고 정의한다. 성공률과 유효 모델 정확도를 별도 보고하는 조건에서 agent failure=0은 원칙적으로 일관된다.
- trusted scorer/원인 미확정 failure는 unknown으로 유지하고 원시 ledger 및 bounds를 남긴다. unknown 존재 시 확증을 유보하는 규칙은 보수적이며 missing-at-random을 가정하지 않는다.
- M1만 confirmatory로 두고 M2를 보조로 분리하며 optional sample-size 증가를 금지한다. power-sensitivity는 zero-null normal approximation의 가정 예시로 명확히 제한했고 MUE 판정 power라고 주장하지 않는다.
- same seed를 같은 LLM 궤적으로 보지 않고 provider cache 사용량, 모델 revision, fresh context와 run outputs 분리를 요구한다. 모델 context 독립성을 OS 격리나 오류 독립성으로 주장하지 않는다.
- 90분/12회가 실제 장기 의존 연구를 발생시키지 않으면 bounded iterative ML experimentation으로 해석을 낮추겠다는 제한이 있다.

## 확인 범위

- 19개 packet 파일의 live SHA256가 frozen manifest와 일치함.
- design 117 LF lines, protocol 56 LF lines, roster 1042 LF lines의 모든 JSON 값, power 30 LF lines를 모두 읽음. 첫 병렬 출력 truncation 이후 누락된 protocol과 roster 전체 내용을 재조회함.
- roster 4/4/20/11 counts, retained data_id 및 family 유일성, hash order, 모든 retained row의 고정 salt SHA가 일치함.
- 실제 데이터 labels, model 호출, scorer 실행, 학습, 통계 모의 실험, 코드/환경 설치를 하지 않음.

원문 읽기: HarnessDev 원문 일부(명시 범위)와 검색 일치 줄만 탐색적으로 읽었다. 원문 전체 읽기·PDF 시각 확인·논문 실험 재현을 주장하지 않는다. 이번 지적은 packet 설계의 논리와 분석 규약에 근거하며 선택 원문의 수치·효능 주장을 증거로 사용하지 않는다. 다른 4편은 hash만 검증했다. source-evidence.json의 이전 full-read 상태를 이번 reviewer의 읽기 상태로 계승하지 않았다.

전체 읽기/부분 읽기/해시만 확인 상태와 19개 파일의 정확한 SHA 및 읽은 줄 범위는 `review.json.read_scope`에 기록했다.

검토 독립성: 동료 보고서를 읽거나 연락하지 않았고 중첩 위임도 하지 않았다. 이 세션의 기본 memory quick-pass에서 과거 ARGO 레지스트리 제목·요약이 노출됐지만 과거 rollout/검토를 열지 않았으며 과거 결론을 판단 근거로 쓰지 않았다. 독립 model context는 OS 격리나 오류 독립성의 증명이 아니다.

작업 지침: planning-with-files 스킬을 읽었다. 지정된 두 파일 외에는 작성하지 않았고 이전 세션 catchup은 사용하지 않았다. live migration-state는 권한 확인용으로 읽었다. 지시된 `docs/CODEX-NAVIGATION-GUIDE.md`는 경로에 없어 읽지 못했다.

미확인 범위:

- runtime B/R prompts, tools, images, seeds, model credentials/access or resolved revision
- actual deployment isolation, cache implementation, host/time scheduling and budget enforcement
- task provenance ancestry, licenses, labels, outer split custody, row/group leakage in dataset bytes
- scorer/refit code, endpoint failure-cause mapping and retry implementation
- empirical variance/power, statistical coverage simulation, final model scores, performance or SOTA
- full contents of retained five papers, external missing literature, other reviewer verdicts

진행 상태: 계약·전체 대상 읽기, 통계/누수 검토, 보고서 작성, 입력 SHA와 출력 정합 검사 모두 완료. 검사는 문서·메타데이터 무결성 범위이며 실행·성능 검증이 아니다.
