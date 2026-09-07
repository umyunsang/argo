# Fable 5.1 독립 설계 검증 — 통합 장기 자율연구 설계 (B/C/G)

- 검토 대상 commit: `f2e203058eedd4bbf5af2674fcc77d6013d5437b` (immutable; 모든 파일은 `git show <commit>:<path>`로 읽음)
- 요청 파일: `paper/research/fable51-design-review-20260907/request.json` SHA-256 `8e62ae2af581d7a34834dbfcc46c310f83a1f34c416d64e7b8156b030514e508` (일치)
- 요청 `input_hashes` 13개 전부 commit blob과 일치함을 확인했다.
- 검토 순서: (1) ROOT, active design, mechanism map, 4개 integration JSON을 먼저 전부 읽고 독립 판단을 기록 → (2) prior-art-rebinding, 저장 원문 locator 일부를 byte 검증 → (3) disagreement-resolution, finding-response-matrix, five-reviews.json 대조. 새 논문·네트워크·실행·subagent 없음.
- 작성 원칙: 동의 인원수는 증거가 아니다. 평점은 서술용이다.

## 0. 판정 요약

| 항목 | 판정 |
|---|---|
| 전체 verdict | **REVISE_BEFORE_EXPERIMENT** |
| 설계 적정성 (design adequacy) | **ADEQUATE_WITH_REVISIONS** — 연구 프로그램 선택, owner 분리, 선택/은닉 채점 원칙, null 허용은 정합적이다. 그러나 (a) 실험 장치가 어디서 실행되는지, (b) 주 outcome이 G의 고유 기제를 실제로 관측할 수 있는지, (c) scientific run의 경계가 무엇인지 세 개의 설계 수준 공백이 남는다. |
| 실행 준비도 (execution readiness) | **NOT_READY** — `integrated-study-design.json`의 primary 6개·resource_envelope 10개·analysis 5개 필드(합 21개)가 null, 인증 task 0, runnable arm 0. 이는 설계 문서가 정직하게 인정한 상태이며 새로운 결함은 아니다. |

핵심 메시지: 이번 revision은 5인 검토가 지적한 "좁은 continuity 선택"을 올바르게 되돌렸고, 문서 수준의 모순(PaperService 검색, exactly-once, 그림-작성 순환)을 해소했다. 남은 위험은 "설계 문구의 미완성"이 아니라 **"이 설계가 요구하는 실험이 현재의 권한·기질·outcome 정의로 실제 관측 가능한가"**다. 아래 F1–F3이 그 위험이다.

## 1. 발견 사항 (severity 순)

형식: 경로+행 / 문제 / 대안 설명 / 구체 변경 / 종결 증거.

### F1 [BLOCKER · 설계] 실험 장치(research apparatus)의 소유·실행 계층이 정의되지 않았다
- 위치: `owner-port-contracts.json` L81–99 (`active_research_control` → `CANDIDATES_NOT_EXECUTION_READY`), L44–59 (`PARTLY_SPECIFIED_NOT_NATIVE_IMPLEMENTED`), L61–79 (`JSON_FIXTURE_ONLY`), L119–139 (`DESIGN_ONLY`); `integrated-research-design-active.md` L30 ("이 owner 명세는 현재 native 구현이 아니다"); `ROOT-research-direction.md` L52 ("native runtime construction은 중단 상태"); `material-mechanism-evidence-map.md` L46 ("문서 제안은 `NOT_IMPLEMENTED`").
- 문제: B/C/G 비교는 실행 가능한 evidence store, audit journal, run adapter, scorer, 세 policy 구현을 필요로 한다. 그런데 native 구현은 중단이고, Python oracle은 "runtime이 아니다"(AGENTS.md). 설계 문서 어디에도 "이 실험을 위한 장치는 어떤 계층에서, 어떤 권한으로 만들어지는가"가 없다. 이 공백은 "owner/port capability 확인 → 아직 미구현 → 다시 설계 명세"의 무한 준비 루프를 만든다(요청 focus 8).
- 대안 설명: root가 기존 Prime Agent skill/prompt/REPL 서비스만으로 장치를 구성할 계획일 수 있다(native 변경 없음). 그렇다면 그것을 명시하면 된다.
- 변경: `research apparatus tier`를 설계에 추가한다. 정의: project-local, 폐기 가능, non-native(prompt pack + Python skill 모듈 + REPL 서비스 + 파일 기반 journal). 이 계층은 ARGO native construction으로 세지 않으며, 코드 해시가 protocol fingerprint에 들어간다. owner-port 항목마다 "apparatus 수준에서 실현" 대 "native 수준 설계만"을 표시한다(예: evidence store·audit journal·run adapter·scorer는 apparatus 실현 필수, native ResearchState projection은 설계만).
- 종결 증거: apparatus tier 결정 기록(권한 범위·금지 사항 포함) + hash-bound runnable B/C/G manifest(CF-02/SR-03의 종결 증거와 같은 것).

