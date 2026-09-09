# ARGO 연구 방향 검토 — 2026-09-05

> 원본 추가 제공 후 정정: `.planning/2026-09-05-argo-source-reconciliation/source-addendum.md`를 함께 읽는다. 이 문서의 36시간 신청서 지적은 이전 Downloads 사본에만 해당하며 현재 제공 APP에는 없다. 해커톤 배점 미확인은 제공 모집 공고 p.3으로 해소됐다. 본선 기간 내 개발은 공고 p.5의 명시 조건이다. 아래 검토는 당시 확인 범위를 보존한 기록이며 이 세 사실은 후속 정정이 우선한다.

## 판정

**목표는 적절하나, 현재 설계가 사용자의 연구 목적을 충분히 식별하거나 SOTA 경쟁력을 입증하는 상태는 아니다.** 최근 연구는 중단·공회전이 아니라 채점 및 실행 격리의 실제 보강이다. 그러나 이를 넘어, **근거를 읽고 경쟁 가설과 실험을 선택한 뒤 결과에 따라 다음 연구 결정을 바꾸는 능력**을 주된 검증 대상으로 삼아야 한다.

이 문서는 현재 파일·영수증·세션 기록과 세 개의 독립 읽기 전용 검토를 종합한 연구 지시의 근거다. 신규 효능 실험이나 native ARGO 구현을 수행한 보고서가 아니다. 연구 방향 선택의 제안과 검증된 사실을 구분한다.

## 확인한 현재 상태

- 초기 HEAD: `aa5f35ce59b97a64404efc643527eb8673921305`. 기존 scorer 두 파일의 수정과 untracked 연구자료를 보존했다.
- 세션: `argo-paper-root`, saved ID `01a05f13-5001-77c8-8530-d92634405424`, live handle `d28d851bde93`.
- 10분 heartbeat로 실제 작업이 진행된다. 2026-09-05 04:11 KST에 agent/observer 격리 확인 후 probe를 시작했고, 04:22 KST에는 agent syscall 격리 통과와 scorer probe 준비를 보고했다. 이는 세션 보고이며 모든 raw syscall을 이번 검토에서 재판정한 것은 아니다.
- task-certification-v4 영수증은 scorer 대상 16과제, evaluator 96회, output manifest 96개 재도출, 변조 fixture 6/6 탐지를 기록한다. 동시에 `fully_certified_task_count=0`, `model_calls=0`, `experiment_authorized=false`다. **채점 장치 검증과 에이전트 성능 검증은 다르다.**
- roster cwd는 여전히 정지된 LG Aimers 경로지만 transcript header는 이 worktree다. 후속 실행은 절대 cwd를 기록해야 하며 LG Aimers에 접근·실행하지 않는다.
- `docs/argo/agent-brief.md` 및 `docs/argo/migration-state.json`의 native construction pause는 유지된다. Python 연구 harness는 명세·시험 장치이며 제품 runtime이 아니다.

## 우선 수정사항

### P0. 측정 대상이 연구 목적보다 좁다

현재 Stage 1은 주어진 scientific-computing 과제의 실행 점수를 측정하고, F는 non-oracle protocol-validity signal을 받는다. 이것만으로 문제·가설·변별 실험을 자율적으로 더 잘 선택한다고 결론낼 수 없다. 세 개의 end-to-end 사례는 시연일 뿐 이 간극을 메우는 인과 표본이 아니다.

근거: `.planning/2026-09-04-argo-paper-research-audit/review-packet/11-integrated-experiment-design.md:56`, `05-preregistration-draft.md:109`.

**수정:** 경쟁 가설 → 구분 가능한 예측 → 선택한 실험 → 허용된 관측 → 다음 연구 결정의 한 연결고리를 주된 실험 단위로 명세한다. generic iteration과 비교할 때 후보 생성·검토·수정 기회 및 모델/자료/예산을 맞춘다. 규칙 기반 채점은 사전 정의된 증거·제약과 결정의 일치만 측정하며, 과학적 참·보편적 참신성을 자동 인증한다고 주장하지 않는다.

