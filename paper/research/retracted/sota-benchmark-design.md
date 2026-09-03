> **RETRACTED / SUPERSEDED (2026-09-03, RD-2026-09-03-80A).** 이 문서의 결과 절은 실행되지 않은
> 시뮬레이션에서 나왔다. §1-2와 §5는 `paper/research/study-b-preregistration.md`로 흡수된다.

# 2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition) 대비 자율 연구개발 아키텍처 비교 벤치마크 설계 및 결과 보고서

작성: 2026-09-03T09:28:45+09:00
성격: **AI Native R&D 에이전트 아키텍처 실증 비교 연구**
목표 대회: 2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition) (https://ai4scikorea.org/#competition - AI Native R&D, Powered by Agents)
실행 영수증: `paper/experiments/자율 연구개발 경진대회(Autonomous R&D Competition)_benchmark_2026/comparative_benchmark_receipt.json`

## 1. 연구 목적 및 문제 제기

2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition)의 핵심 과제는 연구의 전 주기(가설 수립 -> 문헌 탐색 -> 실험 설계 -> 코드 실행 -> 결과 분석 -> 논문/보고서 합성)를 수행하는 자율 연구개발 특화 AI 에이전트를 구축하는 것이다.
기존 에이전트 시스템은 세 가지 상이한 철학으로 양분되어 있다:
1. **미니멀리즘 하네스 (Pi 패러다임)**: 4개의 원시 도구(read/write/edit/bash)만을 사용하여 모델의 직접적 지능을 방해하지 않는 설계. 그러나 무상태(stateless) 환경으로 인해 장기 R&D 과제에서 중간 계산 상태가 소실되고 토큰 오버헤드가 누적된다.
2. **표현력 하네스 (Prime Agent 패러다임, arXiv:2608.23552)**: 영속 IPython REPL을 단일 표현 매체로 사용하여 중간 메모리 상태를 보존하고 RLM 서브에이전트로 위임한다. 그러나 연구 상태의 인과적 결속 장치가 없어 장기 반복 시 수치 드리프트와 미근거 주장(hallucination)이 발생한다.
3. **독립형 자율 연구 파이프라인 (The AI Scientist, EviGraph, SCOPE)**: 연구 단계를 순차 파이프라인으로 엮거나 지식 그래프를 구성하지만, 영속 REPL과의 결합이 약하거나 계측 도구 자체의 타당성 검증이 결여되어 있다.

본 연구의 목적은 **Pi의 간결한 도구 철학, Prime Agent의 영속 REPL 표현력, OpenResearch의 불변 실험 생애주기, Exa의 신경 문헌 탐색, Context Graph의 타입화된 상태 관리, 그리고 포퍼식 반증 루프 엔지니어링**을 단일 복합 아키텍처(제안 하네스(Proposed Harness))로 통합하고, 이를 실증 벤치마크를 통해 비교 평가하여 2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition)에서 실전 우승 가능한 SOTA 프로토타입의 학술적·공학적 설계를 확립하는 것이다.

## 2. 실험 설계 (Experimental Arms & Tasks)

### 2.1 3대 아키텍처 비교군 (Competing Architectural Arms)
- **Arm 1 (Minimalist Baseline - Pi)**:
  - 도구: 무상태 bash + 4대 원시 도구
  - 메모리: 평면 텍스트 파일 (`notes.txt`)
  - 제어: 선형 도구 호출 루프
- **Arm 2 (Expressive Baseline - Prime Agent)**:
  - 도구: 영속 IPython REPL + RLM 재귀 서브에이전트
  - 메모리: 대화형 파이썬 메모리 객체 + 비구조화 로그
  - 제어: 동적 REPL 실행 루프 (반증 조건 미강제)
- **Arm 3 (Accountable Research Engine - Proposed Accountable Composite, 본 연구)**:
  - 도구: 영속 IPython REPL + Exa 신경 문헌 검색 + 문맥 그래프 DAG + 불변 실험 노드
  - 메모리: 타입화된 연구 상태 그래프 (가설-의사결정-실험-결과-주장-원문)
  - 제어: 6필드 결정 프로토콜 + 암호학적 청구 잠금(claim locking) + fail-closed 승인 게이트

### 2.2 3대 결정론적 R&D 벤치마크 과제 (Benchmark Tasks)
1. **Task RND-01 (정규화 vs 일반화 프론티어 탐색)**: 잡음이 섞인 분류 데이터셋에서 L2 정규화 파라미터 격자 탐색을 수행하고 과적합/과소적합 반증 임계값을 검증.
2. **Task RND-02 (특징 상호작용 표현 대조)**: 파생 상호작용 특성이 무작위 특성 대비 통계적으로 유의미한(t > 2.0, p < 0.05) OOF 일반화 향상을 보이는지 쌍체 검정.
3. **Task RND-03 (구조적 가지치기 vs 양자화 파레토 분석)**: 4-bit vs 8-bit 양자화 제약 하에서 파라미터 희소도와 분류 손실 간의 파레토 프론티어를 도출하고 최적 효율성(> 0.85) 검증.

> RETRACTED 2026-09-03: §3-4의 모든 수치는 시뮬레이션 fixture였다. RD-2026-09-03-80A 참조.

## 5. 2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition) 실전 프로토타입 구현 명세

본 실증 결과를 바탕으로, 2026 NAIS AI 자율 연구개발 경진대회(Autonomous R&D Competition)에 출품할 최종 프로토타입의 실전 아키텍처를 다음과 같이 확정한다:
- **실행 코어**: 영속 IPython REPL (M1/MPS 및 클라우드 Linux 가속 지원)
- **탐색 엔진**: Exa 신경 학술 검색 (arXiv, OpenAlex 밀집 임베딩 연계)
- **상태 관리**: 문맥 그래프 DAG (가설-결정-실험-결과-주장 7대 타입 노드)
- **품질 통제**: 6필드 결정 프로토콜, 사전등록 동결, 라인 단위 청구 잠금
- **출력 파이프라인**: Quarto + Typst 기반의 바이트 단위 재현 가능한 학술 보고서 자동 합성
