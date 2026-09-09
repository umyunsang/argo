# STATISTICS — ARGO 졸업논문 통계 근거 검토

- 기준일: 2026-09-05 KST. 범위: 논문 초안의 통계적 주장과 방법론 문구만 검토.
- 상태: 본문 구간을 읽은 일차 자료 5건 보존; 공개 통계 인용은 Agarwal·Dror·Nosek의 출판 논문 3편만 채택한다. 아래 제안은 새 실험계획의 승인·확정이 아니다.
- 통합 결정(2026-09-05 KST): HAL은 최종 학회 PDF 미열람 때문에 공개 참고문헌과 삽입 문구에서 제외한다. S1 및 관련 검토는 비공개 현재 연구 기록으로만 유지하며 최종 PDF 추가 탐색은 하지 않는다.
- 수행: 프로젝트 `AGENTS.md`, `docs/argo/agent-brief.md`, `docs/argo/migration-state.json`, 현재 계획의 `findings.md` 확인 및 `web.run` 원문·출판 상태 확인. 원시 실험 재분석, 테스트, 네이티브 변경, 외부 에이전트 사용 없음.
- 계획·진행 기록: 지침 확인 → 원문 및 서지 확인 → 적용 조건·반론 정리 → 초안 문구 → 요청에 따른 원문 보존·부분 재열람·해시 기록 완료. lane 소유권에 따라 공용 계획 파일은 수정하지 않았다.

## 1. 지금 내릴 수 있는 결론

**현재 결과 장은 평가도구 검증과 기존 실험의 증거 한계를 보고해야 한다. ARGO 효과의 크기·신뢰구간·유의성을 보고할 단계가 아니다.** 아래 프로젝트 수치는 이 연구 lane에 주어진 현행 맥락이며 원시 자료를 재검증한 결과가 아니다. 문헌은 이 숫자의 사실성을 증명하지 않는다.

| 주어진 프로젝트 상태 | 허용되는 서술 | 피해야 할 서술 |
|---|---|---|
| Stage 0: 과제 scorer 16개, 정상·손상 fixture 검사 96건 모두 결정론적 PASS | 지정된 검사 집합에서 기대한 채점 동작을 확인했다 | 독립 과제 96개에서 ARGO 성공률 100%; 모집단 신뢰성 입증 |
| runtime policy PASS; integrated runner 미인증 | 런타임 정책 검사 통과와 통합 실행기 인증은 별개다 | 종단 간 실행과 효과 평가까지 완료했다 |
| efficacy admitted 0 | 효과 추론에 채택된 실행이 아직 없다 | ARGO의 효과 또는 성공확률이 0이다 |
| T3: 하나의 과제, 내부 seed 0, 총 120회 실행 | 동일 과제에 대한 개발·진단 기록이다 | 조건별 독립 표본 n=40; 과제 간 일반화 근거 |
| T1-prime: 48건 중 evaluator crash 42건, 격리 | 평가 과정 결함 때문에 효과 추론에서 격리했다 | crash를 정답·정상 실패로 바꾸어 효능 표본을 복원했다 |

## 2. 원문 독서 및 출판 상태 — 5개 자료

아래 독서 위치는 선택적으로 읽은 본문 구간이지 논문 전체 정독 표시가 아니다. 보존본에 직접 연결되는 재열람 범위, PDF 물리 페이지, HTML anchor, 미열람 범위 및 SHA256은 `statistics-sources/README.md`와 `manifest.json`에 기록했다. 이번에 다시 받은 bytes와 이전 `web.run` 전달 내용의 바이트 동일성은 증명하지 않는다.

### S1. Kapoor et al., HAL — 비공개 검토 전용, 공개 인용 제외

