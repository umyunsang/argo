# Supervisor instruction #0004 (paper) — 웹 GPT 인계 취소, argo-paper-root 세션 재개

- 발신: Claude Code supervisor
- 시각: 2026-09-02 21:35 KST
- 대상: argo-paper-root
- 근거: 사용자 결정(21:30 KST "웹 gpt로 진행 못하겠다, argo-paper-root 세션에서 진행"), `prime-agent list`(argo-paper-root working), `git status`(paper/evidence-matrix.csv 0바이트), status.md(last_updated 15:49, validation run 3fe2958b in flight), handoff-2026-09-02.md

## 0. 연구 위임의 범위 (사용자 원 지시, 이 지시 전체에 우선)

사용자 원 지시(2026-09-02, 원문):

> exa플러그인을 이용해 alphaXiv/OpenResearch 설치하고 사용법 확인해. 자율연구 엔진은 openresearch로 진행할거야. 너가 깊이 추론해서 스스로 연구를 설계하고, 연구 가설이나 조건, 방법 등 모든 요소를 직접 설정해야 하고, 근데 이걸 또 그냥 정하는게 아니야 깊이 있는 추론과 인사이트를 통해 선택을 해야하고, 그 선택에 대해 근거까지 있어야 해. 비슷한 실험 찾아보고, method 찾아보고, 쓸만한 레퍼런스 찾아보고, 자료정리도 해야해. 또한 이 모든 걸 다른 ai 에이전트들도 인지하고 작업할 수 있게 context graph로 스스로 작성해서 그래프 맵을 구축해야 해. 관련 선행 연구를 찾아서 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리 구축하고 실험을 진행하는거야. 비슷한 연구들이 어떤 식으로 실험을 설계했는지 비교 경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행하는거야.

적용: 이 세션에는 exa 플러그인이 없으므로 "설치와 사용법 확인"은 로컬 `orx`(openresearch-cli)로 한다. `orx version --check`, `orx skill`, `orx discover keyword|embedding|openalex --help`, `orx paper --help`, `orx create-experiment --help`, `orx exp --help` 출력을 확인해 `paper/research/orx-usage.md`에 정리하고, 이후 문헌 검색은 `orx discover`, 전문 취득은 `orx paper`, 실험은 `orx create-experiment`/`orx exp`로만 한다. 나머지 항목(스스로 설계, 근거 있는 선택, 비슷한 실험·method·레퍼런스 탐색과 자료 정리, 다른 에이전트가 읽을 수 있는 context graph, 선행 연구 기반 온전한 실험 설계안, 실험 실행, 비슷한 연구와의 설계 비교·경쟁)은 instruction-0003 §0 적용 원칙 1~4와 §3-2~§3-7이 구체 절차다.

## 1. 상황

1. 웹 GPT 인계는 취소됐다. 웹 GPT가 만든 이관 저장소, 조건 브랜치 4개, 스텁 실행, locator는 정본에 들어오지 않았고 앞으로도 들여오지 않는다. 이 세션이 정본 브랜치 `orx/integrate-harness-evaluation-counterevidence-and`에서 계속 진행한다.
2. 15:49 이후 supervisor 커밋 6개(96883d0bb~1726cc3e9)는 `paper/supervisor/` 파일만 바꿨다. 논문·소스·그래프·프로토콜은 `b2070ed09` 상태 그대로다.

## 2. 재개 절차 (다른 작업보다 먼저, 순서대로)

1. HEAD가 `1726cc3e9`이고 origin과 같은지 확인한다.
2. 작업 트리에서 `paper/evidence-matrix.csv`가 비어 있다(index `e69de29bb`, HEAD 대비 154행 삭제). 네가 지금 진행 중인 쓰기라면 즉시 완성하고 검증한다. 아니면 `git restore --source=HEAD -- paper/evidence-matrix.csv`로 그 파일 하나만 복원하고, 복원 사실과 원인 추정을 status.md에 적는다. 다른 파일에는 손대지 않는다.
3. 중단 지점은 status.md의 `current_phase`, 즉 체크포인트 `b2070ed09`에서 띄운 immutable validation run `3fe2958b-44b6-4760-89fb-f711440c2ae0`이다. `orx runs`/`orx logs`로 완료·실패·유실을 판정해 status.md에 기록한다. 유실이면 같은 명령으로 다시 띄운다. 실행 증거는 efficacy와 분리한다.
4. `handoff-2026-09-02.md` 첫 줄 아래에 "2026-09-02 21:30 KST 웹 GPT 인계 취소, argo-paper-root 재개" 한 줄을 추가한다.

## 3. 본 작업

1. `paper/supervisor/instruction-0003.md`(v3)를 읽고 §0 연구 위임 범위, §3 작업 순서(round 8), §5 불변 조건을 그대로 수행한다. §2(토큰·클론·새 브랜치)와 §4-3(tar 납품)은 웹 GPT용이므로 무시하고, 평소처럼 이 워크트리에서 정본 브랜치에 직접 커밋·푸시한다.
2. §1-3의 4편(`2403.14403` Adaptive-RAG, `2310.11511` Self-RAG, `2405.14831` HippoRAG, `2602.15112` ResearchGym)은 웹 GPT의 locator를 받지 못했으므로 `orx discover`/`orx paper`로 직접 취득해 전문 읽기하고 round 8 형식으로 등록한다.
3. instruction-0002~0002e의 규칙과 status.md의 "Next concrete actions" 1~5는 유효하다. 이번 라운드의 우선순위는 instruction-0003 §3-3(설계 경쟁 문헌 루프), §3-4(설계 비교표), §3-5(결정 기록과 설계 갱신), §3-7(실행 가능한 파일럿 실행)이다.

## 4. 보고

- status.md를 라운드 단위로 갱신하고, 각 항목에 orx run id와 커밋 sha를 남긴다.
- 사용자 결정이 필요한 항목은 questions.md에 Q-0003부터 여섯 필드 형식으로 올리고 기본값을 적는다.
- 불변 조건: 답변된 orx ancestor 편집 금지, 공개 엔진·회사·도메인 이름 금지, 실행하지 않은 결과 금지, 결정 기록 없는 설계 변경 금지, 커밋 위생(변경 파일만, 이모지 금지, force push 금지).
