# Supervisor instruction #0003 (paper) — 웹 GPT 1차 보고 응답: 자율 연구 위임 범위, 정본 접근 복구, round 8 규칙

- 발신: Claude Code supervisor
- 시각: 2026-09-02 19:35 KST (v3: §0 연구 위임 범위 추가, §1-2·§3 개정; v2: 토큰 기반 §2·§4)
- 대상: 웹 GPT paper 세션
- 근거: 사용자 원 지시(2026-09-02), 웹 GPT 1차 보고(이관 저장소 `argo-autoresearch-transfer`, 커밋 59be628), `gh repo view umyunsang/argo`(public), 정본 `paper/research/research-design.md`, `paper/research/autonomous-research-decision-ledger.json`, `paper/supervisor/status.md`, 정본 코퍼스 grep

## 0. 연구 위임의 범위 (사용자 원 지시, 이 지시 전체에 우선)

사용자 원 지시(2026-09-02):

> Exa 플러그인을 이용해 alphaXiv/OpenResearch를 설치하고 사용법을 확인한다. 자율연구 엔진은 openresearch(orx)로 진행한다. 깊이 추론해서 스스로 연구를 설계하고, 연구 가설·조건·방법 등 모든 요소를 직접 설정한다. 그냥 정하는 것이 아니라 깊이 있는 추론과 인사이트로 선택하고, 그 선택에 근거를 남긴다. 비슷한 실험을 찾아보고, method를 찾아보고, 쓸만한 레퍼런스를 찾아보고, 자료를 정리한다. 이 모든 것을 다른 AI 에이전트들도 인지하고 작업할 수 있게 context graph로 스스로 작성해 그래프 맵을 구축한다. 관련 선행 연구를 찾아 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리·구축하고 실험을 진행한다. 비슷한 연구들이 어떤 식으로 실험을 설계했는지 비교·경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행한다.

적용 원칙:

1. 이 위임은 계속 유효하다. §1의 "이관본 설계 미채택"은 병렬 저장소의 파일과 재유도 설계를 정본에 그대로 들여오지 않는다는 뜻이지, 설계 권한을 회수하는 것이 아니다.
2. 정본 `paper/research/research-design.md`(Study A: RQ1~RQ5, H-A~H-E, C00~C11)와 `paper/research/minimum-executable-experiment.md`(16-episode 파일럿)는 이전 세션이 같은 위임 아래 만든 현재 상태다. 너는 이를 상속받고, 선행 연구 비교에서 나온 근거가 있으면 가설·조건·측정·표본·분석 어느 요소든 고칠 권한과 의무가 있다. 근거 없는 변경과 라벨만 바꾸는 변경은 금지다.
3. 모든 설계 선택은 "대안 → 검토한 선행 연구(전문 읽기 locator) → 근거 → 결정 → 기대 효과/위험 → 반증 조건" 여섯 항목으로 `paper/research/autonomous-research-decision-ledger.json`에 결정 기록(`RD-2026-09-0N-NN`)으로 남기고, `research-design.md`의 Choice 표에 같은 행을 추가하며, `paper/context-graph.json`에 결정 노드와 출처·가설·조건 엣지를 연결한다. 다른 에이전트가 그래프만 보고 설계 근거를 재구성할 수 있어야 한다.
4. 설계는 반드시 실행으로 이어진다. 실행 가능한 단위(§3-7)를 이번 라운드 안에서 돌리고, 실행 불가능한 단위는 어떤 자원(모델 API, 격리 샌드박스, 독립 평가자)이 없어서 불가능한지와 supervisor가 로컬에서 그대로 돌릴 수 있는 명령을 남긴다.

## 1. 진단

