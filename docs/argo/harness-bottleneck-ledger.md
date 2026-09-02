# Harness bottleneck ledger

Evidence-backed record of harness problems observed while running test instances on stock Prime Agent (0.9.0 Homebrew) plus OpenResearch CLI. Each entry names the observation, the evidence, the immediate mitigation applied through supervision, and the candidate ARGO-native fix. ARGO-native fixes are proposals only while construction is paused (`migration-state.json`).

Entry format: `HB-####` id, date (KST), instance, observation, evidence, mitigation applied, candidate native fix, status.

## HB-0001 Idle-stall after delegation turn

- Date: 2026-09-02, DeepVoice.
- Observation: the DeepVoice root session finished a turn at 08:01 KST with `taskState: needs_input` after acknowledging a paper-root message, although the standing user directive was autonomous research. No `/goal` or heartbeat was set, so nothing re-entered the session. The daemon evicted the worker after the 30-minute idle window (`idleEvictionMinutes: 30`).
- Evidence: `~/.prime/agent/sessions/01a05e36-703f-72ce-a33c-44560d6f81f5.jsonl` shows only `agent_status` entries with `needs_input` from 23:01Z to 23:33Z; `prime-agent list` at 08:35 KST did not include the session; last `deepvoice/` artifact change was `context/map.md` at 05:31 KST.
- Mitigation: supervisor instruction #0001 (`deepvoice/supervisor/instruction-0001.md`) sent with `prime-agent send`, which wakes the saved session; instruction requires `/goal`, a 30-minute heartbeat, and a rule that user-decision items go to `supervisor/questions.md` instead of ending the turn.
- Candidate native fix: a research root session with an open GoalSpec must not end a turn in `needs_input`; the runtime should re-enter through the goal loop, and idle eviction should be suppressed while a goal is open.
- Status: OPEN, mitigation applied.

## HB-0002 Role mixing across instances inside one root session

- Date: 2026-09-02, DeepVoice and paper.
- Observation: from about 05:31 to 08:01 KST the DeepVoice root spent its turns creating, correcting, and steering the paper session (first as an RLM child, then as a separate root after the user objected), producing no DeepVoice output.
- Evidence: assistant messages at 22:25Z, 22:26Z, 22:34Z, 22:51Z, 22:55Z in the DeepVoice transcript all concern `argo-paper-root`.
- Mitigation: instruction #0001 restates that paper work is out of scope for the DeepVoice root; the supervisor now owns cross-session coordination.
- Candidate native fix: per-instance scope containment (ARGO addition already planned as "scope containment"), so a session bound to one instance cannot spawn or steer another instance's root.
- Status: OPEN, mitigation applied.

## HB-0003 Instance workspace outside version control

- Date: 2026-09-02, DeepVoice.
- Observation: `deepvoice/` is excluded from the engine repo through `.git/info/exclude` and has no repository of its own, so contracts, decision records, and the context graph have no history and OpenResearch cannot register experiments against it.
- Evidence: `git ls-files deepvoice` returns 0 files; `git check-ignore -v deepvoice/instance.json` matches `.git/info/exclude:8`.
- Mitigation: instruction #0001 requires `git init` inside `deepvoice/` with data and weights ignored.
- Candidate native fix: instance bootstrap creates the instance repository and the orx project as one step.
- Status: OPEN, mitigation requested.

## HB-0004 State contract fields left null

- Date: 2026-09-02, DeepVoice.
- Observation: `deepvoice/instance.json` carries `next_action`, `blockers`, and `updated_at` as null while the state is `BOOTSTRAPPING_DATA_LICENSE_PREFLIGHT`, so an external supervisor cannot read progress without parsing the transcript.
- Evidence: `instance.json` modified 04:57 KST, fields null.
- Mitigation: instruction #0001 requires these fields on every milestone.
- Candidate native fix: schema-validated instance state with required fields, written by the runtime rather than by the model.
- Status: OPEN, mitigation requested.

## HB-0005 Session cwd bound to a symlinked sibling instance

