# Literature / novelty review

**판정: 최신 종합 문서의 문헌 해석은 지지됨. 후속 대조군 출처 연결에 낮은 심각도 수정 1건.**

이 판정은 20260908 두 README와 두 결정 기록의 prospective 학술 해석에 한정한다. 확인한 원문 구간에서 핵심 기제나 저자 보고 결과를 뒤집는 오독은 발견하지 않았다. 보편적 연구 공백의 독창성, 효능·SOTA·연구 완료·실행 승인·프로토타입 완성을 인증하지 않는다.

## 남는 학술 질문

같은 원자료·근거 접근·연구 의무·기본 복구·기회와 자원 경계를 가진 강한 대조군에 비해 graph-mediated 제어가 단일 사전 선택 최종 산출물의 독립 성과와 비용에 실용적 증분을 주는가라는 질문은 유지할 수 있다. 확인한 논문들은 이 정확한 비교를 대신 답하지 않는다. 이는 검토한 문헌 안에서 남는 실증 질문이며, 모든 선행연구에 비교가 없다는 증명은 아니다.

scoped claim, 무효화, 실패 보존, typed operational graph, 후속 부분의 재생성, rollback, 실행 상태 복구는 이미 선행 기제다. 기여 후보는 앞으로 측정할 제한된 비교와 설계 선택이다. 관련 도구를 모두 연결했다는 사실은 학술 효능 기여가 아니다. 논문 뒤 프로토타입으로 넘길 근거를 만들려는 목적에는 이 참고문헌 묶음이 적합하다. 현재 자료로 설계 승자를 정할 수는 없다.

## LIT-01 · LOW · 후속 대조군의 Arbor 식별자를 직접 연결할 것

**분류:** `directly_supported`. **영향 범위:** prospective source binding. 최신 README의 두 Arbor 구분은 정확하며 현재 P0의 결함을 뜻하지 않는다.

계승된 study contract는 `Arbor ablation`과 `Arbor_external_anchor`만 기록한다. 최신 확장 문서는 AMD의 `2606.12563`과 HTR의 `2606.11926`을 구별하지만, 후속 대조군 선택에 쓰일 참조 자체는 아직 고유 식별자로 연결되지 않았다. AMD no-DFS 비교에는 단일 agent와 revert 경로 부재·crash가 함께 있다. HTR의 tree/insight ablation은 별도 설계여서 같은 결과로 인용할 수 없다.

근거:
- `packet/paper/research/fable51-design-review-20260907/integration/integrated-study-design.json` · SHA-256 `f73eef99ba186f5882fc79a07e72c911d0d54ce8f85a4a7c08560e551940c72e` · LF [[36, 36], [314, 317]] · The operative prospective study uses Arbor ablation and Arbor_external_anchor without an ID/version/title.
- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` · LF [[17, 17], [24, 26]] · The latest expansion establishes two distinct Arbor identities and warns against combining their mechanisms, code, or effects.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2606.12563v1.txt` · SHA-256 `9a5aacec255d3b8c6c38f57f310050661f45d0571ed7357a1882dc0a8f2d2bf7` · LF [[457, 464], [561, 574]] · AMD no-DFS ablation jointly removes structure and a revert path and ends in a crash; the critic ablation concerns measurement validity.

