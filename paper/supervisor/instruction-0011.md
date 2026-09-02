# Supervisor instruction #0011 — Quarto 정본 원고 전환, 서사 보정, 하네스 비교 arm 설계(실행 금지)

- 발신: Claude Code supervisor
- 시각: 2026-09-03 05:45 KST
- 대상: argo-paper-root
- 근거: 사용자 지시 2026-09-03 05:33 KST(Quarto 도입), status.md cycle 61(next_first_action: 한글 Ⅰ장), `paper/word/tooling-benchmark/benchmark.qmd`(2026-09-02 13:09, 세션이 Quarto를 벤치마크했으나 채택 기록 없음), `paper/word/build_submission.py`(현재 paper.tex → pandoc → docx), supervisor 검증 렌더(2026-09-03 05:37 KST, Quarto 1.10.18, 아래 §1.1)
- 선행 지시: instruction-0009·0010은 전부 유효하다. 이 지시는 0009 §2(한글 정본 원고)의 소스 형식을 Quarto로 확정하고, 0010의 작업 순서 안에 §1~§3을 끼워 넣는다.

## 0. 요약

1. 한글 정본 원고의 소스는 Quarto(`.qmd`)로 한다. 그림·표·소스코드·인용을 한 소스에서 관리하고, 표는 receipt를 읽는 코드 셀이 렌더 시점에 생성한다. 최종 산출물은 지금처럼 docx(그리고 기존 hwp 경로)이며 모든 게이트는 그대로 적용된다.
2. 한글 본문 서술에 보정 4건을 반영한다(§2). 특히 Ⅴ장의 "교정 세트는 이 시스템이 스스로 만들 수 없는 유일한 부품" 문장은 2026-09-03 05:17 KST 이후 사실과 다르다.
3. 현재 논문에는 다른 하네스와 비교 가능한 성능 수치가 하나도 없다. 결정론적 검증기를 쓰는 하네스 대 하네스 비교 arm을 **설계·비용 산정만** 하고 Q-0009로 올린다. 실행·지출은 금지한다.

## 1. Quarto 정본 원고

### 1.1 supervisor 검증 결과 (2026-09-03 05:37 KST)

`/usr/local/bin/quarto` 1.10.18이 설치돼 있고 pandoc을 내장한다. `quarto check jupyter`는 `/opt/homebrew/opt/python@3.14/bin/python3.14` + Jupyter 5.9.1로 통과했다. 한글 제목·`# Ⅰ. Introduction` 제목·`![캡션](png){#fig-x}`·파이프 표 `{#tbl-x}`·`@fig-x`/`@tbl-x` 상호참조·파이썬 코드 블록을 넣은 소스를 `reference-doc: paper/word/reference.docx`로 렌더한 결과, docx에 `[Heading1] Ⅰ. Introduction`, `[ImageCaption] 그림 1. 전체 시스템 아키텍처`, `[ImageCaption] 표 1. …`, `[SourceCode]`, 본문 내 "그림 1", "표 1" 참조, `pgSz w=11906 h=16838`(A4)이 그대로 나왔다. 렌더 시간 0.6초. 따라서 `thesis_form_gate`의 용지·제목·그림 수·표 수 조건은 Quarto 경로로 충족 가능하다.

### 1.2 구성

- 소스 위치: `paper/manuscript/thesis-ko.qmd`(단일 파일) 또는 장별 파일을 `{{< include >}}`로 묶은 `paper/manuscript/` 디렉터리. 선택 이유를 결정 레코드에 남긴다.
- 프런트매터 기준: `paper/word/tooling-benchmark/benchmark.qmd`의 설정(공식 reference-doc, `ieee.csl`, `references.bib`, crossref `그림`/`표`/`식`, caption 위치)을 출발점으로 삼되, 학과 양식(`paper/official-thesis-requirements.md`)이 요구하는 캡션 형식과 `title-delim`을 다시 확인해 맞춘다. `lang`은 본문이 한글이므로 `ko`로 두고 영문 핵심어는 그대로 쓴다.
- 표: 최소 5개(§2.3)를 `#| label: tbl-…`, `#| tbl-cap:` 코드 셀이 receipt JSON에서 읽어 생성한다. 표 값이 receipt와 다르면 렌더가 실패해야 한다(셀 안에서 `assert`). 이것이 "커밋된 바이트에서 재도출" 원칙을 원고까지 확장하는 방법이다.
- 소스코드: 재도출·변이 감사 스크립트의 핵심 부분을 `#| echo: true` 리스팅으로 보인다. 양식이 본문 내 코드 리스팅을 허용하는지 `official-thesis-requirements.md`로 확인하고, 허용되지 않으면 부록으로 보낸다.
- 그림: `paper/figures/rendered/` 산출물을 `{#fig-NN}`으로 넣는다. instruction-0010 §1의 gpt-image-2 재생성이 끝나면 ledger의 `output_path`를 따라 자동으로 교체되도록 경로를 ledger에서 읽는다.
- 빌드 진입점: `submission_artifact_gate`가 `paper/word/build_submission.py`를 재빌드 명령으로 못 박고 있으므로 이 스크립트가 `quarto render … --to docx`를 호출하도록 바꾼다. 게이트 정의를 바꾸지 않는다. 바이트 재현성 receipt(`reproducible-build-receipt.json`)는 Quarto 경로에서도 통과해야 한다(docx 내부 타임스탬프 정규화는 지금 방식 유지).
- 공개 출력 게이트: qmd 본문·코드 셀 출력 어디에도 엔진 제품명, run id, `.orx`, supervisor, 이미지 벤더명이 찍히면 안 된다. 코드 셀은 receipt에서 숫자만 읽고 경로·id는 출력하지 않는다.
- 영문 초안(`paper.tex`)은 역사적 산출물로 보관한다. 정본은 qmd 하나다. 두 소스를 병행 편집하지 않는다.

