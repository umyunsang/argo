# 역할 4 — 회의적 독자 연구설계 검토

- **검토자 역할:** logical gaps, novelty, contribution, alternative explanations
- **packet SHA-256:** `a89c23c4c5e5fda79fc3efd2301a3c33eb3b13f1bdc8fd6a597a85bdd59e2fe9`
- **판정:** **REVISE_BEFORE_EXPERIMENT**
- **판정 범위:** 연구설계 수정 요구이며, 실험 실행·네이티브 구축·원고 작성·출판 승인이 아니다.

## 총평

자료는 설계를 고칠 만큼 충분하지만, 확증 실험을 고정할 만큼 완결되지 않았다. 가장 큰 문제는 “Pi/Prime, OpenResearch CLI, Exa, context graph, loop engineering, graph engineering을 통합한다”는 제품 방향과 “어떤 한 조작이 학술적으로 새롭고 유효한가”라는 논문 질문이 아직 분리되지 않았다는 점이다. 최신 지시는 각 요소의 연결과 소유권 및 실험으로 이기는 설계를 연구 질문으로 남기라고 한다. 반면 현재 draft는 별도의 선택 기록 없이 `research-continuity harness`를 주제로 먼저 고른다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` §Governing user direction/§What is under review, L5–13; `paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` §3–4, L21–38). 이 선택은 유력한 후보일 수 있으나 승인된 결론은 아니다.

가장 방어 가능한 후보는 **A: graph/evidence-mediated research package 대 강한 source-backed iterative baseline**이다. 기여는 도구 결합이 아니라 “동일 사실·기회·총자원에서 versioned evidence-dependency control이 실제 ML 연구의 held-out 산출물과 잘못된 근거 승계를 개선하는가”여야 한다. B는 기제 진단, C와 D는 병목 기반 후속으로 둔다.

## 차단 발견

### SR-01 — `BLOCKER`: 아키텍처 선택과 학술 contrast가 뒤섞였다

현재 비교표는 compression과 higher-order refinement를 “지금은 과도하다”는 서술로 제외하고 continuity package를 선택한다. 그러나 문헌 bundle 자체는 여덟 연구가 발전시키는 대상이 서로 달라 하나의 성능 순위로 합칠 수 없다고 경고한다 (`paper/research/long-horizon-harness-benchmark-20260907/benchmark-synthesis-ko.md` §1, L5–9). 또한 native 설계표는 Prime/Pi를 실행 기질, Exa를 discovery 후보, evidence plane을 계측, graph와 research-refine을 후보 treatment, OpenResearch를 run authority로 서로 다르게 분류한다 (`paper/research/five-reviewer-design-review-20260907/packet/paper__research__material-mechanism-evidence-map.md` §일곱 재료, L21–29). 이들을 framework head-to-head로 “벤치마킹”하면 서로 다른 문제를 푸는 계층을 비교하게 된다.

**수정:** architecture-selection DecisionRecord에서 요소를 `fixed substrate`, `common service`, `candidate treatment`, `deferred option`으로 나눈다. A–D를 scientific gap, 식별 가능한 차이, 비용·표본 가능성, null일 때의 제품 결정으로 비교한다. A를 잠정 선두, B를 진단으로 두되 결과 전에 이유를 고정한다. 대안·반증과 positive/null/negative/failed-execution의 정보가치를 요구하는 기존 계약을 따른다 (`paper/research/five-reviewer-design-review-20260907/packet/docs__argo__research-decision-contract.md` §Required decision record, L7–29).

**닫는 증거:** 해시 고정 선택 기록, A–D 비교표, reopen 조건, 논문 treatment와 제품 기질을 분리한 그림.

### SR-02 — `BLOCKER`: 신규성은 아직 “통합”이라는 이름밖에 없다

`study-contract.json`은 새 component novelty나 efficacy가 없다고 정직하게 적는다 (`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json` L7–10). 더 강하게, contribution ledger는 aggregate typed graph, portable artifact, claim lineage 같은 넓은 독창성 주장이 이미 불가능하고, exact residual도 `UNCLASSIFIED`라고 한다 (`paper/research/five-reviewer-design-review-20260907/packet/docs__argo__thesis-contribution-ledger.md` §Initial component ledger, L25–32). “다섯 상태”도 문헌 기반 재구성이며 독창성이 아니라는 bundle의 자기 제한도 타당하다 (`paper/research/long-horizon-harness-benchmark-20260907/benchmark-synthesis-ko.md` §4.1, L58–66).

**수정:** 논문 기여를 다음 하나의 조건부 주장으로 좁힌다. “자연스러운 late evidence/protocol revision과 fresh-context 경계가 있는 bounded ML research campaign에서, versioned dependency traversal과 scoped invalidation을 의무화한 정책은 강한 source-backed notebook보다 full-cost당 terminal held-out 성능을 높이고 invalid carryover를 줄이는가?” 이것은 아직 신규성 주장이 아니라 prior-art review가 확인해야 할 residual이다. Ledger가 이름만 제시한 EviGraph, claim-aware observability, XScientist, ScientistOne, Rethinking Harness Evaluation, HarnessOpt-Bench 및 dual-refinement 관련 후보는 root가 원문을 회수·완독해야 한다. 이 보고서는 그 미열람 후보를 검증된 문헌으로 취급하지 않는다.

**닫는 증거:** 원문 receipt/locator, problem–intervention–control–outcome 표, closest-work exact residual, 넓은 최초 주장을 금지한 claim ledger. residual이 같으면 reproduction/negative evaluation로 재분류한다.

### SR-03 — `BLOCKER`: 추가 숙고·검사·사람 개입이 하네스 효과로 위장될 수 있다

강한 대조군도 전체 이력과 checklist를 받지만, treatment만 preservation/gap/negative-applicability 검토와 capsule 소비를 **의무화**한다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` §7/§11, L67–74, L104–108). 동일 hard ceiling은 실제 사용 token, tool call, critique 수, 사람의 정리 시간을 같게 만들지 않는다. HoH의 저자 보고도 조건별 token이 달랐고 HoH@3 8.41M 대 Vanilla@3 6.33M이었다 (`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01481v1-layout.txt` Table 2, LF727–733). HarnessDev의 저자 보고에서는 visible feedback 방향과 held-out 방향이 64회 중 34회만 일치했고 선언본이 held-out 최선인 경우도 2/9였다 (`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01437v1-layout.txt` §4.3, LF789–792). 더 많이 평가하고 고르는 행위 자체가 효과와 과적합을 함께 만든다.