- 제목: *Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation*.
- 출판 상태: ICLR 2026 공식 포스터 목록 및 저자 기관의 공식 프로젝트 서지에서 정식 학회 발표 확인. 열람한 본문은 **arXiv:2510.11977v1, 2025-10-13**이다. 조회한 arXiv 이력에는 v1만 있다. 학회 최종 PDF는 OpenReview 브라우저 검증 화면 때문에 읽지 못했으므로, 아래 구간을 최종본 구간이라고 주장하지 않는다.
- 본문: https://arxiv.org/html/2510.11977v1
- 상태 근거: https://iclr.cc/virtual/2026/poster/10006806 ; https://hal.cs.princeton.edu/
- 식별자: https://doi.org/10.48550/arXiv.2510.11977 — **arXiv DOI이지 학회 proceedings DOI가 아니다.**
- 읽은 위치: §1 비용·로그·평가 분리; §4.2 로그 분석; Appendix A2 실행 격리·timeout·로그; A3 항목 1, 2, 5, 8; A4.1–A4.2; A5 누출 사례.
- 직접 근거: 비용과 결과를 함께 관찰해야 하며, 인프라 실패가 능력 실패처럼 집계될 수 있다. 저자들은 대부분의 평가에서 반복 기반 통계 검증이 없었다는 한계도 공개한다.
- 적용: 비용의 경계와 실패 원인을 분리해 보고할 근거. 반론: HAL 자체가 소표본 불확실성을 해결한 표준은 아니다. 회피: HAL의 실행 규모·단일 실행 관행·모델 순위를 ARGO의 표본 설계나 효과 근거로 복사하지 않는다.

### S2. Agarwal et al., NeurIPS 2021

- 제목: *Deep Reinforcement Learning at the Edge of the Statistical Precipice*.
- 출판 상태: *Advances in Neural Information Processing Systems*, 34, NeurIPS 2021 정식 논문. 조회한 공식 서지에 없는 proceedings DOI는 만들지 않았다.
- 공식 서지: https://proceedings.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html
- 읽은 본문: https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf
- 읽은 위치: §2, PDF pp.2–3 과제×반복 모형; §3, pp.4–5 점추정·평가 프로토콜 문제; §4.1, pp.5–6 stratified bootstrap, Figure 6 캡션·해설; §4.2, pp.6–7 분포 보고. 전체 그림의 수치 판독·재현은 수행하지 않았다.
- 직접 근거: 고정된 과제별로 반복을 재표집하는 층화 bootstrap과 효과 차이의 구간 보고를 제시한다. 반복이 적으면 구간의 실제 coverage가 명목 수준에 못 미칠 수 있다.
- 적용: 과제와 반복 차원을 보존하고 불확실성의 발생원을 밝히는 근거. 반론: RL 훈련 run과 LLM agent rollout은 동일하지 않다. 회피: 논문의 run 수, IQM, Atari 정규화, bootstrap 방식을 ARGO의 확정 규칙으로 이식하지 않는다. 특히 **고정 과제 내부 반복 재표집은 새로운 과제 모집단에 대한 추론과 다르다.**

### S3. Dror et al., ACL 2018

- 제목: *The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing*.
- 출판 상태: ACL 2018 Long Papers 정식 논문, pp.1383–1392. 저자들의 방법론·실태 조사 논문이며 McNemar/Wilcoxon 검정의 최초 발표 논문은 아니다.
- 공식 서지 및 DOI: https://aclanthology.org/P18-1128/ ; https://doi.org/10.18653/v1/P18-1128
- 읽은 본문: https://aclanthology.org/P18-1128.pdf
- 읽은 위치: §2.1 효과 차이; §3.2.2, pp.1387–1388 McNemar, Wilcoxon, permutation, paired bootstrap; §3.3 선택 조건; §5, p.1390 관측 간 의존성.
- 직접 근거: McNemar는 짝지은 이진 관측의 주변확률 비교이고, Wilcoxon signed-rank는 차이의 대칭성 조건을 가진 순위 기반 검정이다. 관측 의존성은 검정의 보장을 훼손한다.
- 적용: 원고의 두 검정명을 단순 통일하기보다 결과 변수와 분석 단위를 먼저 맞춰야 한다. 반론: 이 논문의 간단한 선택 트리는 모든 계층적 agent 자료를 해결하지 않는다. 회피: 비모수 검정을 ‘가정이 전혀 없는 검정’으로 쓰거나, 동일 과제의 반복을 독립 관측으로 넣지 않는다.

### S4. Nosek et al., PNAS 2018

