# Reviewer 2 — 비교 공정성 독립 검토

**판정: 수정 후 유효한 제한 비교로 진행 가능.** 3개 MEDIUM 사전 명세/주장 범위 지적이다. 관측된 runtime 결함이나 실제 비용 누락의 보고가 아니다. B를 straw baseline으로 볼 근거와 v1이 SOTA를 달성했다고 과장한 문구는 찾지 못했다.

## 검토 경계

비교 공정성, strong B, 개발/선택 기회, tool/context/resource/human effort, 실패 비용, benchmark와 horizon, M2, native/adapted 및 SOTA 해석. 모든 19개 frozen manifest SHA-256이 일치한다. 실험·모델·학습·scoring 실행은 0회이며 지정된 리뷰 두 파일만 작성했다.

Generic memory summary plus a quick MEMORY.md keyword search exposed old ARGO design snippets. They were navigation exposure only; no old scientific conclusion or verdict is used. No rollout summaries or peer reviews were opened.

새 배정 context였지만 shared filesystem은 OS 격리가 아니다. Peer 결과를 읽거나 연락하지 않았고 하위 위임은 하지 않았다. planning-with-files 지침을 읽었으며, 추가 파일/과거 session catch-up 대신 이 리뷰 파일에 계획과 진행 상태를 보존했다. 계획: frozen 입력 검증 → 원문 비교 검토 → 지적 작성 → 근거 경로/해시/행 확인. 모두 완료.

## 건전한 설계 선택

- B는 persistent execution, REPL/RLM 위임, 같은 기록·원문·도구, 자체 팀/도구/계획 구성을 허용하고 R와 유사한 전략을 자발적으로 쓰는 것도 허용한다. 따라서 단순 무기억·단일 프롬프트 straw baseline이라는 지적은 근거가 없다. 다만 실제 B prompt/tool/runtime가 아직 없으므로 강한 baseline의 구현 품질은 인증할 수 없다.
- 같은 모델 안에서 runtime 자원 상한·데이터·초기 artifact·최종 선택 규칙을 맞추고 R의 context/role/descendant 비용까지 포함한다. 실패·중단·재시도를 남기고 trusted failure를 unknown으로 두는 방향은 공정하다.
- 원문 Headline을 한 순위로 합치지 않고 native 설정 비교를 별도 보조 프로토콜로 남긴다. R−B를 공통 substrate 위의 package 효과로 한정한 것은 적절하다. native Prime의 전체 성능이나 다른 native 제품을 능가했다는 근거로 재명명해서는 안 된다.
- Prime 원문의 nanoGPT 결과는 행동 차이와 최종 기록의 작은 차이를 구별한다. HoH의 main 비교와 추가 continuation 비교, Scroll의 외부 문헌 점수와 공통 backbone 비교, HarnessDev의 외부 system reference는 서로 다른 비교다. v1은 이들을 SOTA 달성의 직접 근거로 사용하지 않는다.
- CC18 repeat0/fold0 단일 outer split은 공식 10-fold leaderboard가 아니라고 명시했다. 고정 20개 유한 benchmark와 frozen corpus로 범위를 한정하므로 현재 문구에 전체 ML/산업 추천/live-web 우위의 직접적 과장은 없다.

## CF-01 · MEDIUM · 동일 개발 기회라는 조건에 사람 작업과 선택 비용의 범위가 빠져 있다

각 family의 후보 수와 모델·CPU·wall 상한은 대칭이지만, 이미 작성한 초기 B/R 자산, 후보 생성 전후의 사람 작성·수정·실패 진단, 후보로 등록하지 않은 버린 시도, 선택 실행 비용을 어느 ledger에 넣는지가 정의되지 않았다. 모든 변경 diff와 생성 비용 보존은 유용하지만 사람 개입의 허용 범위와 개발 예산의 시작점은 대신하지 못한다. 특히 3후보×4선택과제×120,000tokens이면 선택의 최대 토큰만 1.44M으로, 1.5M에 포함하는 해석에서는 개발에 최대 60,000tokens가 남는다. 이는 실행 불가능하다는 주장이 아니라 두 가지 다른 개발 절차가 현재 문구와 양립한다는 문제다.

**주장에 미치는 영향:** 양성 R−B는 숨은 추가 개발·진단 노력이나 서로 다른 선택 기회에 의한 결과일 수 있다. 그러면 예산이 제한된 같은 개발 기회로 선택된 두 package의 비교라는 해석 및 전체 비용 설명이 성립하지 않는다. 배포 때의 token cap과 실패 비용 보존만으로 이 교란은 해결되지 않는다.

