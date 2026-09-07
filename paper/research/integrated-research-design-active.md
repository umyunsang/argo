# 통합 장기 자율연구 설계 — Sol 5인과 Fable 5.1 검토 반영 revision

상태: **RE_REVIEW_READY_FOR_TASK_QUALIFICATION_WITH_CONDITIONS · NOT_PREREGISTERED · NO_NEW_EXECUTION_AUTHORITY**
갱신: 2026-09-07
상위: `paper/research/ROOT-research-direction.md`

## 1. 연구 목적

장기 자율연구를 수행하는 harnessed LLM agents system을 최신 AI/ML 기제와 연결하고, 통합 제어 설계를 실험으로 비교해 후행 prototype의 최소 유용 구성을 선택한다. 기록용 graph는 자율연구를 지원한다. agent-visible graph 제어가 과제 성과에 필요한지는 별도 실증 질문이다. 도구 제품의 설치/통합 자체를 신규성이나 SOTA로 주장하지 않는다.

**주 RQ:** 같은 모델·근거 접근·실험 기회·전체 자원 한도에서 graph/evidence-mediated 제어가 강한 원문 기반 반복 연구보다 최종 검증 성과와 근거 승계에 추가 가치를 주는가?

typed-vs-tree 과거안, negative-result reuse pivot, compression, meta-recursion은 보존된 선택지다. 이번 revision은 graph가 승자라는 결론이 아니라 이 통합 질문을 우선 조사하겠다는 결정이다.

## 2. 정확한 설계 기록

- `paper/research/five-reviewer-design-review-20260907/integration/architecture-selection-record.json`: A–D 연구 후보와 B/C/G 개발 screen, reopen/null 규칙.
- `paper/research/fable51-design-review-20260907/integration/integrated-study-design.json`: 현행 prospective study. 검토 commit `ee7e0fdaf`; task-specific 프로토콜 값은 아직 미정이다.
- `paper/research/fable51-design-review-20260907/integration/research-completion-contract.json`: 현행 ResearchDone/단계별 승인/PublicationReady/PrototypeReadiness 계약.
- `paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json`: 재검토 후 다음 과제별 revision에 적용할 N1–N10 필수 조건. 이 조건 문서는 실행 계약이나 새 재검토 PASS가 아니다.
- `paper/research/five-reviewer-design-review-20260907/integration/owner-port-contracts.json`: 보존된 유일 owner/input/output/금지 권한 명세. 현행 study와 재검토 후속 조건의 명시적 qualifier가 우선한다.
- `paper/research/five-reviewer-design-review-20260907/integration/integrated-study-design.json`, `research-completion-contract.json`: 현행이 아닌 5인 검토 predecessor로 보존한다.
- `paper/research/five-reviewer-design-review-20260907/integration/prior-art-rebinding.json`: 넓은 기존 문헌의 exact locator 재결합.
- `paper/research/five-reviewer-design-review-20260907/integration/disagreement-resolution.json`: 리뷰 이견과 root 판단.

원검토/이견은 삭제하지 않는다. 설계 문구 수정은 empirical blocker가 닫혔다는 뜻이 아니다.

## 3. 공통 연결과 후보 차이

연구 목표 → discovery candidate → 실제 읽은 source evidence → hypothesis/experiment alternatives → frozen run intent → scientific run authority → immutable artifact → independent assessment → research-state update/refine → successor 또는 정당한 stop의 연결을 명시한다.

Prime/Pi는 process/session/REPL/RLM/recovery를, DiscoveryPort는 검색 후보를, SourceEvidenceService는 bytes/version/locator를, ORX는 scientific run을 소유한다. 연구 event/audit graph가 process나 외부 run lifecycle을 다시 소유하지 않는다. PaperService는 검색하지 않고 연구 완료 뒤 closed evidence를 소비한다. 이 owner 명세는 현재 native 구현이 아니다.

## 4. 개발 B/C/G screen

