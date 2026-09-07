# 공개 ML 자율연구 과제 구체화 — 원문·코드·권한 통합

## 현재 성과

- 기존 Prime Agent의 세션/REPL/RLM에서 원문, 공개 코드, 실제 인터페이스, 정적 장치를 독립 파일로 병렬 처리했다. 별도 supervisor나 네이티브 변경은 없다.
- MLE-bench/PaperBench 기존 원문과 MLAgentBench v2, 1GC-7RC v2, AgentHPOBench v1, Agent Laboratory v2를 읽은 범위·원본 해시로 연결했다. MLAgentBench는 root가 추출 텍스트 전체 LF1–2374를 읽었다.
- MLA/HPO pinned 공개 코드 1,186개 Git blob을 비교했고, 감사에서 읽은 101개 코드/라이선스/명세 파일만 별도 재현 capsule에 넣었다. 데이터·모델·정답 payload는 넣지 않았다.
- source audit106개 파일 확인, MLA46개 exact quote, HPO58개 LF range를 재도출했다. Prime/ORX source excerpt12개는 terminal-LF hash 관례를 명시했다.
- 공통 산출물 byte-binding fixture는 commit `ccdbf3df0a23169637711ea363262ced89aaf2df`에서 7 tests와 clean clone `npm run check`를 통과했다. 중복 guard 제거 시 실패하는 행동 검증도 보존했다.

## 중요한 과학적 결과: 공개 benchmark를 그대로 쓰면 비교가 달라진다

MLAgentBench는 실제 ML iteration을 제공하지만, CIFAR starter는 test label을 읽고 매 epoch test score를 출력한다. 논문 예시에는 호출되지 않는 dropout edit와 accuracy 감소를 개선이라고 부르는 기록, 실행 관측 없이 최종 파일을 성공으로 보고하는 경우도 있다. 원문/코드 검토는 이 문제를 동기화하며 local efficacy를 만들지 않는다.

AgentHPOBench는 predefined HPO menu를 조정하며 별도 hidden test를 두지 않는다. 또한 읽은 논문은 final fifth 결과, pinned strict runner는 best metric 선택이므로 같은 outcome으로 합치지 않는다. California Housing 등 upstream task만 적절히 분리할 후보가 있다.

1GC는 실제 방법 경쟁 후보를 주지만 test-visible 개발·scored checkpoint 선택을 그대로 계승할 수 없다. 논문에 적힌 정확한 GitHub URL은 API와 public page 모두 404였다. 해당 code-reuse 경로는 아직 확인되지 않았으며 '없다'고 단정하거나 다른 fork를 대신 고르지 않는다. PaperBench의 전체 LLM rubric 복제 체계도 이번 작은 deterministic P0와 동일한 평가물이 아니다.

## 과제 선택은 아직 하지 않았다

복원한 후보는 House Price(`home-data-for-ml-course`), Spaceship Titanic, California Housing, CIFAR-10이다. Kaggle 두 과제의 파일 metadata 접근은 이미 확인했다. 계정은 access dependency이지 탈락 사유가 아니다. source baseline 미완성, scorer row/ID 검증, public split 복원, group/entity leakage, 라이선스와 전체 runtime/cost를 비교한다. 최종 추천과 중요한 제외/범위 선택은 사용자 확인 전 미확정이다.

공개 Kaggle data/rules URL은 현재 받은 HTML에서 제목/메타만 보여 주었다. 전체 약관을 읽거나 동의한 것으로 기록하지 않는다. 데이터 다운로드·제출은 0이고 토큰은 별도 저장·전달하지 않았다.

## 실행 준비와 효능의 경계

7 static tests는 process-local lock-ID와 실제 bytes/score binding 사양만 검증했다. campaign-wide/durable lock, trusted host isolation, complete launch census 또는 task score를 검증하지 않았다. ORX local은 no-login 실행 경로가 있지만 보안 격리나 timeout/idempotency/일반 artifact enumeration을 보장하지 않는다. task-bound trusted scorer와 종료 조건은 여전히 별도 필요하다.

apparatus 코드/모의 검증 승인과 실제 모델·학습·평가/설치/공개 범주 승인은 유지한다. 특정 P0/P1/P2 run, 수치 예산, 설치/공개 대상은 아직 고정되지 않았다. 검증 전 native 변경 금지, ResearchDone 전 원고 금지, 소모 run 비재실행은 유지한다.

## 다음

1. 네 후보 비교의 24개 source 파일·43개 exact quote를 확인했다. House Price(`home-data-for-ml-course`)를 P0 후보로 추천하며 Spaceship Titanic을 차선으로 보존한다.
2. `p0-task-selection-proposal-v1.json`의 연구 적합성/평가 위험/자원 부담을 사용자에게 제시하고 task 선택을 받는다. 현재 task는 미선택이다.
3. 선택된 P0의 terms/data ancestry, train/dev/hidden custody, metrics/MUE timing, agent lock/no-lock, 실패/복구·전수 비용과 고정 환경/명령을 닫는다.
4. 정확한 숫자 실행 계약을 task-bound 검토한 뒤 실제 실행으로 넘어간다. 더 많은 일반 설계 review는 다음 단계가 아니다.
