# 5분 데모 시나리오 — B2 하네스가 과제 하나를 끝까지 수행

진입점: `python -m study_b.demo T3 --seed 42`

| 시각 | 화면 | 검증 가능한 산출 |
|---|---|---|
| 0:00 | 과제 제시 — `TASK.md`와 `data.json`만 있는 작업공간. 정답 파일은 여기에 없다. | `run_t3.assert_isolated`가 격리를 강제, 심볼릭 링크까지 거부 |
| 0:30 | **그래프 노드 생성** — gap → hypothesis → decision 노드가 타입과 함께 생긴다 | `TypedContextGraph.render()` |
| 1:00 | **결정 기록** — 6필드가 모두 차야 통과. 반증 조건을 비우면 그 자리에서 거부된다 | `ValueError: decision record missing fields: ['falsifier']` |
| 1:30 | 실행 — 교차검증을 실제로 돌려 receipt를 만든다 | `oracle_digest` |
| 2:30 | **반증 트리거** — 사전등록 임계값에 못 미치면 루프가 계속된다 | `falsified on ['pass_rate']; pivoting` |
| 3:30 | **궤도 수정** — 다음 반복에서 표현을 바꿔 재실행 | `loop.history` 반복 기록 |
| 4:00 | **청구 잠금** — 보고서 초안의 수치를 receipt와 대조 | 근거 없는 수치를 이름으로 지목 |
| 4:30 | 대비 시연 — 같은 과제를 B2−P(잠금 없음)로 돌리면 같은 초안이 **그대로 통과**한다 | `{"checked": false}` |
| 5:00 | 마무리 — "이 시스템이 자랑하는 것은 정답률이 아니라, 틀렸을 때 틀렸다고 말한다는 것이다" | |

핵심 대비는 4:30이다. 성분 하나를 빼면 같은 보고서가 검사 없이 통과한다 — 절제 설계가 곧 데모다.