| 조건 | 공통 기질/사실 | 유일한 후보 차이 |
|---|---|---|
| B | persistent source-backed hypothesis/result/failure tree, 원문 복구, 동일 버전·적용 사실, critique/restart/validity 지침 | advisory 연구 계획·점검 |
| C | B와 동일 | schema-neutral compulsory applicability/revalidation/preservation/capsule 절차 |
| G | C와 동일한 의무·원자료 권리 | versioned graph/evidence traversal, scoped invalidation, graph-mediated continuation |

C-B는 compulsory-process package, G-C는 graph-control package의 증분이다. G-B만 보고 graph topology 때문이라 주장하지 않는다. graph만 보이는 passive arm은 실제 의문과 비용이 정당화될 때 추가한다. Reviewer의 2×2 제안은 이 조건부 대안으로 보존하며 필수 전체요인 실험으로 바꾸지 않는다.

그래프 관계는 treatment가 허용된 사실에서 생성하며 오류와 비용을 부담한다. 숨겨진 정답 관계를 주입하지 않는다. 사전 추출 관계를 공통 제공하는 control-only 진단은 별도 이름으로 둔다. 대조군이 직접 의존성 검사를 구현해도 금지하지 않으며, 실제 조작 차이와 오염은 로그로 확인한다.

## 5. 실제 연구 캠페인과 독립 평가

후보는 하나의 coherent 공개 small-compute ML task/source 묶음이다. license, ancestry, train/dev/final-test, 기제별 competing method, actual training/analysis와 다음 결정, final artifact가 있어야 한다. 기존 coding/retrieval/skill/SFT 점수는 이 연구 캠페인의 직접 대체가 아니다.

주 outcome은 예산 종료 전에 dev evidence로 선택한 **단일 frozen artifact**의 hidden task 성과다. metric/단위/정규화/무산출물 floor/invalid 처리/선택 규칙은 아직 미정이며 task 선정 후 실행 전에 고정한다. archive-best, best seed/checkpoint와 hidden-score 기반 재선택은 primary에서 금지한다.

trusted deterministic scorer는 자신의 격리된 경계에서 hidden data/test를 읽는다. planner/developer/LLM critic은 읽지 못한다. primary scorer는 treatment label과 연구 trace 없이 artifact와 frozen evaluation manifest를 받는다. 모든 final selection lock 뒤 결과를 공개한다. 사람/rubric 검토는 보조 의미 calibration이며 model-role 분리는 오류 독립성이 아니다.

## 6. 지평·자원·추론

장기는 scientific dependency horizon으로 정의한다. 앞 결과가 뒤 행동을 바꾸는지, 원자료를 실제로 사용했는지, context 경계를 넘었는지를 측정한다. 네 결정·두 dependent decision·한 restart·관련/무관한 수정은 개발 stress template 후보이며 universal threshold가 아니다. 실제 ML 과제에 자연스러운 조건을 인증하고 confirmation 전에 고정한다. 스트레스 개입은 주 metric을 사후 바꾸지 않는다.

model/provider/revision/thinking/sampling, source/first-record 권리, task split, candidate/critic/evaluation/recovery opportunity, 모든 descendant 포함 자원 hard ceiling을 일치시킨다. 결과에 따라 선택한 관측은 달라질 수 있지만 획득 권리와 기회는 같다. source extraction, graph build/update, critic, assessor, 실패/retry, cache-aware token, tool/CPU/GPU, worker time/wall time, human adaptation/intervention을 모두 기록한다. 동일 ceiling은 동일 소비가 아니므로 실제 사용량과 quality–cost를 함께 보고한다.

과제/source programme이 추론 단위다. seed/round/candidate/checkpoint와 같은 dataset/repository/generator ancestry는 nested다. 6/24 혹은 2 families를 통계적 하한으로 자동 채택하지 않는다. sample size는 dev-only variance/attrition/MUE 또는 precision/비용 계획으로 산출한다. 유의하지 않음은 equivalent/non-inferior를 뜻하지 않는다. 개발에서 선별한 후보와 최강 대조군을 confirmation 전에 동결한다.

## 7. 실패, 복구와 중단

