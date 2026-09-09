# 지속적 자율 ML 연구 하네스 연구 설계 v1

상태: 독립 검토용 사전 설계. 실제 실험·native 구현·프론티어 모델 학습 없음.

## 1. 목적과 가설

외부 프론티어 모델의 가중치를 고정한 상태에서, 지속 실행·프로그램적 문맥·근거에 따른 재계획을 연결한 연구 하네스가 강한 기존 실행 방식보다 제한된 ML 연구를 잘 수행하는지 평가한다. 논문은 방법과 검증 결과를, ARGO는 검증된 연구 loop를 실제 수행하는 prototype을 산출한다. 단순한 graph 유무나 경험 전이만의 연구가 아니다.

주 질문: **같은 모델과 연구 예산에서, 검증된 산출물과 근거를 이어받아 다음 연구를 계획하는 하네스가 더 나은 최종 모델을 만드는가?**

주 가설 H1은 주 모델 M1에서 통합 연구 하네스 R의 평균 검증 산출물 효용이 강한 기존 하네스 B보다 크다는 것이다. 두 번째 모델 M2에서 같은 차이가 유지되는지는 사전 명시된 보조 이식성 질문이다. 양성·null·negative·실행 실패를 모두 보고한다. 결합 자체, node/문서/실험 수, 오래 켜 둔 시간을 신규성·연구 성과로 주장하지 않는다.

## 2. 원문 근거와 설계 선택

Prime Agent는 실행·REPL/RLM·외부 상태와 모델 주도 전략의 공통 기반, Scroll은 원본 기록의 주소화·선택적 조회, HoH는 artifact/evidence를 보존하며 재계획하는 절차, RecEvolve는 실제 ML 가설/구현/평가 loop, HarnessDev는 개발과 별도 평가를 분리하는 하네스 개선 관점이다. 다섯 보존 원문과 이전 read receipts가 evidence manifest에 연결된다.

HoH의 프로젝트 개선과 HarnessDev의 하네스 개선은 다르다. 본 실험에서 R 후보를 만드는 개선은 개발/선택 자료에서 끝내고 평가 전에 동결한다. 평가 run 안에서는 연구 대상인 ML 파이프라인·가설·판단만 바꾼다. 프론티어 가중치, 하네스 코드·system policy·scorer는 바꾸지 않는다.

대안은 (a) 모델의 자유로운 도구/위임 전략을 지원하는 강한 B, (b) 동일 기반에 연구 phase와 context view를 명시하는 R, (c) 자유로운 online harness 자기수정이다. (c)는 현재 결과와 개선자 변경의 원인을 섞으므로 주 실험에서 제외한다. graph 형식·skill 압축·meta 깊이는 주 처치로 고정하지 않는다.

## 3. 주 과제와 표집

주 실험은 **공개 tabular classification 모델 개선 프로그램**이다. agent가 전처리·특징·모델·하이퍼파라미터와 다음 실험을 선택해 실제 학습·평가를 반복한다. 연구 대상은 이 작업을 수행하는 하네스이며 새로운 프론티어 모델, 일반 과학적 발견, 산업 추천 시스템을 재현하는 주장이 아니다.

OpenML-CC18 suite 99의 72개 task/dataset metadata를 회수했다. 500–20,000행, 원본 특징 수(목표 포함) 100개 이하로 한정한다. MiceProtein·GesturePhaseSegmentationProcessed·ozone-level-8hr은 반복 주체/연속 자료 문제로 제외한다. mfeat views, NASA MDP, Wisconsin breast 데이터는 보수적으로 family로 묶고 하나만 선택한다. 정확한 목록과 사유는 `task-roster.json`에 있다. 상세 ancestry·라이선스·실행 적합성은 아직 metadata 이상의 검증이 아니다.

고정 salt `ARGO-LH-20260909-v1|data_id`의 SHA-256 순서로 family당 하나를 남기고, 첫 4개는 개발, 다음 4개는 선택, 다음 20개는 주 평가에 배정한다. 나머지 11개는 outcome 노출 전의 적합성 확인에만 쓰는 예비 목록이다. 논문·과거 House Price P0 계보는 개발 측 노출로 기록하며 주 평가에 재배정하지 않는다. benchmark 성능이나 agent outcome을 보고 과제를 골라내지 않는다.

