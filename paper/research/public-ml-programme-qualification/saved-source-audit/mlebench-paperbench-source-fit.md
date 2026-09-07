# MLE-bench / PaperBench 저장 원문 P0 source-fit 감사

## 판정

**두 논문 중 어느 것도 그 자체만으로 모든 조건을 만족하는 단일 소규모-compute P0 과제를 인증하지 않는다.**

- **MLE-bench:** `CANDIDATE_INPUT__NOT_CERTIFIED`. 두 계열 중 원하는 형태에 더 가까운 **과제/채점 계약 후보**다. 오프라인 과제 묶음, 고정 CSV, 점수를 주지 않는 형식 검증기, 로컬 metric grader, 재구성 split 기록, 반복적 해법 선택을 제공한다고 논문은 설명한다. 그러나 구체적인 한 과제의 계정 없는 데이터 취득, 라이선스, split/label 비공개성, 채점기 결정성·독립성, 실제 경쟁 방법, artifact lock, 소규모 자원 상한은 원문만으로 인증되지 않는다.
- **PaperBench:** `DEFER_FOR_P0_TASK_SELECTION__REUSE_CONTRACT_IDEAS_ONLY__NOT_CERTIFIED`. fresh-VM 재실행과 `reproduce.sh` 경계는 재사용할 수 있다. 하지만 보고된 단위는 장시간·고비용의 전체 논문 복제이고, 서비스 credential을 전제하며, 최종 rubric 채점기는 저자들이 명시적으로 **비결정적**이라고 밝힌 LLM judge다. Code-Dev는 실행과 결과 재현을 생략하므로 ML outcome 대체물이 아니다.

따라서 이 감사에서는 구체 과제를 선택하거나 두 계열 밖 후보를 순위화하지 않았다. 논문에 보고된 medal/replication score는 로컬 campaign 검증 근거가 아니다. 공개 competition이라는 사실도 test가 모델 지식에서 숨겨졌다는 뜻이 아니다. 예상되는 G 우위로 과제를 고르지 않았다. 과거 MLE-Lite/GPU 실행은 승인되지 않은 이력으로 간주하여 feasibility, score, 예상 우위, P0 준비성 근거에서 배제했다.

## 출처와 완독 확인

고정 source commit: `4cd5d0e6ae7052a0a91682865e1bfabdc64c1d10`

| source | 저장 경로 | `git show` 바이트 SHA-256 | 완독 범위 | version |
|---|---|---|---|---|
| MLE-bench, arXiv 2410.07095 | `paper/sources/tex/2410.07095/sections/00_fulltext.txt` | `afac2ba2dbbb23d4dbcafd77fbec5b5bc0818df3ed7e7f4ecc0b0863a397a501` | 1–1408행 전체, 107,977 bytes | arXiv revision은 저장 receipt에 고정되지 않아 `NOT_VERIFIED_UNPINNED` |
| PaperBench, arXiv 2504.01848 | `paper/sources/tex/2504.01848/sections/00_fulltext.txt` | `9a6c828f8d1da9d1a06d404d96faf53bf7f4da6d0ddb73f1b7a5b92f4a57370b` | 1–1556행 전체, 111,768 bytes | arXiv revision은 저장 receipt에 고정되지 않아 `NOT_VERIFIED_UNPINNED` |

두 파일은 commit의 `git show` 내용과 현재 파일이 동일했다. `paper/sources/claim-locators.json` (`90ab65ed5f339907837ac85f0f8ccc1a671aad8d5f98d65cd310899a9ae0a38e`)의 관련 18개 locator에서 source hash, inclusive LF span text, excerpt hash를 모두 재계산했고 모두 일치했다. `paper/research/retrieval-record-0015.json` (`5d8acccd11c67f56e965d06c066cab47155c6335e404a4934d86eaa885cee4ce`)은 두 arXiv ID와 제목을 `VERIFIED`로 기록한다. 반면 `paper/sources/arxiv-source-receipts.json` (`5de698e5910a618c10a01e29dfaff79e5c0e9a5d0258952b525138e22a77c83c`)의 8개 항목에는 두 ID가 없다. locator는 무버전 `/e-print/<id>` 취득을 적었으므로 arXiv revision은 추정하지 않았다.