C64형 released text–gold 불일치는 모델 실행 전에 independent semantic adjudication과 negative controls로 검사한다. 실제 runner의 hidden access 차단, owner 중복, source 승격, changed-version 재사용, external-launch ambiguity를 failing-first fixture로 확인한다. 정적 pass는 해당 contract 구현만 지지한다.

외부 run은 `RUN_INTENT_FROZEN → LAUNCH_REQUESTED → RECONCILING → RUN_ID_BOUND → TERMINAL_RECEIPT_IMPORTED`의 제안 상태로 연결하며 UNKNOWN/BLOCKED를 명시한다. ORX의 임의 request-ID lookup과 exactly-once 실행은 검증되지 않았다. at-most-once local binding만으로 외부 중복 실행 방지가 증명됐다고 말하지 않는다. 모호한 결과를 실패나 미실행으로 바꾸고 재시작하지 않는다.

모든 assigned launch/partial/crash/timeout/invalid/사람 개입을 보존한다. 과학 outcome, protocol invalid, infrastructure missingness를 분리하고 treatment-blind 사전 규칙을 사용한다. 소모된 v12/font authority는 재사용하지 않는다. frozen 실험을 outcome 뒤 수정하거나 실패를 post-hoc 제외하지 않는다.

## 8. 결과가 설계를 바꾸는 규칙

- G의 실용적 held-out 이점과 비용/안전 기준이 지지되면 G를 prototype 후보로 승격하되 native 구현 검증은 별도다.
- 충분한 정밀도에서 G-C 이점이 배제되면 더 단순한 C, B가 기준을 충족하면 B를 선택할 수 있다.
- 넓은 불확실성은 미결론이고, invalid-only는 efficacy 결과가 아니다. 제한된 feasibility 결론 또는 새 범위 결정을 따른다.
- compression·meta-depth·학습·환경 합성은 병목의 독립 근거와 별도 설계/예산 뒤에만 추가한다.

통계적 positive만 연구 완료의 조건이 아니다. 사전 규칙을 지킨 null/negative와 실패 분석도 닫힌 연구가 될 수 있다. 단순 시스템을 선택할 가능성을 남기는 것이 prototype 설계 연구의 목적이다.

## 9. 문헌·기존 실험의 재사용

최근 여덟 원문과 더 넓은 corpus의 21개 exact locator를 연결했다. EviGraph/Arbor/claim-lineage 등이 이미 유사 기제를 갖기 때문에 broad novelty를 주장하지 않는다. exact residual은 open이다. 새 task/baseline 후보 MLAgentBench/MLE-bench/PaperBench/Agent Laboratory/AI Scientist는 기존 receipts를 먼저 확인하고 필요한 primary source만 root가 회수한다.

96 scorer invocations, B3, graph/replay와 정적 witness, font compatibility는 원래 instrument/development/runtime 범위만 유지한다. C64 causal invalid, v12 INVALID/NOT_ADMITTED와 모든 실패는 변하지 않는다. World-init static branch는 보존하되 primary 연구의 무기한 선행 수리 경로가 아니다. integrated long-horizon efficacy는 0이다.

## 10. 연구 후 원고, 증거 후 prototype

ResearchDone는 task/protocol/개발·확증 분석/실패·비용/ArchitectureSelectionRecord/closed claim evidence가 완결돼야 열린다. 현재 모두 완결되지 않았고 새 본문은 쓰지 않는다. 원고를 만든 뒤 PublicationReady에서 최종 그림·metadata·숫자·원문·전 페이지를 검사한다. 최종 figure bytes를 research-before-writing gate에 넣는 순환을 제거했다.

내부 prototype crosswalk는 유일 owner와 chosen/rejected design에 연결한다. 현장 reuse 규칙과 native construction 재개 승인은 별도다. 정본 QMD·이전 exports·원본 계획서를 수정하지 않는다. 설치는 필요성과 project-local version/license/security/rollback을 확인한 경우만 판단하며 새 paid 실행을 허가하지 않는다.

현재 next: task/baseline/metric의 구체화와 owner/port capability 검증. manuscript writing이나 새 native runtime 구현이 아니다.

