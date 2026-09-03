# 비교 실험 표 — 선행 하네스·에이전트 비교 연구와 Study B의 정렬·이탈

작성 2026-09-03T10:25:13 · 근거 instruction-0013 §5
**증거 범위:** 각 행은 정독 보고서와 **arXiv 전문 HTML 본문**에서 확인한 사실만 담는다.
확인되지 않은 칸은 **"미기재"**로 적고 추정하지 않는다.

> **2026-09-03 정정.** 이 문서의 초판은 "8편 어디에도 짝지은 통계 검정이 기재되지 않았다"고 적었다.
> 그 진술은 정독 보고서만 근거로 한 것이었고 **틀렸다**. 전문 HTML을 직접 받아 확인한 결과
> DarwinX는 **paired exact McNemar**를, HarnessOpt-Bench는 **라운드 평균의 표준오차**를 실제로 쓴다.
> 아래 표와 §3-1을 그에 맞게 고쳤다. 초판 진술은 지우지 않고 여기에 남긴다.

## 1. 표

| # | 연구 | 아암/비교 대상 | 과제·벤치마크 | n (정독 보고서 기준) | 1차 endpoint | 짝지은 통계 검정 | 절제(ablation) | 비용 보고 |
|---|---|---|---|---|---|---|---|---|
| 1 | HarnessOpt-Bench [2608.06301] | 하네스 구성 변형 | Terminal-Bench 2.0, GAIA, OfficeQA Pro, BrowseComp-Plus | **K=3 라운드** | 라운드 평균 점수 | 검정 없음. **± = 라운드 평균의 표준오차** | 언급 없음 | 미기재 |
| 2 | Arbor [2606.11926] | 에이전트 구성 변형 | Terminal-Bench 2.0 | 보고서에 미기재 | 성공률 | **미기재** | 2회 언급 | 미기재 |
| 3 | ResearchClawBench [2606.07591] | 에이전트 시스템 간 | 자체 40개 연구 과제 | 40 과제 | 재발견→신규발견 달성도 | **미기재** | 언급 없음 | 미기재 |
| 4 | LongHorizon-Harness [2608.01964] | 장기 과제 하네스 | Terminal-Bench 2.1 | 108, 114 (문맥상 과제 수) | 성공률 | **미기재** | 언급 없음 | 미기재 |
| 5 | Evo-Bench [2608.09096] | 진화적 구성 탐색 | 보고서에 미기재 | 보고서에 미기재 | 성능 향상 | **미기재** | 1회 언급 | 미기재 |
| 6 | HEP [2607.09195] | 하네스 진화 정책 | 보고서에 미기재 | 보고서에 미기재 | 성능 향상 | **미기재** | 언급 없음 | 미기재 |
| 7 | DarwinX [2608.07545] | 진화된 하네스 vs 기준 | Terminal-Bench 2.1, TerminalWorld, WebArena-Infinity, SWE-bench Verified | TerminalWorld **41 held-out 과제** | 벤치마크 pass@1 | **있음 — paired exact McNemar** (p=1.0, p=0.45) | **있음** — 이득을 검증/계약 스킬 번들에 귀속 | 미기재 |
| 8 | 영속 REPL 하네스의 nanogpt 효과 [2608.23552] | 하네스 유무 | nanogpt 계열 과제 | 기존 locator `prime_nanogpt_harness_effect` 참조 | 과제 성능 | **미기재** | 언급 없음 | 미기재 |

## 2. Study B가 각 행과 일치하는 지점

- **구성요소 귀속 방식**: DarwinX(7행)가 이득을 특정 스킬 번들에 귀속시킨 절제 설계, Arbor(2행)·Evo-Bench(5행)의
  구성 변형 비교와 같은 논리를 따른다. Study B의 B2−G/−P/−R/−L은 이 절제 관행의 직접 적용이다.
- **과제 계열**: ResearchClawBench(3행)를 T1로 그대로 채택한다(MIT 라이선스 확인). 연구 과제를 대상으로 한다는 점에서
  3행과 정렬하고, 코딩 벤치마크 중심인 1·2·4·7행과는 대상이 다르다.
- **하네스가 독립변수**: 8개 행 전부와 마찬가지로 모델을 고정하고 하네스를 바꾼다.

## 3. Study B가 이탈하는 지점과 그 이유

