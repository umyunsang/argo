# 5인 독립 검토 및 통합

최종 입력: `packet-manifest.json`의 동결 자료. 초기 Astra 작업은 취소·보존했고, 실제 수신·통합한 결과는 Sol/xhigh 대체 리뷰 다섯 개다. 동일 모델의 독립 세션/역할이며 cross-model independence나 실험 재현을 뜻하지 않는다.

- [한국어 통합](integration/review-synthesis-ko.md)
- [원검토 보존본](integration/five-reviews.json) · [수신·원본 해시](integration/intake.json)
- [29개 finding 대응](integration/finding-response-matrix.json)
- [이견 조정](integration/disagreement-resolution.json)
- [설계 선택 record](integration/architecture-selection-record.json) · [현재 실험 설계안](integration/integrated-study-design.json)
- [owner/port](integration/owner-port-contracts.json) · [연구 완료 기준](integration/research-completion-contract.json)
- [기존 prior-art 재결합](integration/prior-art-rebinding.json)
- [로컬 정적 검사](integration/local-validation.json)

다섯 verdict는 모두 `REVISE_BEFORE_EXPERIMENT`다. 통합 문서에 수정안을 반영했지만 task/metric/gold/power/budget/실행 및 native 구현은 아직 닫히지 않았다. 새 원고 작성은 ResearchDone 뒤에만 진행한다. 과거 invalid/runtime/instrument 결과의 범위는 바꾸지 않는다.

`integration/reviews/`는 원 보고서와 바이트가 같은 root-owned 보존본이다. `sol-xhigh/`의 원본은 작업자 보존 기록이다. `packet/existing-thesis-ko.qmd.txt`는 기존 원고의 검토용 snapshot이며 새 원고나 출판 후보가 아니다. 자료에는 내부 경로/제품 설계가 포함되므로 공개 논문이나 제출물에 통째로 첨부하지 않는다.

과거 UI-parity 전용 navigation contract는 역사 범위로 보존했다. 새 연구 방향의 active route는 `integration/navigation-contract.json`으로 검사한다. 이 전환은 전체 graph/원문/출판 검사를 면제하지 않는다.
