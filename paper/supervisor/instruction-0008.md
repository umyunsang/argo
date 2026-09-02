# Supervisor instruction #0008 (paper) — goal 오류 상태 복구

- 발신: Claude Code supervisor
- 시각: 2026-09-02 22:24 KST
- 대상: argo-paper-root
- 근거: 세션 파일 thread_goal_state 15:50:19 KST `status: error`, lastError "You have hit your ChatGPT usage limit (pro plan)"; 22:16:08 KST 사용자 `/goal resume` → "Goal error" (error 상태에서는 resume이 무효, `_resumeGoal`은 paused/budget_limited만 처리); 22:16 이후 taskState needs_input

## 1. 사실

- goal은 15:50 KST에 이전 모델의 사용량 한도 오류로 `error` 상태가 되었고 그 뒤로 한 번도 재주입되지 않았다. 사용자의 `/goal resume`은 error 상태에서 아무 일도 하지 않는다.
- 오류 상태의 goal은 커널 goal 스킬의 `goal.create()`로 교체할 수 있다(호스트 `_createGoalFromHost`: complete/error는 새로 시작).
- 22:16 백엔드 프로브 결과(haiku-4-5 ok, gemini-3.7-flash timeout 124, grok-4.6 402)를 받은 직후 턴이 끝났다. 그 결과를 잃지 말고 이어서 쓴다.

## 2. 즉시 할 일

1. 커널에서 실행: `await goal.create("Autonomously complete and continuously improve the ARGO graduation paper through OpenResearch with evidence-grounded claims and deterministic validation, running the standing research loop of paper/supervisor/instruction-0005.md §2 and instruction-0007.md without ending on reports.")` 그리고 `await goal.get()`으로 `status: active`를 확인해 status.md에 goal id를 적는다. token_budget은 지정하지 않는다(사용자 요청 없음).
2. goal이 활성이면 heartbeat `c024a580`은 바쁜 동안 자동으로 건너뛴다. 그대로 둔다.
3. 백엔드 프로브 결과를 `paper/supervisor/cost-ledger.md`와 결정 기록에 적고, 사이클 3(과제 4개 동결 → 백엔드 고정 → burned-task 2건 → 16-episode 파일럿 실행)을 #0007 §4대로 이어간다.

## 3. 불변 조건

instruction-0003 §5, 0005 §4, 0006 §2~§3, 0007 §2·§5 그대로.
