# Supervisor instruction #0007 (paper) — idle 원인, 루프 종료 조건 삭제, 파일럿 잔여 항목은 연구자 결정

- 발신: Claude Code supervisor
- 시각: 2026-09-02 22:08 KST
- 대상: argo-paper-root
- 근거: `prime-agent schedule list`(heartbeat 28b18ed8 paused, last 17:33), `prime-agent list`(22:03 idle, 636 messages), status.md "30-minute heartbeat active" 불일치, 사용자 메시지 22:03 "왜 계속 idle 상태가 되는거야?"

## 1. 왜 멈추는가

Prime Agent는 턴 단위다. goal이 일시정지된 상태에서 턴이 끝나면 아무것도 세션을 다시 깨우지 않는다. 대체 구동기였던 30분 heartbeat `28b18ed8`은 paused였다. 그래서 사이클 1·2를 끝낸 뒤 22:01부터 idle이었다. supervisor가 heartbeat를 새 스케줄(cron `*/30 * * * *`, 루프 한 사이클 프롬프트)로 재가동했다. status.md의 heartbeat 문구를 새 id로 고쳐라(`prime-agent schedule list`로 확인).

## 2. 루프 종료 조건 삭제

- instruction-0005 §2의 "모든 공백이 외부 의존이면 멈춘다"를 삭제한다.
- 외부 의존 단위는 Q에 기본값을 적고 기본값으로 즉시 진행하거나 다음 단위로 넘어간다. 턴은 사용자의 정지 메시지로만 끝난다.
- 턴이 어쩔 수 없이 끝날 때는 status.md 첫 부분에 `next_first_action:` 한 줄을 남겨 heartbeat가 그 행동부터 이어받게 한다.
- status.md의 "Next concrete actions"는 이미 끝난 항목(1·4)을 아직 나열하고 있다. 매 사이클 끝에 실제 상태로 다시 쓴다.

## 3. Q-0005 답변

(b) 보류. questions.md에 기록됨. GPU는 파일럿 이후, 사전등록과 cost-ledger 행을 커밋한 뒤 새 Q로 다시 올린다. 이 Q는 더 이상 blocking이 아니다.

## 4. 파일럿 잔여 3항목은 외부 의존이 아니라 연구자의 결정이다

1. **과제 동결.** 설계 비교표(`design-comparison-round8.md`)와 선행 연구 locator를 근거로 4개 과제를 직접 선택해 동결하고 6필드 결정 기록을 남긴다. withheld target은 release sandbox로 은닉한다. 선택 기준(난이도 분포, 구조화 상태와 동적 검색이 효과를 낼 수 있는 조건, 채점 가능성)을 근거와 함께 적는다.
2. **백엔드 고정.** 사용 가능한 백엔드를 열거한다: `prime-agent --print --model <id>` 고정 호출(세션이 이미 인증된 경로), 환경의 API 키, `orx compute --cpu` 인스턴스 등. 하나를 고정하고 근거를 기록한다. 에피소드당 token_ceiling과 16-episode 총 예상 토큰을 `paper/supervisor/cost-ledger.md`에 적는다. 총 예상이 200만 토큰을 넘으면 Q를 올리고 기본값(축소 파일럿 8 episode)으로 진행한다.
3. **burned-task 2건 등록.** Q-0004 승인됨. `burned-task-ledger.json`에 기록하고 확증 실험에서 영구 제외한다.

그 다음 16-episode 파일럿을 실제 실행하고, 실행 영수증(명령·입력 sha·백엔드·토큰 소비·결과 파일 digest)을 immutable evidence로 남긴다. 결과 해석은 사전등록 기준(TOST 동등성 마진, 분산 분해)으로만 하고, 파일럿은 도구 검증이므로 효과 주장을 하지 않는다.

## 5. 자율 연구 위임 (사용자 원문, 모든 사이클에 적용)

> 너가 깊이 추론해서 스스로 연구를 설계하고, 연구 가설이나 조건, 방법 등 모든 요소를 직접 설정해야 하고, 근데 이걸 또 그냥 정하는게 아니야 깊이 있는 추론과 인사이트를 통해 선택을 해야하고, 그 선택에 대해 근거까지 있어야 해. 비슷한 실험찾아보고, method 찾아보고, 쓸만한 레퍼런스 찾아보고, 자료정리도 해야해 또한 이모든 걸 다른 ai 에이전트들도 인지하고 작업할수 있게 context graph로 스스로 작성하서 그래프 맵을 구축해야 해. 관련 선행 연구를 찾아서 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리 구축하고 실험을 진행하는거야. 비슷한 연구들이 어떤식으로 실험을 설계했는지 비교 경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행하는거야.

"외부 의존"이라고 판단하기 전에 이 위임을 다시 읽어라. 가설·조건·방법·과제·백엔드·채점 기준은 모두 연구자가 근거를 들어 정하는 요소다.

## 6. 불변 조건

instruction-0003 §5, 0005 §4, 0006 §2~§3 그대로. 세션 모델은 바꾸지 않는다.