### F2 [BLOCKER · 설계] 주 outcome과 G의 고유 기제 사이에 신호 대 잡음 불일치가 있다
- 위치: `integrated-study-design.json` L31–35 (`natural_campaign` primary, stress는 labeled strata), L38–45 (primary = hidden 성과); `ROOT-research-direction.md` L36; `integrated-research-design-active.md` L48, L54.
- 근거(저장 원문, author-reported): Prime Agent 논문 `sources/2608.23552v1-layout.txt` L456–457 — nanoGPT speedrun 다일 자율연구에서 "the choice of harness has little effect on final records compared to the noise of the experiment" (2–3 seeds/harness). 같은 논문 L458–470은 harness가 outcome이 아닌 **행동**(REPL 밖 실험 수)만 바꿨다고 보고한다. Arbor `paper/sources/tex/2606.11926/main.tex` L823–832는 tree/insight 제거가 MLE-Bench Lite 11과제에서 Any Medal 81.82→63.64/54.54%로 떨어진다고 보고한다(구조 차이가 보이는 경우도 있음; power prior로는 쓰지 않음).
- 문제: G가 C에 더하는 것은 "versioned traversal·scoped invalidation·graph-mediated continuation"이다. 이 기제는 **앞 근거가 뒤집히거나 context가 끊길 때** 작동한다. 그런데 primary는 "자연 캠페인"이고 revision/restart는 secondary strata다. 자연 캠페인에서 revision이 저절로 발생하지 않으면 G−C는 구조적으로 0에 가깝고, harness 논문의 관측대로 잡음에 묻힌다. 반대로 stress를 primary에 넣으면 "G에 유리하게 설계했다"는 비판을 받는다. 현재 문서는 이 긴장을 인식하지만(L54 "스트레스 개입은 주 metric을 사후 바꾸지 않는다") 해소하지 않았다.
- 대안 설명: Arbor형 결과처럼 G가 revision 없이도 후보 선택·가지치기를 개선할 수 있다. 그러면 자연 primary가 맞다. 그러나 이 가정은 dev에서 확인해야 하며, 확인 전에 confirmation primary를 자연 캠페인으로 못 박을 이유는 없다.
- 변경: 과제 정의에 **arm 공통·사전 등록 event schedule**을 포함시킨다(예: 결정 k번째 뒤 데이터셋 버전 갱신 공지, baseline 전처리 결함 공개, 1회 fresh-context 재시작). 이것은 "사후 스트레스"가 아니라 "과제의 일부"이며 모든 arm에 같은 시점·같은 bytes로 주어진다. primary는 event 포함 캠페인의 최종 artifact hidden 성과로 유지한다. event 없는 자연 stratum은 labeled secondary로 남긴다. dev 단계에서 (i) event 유무별 arm 행동 차이, (ii) within-cell 분산을 추정해 MUE를 잡음과 비교한 뒤 confirmation primary를 확정한다.
- 종결 증거: task certificate에 event schedule 해시 포함; dev 분산·MUE 대비표(blinded); "event가 없으면 G−C 기대효과 0"을 명시한 사전 등록 문장.

