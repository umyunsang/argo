# Fable 5.1 수정본 재검토

**결론: 조건부로 과제·프로토콜 구체화에 진행 가능. 실험 실행 준비 완료는 아니다.**

- 검토: `anthropic/claude-fable-5-1` / `xhigh`, 새 독립 세션.
- 대상 commit: `ee7e0fdaf`.
- F1–F14: **12개 설계 수준 해결, 2개 부분 해결(F3·F7)**. 실증 종결은 없다.
- 치명적인 개념 차단 사항: reviewer는 없음으로 판정.
- root가 보고서 두 SHA, 입력 22개 commit SHA와 lineage를 확인했다.

## 남은 핵심 조건

1. 연구용 장치의 **코드 작성 범위에 대한 사용자 결정**.
2. C/G 강제 점검을 R1 launch·최종 artifact lock에서 집행하고 우회·탐지 범위를 검증.
3. 자동 R1/R2 사전 분류와 결과 lineage 검사. 사후 분류만으로 실행 권한을 대체하지 않음.
4. P1 대비를 보기 전 MUE 고정, agent 단일 artifact 선택·lock과 미lock 처리 명세.
5. 결측의 원인/관측 구분, P0 ancestry의 P2 제외, 단계별 invalid/retry와 전체 비용 회계.

Fable은 UNKNOWN 블록 자동 제외 기각, PA-NULL의 zero-effect 과잉 추론 기각, hash/비공개 구분, 로그/인과 구분 등 기존 root 반박을 타당하다고 평가했다. 단, adapter 우회가 자동 탐지된다거나 채점 1회가 비차등 결측을 보장한다는 제안은 root가 다시 한정했다. 리뷰 의견은 효능·권한 증거가 아니다.

다음은 **공개 ML programme·독립 scorer·license·source ancestry를 선정하는 일**이다. 다음 검토도 일반 설계 반복이 아니라 그 과제의 P0 프로토콜 검토로 한정한다. 인증 task·실행 가능한 arm은 아직 없고 P0/P1/P2는 미승인이다.

## 자료

- [재검토 원문 사본](../paper/research/fable51-design-review-20260907/re-review-01/integration/review.md)
- [root 조정 요약](../paper/research/fable51-design-review-20260907/re-review-01/integration/review-synthesis-ko.md)
- [N1–N10 후속 조건](../paper/research/fable51-design-review-20260907/re-review-01/integration/task-qualification-requirements.json)
- [사용자 결정용 구현 범위 제안](../paper/research/fable51-design-review-20260907/re-review-01/integration/apparatus-scope-decision.json)

새 코드·실험·설치·원고·native 구현·push는 하지 않았다.
