# Supervisor instruction #0009 — 학과 졸업논문 양식 준수·한글 본문·그림/표 최대화·gpt-image-2 흑백 벡터 다이어그램

- 발신: Claude Code supervisor
- 시각: 2026-09-03 05:20 KST
- 대상: argo-paper-root (goal `abf5e851-82b2-49e6-9851-c869ae06a99b` active)
- 근거: 사용자 지시(2026-09-03 04:55 KST, §8에 원문), `/Users/um-yunsang/Downloads/[붙임1]+졸업논문(양식).pdf` 3쪽 전문(supervisor가 직접 읽음; 세션 사본 `paper/hwp/source/[붙임1]+졸업논문(양식).hwp`, `paper/hwp/work/official-template-page-{1,2,3}.png`), `paper/official-thesis-requirements.md`, `paper/word/graduation-thesis.pdf`(현재 제출물), `paper/word/build_submission.py`, `paper/supervisor/status.md`(cycle 57), `paper/supervisor/questions.md`(Q-0006, Q-0007 open)

## 0. 현황 진단 (supervisor 측정값)

현재 제출물 `paper/word/graduation-thesis.pdf`는 사용자 요구와 학과 양식에 모두 미달한다. 이는 연구 루프를 대체하는 것이 아니라 **연구 루프 안에서 최우선으로 닫아야 할 결함**이다.

| 항목 | 양식 요구 | 현재 제출물 | 판정 |
|---|---|---|---|
| 용지 | A4, 1단, 더블 스페이싱 | Letter(612×792pt) | FAIL |
| 본문 언어 | 한글 (사용자 지시) | 영어 전문 | FAIL |
| 제목 페이지 | 국문 제목 + 영문 제목 | 영문 제목만 | FAIL |
| 요약 | 국문요약 ≤500자 + Keyword ≤5 | 영문 Abstract(국문 요약은 `korean-summary.txt`에만 존재) | FAIL |
| 장 번호 | Ⅰ, Ⅱ, Ⅲ… / 절은 1, 2, 3 | 번호 없음 | FAIL |
| 그림 | 본문에 필요한 그림 포함, 제목 하단 국문 병기 | 0장 | FAIL |
| 표 | 제목 상단 국문 병기 | 0개 | FAIL |
| 참고문헌 | 인용 순서, 양식 예시 형식, 우측 상단 [n] | 확인 필요 | CHECK |
| 분량 | A4 10매 기준(장당 1,000자 내외) | 21쪽(Letter, 영문) | 재측정 |

`paper.tex`는 ASCII LaTeX이고 고정 툴체인에 CJK 폰트가 없다(`build_submission.py` docstring). 따라서 한글 본문은 **툴체인 결정**을 먼저 요구한다(§3).

## 1. 양식 규칙 — 그대로 게이트로 옮긴다

양식 PDF 1쪽 "졸업논문 작성요령"과 2–3쪽 예시에서 추출한 규칙이다. 모두 `.orx/paper_protocol.json`의 `submission_artifact_gate`(또는 신설 `thesis_form_gate`)에 결정론적 검사로 넣고, `paper_validate.py`가 fail-closed로 막는다.

