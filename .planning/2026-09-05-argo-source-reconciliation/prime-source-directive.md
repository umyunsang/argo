# 추가 제공 원본에 따른 정정 — 기존 교정 지시의 보충

## 최우선: 사용자가 방금 명시한 단일 연구 연쇄

사용자 원문: “졸업논문과 nais_ai는 독립적이지 않고 서로 연결 연쇄되어있는 작업이 졸업논문이 선행되어야할 연구야”

**졸업논문 연구가 ARGO 설계·검증의 선행 단계이고, 검증된 설계를 구현한 ARGO가 NAIS 프로토타입인 하나의 연구 프로그램으로 진행하라.** 별도 논문용 benchmark와 그와 무관한 해커톤 demo라는 두 트랙으로 쪼개지 마라. 연구 지표/구현 acceptance와 현장 개발 규칙의 구분은 동일 연구의 증거·단계 구분일 뿐이다.

지금 해야 할 일은 벤치마킹 재료를 어떤 native owner·상태·제어·근거·실행 경계로 연결할지 완전한 설계 대안을 도출하고, 그 선택에 영향을 줄 가설/실험/비교를 수행할 연구설계를 만드는 것이다. scientific-choice/graph 실험 하나가 전체 통합 연구 목적을 대체해서는 안 된다. 가장 정보성 있는 실험부터 우선하되 결과가 prototype의 구성·연결·동작 선택을 실제로 바꾸도록 명시하라.

같은 graph에서 문헌/대안 → 논문 가설/실험/결과 → 채택·기각 설계 → native 계약 → ARGO 구현 → NAIS 시연/검증을 추적하라. 실패/무효/기각 설계도 이유와 함께 보존한다. 이 사용자 명시 관계를 현재 canonical 연구 entrypoint와 active graph에 반영해 다음 agent도 같은 선행/후행 관계를 복구하게 하라. 사용자의 이 교정은 목표 관계의 정정이지 기존 native construction pause나 비용 승인을 해제한 것이 아니다.

## 제공 원본의 구체적 정정

사용자가 앞선 검토 직후 아래 세 원본을 직접 제공했다. 별도 연구를 재시작하지 말고 진행 중인 네 산출물에 반영하라. repository cwd는 `/Users/um-yunsang/argo-paper-orx`다.

- APP: `/Users/um-yunsang/Library/Mobile Documents/com~apple~CloudDocs/NAIS_AI/[ARGO] 2026 NAIS AI Hackathon_참가신청서.pdf`
- NOTICE: `/Users/um-yunsang/Library/Mobile Documents/com~apple~CloudDocs/NAIS_AI/2026 국가과학기술연구회 국가과학AI연구센터(NAIS) AI 해커톤 모집 공고.pdf`
- THESIS: `/Users/um-yunsang/Desktop/졸업논문계획서/졸업논문_계획서_엄윤상.pdf`

먼저 `.planning/2026-09-05-argo-source-reconciliation/source-addendum.md`를 전체 읽고 제공 PDF의 해당 쪽/해시를 확인하라. 개인정보가 있는 페이지의 원문 전체를 session 출력·graph·공개 repo에 복사하지 말고, 개인 식별값을 제외한 연구/대회 요구사항만 인계하라. 원본 PDF를 변경하지 마라.

핵심 보충:

1. 현재 APP 해시는 `a829572375ddca11ec94cbbd48827419564f655fa36aab25e3a9d3fdca8a47e6`이고 이전 Downloads 사본과 다르다. **현재 제공 신청서에는 36시간 계획이 없다.** 이전 검토에서 그 결함을 현재 신청서에 귀속한 부분을 정정한다.
2. NOTICE p.3의 본선 배점은 적합성10·활용성20·혁신성25·실현가능성25·확장성20이다. 논문 성능지표와 별개로 각 항목을 작동하는 prototype 증거에 연결하라. 미확인 배점 상태는 해소됐지만 SOTA 1위가 대회 필수라는 요구를 만들지 마라.
3. NOTICE p.5는 **실제 개발 전 과정이 본선 기간 내여야 한다**고 명시한다. 또한 사전 세로 JPG/PNG 포스터, 본선 prototype+PPT/PDF+GitHub source, 발표 약5분/Q&A 약3분이다. 포스터/기획과 현장 개발을 구분하라. APP p.7의 AI·OSS·외부 데이터 공개 의무를 함께 보존하라. 상세 사전 코드/fork/API 재사용 경계는 미확인이지 blanket allowed/forbidden이 아니다. 지금 push/공개할 권한도 아니다.
4. NOTICE p.2는 본선 날짜만 명시한다. 기존 웹페이지의 19시간은 전체 행사 관측치이며 순수 개발시간이 아니다. 제출 마감·본선 지침이 확인되기 전 개발시간을 확정하지 마라.
5. APP pp.2–4의 실제 독립 병렬 노드·경쟁·접기·되돌림과 THESIS p.1의 scientific choice를 모두 보존하라. 두 설계 중 한 실험을 선택하는 논문 episode와, 둘 이상의 실제 실행 후보를 비교하는 prototype 시연을 구별하라. 한 실행만으로 병렬 실험 경쟁 구현을 주장하지 마라.
6. APP pp.3–4의 '하네스 차이=비교 불가'를 THESIS 요소 제거 실험과 양립하도록 정밀화하라: 고정 비처리 조건+사전 등록된 treatment 차이+조건별 코드해시. 미등록 차이만 배제하고, 제거 실험 자체를 코드해시 차이로 금지하지 마라.
7. APP p.3의 Prime native 실행 소유권 + LangGraph/SqliteSaver graph plane + append-only evidence plane은 구체적 제안이다. 무조건 무시하거나 최선으로 고정하지 말고 필요성·중복 ownership·복구/동기화 비용·대안 비교로 선택하라. 현재 native construction pause는 유지한다.
8. source requirement→choice→implementation evidence→verification을 기존 active graph 소비 경로에 반영하라. APP의 '최근 agent는 single-pass'와 THESIS의 '예비 실험 완료'를 검증된 novelty/efficacy로 재사용하지 마라. 원본은 보존하고 successor에서 범위를 교정하라.

완료한 격리 probe를 반복하거나 새 비용 실험을 시작하지 마라. native construction pause, 기존 비용 승인, LG Aimers 중지, private instance 분리, clean-room 경계는 그대로다. 새 패키지 설치/외부 문의/제출/공개를 지시하지 않는다.

짧은 수신 응답에서 **논문 연구가 선행하고 ARGO/NAIS 구현이 그 결과를 계승하는 단일 연쇄**를 먼저 확인하고, 원본 버전 정정·공식 배점·공식 현장 개발/제출 조건·처리군 비교 예외를 기존 네 산출물의 어디에 반영할지 알려라. 읽기/수용과 실제 graph/설계 수정 완료는 분리해서 보고하라.