정확한 1-based LF 원문, 포함 행 범위, 범위별 SHA-256은 동반 JSON의 `evidence_spans`에 있다. 범위 hash 규칙은 `sha256(UTF-8 bytes of LF-joined inclusive logical lines, no trailing LF)`이다.

## 조건별 비교

| 요구 조건 | MLE-bench | PaperBench |
|---|---|---|
| 실제 ML 방법 경쟁 | 모델을 학습해 CSV 예측을 만들고, 방법에 독립적이며, AIDE가 해법을 탐색한다고 서술한다. 그러나 한 P0 과제의 실제 대안 방법과 feasibility는 미확인이다. | 현대 ML 실험을 복제하지만 단위가 전체 논문이다. 작고 결정적인 방법 경쟁 과제를 제공하지 않는다. |
| 이전 결과를 사용한 결정 | 성능과 valid CSV를 고려한 반복·snapshot·best-attempt 선택이 있다. 저자도 선택이 불완전하다고 보고한다. task-bound decision/selection rule은 없다. | piecemeal iteration은 있으나 rubric dependency가 완전하지 않다고 저자가 밝힌다. 숨긴 rubric은 개발 피드백으로 쓸 수 없다. |
| source/data ancestry | original/reconstructed split과 일부 split 방식을 문서화한다. 정확한 source bytes, generator commit, seed/indices, family registry는 미확인이다. | paper/addendum/blacklist와 fresh reproduction 경계는 있다. task-specific data/license/generator ancestry는 원문에서 인증되지 않는다. |
| 단일 agent-selected artifact | `/home/submission/submission.csv` 하나와 score-free validator는 좋은 형태다. 명시적 artifact ID/hash/time lock, missing-lock, hidden-score 전 lock은 없다. | 하나의 repository와 `reproduce.sh`를 task 종료 후 fresh VM으로 복사한다. agent 선택 기록, hash lock, mutation/fallback 규칙은 없다. |
| 독립·결정적 평가 | competition별 로컬 grading code와 metric을 제공한다고 논문은 말한다. 실제 코드의 결정성, label custody, trusted boundary는 확인하지 않았다. LLM log monitor는 primary scorer가 될 수 없다. | fresh reproduction은 독립성 아이디어다. 그러나 최종 SimpleJudge는 LLM이고 저자가 비결정적·expert보다 부정확하다고 명시한다. full PaperBench score는 부적합하다. |
| 소규모 compute | `Low`는 사람의 engineering 시간 추정이며 **훈련 시간을 제외**한다. 보고 setup은 24시간 A10/대형 RAM·disk이고 전체 평가는 1,800 GPU-hour다. 수치 P0 예산을 도출할 수 없다. | 전문가에게 최소 수일, agent 12시간 A10, o1 rollout 약 $400, judge 추가 비용이다. Code-Dev는 outcome 실행을 없앤다. |
| 계정/credential/비공개 데이터 없음 | 저자는 sensitive data가 없고 license를 고려했다고 말하지만, 필터는 Kaggle 외 다운로드만 금지한다. Kaggle 계정·토큰·click-through 없는 취득은 입증되지 않았다. | 필요한 온라인 서비스 key 제공을 규칙으로 명시하고 실험에서 HuggingFace/OpenAI key를 제공한다. selection filter만으로 credential-free/license/privacy가 입증되지 않는다. |
| hiddenness/leakage | validator는 점수를 주지 않지만, 공개 competition/solution과 공개 train에서 만든 test 때문에 memorization·label reconstruction 위험이 있다. 저자는 미래 모델에 보증하지 않는다. | rubric은 숨기지만 author code는 온라인에 있고 blacklist 검사는 문자열 검색+수동 검토다. 결정적 contamination 통제가 아니다. |

## MLE-bench에서 재사용할 수 있는 것