- G1 **순서**: 제목 페이지 → 국문요약(Abstract) → Ⅰ. Introduction → Ⅱ. Related Works → Ⅲ. Proposed Method → Ⅳ. Experimental Results → Ⅴ. Conclusions → 참고문헌(References). 양식의 장 제목 문자열을 그대로 쓴다(`Ⅰ. Introduction`, `Ⅱ. Related Works`, `III. Proposed Method`, `IV. Experimental Results`, `V. Conclusions`, `참 고 문 헌 (References)`). 작성요령의 "관련 기술현황"은 Ⅱ장, "본문(제안기술)"은 Ⅲ장, "실험결과"는 Ⅳ장에 대응한다.
- G2 **용지·조판**: A4(595×842pt), 1단, 더블 스페이싱, 쪽 번호(양식 예시처럼 하단 중앙 `- n -`).
- G3 **분량**: 그림·표 포함 A4 10매를 기준선으로 한다(장당 1,000자 내외). 원문 "최소 10매 … 이내"의 상·하한 충돌은 `official-thesis-requirements.md`의 확인 항목으로 유지하되, **10매 미만은 FAIL**로 둔다.
- G4 **제목 페이지**: 국문 제목과 영문 제목을 모두 둔다(양식 2쪽 "국문 제목 / Put English Title Here").
- G5 **요약**: 국문요약 500자 이내. 바로 아래 `Keyword : ` 한 줄에 **영문 핵심어 5개 이내**(사용자 지시: 영문 핵심어는 영어로).
- G6 **장·절 번호**: 장은 로마자(Ⅰ, Ⅱ, Ⅲ, Ⅳ, Ⅴ), 절은 아라비아 숫자(1, 2, 3). 절 제목은 한글.
- G7 **영문 표기**: 영문 문장은 첫 글자만 대문자, 나머지 소문자(고유명사 제외). 영문 제목·표·그림 라벨·참고문헌 제목에 적용한다.
- G8 **그림**: 본문에서 언급된 쪽에 싣고, 넘어가면 다음 쪽 맨 처음. 제목은 그림 하단, `그림 n. 제목` 형식으로 국문 병기(영문을 함께 쓰면 국문이 반드시 동반). 식별 가능한 해상도(래스터라면 300 dpi 이상, 벡터 우선).
- G9 **표**: 제목은 표 상단, `표 n 제목` 형식으로 국문 병기. 본문 언급 쪽 배치 규칙은 그림과 같다.
- G10 **참고문헌**: 본문 인용 순서대로 번호. 형식은 양식 예시(저자, "제목," 저널/학회명, Vol./No., pp., 월 연도). 영문 표기가 있는 문헌은 영문으로. 본문 인용은 우측 상단 `[n]`.
- G11 **본문 언어**: 본문(요약, Ⅰ–Ⅴ장)은 한글. 영문 고유명사·기술 용어·식별자·수식은 원형 유지. 결정론 검사: 참고문헌·코드 식별자·수식을 제외한 본문 글자 중 한글 비율 ≥ 0.6, 그리고 영문만으로 된 문단이 0개.
- G12 **공개 출력 게이트 확장**: 기존 `public_output_gate` 패턴을 국문 원고, 그림 스펙, 이미지 프롬프트, 그림 내부 라벨(OCR 텍스트)에도 적용한다. 해커톤 기업/도메인명과 공개 엔진명은 그림 안에서도 나오면 안 된다.

## 2. 언어 원칙 — 번역이 아니라 근거 기반 재작성

- 영문 `paper.tex`를 기계 번역하지 않는다. **국문 원고를 정본(canonical source)으로** 두고, 각 문장은 evidence-matrix의 locator와 claim check를 그대로 이어받는다. 주장 승인 상태(admissible / withheld)가 언어 전환 중 바뀌면 안 된다.
- 정본이 둘이 되지 않게 한다. 영문 원고는 (a) 폐기하거나 (b) 국문 정본에서 생성되는 파생물로만 둔다. 어느 쪽인지 6필드 결정 기록으로 남긴다.
- 그림 내부 라벨은 **영문**으로 한다(이미지 모델의 한글 텍스트 렌더링 신뢰도가 낮고, 영문 핵심어 규칙과도 일치). 캡션은 국문 정본이며 필요하면 괄호 영문 병기.
- 문장 단위 "영문 첫 글자만 대문자" 규칙(G7)을 라벨·캡션·참고문헌에 적용한다.

## 3. 툴체인 결정 (첫 사이클에서 닫는다)

한글 본문을 결정론적으로 빌드하려면 다음 중 하나를 골라 6필드 결정 기록과 receipt로 남긴다. 어느 쪽이든 `paper_protocol.json`에 폰트 파일 sha256을 고정하고 clean-clone validation run이 통과해야 한다.

- (a) `paper.tex`를 XeLaTeX + `kotex`/`xeCJK`로 전환하고 자유 라이선스 CJK 폰트(예: Noto Sans/Serif CJK KR, Nanum)를 저장소 또는 고정 경로에 두고 sha256으로 고정. PDF는 여기서, docx는 지금처럼 quarto pandoc으로.
- (b) 국문 Markdown/LaTeX 정본 → pandoc → docx(제출물) → LibreOffice headless → PDF(검증용). `reference.docx`에 A4·더블 스페이싱·한글 서체·`- n -` 쪽 번호를 박는다.

