# 직접 선행연구 비교와 ARGO 설계 변경

검토일: 2026-09-05 KST. 담당: 독립 문헌 검토자 Chandrasekhar, root 통합.
범위: 아래 명시한 원문 절을 직접 열람했다. 전체 부록까지 완독했다거나 기존 FULL_PAPER_READ receipt를 승계했다고 표시하지 않는다. Root도 출판사/PMLR/NeurIPS/arXiv 원문으로 주요 서지·방법을 확인했다. 초기 web 도구 빈 응답은 이후 해소됐다.

## 1. Co-Scientist — 가장 가까운 경쟁 기제

- 정식 제목: Accelerating scientific discovery with Co-Scientist.
- 출판: Nature, 2026-05-19. DOI `10.1038/s41586-026-10644-y`.
- 원문: `https://www.nature.com/articles/s41586-026-10644-y`.
- 직접 읽은 위치: Methods / Ranking agent, Proximity agent, Evolution agent, Ablation analysis; Discussion.
- 방법: proximity graph로 Elo tournament의 비교 대상을 정한다. 상위 후보에는 더 많은 debate 연산을 쓰고, evolution은 기존 가설을 덮어쓰기보다 새 후보로 추가하여 다시 경쟁시킨다.
- 한계: 자동 평가·전문가 참여·실제 생물학 검증의 증거층을 구분해야 한다. proximity와 품질의 상관을 graph representation의 인과효과로 바꾸면 안 된다. Discussion은 원문의 특정 그림·데이터까지 추적하는 provenance를 개선 과제로 명시한다.
- ARGO 선택: “그래프+경쟁+refine” 또는 넓은 “graph-conditioned selection”만으로 신규성을 주장하지 않는다. **유사도 관계와 evidence dependency/무효화 전파의 차이**를 동일 예산의 강한 비교군으로 평가한다.

## 2. The AI Scientist — 결과 기반 실험 트리가 이미 존재

- 정식 제목: Towards end-to-end automation of AI research.
- 출판: Nature, 2026-03-25. DOI `10.1038/s41586-026-10265-5`.
- 원문: `https://www.nature.com/articles/s41586-026-10265-5`.
- 직접 읽은 위치: Methods / Template-free AI Scientist, Generalized idea generation, Experiment progress manager, Parallelized agentic tree search for experimentation; Human evaluation results.
- 방법: 실험 노드가 code/plan/error/metric/critique 등을 저장하고, buggy node의 수정 또는 정상 node의 개선으로 분기한다. 단계별 leaf 선택을 다음 root에 이어 주며 replication·aggregation도 포함한다. 노드당 최대 1시간 및 단계별 budget 종료 규칙이 있다.
- 한계: 워크숍 대상 산출물에는 사람의 선택이 개입했다. 그 심사 결과를 무인 성공률이나 보편적인 재현성으로 해석할 수 없다. 전체 탐색·실패·선별 비용을 포함해야 한다.
- ARGO 선택: 단순 선형 agent뿐 아니라 결과 기반 tree policy도 경쟁 대안으로 검토한다. prototype의 branch/refine 자체는 구현 기능이지 새 과학적 기여의 충분조건이 아니다.

## 3. A-MEM — 기억 QA와 과학적 증거 계보는 다르다

- 출판: NeurIPS 2025 정식 proceedings; arXiv `2502.12110`.
- 원문: `https://proceedings.neurips.cc/paper_files/paper/2025/file/19909c36f51abc4856b4560aff3d36d6-Paper-Conference.pdf`.
- 직접 읽은 위치: PDF pp.3–6, §3.1–3.4, §4.1–4.2 및 실험 표.
- 방법: 구조화 note, embedding top-k, LLM link generation, 기존 note의 context/keyword/tag 변화, retrieval. LoCoMo/DialSim의 대화 기억 QA가 주요 평가다.
- 한계: 동일 system prompt가 동일 retrieval/context budget을 뜻하지 않는다. 대화 QA 결과는 과학적 dependency graph의 필수성을 입증하지 않는다.
- ARGO 선택: semantic association과 typed dependency를 구분하고, 불변 원문/버전별 계보를 왜 선택하는지 기록한다. `material-mechanism-evidence-map.md:29`의 “필요성 입증” 표현을 적용 범위에 맞게 축소한다.

