# Study B 사전등록 — 하네스 구성 벤치마크 (Harness-Composition Benchmark)

- 작성 2026-09-03T10:14:39 · 상태 **DRAFT — 미봉인 · 미실행**
- 근거 지시: instruction-0013 §4, instruction-0013a §B
- 흡수: `harness-comparison-arm-design.md`, `paper/research/retracted/sota-benchmark-design.md` §1-2·§5 (둘 다 superseded)
- **실행 게이트: 사용자의 Q-0009 개정 승인 전에는 어떤 에피소드도 실행하지 않는다.**

## 1. 연구 질문

하나의 언어모델을 고정했을 때, 그 주위에 두르는 **하네스 구성요소**가 자율 연구개발 과제의
결정론적 검증기 통과율과 보고 충실도를 바꾸는가. 바꾼다면 **어느 구성요소가** 바꾸는가.

Study A는 이 질문에 답하지 못했다. 판정 기반 endpoint는 조건 성분이 약 0이었고 계측기 분산이
효과보다 컸다(Cycle 56-59). 그 결과는 그 자체로 정직한 **측정 장(measurement chapter)**이며,
Study B가 결정론적 검증기와 receipt 대조로 가야 하는 **이유**다.

## 2. 아암 (모델 고정, 예산 동일, 구성요소 하나만 차이)

| id | 아암 | 구성 | 메커니즘 노드 |
|---|---|---|---|
| B0 | 최소 도구 하네스 | read/write/edit/bash + 메모 파일, 무상태, REPL 없음 | `mechanism:minimal_tool_coding_harness` |
| B1 | 표현력 REPL 하네스 | 영속 Python REPL + 재귀 서브콜 | `mechanism:persistent_repl_recursive_harness` |
| B2 | 책임 가능 복합 하네스 | B1 + 타입 컨텍스트 그래프 + 6필드 결정 프로토콜 + claim locking + 페일클로즈드 게이트 + 결과 주도 검색 + 반증 루프 | 위 + 나머지 5개 |
| B2−G | B2 − 컨텍스트 그래프 | 평면 메모 파일로 대체 | `typed_research_context_graph`, `graph_engineering` 귀속 |
| B2−P | B2 − 결정 프로토콜·claim locking | 자유 서술 보고 | `failclosed_research_lifecycle` 귀속 |
| B2−R | B2 − 결과 주도 검색 | 로컬 자료만 | `result_driven_semantic_search` 귀속 |
| B2−L | B2 − 반증 루프 | 사전등록 임계값 없이 1회 실행 | `loop_engineering` 귀속 |

아암 간 차이는 명시된 구성요소 **하나**뿐이다. 구성요소 귀속 방법론은 HarnessOpt-Bench
[2608.06301], Arbor [2606.11926], DarwinX [2608.07545]의 ablation 설계를 따른다.
각 아암은 커밋 해시로 고정된 코드·도구 집합·시스템 프롬프트를 갖는다(봉인 시 기입).

## 3. 실행 기판 (instruction-0013a §B)

**아암 × 과제 블록 하나 = 불변 실험 노드 하나.** 노드는 프로젝트 `0dd58a66…`의
`c11c76ef…` 하위에 `study-b/<arm>/<task>` 제목으로 만든다. run command는 이 문서에 봉인된
문자열과 **바이트 동일**해야 하며 아암·과제·시드는 인자로만 바뀐다.

실행은 `orx exp run <expId> --backend local` → `orx exp wait` → `orx logs <run-id>` 경로만
인정한다. **REPL에서 직접 실행한 에피소드는 결과로 인정하지 않는다.** 드라이런도 같은 경로다.

receipt 필수 필드: `origin`, `model_id`, `provider_usage_log`, `protocol_fingerprint`,
`harness_commit`, `episode_transcripts_dir`, **`orx_project_id`, `orx_experiment_id`,
`orx_run_id`, `node_commit`**. 게이트가 run 존재·상태 `done`·커밋 일치를 검사한다.

## 4. 과제 (결정론적 검증기, CPU 우선)

1. **T1 ResearchClawBench 실행 서브셋** — 저장소 `github.com/InternScience/ResearchClawBench`
   확인됨. **라이선스·다운로드 경로를 사용 전에 검증하고 retrieval record로 남긴다(미완).**
