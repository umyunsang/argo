# Fable 5.1 재검토 — 수정된 통합 장기 자율연구 설계 (re-review-01)

- 검토 commit: `ee7e0fdaf23353c094b1a872b564d82fa234bfc7` (immutable; 모든 입력은 `git show <commit>:<path>`로 읽음). 수정 통합 commit `fb4e597e14a11956d832d99ff38f130de742323e`, 이전 Fable 검토 commit `f2e203058eedd4bbf5af2674fcc77d6013d5437b`. 세 commit의 조상 관계(f2e2030 → fb4e597 → ee7e0fd)를 `git merge-base --is-ancestor`로 확인했다.
- 요청: `paper/research/fable51-design-review-20260907/re-review-01/request.json` SHA-256 `3e4df497b789fee87c6e74554d951f339f8e9beb26439e8fb6c52c44a99ac907` (일치). 요청의 22개 `input_hashes`를 검토 commit의 git blob에서 재도출해 전부 일치함을 확인했다. 작업 트리의 다른 미커밋 변경은 사용하지 않았다.
- 순서: (1) ROOT, active design, mechanism map, fable51 `integrated-study-design.json`, `research-completion-contract.json`을 전문으로 읽고 독립 판단을 먼저 기록 → (2) 이전 Fable review.md/review.json, root `finding-response-matrix.json`, `review-synthesis-ko.md`, `intake.json`, 5인 integration 5개 JSON, prior-art-rebinding 일부 → (3) next/handoff/graph는 의미 충돌 확인에 필요한 절만, `immutable-validation.json` 전문, 저장 원문 두 span을 byte로 재확인. 새 문헌·네트워크·실행·subagent·설치 없음.
- 원칙: 검토자 동의 인원과 root 문구('addressed')는 종결 증거가 아니다. 설계 종결(design closure)과 프로토콜/실증 종결을 분리해 표기한다. 이 검토의 어떤 판정도 실행·설치·원고·native 재개 권한이 아니다.

## 0. 판정 요약

| 항목 | 판정 |
|---|---|
| 전체 verdict | **READY_FOR_TASK_QUALIFICATION** (조건부; 아래 §6의 설계 문장 N2–N6와 사용자 결정 N1을 RD4a-pre 검토 전에 닫는 조건. 실행 권한 아님) |
| 설계 적정성 | **ADEQUATE_WITH_CONDITIONS** — 연구 질문, B/C/G package 식별, 단계 P0/P1/P2와 RD4a-pre/RD4a-dev/RD4b, 결측·봉인·블록 원칙, apparatus 계층, R1/R2 개념은 정합적이다. 남은 것은 새 개념 검토가 아니라 dataset과 무관한 설계 문장 다섯 개(선택 주체, gate 집행 locus, R1/R2 기계 규칙, MUE 확정 시점, 결측 locus)와 apparatus 구현 권한에 대한 사용자 결정이다. |
| task/protocol qualification 준비도 | **READY** — 공개 ML programme/scorer/ancestry 적합성 연구와 task-bound apparatus·arm·missingness 명세는 지금 시작할 수 있다. 위 문장들은 그 task-bound protocol revision 안에서 함께 닫으면 되며 또 한 번의 일반 설계 검토는 필요하지 않다. 다음 검토는 task-bound P0 protocol 검토여야 한다. |
| 실행 준비도 | **NOT_READY** — 인증 task 0, runnable arm 0, integrated efficacy 0, primary 6·resource 10·analysis 5·arm_deltas 3행·phase envelope 3·bounded_closure 2 등 수치 필드 null, 세 phase 권한 모두 미승인. 이는 문서가 정직하게 인정한 상태이며 새 결함이 아니다. |
| 치명적 개념 blocker | **없음.** 아래 MAJOR 항목은 모두 한두 문장의 설계 결정 또는 사용자 권한 결정이며, task 선정 없이도 지금 내릴 수 있고 P0 protocol이 어차피 강제하는 결정이다. |

핵심 메시지: 이번 수정본은 이전 Fable F1–F14를 실제로 설계에 반영했고, 이전 Fable 처방 중 네 가지(whole-block INFRA_VOID 기본 제외, event 없으면 G−C≈0 사전등록, 로그로 기제 귀속, 채택 규칙의 미분류 영역)는 root가 타당한 이유로 기각·교정했다. 나는 그 기각에 동의한다. root가 F2/F4/F5/F7/F13을 검증 불가능하거나 미결정 상태로 과잉 한정했다고 보지 않는다: 모집단·contrast·비교군은 '미정'이 아니라 '기록된 규칙으로 P1 뒤 동결'이라는 2단계 결정이고, 각 결정 시점이 RD4a-dev/RD4b에 묶여 있다. 다만 R1/R2와 의무 gate는 정의는 있으나 자율 실행 안에서 집행·탐지될 locus가 없어 아직 '실행 가능한 형태'가 아니다(N2, N3).

## 1. 독립 판단 (root 반박을 읽기 전에 기록)

- 주 estimand: efficacy형(lock된 단일 artifact의 hidden 성과)으로 읽히며, 원인 3분류(scientific/protocol/infra)와 treatment-blind 판정은 개념적으로 정해졌다. 숫자 floor는 metric 의존이므로 null이 정당하다. 다만 utility-floor 문장이 primary에 섞여 읽히고(N6), artifact 선택 주체가 미정이다(N5).
- R1/R2: 등급 정의와 anti-evasion은 있으나, R2가 허용 공개 입력을 로컬로 읽는 이상 REPL fit은 물리적으로 가능하다. 경계는 기계적 기준과 lineage 검사로만 성립한다(N3).
- C/G의 'not prompt-only' 의무 gate: native 변경 금지 아래 열린 REPL에서 project-local guard는 우회 가능. 집행 locus를 R1 launch/lock 지점으로 두면 성립한다(N2).
- arm_deltas의 null 3행(prompt/capsule/receipt)은 동일 ceiling 정책이 이미 진술돼 있으므로 task-bound 값이다. 정당한 null.
- 단계·권한: P0→P1→P2, 각 phase 별도 계약·수치 envelope·승인, 실패/ceiling 시 분석·범위 결정 없이는 ResearchDone/원고 gate가 열리지 않음. 실제로 유한하고 순서가 맞다.
- apparatus: lifecycle owner를 추가하지 않고 native pause를 재정의하지 않는다. 그러나 apparatus '구현' 권한은 어디에도 없다(N1).