주 대상은 고정한 20개 과제의 유한 benchmark 평균이다. 이들을 모든 과학 분야의 무작위 표본이라고 하지 않는다. detailed ancestry 확인에서 family 중복이 드러나면 첫 평가 outcome 이전에 roster를 새 버전으로 다시 동결한다. 이후 실패한 과제는 예비 과제로 교체하지 않는다.

각 OpenML task의 repeat 0/fold 0을 outer test로 고정한다. outer train의 80%/20% stratified split(seed 20260909)을 내부 train/dev로 쓴다. 최종 제출 코드를 outer train 전체로 한 번 refit한 뒤 outer test에서 평가한다. outer split의 표준화를 활용하지만 이는 OpenML 공식 10-fold leaderboard protocol 그대로가 아니다.

## 4. 두 조건의 정확한 차이

공통: 동일 model/reasoning, 기본 연구 지시, train/dev 자료·원문 corpus·기본 예제, 파일/코드/실험 tools, persistent execution, RLM 위임 권리, 기록 조회, 검증·예산·최종 선택 규칙. B도 실패 기록을 읽고, 도구와 자체 dependency checks를 만들며, 팀을 구성할 수 있다. B가 자발적으로 R와 유사한 방법을 쓰는 것을 막지 않는다.

**B: expressive baseline.** 고정된 Prime substrate와 강한 연구 지시 아래 모델이 직접 도구·위임·문맥·계획을 구성한다. host가 연구 phase/역할 교대를 강제하지 않는다. 고정 기본 prompt와 같은 자료의 개발 튜닝 후보를 선택 과정에 포함한다.

**R: evidence-steered research harness.** 같은 substrate에서 다음 고정된 운영 정책을 쓴다.

1. Planner는 현재 artifact, 이전 개발 관측·실패, 남은 자원에서 다음에 구별할 질문·실험과 보존할 사실을 정한다.
2. Investigator는 같은 tools로 분석·구현·실험을 수행하고 candidate artifact를 남긴다. 외부 실험은 ORX 식별자와 연결한다.
3. Assessor는 고정 candidate와 dev 실행 근거를 읽어 성과·실패·미확인·다음 필요 근거를 구분한다. 자신이 만든 설명이나 critic 합의가 독립 scorer를 대신하지 않는다.
4. Context view는 현재 질문에 맞는 원문·기록의 주소와 필요한 payload만 구성한다. 원본은 공통 store에 남고 B도 같은 원문에 접근할 수 있다. 두 번째 REPL이나 run registry를 만들지 않는다.
5. 남은 예산에서 계획을 갱신하거나 현재 artifact를 최종 선택한다. 정체·negative 결과에서는 다른 질문을 선택하거나 중단할 수 있으며 새 기능/성능 상승을 매회 강제하지 않는다.

R의 생성 context, 추가 role calls, retrieval, validation과 모든 descendant 비용이 R 예산에 들어간다. 모든 role은 같은 고정 M1/M2를 사용한다. 역할 분리는 모델 오류 독립성을 뜻하지 않는다. R−B는 이러한 운영 package의 효과이며 순수한 graph·context·팀 구성 하나의 인과효과가 아니다.

## 5. 하네스 개발·선택과 동결

각 family(B,R)에 같은 개발 상한을 준다: 후보 최대 3개, 개발 데이터 4개, 선택 데이터 4개, family별 총 모델 token 1.5M·CPU 40core-hours·wall 24h. 이 수치는 설계 상한이며 측정 비용이나 실행 승인 아님.

B 후보는 강한 기본 prompt, 개발 기록으로 개선한 연구 지시, 개발에서 만든 자율 도구사용 지침이다. R 후보는 기본 연구 cycle, context-view 조정, 개발 실패 근거로 한 번 개선한 role/policy 지침이다. 임의 후보 증식·target 결과 기반 후보 추가를 금지한다. 후보 생성자도 고정 모델을 사용한다. 모든 변경 diff·trace·생성 비용을 보존한다.