**최소 수정:** 초기 B0/R0 코드·prompt·도구 자산과 이미 투입한 출처·사람 작업을 시작 자산으로 공개하고, 그 이후의 사람 수정/진단은 양 family에 같은 사전 규칙으로 허용하거나 금지한다. 후보 등록 전 폐기·실패를 포함한 모든 개발 호출을 family cap에 넣고, 선택 12회까지가 1.5M/40core-hours/24h 안인지 별도 대칭 예산인지 한 줄과 집계식으로 고정한다. 역사적 인간 개발시간을 억지로 같게 만들 필요는 없으며 초기 자산 비교라는 범위로 정직하게 한정할 수 있다. 배포 중 과학적 조언·코드 구조 수정은 자율 실행 결과와 구분하고, 허용한 기술적 복구는 양 arm의 동일 규칙과 비용으로 남긴다.

**저비용 반증:** 모델 실행 없이 가상 ledger에 초기 자산, 폐기 후보, 사람 수정, 선택 12회, 실패 재시도를 넣어 두 명의 독립 집계자가 같은 cap 사용량과 허용/비허용 판단을 내리는지 확인한다. 양쪽에 같은 개발 권리가 주어져도 B의 필요한 후보 수정만 금지된다면 공정성 조건은 실패한다.

**남은 불확실성:** 현재는 실제 사람 개입이나 비용 누락이 관측된 것이 아니다. 작성자가 동일한 내부 집계 규칙을 의도했다면 명세 보완으로 해결된다. 개발 cap을 늘리라는 권고가 아니다.

**근거:**

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L49–L57 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L8–L17 · SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L63–L67 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L89–L91 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L105–L107 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`

## CF-02 · MEDIUM · M2 이식성의 동결 단위와 선택 모델이 명시되지 않았다

선택한 B/R을 동결한다는 규칙은 있지만 후보 생성자·개발 실행자·선택 실행자의 정확한 모델이 지정되지 않았고, M2에서 M1으로 선택한 같은 후보를 쓰는지 family별로 다시 고르는지 명시되지 않았다. model settings까지 동결 manifest에 포함하므로 M2를 위한 허용 변경 목록도 필요하다. HarnessDev는 creator와 executor를 분리하고 동결 H를 다른 executor에서 실행하며, Scroll도 backbone만 변경하는 평가를 구분한다.

**주장에 미치는 영향:** M2에서 재튜닝/재선택하면 모델별로 최적화된 별도 package의 비교가 되고, M1에서 얻은 하네스 이식성의 시험은 아니다. 두 해석은 null/negative 결과 및 개발 비용을 다르게 해석하게 한다.

**최소 수정:** 생성자·개발·선택 모델을 지정하고 M1에서 동결된 B/R 후보 ID·prompt·context policy·도구 코드를 M2에서 재튜닝이나 재선택 없이 사용한다고 명시한다. 바꿀 수 있는 항목은 executor 모델 ID와 사전에 지정한 provider serialization 등 필요한 기계적 바인딩으로 열거하고 양 arm에 동일 적용한다. 모델별 재선택을 원하면 그것을 별도 적응 비교로 명명하고 비용을 분리한다. 이번 M2는 같은 provider의 지정된 두 모델 사이 보조 이식성으로 한정한다.

**저비용 반증:** M1/M2 실행 manifest를 모델 호출 없이 비교한다. 허용된 executor 바인딩 외의 후보 ID, prompt, controller, 도구, 문맥 정책, 선택 규칙이 다르면 frozen-harness transfer라는 표시는 실패한다.

**남은 불확실성:** 문맥상 한 번 선택 후 이식하려는 의도일 가능성이 높다. 실제 재튜닝이 발생했다는 지적이 아니라 두 해석을 제거해야 하는 사전 명세 문제다. M2 표본 확대나 추가 provider를 요구하지 않는다.

**근거:**

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L11–L17 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L51–L55 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L61–L67 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` L6–L17 · SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt` L200–L227 · SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt` L618–L625 · SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt` L471–L478 · SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`

## CF-03 · MEDIUM · 지속적 연구라는 핵심 범위의 관측 기준이 아직 결과 전 판정 규칙으로 고정되지 않았다