### P0. 활성 문서와 그래프의 권위가 분열돼 있다

`paper/research/material-mechanism-evidence-map.md:16`은 격리된 T3/B0/B1 수치로 채택을 정당화하고, `:20`은 B2 관측을 채택 근거로 쓰며, `:21`은 pivots=0을 과제 난이도 탓으로 단정한다. 원인 확인 없이 “구현은 정상”이라고 쓸 수 없다.

`paper/context-graph.json:8215`는 시뮬레이션 결과를 RETRACTED로 표시하지만 `:14845`의 역사적 supports edge는 그대로다. 역사 보존 자체는 허용되지만 활성 claim projection이 반드시 이를 배제해야 한다. 새 overlay는 `DRAFT_NOT_APPLIED`; `.orx/paper_validate.py:2039`는 canonical graph를 직접 읽는다. 따라서 overlay 검증을 canonical 소비자 전체의 수리로 간주할 수 없다.

**수정:** 과거 자료를 지우지 말고 supersedes/retracts 및 단일 active projection/entrypoint를 정한다. 미적용 overlay는 명시적으로 미적용으로 남긴다. 모든 소비자는 채택 이유를 `architectural choice / prior-art motivation / instrument finding / demonstrated efficacy`로 구분한다. 오래된 결과에 의존한 결론은 재개방한다.

### P0. 검정력 조건이 성공 조건과 충돌한다

`05-preregistration-draft.md:80`은 조정 신뢰구간의 하한이 +0.10을 넘어야 성공이라고 정한다. `:101`은 실제 효과 +0.10에서 80% power를 요구한다. 전자는 사실상 `H0: delta <= 0.10`인 검정이다. 참값이 그 경계일 때 보정된 검정의 기각 확률은 명목 오류 수준 이하이지 80%가 될 수 없다. 이는 이 문서의 수학적 해석이며 추가 실험으로 해결할 문제가 아니다.

**수정 대안:** (A) `H0: delta <= 0`에 대해 `delta=0.10`에서 power를 설계하고 실제 유용성은 추정치/구간으로 별도 해석하거나, (B) 최소유용차이 `delta0=0.10`을 검정하되 power용 대립가설 `delta1>delta0`를 타당한 근거로 정한다. 연구 질문에 맞춰 하나를 선택해야 한다. n=16, 네 개발 과제, 13개 검정도 관행적 필수값이 아니라 분산 불확실성과 비용에 따라 재설계할 선택지다.

### P1. 비교군이 약하면 기능 묶음의 효과만 나온다

equal-content G0와 fixed substrate는 개선이다. 하지만 G에는 표현·gate·operation, C에는 후보 수·독립성·critic·admission, F에는 추가 revision 기회가 함께 변한다. 같은 최대 예산만 주었다고 같은 추론 기회를 제공한 것은 아니다.

근거: `02-treatment-manifest.json:5`, `02-treatment-manifest.json:311`.

**수정:** 비교하려는 차이를 정확히 한정한다. 경쟁 선택을 시험하면 동일 후보 pool과 동일 심사 정보에서 선택 정책을 비교한다. 독립 생성의 효과를 시험하면 선택기는 고정한다. graph 표현 효과를 시험하면 양쪽에 동일 사실·관계 정보 및 동일 admission 규칙을 주고 접근/계산 방식만 바꾼다. 분리가 불가능하면 솔직히 결합 정책의 효과로 명명한다. 실제 토큰·비용·시간과 동등 budget slice의 성능도 함께 보고한다.

### P1. ALL-ON이 모든 조합을 이겨야 할 이유가 없다

`05-preregistration-draft.md:41`의 `RA=S*P^3`는 이진 점수에서 `S=P`이므로 `P^4`가 된다. 실패를 여러 번 비선형 벌점화하는 효용의 근거가 필요하다. `:87`의 FULL 대 나머지 7개 모두 +0.10 우위는 효율적인 ARGO 설계보다 기능 축적을 유도할 수 있다.