### F3 [MAJOR · 설계] "scientific run"의 경계가 없어 ORX 권위 규칙이 실제 캠페인에서 실행 불가능하거나 공허하다
- 위치: `material-mechanism-evidence-map.md` L27 ("repository의 별도 ad-hoc process 또는 두 번째 run registry를 만들지 않는다"); `owner-port-contracts.json` L100–118, L133–137; `integrated-research-design-active.md` L30.
- 문제: small-compute ML 캠페인은 수십 회의 로컬 분석(REPL에서 metric 재계산, 데이터 진단, 소규모 sanity 학습)을 낳고, Prime Agent 논문(L458–470)은 모델이 실제로 그렇게 행동함을 보인다. 이 계산이 결정을 바꾼다면 "receipt 없는 scientific run"이다. 반대로 모든 계산을 ORX로 보내면 ORX 왕복시간이 dependency horizon을 지배하고 UNKNOWN 노출이 급증한다. 설계는 두 극단 중 어느 쪽인지 정하지 않았다.
- 대안 설명: root는 "artifact를 만드는 학습/평가"만 scientific run으로 볼 의도일 수 있다. 그렇다면 로컬 분석의 기록 규칙이 필요하다.
- 변경: 두 등급 규칙. R1 authority run = artifact/최종 후보를 생성·평가하는 학습·평가, ORX receipt 필수. R2 local analysis = REPL 계산, audit journal에 code/input/output 해시로 기록, ORX 아님. 결정 노드가 인용하는 모든 숫자는 R1 또는 R2 receipt를 참조해야 한다. "두 번째 run registry 금지"는 R1에만 적용됨을 명시한다.
- 종결 증거: protocol에 run-class 규칙; receipt 없는 숫자를 인용한 결정 노드를 거부하는 audit fixture(failing-first).

### F4 [MAJOR · 통계/공정성] 인프라 UNKNOWN이 arm별 차등 결측을 만든다
- 위치: `owner-port-contracts.json` L133–137 ("convert UNKNOWN into failure or not-run" 금지, blind retry 금지), L250–251; `integrated-research-design-active.md` L64–66; `integrated-study-design.json` L41 (`invalid_handling: null`). 현재 실례: `paper/research/next-experiment-manifest.json` `openresearch_blocker.last_run` = "stale running record".
- 문제: UNKNOWN을 실패로도 미실행으로도 바꾸지 않고 재시도도 하지 않으면 그 arm의 실험 기회가 사라진다. 더 많은 launch를 하는 arm(G일 수도, C일 수도)이 더 자주 노출되므로 결측이 treatment와 상관된다. 이는 정직한 원칙이 만든 새 편향 경로다.
- 대안 설명: UNKNOWN이 매우 드물어 무시 가능할 수 있다. 그러나 현재 유일한 ORX 기록이 stale running이므로 그렇게 가정할 수 없다.
- 변경: treatment-blind 세 등급 규칙을 `invalid_handling`에 채운다. (i) infrastructure-UNKNOWN/BLOCKED가 마감까지 해소되지 않으면 해당 **programme block 전체**(모든 arm)를 `INFRA_VOID`로 primary에서 제외하고 census에 보고. (ii) protocol-invalid(agent 책임: hidden 접근 시도, 무산출물, 선택 규칙 위반) → floor 점수로 ITT 포함. (iii) scientific failure(정당한 절차 뒤 낮은 성과) → 실제 점수. 사람 개입으로 UNKNOWN을 해소하는 것은 허용하되 개입 ledger에 기록하고 arm-blind로 수행한다.
- 종결 증거: 규칙이 채워진 `invalid_handling`; dev 로그에 규칙을 blind 적용한 receipt; ITT/per-protocol 감도분석 계획.

### F5 [MAJOR · 측정 독립성] "hidden"은 접근 은닉이지 지식 은닉이 아니며, 1인 운영에서 봉인 절차가 없다
- 위치: `integrated-research-design-active.md` L50; `owner-port-contracts.json` L141–158; `integrated-study-design.json` L24–30.
- 문제: 공개 ML task의 test split은 모델 사전학습에 들어갔을 수 있다. 오염은 arm 공통이라 contrast를 편향시키지는 않지만, 모델이 답을 알면 원문·근거 제어가 개입할 여지가 줄어 효과를 축소한다. 또한 dev에서 장치를 조정하는 사람과 hidden split을 준비하는 사람이 같다. 문서는 "planner/developer/critic은 읽지 못한다"고 하지만 사람 운영자의 봉인 절차가 없다.
- 대안 설명: 선택된 과제가 최신 재분할 또는 사후 생성 데이터라면 지식 은닉이 부분적으로 성립한다.
- 변경: task certificate에 (a) private re-split 또는 post-cutoff 데이터 우선, (b) 공개 test를 쓰면 오염 진술과 pre-run canary probe, (c) hidden split·scorer code의 해시 commitment를 **dev 시작 전**에 기록하고 confirmation 뒤 공개, (d) hidden-open 로그.
- 종결 증거: commitment receipt; 오염 진술; hidden-open 후 변경 0건 감사(MS-B5와 동일).