CC18의 유한 tabular 개선 비교 자체는 타당한 축소 과제이며 90분/12 dev 호출을 multi-day와 구별한 점은 적절하다. 다만 pilot에서 의존 지평을 기록한 뒤 없으면 bounded iterative experimentation으로 한정한다는 조건만 있고, 무엇을 어떤 관측으로 충족해야 지속적 연구 범위를 지지하는지 고정되어 있지 않다. 현재 절차는 12개의 서로 독립적인 튜닝 시도만으로도 완수할 수 있다. 최종 BA가 상승해도 그 원인이 긴 연구 상태의 유지·회복인지 짧은 탐색 조직화인지 구별하지 못한다.

**주장에 미치는 영향:** 결과가 나온 뒤 시간·호출·문맥 전환 또는 설명문을 임의로 골라 지속성을 인정하면, 같은 양성 결과를 지나치게 넓은 핵심 제목에 연결할 수 있다. 현재의 정직한 fallback은 과장 방지책이지만 사용자 목적의 지속적 연구 검증을 자동으로 완성하지는 않는다.

**최소 수정:** 주 비교의 제목과 confirmatory claim은 우선 bounded iterative ML experimentation으로 고정한다. 지속성에 관한 보조 주장은 개발 pilot의 outcome을 보기 전에 작고 구체적인 관측 기준을 정한다. 예를 들어 비인접 실험의 실제 산출물/실패 근거가 후속 가설·후보 선택에 연결되는 evidence chain과, 같은 연구 목표의 새 context 또는 복구 뒤 이전 확정 선택·pending run을 보존한 실제 후속 실행을 기록한다. 양 arm과 모든 대상 trace에 같은 규칙을 적용하고 충족하지 않은 경우도 보고한다. 자연스러운 의존 지평이 없으면 이 20개 과제를 탈락/교체하거나 benchmark를 무한 확대하지 말고, 더 긴 연구에 대한 효능은 미검증으로 남긴다. 필요하면 이미 계획한 한 목표 prototype을 별도 bounded continuity demonstration으로 쓰되 주 성능 실험과 섞지 않는다.

**저비용 반증:** 추가 모델 실행 없이 모든 앞선 관측을 무시하고 독립 탐색만 하는 모의 trace를 작성해 예정된 지속성 기록/판정 규칙에 넣는다. 이 trace도 지속성을 충족한다면 그 규칙은 핵심 연구 지평을 측정하지 못한다. 실제 pilot에서는 context 최대 길이만큼이 아니라 후속 선택에 사용된 이전 증거의 식별 가능한 연결을 확인한다.

**남은 불확실성:** 실제로 일부 CC18 episode에서도 긴 의존관계가 나타날 수 있다. 90분이라서 무조건 부적합하다는 주장이 아니다. 이 보조 관측은 지속성의 작동 증거이며 multi-day 또는 모든 과학 분야의 성능 우위를 입증하지 않는다.

**근거:**

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-to-prototype-objective.md` L5–L7 · SHA-256 `284aec4307c35bf542c15a19ae073d3f57d755c8794596900049f25493a127d9`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L1–L11 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L23–L31 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L63–L63 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L103–L109 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` L113–L113 · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.23552v1.txt` L412–L431 · SHA-256 `bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01622v1.txt` L374–L393 · SHA-256 `4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt` L430–L451 · SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`

## 읽기 범위와 검증 한계

이전 source-evidence.json의 full-read 표시는 이 reviewer의 읽기 이력으로 승계하지 않았다. 전체 manifest 및 아래 scope의 SHA와 구체 행은 review.json에도 보존한다.