- 제목: *The preregistration revolution*.
- 출판 상태: *PNAS* 115(11), 2600–2606 정식 Colloquium Paper; 온라인 2018-03-12, 호 발행 2018-03-13. 방법론 제안·논증이며 모든 분야에서의 인과적 효과를 입증한 실험은 아니다.
- 출판사/DOI: https://doi.org/10.1073/pnas.1708274114
- 이전 검토에 기재한 대학 PDF 주소: https://psychologicalsciences.unimelb.edu.au/__data/assets/pdf_file/0007/2888098/The-preregistration-revolution.pdf — 이번 보존 시도에서는 HTTP 403으로 PDF 확보 실패. 오류 HTML은 원문과 분리했다.
- 보존·재열람한 일차 본문: https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/ ; `#s3` “Preregistration Distinguishes Prediction and Postdiction”, `#s4` “Preregistration in Practice” 도입, `#s5` The Ideal, `#s6`–`#s8` Challenges 1–3, `#s20` Conclusion.
- 페이지 경계: 이전 검토에는 예측/사후설명 pp.2601–2602, 실무·Challenges 1–3 pp.2602–2603, Conclusion p.2605를 기재했다. 이번에는 PDF를 보존하지 못해 이 세부 페이지 대응을 재확인하지 않았다. 상세 인용에는 위의 검증된 HTML section locator를 우선하며, HTML을 PDF 페이지 증거로 둔갑시키지 않는다.
- 직접 근거: 결과 관찰 이전의 예측과 관찰 이후의 설명을 구분한다. 계획 변경을 투명하게 보고할 수 있지만, 사전등록 자체가 나쁜 통계나 결과 의존적 중단을 정당화하지 않는다.
- 적용: 기존 진단자료는 탐색으로, 미래의 결과 비열람 조건에서 승인된 검증은 확인으로 구별한다. 반론: 탐색은 열등하거나 금지된 연구가 아니다. 회피: 지금 문서를 작성한 행위를 기존 T3/T1-prime 실험의 사전등록으로 소급하지 않는다.

### S5. NeurIPS 공식 Paper Checklist — 2026-09-05 열람

- 출판 상태: 학회 공식 온라인 지침. 심사 논문이나 효과 검증 연구가 아니다. 페이지의 2026 탐색 메뉴를 문서 개정일로 해석하지 않는다.
- 원문: https://neurips.cc/public/guides/PaperChecklist
- 읽은 위치: 항목 1 Claims, 2 Limitations, 6 Experimental Setting/Details, 7 Experiment Statistical Significance, 8 Experiments Compute Resource.
- 직접 근거: 주장 범위·독립성 등 가정·변동 원인·구간 산출 방법·SD와 SE의 구별·실패/예비 실험을 포함한 계산 자원 보고를 요구한다.
- 적용: 논문의 통계 보고 점검표로 활용한다. 반론: 학회 체크리스트 준수는 통계적 타당성의 증명이 아니다. 회피: 모든 결정론적 fixture에 의미 없는 error bar를 붙이거나 ‘최신 SOTA 통계법’이라고 부르지 않는다.

## 3. 좁은 방법론 권고 — 미확정 제안

아래는 S1–S5를 ARGO 상황에 연결한 **비공개 방법론 검토와 미확정 제안**이다. S1과 S5의 표시는 연구 검토 이력이며 공개 인용으로 옮기지 않는다. 공개 삽입 문구와 참고문헌은 §4–§5의 출판 논문 3편만 사용한다. 문헌이 아래 설계를 직접 검증했다는 의미가 아니며, 샘플 수·예산액·유의수준·실행 조건을 확정하지 않는다.

### 3.1 추론 대상과 독립 단위를 먼저 선언한다

- 새로운 과제에 대한 일반화가 질문이라면 서로 독립적으로 취급할 수 있는 과제 또는 더 상위의 원천 군집이 기본 단위 후보다. 동일 저장소·데이터 원천의 변형 과제라면 과제 ID가 다르다는 이유만으로 독립이라고 간주하지 않는다. rollout은 과제 안에 중첩된 실행이다. [S2 §2; S3 §5]
- 반대로 특정 고정 과제 집합을 다시 실행했을 때의 성능만 질문한다면 과제 집합에 조건부인 실행 변동을 기술할 수 있다. 두 질문을 하나의 n과 구간으로 섞지 않는다. [S2 §§2, 4.1에 기초한 적용 구분]
- T3의 seed가 같다는 사실만으로 모든 실행이 비트 단위로 동일했다고 단정할 수는 없다. 그러나 task cluster가 하나라는 사실은 바뀌지 않는다. 반복의 무작위성·환경 초기화가 입증되지 않은 현재 기록에서 독립 반복 수를 새로 산정하지 않는다.

### 3.2 고정 예산 estimand는 문장으로 먼저, 수식은 설명용으로

