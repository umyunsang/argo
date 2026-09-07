# Fable 5.1 연구설계 검토 결과

**판정: 설계 방향은 타당하나, 실험 전 수정 필요.**

`anthropic/claude-fable-5-1` / `xhigh`가 커밋 `f2e203058`을 독립 검토했다. 기존 Sol 의견을 보기 전에 자체 판단을 수행하도록 요청했다. 보고서 두 SHA, 입력 13개의 committed SHA, 미정 필드 21개를 root가 재확인했다.

## 핵심 발견

- native 구축과 별개인 **연구용 실행 장치**의 범위·소유권이 빠져 있었다.
- **graph 기제가 실제 발화하는 과제 조건**과 주 outcome의 연결이 불명확했다.
- scientific run과 로컬 분석의 경계, UNKNOWN에 따른 차등 결측, hidden 자료의 실제 봉인, block/paired 분산 설계가 더 필요했다.

## 반영

프로젝트 내부 연구 장치의 개념 계층, R1 실행/R2 분석 구분, B/C/G 의무 집행 차이표, programme별 블록 설계, 단계별 승인을 보강했다. **P0 통합 feasibility → P1 B/C/G 개발 → P2 별도 봉인 확증**을 작업용 경로로 정리했다. 아직 실행 가능한 arm, task 인증 또는 실험 승인은 없다.

## 그대로 채택하지 않은 제안

- UNKNOWN이면 programme block을 통째로 제외: 실행 횟수와 연결된 선택 편향 위험 때문에 기본 규칙으로 기각했다.
- event가 없으면 graph 효과가 0: 인용 원문으로 입증되지 않는다.
- hash commitment는 비공개 보장, 기능 로그는 인과 분리라는 해석: 둘 다 성립하지 않는다.
- C/G 비교·두 시작·한 번의 repair·최저비용 prototype을 자동 고정: 모두 과제·개발 근거와 별도 승인 뒤 판단한다.

**다음은 공개 ML programme·독립 scorer·source ancestry를 구체화하는 일이다.** 수정본은 아직 Fable 재검토를 받지 않았으며, 검토 일치는 실험적 효능이나 실행 권한이 아니다. 새 실험·설치·원고·native 구현·push는 없었다.

## 상세 자료

- [원검토 사본](../paper/research/fable51-design-review-20260907/integration/review.md)
- [root 조정 및 요약](../paper/research/fable51-design-review-20260907/integration/review-synthesis-ko.md)
- [F1–F14 처리표](../paper/research/fable51-design-review-20260907/integration/finding-response-matrix.json)
- [현행 연구설계](../paper/research/fable51-design-review-20260907/integration/integrated-study-design.json)
- [단계별 완료·승인 계약](../paper/research/fable51-design-review-20260907/integration/research-completion-contract.json)