**수정:** 공식 task score, 결정 적합성, reliability, 비용을 분리한다. 핵심 contrast 한 개를 먼저 선택하고, factorial interaction과 모든 조합 우월성은 추가 자원으로 식별 가능한 경우에만 후속 연구로 둔다. 적은 기능 조합이 더 좋으면 그것을 선택하는 것이 연구 목적에 맞다.

### P1. 그래프 도구의 존재와 연구를 제어하는 그래프는 다르다

`experiments/study_b/harness/extensions/b2_harness.js:100`에는 실제 `graph_query`가 있으므로 “쓰기만 한다”는 단정은 틀리다. 다만 `:13`은 빈 메모리 상태로 시작하고, inspected extension에는 저장 상태 복원이나 관계 쓰기 연산이 없다. `:35`의 gate는 특정 graph-backed decision과 실행을 연결하지 않고 아무 decision/threshold의 존재를 검사한다. `:196`의 pivot 카운트도 bounded graph-state transition을 보장하지 않는다.

독립 점검 결과 canonical 487 nodes/879 edges, overlay 105/176이다. 활성 결합 view의 104 nodes는 전부 overlay 출신이다. 104/104 reachability는 이 slice의 구조 검증이지 전체 역사 수리나 과학적 효과가 아니다. 선택 행 15개에 locator가 있어도 각 선택/기각 대안에서 원문 span·반례로 가는 typed edge는 별도 확인해야 한다.

**수정:** `snapshot/query → evidence IDs → alternatives → admitted decision → allowed action → run/result → next decision`을 관측 가능하게 만든다. 새 문맥의 다른 agent가 source span과 graph revision만 받아 동일하게 허용되는 다음 행동 및 금지 근거를 복구하는지 검사한다. 정답 문구 일치가 아니라 결정 계약 충족을 평가한다.

### P1. 통합 설계는 구성요소 목록에서 끝나면 안 된다

현재 문서에는 소유권 원칙은 있다. `packages/coding-agent/docs/architecture.md:43`의 session lifecycle, `docs/argo/paper-pipeline-contract.md:59`의 injected PaperService, `docs/argo/migration-plan.md:52`의 receipt-first ORX integration, `:66`의 research/engine refine 분리는 보존해야 한다.

**수정:** 각 재료에 대해 `학술 기제 / 직접 읽은 근거 / 다른 선택지·반례 / native owner / 입출력 계약 / 측정 signature / 비교군 / MVP 또는 후속`을 한 표로 연결한다. Pi/Prime을 고정 기질로 사용해도 출처·라이선스는 숨기지 않는다. 제품명 자체를 과학적 기여로 사용하지 않는 것과 구현 attribution을 생략하는 것은 다르다.

## 추천하는 최소 핵심 연구 — 설계 후보, 아직 사전등록 아님

**주 질문:** “동일한 증거·도구·추론 기회 아래, 버전·반증·실험 계보를 반영하는 연구 상태가 단순 기록/일반 반복보다 증거에 맞는 다음 실험 선택과 교차-agent 인계를 개선하는가?”

선택 이유: 기존 execution benchmark를 폐기하지 않으면서 사용자 목적의 빠진 변수를 직접 측정하고, 첫 prototype 경로와 같은 동작을 시험할 수 있다. 처음부터 8개 조건·검색·복구·13개 검정을 모두 요구하는 것보다 무엇이 유용한지 먼저 판별한다. 이 우선순위 자체도 기존 GCF 전체 설계와 대조하여 선택/기각 이유를 기록해야 한다.