1. 정본은 공개 저장소이고 인수인계 브랜치는 원격에 있다. 저장소 `https://github.com/umyunsang/argo`, 브랜치 `orx/integrate-harness-evaluation-counterevidence-and`. 컨테이너 DNS 차단이 원인이며, GitHub 커넥터와 브라우징은 동작했으므로 §2 경로로 읽고 쓸 수 있다.
2. 이관본의 Study A 2×2(구조화 상태 × 동적 검색)와 16-episode 파일럿은 정본 `research-design.md`와 `minimum-executable-experiment.md`에 이미 있다. 이관본은 재설계이지 증분이 아니다. 정본 설계가 현재 상태이며, 이관본의 H1~H4 라벨, 복합점수 가중치(30/20/20/15/15), 검색 허용 조건(불확실성 0.60 등)은 재유도된 것이므로 그대로 채택하지 않는다. 그중 정본보다 낫다고 판단하는 항목이 있으면 §0-3 결정 기록 형식으로 근거를 들어 정본 설계를 고친다. 사용자 결정이 필요한 것(마감, 예산, 외부 자원, 제출)만 Q로 올린다.
3. 전문 검토 7편 중 4편이 정본 코퍼스에 없다: `2403.14403`(Adaptive-RAG), `2310.11511`(Self-RAG), `2405.14831`(HippoRAG), `2602.15112`(ResearchGym). 3편(`2410.05080`, `2504.01848`, `2502.14499`)은 이미 있다. 신규 4편은 정본 형식으로 병합한다. 이관본에서 재사용할 것은 이 4편의 전문 읽기 기록과 locator뿐이다.
4. 컨테이너 안의 orx 설치, 로컬 프로젝트, 조건 브랜치 4개, 스텁 러너의 `NOT_ESTIMATED` 실행 영수증은 컨테이너 산출물이다. 정본 orx 프로젝트는 사용자 머신에 있다. Git 이력(bundle)은 가져오지 않는다. 파일 내용만 병합한다.
5. 정본 status.md의 E5 launch 블로커 세 가지(hidden-task sandbox, independent scoring, fixed Study A runner)는 이관본이 해소하지 않았다. §3-7이 이 블로커를 직접 다룬다.

## 2. 정본 접근과 반영 (사용자 개입 없음)

1. 사용자가 제공한 GitHub 토큰으로 정본을 직접 읽고 쓴다. 저장소 `umyunsang/argo`, 기준 브랜치 `orx/integrate-harness-evaluation-counterevidence-and`. 기준 커밋은 작업 시작 시 API(`GET /repos/umyunsang/argo/branches/<기준 브랜치>`)로 확인해 보고에 적는다.
2. 컨테이너에서 git 네트워크가 되면 `git clone --depth 1 --branch <기준 브랜치> https://x-access-token:<TOKEN>@github.com/umyunsang/argo.git`로 받고, clone 직후 `git remote set-url origin https://github.com/umyunsang/argo.git`로 URL에서 토큰을 지운 뒤 push 때만 토큰을 쓴다.
3. git 네트워크가 안 되면 스냅샷 브랜치 `paper-snapshot-2026-09-02`의 zip(`https://github.com/umyunsang/argo/archive/refs/heads/paper-snapshot-2026-09-02.zip`)이나 GitHub 커넥터로 트리를 받아 작업하고, 반영은 GitHub REST Git Data API로 한다: 기준 커밋의 tree sha를 `base_tree`로 하여 변경 파일만 blob을 만들고 `POST /repos/umyunsang/argo/git/trees`, `POST /repos/umyunsang/argo/git/commits`(parent = 기준 커밋), `POST /repos/umyunsang/argo/git/refs`로 새 브랜치를 만든다.
4. 반영 대상은 새 브랜치 `paper/round8-web-gpt`뿐이다. 기준 브랜치와 `main`에는 쓰지 않는다. 완료 후 기준 브랜치를 base로 PR을 연다(제목 접두 `docs(paper):`). 병합은 supervisor가 로컬 검증 후 한다.
5. 토큰은 어떤 파일·커밋·로그·보고에도 적지 않는다. 노출을 발견하면 즉시 보고한다.
6. 병렬 저장소 금지. 모든 변경은 정본 경로에 대한 커밋이다. 커밋은 변경 파일만 명시하고, 이모지 금지, 메시지 접두 `docs(paper):`.

## 3. 작업 순서 (round 8)

