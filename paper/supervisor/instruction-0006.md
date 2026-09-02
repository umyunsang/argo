# Supervisor instruction #0006 (paper) — Q-0003·Q-0004 답변, GPU는 Colab CLI, exa MCP 사용 규칙

- 발신: Claude Code supervisor
- 시각: 2026-09-02 22:00 KST
- 대상: argo-paper-root
- 근거: 사용자 답변(21:54 KST "권고대로 진행해. gpu가 필요할때는 colab cli 사용해. exa플러그인 사용중인거 맞지?"), `prime-agent mcp list`(exa, parallel), `which colab`

## 1. Q 답변 (questions.md에 기록됨)

- Q-0003: 권고대로. 지금은 (b) 설계 전용 Study A를 계속한다. 단 Study C 상태를 `DESIGN_ONLY_RESOURCE_BLOCKED`에서 "Colab CLI 경로 확보, 실행 전 사전등록 필요"로 바꾼다. 결정 기록 08A와 study-c-runbook.md의 자원 절을 그에 맞게 고친다.
- Q-0004: (a) 승인. 귀인 분과 과제 2건 소모. 소모 과제 id를 기록한다.

## 2. GPU 실행 규칙 (Colab CLI)

1. GPU가 필요한 모든 단위는 `colab` CLI(`~/.local/bin/colab`)로 실행한다. 먼저 `colab --help`와 하위 명령 도움말을 읽고 `paper/research/orx-usage.md`와 같은 형식으로 `paper/research/colab-usage.md`에 확인한 명령·용도를 적는다.
2. 실행 전 사전등록: 목표, 고정 명령, 입력 sha, 예상 VM 시간과 est_CU, 중단 규칙, 성공·실패 판정 기준을 결정 기록으로 남긴다. 사전등록 없는 GPU 실행은 금지다.
3. 비용 회계: `paper/supervisor/cost-ledger.md`에 실행마다 VM 생존 시간(provision→close), 적용 요율과 출처, est_CU, 누적 est_CU를 적는다. CLI에 잔액 조회가 없으므로 추정 회계로 한다. 실행이 끝나면 즉시 세션을 닫고 `colab sessions`가 비어 있음을 기록한다.
4. 승인 게이트(supervisor 가정, 사용자가 바꿀 수 있음): 단일 실행 예상 10 CU 초과 또는 누적 25 CU 초과 전에는 Q(blocking: true)로 승인을 받는다. 첫 GPU 실행은 규모와 무관하게 Q-0005로 예상 CU와 계획을 올리고 답변 후 실행한다.
5. Colab 세션은 시간 제한이 있다. Study C의 과제당 약 24시간 실행은 체크포인트·재개 가능한 단위로 나눠 설계하고, 이를 RUNBOOK에 반영한다.
6. 파일럿 전제 구축과 16-episode 파일럿 자체는 GPU가 필요 없다. GPU 없이 되는 일을 먼저 끝낸다.

## 3. exa MCP 사용 규칙

1. 세션에는 MCP 서버 `exa`와 `parallel`이 등록되어 있다. 사용 여부를 확인해 첫 보고에 적는다.
2. exa는 웹·문서 검색용이다: 자율 연구 엔진의 공식 문서와 릴리스, 벤치마크·선행 연구의 공개 저장소와 코드, 평가 rubric 원문, 도구 사용법. 문헌 발견과 출처 provenance는 계속 `orx discover`·`orx paper`로 한다. exa 결과로 찾은 논문도 반드시 orx로 다시 취득해 exact-version 아카이브와 locator를 만든다.
3. exa 질의는 retrieval record의 `web_queries` 배열에 질의·시각·채택 결과 URL을 기록한다.

## 4. 루프

instruction-0005 §2의 상시 루프는 그대로다. 이 지시로 멈추지 않는다.
