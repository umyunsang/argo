# Supervisor instruction #0004 (paper) — 웹 GPT 인계 취소, argo-paper-root 세션 재개

- 발신: Claude Code supervisor
- 시각: 2026-09-02 21:35 KST
- 대상: argo-paper-root
- 근거: 사용자 결정(21:30 KST "웹 gpt로 진행 못하겠다, argo-paper-root 세션에서 진행"), `prime-agent list`(argo-paper-root working), `git status`(paper/evidence-matrix.csv 0바이트), status.md(last_updated 15:49, validation run 3fe2958b in flight), handoff-2026-09-02.md

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