### F6 [MAJOR · 통계] 분산 설계에 블록/짝 구조와 분산성분 추정 계획이 없다
- 위치: `integrated-study-design.json` L37 ("clustered for shared ancestry"), L72–74 (`repeats_nested`, `power_or_precision_plan` null); `integrated-research-design-active.md` L58.
- 문제: 추론 단위가 programme이고 seed/round가 nested라는 점은 맞다. 그러나 가장 큰 분산 감소 수단인 "모든 arm을 같은 programme·같은 시작 baseline·같은 seed에 배치하는 블록 설계"가 명시되지 않았다. 또 between-programme과 within-cell(run-to-run) 분산을 분리 추정하려면 일부 cell에 독립 시작이 2회 이상 있어야 한다. 이는 nested 설계의 논리적 요건이며 표본 하한이 아니다.
- 대안 설명: root는 "family-level paired analysis"(MS-B3 종결 증거)를 이미 의도할 수 있다. 문서에 없을 뿐이다.
- 변경: analysis에 "programme = block, 모든 arm 동일 블록 배치, 실행 순서 무작위, 짝 차이의 cluster/randomization interval"을 명시. dev에서 일부 cell에 ≥2 독립 시작을 두어 분산성분을 추정하고, 그 값으로만 confirmation 정밀도 계획을 만든다. 숫자 하한(6/24 등)은 채택하지 않는다(root 결정 R-N 동의).
- 종결 증거: 분산성분이 채워진 blinded precision worksheet; 블록 배치·순서 무작위화 receipt.

### F7 [MAJOR · 식별] B/C/G의 조작적 차이가 표로 존재하지 않아 C−B, G−C가 무엇의 효과인지 아직 말할 수 없다
- 위치: `integrated-research-design-active.md` L34–42; `architecture-selection-record.json` L44–72; `integrated-study-design.json` L18, L100.
- 문제: "compulsory"가 prompt 지시인지 tool gating(기록 없으면 다음 행동 차단)인지, G의 "graph-mediated continuation"이 결정적 affected-set 계산 도구인지 LLM이 graph를 읽는 것인지 미정이다. 만약 C는 prompt 강제, G는 도구 강제라면 C−B는 "prompt 대 harness", G−C는 "표현+결정적 계산+context 형태"가 섞인다. 설계가 G−C를 package라고 부르는 것은 정직하지만, prototype 결정에는 "graph 없는 결정적 의존성 검사 도구"가 같은 효과를 내는지가 중요하다.
- 대안 설명: G의 이점은 graph가 아니라 (a) 결정적 의존성 계산, (b) 더 압축된 active view, (c) 더 많은 검사 기회에서 올 수 있다(다섯 검토도 같은 대안을 지적; 동의).
- 변경: arm-difference table을 만든다. 열: 상태 표현 / 강제 gate(어떤 tool call이 어떤 기록 없이는 차단되는가) / 사용 가능 도구(G: traverse, affected_set; C: 동일 도구를 tree 위에서 제공하는지 여부 명시) / prompt bytes / capsule 생성기 / 허용 context bytes. C의 compulsory도 tool gating으로 구현해 C−B가 "강제 방식"이 아닌 "강제 유무"가 되게 한다. G의 각 graph 기능 호출을 로그해 결과 해석 때 기제 귀속에 쓴다. passive-graph 4번째 arm은 이 로그가 해석을 못 줄 때만 추가(root 조건부 결정 동의).
- 종결 증거: hash-bound arm-difference table; code-path activation receipt; delivered-vs-used 근거 계측.

