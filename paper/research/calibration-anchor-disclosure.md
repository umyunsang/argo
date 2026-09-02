# 교정 기준의 정체 공개 (calibration anchor disclosure)

작성 2026-09-03T05:26:37+09:00

## 사실

`paper/experiments/calibration/label-form.json`의 25건 라벨은 **사람이 아니라 언어 모델이 기입했다.**

- 라벨러: `supervisor-model: claude-fable-5-1 (Claude Code supervisor session, non-human); user-authorized 2026-09-03 05:08 KST`
- 2차 라벨러: `second-pass model: claude-opus-5 (independent subagent, non-human)` (blind, 1차 답을 보지 못함)
- 사용자 승인: 2026-09-03 05:08 KST

## 명칭 규칙

이 세트는 **"supervisor-model-anchored calibration set"(감독 모델 기준 교정 세트)**로만 부른다.
`human-anchored`, `human-labelled`, `사람 라벨`로 쓰지 않는다. `human-label-protocol.md`는
사람 라벨을 전제로 작성된 원래 프로토콜이므로 수정하지 않고, 이 문서가 차이를 기록한다.

## 왜 중요한가

제공자 독립성은 유지된다 — 라벨러는 판정기(`huggingface` 계열)와도 처치 모델(`anthropic/claude-haiku-4-5`)과도
다른 계열이다. 그러나 **제공자가 다르다는 것과 사람이라는 것은 다른 성질이다.** 모델 기준은
모델들이 공유하는 체계적 오독을 그대로 물려받을 수 있고, 그 경우 일치도는 정확도가 아니라
공통 편향을 측정한다. 2차 라벨러도 모델이므로 24/25라는 일치도는 이 한계를 해소하지 못한다.

## 현재 상태

| 항목 | 값 |
|---|---|
| 기입된 라벨 | 25 |
| 판정 가능(satisfied/not_satisfied) | 19 |
| unclear (교정 세트에서 제외) | 6 — L004, L006, L014, L018, L020, L025 |
| 프로토콜 요건 | 25 |
| 부족분 | 6 |
| 2차 일치도 (전체 / unclear 제외) | 24/25 / 18/18 |
| 불일치 | L022(satisfied vs unclear) |

**판정 채점은 여전히 inadmissible이다.** 판정 가능한 라벨이 19건으로 요건에 미달하고,
기준이 사람이 아니라 모델이기 때문이다. 보충 양식
`paper/experiments/calibration/label-form-supplement-001.json`(8건, 동일 층화, seed 20260903)을
준비했다.

## 위협·한계 표에 들어갈 행

> 교정 기준이 사람이 아니라 언어 모델이다. 제공자 계열은 다르지만, 모델 공통의 체계적 오독은
> 이 기준으로 검출되지 않는다.