### 1.3 결정 기록

2026-09-02 13:09~13:12에 Quarto 벤치마크를 만들고도 채택하지 않은 이유를 결정 레코드에 적는다. 그 이유가 지금도 유효한 게이트 실패라면 채택 대신 Q로 올린다. 그렇지 않으면 전환을 RD로 기록하고 반증 조건은 "전환 후 `thesis_form_gate`·`submission_artifact_gate`·재현성 receipt 중 하나라도 실패"로 둔다.

## 2. 한글 본문 서사 보정

2.1 **Ⅰ장 첫 절에 원칙을 세운다.** "측정 도구의 admissibility가 효과 추정에 선행한다"를 한 문단으로 먼저 선언하고, 채점기 반증·교정 세트 크기·판정 불인정 선언이 모두 그 원칙의 결과임을 명시한다. 현재 영문 초안은 이 원칙을 Study scope 절 셋째 문단에 묻어 두고 있다.

2.2 **Ⅴ장 교정 세트 문장을 갱신한다.** 영문 초안 결론의 "the set is the one component this system cannot produce for itself"는 이제 사실이 아니다. 2026-09-03 05:17 KST에 감독 모델(비인간) 기준 교정 세트 25건이 존재하고, 2차 라벨러 일치도 24/25(unclear 제외 18/18, 20% 중복 5/5)가 기록돼 있다. 한글 본문은 (a) 라벨러가 사람이 아님을 그대로 쓰고, (b) 선택적 평가기의 예비 결과(무결 19건 기준)를 Ⅳ장에 넣고, (c) 25건 무결이 갖춰질 때까지 "예비"임을 표시한다. instruction-0010 §2의 표현 규칙("감독 모델 기준 교정 세트", "human-anchored" 금지)을 지킨다.

2.3 **표 최소 5개의 재료는 이미 Ⅳ장에 있다.** 조건표(C00~C11), 가설·반증 조건표(H-A~H-C), 채점 도구 반증 결과표(단서 매칭 오판율, 대체 판정기 일치도, 채점 방식 이동 0.188), 분산 성분표(G-study 조건·요소·잔차 성분과 dependability), 예산 완료율표(조건별 완료/에피소드, Wilson 구간). 모두 §1.2의 코드 셀 방식으로 만든다.

2.4 **과정 지표는 조작 확인으로만 쓴다.** cycle 59의 판단을 한글 본문에서도 유지한다. 호출 수·토큰이 조건을 구분한다는 사실을 결과로 승격하지 않는다.

## 3. 하네스 비교 arm — 설계와 비용 산정만

### 3.1 문제

현재 설계는 한 하네스 안의 조건(2×2)을 LLM 판정 endpoint로 비교한다. 선행 하네스 연구는 같은 모델을 고정하고 하네스 대 하네스를 결정론적 검증기(테스트 통과, 점수, 기록)로 비교해 수치를 낸다. 기저 하네스 논문(`2608.23552`, FULL)은 장문맥 스위트·ARC-AGI-3·nanoGPT speedrun·PMPP-Hard에서 Claude Code·Codex·Pi-mono와 비교했고, 최소 하네스 계열은 Terminal-Bench 같은 실행 채점 벤치마크에서 순위로 주장한다. 이 논문에는 어떤 선행 하네스와도 비교 가능한 수치가 없다. 판정 endpoint가 무너진 이유의 절반은 "검증기가 결정론적이지 않은 과제를 골랐다"는 데 있다.