후보 질문: “동일하게 정의한 자원 상한과 제출 규칙 아래, 평가 대상 과제에서 조건 A와 B의 유효한 최종 산출물 점수가 얼마나 다른가?” **아래 고정 예산 estimand는 비교 대상을 명료하게 하기 위해 본 연구가 자체 정의한 제안이며, 관측 결과·선행 문헌에서 검증된 추정량·승인된 새 프로토콜이 아니다.** HAL을 이 정의의 공개 출처로 인용하지 않는다.

\[
\Delta(B)=\mathbb E_{T\sim\mathcal D}
\left[\mathbb E\{Y_A(T;B)\mid T\}
-\mathbb E\{Y_B(T;B)\mid T\}\right].
\]

이 수식에는 관측값을 대입하거나 효과를 추정하지 않았다. 여기서 B는 아직 정하지 않은 자원 계약, T는 목표 과제, 내부 기대값은 허용된 실행 변동을 뜻한다. 목표가 고정 suite라면 외부 기대값 대신 그 suite와 명시된 가중치에 대한 평균을 사용한다. 반복 수가 많은 과제에 자동으로 더 큰 가중치를 주는 pooled run 평균은 다른 estimand다.

- 적용: 조건별 시도·재시도·검색·refine·선택에 든 자원이 어디까지 B에 포함되는지 밝혀야 한다. 실행 예산과 전체 연구개발 비용도 구분한다. [S1 §1, A2; S5 항목 8]
- 반론: 동일 토큰 수는 동일 가격·지연·계산량이 아니며 provider의 같은 reasoning label도 같은 자원을 뜻하지 않는다. [S1 A3 항목 8, A4.2]
- 회피: 성공한 실행만의 평균 비용, 무제한 재시도 후 성공, 숨은 정답을 이용한 best-of-run 선택을 단일 시도 성능과 섞지 않는다. budget-limited policy의 최종 산출물, pass@k, oracle best-of-k는 교환 가능한 지표가 아니다. [S1; S2 §3에 기초한 적용]

### 3.3 짝지은 비교를 보존하되 검정은 아직 잠그지 않는다

기본 비교표는 동일 과제에 대한 A/B 결과와 그 차이를 나란히 두는 방식이 적합하다. 과제 내 반복을 요약한다면 `d_t = mean(Y_A,t) - mean(Y_B,t)`처럼 과제별 차이를 먼저 만든다. 이는 추정량의 예시이지 현재 자료를 재계산하라는 지시가 아니다. [S2; S3]

| 후보 방법 | 적용 조건 | 반론 / 회피 |
|---|---|---|
| McNemar | 독립적인 과제 쌍마다 A/B의 이진 결과 하나씩; discordant pair 정보가 핵심 | 반복 평균은 이진 관측이 아니다. 작은 불일치 수에 큰 표본 근사를 기계적으로 사용하지 않는다. exact conditional 방식은 이 조건이 성립할 때 별도 검토할 후보일 뿐 현재 채택하지 않는다. |
| Wilcoxon signed-rank | 독립 과제별 수치 차이에 순위를 부여할 의미가 있고 대칭성 등 가정을 방어할 수 있을 때 | 평균 효과를 직접 검정하는 것처럼 쓰지 않는다. 작은 이산 표본의 ties·0 차이·exact 구현 조건을 무시하지 않는다. |
| Paired permutation / randomization | 실제 배정 구조 또는 귀무가설 아래 A/B 교환 가능성이 정당화될 때 | ‘짝이 있다’는 사실만으로 교환 가능성이 생기지 않는다. 과제의 중첩 반복을 무작위로 흩어 섞지 않는다. |

근거 위치: S3 §3.2.2, §5. 원고의 현재 해결책은 **McNemar와 Wilcoxon 중 하나를 임의 선택하는 것**이 아니라, 실제 시행되지 않은 확정 검정 문구를 삭제하고 조건부 선택 원칙을 일관되게 쓰는 것이다.

### 3.4 구간과 소표본: 출력 가능성과 타당성은 다르다