- `.planning/2026-09-09-research-design-four-reviews/packet-v1/design-v1.md` · full · 행 [[1, 117]] · SHA-256 `a5c8dbcdceb81d5a1371641de845599bac8691a09fcb508db80f47877b3c0f18`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/protocol-v1.json` · full · 행 [[1, 56]] · SHA-256 `2a90e983116d5f8e0408e5dbf44186f8a4dbb90db0419ce01f760e6206725624`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/task-roster.json` · full_json_all_fields_including_all_rows_and_exclusions · 행 [[1, 1042]] · SHA-256 `e952968e594b2bd32ed10e6b8f9c3c0863f8e856490e41932fd333e3d388c691`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/AGENTS.md` · full · 행 None · SHA-256 `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/agent-brief.md` · full · 행 None · SHA-256 `9663771bba9aa243f5ea9bc454bf2bf68337ebfee407ed442e8e9f1fb0e1cffe`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-to-prototype-objective.md` · full · 행 None · SHA-256 `284aec4307c35bf542c15a19ae073d3f57d755c8794596900049f25493a127d9`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/docs/argo/research-decision-contract.md` · full · 행 None · SHA-256 `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/README.md` · full · 행 None · SHA-256 `d9563e13bb61244a5d7f649269196dea194191ecce47603b944f76f6eadb9755`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/source-evidence.json` · full_receipt_only_not_inherited_reading · 행 None · SHA-256 `2665dfcf8e60499ebed10e53c7be3f27b139cf86bb5febcd8ee376a8e962fdde`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/decision-record.json` · full · 행 None · SHA-256 `1c06fc00e493554d5f07a9490945fc2f284a1880ad3ee040e01b45d357d9fab6`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.23552v1.txt` · full_extracted_text · 행 [[1, 882]] · SHA-256 `bb5da5a634794581a1f52dbf96daa164790a5fef78943dc4d1a3b14a252b9fa3`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01622v1.txt` · full_extracted_text · 행 [[1, 617]] · SHA-256 `4f6a738aac042779143d0aca7cf910b3e5436cdcc1640e6cb13faa6586369985`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01437v1.txt` · selected_method_and_comparison_sections_plus_keyword_navigation · 행 [[194, 477], [610, 629], [1030, 1046], [1243, 1278], [1440, 1470]] · SHA-256 `82459e9b1506b9ccb5c523b87f35d9ceb0794bde92919fa5b043900c9852f5ab`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2608.21690v1.txt` · selected_method_and_comparison_sections_plus_keyword_navigation · 행 [[1, 107], [267, 355], [383, 562], [689, 715]] · SHA-256 `37f692dfb96e18d13964659c32778ab0d02d4a45fe0a77e7f3634b87985319af`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/paper/research/five-anchor-harness-20260908/sources/2609.01481v1.txt` · selected_method_and_comparison_sections_plus_keyword_navigation · 행 [[1, 135], [1703, 1765], [1970, 2004], [2120, 2142]] · SHA-256 `c639844f3eaad3ed6458cea9ac6286ac60dbcf17edee7e915fb6a052bdbe117a`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/power-sensitivity.json` · hash_verified_only_not_content_reviewed · 행 [] · SHA-256 `1b988beb5c3b591c119a10f7351bd60bfa2ad05341b0880930b7e7e0954a4d75`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/model-catalog-evidence.json` · hash_verified_only_not_content_reviewed · 행 [] · SHA-256 `082338d639597fbb5e6c0605e9be9ae05ed1d7747df3d6a3f7bf513e6dbfe525`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/openml-cc18-metadata.json` · hash_verified_only_not_content_reviewed · 행 [] · SHA-256 `065752575d30da0f4c0fff06a1bc797b449739028a4962cbcd8cc951105d63e6`
- `.planning/2026-09-09-research-design-four-reviews/packet-v1/openml-cc18-task-list.json` · hash_verified_only_not_content_reviewed · 행 [] · SHA-256 `a45f1a9394167f5882dbeed084f0ec633743f84fb05d4907d68fa2a2c513be6f`

추가 읽기: review-contract.md, packet-v1-manifest.json, current docs/argo/migration-state.json(권한 확인만), planning-with-files/SKILL.md, MEMORY.md 검색 노출.

**확인하지 않은 항목:**

- 실제 B/R prompts, controller/tool implementations and image contents; no runtime baseline strength certification
- 계정 접근, resolved model revision, actual billing and provider token semantics
- 데이터 rows/labels, 상세 ancestry/license, actual split custody
- 격리/자원/scorer 구현과 실제 negative fixtures
- PDF visual layout or figures; three primary papers only selected sections, not full-paper rereads
- 통계적 randomization/power의 독립적 재계산; 다른 reviewer lane
- current external SOTA leaderboard or broad missing-literature search; no external superiority claimed

초기 대량 출력이 잘려 핵심 자료와 실제 인용 구간을 작은 범위로 다시 읽었다. 현재 검토는 작은 문구/프로토콜 보완으로 적용 가능하며 전체요인 실험·더 큰 benchmark·추가 provider를 요구하지 않는다.

<oai-mem-citation>
<citation_entries>
MEMORY.md:30-43|note=[retrieval exposure disclosed; prior design conclusions excluded]
</citation_entries>
<rollout_ids>
01a06b05-fc4b-7f31-99ab-1f2bae69aac6
</rollout_ids>
</oai-mem-citation>