1. 읽기: `paper/supervisor/handoff-2026-09-02.md`, `status.md`, `instruction-0002.md`~`0002e`, `questions.md`, `.orx/paper_protocol.json`, `docs/argo/literature-review-protocol.md`, `paper/research/research-design.md`, `minimum-executable-experiment.md`, `autonomous-research-decision-ledger.json`, `capability-map.md`, `literature-round7-retrieval-record.json`. 첫 보고에 읽은 파일 목록과 각 파일의 핵심 규칙 한 줄을 적는다.
2. 엔진 설치와 사용법 확인: Exa 플러그인으로 `alphaXiv/OpenResearch` 저장소, README, 최신 릴리스, 문서 페이지를 찾는다. 컨테이너에 최신 orx 릴리스를 설치한다(이미 0.1.118을 GitHub 릴리스 자산으로 설치했다면 재사용하고 `orx version --check`로 확인). `orx --help`, `orx skill`(에이전트용 CLI 사용법), `orx discover keyword|embedding|openalex --help`, `orx paper --help`, `orx create-experiment --help`, `orx exp --help`, `orx runs --help`, `orx logs --help` 출력을 확인하고 `paper/research/orx-usage.md`에 명령·용도·이번 라운드 사용 예시·확인한 버전을 정리한다. 이후 모든 문헌 검색은 `orx discover`, 전문 취득은 `orx paper`로 하고, 명령·결과 id·선택 결과를 round 7 형식(`loops[].initial_commands`, `result_ids`, `selected_full_reads`, `selection_rule`)으로 `paper/research/literature-round8-retrieval-record.json`에 남긴다.
3. 설계 경쟁 문헌 루프(핵심): 목표는 "비슷한 연구가 실험을 어떻게 설계했는가"다. 최소 3개 objective로 `orx discover` 루프를 돈다. (a) LLM 연구 에이전트의 통제 실험 설계(조건 정의, 통제, 무작위화 단위, 반복 수). (b) 에이전트 시스템의 결과 측정(rubric, 독립 채점, judge 신뢰도, 은닉 과제 격리). (c) 검색·구조화 상태가 에이전트 성능에 미치는 효과의 인과 추정(2×2/요인 설계, 표본 크기, 통계 검정). 각 objective에서 embedding·keyword·openalex 세 원시 명령을 모두 쓰고, 상위 후보를 전문 읽기로 올려 정본 코퍼스에 없는 것만 등록한다. §1-3의 4편은 이 루프의 첫 등록분이며, 신규 전문 읽기는 그 4편을 포함해 최소 5편 이상이다. 등록 형식은 round 7 파일을 복제한다: source receipts, arXiv metadata xml과 receipt, `claim-locators.json` 추가, `evidence-matrix.csv`/`.md` 행 추가, `context-graph.json`/`.md` 노드·엣지 추가, `paper_protocol.json`의 `structured_expectations` 갱신(먼저 기대치를 올려 실패를 `paper/sources/literature-round8-validator-failing-first.json`에 기록한 뒤 충족). evidence level은 `docs/argo/literature-review-protocol.md`를 따른다.
4. 설계 비교표: `paper/research/design-comparison-round8.md`를 만든다. 행은 전문 읽기한 선행 실험(정본 기존 FULL 읽기 포함 최소 8편), 열은 연구 질문, 조건/요인, 통제 변수, 무작위화 단위, 과제 출처와 은닉 여부, 측정 지표와 채점 주체, 표본 크기와 반복, 통계 분석, 보고된 효과 크기, 한계다. 마지막 절에 Study A와의 항목별 비교와 "우리가 더 잘하는 것 / 못하는 것 / 바꿔야 하는 것"을 적는다.
5. 설계 결정과 갱신: 비교표에서 나온 각 변경 후보에 대해 §0-3 여섯 항목 결정 기록을 만든다. 채택하면 `research-design.md`의 해당 절(가설, 조건, 측정, 표본, 분석, 사전등록 항목)과 `minimum-executable-experiment.md`를 고치고, 기각하면 기각 근거를 no-change 기록으로 남긴다. 이관본의 복합점수 가중치·불확실성 임계값 같은 재유도 항목도 여기서 근거를 들어 판정한다. 변경 없이 마치는 것은 허용되지만 "검토했고 바꿀 이유가 없다"는 기록이 있어야 한다.
6. 지식 영역 반영: area 5(RAG engine)에 Adaptive-RAG·Self-RAG·HippoRAG, area 8(autonomous research engine)에 ResearchGym을 배정하고, 새 전문 읽기는 해당 영역에 배정한다. `capability-map.md`와 `evidence-matrix.md` 영역 표를 갱신한다.
7. 실험 실행: `minimum-executable-experiment.md`의 16-episode 파일럿 중 이번 라운드에서 실행 가능한 부분을 orx로 돌린다. 순서: (a) 4개 과제 패킷과 rubric을 만들되 목표 논문과 rubric은 에이전트가 볼 수 없는 별도 디렉터리에 둔다. (b) `orx create-experiment`로 C00/C01/C10/C11 4 노드를 만들고 처리 차이는 커밋된 설정 파일에만 둔다. (c) 고정 러너 1개 명령으로 실행한다. (d) 결과는 `paper/experiments/round8-pilot/`에 run id·명령·설정 sha·산출물·채점 로그를 두고 status는 `EXECUTED`/`PARTIAL`/`NOT_EXECUTED`로만 표기한다. 모델 API나 격리 샌드박스가 없어 못 돌리면 그 사실과 필요 자원, supervisor가 로컬 orx 프로젝트에서 그대로 돌릴 수 있는 명령 목록을 같은 디렉터리의 `RUNBOOK.md`로 남긴다. 스텁 러너의 `NOT_ESTIMATED` 실행은 실행으로 세지 않는다.
8. `paper/paper.tex`: Related Works 영역 5·8 인용을 추가하고, Method 절에는 결정 기록 id를 인용한 설계 근거 문장을 추가할 수 있다. 실행되지 않은 결과는 결과로 쓰지 않는다. `forbidden_claim_regexes`를 지킨다.
9. `status.md`를 갱신한다(라운드 요약, 결정 기록 id, 실행 상태, 다음 행동). 사용자 결정이 필요한 항목은 `questions.md`에 Q-0003부터 여섯 필드 형식으로 올린다.

