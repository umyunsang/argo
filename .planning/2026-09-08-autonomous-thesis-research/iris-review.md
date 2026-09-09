# Iris 원문 검토

2608.02143v1, 전체 추출 본문 1–1406 LF를 읽었다. 그림 추출 텍스트는 포함하지만 시각 검사는 하지 않았다. arXiv 공개 원고이며 동료심사 게재지는 미확인이다. SHA/locator는 iris-review.json.

가장 직접적인 신규성 반례다. scope·찬성/반증 근거·active/qualified/invalidated claim과 후속 증거에 따른 수정이 이미 명세돼 있다(IRIS-02). 따라서 이들의 존재를 새 기여로 삼지 않는다. 연구 질문은 같은 근거와 진단 권리에서 graph-mediated 집행/재개가 강한 evidence-aware 대조군보다 실제 추가 가치를 주는지로 남는다.

실험 변경을 수반하지 않는 진단과 후보 변경을 분리하는 것은 채택할 설계 근거다(IRIS-03). 다만 논문의 epistemic/interventional 분류와 이 저장소의 R1/R2 비용·실행 권위는 동일하지 않다. 새 학습·selection score를 진단으로 이름만 바꾸어 우회하지 않는다.

Main leaderboard는 직접 재현한 matched control이 아니다. Cross-domain optimizer backbone도 다르며, 제거 비교는 15개 small-data task에 각 1회다. Information management 제거는 장기 지식과 다양한 근거 접근도 같이 없앤다. 따라서 충분한 tree/flat 대조군을 보존하는 것이 이 연구의 공정성 조건이다. 본문 private-test trajectory가 post-hoc 평가인지 온라인 노출인지 해당 절에서 명확하지 않으므로 local final-only scoring의 근거로 그 그림을 재사용하지 않는다.

채택: 근거 획득과 지식 수정의 명시적 연구-loop, scoped claim의 선행기술 인정, 강한 공통 evidence 권리. 보류: Iris 전체를 새로운 독립 arm으로 즉시 추가, paper의 headline 수치를 로컬 prior/power/SOTA로 전환. 이 검토는 효능 측정이 아니다.