각 후보는 선택 과제마다 한 번 실행한다. 유효 산출물의 아래 U 평균 최대 후보를 선택한다. 동률(1e-6 이내)은 실제 총 token이 적은 후보, 다시 같으면 미리 정한 후보 ID순으로 고른다. 검증 불능의 selection scorer 상태가 남으면 선택을 확정하지 않는다. 두 family 각각 선택 후보를 고정하고 primary 결과에 접근하기 전에 코드·prompt·tools·context policy·model settings·image·source corpus·scorer·roster hash를 포함한 manifest를 작성한다.

이 실험은 **예산이 제한된 개발 절차로 선택된 B와 R의 배포 성과**다. 최선의 모든 하네스와 비교하거나 developer search가 없는 순수한 손작성 구조 효과라고 하지 않는다. 개발 비용은 배포 비용과 구분해 함께 보고한다.

## 6. 모델·자원·반복

제안된 M1은 `openai-codex/gpt-5.6-sol`, M2는 `openai-codex/gpt-5.5`, reasoning high다. 현재 CLI registry에 존재함을 확인했으나 계정 접근·실행 가능성을 확인한 것은 아니다. 각 모델에서 서로 같은 request settings와 입력 view 한도를 사용한다. aliases의 실제 resolved version/fingerprint/실행일을 기록한다. 다른 provider로 조용히 바꾸지 않는다.

배포 episode 상한: root+descendants 합계 120,000 normalized tokens(비cache input+cache input+output, reasoning은 provider 정의에 따라 한 번만), active input 64K/호출, output 8K/호출, CPU 120core-min, wall 90min, concurrent compute 2, 메모리 8GiB, dev score 호출 최대 12회(기본 baseline 포함), final refit 1회. final refit/최종 분석에 CPU 15core-min·wall 10min을 예약해 남은 상한에서만 dev 작업을 허용한다. CPU와 wall/token을 서로 교환하지 않는다.

이는 **제안된 집행 목표**다. 요청별 reserve/admission, subprocess limit 및 provider usage 정규화를 실제 apparatus에서 검증하기 전 hard-cap 구현 완료라 부르지 않는다. 관측 불명 usage·미확정 외부 launch는 중단하고 기존 run과 대조하며, 맹목 재시작하지 않는다. 초과·중단의 비용은 제거하지 않는다. provider 자체의 fingerprint 변경이 block 사이 발견되면 새 block을 시작하지 않고 epoch를 별도로 고정한다.

M1: 20과제×2조건×2반복=80episodes. M2는 test roster 앞 10과제에서 2조건×2반복=40episodes의 보조 이식성 평가다. 총 120 target episodes, 최대 14.4M deployment tokens와 240 CPU-core-hours다. 개발·선택·scorer·실패 비용은 별도 더하며 이 수를 전체 비용이라고 하지 않는다. dollar 추정은 실제 provider 단가/구독 shadow price를 실행 전에 기록하며 무료로 간주하지 않는다.

과제마다 네 개 fresh run을 두 묶음(각 2반복)으로 만들고, B/R label을 block 안에서 무작위 배정한다. 실행 순서와 host/time slot도 무작위화한다. task의 네 run 간 연구 기억·cache artifact를 공유하지 않는다. 모델의 같은 seed가 같은 궤적을 뜻한다고 가정하지 않는다. 입력 자료/환경 캐시는 두 조건에 같은 준비 상태로 제공하고 provider prompt-cache 사용량은 별도로 기록한다.

## 7. 누수·출처·재현성 경계

trusted host/orchestrator/scorer와 evaluated worker를 구분한다. worker와 그 REPL·생성 코드가 볼 수 있는 mount에는 train/dev와 허용 corpus만 둔다. test labels, scorer code/credentials, 다른 run outputs, Docker socket, host home은 노출하지 않는다. worker의 직접 네트워크는 끄고 LLM broker와 corpus search만 허용한다. 이 구성은 연구 apparatus의 제안이며 기존 same-UID 파일 권한만으로 격리를 증명하지 않는다.

