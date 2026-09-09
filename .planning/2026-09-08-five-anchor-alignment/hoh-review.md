# Harness-of-Harness 원문 검토

상태: `COMPLETE_LOCAL_FULL_TEXT_READ`. 이 문서는 내부 연구 정렬용이며 실험·구현 완료 기록이 아니다. 아래 성능 수치는 모두 저자 보고치다.

## 원문과 읽기 범위

Haoyang Yan, Min-Le Su, Hangfan Zhang, Zhanhao Li, Chen Zhang, Shao Zhang, Yang Chen, Lei Bai, Shuyue Hu, **Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement**, [arXiv:2609.01481v1](https://arxiv.org/abs/2609.01481v1), 2026-09-01, preprint. 확인되지 않은 학회·저널 이름을 부여하지 않는다.

- 원문: `sources/2609.01481v1.txt`; SHA256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`; 3251 LF.
- 읽기 완료 구간: 1–120, 121–430, 431–830, 831–1250, 1251–1640, 1641–2040, 2041–2460, 2461–2860, 2861–3251. 본문·참고문헌·부록·추출된 표와 그림 설명 전부 포함.
- 같은 이름의 PDF가 없어 렌더링된 그림·추출 누락 여부는 확인하지 않았다. 저장소 코드나 게임·실험을 재현하지 않았다.
- `AGENTS.md`, `agent-brief.md`, `migration-state.json`, 현재 `task_plan.md`를 읽었다. 지시된 `docs/CODEX-NAVIGATION-GUIDE.md`는 없었다. 관련 memory 검색에는 유효한 일치가 없어 기억을 주장 근거로 사용하지 않았다.

## 사용자에게 직관적인 연구 문제

계속 좋아지는 프런티어 모델을 사용하더라도, 연구 목표 하나를 주고 오래 실행시키는 것만으로 연구가 누적되지는 않는다. 필요한 것은 앞선 실험에서 무엇을 실제로 알게 되었는지 보존하고, 그 근거로 다음 가설과 실험을 고르며, 실행 결과를 독립적으로 확인해 연구 방향을 수정하는 운영 방법이다. 이 연구는 모델 가중치를 바꾸지 않은 상태에서 이러한 하네스와 연구 절차가 짧은 성공을 넘어 지속적인 과학적 진전을 만들 수 있는지 밝히는 문제다. HoH는 이 중 ‘앞선 산출물과 검증 근거를 이어받아 다음 작업을 선택하는 장기 루프’의 강한 출발점이지만, 소프트웨어 기능의 완성과 과학적 결론의 타당성은 평가 방법이 달라야 한다.

## 정확한 루프와 고정·변경 대상

원문의 상태는 공개 요구사항 `S`, 산출물 `A_t`, 실행 근거 `E_t`, 이번 회차 개발 문서 `D_t`다. **모델, 기본 하네스, 역할 정의, Runtime 정책은 한 실행 안에서 고정**된다. 변하는 것은 개발 문서·소프트웨어 산출물·실행 근거다. HoH의 continual improvement 대상은 소프트웨어 프로젝트이며, 모델 학습이나 하네스 코드 자기수정 실험이 아니다. [LF 177–184, 203–214, 285–289]

1. Planner: `S`와 직전 `E_(t-1)`에서 작고 관찰 가능한 목표 `D_t`를 정한다. 해결할 문제, 보존할 동작, 검증 조건을 함께 정한다. 범위는 파일 수보다 하나의 완결된 동작에 맞춘다.
2. Developer: `A_(t-1)`에서 이어서 `A_t`를 만든다. 변경 전 기준 동작을 확인하고 변경 뒤 관련 경로를 재실행한다. 자체 테스트는 후보 제출을 위한 피드백이다.
3. Runtime과 QA: 후보를 고정한 뒤 QA가 공개 요구사항과 이번 목표에 맞춰 black-box/white-box 검사를 한다. 개발자의 완료 진술은 수용 근거가 아니다.
4. QA/adapter: `(claim, execution record, status)`로 정규화한다. 충분한 근거는 `verified`, 실패·미충족·회귀·근거 부족은 `gap`으로 기록한다. 전자는 다음 보존 조건, 후자는 다음 작업·검증 요구가 된다.
5. 반복 예산 `T`까지 수행하고 `A_T`를 반환한다. Algorithm 1은 자동 과학적 완료 판정이나 무한 개선, 최적 후보 선택 규칙을 제시하지 않는다. 외부 benchmark 평가 출력은 개발 루프에 돌아오지 않는다. [LF 431–572, 1489–1592, 1675–1708, 1722–1734]

회차 간 두 상태 채널은 `A_t`와 `E_t`다. `D_t`는 같은 회차의 개발과 검증이 공유하며, 다음 Planner는 직전 문서를 세 번째 상태로 받는 대신 `S`와 `E_t`에서 새 문서를 구성한다. 감사용 문서 보관과 다음 모델 입력 재주입은 다르다. [LF 322–397, 1675–1708]

## 역할, 문맥, 도구, lifecycle 소유권

| 소유자 | 입력·행위 | 결과·권한 경계 |
|---|---|---|
| Planner | 공개 요구사항, 직전 근거, 계획 맥락 | 우선순위·보존·검증 조건; 활성 산출물 변경 금지 |
| Developer | 기존 작업공간, `S`, `D_t`, native file/repository/shell/build/local-testing 도구 | 활성 산출물의 단일 작성자; 구현 전략·도구 선택은 자율 |
| QA Tester | `S`, `D_t`, 격리된 후보 복사본, 공개 실행 기록, deterministic check 결과 | 후보 수정 없이 실행·검사하고 근거를 인용한 보고서 작성 |
| Runtime/adapter | 입력 고정, 접근·도구·쓰기 권한, 출력 형식, 후보 identity | 실행·역할 전환과 evidence 정규화, 외부 평가 정보 격리 |

세 역할은 **같은 harness-model 조합의 별도 invocation**이다. 독립 QA는 구현과 판정의 역할·후보 분리이며, 다른 모델이나 독립적인 오류 분포를 보장하지 않는다. Runtime 권한 강제는 논문이 서술한 계약이며 이 검토에서 코드를 검증하지 않았다. 구조화 출력이 schema를 위반하면 retry한다. [LF 117–120, 318–321, 422–430, 1180–1290, 1448–1460]

문맥은 파일의 계획·보고서·이력을 간결한 분류별 index로 먼저 보여주고 필요한 내용을 읽는 progressive disclosure다. 전용 memory module 없이 역할별 도구와 on-demand Markdown skills를 사용한다고 설명한다. 단, **benchmark에는 추가 도구·skills·version-control 메커니즘이 없고**, 다일 게임 사례에는 Godot MCP, 자산 생성, UI/UX, 테스트 skills, GitHub 이력 등이 추가된다. Benchmark 향상을 skills·memory·rollback의 효과로 귀속할 수 없다. [LF 117–170, 899–926]

원문의 범위 차이는 보존해야 한다. 본문은 Planner의 산출물 read-only 검사를 허용하지만 부록 prompt는 production code를 inspect하지 말고 scaffold·evidence에서 priority overlay만 반환하라고 한다. 도입부는 수리와 새 기능을 함께 강조하지만 구체 prompt는 blocker/regression 우선이며 최대 세 priority다. 과학 연구 모든 회차에 새 성과나 세 목표를 강제할 근거가 아니다. [LF 103–109, 372–380, 431–463, 1312–1346]

## 측정·비교·절제 근거

조합은 Codex CLI 0.142.5/GPT-5.5 high, OpenCode 1.14.30/DeepSeek-V4-Pro, Pi 0.80.10/MiniMax-M3 client-side high다. 조합 안에서 vanilla/HoH의 초기 작업공간·모델·기본 설정·공개 도구는 동일하다. GameCraft 45개(15 family별 3개), FrontierSWE 15개(구현 4, 성능 9, 연구 2)를 평가했다. ProgramBench는 평균 hidden behavioral test 통과율을 보고하지만 공급된 텍스트에서 과제 수·목록·상세 실행 부록은 확인되지 않는다. [LF 578–626, 1711–1761, 1811–1967]

| 비교 | 저자 보고 결과 | 적용 범위 |
|---|---|---|
| GameCraft vanilla → HoH@3 | Codex 49.58 → 71.52; OpenCode 26.90 → 48.98; Pi 42.16 → 58.78 | runnable 여부와 기능·콘텐츠·시각·표현 rubric의 평균 |
| FrontierSWE 평균 reward | 0.31 → 0.54; 0.23 → 0.31; 0.26 → 0.55 | task reward 평균; 과학적 발견 성공률 아님 |
| ProgramBench test pass rate | 60.41 → 66.50; 45.27 → 57.56; 35.83 → 52.68 | hidden behavioral tests의 연속 통과율 |
| GameCraft/Codex 3회 개발 비교 | vanilla continuation 58.24/6.33M tokens; HoH 71.52/8.41M | 개발 횟수 일치; 총 호출·토큰·시간·금액은 일치하지 않음 |
| 비슷한 토큰량의 checkpoint 비교 | HoH@2 64.84/5.67M vs continuation@3 58.24/6.33M | 추가 토큰량만으로 설명하기 어렵다는 해당 조건 근거 |

표 근거: LF 638–690, 799–830. Codex GameCraft 향상은 논문의 반올림 전 계산에 따라 `+21.93`으로 보고된다. 표시된 두 평균의 차이는 21.94다.

절제는 GameCraft 45개, Codex/GPT-5.5, 3회 조건이다. 첫 계획 고정 63.39(−8.13)/7.56M, 다음 계획에서 QA 근거 제외 65.23(−6.28)/7.46M, 매 회차 빈 작업공간 재구현 63.67(−7.85)/11.12M, 전체 71.52/8.41M이다. 갱신 계획·근거 피드백·산출물 연속성의 유용성을 해당 조건에서 지지한다. QA 역할 분리 자체, single writer, progressive disclosure, skills, rollback을 각각 절제한 결과는 아니다. [LF 843–875, 1990–2058, 2807–2936]

10회 FrontierSWE는 **동일 Codex의 vanilla+HoH@1–10이라는 11-checkpoint pool**이다. 상세 절은 vanilla 27.33%, @3 39.33%, @9 76.00%, @10 72.67% dominance를 보고한다. 본 실험의 12개 system-condition pool에서 나온 vanilla 44%/HoH@3 71%와 한 시계열로 연결하면 안 된다. 도입부 ‘22%→72.67%’는 상세 protocol과 맞지 않아 이 검토는 상세 수치를 우선한다. 본 실험 dominance는 각 domain 내부 과제의 pairwise 승률을 계산한 뒤 3개 domain을 같은 비중으로 평균하며, 단순 15과제 평균 reward와 구분된다. [LF 160–162, 743–766, 2146–2227]

## 다일 실행·비용·재현 한계

Fusepoint는 PRD만 있는 빈 작업공간에서 Codex/GPT-5.6-Sol high로 **분석 cutoff 70회**를 수행했다. 인간은 네트워크/API 복구에 개입했지만 계획·구현·디버깅·테스트·수용에는 개입하지 않았다고 저자가 밝힌다. 81개 이슈 중 65 closed, 16 unresolved, 17 reopened다. 이는 성장·회귀·재수리를 추적한 사례이며 완벽한 단조 개선이 아니다. 초록 ‘more than 70’와 분석 cutoff 70은 구분한다. [LF 27–32, 877–954]

- task-condition당 **한 번의 유효 실행**이며 인프라/transport 실패는 교체한다. 모델 생성 seed 공통 통제가 없고 temperature/top-p는 provider/client 기본값이다. task bootstrap 구간은 같은 과제 재실행의 모델 변동성을 추정하지 않는다. [LF 1722–1761, 2098–2102]
- token은 입력+출력이며 cached input이 포함될 수 있고 benchmark evaluation은 제외된다. provider 간 비교에 사용하지 않는다. pass control은 exact token/time/cost matching이 아니다. [LF 619–626, 2099–2144]
- FrontierSWE Table 24의 @1/@2/@3 token·time은 감소하는 항목이 있으므로 @3을 3회 전체 누적 비용으로 읽을 근거가 불명확하다. 다일 게임 전체 API 금액·자산/전문 도구 비용·복구 인력 비용·전 과정 budget cap은 이 텍스트에서 확인되지 않는다. [LF 2937–2977]
- FPS는 단일 사례이며 대조군이 없다. 이슈 closed 수는 과학 기여 수가 아니다. 부록 B.8에 PXI 계산법은 있지만 공급된 텍스트에서 평가자 수와 대응 결과표를 찾을 수 없다. [LF 2229–2260]
- ‘세 절제 조건이 모든 과제에서 열등’은 Table 22 Lighthouse의 full 80.90보다 w/o warm-start 81.50이 높은 반례와 맞지 않는다. 평균 열등 결과만 사용한다. [LF 869–875, 2919]
- 재현 패키지 설명은 core/prompts/adapter/wrappers를 포함하고 raw runs·task data·analysis/environment records 등은 제외한다. 이 검토는 실제 구현의 재현성이나 runtime isolation을 판정하지 않았다. [LF 2261–2267]

## 과학 연구로의 이전

**직접 뒷받침되는 원칙:** 장기 작업에서는 최신 산출물과 그 상태를 평가한 근거를 함께 이어받고, 근거로 다음 범위를 갱신하며, 실행과 수용 판정을 구분해야 한다. 성장·수리·보존의 우선순위는 현재 상태에 따라 바뀐다. 이는 경험을 skill로 변환하는 특정 문제보다 넓은 ‘지속적 자율 작업의 운영’에 관한 근거다.

**새 검증이 필요한 이전 가설:** `PRD → 제품`을 `연구 질문 → 재현 가능하고 근거가 있는 결론`으로 바꾸면 새 기능 완성 수로 진전을 판단할 수 없다. 대안 가설을 구별하는 실험, 부정적 결과, 잘못된 방향의 중단도 진전이다. 과학적 주장은 새 근거로 철회될 수 있어 기존 verified 주장을 영구 보존하는 규칙과도 다르다. 보존할 것은 데이터·조건·관찰·검증 이력이며 해석의 적용 범위는 수정되어야 한다.

FrontierSWE Research 두 과제는 optimizer 설계와 제약된 molecular graph regressor 학습이다. Codex PCQM4Mv2 reward는 0.90→0.89, OpenCode는 0→0, Pi는 0→0.88이므로 연구 과제 전체에서 일관된 향상을 보였다고 할 수 없다. ‘연구 과제 일부를 포함한 코드/실험 최적화’의 근거이며 자율 문헌검토, 문제 선택, 인과적 설계, 발견, 논문 주장 검증의 장기 성공을 보여주지 않는다. [LF 1955–1960, 2577–2660]

후속 설계에서는 실행 성공과 결론의 타당성을 구분하고, 다음 실험 선택의 적절성·재현·근거 없는 완료 선언·회귀/재작업·적절한 중단·전체 자원당 검증된 연구 진전을 살펴볼 수 있다. 한 모델 버전 안에서 하네스 효과를 구분한 뒤 외부 모델 업그레이드 이후 효과가 유지되는지 별도 비교해야 한다. 이는 제안이며 HoH의 검증 결과가 아니다.

## Five-anchor 역할과 Prime native migration 원칙

Five-anchor 합성에서 HoH의 역할은 **한 프로젝트를 오래 전진시키는 planning–execution–independent verification 루프와 산출물/근거의 연속성**이다. Prime는 프로젝트 문서가 정한 실제 native substrate다. Scroll/HarnessDev/RecEvolve와의 세부 관계는 각각의 원문을 통합하는 root가 확정해야 하며 이 한 논문에서 대신 추론하지 않는다. HoH를 skill-transfer 연구로 축소할 근거가 없다.

HoH 자체는 기존 하네스를 수정하지 않고 바깥에서 조율한다. 이 구현 형태를 복제하는 대신 **검증할 원칙과 설계 변수**를 추출해야 한다. 향후 construction 재개 후 역할 invocation과 권한은 기존 daemon/session worker에, 계획·근거 접근은 persistent REPL/RLM 문맥 관리에, 후보와 실행·복구 이력은 transcript/session artifact/snapshot에 연결하는 native 소유권을 제안할 수 있다. 이는 `agent-brief.md`를 따른 제안이며 native 코드의 현재 동작을 감사한 결과는 아니다.

별도 HoH supervisor·scheduler·process registry·recovery authority를 만들 이유는 이 원문에서 나오지 않는다. 독립 검증도 기존 소유자 아래 제한된 세션과 후보 복사본으로 설계할 수 있다. 과학 연구를 수행하는 루프와 하네스를 개선하는 루프를 조건·이력에서 분리해야 고정 하네스 조건과 자기개선 anchor의 효과를 구분할 수 있다. 현재 작업은 연구 설계이며 native 변경이나 모델 실행은 승인되지 않았다.

## 신규성의 경계

계획–실행–검증, 근거 피드백, warm-start, 구조화 보고서, 역할 분리, 파일 기반 문맥, 버전 이력은 이미 제시된 방법이다. 이를 재현하거나 Prime 안에 배치하는 것만으로 학술 신규성이 생기지 않는다. 후보 기여는 **과학 연구의 목표 선택·실험·해석이 이어지는 상황에서 어떤 하네스 구성이 지속적이고 타당한 진전을 만들며, 외부 모델 발전 뒤 어떤 원칙이 유지되는지** 구분하는 방법과 측정 결과다. 실제 기여 여부는 다섯 anchor 비교와 과학 과제의 독립 평가 후 판단해야 한다. 이 검토는 결과나 신규성을 증명하지 않는다.

## 작업 기록

이 lane은 `hoh-review.md`와 `hoh-review.json`만 작성했다. 중앙 계획 갱신은 root 소유다. 문서 첫 교체에서 동일 경로 delete/add patch가 거부되어 내용 변화 없이 종료되었고, 전체 내용을 읽고 scoped 문서 쓰기로 교체했다. 실험·모델 호출·native 코드 변경·외부 게시·추가 검색 loop는 수행하지 않았다.