1. 공개 연구/재현 과제에서 competing explanation과 관측 가능한 예측이 있는 episode 후보를 고른다. 사전 정의된 정답·제약의 독립 근거가 없는 문제는 자동 primary scoring에서 제외하고 qualitative로 둔다.
2. task family별 개발/평가 분리를 한다. 같은 문제의 seed만 바꾸어 표본 수를 늘리지 않는다. 자료 접근 범위, baseline 해결 가능성, floor/ceiling을 개발에서만 확인한다.
3. 고정 자료 pack에서 두 대안, 구분 실험, 사전 기대 결과와 중단/수정 조건을 생성한다. held-out 평가기는 agent 및 자기 작성 verifier와 분리한다.
4. negative/null/contradictory evidence가 공개되는 경우 다음 행동을 평가한다. 무조건 pivot을 장려하지 않는다. 기존 설계 유지·보류·수정 중 정당한 결정을 인정한다.
5. flat-state generic iteration을 해석용 baseline으로 두고, 문헌 검토에서 확인한 proximity-guided competition 또는 결과 기반 experiment-tree 중 가장 가까운 강한 active comparator를 주 contrast로 선택한다. 후보/검토/수정 기회가 같아야 한다. representation 또는 policy 묶음 중 무엇을 비교하는지 미리 고정하고 개선이 추가 예산 때문인지 별도로 해석한다. 원 시스템 전체를 재현하지 않았다면 mechanism-matched comparator라고 명명한다.
6. primary는 independently checkable decision-contract success로 좁힌다. official task score, invalid claim reuse, 불필요한 반복, 인계 충실도, 비용은 별도 측정한다. 단순 schema 충족률을 과학적 우수성으로 이름 바꾸지 않는다.
7. task/episode가 추론 단위이며 반복은 nested다. 한 주 contrast, 효과크기/오류/검정력 또는 탐색적 precision 목표, 결측·실패·재시도 규칙을 사전 고정한다. 독립 근거 부족 시 exploratory로 보고하고 강한 주장을 하지 않는다.
8. 추가 ablation은 첫 결과가 구별하지 못하는 설명을 가르는 경우에만 선택한다. 불필요한 graph/critic/refine이 이기지 못하면 더 단순한 설계를 ARGO 후보로 남긴다.

## 설계할 native 연결 경로

`원문 수집 → 검토된 source span → 대안/반증 관계 → 결정 → scientific run receipt → 결과 → 연구 상태 갱신 → 다음 결정/인계`

| 경계 | 설계 계약 | 하지 않을 일 |
|---|---|---|
| Pi / Prime 기질 | native worker·AgentSession·REPL/RLM·복구를 보존 | 추가 orchestrator로 lifecycle 중복 |
| Exa 등 검색 | 발견 URL → 저장 bytes/hash → 실제 읽은 span → 적용 범위가 있는 evidence | 검색 snippet으로 claim 승인 |
| Context / graph engineering | instance별 append-only event와 버전 projection, typed 관계와 revision-aware query | snapshot만 공유하고 소비 경로는 불명 |
| OpenResearch CLI | 지정 scientific run authority의 protocol/run/code/environment/output ID를 receipt importer로 연결 | 별도 scientific run registry 복제 |
| Loop engineering | scientific-state successor는 evidence에 따라 생성; engine 변경은 별도 held-out promotion | engine patch가 기존 scientific result를 소급 변경 |
| 다른 agent 인계 | instance ID, snapshot hash, decision revision, evidence spans, 허용 write와 next action 계약 | 사적 대화 전체 복사에 의존 |

이는 설계 요청이다. native 구현 재개는 기존 validation 및 사용자 재개 승인 이후다.

## NAIS 시간·출처·현장 경계

2026-09-05 현재 공식 웹페이지의 본선은 **2026-09-30 17:00–2026-10-01 12:00 KST, 19시간**이다. 신청 기간은 8월 6일–9월 7일이다. hackathon-specific 가중 평가표는 확인하지 못했고 AI Art의 평가 가중치를 가져오지 않았다.

사용자 제공 신청서에는 개발을 현장에서 하고 다른 대회의 private data나 미리 만든 산출물을 사용하지 않겠다는 내용이 있다. 같은 신청서의 36시간 계획은 현행 19시간과 충돌한다. 원본은 고치지 않고 현재 계획 addendum을 만든다. `paper/research/external-event-facts-receipt.json:43`의 “19시간이므로 사전 prototype이 사실상 완성돼야 한다”는 추론은 철회해야 한다.