### F8 [MAJOR · 기여 범위] "통합 시스템 기여"에 1급 feasibility outcome이 없다
- 위치: `ROOT-research-direction.md` L11, L28; `architecture-selection-record.json` L4–5; `integrated-research-design-active.md` L9–11.
- 문제: Pi/Prime, discovery, evidence plane, ORX는 모두 고정 공통 계층이고 인과 treatment는 control policy만이다. 따라서 논문의 인과 내용은 "제어 표현 ablation"이다. 통합 시스템 자체의 기여는 서술이 된다. 이 상태로는 외부 독자가 "메모리 ablation + 시스템 설명"으로 읽는다(요청 focus 2).
- 대안 설명: 설계·owner 계약 자체를 기여로 보는 관점도 가능하다. 그러나 근거 없는 설계 기여는 사용자가 배제한 "feature stack"과 구분되지 않는다.
- 변경: Stage 0 단일 arm feasibility를 **보고 가능한 결과**로 정의한다: 실제 공개 ML 캠페인 1개를 통합 loop(discovery→source evidence→R1 run via ORX receipt→sealed scorer→refine→successor)가 끝까지 완주하는지, 완주율, 실패 해부, 전체 비용. 논문 기여를 (i) 통합 loop의 feasibility/실패 해부, (ii) C-vs-G 인과 contrast, (iii) owner 계약 설계로 3분한다. (i)은 null이어도 결과다.
- 종결 증거: Stage 0 protocol에 "완주" 정의와 census 스키마; 결과 receipt.

### F9 [MINOR · 계보] inconclusive 시 prototype 기본값과 native resume gate의 교차 의존이 미기재
- 위치: `architecture-selection-record.json` L92–95; `research-completion-contract.json` L60–66 (L63 "native construction resume gates and explicit restart satisfied").
- 문제: 넓은 불확실성 결과에 대해 "no efficacy winner"만 있고 NAIS prototype이 무엇을 채택하는지 없다. 또 resume gate는 이 연구와 무관한 DeepVoice 검증 상태(harness 정책)에 묶여 있어 논문 결과가 있어도 prototype이 막힐 수 있다. 순환은 아니지만 미기재 교차 의존이다.
- 변경: outcome_mapping에 "inconclusive → Stage 0 feasibility를 통과한 가장 저렴한 arm을 prototype 기본값으로, graph는 audit/export, efficacy 주장 없음"을 추가. PrototypeReadiness에 resume gate 의존을 명시하고 decouple 여부를 사용자 결정 항목으로 올린다.
- 종결 증거: 결정표 행 추가; gate 의존 진술.

### F10 [MINOR · 절차] RD4의 단일 실행 승인이 dev/confirmation 2단계와 맞지 않는다
- 위치: `research-completion-contract.json` L25–27; `integrated-study-design.json` L98–103.
- 변경: RD4a(장치·dev family·dev 예산 승인), RD4b(동결 후 confirmation 승인)로 분리.
- 종결 증거: contract 갱신.

### F11 [MINOR · 표현] 주 RQ는 2부("최종 성과"와 "근거 승계")인데 primary는 1개
- 위치: `integrated-research-design-active.md` L11; `integrated-study-design.json` L4, L47–56.
- 변경: 근거 승계·continuation 지표는 secondary이며 primary null 시 승격하지 않음을 한 문장으로 명시.

### F12 [MINOR · 누설] 사람 적응(harness tuning) 누설은 "기록"만으로 막히지 않는다
- 위치: `integrated-research-design-active.md` L56; `integrated-study-design.json` L22.
- 변경: confirmation family 목록을 dev 시작 전에 해시 commitment로 봉인하고 동결 뒤 공개. 개발자가 confirmation family를 알면 장치 조정이 그 family로 향한다.
- 종결 증거: commitment receipt.

### F13 [QUALIFY · 비교군] 외부 runnable comparator(Arbor)의 역할을 정해야 한다
- 위치: `paper/research/arbor-source-artifact-audit.json` (Apache-2.0, commit `2f4e654…`, FULL_PAPER_READ, "strong comparator only"); CF-02.
- 판단: 인과 contrast는 같은 기질 위의 in-house B/C/G여야 한다(기질 혼입 방지). Arbor를 그대로 arm으로 넣으면 기질이 다르므로 causal 비교가 아니다. 그러나 in-house B만 있으면 "약한 baseline" 비판을 받는다. 절충: 예산이 허용할 때만 Arbor의 matched-run을 **non-causal external anchor**로 labeled 보고, SOTA 순위 금지. CF-02의 "runnable identity 필수"는 in-house arm에 대해 동의, 외부 comparator 재현은 선택으로 qualify.

### F14 [ACCEPT · 확인] 4/2/1 stress template 숫자의 지위
- 위치: `integrated-research-design-active.md` L54; `integrated-study-design.json` L34; `disagreement-resolution.json` L72.
- 판단: "후보이며 universal threshold가 아니다"라는 처리에 동의. F2의 event schedule로 대체되면 이 숫자는 자연히 과제별 값으로 바뀐다.