### 3.2 설계 과제 (실행 금지)

- 처치: 같은 모델·같은 예산에서 (i) 상속 기저 하네스(`thesis-contribution-ledger.md`의 `INHERITED` 구성) 대 (ii) 기저 + 본 논문의 구조화 프로토콜(C10/C11 구성). 기저 하네스는 제품명이 아니라 `2608.23552` 인용으로만 지칭한다(public_output_gate).
- 과제 후보: 실행 채점이 가능한 공개 벤치마크 중 논문 범위(연구·ML 과제)에 맞는 것. Arbor가 쓴 MLE-bench Lite 부분집합, 실행 채점 확장이 가능한 dry-lab 과제, 또는 완료율 arm(Q-0007)의 과제를 결정론적 검증기로 재구성한 것. 각 후보의 검증기가 결정론적인지, 목표 바이트 격리가 가능한지, GPU가 필요한지 표로 비교한다.
- endpoint: 통과/실패 이진 → McNemar 기반 표본 크기, 또는 벤치마크 고유 점수 → 과제 클러스터 부트스트랩. 판정기는 쓰지 않는다.
- 비용: 처치 토큰 USD, 판정 0 USD, GPU 시간(필요 시 Colab CLI, 사용자 정책 "gpu가 필요할때는 colab cli 사용"), 벽시계 시간. 상한 시나리오 2개(최소 검출 가능 설계, 예산 절반 설계).
- 산출물: `paper/research/harness-comparison-arm-design.md` + 사전등록 초안 JSON + 비용 receipt. 비교 실험 표에 `2608.23552`의 비교 방식을 comparable experiment로 추가한다. 최소 하네스 계열의 Terminal-Bench 결과는 논문이 아니라 공개 게시물이므로 근거 수준을 낮게 표기하거나 제외한다.
- Q-0009로 올린다. 기본값 (b) "실행하지 않음". 사용자가 (a)를 고르기 전에는 에피소드 하나도 돌리지 않는다.

## 4. 작업 순서

instruction-0010 §4의 순서를 다음으로 갱신한다: (1) Quarto 전환 + 한글 Ⅰ장을 qmd로 직접 집필 → (2) 0010 §1 그림 재생성, §2 라벨 receipt, §3 HF 소급 회계 → (3) §3 하네스 비교 arm 설계 → (4) 연구 사이클. 사이클마다 status.md 첫 줄에 어디까지 왔는지 적는다.

## 5. 사용자 위임 사항 (원문)

"ai 에이전트가 스스로 연구를 설계하고, 연구 가설이나 조건, 방법 등 모든 요소를 직접 설정해야 하고, 근데 이걸 또 그냥 정하는게 아니야 깊이 있는 추론과 인사이트를 통해 선택을 해야하고, 그 선택에 대해 근거까지 있어야 해. 비슷한 실험찾아보고, method 찾아보고, 쓸만한 레퍼런스 찾아보고, 자료정리도 해야해 또한 이모든 걸 다른 ai 에이전트들도 인지하고 작업할수 있게 context graph로 스스로 작성하서 그래프 맵을 구축해야 해. 관련 선행 연구를 찾아서 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리 구축하고 실험을 진행하는거야. 비슷한 연구들이 어떤식으로 실험을 설계했는지 비교 경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행하는거야."

2026-09-03 05:33 KST: "논문작성 도구는 quarto 도구를 설치하고 사용하면 그림과 표 넣기도 편하고 소스코드도 넣을수 있어."

## 6. 불변 조건

- instruction-0010 §6 전부 유지(키 비노출, `label-key.json` 비전송, 명칭 규칙, AGENTS.md git 규칙, 세션 모델 변경 금지, 답변된 orx ancestor 편집 금지, DeepVoice 증거 사용 금지).
- §3은 설계 문서만 만든다. 벤치마크 과제 다운로드·에피소드 실행·GPU 할당·판정 호출 어느 것도 하지 않는다.
- Quarto 전환 중에도 `paper/word/graduation-thesis.docx`는 항상 게이트를 통과하는 상태로 커밋한다. 전환이 게이트를 깨면 되돌리고 Q로 올린다.

## 7. 보고

status.md 첫 줄에 (1) 정본 소스 경로와 렌더 게이트 통과 여부, (2) 한글 장 진행(0/5 → n/5)과 표 개수, (3) Q-0009 준비 여부를 적는다. 다음 supervisor 점검은 45분 정책에 따른다.
