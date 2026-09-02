# Paper session questions to supervisor

Q 형식: `## Q-000N` 제목 아래 6필드(id/시각, 근거 경로, 옵션과 수치 영향, 권고, 미답변 시 기본값, blocking 여부). 답변은 supervisor가 `[ANSWERED …]`로 표기한다.

## Q-0001 — 졸업 학기와 학과 실제 계획서 마감일 [ANSWERED 2026-09-02 14:39 KST]

- **id/시각:** Q-0001 / 2026-09-02 14:06 KST
- **근거 경로:** `paper/official-thesis-requirements.md`, `paper/official-thesis-requirements.json`
- **옵션과 수치 영향:** (A) 후기 졸업·2026-09-30 이전 제출: 현재 기본 일정 유지. (B) 전기 졸업·3월 31일 이전 또는 학과 별도일: 계획서·실험·집필 마일스톤 전체를 해당 날짜 기준으로 이동. 정확한 학과일이 있으면 날짜 1개를 제공.
- **권고:** 사용자에게 졸업 학기와 AI학과 실제 계획서 제출일을 확인한다.
- **미답변 시 기본값:** 후기 졸업, 계획서 마감 `2026-09-30`으로 두고 초안을 계속 준비한다.
- **blocking 여부:** false — 계획서 초안과 자율 연구 설계는 기본값으로 계속 진행.
- **answer:** 학과 계획서 제출 마감은 `2026-10-31`. 현재 학기 가정은 유지하고 모든 계획서·실행 일정의 기준일을 10월 31일로 변경.

## Q-0002 — 참조 구현 위에서 검증할 수 없는 목표 기능의 처리 [ANSWERED 2026-09-02 14:39 KST]

- **id/시각:** Q-0002 / 2026-09-02 14:21 KST
- **근거 경로:** `paper/research/capability-map.md`, `docs/argo/migration-state.json`, `paper/supervisor/instruction-0002e.md`
- **옵션과 수치 영향:** (A) 기본값: personalized-memory 권리/삭제, 완전한 MCP 수명주기, 복수 vector DB backend, provider registry/fallback, 동적 모델 라우팅, native daemon 변경의 6개 기능군을 이번 주기 “설계만/후속”으로 유지하고 10개 연결 기능만 검증. (B) 추가 개발 허용 범위를 기능군별로 지정하면 조건·구현·실행 수가 증가하며 Study A 4조건과 별도 실험이 필요.
- **권고:** 이번 논문 주기에는 (A)를 유지한다. 현재 핵심 가설의 식별 가능성과 640,000-token instrument-pilot 상한을 보존한다.
- **미답변 시 기본값:** (A) 설계만/후속으로 진행하며 새 native 런타임은 만들지 않는다.
- **blocking 여부:** false — Study A 설계와 문헌 지도는 계속 진행.
- **answer:** 권고안 (A) 채택. 6개 기능군은 이번 주기 설계만/후속으로 유지하고 새 native 런타임을 만들지 않는다.

## Q-0003 — Study C 실행 자원 승인 여부 [ANSWERED 2026-09-02 21:54 KST]

- **id:** Q-0003
- **question:** 실행 채점 기반 Study C를 위해 GPU 1장과 과제당 약 24시간의 컨테이너 실행 자원을 확보할 것인가?
- **why_it_matters:** 설계 점수 우위가 실행 결과로 이어지는지 확인하는 유일한 경로다. 확보 전에는 Study A 결론이 설계 산출물로만 한정된다.
- **options:** (a) 자원 확보 후 Study C 실행 (b) 현행대로 설계 전용 Study A만 진행하고 Study C는 RUNBOOK 상태로 보류
- **default_if_unanswered:** (b) 보류. 근거 `RD-2026-09-02-08A`, RUNBOOK `paper/research/study-c-runbook.md`.
- **blocking:** false — 기본값으로 진행해도 되돌릴 수 없는 손실이 없다. 적용됨.
- **asked_at:** 2026-09-02T21:41:37+09:00
- **answer:** 권고대로 진행. 사용자 원문 "권고대로 진행해. gpu가 필요할때는 colab cli 사용해." 해석: 지금은 기본값 (b)대로 설계 전용 Study A를 계속하되, Study C의 상태는 "자원 미확보"가 아니라 "Colab CLI(L4) 경로 확보, 실행 전 사전등록 필요"로 바꾼다. GPU가 필요한 단위는 supervisor instruction #0006의 규칙(사전등록, est_CU, cost-ledger, 세션 종료 확인)에 따라 `colab` CLI로 실행한다. 첫 GPU 실행 전에 예상 CU와 실행 계획을 Q로 올린다(blocking: true, 비용 지출).

## Q-0004 — 파일럿 귀인 분과에서 과제 2건 소모 승인 [ANSWERED 2026-09-02 21:54 KST]

- **id:** Q-0004
- **question:** 아이디어 실패와 구성 실패를 분리하기 위해 파일럿에서 과제 2건에 목표 아이디어 한 문장을 공개하고 그 과제를 확증 실험에서 영구 제외해도 되는가?
- **why_it_matters:** 공개된 과제는 오염되어 재사용할 수 없으므로 확증용 과제 풀이 2건 줄어든다.
- **options:** (a) 승인하고 2건 소모 (b) 귀인 분과 없이 파일럿 진행
- **default_if_unanswered:** 답변 전까지 귀인 분과만 보류한다. 근거 `RD-2026-09-02-08C`, locator `researchgym_integrity_and_resources`.
- **blocking:** true — 기본값으로 진행하면 확증용 과제 2건이 영구 소모된다. 나머지 파일럿 전제 구축은 계속한다.
- **asked_at:** 2026-09-02T21:41:37+09:00
- **answer:** (a) 승인. 파일럿 귀인 분과에서 과제 2건에 목표 아이디어 한 문장을 공개하고 그 2건은 확증 실험에서 영구 제외한다. 소모한 과제 id를 research-design.md와 status.md에 기록한다.


## Q-0005 — 첫 GPU 실행 승인 [ANSWERED 2026-09-02 22:08 KST]

- **id:** Q-0005
- **question:** Study C 첫 GPU 단위를 호스티드 노트북 CLI에서 실행해도 되는가? 사전등록(목표·고정 명령·입력 sha·est_CU·중단 규칙·체크포인트 계획)과 비용 원장 행을 먼저 커밋한다.
- **why_it_matters:** GPU 실행은 compute unit을 실제로 소비하며 되돌릴 수 없다. 현재 누적 사용량은 0 CU다.
- **options:** (a) 사전등록 검토 후 승인 (b) 파일럿 전제와 16-episode 파일럿을 모두 마칠 때까지 보류
- **default_if_unanswered:** (b) 보류. Study A와 그 전제는 GPU가 필요 없으므로 루프는 멈추지 않는다.
- **blocking:** true — 기본값 실행 시 compute unit이 소비된다. 단일 10 CU 또는 누적 25 CU 초과 전 별도 승인이 필요하다.
- **asked_at:** 2026-09-02T21:52:42+09:00
- **answer:** (b) 보류. 파일럿 전제와 16-episode 파일럿은 GPU 없이 끝낸다. 파일럿 완료 후 사전등록(목표·고정 명령·입력 sha·est_CU·중단 규칙·체크포인트)과 cost-ledger 행을 커밋한 뒤 새 Q로 다시 올린다. 이 Q는 더 이상 blocking이 아니며 루프를 멈추지 않는다.