## 2. 요청된 여덟 초점에 대한 답

1. **B/C/G가 compulsory deliberation과 graph control을 구분하는가, 비용 가치가 있는가.** 개념적으로는 구분한다(C−B: 강제 절차, G−C: graph-control package). 조작적으로는 아직 아니다(F7). 세 arm의 dev 비용은 분산 추정을 겸하면 정당하다. confirmation에서는 C-vs-G가 결정적 contrast이고 B는 dev가 "B가 최강 신뢰 비교군"임을 보일 때만 남긴다.
2. **통합 시스템 기여 대 좁은 메모리/topology 주장.** 현재 인과 내용은 제어 표현 ablation이다. F8의 Stage 0 feasibility outcome을 1급 결과로 두지 않으면 통합 주장은 서술에 머문다. topology 단독 주장 금지는 이미 잘 되어 있다.
3. **공개 ML 캠페인 적합성, 독립 gold, source-family 누설.** 자격 기준(ISD L24–30)은 옳다. 누락: 지식 은닉 대 접근 은닉(F5), confirmation family 봉인(F12), event schedule(F2). Arbor가 MLE-Bench Lite에서 이미 tree ablation을 했으므로 같은 계열 과제는 비교 가능성은 높이지만 novelty residual은 좁힌다 — 정직하게 "matched-rights reproduction-class evaluation"으로 부를 준비를 해야 한다.
4. **선택·전체 비용·nested 무작위성·표본.** 단일 사전선택 artifact, archive-best 금지, root+descendant 비용은 옳다. 누락: 블록/짝 설계와 분산성분 계획(F6), invalid 3등급(F4). 숫자 하한 불채택은 옳다.
5. **ORX/Prime 권위, UNKNOWN 대 exactly-once.** at-most-once local binding과 exactly-once external 실행의 구분, UNKNOWN 유지는 옳다. 누락: run-class 경계(F3), UNKNOWN의 차등 결측 처리(F4). 현재 유일한 ORX 기록이 stale running이므로 이 문제는 가설이 아니다.
6. **trusted scorer 대 untrusted critic.** 분리는 옳고 "같은 RLM 역할 분리는 독립성 아님"도 옳다. 누락: 사람 운영자 봉인·commitment(F5), artifact 실행 환경 manifest 고정(artifact가 scorer sandbox에서 실행 불가 → floor, arm 공통).
7. **gate 순환.** 그림-작성 순환은 제거됐다. 남은 것은 순환이 아니라 교차 의존(F9)과 승인 단계 분리(F10).
8. **논문·prototype으로 가는 실행 가능 경로.** 현재 가장 큰 위험은 F1이다. apparatus tier 없이는 모든 next_action이 "명세 확인"에서 끝난다. 아래 §4의 단계형 최소 연구가 경로다.

## 3. Sol 5인 검토와 root 조정에 대한 판정

| 항목 | 판정 | 이유 |
|---|---|---|
| R-ARCH (통합 graph/evidence 비교를 프로그램으로, graph 승자 아님) | **수용** | 사용자 invariant와 일치. |
| R-ARMS (B/C/G 개발 screen, passive 4번째 arm 조건부, G−B는 package 표기) | **수용 + F7 조건** | 조작적 차이표 없이는 screen이 무엇을 screen하는지 불명. SR-04의 "primary contrast G−B" 고정은 **기각**하고 root의 "dev 뒤 동결"을 지지. 다만 예산 부족 시 C-vs-G가 기본 결정 contrast임을 추가. |
| R-N (6/24 하한 거부, dev 분산에서 도출) | **수용 + F6** | MS-B3의 구조 요소(paired, nested 2 starts in dev, ITT)는 옳고 숫자만 거부하는 root 판단에 동의. "일부 cell ≥2 starts"는 하한이 아닌 분산 추정의 논리 요건. |
| R-HORIZON (자연 적합성 평가, 4/2/1은 template) | **qualify (F2)** | "자연 적합성"만으로는 G 기제가 발화하지 않을 수 있다. arm 공통 사전 등록 event schedule을 과제 정의에 포함하는 절충을 권고. |
| R-ASSESSOR (trusted scorer / untrusted critic) | **수용 + F5** | 사람 운영자 봉인 절차 추가. |
| R-IDEMPOTENCY (UNKNOWN 유지, at-most-once) | **수용 + F4** | 차등 결측 규칙 없이는 정직한 원칙이 편향이 된다. |
| R-OWNER (DiscoveryPort/SourceEvidenceService/PaperService/ORX/Prime 분리) | **수용 + F3** | run-class 경계 필요. |
| R-WRITE (ResearchDone→작성→PublicationReady, 순환 제거) | **수용 + F10** | |
| R-NOVELTY (21 locator 재결합, residual UNESTABLISHED) | **수용** | SR-02의 "residual 없으면 reproduction/negative evaluation로 재분류"도 수용. Arbor/EviGraph가 가까워 그 가능성은 높다. |
| R-INSTALL | **수용** | |
| CF-02 (외부 comparator 완전 재현) | **qualify (F13)** | in-house runnable identity는 필수, 외부 재현은 선택. |
| D3-B3 "네 arm" | **root 조건부 처리 수용** | F7의 기능 호출 로그가 더 저렴한 대체. |
| WR-05 (그림 bytes) | **root 분리 수용** | |
| MS-B1/CF-01/D3-B3/SR-03의 "arm diff 표" | **수용, 미종결** | F7과 동일. |