1. **과제 bundle:** description + dataset + grading code + leaderboard snapshot (`mle_task_components`, 577–594행, `e56bf4d67e84736ccc469956350ca4b3bd86f9e85258d05c75399ca456f87546`). 실제 P0에서는 leaderboard를 primary scorer로 쓰지 말고 source/data/generator hash와 license/privacy를 추가해야 한다.
2. **score-free validator:** CSV 형식 오류만 돌려주고 score를 감춘다 (`mle_artifact_and_score_free_validator`, 625–630행, `5a90c36b6b8f1c65535d6c0d9158ca760612ea8964e21a17df0f6f77f2b85291`).
3. **단일 산출물 표면:** 학습한 모델의 예측을 `/home/submission/submission.csv`에 둔다 (`mle_training_and_final_csv_contract`, 1008–1025행, `59eb46089c3f341b1ff1b57e75085fa4c9a280b72bc0eb4232c3aec04a103b1e`). P0에서는 agent가 선택한 ID/hash/time을 hidden scoring 전에 잠가야 한다.
4. **selection 실패를 endpoint로 보존:** 성능과 valid CSV를 함께 보는 선택 규칙이 있어도 저자는 best-attempt 선택이 불완전하다고 보고했다 (`mle_time_snapshots_and_imperfect_selection`, 740–743행; `mle_aide_selection_criteria`, 1033–1045행).
5. **ancestry 표면:** original/reconstructed split과 competition별 split note는 출발점이다. 하지만 공개 원 train label과 공개 split recipe로 hidden label을 복원할 수 있는지는 코드·데이터 바이트에서 별도 검사해야 한다.

MLE-bench의 `Low` 22개와 별도 development 7개는 **candidate pool 표지**일 뿐이다. 논문은 development 7개의 정확한 과제 목록과 계약을 이 저장 원문에서 제시하지 않는다. `Low`도 훈련 시간을 제외하므로 어느 한 과제도 여기서 `small-compute`로 인증하지 않았다.

## PaperBench에서 재사용하거나 버릴 것

재사용 후보는 두 가지뿐이다.

- task 종료 후 submission을 fresh VM으로 복사하고 `reproduce.sh`를 실행하는 **fresh-copy replay** (`paperbench_task_hidden_rubric_fresh_reproduction`, 136–148행, `06a7855966c0f23fd9fd87fbe6d1c3b8ae7ddc94e7d21fe974bc16a59e57ed7d`). 이를 쓰려면 먼저 repository hash를 잠그고 network 없는 dependency closure와 deterministic result parser를 추가해야 한다.
- Code Development / Execution / Result Match를 분리하는 **failure taxonomy** (`paperbench_hierarchical_scorer`, 150–185행). primary 효능은 여전히 하나의 hidden ML metric이어야 하고, rubric partial credit은 process 진단으로만 쓸 수 있다.

버리거나 보류할 것은 다음과 같다.

- **SimpleJudge:** human-gold F1 0.83이라는 보고는 결정성을 만들지 않는다. 저자는 judge가 비결정적이고 expert보다 부정확하다고 명시한다 (`paperbench_author_limitations`, 543–555행, `885b99118a75373c0dffa7d8cea9fd19302536873f0562ffb66a0ec6b86980b6`).
- **Code-Dev:** GPU를 줄이지만 실행과 Result Match를 생략하고 full score와 약한 상관만 보인다 (`paperbench_codedev_tradeoff`, 217–223행).
- **전체 논문 복제:** 논문 스스로 unstructured output을 programmatically grade할 수 없다고 적는다 (`paperbench_programmatic_score_not_viable_for_full_scope`, 528–536행). 이것을 작은 결정적 ML outcome scorer로 바꾸었다고 간주하면 안 된다.
- **credential 전제:** 필요한 key 제공이 규칙이고, 보고 실행은 HuggingFace/OpenAI credential을 준다 (`paperbench_rules_credentials_and_monitor`, 204–215행; `paperbench_api_key_and_runtime_template`, 1537–1545행).

## N1–N10 연결