## 2. F1–F14 설계 종결 매트릭스

판정 어휘: DESIGN_RESOLVED = 개념 선택이 내려졌고 문서 간 일관되며 task-specific 값만 남음 / PARTIALLY_RESOLVED = 개념은 다뤘으나 task와 무관한 설계 공백이 남음 / OPEN / REJECTED_WITH_VALID_REASON. 프로토콜·실증 종결은 전부 미완이며 표의 '잔여' 열에 적는다.

| F | 제목 | 설계 종결 | 설계 근거 (commit bytes) | 잔여(프로토콜/실증/사용자) |
|---|---|---|---|---|
| F1 | Research apparatus tier undefined | **DESIGN_RESOLVED** | ISD /apparatus (status, role, candidate_components, fixed_native_owners, prohibited, before_implementation, owner_realization 12 rows); active L97; mmem L77 | 구현 권한(사용자 결정, N1), 실제 파일/owner/code·prompt·env hash와 protocol fingerprint(프로토콜), runnable arm 0(실증) |
| F2 | Primary outcome vs G mechanism SNR | **DESIGN_RESOLVED** | ISD /challenge_design (primary_population UNSELECTED, selection_rule, schedule_if_used, same_observation_rights, source_scope, secondary_rule); active L100 | P1이 어떤 모집단 변형을 screen하는지와 outcome-blind 선택의 조작적 정의(누가 무엇을 masked 상태로 판단하는가)는 P1 프로토콜 항목; P2 primary 모집단 동결은 RD4b |
| F3 | R1/R2 run-class boundary | **PARTIALLY_RESOLVED** | ISD /run_classes (R1, R2, derived_metrics, decision_lineage, local_journal, backend_exception); active L98; mmem L79 | 기계적 분류 규칙과 집행/탐지 locus 부재(N3). '/run_classes/derived_metrics'의 'classified before execution'은 자율 실행과 양립하지 않음. |
| F4 | Infra UNKNOWN differential missingness | **DESIGN_RESOLVED** | ISD /missingness_policy (census, no_automatic_post_assignment_exclusion, before_randomization, after_assignment, protocol_invalid, scientific_failure, reconciliation, historical_record); active L101; ROOT L68 | metric별 floor 숫자·bounds 방식은 task 프로토콜; primary missingness의 locus 문장(N6)은 설계 문장 한 줄 |
| F5 | Access-hidden vs knowledge-hidden; single-operator sealing | **DESIGN_RESOLVED** | ISD /sealing (before_development, commitment_vs_confidentiality, hidden_scorer, contamination, single_operator_limit, confirmation_freeze); active L102 | 실제 commitment/custody/access/reveal receipt, 오염 진술, 선택 task의 split 출처(프로토콜/실증) |
| F6 | Block/paired design and variance components | **DESIGN_RESOLVED** | ISD /analysis (blocking, nested_randomness, estimators, precision_plan); active L102 | MUE 확정 시점(N4)은 설계 문장 한 줄; 분산성분 값·n·반복 수는 P0/P1 산출 |
| F7 | Operational B/C/G deltas | **PARTIALLY_RESOLVED** | ISD /arm_deltas (common 5, table 6 axes 중 3 axes 채움, logging, claim_limit); active L99 | C/G 의무 gate의 집행 locus와 우회 탐지(N2)는 task-independent 설계 항목; prompt/capsule/receipt 3 axes null은 task-bound로 정당 |
| F8 | First-class feasibility outcome | **DESIGN_RESOLVED** | ISD /stages/0 (P0, distinct from SAB Stage 0, results, authority RD4a-pre); RCC /bounded_closure/P0_failure; mmem L81 | task-specific 완주 정의, P0 측정 항목에 R1 latency/UNKNOWN/우회 발생률 명시(N10), 숫자 ceiling |
| F9 | Inconclusive prototype default and resume-gate coupling | **DESIGN_RESOLVED** | RCC /prototype_inconclusive_rule, /PrototypeReadiness_separate[2]; ISD /decision_rule_options/prototype; active L104 | 측정된 후보 집합 자체(실증); decoupling 사용자 결정 여부는 사용자 항목 |
| F10 | RD4 split into phase authorities | **DESIGN_RESOLVED** | RCC /ResearchDone/3 subgates, /phase_authorities RD4a-pre·RD4a-dev·RD4b; ISD /stages authority 필드 일치 | requires에 invalid/missingness/retry 규칙 누락(N7, 사소) |
| F11 | Two-part RQ, one primary | **DESIGN_RESOLVED** | ISD /challenge_design/secondary_rule; active L100 마지막 문장 | 없음(통계 endpoint는 task 후) |
| F12 | Human-adaptation leakage / confirmation family sealing | **DESIGN_RESOLVED** | ISD /sealing/before_development, /sealing/confirmation_freeze | 실제 ancestry certificate·sampling commitment·custody receipt(실증); P0 programme ancestry의 dev-side 선언(N9) |
| F13 | External comparator (Arbor) role | **DESIGN_RESOLVED** | ISD /comparator (primary, C_vs_G, Arbor_external_anchor) | 문구 과잉(N8, 사소); 실제 사용 여부는 별도 승인 |
| F14 | 4/2/1 template status | **DESIGN_RESOLVED** | ISD /challenge_design/suggested_template | 과제별 horizon certificate(프로토콜) |

