# Supervisor instruction #0003 (paper) — 웹 GPT 1차 보고 응답: 정본 접근 복구와 이관본 병합 규칙

- 발신: Claude Code supervisor
- 시각: 2026-09-02 19:20 KST (토큰 제공에 따라 §2·§4 개정)
- 대상: 웹 GPT paper 세션
- 근거: 웹 GPT 1차 보고(이관 저장소 `argo-autoresearch-transfer`, 커밋 59be628), `gh repo view umyunsang/argo`(public), `git ls-remote origin`(브랜치 존재, 96883d0bb), 정본 `paper/research/research-design.md`, `paper/supervisor/status.md`, 정본 코퍼스 grep

## 1. 진단

1. 정본은 공개 저장소이고 인수인계 브랜치는 원격에 있다. 저장소 `https://github.com/umyunsang/argo`, 브랜치 `orx/integrate-harness-evaluation-counterevidence-and`, 기준 커밋 `96883d0bb`. 컨테이너 DNS 차단이 원인이며, GitHub 커넥터와 브라우징은 동작했으므로 아래 §2 경로로 읽을 수 있다.
2. 이관본의 Study A 2×2(구조화 상태 × 동적 검색)와 16-episode 파일럿은 정본 `paper/research/research-design.md`(RQ1~RQ5, H-A~H-E, C00~C11)와 `paper/research/minimum-executable-experiment.md`에 이미 있다. 이관본은 재설계이지 증분이 아니다. 정본 설계가 우선하며 이관본의 H1~H4 라벨, 복합점수 가중치(30/20/20/15/15), 검색 허용 조건(불확실성 0.60 등)은 채택하지 않는다. 정본과 다른 항목은 `questions.md`의 Q 후보로만 제안한다.
3. 전문 검토 7편 중 4편이 정본 코퍼스에 없다: `2403.14403`(Adaptive-RAG), `2310.11511`(Self-RAG), `2405.14831`(HippoRAG), `2602.15112`(ResearchGym). 3편(`2410.05080`, `2504.01848`, `2502.14499`)은 이미 있다. 신규 4편만 정본 형식으로 병합한다. 이관본에서 재사용할 것은 이 4편의 전문 읽기 기록과 locator뿐이다.
4. 컨테이너 안의 orx 설치, 로컬 프로젝트, 조건 브랜치 4개, 스텁 러너의 `NOT_ESTIMATED` 실행 영수증은 컨테이너 산출물이다. 정본 orx 프로젝트는 사용자 머신에 있다. Git 이력(bundle)은 가져오지 않는다. 파일 내용만 병합한다.
5. 정본 status.md의 E5 launch 블로커 세 가지(hidden-task sandbox, independent scoring, fixed Study A runner)는 이관본이 해소하지 않았다.

## 2. 정본 접근과 반영 (사용자 개입 없음)

1. 사용자가 제공한 GitHub 토큰으로 정본을 직접 읽고 쓴다. 저장소 `umyunsang/argo`, 기준 브랜치 `orx/integrate-harness-evaluation-counterevidence-and`. 기준 커밋은 작업 시작 시 API(`GET /repos/umyunsang/argo/branches/<기준 브랜치>`)로 확인해 보고에 적는다. 2026-09-02 19:20 KST 기준 HEAD는 `d90d7fd1e`다.
2. 컨테이너에서 git 네트워크가 되면 `git clone --depth 1 --branch <기준 브랜치> https://x-access-token:<TOKEN>@github.com/umyunsang/argo.git`로 받고, clone 직후 `git remote set-url origin https://github.com/umyunsang/argo.git`로 URL에서 토큰을 지운 뒤 push 때만 토큰을 쓴다.
3. git 네트워크가 안 되면 스냅샷 브랜치 `paper-snapshot-2026-09-02`의 zip(`https://github.com/umyunsang/argo/archive/refs/heads/paper-snapshot-2026-09-02.zip`)이나 GitHub 커넥터로 트리를 받아 작업하고, 반영은 GitHub REST Git Data API로 한다: 기준 커밋의 tree sha를 `base_tree`로 하여 변경 파일만 blob을 만들고 `POST /repos/umyunsang/argo/git/trees`, `POST /repos/umyunsang/argo/git/commits`(parent = 기준 커밋), `POST /repos/umyunsang/argo/git/refs`로 새 브랜치를 만든다.
4. 반영 대상은 새 브랜치 `paper/round8-web-gpt`뿐이다. 기준 브랜치와 `main`에는 쓰지 않는다. 완료 후 기준 브랜치를 base로 PR을 연다(제목 접두 `docs(paper):`). 병합은 supervisor가 로컬 검증 후 한다.
5. 토큰은 어떤 파일·커밋·로그·보고에도 적지 않는다. 노출을 발견하면 즉시 보고한다.
6. 병렬 저장소 금지. 모든 변경은 정본 경로에 대한 커밋이다. 커밋은 변경 파일만 명시하고, 이모지 금지, 메시지 접두 `docs(paper):`.