공개 OSS, 사전 설계·자료 및 코드 사용의 정확한 허용 범위는 주최 측 세부 규칙 확인 전까지 확정하지 않는다. 연구 worktree를 준비하는 일과 그 산출물을 본선에 반입하는 일은 구분한다. 기존 clean-room 방침은 유지하며 이번 검토에서 외부 문의·제출은 하지 않는다.

**제안 19시간 MVP 계획:** 0–2h 규칙/공개 의존성/환경, 2–7h source→대안→결정→한 실행, 7–11h 결과 기반 한 번의 refine와 graph 표시, 11–14h 새-context 인계와 negative case, 14–17h 통합 재실행/오류수정, 17–19h 시연/설명/제출 버퍼. 이는 새 일정 제안이지 공식 시간표나 실현성 검증 결과가 아니다. engine self-modification·광범위 분야지원·대규모 benchmark는 MVP에서 제외한다.

## 다음 산출물과 진행 판단

기존 설계를 대체하는 또 하나의 거대 framework 대신, 아래 네 산출물을 현재 연구의 단일 entrypoint에서 연결한다.

1. **통합 연구설계:** 핵심 가설 1개, 강한 비교군, 왜 그 실험이 대안을 구별하는지, sampling/metrics/power-or-precision/cost/stopping, positive/null/negative별 설계 변경.
2. **기제–구현 계약표:** 원문 근거·반례·native owner·interface·signature·ablation·MVP, 연구 harness와 미래 제품의 경계.
3. **활성 graph 인계:** canonical/overlay/retraction precedence와 선택별 evidence edge, 새-context next-action 복구의 측정 명세. 미실행은 미실행으로 기록.
4. **다음 실행 manifest:** 가장 작은 정보성 실험 한 개, 실제 command/cwd/input hashes/expected observations/cost/필요 승인. 승인 없는 값은 null로 남기고 launch하지 않는다.

현재 진행 중인 무과금 격리 probe는 결과를 수집하여 좁은 범위의 성공/실패를 닫는다. 새로운 직접 위험이 없으면 인증 항목을 계속 늘리는 대신 위 과학적 설계 작업으로 이동한다. 실패 시 exact blocker와 최소 수정만 기록한다. heartbeat는 완료·의사결정·새 증거의 변화를 보여야 하며 HOLD 문장 반복을 진척으로 세지 않는다.

## 증거 범위

- 이번 root 및 두 저장소 검토자는 test suite, agent efficacy episode, 유료 model job을 실행하지 않았다. 영수증을 읽은 사실은 root가 실험을 재수행한 사실이 아니다.
- 공식 HTML/JS를 현재 HTTPS로 다시 읽고 보관했다. JS SHA-256은 기존 receipt와 동일하나 이번 파일의 byte count는 577579다. 기존 `asset_bytes=559838`와는 count 표기 불일치이며 내용 변경 증거가 아니다.
- 졸업논문계획서와 NAIS 신청서를 읽었으나 개인정보는 이 산출물에 복사하지 않았다.
- 과거 audit 메모는 탐색 힌트로만 사용했고 현재 세션을 과거의 stopped 상태로 오인하지 않았다.
- 문헌별 직접 비교는 `literature-challenge.md`에 별도 기록한다. 인용 가능한 지위와 원문 적용 범위를 벗어난 SOTA 주장은 허용하지 않는다.
- 문헌 검토는 Co-Scientist 및 The AI Scientist의 2026 Nature 출판과 graph/tournament/tree/refine의 선행 존재를 확인했다. 따라서 넓은 graph-conditioned choice도 신규성이 확정된 표현이 아니다. 원문 evidence dependency의 무효화·선택적 재계획·인계라는 좁은 차이를 경쟁 검증할 후보로 삼는다.
