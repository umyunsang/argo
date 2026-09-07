# Fable 5.1 수정본 재검토 결과

## 판정

**READY_FOR_TASK_QUALIFICATION — 조건부로 과제·프로토콜 구체화 진행 가능.**

Fable 5.1 / xhigh의 새 세션이 `ee7e0fdaf23353c094b1a872b564d82fa234bfc7`을 재검토했다. 개념적으로 치명적인 차단 사항은 없다고 판정했다. 기존 F1–F14 중 12개는 설계 수준 해결, F3/R1–R2 집행과 F7/의무 gate 집행은 부분 해결이다. 이는 실증 종결이 아니다. 인증 task·runnable arm·통합 효능은 여전히 0이고 P0/P1/P2 모두 미승인이다.

원검토 두 파일의 SHA, 요청 SHA와 입력 22개를 커밋 blob에서 재도출했다. 두 predecessor와 검토 commit의 조상 관계도 확인했다. 원문 확인은 저장된 Prime/Arbor 특정 span만이며 전체 논문 재독이나 최신 문헌 조사는 아니다.

## 타당하다고 재확인된 반박

- UNKNOWN 발생 programme block을 primary에서 자동 제외하면 post-treatment 선택 편향이 생길 수 있다.
- Prime의 nanoGPT 잡음 관측은 event 없는 G−C=0을 입증하지 않는다.
- 해시 commitment는 변경 탐지이지 비공개·무노출 보장이 아니다.
- 기능 호출 로그는 발화 관측이지 표현·계산·context의 인과 분리가 아니다.
- 두 시작으로 안정된 power가 확보되지 않는다. C/G 또는 최저 비용 prototype을 리뷰 권고로 고정하면 안 된다.
- 양의 효과와 최소유용효과(MUE) 이상의 효과는 다른 판단이며 사전 결정표는 모든 경우를 다뤄야 한다.

## 다음 과제별 프로토콜에서 닫을 사항

1. **장치 구현 권한:** 허용 코드·명세 경로, owner, native 분리와 비자동 승격 규칙을 사용자에게 확인한다. 문서 수준 task qualification은 지금 가능하다.
2. **강제 점검 지점:** R1 launch와 artifact lock에서 C/G에 같은 guard를 적용한다. B에도 공통 실행권한·예산 gate는 적용한다. 열린 REPL/직접 실행 우회가 탐지되는지는 실제 capability·census로 확인해야 한다.
3. **R1/R2 분류와 lineage:** 자동 사전 분류와 사후 전수 감사를 함께 쓴다. 새 학습/선택용 평가를 R2로 세탁하지 않는다. 사전 승인 없는 실행을 사후 분류로 정당화하지 않는다.
4. **MUE·선택 주체:** P1 arm 대비를 보기 전에 MUE/도출 규칙을 commit한다. 작업용 primary는 agent가 단일 artifact를 lock하는 방식이다. 미lock 처리·fallback은 task별로 실행 전에 하나로 고정한다.
5. **결측·계보·비용:** no-lock, 중간 launch UNKNOWN, scorer 실패와 최종 점수 관측을 분리한다. P0 ancestry는 개발 측으로 분리하고 P2에서 제외한다. 각 단계의 invalid/retry 규칙, latency/UNKNOWN/gate/R2 census를 명시한다.

## 재검토 처방의 추가 한정

- “실행 전 분류”가 반드시 사람의 매회 판단은 아니다. 자동 preflight는 자율 실행과 양립한다. 사후 lineage만으로 권한 경계를 대체하지 않는다.
- adapter 자체는 자기 경로만 막는다. 직접 ORX 실행의 완전 탐지나 신뢰 경계는 아직 검증되지 않았다.
- 모든 R2 근거를 선택 노드에서 금지하지 않는다. 새로운 selection-performance score는 R1 lineage가 필요하지만, 공개 source·data 진단·허용된 재계산은 typed supporting evidence가 될 수 있다.
- arm당 채점 호출 1회가 비차등 결측을 보장하지 않는다. no-lock/no-artifact도 모든 배정의 결과 회계에서 빠지지 않는다.
- Arbor ablation의 81.82/63.64/54.54%는 저장 표에 있다. 그러나 첫 Fable의 n=11과 재검토의 n=22는 확인한 원문에 명시되지 않았다. 둘 다 검증된 표본 수로 사용하지 않는다. 문서 변경이 문자 그대로 “삭제 없이 추가만”이라는 주장도 title/status 교체가 있어 정정했다.

전체 N1–N10의 처리와 task-bound 종결 근거는 `task-qualification-requirements.json`에 있다. 범위 제안은 `apparatus-scope-decision.json`이며 아직 승인되지 않았다. 이번에는 새 일반 설계를 반복 작성하거나 재검토를 추가하지 않는다. 다음 검토는 실제 공개 ML programme에 묶인 **P0 프로토콜 검토**다.

원검토와 검토된 ISD/RCC는 그대로 보존했다. 현재 문서 포인터와 후속 조건만 연결한다. 이 후속 조건 자체가 Fable에 다시 검토됐다는 주장은 하지 않는다. 새 apparatus code·실험·설치·원고·native 변경·push는 없다.
