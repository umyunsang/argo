# DOMAIN/METHODS — ARGO 통합 연구 설계 근거 검토

- 기준일: **2026-09-05 KST**. 로컬 시계로 확인했으며, 마감 정리 직전 확인은 06:01:03 KST이다. 아래 2026년 출판본은 미래 문헌이 아니다.
- 상태: **이 문헌검토 lane 완료 / root 통합 대기**. 출판본 5편의 선택한 방법·평가·한계 구간을 읽었다. 모두 **selected-sections**이며, 전체 PDF 정독이나 독립 재현을 주장하지 않는다.
- 쓰기 소유: 이 파일과 사용자 추가 승인 범위인 `domain-sources/`만. 원고·그림·공유 계획·실험 감사는 root 소유이다.
- 연구 연쇄: **논문 연구 → 근거 기반 통합 연구설계의 선택·검증 → 승인 후 native ARGO 구현 → NAIS 프로토타입**. 측정 절차만을 별도 연구목표로 대체하지 않는다.
- 현행 경계: native construction paused; 인정된 ARGO 효능 근거 **0**. 아래 설계·endpoint는 **제안**이지 구현·실험 완료 기록이 아니다.

## 1. 결론과 root 전달사항

선택할 학술적 추상화는 제품 이름의 결합이 아니라, **문헌의 특정 구절로 뒷받침되는 후보 생성 → 대안 간 비교와 구별 가능한 예측 → 관측 전 실험 선택 → 실행·실패 기록 → 결과에 따른 주장 및 후속 계획 갱신 → 근거를 보존한 인계**이다. 문헌은 이 연쇄의 서로 다른 일부를 뒷받침한다. 그러나 검토한 어느 논문도 이 조합의 ARGO 구현이나 NAIS 효능을 검증하지 않는다. 통합이 유리하다는 결론 또한 후속 비교가 필요한 연구가설로 둔다. [D1–D5 및 본 검토의 설계 추론]

- 원고 우선 BibTeX key: `baek-etal-2025-researchagent`, `chen2025scienceagentbench`, `pmlr-v267-huang25n`, `Asai2026`.
- 서지 정정: **ResearchAgent = NAACL 2025**, **ScienceAgentBench = ICLR 2025**이다. 초기 작업 메모의 학회 추정은 폐기했다.
- 2026년 대안 **AstaBench**도 공식 ICLR 출판본으로 방법·한계를 확인했다. 따라서 “통합 연구 벤치마크가 없다”는 연구공백 주장은 부적절하다. 다만 그 E2E 과제는 AI/NLP 영역과 제시된 연구 과제·단계에 제한되므로 ARGO의 자유로운 목표 설정·다영역 자율연구와 같지 않다. [D5, §3, Appendix E.9–E.10]
- root 제공 현재 표본 **16개 = bio 5 / chem 5 / geo 2 / psych 4**는 **scorer fixtures only, E2E 0**로 취급한다. 이 lane은 raw audit를 재수행하지 않았으며, 이 수치는 원 논문 전체 벤치마크의 구성이나 ARGO 성공률이 아니다.
- GoT AAAI 2024·ADAS ICLR 2025의 심층검토는 root 소유로 남겼다. Pi/PrimeAgent/OpenResearchCLI/Exa는 구현·발견 수단이지 이 문서의 과학적 근거가 아니다.

## 2. 근거 등록부와 실제 읽은 범위

페이지는 별도 표시가 없으면 **PDF 첫 장을 1로 센 물리 페이지**이다. 추출 `.txt`의 줄번호는 보조 탐색용이며, 최종 locator는 아래 PDF와 절 제목을 따른다. 다운로드·전체 텍스트 추출은 전체 읽음의 증거가 아니다. 부분 출력이 잘린 구간은 완독 범위에 포함하지 않았다.

