# 01 방법론·통계 독립 설계 검토

- **Reviewer role:** 방법론·통계
- **Packet SHA-256:** `a89c23c4c5e5fda79fc3efd2301a3c33eb3b13f1bdc8fd6a597a85bdd59e2fe9` (직접 재계산 일치)
- **Verdict:** **REVISE_BEFORE_EXPERIMENT**
- **경계:** 연구설계 검토이며 실행·출판·프로토타입 승인 판정이 아니다. 아래 문헌 성능은 모두 저자 보고값이고 로컬 재현값이 아니다.

## 총평

재료는 충분하지만 confirmatory design은 아직 없다. 최신 지시는 graph-based autonomous research loop와 논문→ARGO/NAIS prototype 계보를 요구하면서도 graph를 당연한 승자로 두지 말라고 한다(`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md:L5–L15,L28–L43`). 반면 현재 `study-contract.json`은 typed graph를 필수가 아니라고 하고 treatment를 세 절차의 후보로만 둔다(`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json:L47–L56`). 따라서 “연구 연속성”만 측정하면 사용자가 요구한 통합 설계 선택을 못 하고, 반대로 Prime/Pi·Exa·ORX·graph·refine을 한꺼번에 바꾸면 무엇이 효과를 냈는지 추정할 수 없다. 결론은 **공통 substrate를 고정하고 active graph control의 증분 효과를 검정하는 단일 package estimand**로 좁혀야 한다.

## 차단 사항

### MS-B1 — 통합 package estimand와 중립 계측 graph가 분리되지 않음 `[BLOCKER]`

- **근거:** 최신 지시는 후보 흐름과 소유권을 가설로 둔다(`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md:L28–L34`). 현재 초안은 package 수준 효과만 주장한다고 하지만(`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md:L30–L38`), graph는 optional이다(`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json:L47–L56`).
- **문제/영향:** 외부 연구 provenance graph가 두 조건을 기록하는 **중립 계측기**인지, agent가 조회하고 eligibility를 강제받는 **active treatment**인지 불명확하다. 이 둘이 섞이면 graph 사용 자체와 graph control 효과를 구별할 수 없다.
- **수정:** 양 조건의 Prime/Pi session substrate, frozen source/discovery rights, ORX run authority, model/tools, assessor를 동일하게 둔다. 주 contrast는 `ACTIVE_EVIDENCE_GRAPH_CONTROL − STRONG_SOURCE_BACKED_TREE_WITH_COMPULSORY_CHECKLIST`로 고정한다. treatment만 exact source/version/claim/hypothesis/experiment/decision edge, reverse invalidation, selective reopening, preservation gate, graph-derived continuation capsule을 실행한다. 보이지 않는 audit graph는 양 arm을 같은 방식으로 기록한다.
- **종결 증거:** arm-difference table, prompt/action surface diff, graph visibility 규칙, contamination 판정, 위반을 포함한 ITT 분석이 hash-bound preregistration에 있어야 한다.

### MS-B2 — 독립 연구 outcome과 최종 선택 규칙이 비어 있음 `[BLOCKER]`

- **근거:** task suite, metric, invalid 처리, selection rule이 모두 `null`이다(`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json:L12–L22`). 정확한 task/gold, 표본·power·budget·command도 미정이다(`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json:L88–L100,L118–L131`; `paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md:L110–L123`). 현재 handoff도 efficacy result와 fully certified task가 각각 0이다(`paper/research/five-reviewer-design-review-20260907/packet/paper__research__active-graph-handoff-manifest.json:L949–L950`).
- **문제/영향:** schema 준수, 적중 decision 수, archive maximum을 연구 성과로 바꿀 위험이 있다. 서로 다른 task-native metric을 사후 정규화하면 방향과 규모를 선택할 자유도도 생긴다.
- **수정:** 하나의 coherent public small-compute ML family bundle을 고르고, family별 campaign 종료 전에 **단일 artifact ID**를 봉인한다. primary는 숨겨진 test/scorer가 측정한 그 artifact의 사전 지정 성능이다. 가능한 한 같은 metric을 쓰고, 부득이한 scaling은 development family만으로 미리 고정한다. crash·budget exhaustion·무산출물의 floor score와 invalid 처리도 미리 정한다. report correctness, negative-result reuse, recovery, graph closure는 별도 진단 또는 안전성 endpoint다.
- **종결 증거:** license/ancestry/split/scorer certification, immutable final-selection receipt, hidden-score isolation test, primary metric formula와 최소 유용 효과(MUE)가 모두 고정되어야 한다.

### MS-B3 — 독립 단위, stochastic noise, power가 실행 가능한 수준이 아님 `[BLOCKER]`