보충:
- F1: lifecycle owner를 추가하지 않고 native pause를 재정의하지 않음을 확인. 'journals reference receipts and do not add lifecycle registries'와 prohibited의 'new process supervisor'가 F1의 핵심 우려를 닫는다.
- F2: 이전 Fable의 'event 없으면 G−C≈0' 사전등록 문장과 event-inclusive 기본값 처방은 PA-NULL L456–457의 범위를 넘어선 과잉 추론이었다. root 반박이 옳다. 다만 F2의 핵심(기제 발화 관측 가능성과 잡음 대비 MUE를 dev에서 확인)은 설계에 남아 있다.
- F3: anti-evasion 문구('Small or local does not exempt')는 옳으나 R2가 허용 공개 입력에 로컬 접근하는 이상 준수 규칙이지 경계가 아니다.
- F4: 이전 Fable의 whole-block INFRA_VOID 기본 제외 처방은 root가 타당한 이유로 기각했다(launch 수가 treatment 의존이면 block 삭제도 post-treatment selection). 문제 자체는 수용·재설계됨.
- F5: root가 hash=변경탐지, custody 별도, 단일 운영자 한계 기록으로 이전 처방보다 엄격하게 닫았다.
- F6: '두 시작은 안정된 power 근거 아님', '같은 seed≠결합 궤적'은 옳다.
- F7: 'not prompt-only' 약속은 현재 기존 REPL 기질 위에서 어떻게 집행되는지 근거가 없다. 로그=발화 증거 한정은 옳다.
- F8: P0 성공이 P1/P2 권한을 상속하지 않고, 실패가 원고 gate를 자동 열지 않는 구조를 확인.
- F9: '가장 저렴한 arm 자동 기본값' 기각은 타당(C만 측정하면 B/G 비용 추론 불가).
- F12: custody 없이는 hash가 blindness가 아니라는 root 한정이 옳다.
- F13: 이전 Fable 자신의 입장(non-causal external anchor, optional)과 일치한다.

F4의 처방(whole-block INFRA_VOID 기본 제외)과 F2의 처방(event-inclusive 기본값·'event 없으면 0' 문장), F7의 '로그로 귀속', 이전 채택 규칙은 **REJECTED_WITH_VALID_REASON**이다. 해당 finding의 문제 자체는 다른 기제로 수용됐으므로 finding 단위 판정은 위 표대로 둔다.

## 3. root 반박 판정

