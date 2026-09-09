# 졸업논문 중간 원고 — 2026-09-05

## 열기

- 읽기: `thesis-current-evidence-20260905.pdf`
- 편집: `source/thesis-ko.qmd`
- 참고문헌: `source/references-current-evidence.bib`
- 조판: `source/thesis-current.typ`, `source/ieee.csl`
- 그림 원본: `source/figures/current-evidence-20260905/*.svg`
- 편집 묶음: `thesis-current-evidence-20260905-editable.zip`

PDF는 15쪽이며 국문요약·5개 장·참고문헌, 그림 3개, 수정 가능한 표 7개와 출판 논문 13편을 포함한다. 실측 결과의 기준 시각은 2026년 9월 5일 05:13:55 KST다. 96회는 채점기의 정답/손상 출력 검사이며 에이전트의 통합 과제 해결 횟수가 아니다. 통합 실행 인증 및 효능 평가가 완료되지 않았다는 한계를 본문과 도표에 명시했다.

이 보존본은 일반적인 수정 작업의 대상이 아니다. 이후 연구는 `paper/manuscript/thesis-ko.qmd`에 반영하고 별도 날짜/판본으로 보존한다. `before/`는 개정 전 원고로 현재 결과로 인용하지 않는다.

## 재조판

Quarto 1.10.18 및 번들 Typst 0.15.1, AppleMyungjo·Times New Roman·Arial 글꼴을 사용했다. 편집 묶음을 풀고 다음 명령을 실행한다.

```sh
cd source
quarto render thesis-ko.qmd --to typst --output thesis-rebuilt.pdf
```

다른 환경의 글꼴 대체와 도구 버전 차이는 페이지 배치를 바꿀 수 있다. 연구 코드를 실행하는 셀은 없다. 이 묶음에는 논문 원문 보존본, 연구 데이터, 모델, 자격증명 또는 제품 런타임이 포함되지 않는다.

## 근거와 제출 전 확인

저장소의 `paper/manuscript/evidence/current-evidence-20260905/README.md`에서 주장·영수증·문헌·문맥 그래프와 다음 갱신 절차를 확인한다. 벡터 PDF/600 dpi PNG 파생본 및 IEEE 공식 도표 지침 보존본은 `paper/manuscript/figures/current-evidence-20260905/`에 별도로 남겼다.

IEEE풍 흑백 공학 도표 원칙을 적용한 **학위논문 중간 초안**이며 IEEE 투고본이나 대학 최종 제출 규정의 인증본은 아니다. 언어모델이 초안·검토·그림 제작을 보조했다. 저자·지도교수의 내용 검토, 학과 표지·인준지·편집 규정 확인, 필요시 검증된 HWP/Word 변환이 남아 있다.