| ID / 문헌 | 검증한 출판 상태와 primary URL | 실제 읽은 범위 및 사용 한계 |
|---|---|---|
| D1 ResearchAgent | NAACL 2025 Long Papers, 6709–6738; DOI `10.18653/v1/2025.naacl-long.342`; [공식 논문](https://aclanthology.org/2025.naacl-long.342/) | **selected-sections**. PDF pp.4–6 = 인쇄 pp.6712–6714: §3.1 후반, §3.2, §3.3 및 §4.1–§4.3 해당 부분. PDF p.10 = 인쇄 p.6718 `Limitations` 전체. §3.1 앞부분과 §4.3 다음 페이지까지 전체를 읽었다고 주장하지 않음. |
| D2 ScienceAgentBench | ICLR 2025 출판본. [공식 PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/f12b4df26344f3be803c06b555252efe-Paper-Conference.pdf) | **selected-sections**. PDF p.1 서지·개요, pp.3–5 §2–§2.3 해당 부분, p.22 Appendix A `Limitations`. §2.3의 다음 페이지로 이어지는 모든 평가 세칙까지 읽은 것은 아님. |
| D3 POPPER | ICML 2025, PMLR 267:25372–25437. [공식 논문](https://proceedings.mlr.press/v267/huang25n.html) | **selected-sections**. PDF p.3 §2.3 본문과 Assumption 1; pp.4–7 Assumptions 2–3, Theorem 4, §2.4, Remark 5, 각주 2, §3의 데이터·평가 설정. p.3 그림 전체 및 논문 전체 부록은 읽음 범위에서 제외. 한계는 조건부 보장·정보 누출·실패 선택 편향·정적 분석 범위가 직접 쓰인 이 구간에 근거함. |
| D4 OpenScholar | Nature **650**, 857–863 (2026), issue 8103; DOI `10.1038/s41586-025-10072-4`. [출판본](https://www.nature.com/articles/s41586-025-10072-4) | **selected-sections**. PDF p.1 서지 확인; p.6 = 인쇄 p.862 `Limitations`; pp.8–9 무쪽번호 Methods의 `Task formulation and challenges`, retrieval pipeline, `Inference: self-reflective iterative RAG` 및 이어지는 학습 설명. 35쪽 전체·모든 보충표를 읽지 않음. |
| D5 AstaBench — 현행 대안 | ICLR **2026** 출판본; [공식 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/b2ce9568dbb559aefc8c98ca5b5314ce-Paper-Conference.pdf), [학회 발표 기록](https://iclr.cc/virtual/2026/oral/10009972) | **selected-sections**. PDF p.5 §3 및 §4.1 시작, p.10 E2E 논의·§6 향후 과제, pp.41–42 Appendix E.9 전체 및 E.10 전체. 모든 하위 benchmark·judge prompt를 읽지 않음. 원고 기본 인용 4편과 구별한 대안 검토이며, root가 본문에 채택한다면 이 공식 출판본의 별도 서지 항목을 추가해야 함. |

**서지 확인 경로.** D1은 ACL Anthology 원문과 `.bib`, D3은 PMLR 원문과 공식 HTML의 BibTeX, D4는 Nature 원문과 Springer 출판사 DOI별 BibTeX를 대조했다. D2·D5는 공식 proceedings PDF의 학회 표기를 확인했다. D2·D3의 출판본 DOI를 확인하지 못했으므로 “DOI 없음”이라고 단정하거나 arXiv DOI로 대체하지 않았다. 다섯 편 모두 이번 채택본은 출판된 학회·학술지 버전이며 **프리프린트로 인용하지 않는다**. D4의 DOI에 들어간 `025`는 발행연도를 뜻한다고 추정하면 안 된다. Nature 온라인 공개일은 2026-02-04이며, 출판사 BibTeX의 월 첫날 placeholder는 최종 항목에서 생략했다.

**최신성 검색 기록.** `web.run`으로 ScienceAgentBench·ResearchAgent·POPPER·OpenScholar·2026 AstaBench의 공식 학회/출판사 현황을 검색·열람 요청했다. 이 실행에서는 표시 가능한 응답 내용·citation ID가 반환되지 않아 그 호출 자체를 확인 근거로 삼지 않았다. Exa는 primary URL 발견에 사용했고, 주장 채택은 직접 확보한 출판본 bytes 및 출판사 서지에 한정했다. RE-Bench 등 미독 후보의 성능·범위를 대신 추정하지 않았다. 검색 범위가 제한되어 전 세계 최신 대안을 망라했다는 뜻은 아니다.

### 보존 bytes와 SHA256

파일은 모두 이 문서와 같은 폴더의 `domain-sources/`에 있다. PDF는 원격 응답을 그대로 저장했고, `.txt`는 `pdftotext -raw` 파생물이다. **해시는 동일 bytes 확인 수단이지, 논문 주장 타당성이나 출판사 서명 검증이 아니다.** 취득일은 2026-09-05 KST이다.

| 저장 파일 | PDF SHA256 |
|---|---|
| `researchagent-naacl2025.pdf` | `f2ef097b0eb33f02002ed7a192d16d769256a2cbd477a57af39213e15a025f89` |
| `scienceagentbench-iclr2025.pdf` | `dbd8d388e3ea5cbf7d04eac631689169030c34cfd391e3c57bd13cde81b977fa` |
| `popper-icml2025.pdf` | `a3c4b3701543a84a74602ae46a624b955e201bb83baeea2c219213a0e65b4998` |
| `openscholar-nature2026.pdf` | `7d3d5b5cf460ebb73d1a8f8ba76dd14567a50812c84d53ece86c7b0441469b18` |
| `astabench-iclr2026.pdf` | `5b76a93021e083872c392b6dd3aea6fcd8627e3b259acbf0993f3fe64b836143` |

- D1 bytes: `https://aclanthology.org/2025.naacl-long.342.pdf`; 원본 서지 `researchagent-publisher.bib`: `https://aclanthology.org/2025.naacl-long.342.bib`.
- D2 bytes: 근거 등록부의 공식 PDF URL과 동일.
- D3 bytes: `https://raw.githubusercontent.com/mlresearch/v267/main/assets/huang25n/huang25n.pdf`; 이 URL은 PMLR 출판 저장소의 자산이다. 서지 보존 `popper-publisher.html`: `https://proceedings.mlr.press/v267/huang25n.html`.
- D4 bytes: `https://www.nature.com/articles/s41586-025-10072-4.pdf`; 원본 서지 `openscholar-publisher.bib`: `https://citation-needed.springer.com/v2/references/10.1038/s41586-025-10072-4?format=bibtex&flavour=citation`.
- D5 bytes: 근거 등록부의 ICLR 2026 공식 PDF URL과 동일.

## 3. 논문에서 채택할 원리와 채택하면 안 되는 주장

### D1 — 문헌에 의존하는 문제·방법·실험설계의 연쇄

ResearchAgent는 문제, 방법, 실험설계를 순차적으로 생성하고 검토한다. 인용 이웃과 entity co-occurrence 검색을 이용하지만, entity store는 제목·초록에서 만든 문헌 탐색 장치이다. 이를 실험 결과의 원인·의존성이나 주장별 지지/반박 그래프라고 부르면 과장이다. 사람·모델의 제안 품질 평가는 존재하나, 저자도 생성 아이디어의 **실험 검증 필요성**을 한계로 명시한다. [D1, pp.4–6, p.10]

**설계 적용:** 후보마다 문제→방법→구별 가능한 실험의 연결 근거를 보존한다. 고정된 15 reviewer 역할이나 인용수 기반 품질 가정을 그대로 이식하지 않는다. 대안은 동일 문헌과 예산을 가진 단일 생성·검토 경로이며, 역할 분할의 이점은 별도로 비교해야 한다.

### D2 — 고정 목표를 수행하는 코드의 검증

ScienceAgentBench는 **102개 과제, 44편 논문, 네 영역**에서 지정된 목표와 데이터로 Python 프로그램을 작성하게 한다. 실행 유효성은 과학적 목표 달성과 같지 않으며, SR은 과제별 기준이다. CBS는 성공 과제에서 1로 덮어쓰므로 SR과 독립적인 품질 증거로 합산하면 안 된다. 저자는 Appendix A에서 **코드 생성 중심**, Python 한정, 실행시간 상한, 공개 자료·확보 가능한 전문가 중심의 영역 선택을 제한으로 밝힌다. [D2, §2, Appendix A]

**설계 적용:** 실행 계층의 acceptance 계약을 만드는 참고로 사용한다. 단독 점수로 아이디어 독창성·실험 선택·타인 인계·맥락 갱신을 검증했다고 쓰지 않는다. 네 영역이라는 사실만으로 전 과학 영역 대표성도 성립하지 않는다.

### D3 — 적응적 검정에는 근거 의존성을 추적해야 한다

POPPER의 보장은 주가설의 귀무가설이 각 하위 귀무가설을 함의한다는 조건, 과거 정보에 대한 조건부 e-value 유효성, 적법한 선택·중단 조건에 의존한다. LLM이 생성했다고 조건이 자동 충족되지 않는다. 각주 2는 실패한 시도를 무시하는 사건 자체가 잠재 증거값과 관련되면 유효성이 깨질 수 있다고 경고한다. 구현은 정적 데이터 분석이며 실제 물리 실험으로의 확장은 가능성이지 완료 결과가 아니다. [D3, §2.3–§2.4, Remark 5, 각주 2]

**설계 적용:** 문헌/metadata만 본 설계 단계와 결과를 본 해석 단계를 구별하고, 선택 시점·열람 정보·실패/중단·반복 데이터 사용을 기록한다. 이 기록은 유효성 점검의 필요 자료일 뿐 충분조건이 아니다. ARGO에 e-value 곱이나 특정 유의수준을 의무화하지 않으며, 실제 검정 적용 가능성은 root 통계 lane과 검토한다.

### D4 — 출처가 아니라 주장에 근거를 붙이기

OpenScholar의 산출물은 검색한 특정 passage와 출력 span을 연결하는 인용 기반 합성이다. retrieval→초안→추가 검색/자기 피드백→인용 보완은 채택 가능한 절차지만, 출력에 인용이 있다는 사실만으로 사실성이 보장되지는 않는다. 저자는 완전 자율 문헌합성을 주장하지 않으며, 전문가 표본·rubric 및 문체 선호·불완전 검색·unsupported claims·corpus 시점 문제를 한계로 설명한다. 출판연도와 평가 corpus의 최신성을 혼동하면 안 된다. [D4, Methods pp.8–9; Limitations p.6]

**설계 적용:** 논문 식별자에 더해 버전·bytes hash·passage/page·주장·지지/반박/불충분 판정을 저장한다. 단순 참고문헌 목록보다 검토 가능성이 높다는 설계 이유는 있으나, OpenScholar가 ARGO의 실험 의존성 그래프나 갱신 효과까지 증명한 것은 아니다.

### D5 — 최신 통합 benchmark도 과제와 채점 의미를 분리해야 한다

AstaBench는 문헌·코딩·분석·E2E를 포함한 suite와 표준 도구를 제안한다. Appendix E.9–E.10의 E2E 과제는 **AI/NLP**, 문헌에서 생성한 아이디어의 전문가 선별, 과제 설명·단계 제공, report/code/artifacts의 rubric 채점으로 구성된다. 평균 단계 완료와 모든 요구 단계 완료는 따로 보고한다. 따라서 코드 실행만 보는 것보다는 넓지만, 백지에서의 과학적 의제 선택이나 타 분야의 실제 발견과 동일하지 않다. §6은 judge 개선·오염 저항성·인간 협업·영역 확장을 향후 과제로 둔다. [D5]

**설계 적용:** 후속 통합 비교의 후보로 남기되 현재 ARGO 측정 결과로 대체하지 않는다. 주변부 단계 성공률을 곱해서 전체 성공률을 계산하지 말고, 동일 run에서 요구된 연쇄가 모두 충족되는지를 직접 정의한다. 단계 독립성은 여기서 가정하지 않는다.

## 4. 제안하는 하나의 통합설계와 대안

다음은 논문들을 근거로 구성한 **본 연구의 제안**이다. 선행연구의 구현 완료 기능을 ARGO의 완료 기능으로 전이하지 않는다.

| 연쇄의 단계 | 최소 산출물 / 다음 단계로 전달할 근거 | 문헌과의 연결 및 미해결점 |
|---|---|---|
| 연구 목표와 후보 구성 | 목표, 제한조건, 대안 후보, 반증 가능한 예상 차이, 미충족 전제 | D1은 문제→방법→실험설계 연쇄를 뒷받침. 사용자의 과학적 목표를 자율적으로 잘 정한다는 증거는 아님. |
| 문헌 근거와 비교추론 | 후보별 지지/반박 passage, 출판·버전 정보, 왜 이 후보가 다른 후보보다 검증가치가 있는지 | D4는 passage 귀속, D1은 문헌 기반 후보 확장에 해당. 증거가 동일한 경쟁 후보를 여러 문장으로 복제하지 않도록 설계. |
| 실험 선택과 관측 전 고정 | 선택 후보, 기각/보류 사유, 구별할 예측, 대조·관측 단위, endpoint, 데이터·도구·예산, 허용 갱신 시점 | D3의 정보 의존성 경고를 반영. 실제 영역별 통계 전제는 추가 검토 대상. |
| native 실행과 결과 해석 | protocol fingerprint, 코드·데이터 버전, 실행/실패 receipt, 결과, 해석 가능한 범위 | D2는 실행 acceptance 설계에 한정해 참조. native daemon·REPL·복구는 로컬 프로젝트의 구현 기반이며 과학적 효과의 근거는 아님. |
| 맥락 갱신과 인계 | 새/철회된 근거, 영향을 받는 주장·계획, 재검토 상태, 다음 담당자가 재구성할 패킷 | D4의 주장 귀속 및 D3의 정보 기록에서 도출한 **확장 제안**. 이 단계의 그래프 우월성·자동 갱신 안정성·인계 성공은 아직 검증되지 않음. |

그래프를 쓰기로 한다면 최소 노드는 `SourceVersion`, `Passage`, `Claim`, `Candidate`, `Protocol`, `Run`, `Decision`으로, 관계는 `supports`, `contradicts`, `depends_on`, `tested_by`, `supersedes`처럼 의미를 구분하는 방안을 제안한다. 예컨대 passage의 철회는 그 passage에 의존한 선택 근거를 재검토 상태로 바꾸되, 이미 발생한 run receipt를 삭제하거나 과거 판단을 덮어쓰지 않는다. 이는 **연구용 표현 제안**이며 canonical runtime schema의 존재·채택 선언이 아니다. graph edge가 증명되지 않은 인과관계를 의미하지 않도록 한다.

비교의 핵심은 “그래프 유무”라는 임의 요인명보다 **해결하려는 실패**이다. 최소 대안은 같은 근거를 보유한 **버전형 flat evidence ledger + 단일 실행 주체**, 더 복잡한 후보는 명시적 의존성 graph와 역할 분리이다. 둘 모두 같은 목표·자료·도구·실행예산·인간 개입 한도를 갖도록 제안한다. 전자는 구성·검증 비용이 작지만 다수 의존관계 탐색을 별도로 해야 하고, 후자는 관계 추적에 유리할 가능성이 있지만 잘못된 edge·오래된 상태·추가 조정비용을 만든다. 어떤 쪽이 적합한지는 갱신 누락과 인계 재구성 endpoint에서 반증 가능하게 비교한다. 지금 **G×C×F**, 에이전트 수, 그래프 기술, 특정 모델을 확정할 근거는 없다.

## 5. 도메인 정합적 endpoint — 전부 후속 제안

연구의 목적은 아래 지표 자체가 아니라 **더 타당한 연구 후보를 선택하고 그 선택을 실행·갱신·인계까지 보존하는 통합설계**이다. 지표는 그 주장을 반박할 수 있게 하는 관측 장치이다. 실험 규모·효과 기준·표본수는 예비 근거 없이 고정하지 않는다.

| 평가 대상 | 반증 가능한 정의 | 단독으로 입증하지 못하는 것 |
|---|---|---|
| 문헌 기반 선택 근거 | 고정 corpus에서 표본 추출한 결정적 claim에 대해 독립 검토자가 passage의 지지/반박/불충분을 판정; 잘못 귀속된 비율과 판단 불일치 별도 보고 | 인용 개수나 문체 선호는 과학적 타당성이 아님. |
| 후보의 검증가치 | 결과를 보기 전에 후보·대안·구별할 예측을 기록하고, 분야 검토자가 실현 가능성 및 경쟁 설명을 구별하는 설계인지 판단 | 신규성/선호 점수는 후속 실험의 성공이 아님. 고정 corpus 내 비중복성과 세계 최초도 구분. |
| 실험 선택의 적합성 | 동일 목표·제약 아래 대안 대비 선택 사유가 endpoint·관측단위·대조조건과 일치하는지 판정; 주장을 구별하지 못하는 계획을 오류로 기록 | 좋아 보이는 계획의 텍스트가 실행 가능성을 자동 보장하지 않음. |
| 실행 fidelity | 실제 run이 고정 protocol·입출력·영역별 scorer를 충족하는지, 실패·중단·재시도와 함께 기록 | 기존 fixture의 scorer PASS는 해당 agent의 실제 run도, 자율설계도 아님. |
| 근거 갱신 | 정해진 증거 수정 사례에서 영향을 받는 주장·선택의 재검토 누락 및 무관한 주장에 대한 과잉 변경을 함께 계산 | 변경 탐지 성공이 새 주장의 참임을 증명하지 않음. |
| 인계 | 원 작성자와 추가 대화 없이 패킷으로 목표·선택 근거·protocol·결과·남은 불확실성을 재구성하는지 확인; 숨은 보조정보 사용은 별도 기록 | 체크리스트 채움이나 파일 전달 자체는 인계 수신자의 이해·재실행 성공이 아님. |
| 통합 연쇄 | 같은 연구 episode에서 근거 귀속·선택 적합성·실행 fidelity·갱신/인계의 사전 정의 요건이 모두 충족되는지 별도 판정 | 서로 다른 과제·run의 부분 점수를 합쳐 E2E 성공이라 부를 수 없음. |

**ScienceAgentBench의 실제 영역과 현재 표본의 구분.** 원 논문의 네 영역은 Bioinformatics, Computational Chemistry, Geographical Information Science, Psychology & Cognitive Neuroscience이다. 이 영역들은 같은 종류의 과학적 목표가 아니다. 각 과제의 목표와 scorer가 요구하는 값·산출물에 맞춰 해석하고, 실행과 목표 충족을 분리한다. [D2, §2]

아래는 root 제공 16개 fixture 구성을 대상으로 한 **검토 질문 제안**이며, 이 lane이 개별 과제·데이터를 조사했다는 뜻이 아니다.

| 현재 fixture 영역 | 후속 설계에서 반드시 명시할 영역 조건 | 인정 가능한 endpoint의 범위 |
|---|---|---|
| bio 5 | 해당 과제의 분석 대상·표본 단위·비교 대상·기대 출력 | 해당 분석 목표 충족 여부. 생물학적 발견·인과성으로 승격하지 않음. |
| chem 5 | 물질/반응 등 실제 대상, 예측·계산·분석 중 목표의 종류, 기준 출력 | 과제별 계산/분석 정확성. 새로운 화학적 실험 선택의 우월성은 별도 검증. |
| geo 2 | 공간·시간 단위, 좌표/집계 조건, 요청된 분석/시각화의 뜻 | 해당 지리정보 과제 충족 여부. 서로 다른 공간 해상도의 점수를 그대로 합치지 않음. |
| psych 4 | 참가자/관측 단위, 반복 관측 여부, 평가할 통계량/산출물 | 지정 분석 또는 예측 목표의 충족. 심리학적 설명의 참이나 임상적 효능과 구분. |

NAIS의 구체적 대상 영역·사용자·입력·허용 도구·실험 실행 범위는 이 lane에서 확정할 수 없다. 그러므로 특정 분야의 benchmark를 NAIS의 대표 평가로 지정하지 않는다. root가 실제 NAIS 연구 시나리오를 명시한 다음, 그 목표에서 **무엇을 자율적으로 선택하고, 어떤 근거로 선택을 기각할 수 있으며, 무엇을 누구에게 인계하는지**에 따라 부분 benchmark와 별도의 통합 시나리오를 매핑하는 것이 적절하다. 현재 판단은 평가 설계 제안이지 실험 착수 승인이 아니다.

## 6. 원고에 통합 가능한 한국어 완결 문단

아래 문단은 **대체 문장 제안**이며 원고를 직접 편집하지 않았다. citation key를 root의 서지 체계에 연결한 뒤 사용한다.

### 연구목표·연구 연쇄

본 연구는 연구 에이전트의 구성요소를 나열하거나 실행 점수만을 측정하는 데 목적을 두지 않는다. 연구자가 제시한 목표 아래에서 문헌 근거에 기반한 후보를 구성하고, 후보 간 차이를 검증할 수 있는 실험을 선택하며, 선택 근거와 실행 결과를 다음 판단까지 일관되게 연결하는 통합 연구설계를 제안한다. 이를 위해 먼저 선행연구가 검증한 기능과 검증하지 않은 기능을 구분하고, 그 결과에 따라 통합설계의 구성과 평가 대안을 선택한다. 이후 설계의 타당성 검토와 재개 승인을 거쳐 이를 ARGO의 native 구조에 구현하고, NAIS 프로토타입에서 실제 연구 시나리오와의 정합성을 검토하는 하나의 연구 연쇄를 유지한다. 각 단계의 산출물은 다음 단계의 입력과 제약을 제공하며, 계획의 존재를 구현 완료나 과학적 효능의 증거로 간주하지 않는다.

### 선행연구에서 도출되는 설계 근거

문헌 기반 연구 지원에서는 후보의 생성과 후보를 지지하는 근거의 확인을 구분할 필요가 있다. ResearchAgent는 문헌을 이용하여 문제, 방법, 실험설계를 연속적으로 구성하고 검토하는 접근을 제시하지만, 생성된 제안의 실제 실험 검증은 남은 과제라고 명시한다. 따라서 제안 품질에 대한 평가를 실행 이후의 과학적 성과로 해석할 수 없다. 한편 OpenScholar는 검색한 구절에 연결된 인용 기반 합성을 통해 주장의 출처를 확인할 수 있는 구조를 제공하면서도 불완전한 검색과 근거 없는 주장 등의 한계를 인정한다. 본 연구는 두 접근에서 후보 구성과 주장별 근거 귀속의 원리를 채택하되, 문헌의 인용관계나 개체 공출현을 실험 결과의 의존관계와 동일시하지 않는다. 후보를 선택한 이유, 그 이유가 의존하는 문헌 구절, 이후 결과에 따라 재검토해야 할 판단을 구분하여 표현하는 것은 본 연구가 추가로 제안하고 검증할 부분이다. `\cite{baek-etal-2025-researchagent,Asai2026}`

### 비교추론·실험 선택·갱신

통합설계에서 실험 선택은 생성된 설명이 그럴듯한지를 평가하는 단계가 아니라, 경쟁하는 설명 사이에 어떤 관측 차이가 나타나야 하는지를 명시하는 단계로 정의한다. 관측 전에 목표, 대안, 선택 근거, 결과변수와 분석 조건을 기록하고, 결과를 확인한 뒤 이루어진 판단 변경은 이전 상태를 덮어쓰지 않고 구별한다. POPPER가 제시한 순차 검증의 보장은 정보 의존성과 조건부 유효성 등의 전제에 의존하므로, 에이전트가 실험을 설계하거나 실행 기록을 남겼다는 사실만으로 통계적 타당성이 확보되는 것은 아니다. 이에 본 연구는 증거를 열람한 시점, 실패와 중단, 반복 사용한 자료를 함께 보존하여 선택과 해석의 전제를 점검할 수 있도록 제안한다. 또한 새 근거나 수정된 결과가 도입되면 이에 의존하는 주장과 후속 계획을 재검토 대상으로 연결하되, 이러한 연결 구조의 유용성은 동일한 근거를 보유한 단순 기록 방식과 비교하여 검증해야 한다. `\cite{pmlr-v267-huang25n}`

### 평가 범위와 현행 결과의 한계

ScienceAgentBench는 지정된 데이터 기반 과학 과제를 수행하는 Python 프로그램을 평가하므로, 실행 가능성과 과제별 목표 달성을 구분하는 데 유용하다. 그러나 논문이 밝힌 코드 생성 중심의 범위와 네 영역의 선택 조건을 고려하면, 그 점수만으로 연구 아이디어의 가치, 실험 선택의 적합성 또는 맥락을 보존한 인계까지 검증했다고 볼 수 없다. 따라서 본 연구는 영역별 실행 기준을 통합 연구의 일부 endpoint로 사용하되, 근거 귀속, 관측 전 선택 근거, 결과에 따른 갱신 및 인계의 충족 여부를 따로 정의한다. 2026년 9월 5일 기준 현재 준비된 16개 표본은 scorer fixture이며, ARGO가 통합 연구 연쇄를 실제 수행한 E2E 결과는 없다. native 구현도 중단 상태이므로, 현 단계의 기여는 확인한 선행연구에 근거한 통합설계와 그 설계를 반증 가능하게 검토하기 위한 평가 조건의 구체화에 한정한다. 후속 ARGO 구현과 NAIS 검증은 이 연구의 연속된 계획이지 완료된 실증 결과가 아니다. `\cite{chen2025scienceagentbench}`

## 7. 검증된 BibTeX 4건

논문 제목·저자·출판처·연도·쪽수/DOI는 출판본 또는 출판사 서지로 대조했다. citation key는 D1·D3·D4의 출판사 key와 D2의 로컬 key이다. 아래는 불필요한 초록·placeholder 날짜를 제외한 정규화 항목이다. D5는 현행 대안 검토용이며 요청한 2–4개 원고 우선 서지 범위를 넘기지 않기 위해 이 목록에서는 제외했다.

```bibtex
@inproceedings{baek-etal-2025-researchagent,
  title = {{ResearchAgent}: Iterative Research Idea Generation over Scientific Literature with Large Language Models},
  author = {Baek, Jinheon and Jauhar, Sujay Kumar and Cucerzan, Silviu and Hwang, Sung Ju},
  booktitle = {Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)},
  year = {2025},
  month = apr,
  publisher = {Association for Computational Linguistics},
  pages = {6709--6738},
  doi = {10.18653/v1/2025.naacl-long.342},
  url = {https://aclanthology.org/2025.naacl-long.342/}
}

@inproceedings{chen2025scienceagentbench,
  title = {{ScienceAgentBench}: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery},
  author = {Chen, Ziru and Chen, Shijie and Ning, Yuting and Zhang, Qianheng and Wang, Boshi and Yu, Botao and Li, Yifei and Liao, Zeyi and Wei, Chen and Lu, Zitong and Dey, Vishal and Xue, Mingyi and Baker, Frazier N. and Burns, Benjamin and Adu-Ampratwum, Daniel and Huang, Xuhui and Ning, Xia and Gao, Song and Su, Yu and Sun, Huan},
  booktitle = {The Thirteenth International Conference on Learning Representations},
  year = {2025},
  url = {https://proceedings.iclr.cc/paper_files/paper/2025/file/f12b4df26344f3be803c06b555252efe-Paper-Conference.pdf}
}

@inproceedings{pmlr-v267-huang25n,
  title = {Automated Hypothesis Validation with Agentic Sequential Falsifications},
  author = {Huang, Kexin and Jin, Ying and Li, Ryan and Li, Michael Y. and Candes, Emmanuel and Leskovec, Jure},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  pages = {25372--25437},
  year = {2025},
  volume = {267},
  series = {Proceedings of Machine Learning Research},
  publisher = {PMLR},
  url = {https://proceedings.mlr.press/v267/huang25n.html}
}

@article{Asai2026,
  author = {Asai, Akari and He, Jacqueline and Shao, Rulin and Shi, Weijia and Singh, Amanpreet and Chang, Joseph Chee and Lo, Kyle and Soldaini, Luca and Feldman, Sergey and D'Arcy, Mike and Wadden, David and Latzke, Matt and Sparks, Jenna and Hwang, Jena D. and Kishore, Varsha and Tian, Minyang and Ji, Pan and Liu, Shengyan and Tong, Hao and Wu, Bohao and Xiong, Yanyu and Zettlemoyer, Luke and Neubig, Graham and Weld, Daniel S. and Downey, Doug and Yih, Wen-tau and Koh, Pang Wei and Hajishirzi, Hannaneh},
  title = {Synthesizing scientific literature with retrieval-augmented language models},
  journal = {Nature},
  year = {2026},
  volume = {650},
  number = {8103},
  pages = {857--863},
  doi = {10.1038/s41586-025-10072-4},
  url = {https://doi.org/10.1038/s41586-025-10072-4}
}
```

## 8. 완료 범위와 인수 조건

- 로컬 `AGENTS.md`, `docs/argo/agent-brief.md`, `docs/argo/migration-state.json` 및 root planning을 읽었고, 현행 pause와 native 완료 slice 부재를 확인했다. 안내된 `docs/CODEX-NAVIGATION-GUIDE.md`는 이 checkout에 없었다.
- 이전 메모의 고정 G×C×F 조언은 현재 요청과 충돌하여 적용하지 않았다. 기억은 경로와 경계를 찾는 데만 사용했다.
- 문헌 발견 → primary bytes 확보 → selected methods/limitations 읽기 → 서지 대조 → 한국어 통합설계·endpoint·BibTeX 작성까지 완료했다. 현재 lane에서 원고·테스트·새 모델 실험·native runtime·계정·배포·git commit을 변경하지 않았다.
- root가 채택할 부분은 §§4–6의 **제안**과 §7의 네 서지 항목이다. D5는 “통합 benchmark 부재” 주장을 피하기 위한 현행 대안이다. 현재 fixture의 구체적 실행 상태·통계 수치·원고 인용번호는 root가 자기 소유 증거와 대조하여 통합한다.
- 이 문서는 자동 미래 갱신 약속이 아니다. 후속 변경은 새로운 source version·해시·읽은 locator·영향받는 claim을 명시한 별도 검토가 필요하다.