**5인 검토와 root 조정 모두가 다루지 않은 것(새 발견):** F1(apparatus tier), F2(PA-NULL로 뒷받침되는 SNR 불일치 — 그들 자신의 번들에 있는 원문), F3(run-class 경계), F4(UNKNOWN 차등 결측), F9(inconclusive 기본값과 resume gate 교차 의존), F12(confirmation family 봉인). 잘못 기각된 항목은 찾지 못했다. revision이 새로 도입한 유해 요소도 찾지 못했다; "control-only diagnostic" 별도 명명(ISD L21)은 좋은 추가다.

**보존할 합리적 이견:** (a) SR-04는 G−B를 primary로 고정하려 하고 root는 dev 뒤 동결한다 — 둘 다 방어 가능하며, 나는 root 쪽이지만 "dev n이 작아 잘못된 비교군을 고를 위험"을 기록으로 남겨야 한다. (b) MS-01의 2×2 pilot 요구와 root의 조건부 — 기능 호출 로그가 해석을 못 주면 MS-01이 옳게 된다.

## 4. 더 작고 결정적인 연구 (권고)

현 설계보다 작은 경로가 더 낫다. 순서가 핵심이다.

- **Stage 0 — 단일 arm feasibility (C arm 권장).** 공개 small-compute ML programme 1개. 목표: 통합 loop 완주(ORX R1 receipt 1개 이상, sealed scorer 점수 1개, refine→successor 1회, fresh-context 재시작 1회). 같은 programme에 독립 시작 2회 이상으로 within-cell 분산의 첫 추정. 산출: 완주 여부, 실패 해부, 전체 비용, 분산 추정. **완주 실패도 결과**이며 그 경우 논문 범위 결정으로 간다(무기한 수리 금지).
- **Stage 1 — dev screen B/C/G.** Stage 0의 비용·분산으로 dev programme 수를 정한다(숫자 하한 없음). 목적: arm 차이 조작 확인, 기능 호출 로그, event schedule 반응, MUE 대비 잡음, 비교군 선택.
- **Stage 2 — confirmation.** 봉인된 programme에서 C-vs-G(B는 dev가 정당화할 때만) 블록 배치, 단일 primary contrast, event schedule 포함 캠페인의 최종 artifact hidden 성과.

## 5. 최소 우선순위 다음 단계 (실행 권한 불필요 항목 우선)

1. apparatus tier 결정 기록 작성(F1) — 어떤 계층·권한·금지·해시.
2. run-class 규칙(F3)과 invalid 3등급 규칙(F4)을 `integrated-study-design.json`/`owner-port-contracts.json`에 채움.
3. arm-difference table 초안(F7): gate·도구·prompt·capsule 열.
4. task certificate 초안: 후보 programme 1개, license/ancestry/split, 지식 은닉 진술, event schedule, hidden commitment 절차(F2, F5, F12). MLAgentBench/MLE-bench/PaperBench/Agent Laboratory/AI Scientist는 root retrieval 후보로만(본 검토에서 읽지 않음).
5. outcome_mapping에 inconclusive 기본값·resume gate 의존 명시(F9); RD4 분리(F10); RQ secondary 문장(F11).
6. 그 뒤에만 RD4a(Stage 0 승인) 요청.