- 결과가 생긴 뒤에는 효과 크기와 그 차이의 구간, 과제별 이질성을 우선 보고하는 방향을 권고한다. SD, SE, CI는 구별하고 해당 구간이 task sampling인지 rollout variation인지 명시한다. [S2 §2, Figure 2; S5 항목 7]
- 고정 suite의 stochastic repeat uncertainty에는 과제별 층화 재표집이 후보지만, 과제 일반화에는 과제/원천 군집을 보존한 paired cluster 재표집 등 별도 설계가 필요하다. 후자는 S2 알고리즘의 자동 적용이 아니라 이 검토의 조건부 확장 제안이다. 실제 대응되는 seed·환경 쌍이 있다면 재표집에서도 그 짝을 보존한다.
- 적은 군집·많은 0/1·천장효과에서는 bootstrap이 근거 없는 좁은 구간을 만들 수 있다. all-PASS fixture에서 계산 가능한 퇴화 구간은 모집단 확실성의 증거가 아니다. 현재는 효과 채택 표본 자체가 없으므로 CI를 만들지 않는다. [S2 Figure 6; S3 p.1388; 현행 프로젝트 맥락]
- 필요한 독립 과제 수와 반복 수는 목표 효과/정밀도·과제 간 이질성·과제 내 실행 변동·비용에 대한 근거가 생긴 뒤 정당화해야 한다. 이번 검토는 어떤 최소 n도 지정하지 않는다. nonsignificant를 동등성·무효과로 해석하지 않는다. [S2 §2 및 이 검토의 설계 원칙]

### 3.5 실패 처리: 능력 실패와 측정 실패를 분리한다

**모든 오류를 일괄 0점으로 바꾸는 방식도, 오류를 모두 제외하는 방식도 채택하지 않는다.** 인프라 실패를 능력 실패처럼 처리할 위험은 S1 A3 항목 5에서 직접 확인된다.

- 제안 A — 유효한 평가기 아래 에이전트가 허용 예산 내 유효 결과를 내지 못했다면, 성공=1/그 외=0으로 정의한 종단 간 endpoint에서는 실패=0이 될 수 있다. 부분점수 endpoint에는 그 규칙을 그대로 일반화하지 않는다. 중간 도구 오류가 회복되었다면 최종 실패와도 구분한다.
- 제안 B — 평가기 crash, 잘못된 oracle, 결과를 판단할 수 없는 로그 손실은 **점수를 알 수 없는 측정 문제**다. capability 분석에서 임의 정답·0점으로 복원하지 말고 무효/미확인 상태와 이유를 보존한다. 시스템 가용성을 별도로 평가한다면 그 endpoint의 실패로 기록할 수 있으나 능력 점수와 혼동하지 않는다.
- 제안 C — 향후에는 모든 예정/시작 실행의 분모, 채점 가능/불가능, agent 실패, timeout, infrastructure 실패, 제외·재시도 사유와 비용을 조건별로 공개한다. 성공·정상 완료만 남긴 분석은 선택된 하위집합의 민감도 분석임을 표시한다. 실패 원인에 따른 사후 제외는 조건 간 비교 자체를 편향시킬 수 있다. [S1; S4 Challenges 1–2; S5 항목 8]
- 현재 결정: T1-prime 격리를 유지한다. ‘intention-to-run’이라는 이름을 붙이는 것만으로 42건의 evaluator crash가 유효한 효능 관측으로 바뀌지 않는다. 결측 최선/최악 경계도 유효 평가 설계를 대신하지 않으며 이번 lane에서는 계산하지 않는다.

### 3.6 탐색·확인과 두 수준의 중단

- 기존 진단·문헌 탐색·검정 검토는 탐색적 연구로 명시한다. 미래 확인 연구에서는 결과를 보기 전에 주질문, 비교, endpoint, 분석 단위, 제외·재시도·중단 규칙을 명료하게 기록하고 승인받는 방향만 제안한다. 복수 비교는 전체 목록과 다중성 처리를 밝혀야 한다. [S4; S3 §5]
- 실행 내부의 중단은 B·timeout·허용 iteration 같은 정책의 일부다. 연구 전체의 표본 수집 중단은 별도의 규칙이다. 더 유리한 결과가 나올 때까지 반복하거나 유의해지는 시점에 중단한 자료를 고정 설계처럼 해석하지 않는다. [S1 A2; S4 Challenge 1]
- 인프라 장애 때문에 멈추는 것은 연구 무결성을 위한 운영 조치일 수 있다. 멈춘 이유·시점·영향 조건·그때 이미 본 결과를 기록하고 이후 재개분을 조용히 합치지 않는다. 순차 검정이나 confidence sequence는 가능 후보이나 이번 조사에서 원문 검증하지 않았으므로 승인된 방법으로 제시하지 않는다.
- 반론: 과도한 사전 고정은 개발 중 오류 수정을 막을 수 있다. 회피: 개발은 계속 탐색으로 허용하되 수정 이력과 평가 자료 사용 이력을 보존하고, 탐색을 소급해서 확인 연구로 바꾸지 않는다. [S4 Challenges 1–3]