주 실험 corpus는 공개 원문/API 자료를 먼저 동결한 whitelist다. 검색 질의는 agent가 자율적으로 하되 benchmark 결과·test labels·해답 구현·OpenML runs API로 이어지는 접근은 제공하지 않는다. Exa/ORX는 corpus를 준비하는 데 사용하고, episode의 검색은 같은 고정 자료를 조회한다. 이 결과를 unrestricted live-web 연구 능력으로 확대하지 않는다.

공개 데이터가 LLM 사전학습에 들어갔을 가능성은 제거했다고 주장하지 않는다. 평가는 이번 개발/선택 과정에서 보지 않은 task라는 뜻이다. runtime leakage, 개발→평가 누수, 사전학습 노출은 별개로 기록한다. 각 run은 새 context이며 이 planning 대화·target manifest·과거 연구 결과를 주입하지 않는다.

각 row는 task/data/version/split·code/environment·model/request·harness·선택 artifact hash·run IDs·resource·status·score를 연결한다. test 결과는 전 과제의 final selection lock 후 공개한다. 평가자가 보는 파일에서는 arm/creator 명칭을 제거하고 candidate와 evaluation manifest만 제공한다. 명칭 가림은 자기검증 오류나 접근 격리의 증명이 아니다.

재현성은 고정 자료·코드·명령·환경·설정·원시 결과로 재실행할 수 있다는 뜻이며, 외부 LLM의 비트 단위 동일 응답을 보장하지 않는다. 본문 publication claims에는 실제 읽은 원문과 허용된 수치만 사용한다.

## 8. 최종 선택·결과 정의

공통 초기 baseline은 imputation + unknown-safe categorical encoding + seeded random forest100trees이다. 학습/내부 평가 비용을 episode에 포함하며, 시작 시 기본 artifact identity를 fallback 선택으로 등록한다. agent는 dev 근거로 다른 verified code hash를 명시적으로 lock할 수 있다. deadline까지 새 lock이 없으면 초기 선택을 유지한다. highest-dev/archive-best를 평가자가 대신 선택하지 않는다.

Primary outcome **U(검증 산출물 효용)**는 독립 final refit/scoring이 완료된 유효 artifact의 balanced accuracy∈[0,1]이다. agent 원인의 무산출·무효 artifact·명시적 protocol violation은 U=0으로 정의한다. 이는 존재하지 않는 모델의 정확도를 대입하는 것이 아니라 예산 내 유효 산출물을 낸 효용의 정의다. 성공률과 유효 모델만의 정확도를 함께 보고한다.

trusted scorer failure, receipt 소실 또는 원인이 미확정된 failure는 U unknown∈[0,1]이다. 임의 0으로 만들지 않는다. primary에 하나라도 unknown이 남으면 mean-effect의 worst/best bounds를 보고하고 확증 significance/실용적 우위는 INCONCLUSIVE로 남긴다. failed task를 다른 task로 교체하지 않는다. 같은 immutable candidate에 대한 scorer 기술 재시도는 양 arm에 동일하게 최대1회, 새 모델 선택/학습은 허용하지 않는다.

모든 배정·중단·실패·반복·재시도 비용은 분모/ledger에 남긴다. failure cause 분류는 arm label을 숨긴 고정 규칙과 원시 receipt에 따라 수행한다. 사람이 사후 실패 원인을 바꾸면 변경·근거를 공개하고 primary와 sensitivity를 나눠 보고한다.

## 9. 통계·유의성·판정

M1이 유일한 confirmatory comparison이다. 각 task에서 반복2개의 U를 arm별 평균하고, D_t=mean(U_R)−mean(U_B)를 계산한다. 주 추정량은 20 task의 동일 가중 평균이다. randomization 단위는 dataset/source-family block이며 2반복을 별도 독립 n으로 늘리지 않는다.

양측 α=0.05의 paired block sign-flip randomization test(2^20 label assignments)를 사용한다. 효과 크기와 task-cluster bootstrap95% interval(10,000 resamples,seed20260909)을 함께 보고한다. bootstrap은 finite20개 선정 suite에 대한 불확실성 요약이고 모든 ML domain 추론이 아니다. M2와 세부 진척/비용/실패 지표는 사전 지정된 보조 결과이며 유의성 탐색으로 primary를 대체하지 않는다.