## 3. 작업 순서 (round 8)

1. `paper/supervisor/handoff-2026-09-02.md`, `status.md`, `instruction-0002.md`~`0002e.md`, `questions.md`, `.orx/paper_protocol.json`, `docs/argo/literature-review-protocol.md`를 읽고, 읽은 파일 목록과 파일별 핵심 규칙 한 줄을 먼저 보고한다.
2. 신규 4편을 round 8로 추가한다. round 7 파일 형식을 그대로 복제한다: `paper/sources/literature-round7-source-receipts.json`, `paper/sources/arxiv-metadata-literature-round7*.xml`과 receipt, `paper/sources/claim-locators.json`의 locator 항목, `paper/evidence-matrix.csv`와 `.md` 행, `paper/context-graph.json`·`.md`의 노드·간선, `paper/research/literature-round7-retrieval-record.json`, `paper/sources/literature-round7-validator-failing-first.json`, `.orx/paper_protocol.json`의 `round7_*` 기대값. 이름의 `round7`을 `round8`로 바꾼 파일을 만들고, 공유 파일(claim-locators, evidence-matrix, context-graph, protocol)에는 항목을 추가한다. 카운트·sha256 기대값은 failing-first 순서로 갱신한다(기대값 먼저 기록해 실패를 남기고, 그다음 충족).
3. 영역 배정: 영역 5(RAG engine)에 Adaptive-RAG·Self-RAG·HippoRAG, 영역 8(자율 연구 엔진 평가·필요성)에 ResearchGym. `paper/research/capability-map.md`와 `paper/evidence-matrix.md` 영역 표를 갱신한다.
4. `paper/research/research-design.md`는 RQ2·H-B 근거 문장과 인용만 보강한다. 조건·가설·지표·표본 수는 바꾸지 않는다. 바꿔야 한다고 판단하면 Q로 올린다.
5. `paper.tex`는 Related Works 영역 5·8 문단의 인용 추가만 허용한다. 미실행 결과 서술 금지, `forbidden_claim_regexes` 위반 금지.
6. `status.md`를 갱신한다(last_updated, 영역 5·8 FULL 수, 다음 행동). 사용자 결정이 필요한 사항은 `questions.md`에 Q-0003부터 6필드 형식으로 올린다.

## 4. 검증과 납품

1. 작업 트리 안에서 `python3 .orx/paper_validate.py`를 실행해 통과시킨다. 컨테이너에 고정 toolchain(tectonic, pdftotext)이 없어 PDF 게이트가 실행되지 않으면 그 항목만 사유와 함께 보고한다. 나머지 구조 검증은 통과해야 한다.
2. 납품은 브랜치 `paper/round8-web-gpt`의 커밋과 PR이다. 최종 보고에 커밋 sha, 변경 파일 목록, 검증 로그 요약, 신규 출처 4편의 source id와 locator 수, 열린 Q id를 적는다.
3. 푸시와 API 반영이 모두 불가능할 때만 `argo-paper-round8-delivery.tar.gz` 하나(변경 파일, `CHANGED_FILES.txt`, 기준 커밋 대비 `round8.diff`, `COMMIT_MESSAGE.txt`, `validate.log`)로 납품한다.

## 5. 불변 조건

- 답변된 orx ancestor 편집 금지. 공개 엔진·회사·도메인 명칭 금지(`public_output_gate`, `forbidden_regexes`). 미실행 결과를 결과처럼 서술 금지.
- `FULL_PAPER_READ`만 설계·방법 근거로 인정. arXiv id 또는 DOI 미확인 인용 금지.
- 사용자 결정이 필요한 사항은 Q로만 올리고, 미답변 시 기본값으로 진행한다.