- Date: 2026-09-02, DeepVoice.
- Observation: the DeepVoice root session's cwd is `/Users/um-yunsang/lgaimer9`, a symlink to `argo/lgaimer`. Resuming it from another directory triggers the "Session found in different project, fork?" prompt, and a supervisor attempt to resume through a TUI produced a stray fork.
- Evidence: session header `cwd: /Users/um-yunsang/lgaimer9`; fork prompt observed at 08:38 KST.
- Mitigation: the session is now addressed only through `prime-agent send`, which wakes it in place; instruction #0001 requires absolute paths under `argo/deepvoice`.
- Candidate native fix: instance-bound sessions record the instance root as cwd, and cwd comparison resolves symlinks.
- Status: OPEN, mitigation applied.

## HB-0006 Supervisor channel is transcript scraping

- Date: 2026-09-02, DeepVoice.
- Observation: the only way for an external supervisor to know what the session is doing is to tail the JSONL transcript and stat files. There is no structured progress event or question queue.
- Evidence: this session's monitoring is a `tail -F` over the transcript plus `stat` on four files.
- Mitigation: `supervisor/` directory convention (instructions in, questions out).
- Candidate native fix: hash-chained event store and a question queue exposed through the daemon protocol (already listed as P1 in `lgaimer/HARNESS.md`).
- Status: OPEN, convention applied.

## HB-0007 Blocker text goes stale after the decision it references is answered

- Date: 2026-09-02, DeepVoice.
- Observation: `instance.json.blockers` still carried "baseline GPU runtime environment not reproduced (user approval needed for paid compute)" at 08:54 KST, after Q-0001 had been answered (08:50) and marked ANSWERED (08:52). Blockers are free text and are not linked to the question they depend on, so nothing clears them automatically.
- Second observation: the same turn produced three new user decisions (CC-BY-SA release compatibility, 5 mixed-license components, PD/NC re-admission). They appeared in `license_ledger.json.gate_status.open_user_decisions`, in `instance.json.blockers`, and in `progress.md`, each phrased differently, before any `Q-000N` entry existed in `supervisor/questions.md`.
- Evidence: `deepvoice/instance.json` (updated_at 2026-09-02T08:54:11+09:00), `deepvoice/research/data-licenses/license_ledger.json` (`gate_status.open_user_decisions`), `deepvoice/progress.md` entry "08:54 KST Echoes↔FMA license closure".
- Mitigation (convention): every user decision gets exactly one `Q-000N` id at creation time; blockers and artifacts reference the id, never restate the question; answering the id is the only way to clear the blocker.
- Candidate native fix: a first-class decision request object (id, question, options, recommendation, deadline, status) owned by the runtime; state-contract blockers are typed references to decision ids and are cleared by the runtime when the decision is answered.
- Status: OPEN, convention to be sent in the next instruction.

## HB-0008 Self-report claims an artifact state that the artifact does not have

- Date: 2026-09-02, DeepVoice.
- Observation: the 08:56 KST progress report said the three license decisions were "already recorded in questions.md". At that moment `supervisor/questions.md` contained only Q-0001. The claim was made without reading the file.
- Evidence: transcript `01a05e36-703f-72ce-a33c-44560d6f81f5.jsonl` line 2645 (assistant text, 2026-09-01T23:56:09Z) vs `grep '^## Q-' deepvoice/supervisor/questions.md` at 08:56:24 KST returning only Q-0001.
- Why it matters: the supervisor channel (HB-0006) is only trustworthy if the agent's end-of-turn summary matches the files. A false "recorded" claim would have left three user decisions invisible to the user.
- Mitigation (convention): instruction #0003 requires reading a file before asserting its state, and makes questions.md the single body for each decision (HB-0007).
- Candidate native fix: end-of-turn report fields that name artifacts are verified by the runtime (path exists, id present) before the turn is allowed to end; mismatches are surfaced as a warning event to the supervisor.
- Status: OPEN, convention sent in instruction #0003.

## HB-0009 goal token budget exhaustion silently deactivates the goal (paper session)