실용적 차이 기준은 평균 U +0.02(2 points)로 제안한다. 후보 결과를 보기 전 정한 benchmark-value 판단이지 원문 효과나 local variance에서 가져온 수치가 아니다. 우위 판정은 p<.05만으로 하지 않는다: primary complete, CI lower>0.02일 때 이 고정 suite에서 실용적 우위를 지지한다. CI upper<−0.02면 유해한 차이, CI 전체가[−0.02,0.02] 안이면 선택한 정확도 수준에서 작은 차이, 나머지는 실용적 판정 불확실이다. unknown 존재는 먼저 INCONCLUSIVE다. 경제적 우위는 별도 전체 비용 결과가 있어야 한다.

표본 수20은 실제 자원과 고정 benchmark 폭의 설계 선택이다. 80% power를 확보했다고 주장하지 않는다. 첨부 normal-approximation sensitivity에서 trueΔ=.02, paired SD .03/.05/.10이면 검정력은 약 .85/.43/.15다. 이는 0 null 검정의 단순 예시이며 CI lower>.02 criterion의 power가 아니다. 실제 분산도 아니다. 평가 중 p나 효과를 보고 표본 수를 늘리지 않는다. 불확실하면 후속 독립 연구로 남긴다.

## 10. 지속적 연구·하네스 개선·SOTA 해석

90분·12기회는 무조건 multi-day 연구가 아니다. 개발 pilot에서 앞선 관측이 뒤 실험 선택을 실제로 바꾸는지, 필요한 context 전환/회복이 발생하는지를 task별로 기록한다. 해당 의존 지평이 발생하지 않으면 결과를 bounded iterative ML experimentation으로 한정한다. 오래 실행한 시간·다수 호출을 장기 과학적 발견의 증거로 삼지 않는다.

Secondary 진척은 dev score/비용 곡선, 정체 후 질문 변경, 근거 있는 negative 결정과 불필요한 반복의 구분, 문맥에서 실제 사용한 source pointer, 개입·복구·UNKNOWN이다. hidden candidate 점수를 여러 번 조회해 trajectory를 만들지 않는다.

이 비교는 동일 common action surface 위의 B와 R 개발 절차 및 배포 package다. 원문의 상이한 모델/예산/metric headline, 산업 RecEvolve 수치, HoH dominance, Scroll memory score를 한 순위로 합치지 않는다. 전체 하네스 개선, 특정 요소의 순수 효과, 인간 연구 대체, SOTA, 모든 미래 모델 적용을 주장하지 않는다. 기존 제품의 제한 없는 native 설정과의 별도 외부 비교는 보조 실행 프로토콜을 마련한 경우에만 수행한다.

## 11. Prototype와 남은 실행 조건

시연은 공개 목표 하나를 받아 가설→실험→근거→다음 선택을 실제 수행하고, 중단/새 context 뒤 같은 선택과 pending run을 복구하는 것이다. 확정된 decision/RunIntent는 복구하고 새 LLM proposal은 새 사건으로 기록한다. rollback이 비용·source 철회·external receipt를 지우지 않는다. 개발 관측과 hidden FinalAssessment는 별도 타입/공개 조건/소비자를 갖는다.

과거 House Price P0의 승인·규약·준비는 별도 원본 그대로다. 이 설계는 새 실험으로 그 권위를 재사용하지 않는다. 현재 해야 할 검토는 이 문서의 과학적·기술적 결함이며, native construction 재개나 training launch가 아니다.

실행 전에 필요한 구체 산출물은 roster의 상세 provenance/license/split 봉인, B/R 실제 prompt/tool/image hashes, isolation·budget/scorer 재현 검사와 정확한 model/billing 설정이다. 원문/metadata 확인과 문서 검토가 이를 통과시킨 것은 아니다. 요청된 네 독립 reviewer가 동일 v1을 검토한 뒤 root가 지적을 반영한 v2를 작성한다.
