# 프로토타입 커널 명세

**Study B의 B2 하네스 구현이 곧 프로토타입 커널이다.** 데모용 별도 코드를 만들지 않는다.

## 위치

```
experiments/study_b/
  harness/components.py   다섯 성분 (그래프·프로토콜·검색·루프 + 평면 대체물)
  harness/arms.py         7아암, 절제가 정확히 한 성분만 다름
  harness/test_harness.py 19 검사
  tasks/oracle_t3.py      결정론적 검증기 (순수 표준 라이브러리, 실제 계산)
  tasks/run_t3.py         작업공간 구성 + oracle 격리 강제 + 채점
  tasks/test_t3.py        15 검사
  run_block.py            고정 실행 계약
  power_mcnemar.py        라벨된 검정력 계산
```

## 고정 진입점

```
/usr/bin/python3 experiments/study_b/run_block.py --arm <ARM> --task <TASK> --seeds <N> --out <RECEIPT>
```

데모 진입점은 `python -m study_b.demo <task>`로 고정하며, 위 커널을 그대로 호출한다.

## 안전 성질 (테스트로 강제)

- 승인 기록 없이 실제 지출을 시도하면 러너가 **스스로 거부**한다.
- 실험 기판 밖(`ORX_RUN_ID` 없음)에서 실행하면 거부한다 — 그런 에피소드는 결과가 아니다.
- 답이 나온 그래프 노드는 다시 쓸 수 없다.
- 6필드가 안 차면 결정이 기록되지 않는다.
- 근거 없는 수치는 이름으로 지목된다. 성분을 빼면 "검사하지 않았음"을 명시 보고한다.
- 작업공간에서 정답 디렉터리로 가는 심볼릭 링크는 거부된다.

## 이식성

격리 실행 환경에는 numpy가 없다(실제 실행 실패로 확인). 커널은 표준 라이브러리만 쓰며
`/usr/bin/python3`에서 그대로 돈다.