| 주제 | root 입장 | 판정 | 이유 |
|---|---|---|---|
| post-assignment whole-block INFRA_VOID deletion | 기본 규칙으로 기각; 배정 분모·UNKNOWN·비용 보존, 원인 3분류, bounds/sensitivity 또는 식별불가 보고; complete-case는 감도분석 | **CORRECT** | launch 수가 arm에 의존하면 '어느 arm이든 UNKNOWN이 있는 block'의 제외 확률이 arm 활동량에 의존하고, 활동량이 block 내 효과와 상관이면 평균 대비 효과 추정이 편향된다. 이전 Fable 처방은 post-treatment 조건화였다. 다만 (i) 중간 launch UNKNOWN은 arm의 ceiling 안에서 소비된 process 사건이지 primary 결측이 아니며, (ii) primary 결측은 최종 artifact가 유효 채점되지 못한 경우로 한정되고, (iii) scorer-run UNKNOWN(arm당 1회, 비차등)과 campaign-run UNKNOWN(차등)을 구분해야 한다는 문장이 아직 없다(N6). |
| PA-NULL and zero-effect-without-events / event-inclusive primary | PA-NULL은 nanoGPT 하네스 비교의 잡음 관측일 뿐 G−C=0의 증거가 아님; 모집단은 UNSELECTED, outcome-blind 적합성·잡음·비용으로 확정; 효과가 큰 event를 골라 잡지 않음 | **CORRECT** | 직접 읽은 2608.23552v1-layout.txt L452–457은 세 모델×(Prime Agent vs 대체 하네스)에서 'the choice of harness has little effect on final records compared to the noise of the experiment'를 말하며, 비교 대상은 하네스 전체이지 graph-control package가 아니다. 2606.11926/main.tex L823–826은 exogenous event 없이도 tree/insight 제거가 22개 task Any Medal 81.82→63.64/54.54%로 떨어짐을 author-report한다(단일 backbone, 반복 수 미기재). 두 span 모두 로컬 효과나 power prior가 아니다. 따라서 'event 없으면 0' 사전등록 문장은 과잉이었고 root 반박이 옳다. 남는 것은 P1에서 어떤 모집단 변형을 실제로 screen할지와 outcome-blind 선택의 조작적 정의다. |
| hash commitments vs custody/operator blindness | hash는 변경 탐지; custody/access/reveal log 별도; 단일 운영자 한계 기록; hash만으로 blinded라 부르지 않음 | **CORRECT** | 이전 Fable 처방(hash commitment + hidden-open log)보다 엄격하고 정확하다. 남는 것은 실제 receipt다. |
| shared contamination-policy interaction | 공통 오염이 policy와 상호작용할 수 있어 '모델 일치=불편 contrast'를 채택하지 않음; canary는 부재 증명이 아님; 공개 test 금지는 아님 | **CORRECT_SEMANTIC_ONLY** | 이전 Fable은 내적 타당성(오염이 arm 공통이라 contrast 자체는 편향되지 않으나 효과가 축소됨)을, root는 외적 타당성(오염 모집단에서의 효과가 비오염 효과와 다름)을 말한다. 두 진술은 양립하며 실질 이견이 없다. root 입장이 공개 task를 검증 불가능하게 만들지는 않는다(재분할/사후 데이터 검사와 진술을 요구할 뿐). |
| usage logs vs causal mechanism attribution | 로그는 발화 관측; representation/computation/context 인과 분리는 별도 ablation 필요; 기본 주장은 package 수준 | **CORRECT** | 이전 Fable의 '로그가 해석을 주면 passive arm 불필요'는 활성화 관측과 매개 추론을 혼동할 여지가 있었다. root가 package-level claim으로 한정한 것이 옳고, 이는 설계를 미결정으로 만들지 않는다(package contrast는 그 자체로 결정 가능). |
| R1/R2 boundary incl. selection/hidden scoring under ORX and small/sanity training loophole | 학습·후보 생성·선택 평가·hidden scoring=R1(ORX); bounded 분석=R2(receipt); small/local 면제 없음; 경계 사례는 실행 전 분류; backend 예외 미도입 | **PARTIALLY_CORRECT** | 정의와 anti-evasion은 옳다. 그러나 (i) R2가 허용 공개 입력을 로컬에서 읽는 이상 REPL에서 fit은 물리적으로 가능하므로 규칙은 준수 의무이지 경계가 아니고, (ii) 'Borderline cases are classified before execution'은 자율 실행 중 사람이 매 계산을 사전 분류한다는 뜻이 되어 연구 대상(자율연구)과 양립하지 않는다. 기계적 기준과 탐지 locus(선택 결정의 lineage 검사 + 데이터 custody 진술)가 필요하다(N3). 우회 의도는 없으나 실행 가능한 형태가 아직 아니다. |
| variance components / MUE | programme block·순서 무작위화·within/between 구분·few-cluster fragility 보고; 두 시작은 power 근거 아님; MUE는 과학/실용 가치로, noise에 맞춰 낮추지 않음 | **CORRECT** | 모두 타당. 누락은 MUE 확정 시점이다: P1 arm contrast 비맹검 후 정하면 관측 효과에 맞춘 조정이 가능하다(N4). 이것은 노이즈에 맞춘 하향뿐 아니라 상향 조정도 포함한다. |
| automatic C feasibility / C-G confirmation / cheapest prototype | 권고로 보존, 자동 채택 거부; fallback은 측정된 feasible/safe 후보 내에서만; C만 측정하면 B/G 추론 불가 | **CORRECT** | reviewer 권고를 자동 규칙으로 승격하지 않는 것이 옳다. 이는 설계를 미결정으로 만들지 않는다: P1 종료 시 기록된 규칙으로 후보·비교군을 동결하도록 RD4b가 요구한다. |
| optional external comparator (Arbor) claims | 별도 승인된 서술적 whole-system anchor; graph-control 단독 귀속 불가; 이 연구는 randomized 외부 비교나 SOTA 주장을 주지 않음; 다만 다른 substrate라도 randomization이 있으면 whole-system causal 추론이 불가능한 것은 아님 | **CORRECT_WITH_WORDING_OVERREACH** | 원칙적으로 옳다(randomized whole-system 비교는 인과적일 수 있다). 그러나 본 연구에 그런 randomization이 없으므로 ISD /comparator/Arbor_external_anchor의 'not all possible causal system-level inference'는 이 연구 범위 밖의 문을 열어 두는 문구다. '이 연구에서는 서술적 비교만'으로 좁혀야 한다(N8). |
| root critique of previous Fable adoption rule (decision_rule_options) | '하한>0 & 점추정≥MUE'는 효과≥MUE의 근거가 아니며, 구간 영역 일부가 미분류; 완전·상호배타 결정표 요구 | **CORRECT** | 이전 review.json recommendation.adoption_rejection_rule을 직접 확인했다. 하한>0이고 점추정<MUE이며 상한≥MUE인 경우는 채택·기각·inconclusive 어느 규칙에도 속하지 않았고, 채택 조건은 '양의 효과'와 '≥MUE'를 혼동했다. root 지적이 옳고 개선이다. |

문헌 의존 판정에서 실제로 읽은 span: `paper/research/long-horizon-harness-benchmark-20260907/sources/2608.23552v1-layout.txt` L441–470 (text SHA-256 `5454486c…d694b` 일치; L456–457 'We find that the choice of harness has little effect on final records compared to the noise of the experiment', L458–470은 하네스가 행동만 바꿨다는 서술), `paper/sources/tex/2606.11926/main.tex` L819–835 (SHA-256 `dec929a1…27cd0` 일치; L823–826 ablation 서술, 81.82/63.64/54.54% Any Medal) 및 같은 파일에서 'MLE-Bench Lite' 문맥 검색(L183, 220, 227, 577, 587, 612, 630, 688, 719–722, 742, 763, 787, 992; 22개 task, Claude Opus 4.6 backbone, 실제 연구 task는 Avg@3, ablation 반복 수는 읽은 범위에서 미기재). 두 span 모두 author-reported이고 로컬 효과·power prior가 아니다. 전문 재독은 하지 않았다.

## 4. 추가 검토 항목

### 4.1 apparatus 계층이 실제로 유한한 다음 단계를 만드는가
만든다. ISD `/apparatus`는 기존 Prime 세션/REPL/RLM 위의 폐기 가능한 project-local 계층으로 한정하고, `fixed_native_owners`에서 process/session은 Prime, R1 lifecycle은 ORX가 유지하며 journal은 receipt를 참조만 한다고 명시한다. `prohibited`의 'new process supervisor', 'native daemon/API/TUI changes'와 owner_realization 12행은 F1의 '무한 준비 루프' 우려를 닫는다. native pause를 재정의하지 않는다. 그러나 이 계층을 **구현할 권한**은 문서에서 도출되지 않는다. ROOT L52의 허용 범위('사전 승인 범위의 로컬 정적 검증')와 ISD `/next_actions/2`('implement only justified bounded static fixtures')는 policy module·adapter·scorer 코드를 덮지 않는다. **정적 fixture를 넘는 task-local 코드를 쓰기 전에 사용자 결정이 필요하다(N1).** 이 결정은 task qualification 문서 작업을 막지 않는다.

