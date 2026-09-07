# 연구 방향과 목적 — ROOT active entrypoint

상태: **USER_AUTHORIZED_TOPIC_PIVOT · RESEARCH_ONLY · NATIVE CONSTRUCTION PAUSED**
갱신: 2026-09-07

## 1. 현재 방향과 권위

사용자는 최근 제시한 AI/ML 연구에 맞게 졸업논문과 연구 방향을 변경하도록 허용했다. 유지할 중심은 **장기 자율연구를 수행하는 harnessed LLM agents system**이다. 이 명시적 지시는 이전 typed-vs-tree 필수 주제와 DiscoveryWorld 필수 경로보다 우선한다.

- 사용자 지시와 범위: `paper/research/autonomous-research-harness-pivot-20260907/user-direction.json`
- 새 연구계획: `paper/research/autonomous-research-harness-pivot-20260907/research-direction-ko.md`
- Active 방법: `paper/research/integrated-research-design-active.md`
- 현재 인계: `paper/research/active-graph-handoff-manifest.json`
- 다음 행동: `paper/research/next-experiment-manifest.json`

기존 entrypoint/design 원문은 `paper/research/autonomous-research-harness-pivot-20260907/predecessor/`에 보존했다. 과거 관측과 승인된 실험 계약은 변경하지 않는다. 공식 계획서 PDF와 지도교수/학과의 주제 변경 승인 여부는 별개이며 확인되지 않았다.

## 2. 새 연구 목적

고정 자원에서 가설–실험–해석–다음 결정을 반복하는 에이전트가 **검증된 성과를 축적하고, 실패를 조건부로 재사용하며, 중단 후 연구를 올바르게 계속하는 방법**을 설계·평가한다.

주 연구 질문:

> 같은 모델·도구·근거 접근·실험 기회·전체 예산에서 명시적 연구 상태와 독립 평가를 연결하는 하네스가 강한 반복 연구 에이전트보다 다단계 연구의 최종 검증 성과를 개선하는가?

주 contrast는 `research-continuity harness − strong iterative research baseline`이다. typed graph는 필수 treatment가 아니다. 압축·재귀 깊이·모델 교체·SFT·환경 합성은 동시에 묶지 않고 관측된 병목에 따라 후속으로 분리한다.

## 3. 최소 범위와 논문 기여

현재 제안은 research contract, 원자료/실험 state, bounded planner, isolated executor, independent assessor, continuation capsule의 최소 연결이다. 각각의 존재를 새 발명으로 주장하지 않는다. 통합 설계·재현 가능한 제한적 평가·실패 분석을 기여 후보로 둔다. 실제 효능은 아직 입증되지 않았다.

실증 후보는 공개 자료·고정 split/metric·현실적 compute 한도를 가진 작은 ML 연구 프로그램이다. 실제 baseline/경쟁 실험/관측/다음 결정/최종 선택을 포함해야 한다. 단순 회전 행동 반복이나 elapsed time만으로 장기 연구를 대체하지 않는다. 과제 묶음, 표본, 독립 semantic gold와 예산은 아직 미정이다.

DiscoveryWorld는 선택 가능한 보조 런타임 사례로 내려놓는다. 현재 미완료 World-init 자료는 보존하되 새 주제의 선행 의무가 아니다. 다음 연구 우선순위는 본문 설계와 실제 ML task programme/평가 계약의 확정이다.

## 4. 문헌 기반

- Prime Agent / Scroll: 영속 실행, 원자료 주소와 선택적 노출. 보존이 의미 충분성을 뜻하지 않는다.
- HoH / RecEvolve: 반복 planning–implementation–evaluation 및 결과/실패의 다음 결정 환류. 같은 모델의 역할 분리를 오류 독립성으로 주장하지 않는다.
- HarnessDev: 후보 동결, creator/executor·feedback/held-out 분리, 작동 경로와 실제 성과 확인.
- SkillZip: 가역 절차 계약과 선택적 hydration은 옵션이며 구조 보존은 의미 검증이 아니다.
- Metaⁿ: 고정 개선 인터페이스와 trace+code 진단은 참고하되 archive max/재귀 깊이를 배포 성능으로 바꾸지 않는다.
- Terminal-Universe: 과제 후보의 observed/inferred provenance와 ancestry split. 합성 복원을 원환경 재현으로 주장하지 않는다.