1. **짝지은 검정을 사후 서술이 아니라 1차 endpoint로 사전등록한다.**
   DarwinX(7행)는 이미 paired exact McNemar를 쓴다. 다만 **사후 보고**이며, 그 결과 41개 과제에서
   25/41 대 28/41의 차이가 **p=0.45로 결정적이지 않다**고 스스로 적는다. HarnessOpt-Bench(1행)는 K=3 라운드의
   표준오차를 보고하되 "두 라운드는 산포를 추정하지 못한다"고 명시한다. 나머지 6편은 짝지은 추론을 기재하지 않았다.
   Study B의 이탈점은 검정의 존재가 아니라 **위치**다: 대비·풀링·α·보정을 데이터 이전에 봉인한다.
2. **검출 한계를 결과 이전에 공개한다.**
   DarwinX의 p=0.45는 이 문제의 **직접적 선례**다. 41개 과제로는 3개 과제 차이를 결정할 수 없었다.
   Study B는 같은 함정을 사전에 계산해 공개한다: 풀링 120쌍에서 MDE 0.140, 과제별 40쌍에서 0.243
   (`experiments/study_b/power_mcnemar.py`). 위 연구들은 이 값을 **결과 이전에** 적지 않았다.
3. **보고 충실도 자체를 endpoint로 둔다.**
   위 8편은 과제 성공률만 본다. Study B는 **청구-receipt 대조(CSR)와 미측정 지표 보고율**을 2차 endpoint로 둔다.
   하네스가 정답률을 못 바꾸더라도 **주장의 근거성**을 바꿀 수 있으며, 이는 자율 연구 맥락에서 독립적 가치를 갖는다.
4. **비용을 실측 기반으로 사전 공개한다.**
   8편 모두 비용을 기재하지 않았다. Study B는 실측 에피소드 단가($0.13463, `origin: model_call`)에서 세 시나리오
   ($48.47 / $113.09 / $169.63)를 계산해 승인 전에 공개한다.
5. **실행 기판이 불변 노드다.**
   아암×과제 블록 하나가 고정 실행 계약을 가진 불변 실험 노드 하나에 대응하며, 그 경로 밖에서 실행된 에피소드는
   결과로 인정하지 않는다. 8편에는 이에 해당하는 재현 계약 기술이 없다.

## 4. `coding-harness-differentiation-matrix.md` 미해결 항목 종결

- **최소 도구 하네스의 단독 논문 부재**: 여전히 부재를 확인했다. B0의 근거 수준은 `PRIMARY_SPEC_OR_CODE`로 유지하고,
  논문에서는 "네 가지 원시 도구의 최소 코딩 하네스"로 서술하며 코드 locator를 인용한다.
- **SWE-agent / OpenHands 대조**: DarwinX(7행)가 SWE-bench Verified를 포함해 코딩 하네스 계열의 대조군을 제공하므로,
  Study B는 코딩 벤치마크 대조를 직접 재현하지 않고 이 문헌을 인용해 위치를 표시한다.

## 5. 한계

이 표는 정독 보고서 기반이다. 각 원논문의 부록·저장소를 직접 열어 n·검정·비용을 재확인하는 작업은 봉인 전 잔여 과제다.

---

## 4. 설계공간 문헌 검증 (instruction-0015 §3)

작성 2026-09-03T16:27:40+09:00 · 검증 원시: `orx discover openalex/keyword` · 보조: exa MCP 2회(채택 0건)
**검증 규칙:** 반환된 제목이 의도한 연구 그 자체일 때만 VERIFIED. 부분 문자열 충돌은 실패로 본다.
실제로 `CodeAct`는 무관한 "Code Adaptive Compute-efficient Tuning"과 충돌해 기각 후 재검색으로 정정했고,
`CORE-Bench`는 벤치마크 포화 연구와 충돌해 **위치하지 못하면 기각** 원칙에 따라 UNVERIFIED로 남겼다.

### 4.1 최소 도구 하네스 계열 (B0의 비교군)

| 연구 | 식별자 | 검증 | Study B와의 관계 |
|---|---|---|---|
| SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | `10.48550/arxiv.2405.15793` | VERIFIED | 하네스 인터페이스 자체가 성능을 좌우한다는 주장의 직접 근거. Study B는 이 주장을 **같은 모델·결정론적 검증기**로 분리해 재검증한다 |
| Executable Code Actions Elicit Better LLM Agents (CodeAct) | `10.48550/arxiv.2402.01030` | VERIFIED | 코드를 행동 매체로 쓰는 선택의 근거. B1의 REPL과 같은 계열이되, CodeAct는 태스크 성능 비교에 머문다 |
| OpenHands: An Open Platform for AI Software Developer Agents | `10.48550/arxiv.2407.16741` | VERIFIED | 플랫폼 규모 비교군. 아암 대조가 아니라 시스템 대조이므로 Study B는 구성요소 단위로 이탈한다 |

### 4.2 기억·그래프 계열 (B2−G의 비교군)