- 관찰(2026-09-02 07:33 KST, argo-paper-root): 세션 생성 시 `--goal --goal-token-budget 250000`으로 심은 goal이 8분 만에 `budget_limited`(251031/250000)로 비활성화됐다. goal 토큰은 매 턴 재전송되는 컨텍스트를 누적 계산하므로 250k는 몇 턴 분량이다. 이후 세션은 사용자 입력이 있을 때만 한 턴씩 진행했고, 사용자는 "입력했는데 더 이상 진행을 안해서 ^c로 껏어"라고 보고했다.
- 원인: 예산 소진이 TUI 밖(supervisor, 사용자)에 알려지지 않고, 에이전트에게 goal을 갱신할 도구가 없다. 갱신 경로는 TUI `/goal [--budget <tokens>] <objective>` 또는 `/goal resume`뿐이다.
- ARGO 요구: (1) goal 예산 단위를 컨텍스트 누적이 아닌 신규 생성 토큰 또는 턴 수로 정의, (2) 소진 시 supervisor 채널에 이벤트 발행, (3) supervisor가 CLI로 goal을 재설정·연장할 수 있는 경로, (4) 기본 예산을 작업 규모에 맞게 추정.

## HB-0010 GPU 비용 회계 불가 (Colab CLI에 잔액 조회 없음)

- 관찰: `colab` CLI는 `pay`(브라우저 열기)만 제공하고 잔액·소모율 조회 명령이 없다. cost-ledger의 모든 L4 행이 "CU delta unavailable"이며 E0 상한 25 CU는 검증 불가능한 규칙이 됐다.
- 조치: 지시 #0005로 VM 생존시간×요율 추정 회계로 전환. 실제 잔액은 사용자가 브라우저에서 읽어 전달해야 한다.
- ARGO 요구: 컴퓨트 provider 어댑터가 실행 전후 잔액 스냅샷(또는 요율×시간 추정)을 강제 기록하고, 상한 초과 예측 시 실행을 거부하는 fail-closed 예산 게이트.

## HB-0011 단일 블로킹 도구 호출이 연구 루프 전체를 2시간 정지 (DeepVoice)

- 관찰(2026-09-02 09:57~12:01 KST): 트랜스크립트에 항목이 전혀 없는 2시간 4분 공백. 경계를 보면 00:57Z 도구 호출 → 03:01Z toolResult로, RuASD 데이터셋 shard(999,813,120B, HuggingFace) 다운로드 한 건이 블로킹된 것이다. 그동안 E0 development 결과(inference 657s)는 12:06 KST까지 처리되지 않았다.
- supervisor 측 한계: 세션 status가 `working`이라 STALL 규칙(status≠working)이 발동하지 않았다. 도구 호출이 걸려 있으면 정지와 구분되지 않는다.
- 조치: Monitor에 "status와 무관하게 트랜스크립트 40분 무변화" 규칙 추가. 지시 #0001(paper)에 "10분 이상 걸릴 호출은 백그라운드+폴링" 규칙 명시.
- ARGO 요구: 도구 호출 타임아웃 기본값과 장시간 작업의 백그라운드 실행을 하네스가 강제하고, 호출 지속 시간을 supervisor 이벤트로 발행.

## HB-0012 supervisor가 heartbeat/goal을 CLI로 설정할 수 없고, 잘못된 CLI 호출이 유령 세션을 만든다

- 관찰 1: `prime-agent schedule add <agent> "every 30m"`는 존재하지만 지속 트리거라 supervisor 자동 실행 정책에서 거부됐고, goal 재설정은 TUI `/goal [--budget <tokens>] <objective>`뿐이다. 세션 연속성 복구가 사용자 수동 작업에 의존한다.
- 관찰 2: `prime-agent follow-up <agent> -- <msg>`는 서브커맨드가 아닌데 오류 대신 이름 없는 새 세션(f818c73b3d13)을 만들어 메시지를 그쪽에 전달했다. 잘못된 주소 지정이 조용히 다른 수신자를 만든다. 검증된 경로는 `prime-agent send <agent> -- <msg>`뿐이다.
- ARGO 요구: supervisor에게 goal/heartbeat 설정 권한을 위임하는 계약(만료·예산 상한·감사 로그)과, 알 수 없는 서브커맨드는 fail-closed로 거부하는 CLI.

## HB-0013 사전등록에 검정력이 없어 one-shot 터미널이 반증 기능을 못 함 (DeepVoice)

