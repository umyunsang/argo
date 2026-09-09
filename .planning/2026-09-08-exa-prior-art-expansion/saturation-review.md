# Life After Benchmark Saturation — 원문 검토

- 검토일: 2026-09-08. 범위: 부모 에이전트가 지정한 원문 추출 텍스트 한 파일. 추가 검색, 코드 실행 실험, 원본 수정 없음.
- 원문: Nitya Nadgir et al., *Life After Benchmark Saturation: A Case Study of CORE-Bench*, arXiv:2606.26158v1, 2026-06-23. [원문 식별자](https://arxiv.org/abs/2606.26158).
- 출판 상태: 제공된 v1 본문은 **Preprint**로 표시됨. 동료심사 게재 상태를 이번 검토에서 확인하지 않았으므로 확정 게재 논문으로 쓰지 않는다.
- 원문 파일: `sources/2606.26158v1.txt`; 125234 bytes, 2570 LF; SHA-256 `d57377ecc52de3ac10fa7216b60c215ca632a47380500d28f885f037290799b2`.
- 읽기: 1–650, 651–1300, 1301–1950, 1951–2570을 모두 읽었다. 상태는 **FULL_EXTRACTED_TEXT_READ**다. PDF 시각 검토·원 코드·로그 재실행·참고문헌 원문 검토까지 뜻하지 않는다. 도표는 추출된 문장·표 값에 한해 사용하고 수식/코드의 추출 서식은 실행 가능한 명세로 취급하지 않는다.
- 아래 LF는 이 해시의 추출 파일에 대한 1-based inclusive line 범위다. HousePrice P0 및 B/C/G 명칭은 부모의 작업 지정에서 받았으며 해당 프로토콜이나 결과를 이 검토자가 독립 감사하지 않았다.

## 저자 보고와 사용 한계

| ID | 본문에서 직접 확인한 방법·결과 | 원문 위치 | ARGO 연구에 사용할 수 있는 범위 |
|---|---|---|---|
| S1 | 기존 정오답 grade와 절차 정확성, 마지막 계산 정확성, 사전 산출물에서 답을 읽는 경로를 로그로 대조했다. LLM rubric으로 표시하고 모든 오답 및 flag를 수동 확인했다. 15개 task-level 오류, 20개 shortcut task(4개 중복)를 발견했다. | §2.1/Table 3, LF279–293; Table 9, LF1360–1364 | 정답률만으로 수행 기제를 입증할 수 없다는 직접 근거. 이 contamination은 **실행 전에 있는 산출물**이며 학습 데이터 오염을 검증한 결과가 아니다. |
| S2 | Table 8은 정답+절차 미충족+올바른 계산인 경우, 필요한 부분만 재현하거나 ad-hoc 계산을 하는 것을 수정 사유로 보지 않는다. 반면 사전 산출물에서 답을 얻은 경우를 제거 대상으로 다룬다. | Table 8, LF1311–1359 | 금지할 shortcut과 정당한 부분 실행은 실제 연구 목표에 따라 구별해야 한다. 이 논문으로 모든 full-pipeline 실행을 강제할 수 없다. |
| S3 | 수정 v1.1은 39 tasks, OOD는 19 tasks다. OOD는 기존 task 구조를 유지하고 분야 구성을 바꿨다. 최상위 5개 accuracy의 차이를 유효 표본 크기 n^0.5를 사용한 근사 SE와 z=1.96으로 비교했다. | §2.1, LF270–273; §2.2, LF302–312; A.2, LF1248–1291 | 정확도 포화와 평가 무용성을 구별하는 근거. 독립적인 동등성/비열등성 검정이 아니며, 서로 다름을 못 보인 결과로 보편적 동등성을 확정할 수 없다. OOD도 전체 R&D 분포를 포괄하지 않는다. |
| S4 | 다섯 Codex CLI 구성(모델별 medium)에 각각 5회 추가 trial을 실행하고 종료 뒤 추가 prompt로 confidence를 받았다. outcome consistency, resource consistency, calibration, discrimination을 측정했다. 보고한 평균 pass rate 93%, confidence 32.1%였고 shell 오류 수와 confidence의 관련성이 task success로 이어지지 않았다. | §3.1, LF417–439 | 반복성과 성공률을 별개로 측정하고 자기확신을 판정자로 쓰지 않을 근거. 일관되게 틀릴 수도 있다. 외부 참조 [47]의 원문이나 세부 계산식을 이번에 검증하지 않았다. |
| S5 | input/cached/output token 합과 실행 당시 단가에 의한 달러 비용을 함께 비교했다. 같은 97.4% accuracy에서 GPT-5.3-Codex medium은 GPT-5.4 high보다 약 60% 적은 비용이라고 보고했다. cache 정책 때문에 token 순위와 달러 순위가 다르다. CORE-Agent Opus 4.5의 timeout 2건은 resource log가 없어 평균에서 제외했다. | §3.2, LF440–457, LF565–574 | 비용·token을 별도로 기록할 근거. 보고 가격은 당시 가격이고 ARGO 가격·효율이 아니다. 실패 run의 resource 누락 때문에 관측 평균을 모든 시도 비용으로 확대할 수 없다. |
| S6 | 세 모델을 각각 3개 scaffold에서 비교하고 390 logs/56 failures를 분석했다. 동일 모델·동일 82.1% accuracy 두 scaffold도 12/39 tasks에서 정오답이 달랐다. 사후 최선 scaffold를 고르는 oracle은 해당 두 모델에서 100%였다. targeted fix 95.2%(269), rewrite 67.8%(59)를 보고했고 같은 capsule에서 양 전략이 등장한 26개로 제한해도 비슷한 연관성을 봤다. | §3.3, LF584–621 | aggregate score뿐 아니라 task별 불일치·실패 기제를 비교할 근거. oracle은 배포 가능한 라우터 성과가 아니다. fix/rewrite는 무작위 배정 처치가 아니므로 targeted fix의 인과 우월성으로 읽지 않는다. |
| S7 | HAL harness, Azure CPU/GPU VM을 썼다. Codex/Claude Code/OpenCode는 45분 timeout·max retries 3, CORE-Agent는 5시간·200 steps·max retries 1이었다. accuracy/efficiency에는 Codex v0.122를 사용했지만 reliability는 GPT-5.1을 제외하고 v0.130.0이었다. 같은 GPT-5.1에서도 CLI 버전으로 accuracy가 크게 달라졌다고 보고했다. | A.3/A.3.1, LF1292–1308 | 버전·reasoning·시간·retry·tool 정책이 포함된 **구성 전체의 결과**다. 모델이나 scaffold 이름만으로 순위를 재사용하지 않는다. 고정 모델 비교도 모든 예산 요인을 통제한 순수 scaffold 인과효과는 아니다. |
| S8 | 20개 논문·5명 공동저자 평가자·50 sessions를 논문/평가자로 균형 배정해 25 manual과 25 협업을 비교했다. 논문·평가자 fixed effects의 log-duration 회귀, researcher-clustered CR2 SE를 사용했다. manual coefficient 0.7485, SE 0.0919, df 3.7, p=.00176, 시간비 2.11을 보고했다. 180분 censoring은 모형에서 보정하지 않았다. | §4.1, LF810–834; A.5.7–8, LF2002–2063 | 제한된 연구자·분야에서 시간 단축을 보고한 선행 사례다. 인간 RCT 효과를 ARGO 자동 실행 비교 효과로 이전할 수 없다. 5 clusters, 선정 편향, 참가자 비맹검, censoring을 함께 밝힌다. |
| S9 | 19/25 협업 runs를 두 인간 setup 단계 이외 자율 완료로 보고했다. 그러나 Table 20의 협업 결과는 exact match 15, tolerance 3, fail 7이다. 논문 외에 검증된 ground truth가 없어 outcome correctness를 평가할 수 없다고 명시했다. | §4.2, LF848–853; §4.3, LF926–956; Table 20, LF2524–2534 | **자율 완료·논문 수치 일치·독립 검증된 정확성은 다른 판정**이다. 19/25를 재현 성공률로 인용하지 않는다. 독립 scoring이 중요하다는 설계 추론을 지지하지만, 저자들이 독립 scorer로 재현 정확성을 입증했다고 쓰면 안 된다. |

## HousePrice P0 및 후속 B/C/G 적용 메모

이하 내용은 선행연구에서 얻은 **설계 추론/후속 진단 제안**이며 로컬 효능 결과가 아니다. 현재 frozen protocol, primary final artifact, scoring rule, 예산, 채택 기준은 변경하지 않는다. 이미 고정한 입력·산출물·로그가 허용하는 범위에서 사후 진단을 분리하고, 새 실행 또는 prompt가 필요한 항목은 후속 설계 후보로 남긴다.

- **P0 해석:** 실행 성공 또는 답 파일 존재는 정량 성능 자체가 아니다. 지정된 primary final artifact를 기존 독립 scorer로 계산한 점수, 실제 생성 경로, 환경 완료를 구분한다. 지금 P0가 어느 항목을 충족했는지는 이 검토로 확인하지 않았다.
- **B/C/G 비교:** 부모가 정한 해당 조건들을 동일 task/seed·동일 model/version/reasoning·동일 시작 환경과 고정 예산에서 대조한다는 원칙을 적용할 수 있다. 실제 통제 상태는 별도 확인한다. aggregate 차이가 없더라도 task별 실패/성공 전환과 비용 차이를 볼 수 있다. 더 많은 도구나 graph 추가 자체는 처치 효능이 아니다.
- **독립 scorer 경계:** scorer가 고정 artifact와 고정 입력에서 계산하는 실제 수치가 primary 판단이다. 생성 agent의 설명·자기평가·critic 동의·종료 선언·graph 완성도는 대체하지 않는다. 기존 scorer와 별도 진단의 충돌은 원래 판정을 조용히 바꾸지 않고 discrepancy로 남긴다.
- **오염 경계:** 시작 artifact inventory와 실행 trace를 보고 제출 수치가 현재 run의 계산에서 나왔는지 확인한다. 문헌 지식 활용과 숨겨진 정답/완성 산출물 직접 읽기를 구분한다. trace가 없으면 clean으로 판정하지 않고 unknown을 남긴다. 금지한 shortcut의 정확한 정의는 기존 protocol을 따른다.
- **확장성 경계:** 공개된 computational reproduction task의 효과는 새로운 과학적 가설의 질, 논문 참신성, graph/loop의 인과적 기여, 종단 간 자율 연구 및 SOTA를 보장하지 않는다.

## 유용한 추가 측정 3개

| 제안 | 이미 있는 기록으로 가능한 진단 | 새 설계가 필요한 경우와 부정 결과 |
|---|---|---|
| 1. 최종 artifact의 점수·실행 증거 대조 | 기존 scorer 값, artifact 식별자/hash, 생성 명령/입력 lineage, agent가 보고한 값의 일치 여부를 한 행에 기록한다. 현재 정답률/성능 점수는 유지하고 artifact 없음·다른 metric·사전 결과 읽기·증거 없음은 별도 진단한다. | trace 또는 scorer 입력이 없으면 검증 불가. agent가 성공을 주장해도 독립 점수와 산출물 연결이 없으면 효과를 입증하지 못한다. |
| 2. 실패를 포함한 총비용·지연 | 모든 시도에 대해 input/cache/output tokens, 기록된 단가/실행일, 도구 비용, wall-clock, retries, timeout, 누락 여부를 보고한다. 총 시도 비용/독립 검증 성공 수와 run별 분포를 볼 수 있으며 성공 0이면 정의 불가로 남긴다. | 누락 실패 비용을 0으로 대체하지 않는다. token-only는 금액 비용의 대리값으로 한정한다. 점수 동률이어도 비용만 늘면 추가 scaffold의 실용적 개선 근거가 약해진다. |
| 3. 반복 outcome/resource 일관성과 조건 간 불일치 | 이미 반복 실행이 있다면 동일 task의 성공 벡터, 점수/비용 변동, 조건별 정오답 전환을 대조한다. correctness와 consistency를 함께 제시한다. 작은 표본의 평균만으로 우월성을 확정하지 않는다. | 반복 run이 없으면 reliability는 아직 미측정. 추가 반복과 paired 불확실성 분석은 후속 protocol에 명시해야 한다. confidence prompt를 지금 추가해 frozen trajectory를 바꾸지 않는다. |

## 논리적 부정 결과

1. 이 논문은 **context graph, loop engineering, ARGO, B/C/G의 우월성**을 시험하지 않는다. 설계·평가 원칙을 뒷받침하며 로컬 성능 증거는 제공하지 않는다.
2. headline accuracy가 높거나 서로 비슷하다는 사실은 절차 타당성, 신뢰성, 비용 효율, 인간 효용이 확보되었다는 결론을 주지 않는다.
3. 부분 실행은 항상 shortcut이 아니며, 전체 실행도 최종 계산·답 선택이 잘못되면 task success를 보장하지 않는다.
4. 사후 oracle 100%, targeted-fix 상관관계, 인간 협업 2.11배 시간비를 ARGO 라우팅·복구·연구 생산성의 예상 개선량으로 옮기지 않는다.
5. 현 원문은 preprint다. 사용자가 요구한 확정 발표/게재 문헌 조건에 합치하는지 별도 확인 전에는 보조 근거 후보로 둔다.

**판정:** 추가 선행연구로 유용하다. 새 구성의 SOTA 주장을 제공하는 논문이 아니라, primary artifact + 독립 scoring + 총비용 + 반복성으로 설계 대안을 검증해야 하는 이유를 구체화한다. 이번 검토의 로컬 validation 결과는 원문 전체 추출 텍스트 읽기 및 claim locator 검증에 한정된다.