권고는 (b)다. 제출물이 Word이고, 현재 `build_submission.py`·`reference.docx`·`apply_official_format`이 이미 그 경로 위에 있다. 단, PDF 검증(G2, G3, G8/G9 배치, OCR 라벨 검사)은 LibreOffice 변환본에서 수행하고 그 변환기 버전을 receipt에 고정한다.

## 4. 그림·표 최대화 — 최소 집합과 원장

사용자 지시는 "그림과 표를 최대한 활용, 특히 그림"이다. 아래는 **하한**이며, 근거가 있는 그림은 더 넣는다. 각 그림은 `paper/figures/specs/fig-NN.json` 스펙(블록·엣지·라벨·캡션 국문·근거 노드 id·인용 절)에서 나오고, 스펙은 context graph에 `figure` 노드로 등록되어 결정·근거 노드와 연결된다.

최소 그림 집합(모두 IEEE 논문풍 흑백 블록/아키텍처/파이프라인 다이어그램):

1. 전체 시스템 아키텍처 — 루트 에이전트, context graph, 검색, 결정·근거 프로토콜, 샌드박스 실행, 검증기, 원고 합성의 블록 구성과 데이터 흐름 (Ⅲ장 첫 절).
2. 자율 연구 루프 — 가설 → 문헌 검색 → 설계 비교 → 사전등록 → 실행 → 근거 → 주장 승인 → 방향 갱신의 순환 파이프라인 (Ⅲ장).
3. Context graph 스키마 — 노드 유형(가설·결정·실험·결과·주장·문헌·그림)과 엣지 유형, 결과 기반 재검색 경로 (Ⅲ장).
4. 결정 프로토콜과 세 객체 비교 동일성(three-object comparison identity) 신호 흐름 (Ⅲ장).
5. 평가 파이프라인 — 은닉 과제 방출 → 샌드박스 → 결정론 채점층 → 판정기 → 교정 게이트의 신호 처리 다이어그램 (Ⅲ장 평가 프로토콜 절).
6. Study A 2×2 요인 설계 — C00–C11 조건과 예산 매칭, 파일럿 16 에피소드 배치 (Ⅲ장 또는 Ⅳ장).
7. 채점 도구 비교 — span 기반 판정 대 전체 산출물 판정의 흐름과 20% 하위표본 드리프트 검사 (cycle 55–57 결과, Ⅳ장).
8. 근거 사슬·검증 — clean-clone validation, locator gate, 재현 빌드 receipt의 블록도 (Ⅲ장 또는 Ⅳ장).
9. 선행 연구 대비 설계 위치 — 비교 축 위에 본 연구와 직접 유사 연구를 배치한 개념도 (Ⅱ장).

최소 표 집합: 선행 연구 설계 비교(`design-comparison-round8.md` 압축), Study A 조건 정의, 실행된 블록과 지표 요약(cycle 54–57 수치), 위협·한계 표, 비용 원장 요약, 결정 기록 인구조사(Ⅳ장 census 절). 표는 국문 헤더, 수치는 evidence-matrix locator를 각주 또는 캡션에 남긴다.

게이트: Ⅱ·Ⅲ·Ⅳ장 각각 그림 ≥1, Ⅲ장 그림 ≥3, 전체 그림 ≥8, 표 ≥5. 모든 그림·표는 본문에서 `그림 n`/`표 n`으로 최소 1회 참조되고, 참조 없는 그림·표와 스펙 없는 그림은 FAIL. `paper/figures/figure-ledger.json`에 그림별 스펙 sha256, 생성 경로(§5), 결과 파일 sha256, 삽입 절, 캡션을 기록한다.

## 5. gpt-image-2 생성 파이프라인

사용자 지시: "IEEE 논문풍 흑백 시스템 블록 다이어그램 또는 academic technical block diagram, system architecture schematic, signal-processing pipeline diagram, 깨끗한 벡터 다이어그램을 gpt-image2 모델로 생성해서 최대한 활용".

