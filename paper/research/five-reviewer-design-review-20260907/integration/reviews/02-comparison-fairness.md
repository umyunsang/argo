# 비교 공정성 독립 검토 — Role 2

- **packet SHA-256:** `a89c23c4c5e5fda79fc3efd2301a3c33eb3b13f1bdc8fd6a597a85bdd59e2fe9`
- **판정:** `REVISE_BEFORE_EXPERIMENT`
- **검토 범위:** 강한 구현 가능 대조군, 비용·기회·선택 공정성, benchmark 적합성, SOTA 주장 한계
- **경계:** 연구설계 검토이며 실행·구축·원고작성·출판 승인이 아니다. 아래 선행 성능은 모두 저자 보고이고 로컬 재현이 아니다.
- **인용 경로:** 아래 `packet/`은 `paper/research/five-reviewer-design-review-20260907/packet/`, `bundle/`은 `paper/research/long-horizon-harness-benchmark-20260907/`을 뜻한다. LF는 저장 원문의 LF-delimited line이다.

## 총평

현재 초안은 단발성·무기억 agent를 대조군으로 쓰지 않고, 같은 원자료·모델·도구·평가기회·전체 예산을 요구하며, 단일 최종 산출물을 hidden evaluation 전에 고정하려 한다. 이 원칙은 강하다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` §7–8, L67–84). 그러나 실제 비교군, 공개 ML research campaign, metric, 표본수, sampling, 수치 budget과 고정 command가 비어 있다(동 파일 §12, L110–123; `packet/study-contract.json` `primary_endpoint`, L12–22; `analysis`, L88–100; `execution`, L118–132). 따라서 지금은 공정한 실험을 **설명**하지만 실행 가능한 비교를 **정의**하지 못한다.

여덟 논문을 하나의 SOTA 순위표로 만들면 안 된다. 발전 대상이 runtime/context, software artifact, reusable harness, skill library, recommender, recursive archive, 합성 환경·학습 가중치로 서로 다르다 (`paper/research/long-horizon-harness-benchmark-20260907/benchmark-synthesis-ko.md` §1, L5–9; `bundle/benchmark-matrix.json` rows, L3–147). 이 packet에서 가장 강하면서 구현 가능한 주 대조군은 외부 framework의 불완전한 복제품이 아니라, **현재 고정 Prime/Pi substrate 위의 source-backed iterative research tree/notebook**이다. 이 대조군도 raw sources, version/applicability facts, hypothesis/result/failure tree, restart, validity checklist, critique, 같은 experiment slots를 가져야 한다. Graph arm의 유일한 등록 차이는 graph가 그 동일 사실을 decision-time eligibility, selective revalidation, reopen/preservation에 강제 연결하는 control이어야 한다.

## 차단 findings

### CF-01 — 선택된 좁은 패키지가 최신 통합 목적을 아직 대표하지 않는다 (`BLOCKER`)

**근거.** 최신 지시는 graph-based autonomous research loop와 Pi/Prime–OpenResearch–Exa–context graph–loop/graph engineering의 연결 및 설계 선택을 요구한다 (`packet/review-brief.md` §Governing user direction, L3–5; §Candidate native ownership, L28–34). 반면 초안은 evidence-based continuity package를 이미 “선택”하고 typed graph를 필수 treatment가 아니라고 둔다 (`packet/integrated-research-design-active.md` §3–4, L21–38; `packet/study-contract.json` `treatment`, L47–56). 이는 폐기할 초안이 아니라 후보 B이지만, 통합 architecture 선택의 답을 선취한다.

**영향.** negative-result reuse가 이겨도 graph control plane의 필요성, representation과 executable control의 차이, 후행 prototype 소유권을 선택할 수 없다.

**수정.** 주 contrast를 `GRAPH/EVIDENCE CONTROL PACKAGE − STRONG SOURCE-BACKED ITERATIVE TREE/NOTEBOOK`으로 둔다. conditional negative reuse와 interruption recovery는 package 내부의 사전 지정 진단으로 유지한다. Graph database나 특정 orchestrator는 treatment가 아니다.

**종결 증거.** 두 arm의 state, action, information, owner/interface 차이를 한 줄씩 고정한 preregistered manifest와, 각 차이가 논문 RQ 및 prototype decision에 매핑된 표가 필요하다. 등록되지 않은 차이는 실행 전에 제거한다.

### CF-02 — “strong baseline”이 아직 실행 가능한 identity가 아니다 (`BLOCKER`)

**근거.** 초안은 좋은 기능 목록만 제시한다 (`packet/integrated-research-design-active.md` §7, L67–74; `packet/study-contract.json` `baseline`, L35–45). 저장된 공개-code 조사에서는 HoH core가 공개 tree에 없고, Prime paper와 현재 code의 실험판 동등성도 미확인이다. Scroll·Meta^n도 선택 파일만 검사했고 실행하지 않았으며, SkillZip/RecEvolve/Terminal-Universe canonical code는 식별되지 않았다 (`bundle/public-code-snapshot.json` L5–24, L27–55, L58–113, L116–129).

**영향.** 임의의 약한 prompt를 “strong”이라고 부를 수 있고, HoH/RecEvolve/Scroll 재현을 암시할 위험이 있다.

**수정.** baseline을 현재 substrate에서 직접 고정한다: exact code/config/prompt hash, state schema, available actions, raw-source expansion, restart/handoff, checklist, critique와 experiment opportunity를 명시한다. baseline도 code/REPL로 dependency check를 자발적으로 구현할 수 있어야 한다. 외부 이름은 `inspired by` 또는 `mechanism-matched`로만 쓴다. Full-system reproduction은 공식 code/commit, dependencies, task adapter, model settings, scorer와 reference score가 모두 검증될 때만 허용한다.

**종결 증거.** 양 arm의 runnable manifest, byte hashes, code-path activation receipt, prompt/config adaptation budget ledger, blinded pre-run audit가 필요하다. 정적 activation은 비교 identity만 닫으며 efficacy는 닫지 않는다.

### CF-03 — 연구 campaign benchmark와 추론 단위가 미확정이다 (`BLOCKER`)

**근거.** 후보는 “공개 tabular ML 또는 작은 최적화” 수준이며 task suite와 gold가 없다 (`packet/integrated-research-design-active.md` §6, L53–65; §12, L123). HoH는 같은 software artifact의 3-loop와 한 개 70-loop 사례이고 (`bundle/hoh-method-audit.md` §1, L16–22), Scroll은 long history retrieval/acting, SkillZip은 skill execution, Terminal-Universe는 corpus/SFT를 평가한다. 이들은 실제 ML 연구 campaign의 직접 대체가 아니다. packet도 retrospective replay가 실제 ML outcome/training cost를 대체하지 못한다고 명시한다 (`packet/review-brief.md` §Feasible study choices, L36–43).

**영향.** 긴 trace, tool turn, candidate run, seed를 독립 장기 연구 성공으로 잘못 셀 수 있다.

**수정.** 서로 독립인 공개 task/source family들로 한 coherent small-compute ML bundle을 인증한다. 각 campaign은 동일 starting baseline, 적어도 두 competing hypotheses, 실제 train/evaluate 결과에 따른 후속 결정, 고정 split/metric, 중간 interruption, 하나의 최종 artifact를 가져야 한다. campaign/family가 추론 단위이고 seed·round·candidate·checkpoint는 nested다.

**종결 증거.** license/data/source ancestry, train/dev/hidden-test split, failing/invalid rule, task-specific metric과 공통 estimand, task-family independence audit, development/confirmation 분리, power 또는 precision 계산이 있는 frozen task certificate가 필요하다.

### CF-04 — equal ceiling만 있고 완전 비용·sampling·실패 회계가 고정되지 않았다 (`BLOCKER`)

**근거.** 초안은 token/tool/compute/wall-clock과 root+descendant를 열거하지만 수치는 null이다 (`packet/study-contract.json` L24–34, L88–100, L118–131). HoH의 3-pass 비교는 71.52/8.41M 대 58.24/6.33M으로 token-matched가 아니며 scorer cost를 제외한다 (`bundle/sources/2609.01481v1-layout.txt` Table 2, LF727–733; `bundle/hoh-method-audit.md` §5.1, L108–126). HoH는 transport failure를 대체하여 원 attempt를 score denominator에서 뺀다 (`bundle/sources/2609.01481v1-layout.txt` Appendix B.2, LF1471–1475). RecEvolve는 model/version, sampling, token/cost, complete run denominator가 없다 (`bundle/recevolve-claim-audit.md` §3, L77–86).

**영향.** Graph arm이 더 많은 preprocessing, retrieval, critic 또는 retry를 받아 이기거나, baseline이 budget exhaustion을 더 자주 겪어도 원인이 숨는다.

**수정.** model ID/revision/thinking, temperature/top-p/seed 또는 provider nondeterminism, context cap, cache policy, tools, source rights, experiment/critic/recovery slots와 작은 budget grid를 고정한다. 실제 input/output/cache-aware tokens, search/source reads, graph build/update/traversal, root+child work, ORX CPU/GPU, assessor, retry, failed launch, human intervention, summed worker time, wall time을 모두 기록한다. 같은 ceiling을 주되 억지로 소진시키지 말고 quality–cost frontier를 보고한다. Transport replacement는 과학 outcome과 별개로 원 launch 및 비용을 보존한다.

**종결 증거.** 값이 채워진 cost schema, pricing/runtime snapshot, 모든 admitted attempt의 population-flow ledger, intention-to-run failure policy, budget-grid 분석 코드와 pre-outcome checksum이 필요하다.

### CF-05 — selection leakage와 SOTA 문구의 차단 규칙이 더 명시적이어야 한다 (`MAJOR`)

**근거.** HarnessDev에서 feedback/held-out 방향 일치는 34/64이고 declared final이 held-out 최선인 경우는 2/9뿐이다 (`bundle/sources/2609.01437v1-layout.txt` §4.3, LF789–794). Meta^n archive-best는 task별 서로 다른 chain 최대의 portfolio statistic이지 하나의 deployable chain이 아니다 (`bundle/sources/2608.24735v1-layout.txt` §2.4, LF365–372; `bundle/meta-environment-audit.md` §1.3, L43–58). Terminal-Universe는 실패 suffix를 자르고 성공 자료를 고르는 training-corpus 규칙이며 연구 성공률 규칙이 아니다 (`bundle/sources/2609.04148v1-layout.txt` §3.3, LF407–412; `bundle/meta-environment-audit.md` §2.4, L111–124). Scroll의 published-system 표는 backbone이 다른 reference이지 controlled comparison이 아니다 (`bundle/sources/2608.21690v1-layout.txt` Table 2, LF433–438). 현재 bundle도 selection week가 검증되지 않았다 (`bundle/source-receipts.json` L462–470).

**영향.** archive-best, best seed/checkpoint, chosen success, 외부 headline 또는 학습된 student gain을 harness SOTA로 바꿀 수 있다.

**수정.** dev evidence만으로 final artifact 하나를 선택·동결한 뒤 hidden score를 한 번 primary로 연다. 모든 archive/candidate/seed와 실패는 진단 분모에 남긴다. Frozen router를 주장하려면 router 자체를 먼저 고정하고 그 정책의 unseen-family score를 낸다. Teacher, task generation, SFT, model-weight 변화는 별도 연구이며 frozen-harness primary와 섞지 않는다.

**종결 증거.** timestamped final-selection receipt, hidden-test access log, all-candidate ledger, held-out 재선택 금지, 독립 scorer calibration이 필요하다. SOTA라는 말은 아래 조건까지 금지한다.

## 최소 staged comparison과 결정적 실험

1. **Stage 0 — task/protocol qualification, 무효능.** 개발 family에서 environment, split, metric, hidden scorer, failure semantics, campaign 길이와 비용 분산을 확인한다. 이 자료로 최소 유용효과와 표본수를 고정한다.
2. **Stage 1 — 유일한 confirmatory package contrast.** `B`는 위 strong source-backed tree/notebook, `G`는 동일 tree/facts에 typed source→claim→hypothesis→experiment→result→decision/successor graph와 mandatory eligibility/reopen/preservation traversal만 추가한다. 둘 다 같은 Prime/Pi session substrate, 같은 frozen discovery corpus와 Exa 후보 접근 상한, 같은 ORX run authority, 같은 model/tools/opportunities/budget을 쓴다. 새로운 evidence는 각 arm의 선택 결과로 달라질 수 있지만 시작 사실, eligible sources와 획득 기회는 같다. Oracle applicability edge나 hidden answer를 G에 주지 않는다.
3. 각 held-out campaign에 사전 지정 interruption을 한 번 넣는다. 최종 artifact는 hidden scoring 전 선택한다. **Primary**는 고정 budget에서 그 artifact의 독립 task metric이다. 비용, valid scientific decision, unsupported claim, redundant retry, false suppression, regression, recovery 정확도는 별도 secondary다. Schema/edge completeness는 manipulation check다.
4. **Stage 2는 조건부.** G가 사전 지정한 실용효과와 uncertainty/cost gate를 넘을 때만 `graph representation without compulsory control` 대 `full graph control`을 비교한다. Compression, Meta^n depth, training, model change, task synthesis는 관측 병목이 있을 때 각각 별도 후속 연구로 연다.

가장 강한 대안 설명은 “graph가 더 나은 reasoning을 만든 것이 아니라, 더 많은 정답성 metadata·context·critic calls·preprocessing과 selection 기회를 받았다”이다. 위 동일 정보권·opportunity와 full-cost 회계, representation/control ablation이 이를 닫는다. 또 다른 설명은 task generator/scorer가 graph schema를 공유해 G에 유리한 것이다. 외부 task metric과 treatment-blind semantic audit가 이를 닫아야 한다.

## SOTA 주장 조건

현재 허용되는 문구는 “사전등록된 mechanism-matched strong baseline 대비, 명시한 protocol에서의 결과”까지다. SOTA는 다음이 모두 있어야 한다.

- cutoff·query·screening·제외 사유가 남은 최신 primary-source landscape. `The AI Scientist-v2`, Arbor, Agent Laboratory, MLAgentBench/MLE-bench 계열은 **root가 원문을 새로 확인할 후보**일 뿐 이 검토에서 검증된 선행결과가 아니다.
- 같은 연구 object와 public benchmark를 다루는 적어도 하나의 공식·pinned·실행 검증 comparator, 또는 full reproduction이 불가능하다고 명시한 뒤 SOTA를 포기한 mechanism-matched 비교.
- 동일 model/revision, tools, source/evaluation opportunities, adaptation budget와 full cost에서 frozen final의 held-out family 결과 및 적절한 uncertainty.
- 외부 reference number, archive maximum, success-filtered corpus, teacher/task/scorer 동시 변경, student SFT gain을 직접 비교에서 제외.

## 재사용·격리와 원고 전 완료 기준

**재사용:** 여덟 원문 receipt/46 locators, object별 benchmark matrix, exact-byte provenance, HoH의 frozen-candidate/QA 분리, HarnessDev의 feedback/held-out 선택 경계, Scroll의 raw-addressability, SkillZip의 structural-not-semantic 경계, RecEvolve의 조건부 negative history 동기, Meta^n의 archive 구분, Terminal-Universe의 observed/inferred 및 selection ledger 구분.

**격리:** B3는 작은 allocation 개발자료, C64는 인과 무효, retrospective graph/replay는 기제 fixture, UI-parity v12는 30/30 pre-observation crash, font는 정확한 5-call host/runtime 호환성뿐이다 (`packet/review-brief.md` L17–26). 여덟 논문의 수치도 저자 보고다. 이들을 local efficacy, SOTA, campaign 표본수 또는 power prior로 쓰지 않는다.

원고 작성 전에는 (1) 최신 비교문헌 원문·code 상태 audit, (2) frozen task/protocol/budget/sampling/failure/selection 계약, (3) baseline과 G identity/activation audit, (4) development와 held-out family 분리, (5) Stage 1의 모든 launch·실패·비용을 포함한 종결, (6) preselected final의 독립 score와 uncertainty, (7) null/negative까지 포함한 DecisionRecord, (8) 주장별 immutable locator/result binding이 필요하다. Research completion 뒤에도 출판 경계 검토는 별도다.

## prototype mapping

Stage 1이 통과하면 Prime/Pi는 process/session/recovery를, Exa는 discovery candidate만, research graph는 versioned evidence/decision projection과 control을, ORX는 scientific run/receipt authority를, assessor는 hidden score를 각각 유지한다 (`packet/review-brief.md` L28–34). Graph 이점이 null이거나 full cost로 사라지면 자동 control을 채택하지 않고 tree/notebook을 주 설계로 두며 graph는 audit/export projection으로 축소한다. 이는 후행 prototype 선택 규칙이지 현재 구현 승인이나 논문 기여가 아니다.

## 기술적 점수(설명용, 1–5)

| 항목 | 점수 | 이유 |
|---|---:|---|
| 대조군 개념 강도 | 4 | 약한 baseline을 피하지만 runnable identity는 없음 |
| benchmark 직접성 | 2 | 실제 public ML research campaign/gold가 미정 |
| 정보·기회 공정성 | 4 | 원칙은 좋으나 graph construction과 oracle edge 통제가 미고정 |
| 전체 비용·sampling 회계 | 2 | 필드만 있고 수치·실패/가격/sampling 계약이 없음 |
| selection/held-out 규율 | 4 | final-artifact 원칙은 좋으나 archive/router/SOTA 금지 규칙 보강 필요 |
| SOTA 주장 준비도 | 1 | 직접 재현 comparator와 최신 landscape closure가 없음 |
| 후행 prototype 결정 가능성 | 3 | ownership 가설은 명확하나 선택 실험이 아직 좁음 |