2. **T2 Q-0007 완주 과제** — 기존 receipt 보유. Q-0007은 Study B의 예산 완주율 endpoint에
   흡수되며 별도 $18.28 지출은 요청하지 않는다.
3. **T3 정칙화·상호작용·압축 3종** — 격리된 시뮬레이션(`fixtures/simulated_oracles.py`)이 아니라
   **같은 샌드박스에서 고정 시드로 실행되는 검증기 스크립트**가 ground truth를 생성할 때만 허용한다.
   oracle receipt는 §3의 출처 필드를 갖고, 피시험 하네스는 oracle을 읽을 수 없으며, 반증 임계값은
   어떤 아암도 실행되기 전에 봉인된다.
4. MLE-bench Lite는 GPU 확보 전까지 보류(기존 결정 유지).

과제군에는 **주장을 receipt와 대조할 수 있는 유형**이 반드시 포함된다(CSR endpoint의 전제).

## 5. Endpoint (순서 고정, 데이터 이전 봉인)

- **1차:** 결정론적 검증기 pass/fail. 과제×시드로 짝지은 **McNemar**(불일치 쌍이 적으면 정확 검정).
  양측, α = 0.05.
- **2차:** ① CSR(허용오차 명시) ② 미측정 지표 보고율 ③ 반증 시 궤도 수정률
  ④ 에피소드당 토큰·비용 ⑤ 예산 완주율(Study A와 같이 경쟁 사건으로 취급).
- 중간 확인 없음. 결과에 따른 에피소드 제외 금지.

## 6. 표본 크기 — 라벨된 검정력 계산 (결과 아님)

`experiments/study_b/power_mcnemar.py`, α = 0.05 양측, 검정력 0.80.
MDE는 두 아암의 **절대 통과율 차이**다.

| 과제당 짝 수 | 불일치율 0.20 | 0.30 | 0.40 |
|---:|---:|---:|---:|
| 40 | 0.198 | 0.243 | 0.280 |
| 60 | 0.162 | 0.198 | 0.229 |
| 120 | 0.114 | 0.140 | 0.162 |

**정직한 함의:** 과제당 40쌍으로는 약 20~28 %p보다 작은 차이를 잡지 못한다. 하네스 구성요소
하나의 효과가 그보다 작다면 이 설계는 그것을 **검출하지 못한다**. 이 한계를 결과 해석 전에 적는다.

## 7. 비용 시나리오 (Q-0009 개정판)

기준: Study A에서 **실측된** 에피소드당 $0.13463
(`corrected-cost-measurement-receipt.json`, 6 에피소드 $0.80776, `anthropic/claude-haiku-4-5`,
`origin: model_call`). 추정이 아니라 측정값의 외삽이며, 과제 난이도가 다르면 달라진다.

| 시나리오 | 아암 | 과제 | 과제당 n | 에피소드 | 추정 상한 |
|---|---:|---:|---:|---:|---:|
| (a) 1차 스크리닝 | 3 | 3 | 40 | 360 | **$48.47** |
| (b) 1차 + 절제 | 7 | 3 | 40 | 840 | **$113.09** |
| (c) 전체 + 2차 반복 | 7 | 3 | 60 | 1,260 | **$169.63** |

이전 harness-comparison 설계의 $7.30/$14.60은 아암 2개·에피소드 수가 훨씬 작은 다른 설계였다.
이 표가 그것을 대체한다.

**승인 전 허용 범위:** 하네스 코드·과제·검증기·fixture 구축, failing-first 테스트,
그리고 가장 싼 모델로 **아암당 n=1 파이프라인 드라이런(총 $2 상한)**. 드라이런 receipt는
`origin: model_call`, `evidence_level: PIPELINE_DRY_RUN`으로 라벨하고 **결과표에 넣지 않는다.**

## 8. 봉인

봉인 시 이 문서의 sha256과 아암 7개의 커밋 해시, 고정 run command 문자열을 기록하고
`.orx/paper_protocol.json`에 다이제스트를 등록한다. 봉인 이후 §2-§6은 수정하지 않는다.

## 9. 미완 항목 (봉인 전 반드시 닫는다)

1. ResearchClawBench 라이선스·다운로드 경로 검증
2. 아암 7개 구현 및 커밋 해시 확정
3. T3 검증기 스크립트와 oracle 격리 증명
4. 고정 run command 문자열 확정
5. 비교 실험 표 `comparable-experiments-study-b.md` 5편 이상