1. **경로 열거(첫 사이클, 필수)**: 세션 환경에서 OpenAI Images API(`POST /v1/images/generations`)에 도달 가능한 경로를 확인한다. 키 값은 절대 출력·기록·커밋하지 않는다. 존재 여부와 변수명만 `paper/figures/image-route-receipt.json`에 남긴다. 모델 id는 `gpt-image-2`를 먼저 시도하고, 거부되면 `/v1/models`에서 `gpt-image` 계열 최신 id를 골라 그 사실을 receipt에 적는다. 1회 저해상도 프로브로 확인한다.
2. **경로가 없으면** Q-0008을 6필드로 올린다: 옵션 (a) 사용자가 OpenAI API 키를 세션 환경에 제공, (b) 사용자가 ChatGPT에서 스펙 프롬프트로 생성해 `paper/figures/incoming/`에 PNG 투입, (c) §5.6 벡터 폴백만으로 진행. 기본값 (c), blocking=false. 프롬프트 파일은 (b)를 위해 미리 만들어 둔다. 루프는 멈추지 않는다.
3. **프롬프트 규격**(스펙에서 생성, 파일로 저장):
   `IEEE-style academic technical block diagram, strictly black and white, clean vector line art, white background, rectangular blocks with thin black outlines, orthogonal arrows with solid heads, sans-serif labels, no color, no shading, no gradients, no 3D, no photos, no icons, no decorative elements, print quality.` 다음에 블록·엣지·라벨을 스펙 순서대로 나열하고 `Labels exactly as written:` 뒤에 라벨 목록을 붙인다. 파이프라인 그림은 가로형(1536×1024), 스키마·아키텍처는 필요 시 정방형(1024×1024). quality는 최고 설정, background는 불투명 흰색, 출력 PNG.
4. **후처리**: PNG → 흑백 이진화 → 벡터화(potrace 또는 vtracer) → SVG/PDF. 원고에는 벡터본을 넣고 PNG 원본은 300 dpi 이상 확인 후 보관. 도구와 버전은 receipt에 고정한다.
5. **가독성 게이트**: 생성물에 OCR을 돌려 스펙 라벨 집합과 대조한다. 라벨 일치율 < 0.9, 오탈자 라벨 존재, 컬러 픽셀 존재, 스펙에 없는 블록 존재 중 하나라도 있으면 FAIL. 같은 스펙으로 최대 3회 재생성한다.
6. **벡터 폴백**: 3회 실패하거나 경로가 없으면 같은 스펙에서 TikZ 또는 Graphviz(dot, 흑백, 동일 스타일)로 렌더링한다. 원장에 `route: gpt-image-2 | fallback-tikz | fallback-graphviz`를 남겨 어떤 그림이 어떤 경로로 만들어졌는지 논문 부록 표로도 보이게 한다.
7. **비용**: 이미지 API 사용은 `paper/supervisor/cost-ledger.md`에 USD 절을 신설해 그림별 호출 수·단가·누적을 적는다. 예상 누적 > $10이면 Q를 올리고 기본값은 폴백 진행이다.
8. **금지어**: 프롬프트·라벨·스펙에 G12 금지 토큰이 들어가면 생성 전 단계에서 FAIL.

## 6. 루프 통합과 순서

- 이 지시는 instruction-0005 §2·0007 §2의 상시 루프 안에 **"원고 양식 워크스트림"**을 추가한다. 양식 게이트(§1, §4)가 전부 PASS할 때까지 매 사이클은 이 워크스트림을 먼저 진전시키고, 남는 사이클 예산으로 연구 증분을 이어간다. 연구 루프는 멈추지 않는다.
- 첫 사이클: §3 툴체인 결정 + §5.1 경로 프로브 + 그림 스펙 9건 초안 + `figure-ledger.json` + 양식 게이트 코드 착수. status.md의 `next_first_action`을 이 첫 사이클로 바꾼다.
- 이후 사이클: 장 단위로 국문 재작성(Ⅰ→Ⅱ→Ⅲ→Ⅳ→Ⅴ→요약·제목·참고문헌)하고, 각 장을 닫을 때 그 장의 그림·표를 삽입해 validation run을 통과시킨다. 장 하나가 열린 채로 다음 장을 열지 않는다.
- 각 커밋 단위: 정본 원고 + 스펙/그림 + 원장 + receipt + validation 결과가 함께 간다. 커밋 메시지에 이모지 금지, 변경 파일만 add.
- 마감 2026-10-31. 양식 게이트 전부 PASS 목표 시점을 status.md에 날짜로 적고, 지나면 사유를 6필드로 남긴다.