### 4.2 P0/P1/P2와 RD4a-pre/RD4a-dev/RD4b
- 순서·상속: RD4a-pre→P0, RD4a-dev(P0 disposition 필요)→P1, RD4b(P1 closed·후보/비교군 동결 필요)→P2. 'No phase inherits later execution authority'가 명시돼 있고 ISD `/stages[*].authority`와 RCC `/phase_authorities` id가 일치한다.
- feasibility 완료 대 연구/원고 gate: `/bounded_closure/P0_failure`는 ceiling에서 닫고 원고 gate를 자동으로 열지 않으며 feasibility-only 논문은 사용자 범위 결정을 요구한다. `/P1_or_P2_ceiling`은 예산 소진만으로 ResearchDone/writing을 열지 않는다. 보수적이고 유한하다. feasibility-only 논문을 위한 RD 변형은 계약에 없는데, 이는 결함이 아니라 '새 범위 결정 → 새 계약'이 요구된다는 뜻으로 읽는 것이 맞다.
- 독립 선택 task와의 호환: programme=block, 모든 arm 동일 block, P2는 별도 source-ancestry programme. task가 외부 규칙으로 선택되더라도 설계는 그 위에 적용 가능하다. 단, P0 programme의 ancestry가 P2에서 제외된다는 문장이 없다(N9).
- 수치 envelope null·repair 횟수 null: 정당하다. reviewer 하한을 발명하지 않은 것이 옳다.

### 4.3 successor와 유지된 predecessor 지침의 실제 충돌
- `git diff f2e2030..ee7e0fd`로 세 md 문서는 추가만 있고 삭제가 없음을 확인했다. predecessor JSON 5개의 해시는 변경되지 않았다.
- 규범 충돌은 찾지 못했다. successor가 명시적으로 재진술한 항목(challenge_design, RD4 분할, PrototypeReadiness의 DeepVoice/native 조건)은 precedence 문구로 우선한다. disagreement-resolution R-HORIZON('자연 적합성 평가, 합성 편집 강제 금지')과 successor의 UNSELECTED 모집단은 양립한다.
- 퇴행 한 건(사소): predecessor RD4가 요구한 'invalid/retry' 계약이 RD4a-dev/RD4b requires에서 빠졌다(N7). 포인터 정체(active L18/L20이 predecessor ISD/RCC를 '현재'로 표기, ROOT §2 목록에 현행 문서 부재)도 N7에 묶는다.
- next/handoff/graph: `next-experiment-manifest.json` current_frontier·next_zero_cost_actions, `active-graph-handoff-manifest.json` status·current_allowed_next_action·active_chain(13 node/15 edge), `paper/context-graph.json`의 fable51 4개 node를 확인했다. ISD/RCC와 의미 충돌 없음. `openresearch_blocker.last_run`의 stale running 기록은 historical warning으로만 표기돼 있으며 현재 발생률 주장이 아니다.

### 4.4 null 필드가 개념 선택을 가리는가
대부분 아니다. metric/aggregation/floor 숫자/effect_threshold 값/resource envelope/families/repeats/prompt·capsule bytes는 task 선정 후 채우는 것이 맞다. `primary.contrast` null은 '미결'이 아니라 P1 뒤 기록된 규칙으로 동결하는 2단계 설계다. 예외로 dataset과 무관한데 null 뒤에 숨어 있는 개념 선택이 세 개 있다: artifact 선택 주체(N5), MUE 확정 시점(N4), primary 결측 locus(N6). 모두 한 문장으로 닫힌다. 여기서 dataset 부재를 새 이론적 blocker로 부르지 않는다.

### 4.5 root가 F2/F4/F5/F7/F13을 검증 불가능하게 과잉 한정했는가
아니다. (F2) 모집단은 RD4b 전에 outcome-blind 규칙으로 고정되며 고정 후 검증 가능하다. (F4) bounds/비식별 보고는 정직한 결과 범주이며 inconclusive 종결이 계약에 있다. (F5) 단일 운영자 한계는 주장 등급을 낮출 뿐 실험을 막지 않고 공개 test도 금지되지 않는다. (F7) package-level 주장은 그 자체로 결정 가능하다. (F13) 선택 항목이라 영향이 없다. 유일한 과잉 문구는 Arbor anchor의 인과 여지(N8)다.

### 4.6 byte validation이 보여 주는 것과 보여 주지 않는 것
`immutable-validation.json`은 clean clone에서 navigation/relations/all-projection validator(845 node·1416 edge·646 projection path)와 19개 파일 해시, 두 frozen receipt 불변, 보호 파일 불변만 확인한다. 이는 문서·계측 증거다. methods·task·runtime·power·hidden isolation·efficacy를 인증하지 않는다고 스스로 밝히고 있으며 내 판단도 같다. 현재 증거: integrated efficacy 0, 인증 task 0, runnable arm 0; C64 causal invalid; UI v12 소모/INVALID; font는 정확한 다섯 호출 호환성만; World-init static-only. 검토자 동의는 실증도 실행 권한도 아니다.

## 5. 새 발견 및 퇴행 (severity 순)

