# 졸업논문 중간 원고 — 2단 편집본

## 열기

- 읽기: `thesis-two-column-20260905.pdf` — A4, 12쪽
- 편집: `source/thesis-ko.qmd`
- 조판: `source/thesis-two-column.typ`, `source/ieee.csl`
- 참고문헌: `source/references-current-evidence.bib`
- 벡터 그림: `source/figures/current-evidence-20260905/*.svg`
- 편집 묶음: `thesis-two-column-20260905-editable.zip`

2026년 9월 5일 작성한 15쪽 단일단 원고를 내용 변경 없이 2단으로 재조판한 판본이다. 국문요약·본문·참고문헌은 2단, 제목·그림 3개·표 7개는 양단을 가로지르는 전체 폭으로 배치했다. 본문은 10 pt, 단 간격은 6 mm이며 전체 본문 폭은 160 mm다. 긴 추정대상 수식은 동일한 기호와 연산을 유지하여 두 줄로 정렬했고, 참고문헌 앞의 강제 페이지 나눔을 제거했다.

기존 단일단 보존본은 `../2026-09-05-current-evidence/`에 그대로 남아 있다. 이 폴더의 `before/`는 2단 편집 직전의 원고와 조판 규칙이다. 새 연구 결과나 효능 주장을 추가하지 않았다. 실측 근거의 기준 시각은 기존 원고와 같은 2026년 9월 5일 05:13:55 KST이며, 통합 실행 인증과 효능 평가는 아직 완료되지 않았다.

## 재조판

Quarto 1.10.18 및 번들 Typst 0.15.1 환경에서 생성했다. AppleMyungjo, Times New Roman, Arial 글꼴을 사용할 수 있어야 하며, 수학 조판에는 번들 New Computer Modern 계열이 사용된다. 편집 묶음을 풀고 다음 명령을 실행한다.

```sh
cd source
quarto render thesis-ko.qmd --to typst --no-execute --output thesis-two-column-rebuilt.pdf
```

이 명령은 연구 코드를 실행하지 않는다. 다른 글꼴이나 도구 버전은 배치를 바꿀 수 있다. 묶음에는 편집 원고·스타일·서지·그림만 포함하며 논문 원문, 연구 데이터, 모델, 자격증명과 제품 런타임은 포함하지 않는다.

## 검수 범위

`layout-verification.json`에 원고 본문·인용키 보존, 도표 수, 페이지 수, PDF 문자 재고 비교와 페이지 경계 검사를 기록했다. 모든 페이지를 시각 검토하여 2단 읽기 순서, 전체 폭 도표, 캡션 결합, 수식과 참고문헌 배치를 확인했다. 후속 검수 파일은 이 판본의 레이아웃 검증만을 뜻하며 연구 효능이나 최종 제출 규정 충족을 인증하지 않는다.

이 판본은 IEEE풍 공학 논문의 시각 언어를 적용한 학위논문 중간 초안이다. IEEE 공식 투고 템플릿 또는 대학 최종 제출 양식의 인증본은 아니며, 제출 전 학과 규정과 지도교수 검토가 필요하다. 원래 주장·근거 연결은 저장소의 `paper/manuscript/evidence/current-evidence-20260905/README.md`를 따른다.
