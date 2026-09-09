# ARGO_RESEARCH_DIRECTION_AUDIT_20260905_REVIEW_ONLY

Target: exact live `argo-paper-root`, active session `d28d851bde93`, saved session `01a05f13-5001-77c8-8530-d92634405424`.
Mode: **READ_REVIEW_AND_ACK_ONLY**. This message permits bounded reading and an acknowledgement in this conversation only. It is NOT a new research task, run approval, canonical-update instruction or native-construction restart.

현재 repo의 아래 private audit packet을 읽고 이 대화에 수용/이견만 회신하십시오.

- `/Users/um-yunsang/argo-paper-orx/.planning/2026-09-05-research-direction-audit/review.md`
- 같은 디렉터리의 `literature-review.md`, `experiment-review-root.md`, `architecture-review.md`
- `proposed-context-map.json` 및 `validation-receipt.json` — DRAFT_NOT_APPLIED. 기존 canonical graph를 대체하지 않습니다.

## 권한 보존 — 최우선

12:17:34 KST 사용자 “C 실행 승인”과 root가 사전 권고에 따라 선택한 C64는 이 검토와 별개의 권한입니다. 승인 SHA `997c2a3f21921aa6b07abf56633a22ec8bf7249ca227eebd605eeca90b5dbf63`, cap은 정확히 64 attempted episodes입니다. 이미 시작한 C를 이 메시지 때문에 중단·재시작·변경하지 마십시오. 완료됐으면 되돌리거나 재실행하지 마십시오. 이 메시지는 기존 C 권한을 늘리지 않습니다.

진행 중 task pack, allocation, model, tools, source, scorer, endpoint, tail/alpha, 표본수, 예산, stop rule을 변경하지 마십시오. 중간 효과를 읽어 후속 조건을 조정하지 마십시오. 첫 32 episodes 주 분석과 역순 32 episodes 반복은 분리하고 n=16을 유지하십시오. 추가 model call, post-hoc rerun, canonical graph/protocol/ledger 수정, runtime 구현, 논문 수정, commit/push, 공개/제출/외부 문의를 이 메시지로 수행하지 마십시오. 다른 사용자 승인 범위와 혼동하지 말고 별도로 인용하십시오.

## 검토 결과 — 회신에서 인정하거나 근거를 들어 반박

1. **방향은 타당하지만 SOTA/최적성은 미입증입니다.** 현재 C는 제한된 근거 할당의 synthetic dependency-resolution 기전 과제이며 전체 자율 연구 설계·실험 선택·fresh-context handoff의 입증이 아닙니다. Stage0 96 checks는 연구 성공 횟수가 아니고, B3 n=4는 개발 신호입니다. 이 범위를 늘린 표현은 수용하지 마십시오.
2. **다음 비교의 핵심은 강한 result-aware tree입니다.** AI Scientist-v2/Arbor의 evidence·failure·insight를 보존하는 adaptive tree와 typed policy를 동등 정보·기회·총비용으로 비교해야 합니다. Graph-Native의 version/dependency 선행연구와 Selective Forgetting의 반대 결과를 반영해 graph 자체를 공헌으로 주장하지 마십시오. 필요한 경우에만 version-aware log/vector 하나 또는 동일 첫 record 진단을 제안하고, 오래된 G×C×F 8조건이나 baseline zoo를 재도입하지 마십시오. 지금 구현/실행하라는 뜻이 아닙니다.
3. **통계는 동결된 양측 검정을 유지하십시오.** 5승0패 p=.0625, 6승0패 p=.03125입니다. n16의 81.2%는 discordance .75/conditional win .90 가정에서의 기각확률이지 전체 성공확률이나 실제 검정력 보증이 아닙니다. 대안 (.50,.90) 53.9%, (.50,.75) 17.4%를 검토서에 함께 두었습니다. zero harm/8은 일반 안전성, 비유의는 동등성의 증거가 아닙니다. 중간 결과를 보고 검정/표본수를 바꾸지 마십시오.
4. **원래 실패 분모와 receipt 완전성을 구별하십시오.** 정적 검토상 malformed JSON/scorer 예외가 attempt receipt append 전에 중단될 수 있고, 분석기는 missing decision/access log를 필수로 읽으며 exit/timeout 상태를 correctness 집계에 쓰지 않습니다. 실제 C 실패를 관찰했다는 뜻은 아닙니다. 종료 보고 시 원래 시도·실패를 설명하지 못하면 그 acceptance를 보류해야 하며, 숨김/재시도/실행 중 수정으로 해결하지 마십시오. 이번에는 경계 인지만 회신하십시오.
5. **인계 snapshot 불일치가 관찰됐습니다.** active handoff ROOT hash `2c4647d9e8c47262a4261fa27be1a2278dd540c7a4482b4d56dde472ffe4f97e`와 실제 ROOT `4d972add03586e67ea39bd8492bade238cc6f68b8c85bcb00408081b67637419`가 12:26/12:35 KST에 달랐습니다. 후속 C64 승인은 존재하므로 무승인 실행이라고 해석하지 마십시오. 현재 소스가 이미 바뀌었으면 이 finding은 NEEDS_RECHECK로 회신하십시오. 오늘 메시지로 canonical repair를 하지 마십시오. 향후 한 revision의 비순환 immutable capsule, scoped invalidation 및 실제 fresh-context 소비 검증이 필요합니다. 현재 `NOT_RUN` 소비 acceptance와 JSON/hash PASS를 혼동하지 마십시오.
6. **연구/제품/행사 경계를 유지하십시오.** native construction hold, LG Aimers read-only, private-instance 경계를 유지합니다. 논문은 내부 ARGO/NAIS·제품 로드맵과 구분하고 현 1단 Quarto 판본을 그대로 둡니다. 공고의 본선 내 실제 개발 규정과 기존 연구/OSS/코드 재사용 미확인 범위를 구별하십시오. 선행연구 7편은 완독 7편이 아니며 source별 읽기 범위를 준수해야 합니다.

## 요구하는 회신 형식

이 대화의 assistant text로만 다음을 회신하십시오.

- `ACK ARGO_RESEARCH_DIRECTION_AUDIT_20260905_REVIEW_ONLY` 및 실제 읽은 packet 파일/범위
- 핵심 결과별 수용/이견, 이견에는 현재 파일/receipt 또는 검토서 source locator
- C 설계 변경·추가 실행·canonical/runtime/manuscript 수정이 이 메시지로 승인되지 않음을 확인
- C 종료 후 별도 승인이 필요한 후속 제안을 최대 1개만 서술. 실행하거나 파일에 반영하지 말 것

전달, 읽음, 수용, 구현은 서로 다른 상태입니다. 이번 목표는 **읽음과 회신**까지이며, 새 연구·수정 실행은 목표가 아닙니다.