## 11. Fable 5.1 검토 후 현행 qualifier

현행 prospective study: `paper/research/fable51-design-review-20260907/integration/integrated-study-design.json`.
현행 완료/단계 권한: `paper/research/fable51-design-review-20260907/integration/research-completion-contract.json`.
전체 판단: 같은 디렉터리 `review-synthesis-ko.md`, `finding-response-matrix.json`. 5인 문서는 predecessor로 보존하며 이 절의 명시적 qualifier가 우선한다. 첫 Fable은 `f2e203058`을 검토했고, 뒤의 새 세션은 수정본 `ee7e0fdaf`를 조건부 task qualification READY로 재검토했다. §12의 후속 조건은 task-bound protocol에서 닫아야 한다.

- **Apparatus:** 기존 session/REPL/RLM을 사용한 task-local prompt/모듈/journal/ORX adapter/scorer의 연구 계층을 정의한다. native runtime 재개, 다른 제품 wrapper, 두 번째 process/scientific-run authority가 아니다. task-bound B/C/G 구현/실행 프로토콜 해시는 아직 없다. 공통 static byte-binding fixture만 후속 commit `ccdbf3df0`에서 검증됐으며 native/runtime 인증은 아니다.
- **R1/R2:** task 학습·후보 생성·선택 평가·hidden scoring은 ORX R1 권위에 둔다. 이미 허용된 input/output의 bounded 로컬 분석은 code/input/output/env/cost R2 receipt를 갖는다. 작은 sanity 학습이라고 권한을 우회하지 않는다.
- **조작:** B/C의 비graph 도구·원문·계산 권리는 같고 의무 gate 여부가 다르다. C/G는 의무의 실제 집행 강도를 맞춘다. G-only 도구, C의 동등 도구, prompt/capsule/context bytes는 task-bound 명세에서 고정한다. 사용 로그는 발화 증거일 뿐 topology·계산·context 효과의 인과 분리가 아니다.
- **대상과 지표:** natural/event-inclusive 중 primary 모집단은 과제 근거·outcome-blind 적합성/잡음/비용으로 고정한다. event가 없으면 G 효과가 0이라고 가정하지 않는다. 공통 event content·exogenous trigger·미도달 처리는 사전 명세한다. 근거 승계·continuation은 secondary이며 primary null 시 승격하지 않는다.
- **결측:** 모든 배정/launch/UNKNOWN/비용을 보존한다. treatment가 launch 수를 바꿀 때 whole-block 제외도 편향이므로 기본 규칙으로 기각한다. operational utility floor와 미관측 hidden 성과의 missingness를 구별하며 exact invalid rule은 metric 선정 후 동결한다.
- **봉인과 통계:** hash는 변경 탐지이며 기밀성/무노출 증거가 아니다. trusted custody·접근·reveal/사전 노출을 별도 기록한다. programme별 paired block, 순서 무작위화, ancestry와 within/between 변동을 구별한다. 두 시작은 안정된 power 증거가 아니며 MUE를 잡음에 맞춰 낮추지 않는다.
- **단계:** 새 P0 통합 feasibility(기존 SAB Stage 0와 별개), P1 개발, P2 확증을 둔다. RD4a-pre/RD4a-dev/RD4b를 각각 실행 전에 승인받는다. C feasibility/C-G confirmation은 권고안이며 미선택이다. 숫자·수리 횟수·전체 예산은 미정이다.
- **종결/후행 구현:** 중단 후 닫힌 분석·범위 결정이 있어야 연구가 완료된다. inconclusive engineering fallback은 실제 측정된 feasible/safe 후보만 대상으로 한다. 효능 승자는 여전히 없고 기존 native/test-instance 재개 조건은 변경하지 않는다.

## 12. 재검토 후 task-bound 필수 조건

`paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json`이 다음 P0/P1/P2 계약의 추가 요구사항이다. 검토된 ISD/RCC 바이트는 바꾸지 않는다. F3/F7의 집행 경계는 부분 해결이며 문구만으로 hard-gate runtime을 인증하지 않는다.