## 7. 열린 Q 처리

- Q-0006(교정 라벨 25건): 사용자에게 전달했다. 답변 전까지 기본값 (b) 유지. 라벨 양식과 프로토콜 경로를 status.md 상단 한 줄로 유지해 사용자가 바로 찾게 한다.
- Q-0007(116 에피소드 $18.28): 사용자에게 전달했다. 답변 전까지 기본값 (b) 유지. 승인되면 사전등록 그대로 실행하고 cost-ledger USD 절에 기록한다.

## 8. 사용자 지침 원문 (모든 작업 지시에 포함)

> ai 에이전트가 스스로 연구를 설계하고, 연구 가설이나 조건, 방법 등 모든 요소를 직접 설정해야 하고, 근데 이걸 또 그냥 정하는게 아니야 깊이 있는 추론과 인사이트를 통해 선택을 해야하고, 그 선택에 대해 근거까지 있어야 해. 비슷한 실험찾아보고, method 찾아보고, 쓸만한 레퍼런스 찾아보고, 자료정리도 해야해 또한 이모든 걸 다른 ai 에이전트들도 인지하고 작업할수 있게 context graph로 스스로 작성하서 그래프 맵을 구축해야 해. 관련 선행 연구를 찾아서 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리 구축하고 실험을 진행하는거야. 비슷한 연구들이 어떤식으로 실험을 설계했는지 비교 경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행하는거야.

> (2026-09-03 04:55 KST) 졸업논문 양식을 지키면서 작성해야해 본문 내용은 영어가 아니라 한글로 작성해야해 영문 핵심어는 영어로 작성해야하고 그리고 그림과 표를 최대한 활용해야해 특히 그림을 활용해야해 IEEE 논문풍 흑백 시스템 블록 다이어그램 또는 academic technical block diagram, system architecture schematic, signal-processing pipeline diagram 깨끗한 벡터 다이어그램을 gpt-image2 모델로 생성해서 최대한 활용해서 추가해야해

그림의 내용(무엇을 블록으로 나눌지, 어떤 흐름을 보일지)도 위 원칙대로 정한다: 유사 연구의 아키텍처 그림이 무엇을 어떻게 보였는지 orx로 확인하고, 본 연구 그림이 무엇을 다르게 보여야 하는지 근거와 함께 스펙에 적는다.

## 9. 불변 조건

- 세션 모델은 사용자가 지정한 `anthropic/claude-opus-5` 유지. 바꾸지 않는다.
- 답변된 orx ancestor는 편집하지 않는다. `paper/supervisor/` 파일은 supervisor 소유이며 세션은 status.md·questions.md·cost-ledger.md만 갱신한다.
- 논문·그림·프롬프트 어디에도 해커톤 기업/도메인명과 공개 엔진명을 쓰지 않는다("자율 연구 엔진"으로 지칭).
- DeepVoice 근거는 이 논문에 쓰지 않는다.
- GPU는 instruction-0006 §2 규칙(Colab CLI, 사전등록, cost-ledger, 승인 게이트) 그대로.
- 키·토큰은 출력·기록·커밋하지 않는다.

## 10. 보고

status.md에 (1) 툴체인 결정 id, (2) 이미지 경로 receipt 요약(모델 id, 프로브 성공 여부, 키 존재 여부만), (3) 그림 원장 요약(번호·경로·게이트 결과), (4) 양식 게이트 G1–G12 PASS/FAIL 표, (5) 장별 국문 재작성 진행률을 매 사이클 갱신한다. 사용자 결정이 필요한 것은 Q id로만 올리고 기본값으로 계속 진행한다.