### N1 [MAJOR · governance/authority]
- 위치: paper/research/ROOT-research-direction.md L52 ('현재 허용: 원문 및 공개 과제 적합성 연구, 설계 명세, 사전 승인 범위의 로컬 정적 검증') ; paper/research/fable51-design-review-20260907/integration/integrated-study-design.json #/apparatus/before_implementation/3 ; same file #/next_actions/2 ('implement only justified bounded static fixtures') ; same file #/apparatus/candidate_components (B/C/G policy modules, ORX identity/receipt adapter, trusted scorer boundary)
- 문제: apparatus 계층은 개념적으로 정의됐지만 그것을 '구현'할 권한이 어디서 오는지 문서가 말하지 않는다. before_implementation은 scientific execution 권한만 별도로 구한다. B/C/G policy module, ORX adapter, scorer boundary는 정적 fixture가 아니라 연구 제어 후보를 실제로 구현하는 코드이며, native 구축이 중단된 상태에서 사실상의 두 번째 runtime으로 표류할 수 있는 바로 그 지점이다.
- 대안 설명: root는 apparatus 코드를 '사전 승인 범위의 로컬 정적 검증' 또는 thesis research의 일부로 볼 수 있다. 그렇더라도 그 해석은 사용자가 명시해야 하며 문서에서 도출되지 않는다.
- 구체 변경: ROOT §6 또는 ISD /apparatus에 '구현 권한' 결정 항목을 추가: (a) 허용 파일 루트(예: paper/research/<task>/apparatus/ 하위만), (b) packages/ 및 native 경로 import·수정 금지, (c) 폐기·비승격 규칙(apparatus 코드는 native/ARGO로 승격 대상이 아니며 prototype 근거는 ArchitectureSelectionRecord만), (d) 정적 fixture 이상의 apparatus 코드 작성은 사용자의 명시적 승인 항목. 이 결정은 task qualification(문서 작업)과 병행 가능하나 task-local 코드 작성 전에 필요하다.
- 종결 증거: 사용자 결정 기록(승인/범위/금지) + apparatus scope manifest(파일 루트·owner·폐기 규칙)
- task qualification 차단: 아니오 / task-local 코드 차단: 예