## 4. 검증과 납품

1. 작업 트리 안에서 `python3 .orx/paper_validate.py`를 실행해 통과시킨다. 컨테이너에 고정 toolchain(tectonic, pdftotext)이 없어 PDF 게이트가 실행되지 않으면 그 항목만 사유와 함께 보고한다. 나머지 구조 검증은 통과해야 한다.
2. 납품은 브랜치 `paper/round8-web-gpt`의 커밋과 PR이다. 최종 보고에 커밋 sha, 변경 파일 목록, 검증 로그 요약, 신규 출처의 source id와 locator 수, 결정 기록 id 목록과 설계 변경 요약, 실험 실행 상태(`EXECUTED`/`PARTIAL`/`NOT_EXECUTED`와 사유), 열린 Q id를 적는다.
3. 푸시와 API 반영이 모두 불가능할 때만 `argo-paper-round8-delivery.tar.gz` 하나(변경 파일, `CHANGED_FILES.txt`, 기준 커밋 대비 `round8.diff`, `COMMIT_MESSAGE.txt`, `validate.log`)로 납품한다.

## 5. 불변 조건

- 답변된 orx ancestor는 편집하지 않는다.
- 논문 본문·소스·그래프 어디에도 공개 엔진 이름, 해커톤 회사·도메인 이름을 쓰지 않는다(`forbidden_regexes`, `forbidden_body_regexes`).
- 실행하지 않은 결과를 결과로 쓰지 않는다. 컨테이너 스텁 실행은 증거가 아니다.
- `FULL_PAPER_READ`만 설계·방법 근거로 쓴다. 검증되지 않은 arXiv id나 DOI는 적지 않는다.
- 설계 변경은 결정 기록 없이 하지 않는다. 라벨·가중치·임계값만 바꾸는 변경은 금지다.
- 사용자 결정이 필요한 것은 `questions.md`의 Q로만 올리고 기본값을 적는다.
