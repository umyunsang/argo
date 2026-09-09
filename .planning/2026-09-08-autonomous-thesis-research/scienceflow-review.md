# ScienceFlow v2 원문 검토

**결론:** 복구 가능한 실행 상태·주소로 복원하는 연구 기억·근거 기반 실행 제어는 이미 구체적인 선행 기제다. 따라서 이를 그래프 설계의 신규성으로 주장할 수 없다. 이 논문은 동일 의무·근거·총예산에서 versioned dependency invalidation이 추가로 유용한지 분리하지 않는다. B/C/G의 남은 질문은 그 좁은 증분이며, 결과는 아직 미관측이다.

## 읽기 증거

- 출처: [arXiv 2608.14354v2](https://arxiv.org/abs/2608.14354v2), 최초 2026-08-14, v2 2026-08-23. 공식 metadata 및 표지에서 **arXiv preprint / Technical Report** 확인. 검토한 metadata에 peer-reviewed venue가 표시되지 않아 게재 검증을 주장하지 않는다.
- 원문: `orx/papers/2608.14354v2.txt`, 157,182 bytes, 3,191 LF lines, SHA-256 `b2c31a916321e2c89c399c53ff26a3eaa582ae5743e089ba63cb1f0707bc151e`.
- `FULL_PAPER_READ`: 보존된 text extraction의 1–3191 전부(본문·참고문헌·부록)를 읽었다. 그림의 caption/text는 포함되지만 PDF 그림의 시각 검수와 구현/실험 재현은 하지 않았다. 아래 L은 `nl -ba`와 같은 1-based LF locator다. 읽은 구간과 초기 truncation 복구는 JSON manifest에 기록했다.

## 기제와 가장 강한 비교 지점

| 기제 | 원문 근거 | 연구에 주는 의미 |
|---|---|---|
| Workspace·memory·validation·resource의 공동 checkpoint | §2.3.1, L352–401; L482–512 | 요약문만 남기는 약한 baseline을 피하고 실행 가능한 상태를 공통 기질로 검토한다. |
| ESTRA의 current/archive × extend/redirect | §2.3.3, L532–623 | 복구와 과학 방향 변경은 별개의 선택이다. 복구가 누적 비용을 초기화하지 않는다. |
| Add/Fold/Unfold/Assemble와 실패 branch 보존 | §2.3.4, L624–797; L2267–2301 | 원문 card 주소·부정적 근거·압축 후 복구는 이미 선행 기제다. |
| Worker의 과학 판단과 controller의 실행 권한 분리 | §2.4, L798–905 | 살아 있는 process와 유용한 연구 진척을 구분한다. process/run의 두 번째 권위자를 만드는 근거로 쓰지 않는다. |

ScienceFlow는 강한 **기능적 비교 설계**의 근거이며 B와 동일한 구현이라는 뜻은 아니다. B에 실행 상태·원문/실패 근거·복구 권리를 충분히 주어야 한다. C의 compulsory applicability/revalidation은 ScienceFlow의 자동 checkpoint나 device admission과 다르다. 공통 운영 제어는 B/C/G에 동일하게 두고, C-B는 의무 절차, G-C는 versioned graph 제어 묶음의 증분으로 남긴다. 읽은 본문은 typed dependency invalidation 또는 적용성 변경의 의무 재검증을 분리 검증하지 않는다. 미보고를 기제 부재나 신규성 확정으로 바꾸지 않는다.

## 비교·ablation의 실제 범위

모든 수치는 **저자 보고**이며 로컬 효능이 아니다.

| 증거 | 확인 내용 | 제한 |
|---|---|---|
| Full MLE-bench | 75 tasks, 3회, 70.22±1.18% mean±SEM (L918–947) | backbone·hardware·동시성·12/24/36h가 다르고 일부 task 수정도 상이. 공통 compute-normalized 우위 아님(L929–932, L2463–2475). |
| Lite ablation | 22 tasks, 24h, 3 seeds, full 80.30±2.62%, ESTRA 제거 66.67±2.62%, execution-control 제거 69.70±5.25% (L1057–1097) | 여기 ±는 sample SD이고 **누적 first-medal** 지표다. graph 효과 또는 단일 최종 lock의 효과가 아니다. |
| State-matched replay | 한 task의 7 historical decisions ×4 actions×3 seeds, branch당 4h(L1024–1056) | 선택된 과거 상태의 국소 비교. 원래 5.26h 뒤 성과가 난 방향이 4h replay에서 나빠 horizon 의존성이 있다. 84 독립 과학 programme가 아니다. |
| SciModelingBench | 같은 모델/2h/8–20 query quota/8 CPU/no GPU/<32 GiB(L1544–1554) | system-task 1회, **best-valid** 보고. 총 LLM/token 비용까지 동일하다는 증거는 아니다. |

## 비용·결측·독립성에서 채택하면 안 되는 관행

Appendix의 비용은 성공하면 first-medal까지 LLM/API만, 실패하면 전체 run 비용이다. accelerator 비용은 제외하고 first-medal 시간은 성공 run만 평균한다. task checkmark는 세 run 중 하나 이상 성공한 archive 지표다(L2305–2330). 또한 일부 외부 baseline의 미완료 run을 medal 실패로 대입한다(L2463–2475). 이는 현재 연구의 단일 artifact lock·전체 비용·UNKNOWN/미관측 hidden score 분리 규칙을 대체할 수 없다.

Telemetry는 54/75 task에만 완비되어 관측 coverage와 전체 outcome의 분모가 다르다(L1098–1103, L2333–2339). storage 결과는 33 measured tasks의 footprint 위반을 적용한 simulation이며 one-GPU 결과도 기록 기반 estimate로 서술된다(L1105–1115). fresh resource-constrained 재실험으로 인용하지 않는다. KTTSP의 긴 기억과 peer guidance는 단일 trace이고 인과효과가 아니다(L1314–1336). Math best-score 비교는 예산 불일치, invalid candidate 제외, 일부 원시 artifact 미복제를 포함한다(L1185–1197, L2744–2752, L2793–2800).

SciModelingBench는 동일 study의 DrugMatrix 6 endpoints를 한 group으로 묶는다(L1463–1502). 이 원칙은 후보 task 수를 독립 표본 수로 세지 않도록 돕는다. runtime hidden-label 격리는 설명하지만 pretraining contamination-free는 명시적으로 주장하지 않는다(L3170–3185). task/source ancestry와 독립 confirmation은 별도 확인 대상이다.

## 후행 prototype에 대한 좁은 제안

실행 가능한 snapshot, append-only 원문 result card, 누적 resource ledger, 과학 경로/실행 권한 분리는 공통 계층의 후보로 둔다. 실험 질문은 “복구 뒤 상위 evidence·protocol 적용성이 바뀔 때, 동일 의무와 총예산의 C보다 versioned dependency traversal이 stale downstream 재사용을 줄이고 사전 잠근 단일 최종 산출물을 개선하는가”로 좁힌다. 이는 **가설**이며 구현 재개 승인이나 G 선택이 아니다.

최종 선택 규칙은 agent의 단일 artifact lock과 종료 후 독립 평가로 유지한다. archive-best/first-medal은 보조 진단으로만 둔다. 모든 worker·controller·재검증·복구·실패 비용을 누적하고 CPU/GPU-hour, tokens, wall-clock을 따로 기록한다. process UNKNOWN, no-lock/no-artifact, scorer failure, 숫자 미관측을 분리한다. captured-state replay는 별도 제한된 개발 진단으로 활용할 수 있지만 자연 의존 지평, 독립 programme 또는 확증 검증을 대신하지 않는다.