- **근거:** 초안 자체가 programme/source lineage를 단위로 두지만 confirmatory n, power, MUE는 `null`이다(`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json:L88–L100`). 로컬 audit도 seed·round·candidate를 독립 표본으로 세지 말고 family-level paired 분석을 요구한다(`paper/research/long-horizon-harness-benchmark-20260907/independent-audits.json:L16–L18`, embedded `local-baseline-audit.md` §§2.1, 4.1–4.3). HoH는 task-condition당 valid run이 1개이고 transport failure를 교체했으며 generation seed를 통제하지 못했다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01481-orx-full.txt:L1723–L1762`). HarnessDev도 evolution cell당 trajectory가 하나라 population uncertainty를 못 낸다고 명시한다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01437-orx-full.txt:L1035–L1045`).
- **문제/영향:** 30 seeds, 여러 rounds, 여러 checkpoints가 있어도 같은 dataset/repository ancestry면 n=1 cluster다. LLM·training randomness와 family heterogeneity가 섞이면 작은 차이는 해석 불가다.
- **수정:** pilot은 최소 6개의 ancestry-disjoint development families에서 2×2(`tree/graph × passive/compulsory control`)를 실행하고 arm-family당 두 independent starts를 nested repeat로 둔다. pilot은 조작, 실패율, family/within-family variance와 MUE 설정에만 쓴다. confirmation은 pilot에서 정한 80% power와 95% interval 기준으로 산정하되 **계획 하한 24 held-out independent families**, arm-family당 두 starts로 한다. 계산된 n이 예산을 넘으면 표본을 줄여 실행하지 말고 claim을 축소하거나 task를 바꾼다. 지금은 미실행 p-value가 필요하지 않다.
- **종결 증거:** ancestry clustering audit, blinded power worksheet, randomized run order, family-level paired mean/cluster bootstrap 또는 randomization interval, nested-repeat variance가 있어야 한다.

### MS-B4 — selection·failure·cost 분모가 causal contrast를 지키지 못함 `[BLOCKER]`

- **근거:** Meta^n의 archive-best는 task마다 다른 chain의 최대를 평균한다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2608.24735-orx-full.txt:L634–L651`); 이는 하나의 배포 artifact가 아니다. HarnessDev는 official trajectory에서 probe·partial·stopped·invalid legs를 제외하고(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01437-orx-full.txt:L332–L404`) 표시 cost에서 creator tokens도 제외한다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01437-orx-full.txt:L459–L466,L1338–L1393`). RecEvolve는 41회/5 threads를 보고하지만 full launch/failure census가 없다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01622-orx-full.txt:L388–L393,L460–L473`).
- **문제/영향:** treatment가 더 많은 critique, candidate, retrieval 또는 hidden feedback을 소비하거나 실패를 분모에서 빼면 graph 효과처럼 보인다. best checkpoint 재선택은 selection optimism을 만든다.
- **수정:** eligible→randomized→launched→retry→completed→selected→hidden-scored 흐름을 모두 보존하고 assigned campaign 기준 ITT로 분석한다. 하나의 사전 선택 artifact만 primary에 쓴다. token(input/output/cache), source/search, tool calls, planner/critic/refine, 모든 descendant, CPU/GPU, evaluation, recovery, 실패/retry, wall time을 기록한다. equal hard ceiling 아래 실제 사용량과 quality–cost curve를 함께 보고한다. 인프라 retry는 결과 노출 전 hash-identical 조건과 최대 횟수를 미리 고정하고 비용·실패 census에서 삭제하지 않는다.
- **종결 증거:** randomized count와 artifact ledger가 일치하고, 모든 실패 유형별 수·비용이 재계산되며, per-task archive max가 primary에 없다는 독립 audit가 필요하다.

### MS-B5 — development/held-out·semantic leakage 방어가 C64 실패를 아직 흡수하지 못함 `[BLOCKER]`

- **근거:** C64는 nominal `p=.03125`였지만 task text의 global withdrawal과 graph의 edge-local withdrawal이 충돌해 causal success가 false였다(`paper/research/receipts/confirmation-closure.json:L19–L38,L69–L81`). HarnessDev의 강점은 모든 candidate를 freeze한 뒤 creator에게 보이지 않는 disjoint 630-set을 평가한 점이다(`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01437-orx-full.txt:L400–L404,L424–L443`), 다만 이는 저자 보고 protocol이다.
- **문제/영향:** deterministic scorer도 잘못된 의미를 정확히 채점할 수 있다. task family, source ancestry, prompt/schema, baseline tuning 또는 graph gold가 confirmation에 스며들면 hidden label만 감춰도 leakage다.
- **수정:** development와 confirmation을 dataset/repository/generator ancestry로 분리한다. task 선정·source snapshot·metric·gold·prompt·schema·baseline adaptation을 development 종료 시 봉인한다. scorer 작성자와 treatment 작성자를 분리하고, C64형 edge-local/global withdrawal 및 “alternative valid action” negative controls를 model 실행 전에 blinded semantic audit한다. hidden set을 연 뒤에는 후보·endpoint·winner를 다시 고르지 않는다.
- **종결 증거:** independent semantic adjudication receipt, source-to-gold locators, actual runner isolation test, zero hidden access log, post-open 변경 0건이 필요하다.