공식 신원 교차확인: [AMD Arbor](https://arxiv.org/abs/2606.12563), [HTR Arbor](https://arxiv.org/abs/2606.11926). HTR의 §4.2·§5.7은 이번에 [선택 구간으로 확인](https://arxiv.org/html/2606.11926v1)했다. 전체 재현 또는 완독으로 표시하지 않는다.

**최소 수정:** 다음 task-bound 비교 기록에서 각 Arbor 참조에 ID/version, 정확한 제목, 기존 source hash/locator와 참조 기제를 붙인다. 동결 P0를 수정하거나 새 일반 승인 체계를 만들 필요는 없다.

**저비용 반증 확인:** study contract LF 36·317의 선행 source record를 따라가 이미 어느 Arbor인지 유일하게 결정되는지 확인한다. 그렇다면 그 링크만 노출하고 이 항목을 닫는다.

**불확실성:** 전체 역사적 source graph와 전이 참조는 읽지 않았다. 이미 고유 식별자가 있다면 직접 링크 누락으로 축소된다. 잘못된 구현이나 비교 실행은 관측하지 않았다.

## 타당한 부분과 직접 근거

### S1

The residual question is empirical and bounded: whether graph-mediated control adds useful final-artifact performance/cost value over a strong control with equal evidence, obligations, recovery and resources. It is not a first-graph or first-invalidation invention claim.

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/README.md` · SHA-256 `68e281b339772ab44add809b2b0bdd78ea54200f222088d094f1a6869f5262a1` · LF [[59, 71], [79, 83]].
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/decision-record.json` · SHA-256 `96ee5c2311156ece38123f577ea70aaa2d053dea6e23d538f87aa961c97b68a1` · LF [[7, 8], [47, 51], [93, 98]].
- `packet/paper/research/exa-prior-art-expansion-20260908/decision-update.json` · SHA-256 `95c3346a61715e9ad18619339d535e79cbf9a6cfd62902f0f44c1f4607aeda30` · LF [[22, 28], [47, 71]].

### S2

Iris and EviGraph overlap is accurately acknowledged. Iris already specifies scoped support/refutation pointers, claim status and revisions. EviGraph already specifies operational typed evidence state, content-dependent repair, retained valid evidence, rollback and scoped negative claims.

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.02143v1.txt` · SHA-256 `120c15dda4a5da8e58f7c549bd185a7d73930c281efb0a7a369bb25e6c165eb6` · LF [[775, 889]].
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff` · LF [[85, 111], [395, 434], [435, 577], [1755, 1760], [2035, 2050]].

### S3

The negative counterevidence is stated at the right level. EvoGraph-Mem reports GPT-4o-mini PDDL progress rate 34% for add+keep+archive versus 31% for full editing. This challenges automatic preference for full editing; it is not a statistical proof of harm or a general ranking. The active-negative reachability point is correctly conditional on the written operations and empty initialization.

- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` · LF [[18, 18], [32, 32], [41, 41]].
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0` · LF [[478, 608], [617, 755], [813, 816], [956, 983], [1035, 1050]].

### S4

Critiques of EviGraph evaluation are appropriately restrained: the source states neutralized evaluator inputs, fixed extraction/judgment rules and common accounting. These descriptions do not supply the missing executed manifests, total-cap parity or variance needed for a matched local comparison.

- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` · LF [[39, 39]].
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff` · LF [[600, 649], [703, 711], [2060, 2072], [2375, 2422], [2478, 2488], [2570, 2618]].

### S5

ScienceFlow recovery and fluid-search allocation are defensible mechanism references, not efficacy priors. ScienceFlow explicitly reports heterogeneous hardware/concurrency and cumulative first-medal ablations. Efficiency Matters uses a single-completion proposer, fixed inexpensive verifier and best-so-far reward AUC over evaluation counts.

- `packet/paper/research/autonomous-thesis-to-prototype-20260908/README.md` · SHA-256 `68e281b339772ab44add809b2b0bdd78ea54200f222088d094f1a6869f5262a1` · LF [[19, 25]].
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.14354v2.txt` · SHA-256 `b2c31a916321e2c89c399c53ff26a3eaa582ae5743e089ba63cb1f0707bc151e` · LF [[350, 383], [532, 571], [920, 937], [1057, 1065]].
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2607.24647v1.txt` · SHA-256 `c5d3f2f9ce91d5c76b7eda74e133a56860fdcb2edcaf97dea5f1a20bfcc59020` · LF [[186, 213], [334, 352], [395, 424], [487, 502], [759, 780]].

### S6

CORE-Bench saturation is relevant to prototype validation: score, calculation path, repeated consistency and costs are different constructs. The synthesis correctly treats targeted-fix/rewrite and the oracle router as descriptive evidence and preserves legitimate partial computation.

- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0` · LF [[19, 19], [33, 33], [43, 43]].
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2606.26158v1.txt` · SHA-256 `d57377ecc52de3ac10fa7216b60c215ca632a47380500d28f885f037290799b2` · LF [[417, 449], [586, 621], [1292, 1308], [1311, 1359]].

## 서지·읽기 범위

현재 source manifests는 공개 preprint와 검증되지 않은 동료심사 게재지를 구분한다. 이번 검토에서 허위 venue 주장은 발견하지 않았으며, 일곱 편 모두의 최신 게재 상태를 따로 인증하지 않았다. Iris는 시스템명이고 정확한 원문 제목은 *Beyond Solution-Centric Search: Adaptive Inquiry and Knowledge Revision for Autonomous ML Engineering*이다. 내부 표의 약칭을 최종 학술 서지로 그대로 복사하지 않는다.

리뷰 계약·packet manifest와 아래 정적 문서는 전체 읽었다. 원문 논문은 아래 구간만 새로 확인했다. 이전 FULL_PAPER_READ 표시는 이번 완독으로 승계하지 않았다. 모든 경로는 이 리뷰 묶음 기준이며 SHA-256은 실제 입력 바이트에서 계산해 packet manifest와 대조했다.

- `packet/AGENTS.md` · 전체 문서 · SHA-256 `8c3ecdb00a0a21beb64fd9940bff28c94001a6d32625301ac8155e40e24d8455`.
- `packet/docs/argo/agent-brief.md` · 전체 문서 · SHA-256 `a76a9cfd7b1c0e877930c144dba446035c4c121b11324bb4bb759592c09fd14d`.
- `packet/docs/argo/migration-state.json` · 전체 문서 · SHA-256 `bb7105c7ce57e6f29d67b0f1e811b3128828f0fd3f0dfee2954d43d52f8e103e`.
- `packet/docs/argo/research-to-prototype-objective.md` · 전체 문서 · SHA-256 `f7c8b1d578f3f5ac4f1a85b7422d74a6e8def96bcbd80aad88578b3e019ddcd4`.
- `packet/docs/argo/research-decision-contract.md` · 전체 문서 · SHA-256 `07be81241e30682d913c5e3a34ba5fbf34478f51418127212b2d4d977edf94de`.
- `packet/paper/manuscript/AGENTS.md` · 전체 문서 · SHA-256 `0e925f4ddbd0a86d66664fed62b2cb7c3aac8192a4095ebb904a698943d95e15`.
- `packet/paper/research/ROOT-research-direction.md` · 전체 문서 · SHA-256 `77975cbb43d648df635f88784a08cdd625e85132150fcefb8a12ec7d7b4d7448`.
- `packet/paper/research/fable51-design-review-20260907/integration/integrated-study-design.json` · 전체 문서 · SHA-256 `f73eef99ba186f5882fc79a07e72c911d0d54ce8f85a4a7c08560e551940c72e`.
- `packet/metadata/current-p0-protocol.json` · 전체 문서 · SHA-256 `2e4ce502ae98280f8d43839cc11e43b26d66a149a89614a788165b5a0c0704bf`.
- `packet/metadata/current-operational-disposition.json` · 전체 문서 · SHA-256 `eed99338c83b70d6e149c7c1755b577233de32e9b38b05680e045195f1abb3a1`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/README.md` · 전체 문서 · SHA-256 `68e281b339772ab44add809b2b0bdd78ea54200f222088d094f1a6869f5262a1`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/decision-record.json` · 전체 문서 · SHA-256 `96ee5c2311156ece38123f577ea70aaa2d053dea6e23d538f87aa961c97b68a1`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/source-evidence.json` · 전체 문서 · SHA-256 `31f8e87e0b3270e62f9b1a140fd4d7f10de69f7982dd80d664699316661e31fa`.
- `packet/paper/research/exa-prior-art-expansion-20260908/README.md` · 전체 문서 · SHA-256 `32f1338571b818925e811f3c5820606129451b8c4d085a3cc8d549f20a0375f0`.
- `packet/paper/research/exa-prior-art-expansion-20260908/decision-update.json` · 전체 문서 · SHA-256 `95c3346a61715e9ad18619339d535e79cbf9a6cfd62902f0f44c1f4607aeda30`.
- `packet/paper/research/exa-prior-art-expansion-20260908/source-evidence.json` · 전체 문서 · SHA-256 `3ff020aae62e692b0b3a5957a729fe374cedbde01bbafc098bb5b4a97120f56c`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.02143v1.txt` · 원문 선택 구간 LF [[1, 65], [740, 900], [930, 1100]] · SHA-256 `120c15dda4a5da8e58f7c549bd185a7d73930c281efb0a7a369bb25e6c165eb6`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2607.24647v1.txt` · 원문 선택 구간 LF [[1, 65], [113, 163], [180, 214], [330, 430], [482, 508], [685, 743], [759, 782]] · SHA-256 `c5d3f2f9ce91d5c76b7eda74e133a56860fdcb2edcaf97dea5f1a20bfcc59020`.
- `packet/paper/research/autonomous-thesis-to-prototype-20260908/sources/2608.14354v2.txt` · 원문 선택 구간 LF [[1, 65], [350, 392], [513, 581], [920, 945], [1057, 1075]] · SHA-256 `b2c31a916321e2c89c399c53ff26a3eaa582ae5743e089ba63cb1f0707bc151e`.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2606.12563v1.txt` · 원문 선택 구간 LF [[1, 65], [270, 315], [445, 473], [553, 579]] · SHA-256 `9a5aacec255d3b8c6c38f57f310050661f45d0571ed7357a1882dc0a8f2d2bf7`.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.11248v1.txt` · 원문 선택 구간 LF [[1, 65], [240, 793], [795, 884], [940, 999], [1033, 1050], [1162, 1231]] · SHA-256 `e8f4e3ed925fcc5a4f5a88cae29b206355e5fec85bbc69b897d9651930001ff0`.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2606.26158v1.txt` · 원문 선택 구간 LF [[1, 65], [408, 454], [586, 637], [1241, 1380]] · SHA-256 `d57377ecc52de3ac10fa7216b60c215ca632a47380500d28f885f037290799b2`.
- `packet/paper/research/exa-prior-art-expansion-20260908/sources/2608.04738v2.txt` · 원문 선택 구간 LF [[1, 65], [70, 215], [320, 590], [600, 715], [1715, 1775], [2010, 2155], [2370, 2488], [2565, 2618]] · SHA-256 `18022dcc5adb3f3a5a214e240a1f1c8a63f16b82c487f9000fb5379b96e54cff`.

외부 읽기: arXiv 두 초록 페이지의 제목·저자·v1 제출 기록과 HTR HTML §4.2·§5.7. 정확한 URL과 browser line 범위는 `review.json`에 있다. 외부 원문 응답 파일은 별도로 저장하지 않았다.

## 독립성과 미확인 범위

새 모델 문맥과 별도 출력 소유권으로 수행했다. 다른 검토자 보고서를 읽거나 연락하지 않았고 중첩 위임도 하지 않았다. 모델 오류·ground truth가 독립이라는 뜻이나 OS sandbox 격리를 뜻하지 않는다. 지침 준수 중 memory registry의 키워드 탐색 항목은 보았으나 연결된 과거 recap·리뷰는 열지 않았고 이전 판정을 근거로 사용하지 않았다.

PDF·그림 육안 검증, 전체 154-source 색인, 완전한 선행 구현 조사, source acquisition의 독립적 진위 감사, 논문 최종 원고/서지/렌더, 코드·자격증명·자료·실험·표본수 설계·실행 승인은 검사하지 않았다. 문헌 저자 수치는 로컬 재현값이 아니다.

작성한 파일은 `literature/review.md`, `literature/review.json`뿐이다. 입력 해시는 일치했고 JSON을 파싱했다. 연구·모델 실행, 설치, 외부 쓰기는 없었다.