## 4. 원고에 바로 사용할 수 있는 문구

### 현재 결과와 제한

> 본 연구의 현 단계에서는 평가도구의 결정론적 검사 결과와 ARGO의 효과를 구분한다. Stage 0에서 16개 과제 채점기의 정상·손상 fixture 검사 96건과 런타임 정책 검사는 통과하였으나, 이는 통합 실행기의 종단 간 인증이나 ARGO의 과제 수행 효과를 의미하지 않는다. 효과 추론에 채택된 실행은 아직 없다. 따라서 효과 크기, 신뢰구간 및 통계적 유의성을 제시하지 않는다. 불확실성의 발생원을 구분하는 통계적 논의는 Agarwal 등의 과제·반복 모형을 참고한다 [@agarwal2021statistical].

### 기존 기록의 해석

> T3의 120회 실행은 하나의 과제와 내부 seed 0에 집중된 진단 기록이므로, 조건별 40회를 독립 과제 표본으로 해석하지 않는다. 또한 T1-prime의 48건 중 42건에서 발생한 평가기 crash는 측정 타당성 문제로 격리하며 이를 임의의 정답 또는 정상 실패로 대체하지 않는다. 이 기록은 개선할 평가 절차를 식별하는 데 사용하되 ARGO 효과의 확인적 근거로 사용하지 않는다. 관측 의존성의 문제는 Dror 등의 §5를 참고한다 [@dror2018hitchhikers]. 평가기 장애 기록의 격리와 미확인 점수 보존은 해당 문헌의 실험 결과가 아니라 본 연구의 증거 채택 결정이다.

### 향후 방법론 — 확정 계획이 아님

> 향후 비교에서는 목표 과제 집합과 자원 제약을 먼저 정의하고, 동일 과제에서 얻은 조건 간 차이를 기본 비교 대상으로 검토한다. 고정 예산에서의 조건 간 기대 점수 차이는 비교 대상을 명료하게 하기 위해 본 연구가 자체 정의한 추정 대상의 제안이며, 관측된 효과나 선행 문헌에서 검증된 결과가 아니다. 과제 간 일반화와 동일 과제의 반복 실행 변동을 구별하며, 결과 변수와 관측 구조가 정해진 뒤 그 가정에 맞는 구간 추정 및 검정 방법을 선택한다. 본 논문은 McNemar 또는 Wilcoxon 검정을 이미 수행한 것으로 기술하지 않으며 표본 수와 새로운 실험 프로토콜도 확정하지 않는다. 기존 자료를 이용한 탐색과 미래의 결과 비열람 상태에서 정한 확인적 분석을 구분하고, 제외·재시도·중단 및 계획 변경 이력을 보고한다 [@dror2018hitchhikers; @agarwal2021statistical; @nosek2018preregistration].

## 5. 공개 인용용 Citation-ready BibTeX — 3건

공개 참고문헌에는 `agarwal2021statistical`, `dror2018hitchhikers`, `nosek2018preregistration`만 전달한다. HAL의 기존 후보 키 `kapoor2026hal`은 철회한다. 최종 학회 PDF 미열람·v1 버전 한계 및 원문은 S1과 보존 폴더에 비공개 검토 이력으로 남긴다. S5 체크리스트도 비공개 보고 점검 자료로 유지하되 이 공개 통계 참고문헌 묶음에는 넣지 않는다.