## 결정적 최소 연구

1. **Development pilot:** 위 6-family 2×2로 representation과 compulsory control을 분리한다. 목적은 효능 확정이 아니라 조작·오염·failure ceiling·분산·비용을 확인하고 두-arm confirmation을 봉인하는 것이다.
2. **Confirmation:** ancestry-disjoint 24+ family에서 `active graph control`과 `strong tree + 동일 인간가독 checklist`를 paired randomized order로 비교한다. family별 두 starts는 nested다. 시작 artifact, source rights, candidate/evaluation ceiling, model revision/thinking, public feedback와 total resource ceiling은 같다.
3. **Primary estimand:** 고정 예산 B에서 family별 최종 단일 artifact hidden score의 paired difference를 family population에 평균한 `Δ_B`. 하나의 primary contrast와 dev에서 고정한 MUE/interval만 confirmatory다. 중단·fresh-context recovery, false suppression, redundant retry, evidence-use, summary truth, actual cost는 분리 보고한다.
4. **선택 규칙:** graph는 `Δ_B`가 사전 MUE를 충족하고 safety/cost ceiling을 위반하지 않을 때만 prototype 기본값이 된다. 그렇지 않으면 strong tree를 택한다. null/negative도 유효한 연구 종료다. 사후 “비용상 우수” 구제는 별도 preregistration 없이는 금지한다.

가장 강한 대안 설명은 graph가 아니라 **더 많은 attention, active-view bytes, mandatory reviews, candidate/scorer opportunities 또는 treatment-shaped gold**가 이점을 만든다는 것이다. 같은 사실·기회·ceiling, 실제 읽은 evidence log, tree+compulsory-control arm, passive-graph ablation이 이를 닫는다.

## 재사용·격리

재사용할 것은 source receipts/46 locators, exact-byte provenance, B3의 작은 development fixture와 비용 기록(`paper/research/receipts/b3-closure.json:L22–L47`), C64 semantic-conflict regression, graph targeting/real-decision instrument다. expanded graph의 159/159은 구조 규칙만 지지하며 50 affected opportunity가 전부 immediate head였다(`paper/research/receipts/dependency-targeting-expanded-closure-v1.json:L28–L68`). real-decision packets도 external outcome 0이고 retrospective rules다(`paper/research/receipts/real-decision-packet-validation-v1.json:L214–L233`).

격리할 것은 C64 causal claim, B3 confirmation 승격, 모든 retrospective/graph/schema PASS의 efficacy 승격, UI-parity v12(30/30 pre-observation crash; `paper/research/receipts/discoveryworld-ui-parity-v12-execution-closure.json:L73–L123`), font qualification의 다섯 call 밖 일반화(`paper/research/receipts/discoveryworld-font-registry-qualification-v1-execution-closure.json:L51–L85,L146–L154`), static World-init, 그리고 HoH/HarnessDev/RecEvolve/Meta^n 저자 보고 성능을 local power prior로 쓰는 것이다.

## 원고 작성 전 완료 기준과 prototype mapping

원고 본문 작성은 (a) frozen protocol과 semantic audit, (b) powered held-out family census, (c) 모든 실패 포함 immutable outcome/cost ledger, (d) single-artifact hidden analysis, (e) interruption/recovery stress, (f) 결과에 무관한 graph-vs-tree 선택 판정, (g) 독립 재계산과 limitation table이 끝난 뒤에만 시작한다. 통계적 유의성이 없더라도 이 절차가 끝나면 null/inconclusive 논문은 쓸 수 있다.

Prototype에서는 Prime/Pi가 daemon·AgentSession·REPL/RLM·recovery/TUI를, Exa가 candidate discovery만, ORX/OpenResearch가 frozen manifest·run·artifact identity를 소유한다. Evidence/context graph는 active-control treatment이자 결과가 지지할 때만 채택할 모듈이다. Independent assessor는 self-reported PASS를 받지 않는다. Research-refine은 evidence graph와 다음 결정을 갱신하고, engine-refine은 논문 뒤 별도 lineage/promotion으로 둔다. Compression·Meta^n depth·training은 관측된 병목과 별도 실험 전에는 추가하지 않는다.

## 설명용 점수(투표 아님, 1–5)

- estimand 명료성 **2**
- 추론단위/cluster 인식 **3**
- power·noise 준비도 **1**
- held-out/leakage 방어 **2**
- selection·failure·cost accounting **3**
- 증거 경계 정직성 **5**
- paper→prototype 계보 **3**