## 4. POPPER — 반증이라는 이름보다 통계 조건이 중요

- 정식 제목: Automated Hypothesis Validation with Agentic Sequential Falsifications.
- 출판: ICML 2025, PMLR 267.
- 서지: `https://proceedings.mlr.press/v267/huang25n.html`.
- 원문: `https://arxiv.org/html/2502.09858`.
- 직접 읽은 위치: §2.1, §2.3 Assumptions 1–3 / Theorem 4, Appendix C Limitations.
- 방법: 주가설·하위 검정의 논리적 관계, 과거 정보에 조건부로 유효한 e-value, 적법한 stopping 조건 아래 순차 오류를 제어한다.
- 한계: Type-I error control은 과학적 진실성의 보장이 아니며 가설 선택·교체 및 데이터 재사용에는 추가 관리가 필요하다.
- ARGO 선택: 현재 “최대 세 번 critique/refine”는 이 보장을 구현한 것이 아니다. MVP는 bounded evidence-conditioned critique로 정확히 명명하고, 통계적 순차 반증을 선택한다면 조건과 구현을 별도 검증한다.

## 5. ScienceAgentBench — 실행 보조 평가로 사용

- 원문: `https://arxiv.org/html/2410.05080v3`.
- 서지: `https://arxiv.org/abs/2410.05080v3`의 저자 메타데이터는 ICLR 2025를 표시한다. 이번 검토의 OpenReview 직접 확인은 403으로 미완료다. 정식 proceedings 확인과 저자 표기를 구분한다.
- 직접 읽은 위치: §2.1, §3 Experimental Setup, Appendix A Limitations, Appendix E.1.
- 방법: 사람이 정한 과학 과업을 수행하는 Python 프로그램 생성이 기본 단위다. 주요 결과는 best-of-three이고 평균/표준편차는 별도 보고한다.
- 한계: 원문의 한계 절은 ideation 및 experimental design을 평가 범위 밖에 둔다. ARGO의 모든 반복 평균과 원 논문의 best-of-three를 직접 우열 비교하면 안 된다.
- ARGO 선택: execution 능력의 보조 benchmark로 유지하되 연구 결정 품질의 주 평가로 대신하지 않는다. 같은 집계·scaffold·예산으로만 비교한다.

## 통합 설계에 반영할 선택

1. 동일 자료·후보·모델·예산의 flat ledger, proximity/experiment-tree 선택 정책, typed evidence-dependency 정책을 비교 후보로 둔다. **주 contrast는 typed 정책 대 가장 가까운 강한 active comparator**로 한정하고 flat은 해석용 baseline으로 둔다. 모두 비교하는 비용이 불가능하면 핵심 두 조건만 남기되 강한 comparator를 제거하지 않는다.
2. 공개 시스템 전체 재현이 아니면 “Co-Scientist/AI Scientist를 이겼다”가 아니라 mechanism-matched comparator라고 명명한다. 원 논문 숫자는 맥락이며 같은 조건 재실험을 대체하지 않는다.
3. 가장 작은 기제 검사는 관련 dependency 변화와 무관한 edge 변화를 대조하여 재계획/보존/인계가 예상대로 달라지는지 확인하는 것이다. 이는 representation 성능 비교와 구분된 manipulation diagnostic이다. 양쪽 자료 equality를 깨뜨린 실험을 content-matched G 효과로 해석하지 않는다.
4. 변화 없음의 해석도 사전 명세한다. 실제 수정 graph가 소비됐고 해당 dependency가 결정을 바꿔야 하는 비중복 과제에서만 부정적 증거가 된다. redundant path·ceiling·미발화 문제는 효과 부재와 다르다.
5. 통계 모순 수리, 독립 채점 및 cross-agent handoff를 이 한 scientific-choice loop에 결합한다. 문헌 수나 graph node 수를 성과로 삼지 않는다.

## 보류하는 주장

선정 논문 전체 부록 완독, 동일 예산 재현 성능, ARGO의 graph-conditioned 행동 효과, 좁힌 기여의 전 문헌상 최초성은 확인하지 않았다. 따라서 이것은 **기여 후보와 경쟁 비교군의 구체화**이며 SOTA 인증이 아니다. 본문에 인용을 새로 결합할 때는 정확한 원문 버전·읽기 범위·span/hash·출판 지위를 보존해야 한다.
