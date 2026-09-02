# Supervisor instruction #0001 (paper)

- 발신: Claude Code supervisor
- 시각: 2026-09-02 13:55 KST
- 대상: argo-paper-root
- 근거: 세션 트랜스크립트(goal 7903f42b… `budget_limited` 251031/250000, 07:33 KST 이후 비활성), 13:15 KST 자기평가, 13:25 KST 사용자 지시, `git status`(변경 파일 16개 미커밋), paper/official-thesis-requirements.md, docs/argo/migration-state.json(native_migration BLOCKED)

## 평가

13:15 자기평가("실행된 실험이 없으므로 Experimental Results를 쓸 수 없다, 우선순위는 실험 가능 상태 만들기")는 정확하며 유지한다. 문헌 23편 전문 검토, claim 32개 검증, 3조건 설계, 공식 양식 분석은 완료됐다. 사용자의 13:25 지시(openresearch-cli 기반 자율 연구, root가 직접 설계, 근거 기반 선택, context graph 동적 구축)를 최우선으로 따르되 아래를 함께 적용한다.

## 1. 연속성 (harness)

- goal 예산 250k 토큰은 07:33 KST에 소진되어 goal이 비활성이다. 에이전트에게는 goal 갱신 도구가 없다. supervisor가 사용자에게 TUI `/goal --budget …` 재설정과 heartbeat 스케줄 등록을 요청했다.
- 재설정 전까지는 턴이 끝나면 멈춘다. 따라서 매 턴 종료 전 `paper/supervisor/status.md`를 갱신한다: 현재 단계, 다음 단계(구체적 명령·파일), 차단 여부와 Q id, 마지막 갱신 시각. 재개 시 이 파일부터 읽는다.
- 한 도구 호출이 10분 이상 걸릴 작업(대량 다운로드, 장시간 실행)은 백그라운드로 돌리고 폴링한다. 단일 블로킹 호출로 세션 전체를 멈추지 않는다.

## 2. Supervisor 채널

- 지시는 `paper/supervisor/instruction-000N.md`, 질문은 `paper/supervisor/questions.md`에 6필드 형식(id/시각, 근거 경로, 옵션과 수치 영향, 권고, 미답변 시 기본값, blocking 여부)으로 올린다.
- 사용자 결정이 필요한 사항은 Q id로만 올리고, 답이 없으면 기본값으로 진행한다.

## 3. 연구 설계 요구 (내용은 세션이 설계한다, 형식만 요구)

- 현재 진행 중인 5편 재검토(SCOPE, ResearchClawBench, Arbor, long-horizon search diagnosis, Hypothesis Evolution Protocol)의 결론은 decision record로 남긴다: 3조건 설계 keep/revise, 근거 source id와 read level. `FULL_PAPER_READ`만 설계 변경 근거로 인정한다.
- 그 다음 산출물은 "실행 가능한 최소 실험 단위 제안서"다. 허용 자원 안에서 실행 가능해야 한다: 네이티브 ARGO 구축 금지(migration-state BLOCKED), DeepVoice 파일 편집 금지, 현재 Prime Agent + orx 하네스는 사용 가능. 각 조건의 실행 경로, 표본 수 결정 근거, 반증 조건, 중단 규칙, 예상 비용(토큰·시간)을 명시한다.
- 허용 경계가 불명확한 항목은 Q로 올린다. 예: DeepVoice supervisor 산출물(progress.md, questions.md, cost-ledger, instance.json)을 읽기 전용 사례연구 증거로 인용할 수 있는지. 미답변 시 기본값은 "허용되지 않은 것으로 간주".
- 미실행 결과는 paper.tex에 쓰지 않는다. Experimental Results는 사전등록 계획과 placeholder로만 둔다.

## 4. 졸업 일정

- official-thesis-requirements.md: 계획서 제출은 후기 졸업자 9월 30일 이전. 사용자의 졸업 학기와 학과 제출일은 추정하지 않는다. Q-0001로 질의한다(blocking=false).
- 기본값: 2026-09-30을 계획서 마감으로 가정하고, 계획서 초안(제목, 목적, 방법 및 개요, 3~12월 연구일정, 참고문헌)을 사전등록 설계에서 파생해 준비한다. 학적정보·지도교수·서명은 비워 둔다. 계획서는 실행 결과가 없어도 정직하게 작성 가능한 산출물이다.

## 5. 커밋 위생

- 변경 파일 16개가 미커밋 상태다. 일관된 경계마다 변경한 파일만 명시적으로 커밋한다. `git add -A`, `git add .`, `git stash`, `git reset --hard`, `--no-verify`, force push 금지. 커밋 메시지에 이모지 금지.
- 주요 단계(재검토 완료, 제안서 완료, 계획서 초안)마다 체크포인트 커밋을 남긴다.

## 6. 불변 조건

- 세션 모델 `openai-codex/gpt-5.6-sol` 유지.
- 논문과 산출물에 해커톤 회사명과 도메인을 쓰지 않는다. 인스턴스는 익명화한다.
- DeepVoice 인스턴스 파일 편집 금지, 답변된 orx ancestor 편집 금지.

## 보고

status.md 갱신과 questions.md의 Q-0001 등록으로 알린다.