- **N1/N3:** 이번 작업은 문서·hash 감사와 두 산출물 작성뿐이다. 실제 task training, selection-performance evaluation, scorer 호출은 R1이며 실행 승인으로 간주하지 않았다.
- **N2:** 두 논문 모두 trusted common launch/lock gate와 완전한 bypass census를 입증하지 않는다.
- **N4:** 구체 과제와 outcome이 없으므로 MUE 값/규칙은 아직 `UNAVAILABLE`이다. 논문 수치에서 만들지 않는다.
- **N5:** CSV 또는 repository를 artifact class로만 재사용한다. agent 선택, lock, hash, timestamp, no-lock/fallback, mutation 금지는 task contract에서 새로 고정해야 한다.
- **N6/N7:** attempt, lock, scorer, numerical observability와 campaign/scorer/artifact/no-lock 실패를 분리하고 retry/repair/no-replacement를 사전 고정해야 한다.
- **N8:** 두 benchmark의 발표 성능은 ARGO whole-system 인과 효과가 아니다.
- **N9:** 선택한 P0 programme/task/source-data/generator family를 development ancestry로 등록하고 P2에서 제외해야 한다.
- **N10:** P0가 실행되지 않았으므로 latency, UNKNOWN/BLOCKED, gate bypass, scorer defect, 비용은 모두 `NOT_OBSERVED`이며 0이 아니다.

## root가 실제 공개 코드·데이터에서 다음에 확인할 것

### MLE-bench

1. 정확한 public repository commit/tag, code license, task registry와 development split 목록.
2. 후보별 원본 URL·byte hash·크기·privacy class·data license/terms·재배포 권한. 계정, API token, click-through, private access 없이 취득 가능한지.
3. preparation/split 코드의 commit, seed/indices, group/time/entity 경계, source-data/generator ancestry. 공개 원 label/recipe로 nominal hidden test를 복구할 수 있는지.
4. grader/validator 실제 코드. validator가 형식만 반환하는지, scorer가 hidden label byte에서 metric을 재도출하는지, 동일 입력 결정성, network/model/human 없음, dependency 고정, 오류/결측 처리, agent와 분리된 trusted boundary.
5. baseline과 최소 두 개의 실제 경쟁 ML 방법. public/dev 결과를 보고 다음 결정을 할 수 있는지. 자원은 별도 승인된 측정 전에는 숫자로 정하지 않는다.
6. 최종 CSV eligibility/schema, agent-selected ID/hash/time lock, hidden score 전 잠금, no-lock/invalid/scorer-failure/crash/fallback/mutation/retry/no-replacement 규칙.
7. P0 ancestry 등록과 P2 family 제외.

### PaperBench를 좁은 아이디어 원천으로 다시 볼 경우

1. exact code commit/license와 per-paper addendum/rubric/blacklist/data/model dependency.
2. SimpleJudge가 아니라 result byte에서 재도출 가능한 task-specific deterministic ML metric이 있는지.
3. credential, private/unstable data, unrestricted browsing, nondeterministic service, 장시간 GPU가 모두 제거되는지.
4. fresh-copy replay 전에 artifact hash lock과 offline dependency closure가 가능한지.
5. author-code/pretraining contamination을 문자열 blacklist보다 강한 ancestry 통제로 다룰 수 있는지.

이 확인이 끝나도 actual P0 실행 전에는 task identity, ancestry, split surfaces, scorer bytes, environment/command, resource envelope, selection rule, N2–N10 처리표를 동결한 task-bound review와 정확한 사용자 실행 승인이 별도로 필요하다.

## 주장 경계와 비실행 확인

위 내용은 모두 저장 논문 원문의 주장 또는 그 주장으로부터의 제한된 source-fit 판정이다. **공개 MLE-bench/PaperBench 코드, license 파일, task registry, dataset, generator, grader, validator, rubric, addendum, container, trace는 읽거나 실행하지 않았다.** 그러므로 실제 runtime 동작은 인증하지 않는다.

외부 retrieval/download, 계정/credential/private data 접근, dependency install, model/scientific/ML/train/eval/scorer/test/fixture run, subagent, native/manuscript edit, git commit은 수행하지 않았다.