### N2 [MAJOR · identification/feasibility]
- 위치: integrated-study-design.json #/arm_deltas/table/1/C ('explicit controller/tool guard for compulsory obligations; not prompt-only') ; same #/arm_deltas/table/1/G ('same obligation set and guard strength as C') ; paper/research/integrated-research-design-active.md L99 ('C/G는 의무의 실제 집행 강도를 맞춘다') ; integrated-study-design.json #/apparatus/prohibited/0 ('native daemon/API/TUI changes')
- 문제: C−B가 '강제 유무'의 효과가 되려면 C의 의무 gate가 실제로 행동을 차단해야 한다. 그런데 apparatus는 기존 persistent REPL 위의 project-local 모듈이고 native 변경은 금지다. 열린 REPL에서 project-local guard는 우회 가능하므로 'not prompt-only' 주장은 집행 locus 없이는 근거가 없다. 집행 강도가 실제로는 prompt 준수에 의존하면 C−B는 다시 'prompt 대 prompt'가 된다.
- 대안 설명: root는 REPL 도구 wrapper 수준의 guard를 의도했을 수 있다. 그 경우 우회 가능성을 측정하면 된다. 그러나 더 강한 locus가 존재한다: 진행의 실체인 R1 launch와 final-artifact lock은 adapter를 통해서만 receipt에 묶이므로, 그 지점의 gate는 우회 시 'intent에 묶이지 않은 ORX run'으로 탐지된다.
- 구체 변경: ISD /arm_deltas 또는 /apparatus에 집행 locus를 선언: (i) compulsory obligations는 R1 launch 요청과 artifact lock 요청에서 adapter가 journal 기록(applicability/revalidation/preservation) 없이는 거부하는 hard gate로 집행, C와 G가 같은 locus·같은 강도, (ii) REPL 수준 guard는 보조이며 우회 가능성을 명시, (iii) 우회 탐지 = receipt reconciliation에서 intent 미결합 ORX run 또는 journal 기록 없는 lock → protocol invalid, (iv) P0가 gate 발화·거부·우회 발생률을 측정 항목으로 보고.
- 종결 증거: apparatus manifest의 집행 locus 문장; 기록 없는 launch/lock을 거부하고 미결합 ORX run을 표시하는 failing-first fixture; P0 gate/우회 census
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N3 [MAJOR · authority boundary]
- 위치: integrated-study-design.json #/run_classes/derived_metrics ('Borderline cases are classified before execution') ; same #/run_classes/R2 ('from already permitted public inputs') ; same #/run_classes/decision_lineage ('Every decision-cited computed number references an R1 or R2 receipt')
- 문제: (i) 자율 캠페인에서 매 로컬 계산을 '실행 전에' 사람이 분류할 수 없다; (ii) R2가 공개 train/dev 입력을 로컬로 읽는 이상 REPL에서 소규모 fit은 물리적으로 가능하며 'small does not exempt'는 준수 규칙이지 경계가 아니다; (iii) decision_lineage는 R2 숫자도 결정 근거로 허용하므로 '선택 점수는 R1만'이라는 의도가 기계적으로 표현되지 않았다.
- 대안 설명: root는 '선택에 쓰이는 점수'만 R1로 강제하고 나머지 로컬 계산은 R2로 기록하는 의도일 수 있다. 그렇다면 그것을 기계적 규칙으로 쓰면 된다.
- 구체 변경: 기계적 run-class 규칙으로 교체: (a) lock 후보로 제출되는 artifact를 생산하거나, 후보 선택·lock 결정에 인용되는 점수를 생산하는 계산은 R1(ORX receipt 필수); (b) 그 외 로컬 계산은 R2로 journal에 code/input/output/env/cost 기록; (c) 선택·lock 결정 노드는 R1 receipt만 인용 가능, R2 인용 시 protocol invalid; (d) 로컬로 읽을 수 있는 split을 task 프로토콜에서 custody 진술로 고정(hidden은 로컬 부재); (e) '실행 전 분류' 문구 삭제, 대신 선택 lineage 검사와 P0 위반 발생률 측정.
- 종결 증거: run-class 결정표(기계적 기준); R2 인용 선택 노드를 거부하는 failing-first lineage fixture(이전 Fable F3 종결 증거 유지); split custody 진술
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N4 [MAJOR · preregistration integrity]
- 위치: integrated-study-design.json #/analysis/precision_plan ('MUE is set from scientific/practical value; do not tune it down to observed noise') ; same #/analysis/minimum_useful_effect (null) ; research-completion-contract.json #/phase_authorities/1/requires, #/phase_authorities/2/requires
- 문제: MUE의 출처는 정해졌지만 확정 시점이 없다. P1 arm contrast를 본 뒤 MUE를 정하면 관측 효과에 맞춘 상향/하향 조정이 가능하고 결정표(/decision_rule_options)의 사전등록 의미가 사라진다. MUE는 과제의 과학/실용 가치에서 나오므로 task qualification 시점에 알 수 있다.
- 대안 설명: root는 'do not tune down'으로 충분하다고 볼 수 있으나 상향 조정과 시점은 다루지 않는다.
- 구체 변경: RD2/RD4a-pre에서 MUE(또는 그 도출 규칙)를 P1 arm contrast 계산 이전에 commit; 이후 변경은 새 protocol disposition + exploratory 표기. RD4a-dev requires에 'MUE committed before development unblinding' 추가.
- 종결 증거: P1 이전 날짜의 MUE commitment receipt
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N5 [MAJOR · estimand]
- 위치: integrated-study-design.json #/primary/outcome ('one preselected frozen final artifact') ; same #/campaign_eligibility/3 ('predefined final artifact selection using development evidence only') ; paper/research/integrated-research-design-active.md L48 ; paper/research/ROOT-research-direction.md L36
- 문제: 최종 artifact를 '누가' 선택하는지 미정이다. agent가 규칙 아래 하나를 commit(lock)하면 선택 판단(과적합 인식 등)이 treatment 효과의 일부가 되고, apparatus가 dev 점수 최대 규칙으로 기계 선택하면 treatment는 후보 pool에만 작용한다. 두 estimand는 다르며 이는 dataset과 무관한 개념 선택이다. P0의 완주 정의(lock 사건)도 이 선택에 의존한다.
- 대안 설명: 'preselected/predefined'는 기계 규칙을 뜻할 수 있다. 그러나 자율연구 시스템 질문에서는 agent commit이 자연스럽고, active L48의 'dev evidence로 선택'도 양쪽으로 읽힌다.
- 구체 변경: primary는 하나를 선택해 문장으로 고정(권고: agent가 adapter를 통해 deadline 전 단일 artifact ID를 lock; 미lock 시 사전 선언 fallback—floor 또는 기계 규칙 중 하나—를 arm-attributable로 적용). 다른 쪽은 labeled secondary. archive-best 금지 문구는 'hidden score 기준'임을 명시.
- 종결 증거: ISD /primary/selection_rule의 클래스 문장(값은 task 후) + P0 완주 정의에 lock 사건 포함
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N6 [MINOR · missingness wording]
- 위치: integrated-study-design.json #/missingness_policy/after_assignment ; paper/research/integrated-research-design-active.md L101
- 문제: 'lack of a usable artifact by deadline may take its justified utility floor while launch remains UNKNOWN'는 utility endpoint를 primary로 읽으면 UNKNOWN→floor의 뒷문이 된다. 또 primary 결측의 locus(최종 artifact가 유효 채점되지 못한 경우)와 중간 launch UNKNOWN(arm ceiling 안에서 소비된 process 사건)의 구분, scorer-run UNKNOWN(arm당 1회, 비차등)과 campaign-run UNKNOWN(차등)의 구분이 없다.
- 대안 설명: root는 utility endpoint를 secondary/대안으로 의도했을 수 있다.
- 구체 변경: 세 문장 추가: (1) primary는 efficacy형(hidden 성과)이며 utility-floor 절은 별도 선언된 utility endpoint에만 적용; (2) 중간 launch UNKNOWN은 primary 결측이 아니라 arm의 realized process 사건으로 census에 기록; (3) primary 결측은 lock된 artifact가 유효 채점되지 못한 경우에 한하며 scorer-run 원인과 campaign 원인을 구분해 규칙을 정한다.
- 종결 증거: ISD 문장 갱신
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N7 [MINOR · omitted obligation / stale pointer · 퇴행]
- 위치: research-completion-contract.json #/phase_authorities/1/requires, #/phase_authorities/2/requires (predecessor five-reviewer RCC L25의 'invalid/retry' 누락) ; research-completion-contract.json #/ResearchDone/0/criterion ('before outcomes') ; paper/research/integrated-research-design-active.md L18, L20 (predecessor ISD/RCC를 '현재 prospective study'로 표기) ; paper/research/ROOT-research-direction.md L17–22 (권위 목록에 현행 fable51 ISD/RCC 부재; §8에만 기재)
- 문제: (a) predecessor RD4가 요구한 invalid/retry 계약이 RD4a-dev/RD4b requires에서 빠졌다; (b) RD1의 'before outcomes'는 2단계 contrast 동결과 맞지 않는다('before confirmation outcomes'); (c) active §2와 ROOT §2의 권위 목록이 predecessor를 현행처럼 표기해 fresh-context 독자가 잘못된 ISD를 집을 수 있다(§11/§8 우선 규정은 있음).
- 대안 설명: successor precedence 문구가 있으므로 규범적 충돌은 아니다.
- 구체 변경: RD4a-dev/RD4b requires에 'frozen invalid/missingness/retry rule' 추가; RD1 문구 수정; active §2·ROOT §2 목록에 현행 ISD/RCC를 넣고 predecessor 표기.
- 종결 증거: 두 문서 갱신
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N8 [MINOR · wording overreach]
- 위치: integrated-study-design.json #/comparator/Arbor_external_anchor
- 문제: 'Different substrate prevents attribution to graph-control alone, not all possible causal system-level inference'는 이 연구에 없는 randomized whole-system 비교의 문을 열어 둔다.
- 대안 설명: 원칙 진술로만 의도됐을 수 있다.
- 구체 변경: '이 연구에서는 서술적 비교만; whole-system causal 주장은 별도 randomized protocol과 승인 필요'로 축소.
- 종결 증거: 문구 갱신
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N9 [MINOR · sealing/ancestry]
- 위치: integrated-study-design.json #/sealing/before_development ; same #/stages/0
- 문제: P0 programme은 development 이전에 선택되지만 ancestry partition commitment는 'before development'다. P0 programme과 그 ancestry가 P2에서 자동 제외된다는 문장이 없다.
- 대안 설명: 'P0/P1 use separate development-assessment data'가 이를 함의한다고 볼 수 있으나 ancestry 수준 배제는 명시되지 않았다.
- 구체 변경: 'P0 programme과 그 source ancestry는 development-side로 선언되며 P2 confirmation 후보에서 제외된다' 한 문장 추가.
- 종결 증거: 문구 갱신 + ancestry commitment에 P0 항목 포함
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