- 관찰(2026-09-02 13:32 KST): dv-rd-0023 터미널(51 rows, 17 components)이 EAT 음악 구성을 기각했다. delta −0.0294, paired CI [−0.2647, 0.2353]. 개발 세트에서 admitted된 이득은 +0.0525(CI [.0131,.0834])였으므로 터미널은 설계상 반증하려던 효과 크기를 검출할 수 없었다. 규칙은 지켜졌지만(재개봉 없음) 정보량은 거의 0이다.
- 조치: 지시 #0005a로 MDE·행 수·예상 CI 폭의 사전등록을 의무화하고, 이번 결과를 "검정력 부족"으로 기록하게 함. 외부 확인은 공개 LB 제출점(사용자 업로드)으로 대체.
- ARGO 요구: preregistration 스키마에 power/MDE 필드를 필수로 두고, 터미널 개봉 게이트가 예상 CI 폭 > MDE이면 fail-closed로 거부.

## HB-0014 goal 루프가 백그라운드 대기 중 턴 스핀을 만든다 (DeepVoice)

- 관측(2026-09-02 14:01~14:05 KST, transcript 05:01:35Z~05:04:48Z): 세션이 L4 실행을 기다리며 도구 호출 없이 "대기 중" 한 줄을 출력하고 턴을 종료 → Prime Agent goal 루프가 `goal_context`를 즉시 재주입 → 3분 13초 동안 assistant 메시지 22개, goal_context 18회, 도구 호출 5회. 지시 #0005 §1(120초 서술 간격)은 서술 간격만 바꾸고 턴 종료 반복은 막지 못했다. tokensUsed 13:20→14:26 약 +1.3M.
- 원인: 대기의 정확한 위치가 지정되지 않았다. 텍스트만으로 끝난 턴을 goal 루프가 "미완료"로 보고 즉시 재개한다. HB-0011(단일 블로킹 호출 2시간 정지)의 반대 실패 모드.
- 조치: 지시 #0006 §1 — 단일 ipython 호출 안에서 `asyncio.sleep(120)` 루프로 최대 20분 블록, 상태 변화 시에만 호출 종료, 텍스트만의 턴 종료 금지.
- 확인(15:10 KST): Prime Agent 0.9.0에는 goal continuation 주기 설정이 없다. `agent-session.js`가 assistant 턴 종료 직후 `followUp` 액션으로 goal_context를 즉시 admit하며(타이머·설정 키 없음), settings.md에는 `idleEvictionMinutes`만 있다. 두 세션의 30분 heartbeat 스케줄은 goal이 세션을 항상 busy로 유지해 runs=0, 매 tick skipped 상태였다. 30분 주기로 바꾸려면 `/goal pause`(TUI 전용) 후 스케줄이 continuation을 맡아야 한다.
- 하네스 요구: goal 루프에 "도구 호출 없는 연속 턴 N회" 감지와 최소 재개 지연(backoff), 그리고 continuation 주기 설정(`goalContinuationIntervalMinutes`)이 필요하다. HB-0011과 함께 "대기 프리미티브(await-with-timeout)"가 하네스 기능으로 있어야 한다. 논문 영역 (1) 관측성/(7) 데몬·goal.

## HB-0015 검증 인스턴스의 방법 선택에 문헌 근거 절차가 없다 (DeepVoice)

- 관측: dv-rd-0024~0027까지 증분 후보(Spectra-0 zero-fit, TFCL, 4-class replay head)가 기억 기반 인용 또는 우연히 읽은 논문 1~2편으로 선택됐다. paper 세션(#0002c)에는 대안 ≥2·근거 id+읽기 수준·비교 실험 표가 의무지만 인스턴스에는 같은 규율이 없었다. 현 패러다임(동결 last-layer mean+std + convex head)의 천장 추정과 점수 여유 분해표도 없었다.
- 영향: 증분 우선순위가 근거 없이 정해지고 단일 개봉 terminal이 낮은 가치 후보에 소모될 위험.
- 조치: 지시 #0006 §3~§4 — dv-rd-0028 방법 포트폴리오(C1~C5) 비교 실험 표, 기대 이득/CU 순위, 점수 여유 분해표. §5 harness-report.md로 9영역 사용 여부를 인스턴스에서 자기 보고.
- 하네스 요구: "방법 선택 전 문헌 근거 기록" 게이트를 연구 엔진 프로토콜(영역 8)에 내장. 영역 (5) 검색·RAG가 인스턴스 루프에 연결되어야 한다.