```bibtex
@inproceedings{agarwal2021statistical,
  title = {Deep Reinforcement Learning at the Edge of the Statistical Precipice},
  author = {Agarwal, Rishabh and Schwarzer, Max and Castro, Pablo Samuel and Courville, Aaron C. and Bellemare, Marc},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {34},
  year = {2021},
  url = {https://proceedings.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html},
  note = {Selected passages read in Sections 2--4.2, PDF pages 2--7. Retained-copy reread: Section 2, pages 2--3; Section 4.1, pages 5--6, including Figure 6 caption and discussion, not a numerical audit of the plot. Official proceedings verified 2026-09-05.}
}

@inproceedings{dror2018hitchhikers,
  title = {The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing},
  author = {Dror, Rotem and Baumer, Gili and Shlomov, Segev and Reichart, Roi},
  booktitle = {Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year = {2018},
  month = jul,
  pages = {1383--1392},
  publisher = {Association for Computational Linguistics},
  doi = {10.18653/v1/P18-1128},
  url = {https://aclanthology.org/P18-1128/},
  note = {Selected passages read in Sections 2.1, 3.2.2, 3.3, 4 and 5; retained-copy reread of matched tests and selection on pages 1387--1388, dependence on page 1390 (PDF pages 5--6 and 8). Verified 2026-09-05.}
}

@article{nosek2018preregistration,
  title = {The preregistration revolution},
  author = {Nosek, Brian A. and Ebersole, Charles R. and DeHaven, Alexander C. and Mellor, David T.},
  journal = {Proceedings of the National Academy of Sciences},
  volume = {115},
  number = {11},
  pages = {2600--2606},
  year = {2018},
  doi = {10.1073/pnas.1708274114},
  url = {https://doi.org/10.1073/pnas.1708274114},
  note = {Published online 2018-03-12; issue date 2018-03-13. Selected full-text passages retained and reread at https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/, sections s3--s8 and s20, accessed 2026-09-05. PDF retrieval failed in this retention pass; use HTML section locators, not newly verified PDF page claims.}
}
```

## 6. 인계 및 미검증 경계

- 초안에 반영할 핵심: 효과 추론 유보, 과제/반복 구별, paired 비교의 조건, 불확실성 발생원, 예산 estimand, 측정 실패 격리, 탐색/확인과 중단 구별.
- 제외한 작업: raw receipt 확인·기존 p-value 재계산·표본 수 선택·새 preregistration 잠금·확정 sequential 방법·통합 runner 인증.
- 경험 검색 분류: 과거 기억의 네이티브 중단 경계는 현행 brief로 `directly_supported`; 과제/반복 구분은 `near_match_only` 탐색 단서로만 사용했다. 과거 메모의 고정 과제 수·일괄 오류 0점 규칙은 이번 범위에 대한 근거가 `insufficient`하여 재사용하지 않았다.
- 열람 제약: 일부 초기 web 검색 응답은 비어 있었고, 구형 NeurIPS 링크는 실패했다. 공식 PDF 경로로 복구했다. HAL 최종 PDF 접근 실패는 원문 v1 열람으로 대체하고 버전 차이를 공개했다. PNAS 출판본은 대학 호스팅 PDF로 읽고 출판사 서지와 대조했다. 미열람 자료를 원문 확인 자료에 포함하지 않았다.
- 중단 판단: 이 다섯 자료로 초안의 과장·검정 모순·표본 단위 문제를 교정할 근거가 충분하다. 포괄적 체계적 문헌고찰이나 보편적 SOTA 선정은 수행하지 않았다.

## 7. 원문 보존 인계 — 2026-09-05 KST

- 보존 폴더: `.planning/2026-09-05-thesis-evidence-draft/statistics-sources/`.
- `README.md`: 문헌별 실제 부분 독서 범위, 페이지/section/추출문 행 locator, 미열람 범위, 다운로드 실패와 대체 본문 기록.
- `manifest.json`: 원문 bytes의 SHA256·크기·URL·HTTP 상태·취득 시각 및 구조화된 독서 범위. `SHA256SUMS`: 보존 파일의 무결성 확인용 목록. 해시는 출판 인증이나 이전 열람과의 동일성 인증이 아니다.
- `references.bib`: §5의 공개 인용용 BibTeX 3건과 일치한다. HAL은 비공개 검토 기록과 원문으로만 남겼다. §4에서 HAL 인용을 제거하고 예산 estimand를 본 연구의 자체 정의·미관측 제안으로 명시했다.
- PNAS는 대학 PDF의 HTTP 403 및 PMC PDF 경로의 HTTP 200 다운로드 준비 HTML을 실패 증거로 보존하고, 정상 수신한 PMC 논문 HTML을 본문 근거로 사용한다. HTTP 200만으로 PDF 성공을 선언하지 않았다.
- 이번 추가 작업에서도 원시 실험, 네이티브 구현, 테스트, 신규 표본 수·실험계획 확정 및 외부 위임은 수행하지 않았다.
