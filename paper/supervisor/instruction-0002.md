# Supervisor instruction #0002 (paper) — 논문 방향 재정립

- 발신: Claude Code supervisor (사용자 2026-09-02 14:03 KST 지시 전달)
- 대상: argo-paper-root
- 우선순위: 이 지시는 #0001을 대체하지 않고 논문의 주제·범위·인용 규칙을 확정한다. 충돌 시 이 문서가 우선한다. 원문은 부록에 있다.

## 1. 연구 목표 (논문 주제)

LLM이 핸들링 가능한 자율 연구를 위한 **harnessed LLM agent system의 필요성과 연구개발**. 논문은 세 질문에 답한다.

1. 왜 harness가 필요한가 — LLM 단독 자율 연구의 한계를 문헌으로 논증 (필요성).
2. 어떤 구성요소로 설계하는가 — 아래 6개 문헌 영역에서 도출한 설계 (제안 방법).
3. 어떻게 검증하는가 — 실행된 실험만 (실험 결과).

## 2. 포함 금지 (hard exclusion)

- 내부 개발 사항과 내부 설계: prime-agent 포크·마이그레이션 상태, Prime-to-ARGO lineage, oracle contracts, orx 내부 프로토콜과 파일 구조, supervisor 지시·질문 파일, instance.json·progress.md 같은 운영 산출물, harness bottleneck ledger 내용, 특정 인스턴스의 회사명·도메인.
- 구현 기반 언급은 다음 수준까지만 허용: "공개된 에이전트 파운데이션[인용]과 연구 엔진[인용] 위에 참조 구현했다"는 한 문장과 실험 재현에 필요한 최소 설정.
- thesis-contribution-ledger.md의 "Migration details belong in the implementation/provenance section" 서술은 폐기한다. paper.tex와 ledger에서 §2 해당 내용을 먼저 목록화하고 제거·재작성 계획을 decision record로 남긴다.

## 3. 인용 규칙

- pi와 prime-agent는 발표된 논문을 먼저 검색해 인용한다. 논문이 없으면 공식 저장소·문서를 소프트웨어 인용(버전, 접근일)으로만 참조한다. 내부 문서 인용 금지.
- 방법·결과 서술의 근거는 FULL_PAPER_READ만 인정한다(기존 프로토콜 유지). discovery_only·abstract_only는 문제 동기 부여까지만.
- 특정 제품(LangChain, LangGraph, CrewAI, Pinecone, Weaviate, MCP)은 논문이 있으면 논문, 없으면 공식 문서 소프트웨어 인용.
- 참고문헌은 본문 최초 인용 순 숫자 대괄호(공식 양식).

## 4. 문헌 지도 (6개 영역, 필수)

| # | 영역 | 하위 주제 | 논문에서의 역할 |
|---|---|---|---|
| 1 | Harness 기능 | sub-agent orchestration, sandbox, evaluator, approval loop, compression(context compaction), observability | 제안 방법의 핵심 구성요소 정당화 |
| 2 | Memory 기능 | working context, context graph, semantic knowledge, episodic experience, personalized memory | 메모리 계층 설계 |
| 3 | Protocols | agent-agent 통신, agent-user 통신, agent-tools 통신(tool calling, MCP) | 통신 계층 설계 |
| 4 | Skills | operational procedure, normative constraints, decision heuristics | 스킬·규범 계층 설계 |
| 5 | RAG engine | foundations, data chunking, vector databases, retrieval pipeline, generation layer | 지식 검색 계층 설계 |
| 6 | Agentic AI dev stack | foundations, AI agents(LLM+LangChain+tool calling), MCP(servers·clients·integration), Vector DB+RAG(Pinecone, Weaviate), multi-agent systems(CrewAI, LangGraph), orchestration(routing, workflows, state) | 관련 연구의 실무 생태계와 비교 기준 |

요구 사항:

- 영역마다 openresearch 검색 스트림 1개 이상. context graph에 영역 노드와 하위 주제 노드를 만들고 논문을 연결한다.
- evidence matrix에 영역 태그를 추가한다. 영역당 앵커 논문 3편 이상을 FULL_PAPER_READ로 확보한다. 기존 23편은 영역에 재배치한다.
- 각 영역의 "harness 필요성" 근거(단독 LLM의 실패 양상)와 "설계 선택" 근거(어떤 구성이 왜 낫다는 증거)를 구분해 기록한다.

## 5. 장 구성 (공식 양식 매핑)

- I. Introduction: 자율 연구에서 LLM 단독의 한계 → harness 필요성. 문헌 근거만.
- II. Related Works: §4의 6개 영역 순서로 절 구성.
- III. Proposed Method: harnessed autonomous research agent system 설계. 구성요소마다 인용 근거와 설계 결정 이유를 적는다. 내부 구현 명칭 대신 일반 용어를 쓴다.
- IV. Experimental Results: #0001 §3의 실행 가능한 최소 실험 단위 결과만. 미실행이면 사전등록 계획으로 표기.
- V. Conclusions.
- 분량은 공식 양식 제한을 지킨다. context graph는 넓게 두되 본문 인용은 주장 지지에 필요한 것만.

## 6. 순서와 보고

1. paper.tex·ledger에서 §2 금지 항목 목록화와 제거·재작성 계획 (decision record, 체크포인트 커밋).
2. 6개 영역 검색 스트림 실행, evidence matrix·context graph 갱신. 영역별 진행률(앵커 논문 수/FULL_READ 수)을 status.md에 유지.
3. Introduction·Related Works 재작성 (근거 확보된 영역부터).
4. Proposed Method 재구성.
5. 최소 실험 단위 제안서(#0001 §3)와 계획서 초안(#0001 §4)은 병행. 문헌 지도는 계획서 참고문헌으로 재사용.

각 단계 종료 시 status.md 갱신과 체크포인트 커밋. 사용자 결정이 필요하면 questions.md에 Q. 진행 중인 5편 재검토는 §4 영역 1에 흡수한다.

## 7. 불변 조건

모델 `openai-codex/gpt-5.6-sol` 유지, 미실행 결과 금지, DeepVoice 파일 편집 금지, 회사명·도메인 금지, `git add -A` 금지.

## 부록: 사용자 지시 원문 (2026-09-02 14:03 KST)

```text
paper 작성 방향을 제대로 잡아야해. 연구 목표는 llm 이 핸들링가능한 자율 연구 a harnessed llm agent system 의 필요성과 연구개발 진행이야. 우리는 구현의 편의와 연구개발 편의를 위해 pi기반 prime-agent를 파운데이션으로 사용하고 openresearch cli를 엔진으로 사용하여 자율연구 워크플로를 구축하고 검증하면서 지속 보강을 하고있는데. paper에는 이런 내부 개발사항과 내부 설계 내용이 들어가면 안돼. paper에는 pi, prime-agent에서 발표한 paper를 참조하거나 활용해서 작성해야하고 기본적으로 sub-agent orchestration, sandbox, evaluator, approval loop, compression, observability 등등 harness 기능 논문들을 활용하거나 cc해야하고, wokring context, context graph, semantic knowledge, episodic experience, personalized memory 등등 memory 기능 관련 논문들도 활용하거나 cc해야하고, agent-agent 통신, agent-user 통신, agent-tools통신 등등 protocols 기능 관련해서도 논문들을 찾아보고 활용하거나 cc해야하고, operational procedure, normative constraints, decision heuristics 등등 skills 기능 관련해서 논문들도 찾아서 사용해야해. rag enginer관련해서도 foundations를 시작으로 data chunking, vector databases, retrieval pipeline, generation layer 등등 논문들을 찾아서 활용해야하고, agentic ai dev 관련해서도 논문들을 찾아봐야해 foundations 논문부터 ai agents(llms+langchain+tool calling), mcp(severs+clients+intergration), vector DB+RAG(pinecone+weaviate), Multi-agent systems(crewAI+ LangGraph), orchestration(Routing+workflows+state) 등등
```
