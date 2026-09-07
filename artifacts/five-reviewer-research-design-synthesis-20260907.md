# 5인 Sol/xhigh 연구설계 검토 통합

[전체 통합](../paper/research/five-reviewer-design-review-20260907/integration/review-synthesis-ko.md) · [설계 기록](../paper/research/five-reviewer-design-review-20260907/integration/architecture-selection-record.json) · [현 연구 설계](../paper/research/five-reviewer-design-review-20260907/integration/integrated-study-design.json)

5개 독립 role review는 모두 REVISE_BEFORE_EXPERIMENT다. 이는 과학적 투표가 아니라 29개 구체적 검토 사항의 수신이다.

- 주 목적은 장기 자율연구 하네스 시스템의 연결·제어를 실험으로 선택하고, 논문 근거를 후행 ARGO prototype으로 넘기는 것이다.
- B/C/G 개발 screen을 작업안으로 둔다: 강한 source-backed tree, 동일 사실의 compulsory control, 동일 의무의 graph/evidence control. Graph는 아직 승자가 아니다.
- 2-arm/3-arm/2×2 의견과 sample-size 제안은 보존한다. 고정 6/24 family 하한은 채택하지 않고 power/precision·비용 근거로 산출한다.
- DiscoveryPort, SourceEvidenceService, read-only PaperService의 owner 충돌을 설계상 정정했다. 외부 run reconciliation은 capability 미확인 상태이며 exactly-once를 주장하지 않는다.
- ResearchDone 뒤 원고 작성, PublicationReady에서 실제 그림·metadata·페이지 확인을 한다. 지금은 새 본문 작성과 실험/native 실행 모두 닫혀 있다.
- 기존 문헌과 21개 scoped prior-art locators, instrument·실패 기록을 유지한다. C64 causal invalid, v12 INVALID, font의 다섯 호출 호환성, World-init static-only는 범위를 바꾸지 않는다.

다음은 실제 공개 ML 과제·중립 scorer·B/C/G 차이·전체 budget 명세다. 이 조건을 채우기 전 SOTA나 통합 효능을 주장하지 않는다.
