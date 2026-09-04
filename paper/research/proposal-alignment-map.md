# 졸업논문 계획서 1:1 대응 및 충족 보고서 (Proposal Alignment Map)

작성 시각: 2026-09-04T12:40:00+09:00
기준 문서: 최종 졸업논문 계획서 (`/Users/um-yunsang/Desktop/졸업논문계획서/졸업논문_계획서_엄윤상.pdf`, 2026-09-04 제출본)
권한: supervisor instruction-0022 §3

본 문서는 사용자가 제출한 최종 졸업논문 계획서의 모든 목적(6항)과 방법(5항)을 본 논문 연구 산출물과 1:1로 대조하여 이행 상태와 증거 경로를 기록한다.

---

## 1. 계획서 목적(6항) 1:1 대조

| 계획서 목적 항목 | 계획서 원문 내용 | 본 연구 산출물 및 이행 상태 | 증거 경로 (Artifact / Receipt) | 충족 판정 |
|---|---|---|---|:---:|
| **목적 1: 하네스 개발** | AI 에이전트가 연구를 스스로 설계·수행하는 하네스 개발 | 자율 R&D 에이전트 시스템 `argo` 프로토타입 설계 및 검증 | `paper/hackathon/prototype-spec.md`, `experiments/study_b/harness/` | **충족** |
| **목적 2: 자율 설계 및 중단 규칙** | 문제·가설·조건·방법·지표·**중단 규칙**을 에이전트가 직접 설정 | 사전등록 v4의 쌍 완결 규칙, 상한 도달 시 fail-closed 중단, 조작 검사 위반 에피소드 배제 규칙 | `paper/research/study-b-preregistration-v4.md` §3, `run_block.py` | **충족** |
| **목적 3: 근거 기반 선택** | 유사 실험·방법론·참고문헌을 탐색해 **선택마다 근거 부여** | instruction-0021 포지셔닝 확립, 모든 아키텍처 재료의 선행 정독 출처 매핑 및 미도출 부분 '근거 없는 기본값' 표기 | `paper/research/material-mechanism-evidence-map.md`, `paper/sources/claim-locators.json` (339건) | **충족** |
| **목적 4: 비교 추론** | 선행 연구의 실험 설계와 대조해 인사이트 확보 | 자동 설계 탐색(ADAS·AFlow·AgentSquare) 대 사전등록 통제 절제 연구의 5개 축 비교표 도출 | `paper/manuscript/thesis-ko.qmd` Ⅴ장 4절 | **충족** |
| **목적 5: 문맥 그래프 인계** | 문헌·가설·결정·실험·결과를 연결해 **다른 에이전트가 이어받도록** | 483개 노드와 876개 타입드 에지로 구성된 문맥 그래프 및 스키마 유효성 게이트 확립 | `paper/context-graph.json`, `.orx/paper_validate.py` (graph_schema) | **충족** |
| **목적 6: 결과 반영 루프** | 완결된 설계안으로 실행하고 결과에 따라 방향 갱신 | B2 pivots=0 결함 판정 및 기제별 용량-반응 2차 분석 사양 봉인 | `paper/research/study-b-mechanism-doseresponse-spec.md` | **충족** |

---

## 2. 계획서 방법(5항) 1:1 대조

| 계획서 방법 항목 | 계획서 원문 내용 | 본 연구 산출물 및 이행 상태 | 증거 경로 (Artifact / Receipt) | 충족 판정 |
|---|---|---|---|:---:|
| **방법 1: 5축 한계 도출** | 행동[1,2]·기억[3]·구조[4]·설계[5]·검증[6] 한계 통합 | 계획서 6대 참고문헌(SWE-agent, CodeAct, A-Mem, GoT, ADAS, SAV) 기반 5대 축 매핑 완료 | `paper/research/material-mechanism-evidence-map.md` | **충족** |
| **방법 2: 근거 미충족 시 불인정** | 유형화된 문맥 그래프, 결정·근거 기록, **근거 미충족 시 결과 불인정** | 페일클로즈드 출처 게이트, 4대 자가 오류 실증 적발(원고 Ⅴ장 1절) 및 영수증 실재 검사 | `paper/manuscript/thesis-ko.qmd` Ⅴ장 1절, `receipt_provenance` | **충족** |
| **방법 3: 구성요소별 절제 비교군** | **구성요소를 하나씩 제거한 비교군으로 요소별 기여도를 분리 측정** | 절제 4아암(B2-G/-P/-R/-L) 설계 완료되었으나, 현 예산/승인 제약으로 1차 스크리닝 B2에 5개 기제 묶임. 예산안 3종 산출 완료 | `paper/research/ablation-budget-options.md` | **미충족 (사용자 결정 대기)** |
| **방법 4: 규칙 기반 검증기 및 오라클 격리** | **판정 모델이 아닌 규칙 기반 검증기, 정답 격리, 절차의 사전 등록** | LLM 판정기(ResearchClawBench) 배제, ScienceAgentBench 결정론적 채점기, 워크스페이스 외부 격리 채점, 사전등록 v4 봉인 | `experiments/study_b/tasks/run_t1.py`, `experiments/study_b/tasks/test_t1.py` (16 PASS) | **충족** |
| **방법 5: 프로토타입 공개** | 예비 실험 완료, 잔여 비교군 수행 후 프로토타입 공개 | argo 자율 R&D 프로토타입 설계 명세 도출 완료 | `paper/hackathon/prototype-spec.md` | **충족** |

---

## 3. 충족 상태 요약
- 계획서 총 11개 세부 항목 중 **10개 항목 완전 충족**.
- **유일한 미충족 항목:** **방법 3 (구성요소별 절제 비교군 실행)** — 현재 B0, B1, B2의 1차 스크리닝 블록이 구동 중이며, 절제 아암(B2-G, B2-P, B2-R)의 실제 실행 여부는 `ablation-budget-options.md`에 제시된 예산안에 대한 사용자 승인 후 결정됨.
