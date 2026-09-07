# 장기 지평 하네스 연구 적용 요약

[전체 분석](../paper/research/long-horizon-harness-benchmark-20260907/benchmark-synthesis-ko.md) · [설계 보강](../paper/research/long-horizon-harness-benchmark-20260907/research-design-amendment.json) · [논문 삽입 후보](../paper/research/long-horizon-harness-benchmark-20260907/manuscript-insert-ko.md)

여덟 지정 연구를 원문으로 검토했다. 핵심은 기능을 모두 합치는 것이 아니라, 불변 원자료·현재 산출물·절차 계약·채택 가능한 근거·작업 뷰를 구분하는 것이다.

주 비교는 강한 evidence-aware TREE와 동일 기회 TYPED 제어 사이에 유지한다. 추가한 설계는 조건부 부정 결과 재사용, 관련/무관한 변경 분리, 과잉/부족 철회, 독립 결과와 총비용 분리다. 압축·meta-depth·환경 합성·학습은 후속 진단이며 현재 처리군에 동시에 넣지 않는다.

- 논문 원문: 여덟 지정 + tampering 보조 연구, v1 PDF 9개.
- exact source locators: 46개.
- 독립 원문/기존 증거 audit: 5개. 최종 synthesis review PASS.
- provenance 검사: 6개 test PASS, 위반 주입 5개가 먼저 실패함을 확인.
- 정적 반례: 10개 test, 8개 경계·12개 control·14개 malformed/missing 사례 PASS.
- 위 수치는 명세/출처 검사이며 agent 효능이나 논문 성능 재현이 아니다.
- 원고 정본/기존 exports/소모된 run은 그대로 보존했다. 새 model/World 실행과 native 구축은 하지 않았다.