## 6. 실험 채택/기각 규칙 (제안; 사전 등록 대상)

- primary 추정량: programme-block 짝 차이(G−C)의 평균과 cluster/randomization 구간, event schedule 포함 캠페인의 최종 artifact hidden 성과, ITT(3등급 규칙).
- **G 채택**: 구간 하한 > 0 이고 점추정 ≥ MUE, 그리고 G/C 전체 비용 비율 ≤ 사전 cap, 그리고 안전 위반(hidden 접근·tampering) 0.
- **G 기각(C 선택)**: 구간 상한 < MUE ("충분한 정밀도로 이점 배제").
- **Inconclusive**: 구간이 0과 MUE를 모두 포함 → prototype 기본값 = Stage 0 통과 최저 비용 arm, graph는 audit/export, efficacy 주장 없음.
- **B 선택**: 사전 non-inferiority 마진 안에서 C와 동등하고 더 저렴할 때만.
- metric/selection/invalid 규칙의 사후 변경은 해당 분석을 exploratory로 표기.

## 7. 유한 연구 완료 규칙 (제안)

연구는 다음 중 하나에서 **닫힌다**. 그 뒤에만 원고를 쓴다.
- (A) Stage 0 완주 실패 또는 사전 정한 수리 예산(1회) 소진 → feasibility/실패 해부 결과로 닫음. 범위 결정을 사용자에게 요청. 성공으로 재표기 금지.
- (B) Stage 0 완주, Stage 1·2 완료, 모든 배정 block이 score/floor/INFRA_VOID 중 하나로 회계됨, primary 분석과 독립 재계산 완료, §6 규칙 적용 → positive/null/negative/inconclusive 어느 것이든 닫음.
- (C) RD4a에서 고정한 전체 시간·비용 상한 소진 → 도달한 stage의 주장 등급으로 닫음.
어느 경우도 "더 많은 인프라 준비"는 완료 조건이 아니다.

## 8. 서술적 평점 (1–5, 투표 아님)

| 축 | 평점 | 한 줄 이유 |
|---|---|---|
| 개념 정합성 | 4 | 프로그램·owner·gate가 일관됨 |
| 식별 가능성 | 3 | package 표기는 정직하나 조작적 차이표 부재 |
| 실행 경로 실현성 | 2 | apparatus tier 부재, 21 null |
| 측정 독립성 | 3 | scorer/critic 분리는 좋음, 봉인·오염 진술 부재 |
| 통계 계획 | 2 | 원칙은 옳고 값·블록 구조 없음 |
| 근거 경계 정직성 | 5 | 소모 권한·invalid·author-reported 경계 유지 |
| 논문→prototype 계보 | 3 | 매핑 있음, inconclusive 기본값·gate 의존 미기재 |

## 9. 범위 한계와 읽은 목록

- 읽은 파일(commit 바이트, 전문): ROOT-research-direction.md; integrated-research-design-active.md; material-mechanism-evidence-map.md; integration/{architecture-selection-record, integrated-study-design, owner-port-contracts, research-completion-contract, prior-art-rebinding, disagreement-resolution, finding-response-matrix, immutable-validation, five-reviews}.json; packet/review-brief.md; long-horizon-harness-benchmark-20260907/{source-receipts, claim-locators}.json; next-experiment-manifest.json; arbor-source-artifact-audit.json(일부 필드).
- 원문 byte 검증한 locator: 2608.23552v1-layout.txt L430–470(PA-NULL 주변); 2606.11926/main.tex L823–832; 2608.03501/aaai2027.tex L232; 2607.12227/neurips_2026.tex L446; 2608.06301/sections/abstract.tex L2–11; 2608.04738/main_arXiv.tex L106–127. 모두 prior-art-rebinding의 source_sha256과 일치.
- 읽지 않은 것: 저장 PDF 전문 재독, MLAgentBench/MLE-bench/PaperBench/Agent Laboratory/AI Scientist 원문(root retrieval 후보로만 기재), 46 locator 전부의 재검증.
- 본 검토는 설계·방법·실현성·인과 식별·계보·주장 경계에 대한 의견이다. 효능·통계·runtime 인증·권한이 아니다. 어떤 실행·설치·subagent·네트워크 호출도 하지 않았다. 작업 트리에 미커밋 변경이 있음을 확인했으나 사용하지 않았다.