**수정:** 세 팔을 둔다. `B`는 강한 source-backed tree/notebook, `C`는 B에 동일한 schema-neutral mandatory applicability/revalidation checklist와 capsule 절차만 추가, `G`는 C와 같은 절차를 versioned typed graph traversal로 실행한다. 주 contrast는 사전 지정한 `G−B` 하나이고, `C−B`는 추가 숙고 효과, `G−C`는 graph 표현·자동제어의 증분을 진단한다. 모든 팔에 같은 raw bytes, 공개 feedback, 호출·후보·critic 기회 상한을 준다. root+descendant token, tool, compute, wall time, 금액, 실패 실행, 수동 수정 분과 작업자 수를 모두 센다. arm 전용 사람이 graph edge나 capsule을 정리하면 그 비용을 청구하고 동일 사실을 다른 팔에도 제공한다.

**닫는 증거:** prompt/action-space diff, 자원·사람 개입 ledger, 동일 input-byte manifest, opportunity audit, 비용–성과 곡선. ceiling 동일성만으로 닫지 않는다.

### SR-04 — `BLOCKER`: treatment-shaped oracle 위험이 아직 제거되지 않았다

계약은 “task generator gold mirroring treatment graph”를 금지하지만 task suite, metric, selection rule이 모두 비어 있다 (`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json` L12–22, L70–86). 기존 원고의 H3 제한 사례는 철회 뒤 정답 집합을 미리 만든 graph-operation 검사일 뿐 실제 과학 판단이 아니다 (`paper/research/five-reviewer-design-review-20260907/packet/existing-thesis-ko.qmd.txt` §Ⅲ.4, L160–162). 알려진 정답과 의도적으로 손상한 출력의 96회 검사도 scorer instrument 확인이지 agent efficacy가 아니다 (`paper/research/five-reviewer-design-review-20260907/packet/existing-thesis-ko.qmd.txt` §Ⅲ.6, L176–188). RecEvolve에서는 batch 8k→1k가 proxy를 부풀렸고 사람이 찾아 rollback했다는 저자 보고가 있다 (`paper/research/long-horizon-harness-benchmark-20260907/sources/2609.01622v1-layout.txt` §5.2, LF232–240). graph가 잘 찾도록 만든 dependency gold나 사람이 사후 구한 exploit은 독립 평가가 아니다.