### N10 [MINOR · P0 feasibility outputs]
- 위치: integrated-study-design.json #/stages/0/results ; same #/run_classes/R1
- 문제: R1이 모든 선택용 평가를 포함하므로 dependency horizon은 ORX 왕복과 UNKNOWN 노출에 지배될 수 있다(이전 F3의 우려 중 root가 P0로 넘긴 부분). P0 results는 completion/failure anatomy/cost만 명시하고 이를 측정 항목으로 이름 붙이지 않는다.
- 대안 설명: 'failure anatomy'와 'full cost'에 포함된다고 볼 수 있다.
- 구체 변경: P0 results에 'per-R1 latency 분포, UNKNOWN/BLOCKED 발생률, gate 발화·거부·우회 건수, R2 위반 건수'를 명시 항목으로 추가.
- 종결 증거: P0 프로토콜의 census schema
- task qualification 차단: 아니오 / task-local 코드 차단: 아니오

## 6. 최소 순서 다음 단계 (실행 권한 불필요 항목만)

1. 사용자 결정 한 건: apparatus 구현 권한과 범위(허용 파일 루트, native/packages 격리, 비승격·폐기 규칙). 정적 fixture를 넘는 task-local 코드는 이 결정 뒤에만 쓴다(N1). 이 결정은 2번과 병행 가능하다.
2. task qualification 시작(이미 ISD next_actions[0]): 공개 small-compute ML programme 1개의 license·ancestry·train/dev/final-test·scorer 경계·competing methods·dependency horizon 인증 초안. 후보 source(MLAgentBench/MLE-bench/PaperBench/Agent Laboratory/AI Scientist)는 root 회수 항목이며 이 검토에서 읽지 않았다.
3. 같은 revision에서 dataset 무관 설계 문장 5개를 ISD/RCC에 추가: 선택 주체와 lock/fallback(N5), 의무 gate 집행 locus와 우회 탐지(N2), R1/R2 기계 규칙과 selection-lineage 검사·split custody(N3), MUE commit 시점(N4), primary 결측 locus 세 문장(N6). 사소 항목 N7–N10 동시 반영.
4. task-bound apparatus·arm manifest: B/C/G prompt/tool/gate/capsule/ceiling 표의 null 3행 채우기, 집행 locus 명세, failing-first fixture 목록(launch-without-record 거부, unbound ORX run 표시, R2-cited selection 거부). fixture 구현은 1번 결정 범위 안에서만.
5. P0 protocol(RD4a-pre 대상): 완주 정의(lock 사건 포함), 측정 항목(R1 latency·UNKNOWN 발생률·gate 발화/우회·R2 위반), 수리 횟수·ceiling·비용 envelope, P0 programme ancestry의 dev-side 선언. 그 뒤 immutable protocol review(설계 일반 검토가 아님)와 별도 정확한 사용자 승인.

이 검토가 요구하지 않는 것: 추가 일반 설계 검토, 표본/수리 하한, C-G 고정, 외부 comparator 고정, 새 task/outcome/gold 생성, 원고, native 변경.

## 7. 읽은 목록과 범위 한계

- 전문(commit bytes): ROOT-research-direction.md(71행); integrated-research-design-active.md(105행); material-mechanism-evidence-map.md(82행); fable51 integration의 integrated-study-design.json, research-completion-contract.json, finding-response-matrix.json, review-synthesis-ko.md, intake.json, review.md, immutable-validation.json; five-reviewer integration의 architecture-selection-record.json, owner-port-contracts.json(267행), integrated-study-design.json(106행), research-completion-contract.json(74행), disagreement-resolution.json(141행).
- 부분: 이전 review.json(키 목록, verdict/model/thinking, 14 finding의 id/severity/title/closure_evidence, recommendation); prior-art-rebinding.json(scope/novelty/new_retrieval_candidates/next, Arbor 2행, 21행 id 목록); source-receipts.json(papers 9건의 read 상태, local_experiment_execution); claim-locators.json(line_convention, 46개 id, PA-NULL·PA-CAUSAL 전체 항목); next-experiment-manifest.json(키 목록, status, openresearch_blocker, current_frontier, research_review_integration, inference_scope, research_completion, execution_ownership, acyclic_binding, prohibited_actions, next_zero_cost_actions, historical_review5_frontier_at_fable_request); active-graph-handoff-manifest.json(키 목록, status, authority_precedence, current_allowed_next_action, current_forbidden_actions, efficacy/task counts, active_chain, research_review_integration, fresh_context_handoff, historical route 일부); paper/context-graph.json(node/edge 수, fable51 node 4개).
- 원문 span: §3에 기재한 두 파일의 명시 행 범위. 저장 PDF 재독, 46 locator 전체 재검증, 후보 task 원문은 읽지 않았다.
- 이 검토는 설계·식별·실현성·계보·주장 경계에 대한 의견이며 효능·통계·runtime·권한 인증이 아니다. 어떤 테스트·실험·설치·네트워크·subagent·모델 호출(자체 추론 외)·commit도 하지 않았다. 출력은 re-review-01/review.md와 review.json 두 파일뿐이다.