- **권한/집행:** 재검토 당시 보류였던 apparatus code 범위는 사용자 `c40c59a9`가 승인했다. 현행 제한은 `paper/research/public-ml-programme-qualification/effective-authority-v2.json`을 따른다. 공통 authority/budget/identity gate는 B/C/G 모두, 추가 compulsory 연구 점검은 C/G가 같은 trusted launch/lock locus에서 집행하는 방향이다. agent-writable journal·guard 존재만으로 우회 방지를 주장하지 않는다. 직접 실행 census와 coverage가 검증돼야 한다.
- **분류/선택:** 사전 고정한 자동 R1/R2/preparation 규칙과 사후 전수 lineage를 함께 검사한다. 새 task 학습/selection-performance score는 R1이다. 원문·데이터 진단·명시적 R1 재계산 R2는 별도 typed supporting evidence다. 사후 R1 분류가 미승인 실행을 정당화하지 않는다. 작업용 primary selection 클래스는 agent의 단일 artifact lock이며 미lock/fallback·deadline은 task 전에 고정한다.
- **MUE/단계:** MUE 또는 outcome-independent 도출 규칙은 P1 arm 대비 계산·공개 전에 commit한다. RQ/candidate·개발 선택 절차는 개발 전, exact confirmation contrast는 P1 후 P2 outcome 전에 고정한다. 모든 단계는 invalid/missingness/retry/repair/no-replacement 계약과 별도 정확한 승인이 필요하다.
- **결측/계보/비용:** process UNKNOWN, no-lock/no-artifact, lock 성공·scorer 결과·numerical observability를 분리한다. utility floor로 미관측 hidden 성과를 대입하지 않는다. scorer 한 번씩 호출했다고 비차등 결측으로 부르지 않는다. P0와 그 task/source-data/generator ancestry는 개발 측으로 기록하고 P2에서 제외한다. P0는 R1 latency·UNKNOWN/BLOCKED·gate 거부/우회·R2 위반과 각각의 분모/탐지 coverage/전체 비용을 보고한다.
- **비교군:** 이 연구의 선택적 Arbor anchor는 별도 승인된 서술적 비교만이다. causal whole-system 연구는 별도 protocol과 승인이 필요하며 여기서 생기지 않는다.

현재는 문서 수준 task qualification으로 진행할 수 있다. 다음 검토는 실제 과제·장치·평가·숫자 예산에 묶인 P0 protocol이며, 추가 일반 설계 검토나 native 구현이 아니다.


## 13. 현재 source/code fan-in과 사용자 결정

`paper/research/public-ml-programme-qualification/integration/parallel-audit-intake-v1.json`이 검증된 원문·공개 코드·현재 Prime/ORX 인터페이스의 입력이다. MLA 원문 v2는 완독했고, AgentHPOBench 논문과 pinned strict runner의 final-step 대 archive-best 차이는 프로토콜 불일치로 보존한다. published score나 코드의 CPU fallback/epoch 값은 local 성과·자원 측정이 아니다.

계정 없는 접근은 필수 조건이 아니다(`666dade1`). Kaggle 두 후보의 파일 metadata 접근을 확인했지만 약관/재배포 권한·원본 다운로드·hidden custody는 미확정이다. 계정 요구를 이유로 제외했던 원결론은 superseded이며, House Price·Spaceship Titanic·CIFAR-10·California Housing은 비교안 상태다. 최종 선택/중요 제외는 사용자 확인 후 한다. routine source 연구와 승인된 static fixture는 병렬로 계속한다.

공통 artifact-lock static fixture의 7 tests와 clean `npm run check`는 `integration/artifact-lock-immutable-validation-v1.json`에 있다. 어떤 실제 task score도 생성하지 않았으며 phase/run/hidden-scorer 권한은 닫혀 있다. 현행 authority·account policy는 같은 qualification 디렉터리의 별도 명시적 사용자 receipt를 따른다. 원 Fable 계약의 historical false/pending 값은 이 후속 승인/제한을 부정하는 값이 아니다.