전체 원문·locator·독립 audit: `paper/research/long-horizon-harness-benchmark-20260907/`. 이 자료의 직전 design amendment는 이번 pivot 이전 비교안이며 새 주제를 제한하지 않는다.

## 5. 평가·중단 원칙

- 주 outcome은 고정 예산에서 단일 최종 선택 산출물의 독립 과제 성과다. metric/실패 점수/최종 선택 규칙은 실행 전에 고정한다.
- 상태 일치, 실패 반복, false suppression, 보존 회귀, 인계, 비용은 별도 진단으로 보고한다. 임의 곱이나 구성 요소 통과 수를 효능으로 대체하지 않는다.
- 과제/원자료 계보가 추론 단위다. seed·candidate·round·같은 환경의 생성 질문은 nested다.
- 모든 launch/실패/무효/철회와 평가·비평·복구 비용을 기록한다. 새 retry 정책이 필요하면 별도 사전등록한다. 소모된 one-shot 권한은 어떤 경우에도 재사용하지 않는다.
- 비공개 scorer/gold에 접근하거나 outcome을 본 뒤 endpoint/표본을 바꾸면 인과 판정을 중지한다.
- 독립 평가에서 이점이 없거나 비용이 설명하면 더 단순한 baseline을 선택할 수 있다.

## 6. 기존 증거와 보존

C64는 task text–oracle 충돌로 인과효과 근거가 아니다. graph/retrospective replay/정적 witness는 해당 규칙·기록 범위만 지지한다. UI-parity v12는 30/30 초기 crash로 `INVALID / NOT_ADMITTED`이며 재시도 불가다. font qualification은 정확한 host/runtime 다섯 font 호출의 호환성만 `PASS / VERIFIED / ADMITTED`이다. World-init와 integrated research efficacy는 미검증이다.

주제 변경은 실패를 성공으로 바꾸지 않는다. 새 방향의 confirmatory efficacy result는 0이다.

## 7. 실행·출판 경계

네이티브 제품 construction은 계속 중단한다. 기존 Prime daemon/AgentSession/REPL/RLM lifecycle과 미래 ORX scientific-run authority를 중복 구현하지 않는다. Python 연구 fixture는 제품 runtime이 아니다.

현재 허용: 문헌/연구 설계, 원고 삽입 후보, 공개 과제 적합성 조사, 기존 승인 범위의 로컬 정적 검사. 새 model/compute/World 실행은 고정 task/scorer/environment/command/budget, immutable review, 별도 정확한 승인이 필요하다. DeepVoice/LG Aimers 접근, credentials 변경, push·공개·제출은 하지 않는다.

정본 QMD, protected evidence, 기존 dated exports는 변경하지 않는다. 논문 출판 범위는 장기 자율연구 하네스와 입증한 결과/한계이며 ARGO·NAIS 내부 운영·로드맵과 분리한다. verified scholarly titles와 서지정보는 정확히 유지한다. 논문 결과가 후행 내부 설계를 안내할 수 있지만, 후행 제품 계획이 논문의 기여나 실험 의무를 결정하지 않는다.

## 8. Graph와 인계

`paper/context-graph.json`은 연구 projection이며 runtime event store가 아니다. 새 방향은 pivot record와 root/design binding을 통해 복구한다. 옛 review/실험 receipt는 자신이 검증한 revision에만 유효하다. `next → handoff → graph`의 비순환 hash binding을 유지한다. 옛 실험 cohort의 evidence cutoff는 보존하고 새 문헌/설계 revision date와 구분한다.
