# Supervisor instruction #0005 (paper) — 상시 자율 연구 루프: 라운드 보고 후 멈추지 않는다

- 발신: Claude Code supervisor
- 시각: 2026-09-02 21:55 KST
- 대상: argo-paper-root
- 근거: 커밋 c677aeb6e·5527c7926·4b019fce1 검토, `literature-round8-retrieval-record.json`(loops 0), `paper/research/` 목록(design-comparison 없음), status.md 21:41, Q-0003·Q-0004, 사용자 지적(21:48 "지시 자체를 자율 연구하도록 지시해야 하는데 ... idle")

## 1. 진단

1. 21:31~21:45 사이에 한 일은 인정한다: 출처 아카이브 복원과 전역 locator 게이트, 4편 전문 등록(fulltext·tex·reports), 결정 기록 08A~08C, research-design 갱신, orx-usage.md, Study C RUNBOOK, status와 Q 두 건.
2. 그러나 instruction-0003 §3 가운데 다음이 빠졌고, 세션은 보고 커밋에서 턴을 끝냈다.
   - §3-3 설계 경쟁 문헌 루프: retrieval record에 `orx discover` 루프가 0개다. 신규 전문 읽기는 이미 알려진 4편뿐이며 "최소 5편 이상, 3 objective × embedding·keyword·openalex"가 수행되지 않았다.
   - §3-4 설계 비교표 `paper/research/design-comparison-round8.md`가 없다.
   - §3-7 실행: 16-episode 파일럿의 전제(은닉 과제 샌드박스, 독립 채점 보정, 고정 러너)를 만들기 시작하지 않았다. status의 next action 1에 적어 두고 멈췄다. Study C는 Q-0003 기본값 (b)대로 보류가 맞지만, 파일럿 전제 구축은 자원이 필요 없으므로 지금 할 수 있는 실행 단위다.
3. 지시가 "라운드를 마치면 보고"로 끝나는 유한 과제 형식이었던 것이 원인이다. 이 지시로 형식을 바꾼다.

## 2. 상시 루프 규칙 (이 지시부터 계속 적용)

1. 턴은 보고로 끝나지 않는다. status.md를 갱신하고 커밋한 직후, 같은 턴 안에서 다음 단위를 고르고 시작한다. 사용자 메시지가 오기 전까지 멈추지 않는다.
2. 한 사이클은 다음 여섯 단계이고, 6이 끝나면 즉시 1로 돌아간다.
   1. 격차 식별: status.md 블로커, context-graph에서 근거가 약한 노드, research-design의 미해결 반증 조건, capability-map의 미검증 항목에서 이번 사이클 목표 1~3개를 고른다. 목표와 선정 근거를 status.md에 한 줄씩 적는다.
   2. 문헌 루프: 목표마다 `orx discover embedding`·`keyword`·`openalex`를 모두 돌리고 명령·결과 id·선정 규칙을 retrieval record에 기록한다. 정본에 없는 상위 후보를 `orx paper`로 전문 취득해 `FULL_PAPER_READ`로 등록한다.
   3. 설계 비교와 결정: 새 전문 읽기를 설계 비교표에 행으로 추가하고, 변경 후보마다 여섯 항목 결정 기록(대안·선행연구 locator·근거·결정·기대효과/위험·반증조건)을 남긴다. 기각도 no-change 기록으로 남긴다. research-design.md와 context-graph를 같은 커밋에서 갱신한다.
   4. 실행 단위: 자원 없이 지금 만들 수 있는 것을 하나 골라 만들고 돌린다. 우선순위는 파일럿 전제 세 가지(은닉 과제 샌드박스와 무결성 probe의 failing-first fixture, 독립 채점 보정 절차와 judge 일치도 측정 fixture, 고정 Study A 러너 한 명령)이고, 세 가지가 통과하면 16-episode 파일럿을 `orx create-experiment`/`orx exp`로 실행한다. 실행 결과는 `EXECUTED`/`PARTIAL`/`NOT_EXECUTED`로만 표기한다.
   5. 검증과 커밋: `python3 .orx/paper_validate.py` 통과, 변경 파일만 커밋, 푸시.
   6. status.md 갱신: 이번 사이클에서 닫은 격차, 남은 격차, 다음 사이클 목표. 그리고 즉시 1로.
3. Q는 루프를 멈추지 않는다. `default_if_unanswered`를 적용하고 계속 진행한다. 여섯 필드에 `blocking`을 넣고, `blocking: true`는 기본값으로 진행하면 되돌릴 수 없는 손실(외부 제출, 예산 지출, 과제 풀 소모)이 생길 때만 쓴다. Q-0003은 (b) 보류, Q-0004는 blocking이므로 사용자 답변 전까지 귀인 분과만 보류하고 나머지 파일럿 전제 구축은 계속한다.
4. 멈춰도 되는 경우는 두 가지뿐이다. 사용자 메시지가 왔을 때, 그리고 현재 격차 목록의 모든 항목이 자원·답변 없이는 한 걸음도 진행할 수 없을 때. 후자면 status.md에 "모든 격차가 외부 의존"이라고 각 격차의 필요 자원과 함께 적고 멈춘다. 그 전에는 멈추지 않는다.
5. 라운드 번호는 사이클마다 올린다(round 9, 10, …). 파일 형식은 round 8과 같다.

## 3. 지금 즉시 (이 지시의 첫 사이클)

1. §1-2에서 빠진 세 가지를 이번 사이클 목표로 한다: (a) 설계 경쟁 문헌 루프 3 objective(통제 실험 설계, 결과 측정·독립 채점·은닉 과제 격리, 요인 설계·표본·통계)에서 신규 전문 읽기 5편 이상, (b) `design-comparison-round8.md`(정본 FULL 읽기 포함 선행 실험 8편 이상 × 설계 요소 10열, Study A 대비 강점·약점·변경점), (c) 파일럿 전제 첫 번째인 은닉 과제 샌드박스와 무결성 probe의 failing-first fixture 구축.
2. handoff-2026-09-02.md에 재개 한 줄이 아직 없다. 추가한다.
3. 세 목표를 마치면 §2-2의 6단계로 status를 갱신하고 곧바로 다음 사이클로 간다.

## 4. 불변 조건

instruction-0003 §5 그대로. 추가: 공개 원고에 엔진 이름을 쓰지 않는 규칙은 `orx-usage.md`의 표현("autonomous research engine")을 따른다.