| 연구 | 식별자 | 검증 | Study B와의 관계 |
|---|---|---|---|
| A-Mem: Agentic Memory for LLM Agents | `10.52202/085713-0593` | VERIFIED | 동적 기억 구성. Study B의 그래프는 **타입과 불변성**이 규율이며 기억 효율이 아니다 |
| Is GraphRAG Needed? From Basic RAG to Graph-/Agentic RAG | `2606.25656` | VERIFIED(별개 연구) | **원 GraphRAG 논문이 아니다.** 그래프 구조화 검색의 이득이 조건부라는 명제만 사용한다. 원 논문을 인용한 것처럼 쓰지 않는다 |
| Reinforced Graph of Thoughts: RL-Driven Adaptive Reasoning | `2605.22195` | VERIFIED(별개 연구) | **원 Graph of Thoughts 논문이 아니다.** 추론을 그래프로 표현하는 계열의 존재 근거로만 쓴다 |

### 4.3 루프·자기수정 계열 (B2−L, B2−P의 비교군)

| 연구 | 식별자 | 검증 | Study B와의 관계 |
|---|---|---|---|
| Self-Refine: Iterative Refinement with Self-Feedback | `10.52202/075280-2019` | VERIFIED | 자기 피드백 반복의 대표 근거. Study B는 여기에 **사전등록 임계와 반증**을 더해 반복을 규율로 바꾼다 |

### 4.4 자동 설계 탐색 (대안 패러다임 — 미승인 미래 작업)

| 연구 | 식별자 | 검증 | 관계 |
|---|---|---|---|
| Automated Design of Agentic Systems (ADAS) | `10.48550/arxiv.2408.08435` | VERIFIED | 설계를 자동으로 탐색한다. Study B는 **고정·사전등록**을 택했으므로 이 계열은 대조 패러다임 |
| AFlow: Automating Agentic Workflow Generation | `10.48550/arxiv.2410.10762` | VERIFIED |위와 같은 관계(구성 자동화) |
| AgentSquare: Automatic LLM Agent Search in Modular Design Space | `10.48550/arxiv.2410.06153` | VERIFIED |위와 같은 관계(구성 자동화). 모듈 공간 탐색은 본 논문의 절제 아암과 같은 분해를 쓰되 탐색으로 채운다 |
| DSPy: Compiling Declarative LM Calls into Self-Improving Pipelines | `10.48550/arxiv.2310.03714` | VERIFIED | 프로그램 가능한 최적화. 평가가 아니라 구성을 자동화한다 |

### 4.5 벤치마크 선택 근거 (T1/T2/T3의 비교군)

| 벤치마크 | 식별자 | 검증 | Study B 사용 |
|---|---|---|---|
| ScienceAgentBench | `2410.05080` | VERIFIED | 연구 과제 선정 근거. T1 계열과 겹친다 |
| PaperBench | `2504.01848` | VERIFIED | 재현성 평가. 판정 기반 채점의 대표 사례이므로 본 논문의 계측 비판 대상 |
| MLE-bench | `2410.07095` | VERIFIED | 실행 채점 가능. 다만 미승인(MLE-bench Lite 제외 명시)이라 **선정 근거로만** 인용한다 |
| DiscoveryBench | `2407.01725` | VERIFIED | 데이터 주도 발견. T3의 자율연구 성격과 정렬 |
| CORE-Bench | 없음 | **UNVERIFIED** | 이번 주기에 위치하지 못했다. **인용하지 않고** 그래프에 unverified 노드로만 남긴다 |

### 4.6 왜 자동 탐색이 아니라 고정·사전등록인가 (결정)

자동 설계 탐색 계열(ADAS·AFlow·AgentSquare·DSPy)은 **더 나은 구성을 찾는 문제**를 푼다. 본 논문이 묻는
문장은 다르다: **자율 연구 하네스가 만든 결과를 무엇이 근거로 만드느냐.** 탐색을 함께 열면 (i) 탐색이
성능을 개선한 것이 하네스 책임인지 최적화 책임인지 분리되지 않고, (ii) 탐색 자체가 결과를 본 뒤에
설계를 바꿀 수 있어 사전등록이 무너지며, (iii) 시드마다 구성이 달라져 재현·회계·귀속이 붕괴한다.
따라서 구성을 고정하고 **절제 아암으로 사후에** 귀속시키는 쪽을 택한다. 근거는 해석 가능성,
provenance, 예산 세 축이며, 결정·반증자는 컨텍스트 그래프 `decision:rd_2026_09_03_90a`에 있다.
자동 탐색 아암은 미승인 미래 작업으로 명시한다.

