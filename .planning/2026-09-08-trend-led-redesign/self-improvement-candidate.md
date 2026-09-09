# 경험에서 만든 연구 도구는 새 ML 문제를 풀게 하는가?

상태: 후보 설계 완료. 두 논문 추출문을 전부 읽었다. 실험·설치·학습·네이티브 구현은 수행하지 않았다. 아래 실험 예산은 제안값이다.

**질문:** 같은 AI가 실험 실패에서 배운 도구와 전략을 갖추면, 처음 보는 데이터셋에서도 더 좋은 모델을 만들 수 있을까?

**권고:** 직관성과 R&D 활용성은 높지만 일반적인 “자기개선 하네스”는 신규성이 약하다. **동일 비용의 재시도·연구 메모보다 재사용 연구 도구가 새 ML 과제에서 추가 성능을 만드는가**로 좁힌 조건부 후보로 남긴다.

## 읽은 근거

LF는 추출문의 실제 줄바꿈 기준이며 PDF 쪽 번호와 다르다. 도형·수식을 별도 렌더로 검증했다는 뜻은 아니다. 정확한 protocol·locator는 동명 JSON에도 기록했다.

| 논문 | 확보 판본 | 추출문 SHA-256 | 완독 |
|---|---|---|---|
| [Meta^n](https://arxiv.org/abs/2608.24735) | arXiv:2608.24735v1, 2026-08-25, preprint | `7117ad8dcc82ae8b8e901f5635c8889bc8bb7bb00f1552b1795abcef0b2eacec` | `sources/2608.24735.txt` LF1–1824 |
| [HarnessDev](https://arxiv.org/abs/2609.01437) | arXiv:2609.01437v1, arXiv 날짜 2026-09-01, 표지 Date 2026-09-02; 출판 venue 확인 없음 | `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab` | `sources/2609.01437.txt` LF1–2257 |

### Meta^n이 보여주는 것

고정된 메타 연산 Ω가 이전 실행 기록과 생성 코드 스택을 읽고, 실행 전 전략 문자열과 호출 가능한 Python helper를 만든다. 기존 solver에 계층을 덧붙이며 기본 solver와 Ω에 같은 모델을 쓴다. 즉 모델 가중치를 바꾸지 않고 실행 방법을 개선하는 구체적 선행 연구다. [LF298–381, 466–544, 1500–1516]

- **적응 입력:** 최대20개 기록, 실패:성공=3:1. 컨텍스트65%는 기록, 35%는 이전 코드; 초과 시 오래된 코드를 제거한다. 깊이2는 원시 기록, 깊이3 이상은 과제군 성능·실패 패턴·직전 계층 효과와 대표3개 기록으로 요약한다. 모든 깊이에서 정보 표현까지 동일한 것은 아니다. [LF1648–1669]
- **선택:** archive-best는 과제마다 서로 다른 후보의 최고 점수를 골라 평균한다. 하나의 best chain을 동결해 배포하는 점수와 다르다. [LF623–641, 684–699]
- **설정:** Ω 템플릿·출력 schema·epsilon=0.02·alpha=0.3 고정. base 온도0.3, Ω 온도0.5/0.7/0.9 순환. 최대 깊이10(TerminalBench4). 기본 seeds42/43/44. single-shot도 executor retry 최대2회, agentic은 최대8턴이다. [LF665–683, 1392–1443]
- **벤치별 탐색:** CO-Bench B=K=2, patience4, max-iter8/6(Gemma/GPT); S2D B1/K3, early stop off, 20/10; LawBench B1/K3, off, Gemma20; SR B2/K2, patience10, 6회; ARC B2/K2, patience4, GPT8회. [LF1392–1411]
- **held-out:** CO-Bench·S2D·LawBench는 held-out으로 표시된다. AlphaEvolve Math·AlgoTune·symbolic regression은 held-out split이 없다. ARC의0.331은 명시적으로 개발 점수이며, 이 추출문에서 정확한 split ID/개수와 숫자로 된 held-out 결과를 확보하지 못했다. 미공개 정확도33.1%라고 쓰면 안 된다. [LF665–683, 704–760, 1392–1431]
- **긍정 신호:** Gemma CO-Bench archive-best0.851±0.014, best chain0.782±0.016 등을 보고한다. 둘은 estimand가 다르며 모든 조건의 우월성을 의미하지 않는다. [LF700–724]
- **비교 한계:** AE Math는 시스템별10/15/16개 평균이 섞인다. GPT depth-1 ablation은 context·helper·recursion을 함께 없애고 seed당 약870K tokens의 validation archive-best만 쓴다. 본문의 “72% context/15% code”는 제거 실험의 감소량 비율이지 상호작용까지 분리한 가법적 인과 기여율이 아니다. [LF1131–1183, 1424–1431, 1488–1496]
- **비용:** Gemma CO-Bench agentic seed42는29 candidates,36.1M tokens,약10시간. SR agentic 총21.7M tokens. 그대로 재현하기는 부담스럽다. [LF1445–1468]

**직접 검증하지 않은 질문:** 하나의 frozen 연구 도구 패키지가 서로 다른 새 ML 데이터셋에서, 같은 총예산으로 연구 메모를 축적한 강한 연구 agent보다 나은가? 기존 문제군에서 archive의 최고 후보를 모은 성능은 이 질문의 답이 아니다.

### HarnessDev가 보여주는 것

Creation은 빈약한 seed로 하네스를 만들고 Evolution은 그 결과를 고친다. creator와 executor를 분리하고, 하네스를 동결한 뒤 평가한다. Creation은6 creator·4분야·5 benchmark·2,207개 고유 과제, creator–benchmark당 독립 생성3회 평균을 보고한다. Evolution은 **코드 하네스**만 다룬다. MLE-bench75개는 Creation의 ML 성능이지 ML 하네스 자기개선 결과가 아니다. [LF232–264, 325–418, 466–482]

- **적응:** SWE-Pro100 + Terminal-Bench89를 반복 관측. 같은 commit의100+89 평가쌍이 완료되어야 공식 후보다. H0 이후 최대10쌍, 사이마다 고정 첫5+5개 probe 최대2회. creator가 최종 후보를 고른다. [LF332–404]
- **held-out:** 종료 후 feedback100과 겹치지 않는 SWE-Pro630개에서 모든 공식 버전을 평가하며 점수를 creator에게 주지 않는다. Terminal89는 모두 개발 feedback이다. 원래731개와100+630 사이1개 차이의 사유는 본문만으로 확정하지 않는다. [LF712–777]
- **총비용 일치 아님:** 평가쌍 횟수 제한은 있지만 로컬 실행은 무제한이며 creator 시간 제한이 없다. token efficiency는 executor 비용이고 creator·judge·probe는 제외한다. matched-search는 future work다. [LF459–463, 1011–1022, 1392–1397, 1689–1718]
- **결과:** self-runtime5개 최종 버전은 held-out +1.43~+4.44pp(평균+3.11). 고정 Gemini4개는 Opus creator만+2.70pp; Qwen−1.11, DeepSeek−2.38, GPT−10.32pp다. 개발 중 점수 상승은 새 문제 개선을 보장하지 않는다. [LF712–777, 871–891]
- **변동성:** 같은 commit pair-score가 약±4.75pp 변할 수 있다고 보고한다. 64개 변경의 feedback/held-out 방향 일치는34/64, 최종 선택이 held-out 최고인 경우2/9다. creator–runtime cell당1 trajectory여서 모집단 비교나 uncertainty estimate를 지지하지 못한다. [LF871–891, 1035–1047]
- **ML 관찰:** Data 실패77.8%를 harness defect로 분류하고2,325개 실행 중441개 degenerate submission을 기록한다. 기술적 실패 분류이며 특정 도구가 원인이라는 무작위 인과 실험은 아니다. MLE 실행은 A80080GB·14vCPU·RAM227GiB, 과제당10시간이다. [LF484–497, 555–567, 1262–1268]

**직접 검증하지 않은 질문:** 실패에서 만든 연구용 측정·탐색 도구가 단순 재시도/메모보다 총비용 대비 유용하며 새 ML 데이터셋으로 전이되는가?

## 신규성 충돌

| 생각 | 선행 연구와 충돌 | 남길 질문 |
|---|---|---|
| 고정 LLM이 자기 코드/도구를 개선 | 두 논문이 직접 다룬다 | 자체를 신규 기여로 주장하지 않음 |
| 실패 기록→재사용 helper | Meta^n과 매우 가깝다 | 새 ML 데이터셋에서 메모 대비 전이 효과 |
| frozen artifact·unseen 평가 | HarnessDev가 이미 적용 | 검증법으로 차용 |
| 여러 후보 중 최고 선택 | 두 논문이 다룬다 | test별 후보 선택 없이 하나를 배포 |
| 같은 총비용의 메모·재시도와 비교 | HarnessDev는 future work | 이 두 논문 대비 빈칸, 전체 문헌 신규성은 미확정 |

HarnessDev LF973–1022는 HarnessOpt-Bench, Evo-Bench, Meta-Harness, Self-Harness, HarnessCompass와 matched-budget evaluation을 이미 언급한다. 이 lane에서는 해당 원문을 추가로 읽지 않았으므로 그 결과를 독립 검증했다고 주장하지 않는다.

남길 기여는 **“ML 연구 경험을 실행 가능한 도구로 남기는 것이 자연어 메모보다 언제 이득인가”에 대한 비용 일치 비교와 실패 분석**이다. 알고리즘 신규성은 미확정이다.

## 가장 작은 공개 ML 실험

### 대상

공개 이진 분류 데이터셋18개를 **적응4 / 후보선택2 / 최종평가12**로 분리한다. OpenML의 공개 과제를 후보 모수로 제안하되 dataset ID·버전·라이선스·같은 원자료의 파생 관계는 아직 선정/검증하지 않았다. 즉시 실행 가능한 task manifest는 아니다.

제안 적격 범위는50,000행 이하·300특성 이하이며, 동일 원자료의 변형은 split을 넘지 않는다. 각 데이터셋의 train/validation/test를 고정하고 test는 최종 evaluator만 본다. 과제별 산출물은 학습된 예측기와 test 예측값, metric은 test AUROC다. 일반 과학 발견이나 문헌 탐색 성능까지 측정한다고 주장하지 않는다.

### 비교와 고정 조건

단일 base LLM exact snapshot/decoding을 creator·executor에 공통 사용한다. runtime/container·ML 라이브러리·데이터·scorer·task당 비용을 고정한다. 이후 별도 실험 장치를 쓰며 현행 ARGO 소스를 고치지 않는다.

모든 조건은 정상적인 파일·Python·ML 실험 loop와 task 안의 임시 코딩 권한을 가진다. tool 조건만 코드를 쓸 수 있게 하는 약한 비교를 만들지 않는다.

| 조건 | 적응 과제의 같은 budget으로 하는 일 | 다음 과제로 전달 |
|---|---|---|
| A 도구+전략 | 공통 기록을 읽고 재사용 연구 helper/전략 개선 | 동결 package+전략 |
| B 계속 연구+메모 — **주 대조군** | 같은 기록, 추가 가설/실험, 재사용 메모 개선 | 동결 메모; task별 임시 코딩 가능 |
| C 원래 agent — 보조 | 경험 재사용 없이 같은 task당 budget | 원래 연구 agent |

A/B는 전달 문서·코드의 크기/context 상한, 후보 기회, 전체 개발/실행 tokens·fit·CPU budget을 맞춘다. helper 내부 fit도 계수한다. A−B는 경험을 코드로 재사용하는 추가 이득, A−C는 전체 경험 효과다. 특정 helper가 필요하도록 환경을 일부러 망가뜨리지 않는다.

### 절차

1. 적응4의 공통 초기 실행 기록을 준비해 A/B에 같은 기록을 준다.
2. 조건별 독립 개발 lineage3개, 개선2라운드만 실행한다. 각 라운드는 적응4를 평가한다.
3. 선택2에서 H0와 후보2개를 각1회 평가한다. 평균 validation 성능으로 하나를 고르고 동점은 적은 비용을 택한다. H0 선택도 허용한다.
4. 패키지/메모를 동결한 뒤 최종12에서 한 번씩 실행한다. lineage별 동일 task/seed mapping을 쓰며 test 후 수정/재선택은 하지 않는다.
5. “막힘 뒤 구제”는 보조 분석이다. C가 유효 실험3회 연속 validation AUROC를0.005 이상 올리지 못한 과제를 plateau로 표시한다. 해당하지 않는 과제도 주 분석에 남긴다. 이 정의는 제안값이며 보편적 연구 정체 기준은 아니다.

“막힘 감지기”의 성능을 별도 연구로 확장하지 않는다. 질문은 배운 도구가 새 문제에 도움이 되는지다.

### 결정적 지표

**최종12개 데이터셋의 paired test AUROC 차이 A−B**. 각 데이터셋의3 lineage를 먼저 평균한 뒤12개 차이를 평균한다. 데이터셋이 통계 단위이며36개 실행을 독립 표본으로 세지 않는다.

시간초과·빈 출력·학습 실패도 모든 시도에 포함하고 task별 고정 trivial predictor AUROC로 점수화한다. 정확한 처리 규칙은 실행 전에 고정한다. 보조 지표는 A−C, plateau 구제, helper 실제 호출률, 개발/실행별 tokens·CPU, validation→test 차이다.

12과제·3lineage는 **최소 신호탐색 실험**이며 검정력 보장이 아니다. 데이터셋 bootstrap interval과 모든 task별 차이를 함께 낸다. 제안한 실용 채택 기준은 평균+0.01AUROC 이상, 95% interval 하한>0, 예산 준수다. 문헌에서 도출된 보편적 threshold가 아니라 후보 선택 기준이다. 실패하면 무효과와 표본 부족을 구분하고 자동 확장하지 않는다.

### 예산과 위험

제안 상한은 실행당20K total LLM tokens,15분,2CPU cores, 최대6fit×60초다. creator는 개선 round당30K tokens. 실제 데이터·runtime에 맞는지는 아직 실행 검증하지 않았다.

- A/B 각각3×(2라운드×적응4 + 후보3×선택2 + 최종12)=78회, 합156회.
- 공통 초기4×3=12회까지168회: downstream3.36M+creator0.36M=**3.72M tokens**, 최대84CPU core-hours.
- C의 최종12×3=36회까지 **204회, 약4.44M tokens, 약102CPU core-hours**.
- 공통 기록·캐시 재사용은 양 조건에 대칭 적용한다. API 가격은 조회하지 않아 USD 비용은 계산하지 않았다. 실제 latency·wall time·토큰 계량 가능성은 미확인이다.

주요 위험은 개발 실패를 설명하려고 후보·검증 횟수를 계속 늘리는 것이다. 두 라운드·독립3회를 유지한다. 작은 평균 차이만 보고 대규모 MLE-bench GPU 실험으로 바로 확장하지 않는다.

## 눈에 보이는 데모

한 화면에 모델 성능 곡선과 agent가 만든 연구 도구를 보여준다.

1. 이전 데이터셋에서 반복 실험의 성능이 정체된다.
2. agent가 실패를 읽고 subgroup 오류분석/특징 후보 평가 같은 연구 도구를 만들고 실제 호출한다.
3. 새 session의 처음 보는 데이터셋에서 동결 도구를 쓰는 agent와 메모만 받은 agent가 같은 budget으로 연구한다.
4. best-validation curve, 최종 test AUROC, 시간, 도구 호출을 함께 비교한다.

실패→새 측정 도구→새 가설→모델 개선의 연결이 보여야 한다. 예외 처리·submission 검사만 좋아진 것을 연구 돌파구로 포장하지 않는다. 숫자는 실제 결과만 쓰고, 한 성공 사례와 최종평가 전체를 함께 보여준다.

## 거절 이유와 후속 연결

**가장 강한 거절 이유:** Meta^n은 이미 실패에서 전략/helper를 생성하고 HarnessDev는 frozen artifact의 미공개 전이를 평가한다. 이번 연구가 단순 도메인 교체만 남거나 메모와 차이가 없다면, 새 주제의 기여가 작다. 생성 도구가 실제 성능 개선에 쓰이지 않으면 더 약하다.

살릴 이유는 같은 모델이 연구 경험으로 다음 연구를 잘하는가라는 질문이 직관적이고 반박 가능하며, 유효할 때 제품 기능이 선명하다는 점이다. thesis에는 과학적 비교를 쓰고 내부 ARGO/NAIS 명칭·계획을 넣지 않는다. 연구가 유효하고 구축 재개가 명시 승인된 이후에만 기존 연구 loop/Continual Harness로 연결할 요구사항을 만든다. 네이티브 기능이나 wrapper 제품을 구현했다는 주장은 없다.

## 작업 기록

- 프로젝트 AGENTS, brief, migration state, root task plan, planning-with-files skill을 읽었다. catchup 미동기화 보고 없음.
- `docs/CODEX-NAVIGATION-GUIDE.md`는 checkout에 없었다.
- 최초 묶음 출력이 잘려 HarnessDev LF1–70을 재독한 뒤 본문·참고문헌·부록 전체를 완독했다.
- 과거 memory의 graph-control 전제는 현재 요구와 충돌해 재사용하지 않았다. thesis→선택 설계→prototype 및 native pause는 현행 문서로 재확인했다.
- 동일 파일 delete/add apply_patch가 거부되어 변경 없이 종료됐고, 단일 update로 전환했다.
- 작성은 이 Markdown과 동명 JSON 두 개뿐. 추가 retrieval·benchmark 실행·설치·source 변경 없음.