**수정:** public small-compute ML programme과 hidden terminal scorer를 treatment 구현 전에 별도 curator가 schema-neutral 형식으로 고정한다. gold는 “필요한 edge를 맞혔는가”가 아니라 raw source/run을 근거로 한 최종 산출물 성능, 허용 가능한 다음 결정, 잘못된 승인·영구 억제를 판정한다. assessor는 condition label과 내부 graph를 보지 않는다. relevant/irrelevant revision stress는 일상적인 ML 변경 유형에서 만들고, 각 팔에 동일 문장과 bytes로 제공한다. 사람 rescue는 사전 규칙 밖이면 contamination으로 기록한다.

**닫는 증거:** 독립 task/gold certification, task·scorer·perturbation 선행 hash, blind scoring receipt, schema-neutral rubric, manual intervention log, 정답 접근 차단. 정적 pass는 manipulation check다.

### SR-05 — `BLOCKER`: “장기”가 실행 시간이며 과학적 의존 지평으로 운영화되지 않았다

Draft는 wall time을 늘리지 말고 결정 연쇄, 선행결과 의존, context 경계와 조건 변경을 기록하라고 맞게 말하지만 최소 지평을 정하지 않는다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` §8, L76–84). Prime Agent의 저자 보고에서도 nanoGPT 최종 기록에 대한 harness 차이는 잡음보다 작았고 (`paper/research/long-horizon-harness-benchmark-20260907/sources/2608.23552v1-layout.txt` §3.3, LF456–459), Factorio에서는 specification exploit가 재사용 skill로 보존되었다 (`paper/research/long-horizon-harness-benchmark-20260907/sources/2608.23552v1-layout.txt` §3.5, LF632–637). 오래 돌고 많이 보존했다는 사실은 과학적 누적도 효능도 아니다.

**수정:** confirmatory task eligibility에 dependency horizon을 넣는다. 각 campaign은 적어도 4개의 순차 결정, 앞 결과가 없으면 허용 행동이 달라지는 후속 결정 2개 이상, fresh-context 경계 1개, 관련 변경 1개와 무관 변경 1개를 가진다. 숫자는 pilot에서 낮추거나 늘리지 말고 confirmatory 전에 justification과 함께 고정한다. 각 결정은 source/run ID를 소비해야 하며, blind assessor가 counterfactual rationale을 판정한다. elapsed hours, loop 수, subagent 수는 설명 변수일 뿐 주 endpoint가 아니다.

**닫는 증거:** 과제별 dependency DAG, 변경 전후 결정 gold, 동등한 state-byte 권리, evidence-consumption trace, lineage 독립성 표. seed·round·candidate는 nested다.

### SR-06 — `BLOCKER`: endpoint·표본·중단 규칙이 비어 있어 어떤 결과도 결론을 못 닫는다

현재 metric, task suite, invalid handling, final selection rule은 `null`이고 confirmatory n, power, minimum useful effect도 `null`이다 (`paper/research/five-reviewer-design-review-20260907/packet/study-contract.json` L12–22, L88–100). draft도 이를 인정한다 (`paper/research/five-reviewer-design-review-20260907/packet/integrated-research-design-active.md` §12, L110–123). 효능 result와 fully certified task는 각각 0이다 (`paper/research/five-reviewer-design-review-20260907/packet/paper__research__active-graph-handoff-manifest.json` L949–952). 따라서 p-value나 static pass가 추가되어도 연구 질문은 닫히지 않는다.

**수정 및 중단 규칙:** 비확증 pilot은 task/instrument variance만 추정하고 그 task family는 confirmatory에서 제외한다. 그 뒤 independent task/source lineages 수, minimum useful effect, inference procedure, invalid-run rule, single-final-artifact selection, full budget을 고정한다. 유효한 null 또는 negative는 실패한 연구가 아니라 연구 완료다. `B`가 사전 non-inferiority 범위 안에서 더 싸면 B를 prototype으로 고른다. C가 G와 같고 더 싸면 flat mandatory ledger를 고른다. G는 사전 practical threshold와 cost cap을 모두 만족할 때만 채택한다. confirmatory contamination 또는 invalid 비율이 사전 상한을 넘으면 efficacy 결론을 중지한다. 사전에 허용한 한 번의 계측 수정 외 post-hoc rescue는 하지 않는다.

**닫는 증거:** preregistration, immutable task/scorer/environment/command/budget, power/정밀도 근거, invalid/failure accounting, 독립 review, outcome별 prototype decision table.

## 결정적 실험

1. **대상:** 공개 라이선스, 고정 split, 작은 compute로 실제 학습·분석이 가능한 하나의 일관된 ML programme 묶음. 독립 단위는 task/source lineage이며 수는 pilot 뒤 prospective precision/power로 정한다.
2. **팔:** 위의 B/C/G 세 팔. model revision, thinking, tools, raw sources, baseline code, public feedback, candidate 수, critic 수, restart 권리, hidden scorer 접근 금지를 맞춘다.
3. **자연 연구 단계:** baseline을 세우고 기제가 다른 가설 둘 이상을 실제 실행한다. 결과를 보아 다음 실험을 선택하고, 예산 종료 전에 최종 artifact 하나를 선택한다. archive best나 과제별 최고 조합은 금지한다.
4. **스트레스:** 같은 campaign의 별도 사전 지점에서 relevant late revision, irrelevant metadata revision, fresh-context restart를 적용한다. 이는 기제 진단이고 terminal ML 성능을 대체하지 않는다.
5. **주 endpoint:** hidden scoring 전에 고른 단일 artifact의 task-specific held-out 성능. **별도 endpoint:** invalid carryover, false suppression, 유효한 negative reuse, decision correctness, recovery 비용·지연, 전체 실패 포함 full cost. graph/schema 준수율은 조작 확인이다.
6. **판정:** `G−B`가 practical threshold를 넘는지 먼저 본다. C 진단으로 추가 숙고와 graph 증분을 분리한다. 모든 저자 보고 선행 수치는 prior일 뿐 예상 효과크기나 local reproduction으로 사용하지 않는다 (`paper/research/long-horizon-harness-benchmark-20260907/source-receipts.json` L28–34, L79–88, L461–470).

## 재사용할 것과 격리할 것

**재사용:** 여덟 원문의 bytes/hash와 46 locator, evolving object별 비교, source/version/claim/run provenance, exact-byte 검증, research-decision contract, 모든 launch·failure를 남기는 규칙, graph를 audit/projection instrument로 쓰는 명세. B3는 작은 allocation development evidence로만 쓸 수 있다. 기존 원고의 “그래프 연결은 진실·인과가 아니다”, “같은 모델의 역할 분리는 독립성이 아니다”, “seeds는 독립 과제가 아니다”라는 제한도 보존 가치가 있다 (`paper/research/five-reviewer-design-review-20260907/packet/existing-thesis-ko.qmd.txt` L128–146, L164–174, L190–207).

**격리:** C64는 nominal `p=.03125`와 무관하게 causal claim에 INVALID이며, UI-parity v12는 30/30 pre-observation crash로 INVALID/NOT_ADMITTED이다. font qualification은 한 host/runtime의 정확한 다섯 호출만, World initialization은 static protocol/lifecycle만 지지한다. retrospective graph/trace와 synthetic counterexample은 구조·계측 진단뿐이다. integrated efficacy는 0이다 (`paper/research/five-reviewer-design-review-20260907/packet/review-brief.md` §Evidence that can be reused, L17–26). 이 실패들은 삭제하지 않되 새 efficacy 표의 분자나 성공 사례가 될 수 없다.

가장 강한 대안 설명은 “graph가 좋아서”가 아니라 **더 많은 mandatory deliberation, 더 잘 정리된 사람이 만든 상태, 더 많은 검사·후보 선택 기회, treatment와 닮은 gold** 때문에 G가 이긴다는 것이다. SR-03과 SR-04가 닫히지 않으면 어떤 양의 결과도 이 설명을 배제하지 못한다.

## 연구 완료·원고 작성·prototype 연결

원고는 다음이 모두 끝난 뒤에만 쓴다: (1) 신규성 residual의 full-read prior-art audit, (2) A–D 선택 기록, (3) task/license/gold 독립 인증, (4) horizon·endpoint·MUE·n·budget·stop rule preregistration, (5) 비확증 pilot과 분리된 단 한 번의 locked confirmatory study, (6) 모든 실패·invalid·사람 개입을 포함한 immutable receipts와 독립 audit, (7) positive/null/negative에 따른 설계 선택. **유효한 null/negative도 완료 조건을 만족한다.** invalid-only 종료는 efficacy를 완성하지 않으며, 사전 상한에 따라 “측정 불가/feasibility failure”로 닫고 사람에게 논문 범위 변경을 요청한다.

그 뒤 writing plan은 문제·정확한 residual → evolving object/보장범위별 관련 연구 → B/C/G와 dependency horizon → preregistered 실제 ML 결과와 full cost → negative/invalid/failure 분석 → 제한과 단순 시스템 선택 순이다. 현재 원고는 경계 문구와 구조만 참고하고 새 결과처럼 갱신하지 않는다. 특히 현재 결론도 efficacy가 열린 질문이라고 명시한다 (`paper/research/five-reviewer-design-review-20260907/packet/existing-thesis-ko.qmd.txt` §Ⅴ, L294–300).

Prototype은 결과에 종속시킨다. Prime/Pi daemon·AgentSession·REPL/RLM·recovery는 공통 substrate, Exa는 discovery candidate, ORX/OpenResearch는 scientific run/receipt authority다. B가 이기면 tree/notebook과 최소 receipt importer를 쓰고 graph는 audit export로 축소한다. C가 이기면 flat mandatory ledger, G가 practical/cost gate를 넘으면 native research-state graph와 scoped invalidation을 택한다. research-refine은 선택된 정책만 구현하고 engine-refine은 별도 held-out 증거 전까지 보류한다. 이 경로가 논문 증거로 후행 ARGO/NAIS prototype을 선택한다.

## 기술 점수(1–5, 서술용)

| 항목 | 점수 | 이유 |
|---|---:|---|
| 논리적 일관성 | 3 | 계층 경계는 좋지만 선택 순서가 뒤집혔다. |
| 신규성 식별 가능성 | 2 | 정직한 제한은 있으나 exact residual prior art가 미완료다. |
| 반증 가능성 | 3 | falsifier는 있으나 endpoint·MUE·n이 비어 있다. |
| 대안 설명 통제 | 2 | token·human·oracle confound를 아직 분리하지 못한다. |
| 논문 크기 적합성 | 3 | A 하나로 고정하면 가능하나 framework 통합 전체는 과대하다. |
| null/negative 정직성 | 5 | 기존 실패를 성공으로 바꾸지 않고 단순 설계를 허용한다. |
| research→prototype 연결성 | 4 | owner 경계는 좋고, 채택 규칙만 수치화하면 된다. |
