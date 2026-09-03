# Paper session questions to supervisor

Q 형식: `## Q-000N` 제목 아래 6필드(id/시각, 근거 경로, 옵션과 수치 영향, 권고, 미답변 시 기본값, blocking 여부). 답변은 supervisor가 `[ANSWERED …]`로 표기한다.

## Q-0001 — 졸업 학기와 학과 실제 계획서 마감일 [ANSWERED 2026-09-02 14:39 KST]

- **id/시각:** Q-0001 / 2026-09-02 14:06 KST
- **근거 경로:** `paper/official-thesis-requirements.md`, `paper/official-thesis-requirements.json`
- **옵션과 수치 영향:** (A) 후기 졸업·2026-09-30 이전 제출: 현재 기본 일정 유지. (B) 전기 졸업·3월 31일 이전 또는 학과 별도일: 계획서·실험·집필 마일스톤 전체를 해당 날짜 기준으로 이동. 정확한 학과일이 있으면 날짜 1개를 제공.
- **권고:** 사용자에게 졸업 학기와 AI학과 실제 계획서 제출일을 확인한다.
- **미답변 시 기본값:** 후기 졸업, 계획서 마감 `2026-09-30`으로 두고 초안을 계속 준비한다.
- **blocking 여부:** false — 계획서 초안과 자율 연구 설계는 기본값으로 계속 진행.
- **answer:** 학과 계획서 제출 마감은 `2026-10-31`. 현재 학기 가정은 유지하고 모든 계획서·실행 일정의 기준일을 10월 31일로 변경.

## Q-0002 — 참조 구현 위에서 검증할 수 없는 목표 기능의 처리 [ANSWERED 2026-09-02 14:39 KST]

- **id/시각:** Q-0002 / 2026-09-02 14:21 KST
- **근거 경로:** `paper/research/capability-map.md`, `docs/argo/migration-state.json`, `paper/supervisor/instruction-0002e.md`
- **옵션과 수치 영향:** (A) 기본값: personalized-memory 권리/삭제, 완전한 MCP 수명주기, 복수 vector DB backend, provider registry/fallback, 동적 모델 라우팅, native daemon 변경의 6개 기능군을 이번 주기 “설계만/후속”으로 유지하고 10개 연결 기능만 검증. (B) 추가 개발 허용 범위를 기능군별로 지정하면 조건·구현·실행 수가 증가하며 Study A 4조건과 별도 실험이 필요.
- **권고:** 이번 논문 주기에는 (A)를 유지한다. 현재 핵심 가설의 식별 가능성과 640,000-token instrument-pilot 상한을 보존한다.
- **미답변 시 기본값:** (A) 설계만/후속으로 진행하며 새 native 런타임은 만들지 않는다.
- **blocking 여부:** false — Study A 설계와 문헌 지도는 계속 진행.
- **answer:** 권고안 (A) 채택. 6개 기능군은 이번 주기 설계만/후속으로 유지하고 새 native 런타임을 만들지 않는다.

## Q-0003 — Study C 실행 자원 승인 여부 [ANSWERED 2026-09-02 21:54 KST]

- **id:** Q-0003
- **question:** 실행 채점 기반 Study C를 위해 GPU 1장과 과제당 약 24시간의 컨테이너 실행 자원을 확보할 것인가?
- **why_it_matters:** 설계 점수 우위가 실행 결과로 이어지는지 확인하는 유일한 경로다. 확보 전에는 Study A 결론이 설계 산출물로만 한정된다.
- **options:** (a) 자원 확보 후 Study C 실행 (b) 현행대로 설계 전용 Study A만 진행하고 Study C는 RUNBOOK 상태로 보류
- **default_if_unanswered:** (b) 보류. 근거 `RD-2026-09-02-08A`, RUNBOOK `paper/research/study-c-runbook.md`.
- **blocking:** false — 기본값으로 진행해도 되돌릴 수 없는 손실이 없다. 적용됨.
- **asked_at:** 2026-09-02T21:41:37+09:00
- **answer:** 권고대로 진행. 사용자 원문 "권고대로 진행해. gpu가 필요할때는 colab cli 사용해." 해석: 지금은 기본값 (b)대로 설계 전용 Study A를 계속하되, Study C의 상태는 "자원 미확보"가 아니라 "Colab CLI(L4) 경로 확보, 실행 전 사전등록 필요"로 바꾼다. GPU가 필요한 단위는 supervisor instruction #0006의 규칙(사전등록, est_CU, cost-ledger, 세션 종료 확인)에 따라 `colab` CLI로 실행한다. 첫 GPU 실행 전에 예상 CU와 실행 계획을 Q로 올린다(blocking: true, 비용 지출).

## Q-0004 — 파일럿 귀인 분과에서 과제 2건 소모 승인 [ANSWERED 2026-09-02 21:54 KST]

- **id:** Q-0004
- **question:** 아이디어 실패와 구성 실패를 분리하기 위해 파일럿에서 과제 2건에 목표 아이디어 한 문장을 공개하고 그 과제를 확증 실험에서 영구 제외해도 되는가?
- **why_it_matters:** 공개된 과제는 오염되어 재사용할 수 없으므로 확증용 과제 풀이 2건 줄어든다.
- **options:** (a) 승인하고 2건 소모 (b) 귀인 분과 없이 파일럿 진행
- **default_if_unanswered:** 답변 전까지 귀인 분과만 보류한다. 근거 `RD-2026-09-02-08C`, locator `researchgym_integrity_and_resources`.
- **blocking:** true — 기본값으로 진행하면 확증용 과제 2건이 영구 소모된다. 나머지 파일럿 전제 구축은 계속한다.
- **asked_at:** 2026-09-02T21:41:37+09:00
- **answer:** (a) 승인. 파일럿 귀인 분과에서 과제 2건에 목표 아이디어 한 문장을 공개하고 그 2건은 확증 실험에서 영구 제외한다. 소모한 과제 id를 research-design.md와 status.md에 기록한다.


## Q-0005 — 첫 GPU 실행 승인 [ANSWERED 2026-09-02 22:08 KST]

- **id:** Q-0005
- **question:** Study C 첫 GPU 단위를 호스티드 노트북 CLI에서 실행해도 되는가? 사전등록(목표·고정 명령·입력 sha·est_CU·중단 규칙·체크포인트 계획)과 비용 원장 행을 먼저 커밋한다.
- **why_it_matters:** GPU 실행은 compute unit을 실제로 소비하며 되돌릴 수 없다. 현재 누적 사용량은 0 CU다.
- **options:** (a) 사전등록 검토 후 승인 (b) 파일럿 전제와 16-episode 파일럿을 모두 마칠 때까지 보류
- **default_if_unanswered:** (b) 보류. Study A와 그 전제는 GPU가 필요 없으므로 루프는 멈추지 않는다.
- **blocking:** true — 기본값 실행 시 compute unit이 소비된다. 단일 10 CU 또는 누적 25 CU 초과 전 별도 승인이 필요하다.
- **asked_at:** 2026-09-02T21:52:42+09:00
- **answer:** (b) 보류. 파일럿 전제와 16-episode 파일럿은 GPU 없이 끝낸다. 파일럿 완료 후 사전등록(목표·고정 명령·입력 sha·est_CU·중단 규칙·체크포인트)과 cost-ledger 행을 커밋한 뒤 새 Q로 다시 올린다. 이 Q는 더 이상 blocking이 아니며 루프를 멈추지 않는다.


## Q-0006 — 교정 라벨 25건 수집 요청 (양식 완성됨) [ANSWERED 2026-09-03 05:17 KST — (a) 25건 기입]

- **id:** Q-0006
- **question:** `paper/experiments/calibration/label-form.json`의 **25개** 항목에 blind 라벨(satisfied / not_satisfied / unclear)을 기입해 줄 수 있는가? 프로토콜은 `paper/research/human-label-protocol.md`다. 각 항목은 `label_id`, 요구사항 한 줄, 후보 구절만 담고 있으며 판정기의 판단과 신뢰도는 들어 있지 않다.
- **why_it_matters:** 판정 채점은 교정 없이는 아무 것도 승인되지 않는다. 라벨이 없으면 1차 지표는 결정론 층으로만 제한된다. 25건 무결 라벨이면 95% 신뢰도에서 위험 10%를 인증한다.
- **options:** (a) 25건 라벨 기입 (b) 라벨 없이 진행하고 판정 채점을 영구 보류
- **default_if_unanswered:** (b) 보류하고 루프는 계속한다. 신뢰도 하한 0.9는 라벨과 무관하게 이미 적용된다.
- **blocking:** false — 기본값으로 진행해도 되돌릴 수 없는 손실이 없다.
- **asked_at:** 2026-09-03T00:03:13+09:00
- **updated_at:** 2026-09-03T00:40:40+09:00
- **status:** 양식이 완성되어 대기 중이다. 저신뢰 층 3건을 보충해 25건(>0.9 10건 / 0.7-0.9 10건 / <0.7 5건)이 됐고, 모든 항목이 동일한 필드 집합을 갖도록 고쳤다. 항목에 판정 결과가 새지 않는지 기계로 확인했다. 라벨이 없는 동안에도 루프는 기본값으로 계속 진행한다.
- **supervisor_note (2026-09-03 05:25 KST):** 사용자에게 전달됨(라벨은 사람만 기입 가능). 답변 전까지 기본값 (b) 유지, 루프 계속. instruction-0009 §7 참조.
- **answer (2026-09-03 05:17 KST):** (a). 사용자가 05:08 KST에 "Q-0006 교정 라벨 25건 니가 직접진행해 승인할게"로 supervisor에게 기입을 위임했다. `paper/experiments/calibration/label-form.json`의 25개 항목에 `answer`/`labeller`/`labelled_at`/`notes`를 기입했다(satisfied 14 / not_satisfied 5 / unclear 6). 라벨러는 사람이 아니라 supervisor 모델(claude-fable-5-1, Claude Code supervisor 세션)이며, 판정기(huggingface/Qwen3.6-27B, GLM-5.3)와 처치 모델(anthropic/claude-haiku-4-5)과는 다른 모델·제공자 계열이다. 이 사실을 논문 본문과 receipt에 그대로 공개할 것("human-anchored"라는 표현은 쓰지 말 것). unclear 6건은 프로토콜대로 제외·별도 집계하므로 무결 라벨은 19건이며, 25건 요건을 채우려면 같은 층화로 추가 항목을 뽑아 supervisor에게 보내야 한다. 2차 라벨러 중복(20% 이상) 결과와 세부 절차는 instruction-0010 §2 참조.


## Q-0007 — 완료율 정밀도를 위한 116 에피소드 블록 실행 승인

- **id:** Q-0007
- **question:** 예산 완료율의 신뢰구간 반폭을 0.15까지 좁히려면 조건당 29 에피소드, 총 116 에피소드가 필요하며 측정된 에피소드당 비용 $0.1576로 약 $18.28가 든다. 이 블록을 실행해도 되는가?
- **why_it_matters:** 현재 조건당 4 에피소드에서 반폭은 0.327이고 네 구간이 모두 겹친다. 그 상태로는 완료율 차이를 확인할 수도, 배제할 수도 없다. 지금까지 이 프로젝트의 누적 모델 비용은 약 $3이므로 $18은 그보다 6배 크다.
- **options:** (a) 116 에피소드 블록 실행 (b) 실행하지 않고 요구 사항만 기록 (c) 중간 규모로 축소 실행
- **default_if_unanswered:** (b). 요구 사항은 재현 가능한 코드로 기록됐고, 정밀도가 부족하다는 사실은 논문에 이미 명시돼 있다. 승인 없이 기존 지출의 6배를 쓰지 않는다.
- **blocking:** false — 기본값으로 진행해도 되돌릴 수 없는 손실이 없으며 루프는 계속된다.
- **asked_at:** 2026-09-03T03:33:28+09:00
- **supervisor_note (2026-09-03 05:25 KST):** 사용자에게 전달됨(지출 승인은 사용자 권한). 답변 전까지 기본값 (b) 유지, 루프 계속. instruction-0009 §7 참조.

## Q-0008 — 그림 생성 경로 (image generation route)

- **질문:** 세션 환경에 이미지 생성 자격증명이 없다. 그림 9장을 어떤 경로로 만들 것인가?
- **대안:** (a) 사용자가 OpenAI API 키를 세션 환경에 제공한다. (b) 사용자가 ChatGPT에서 `paper/figures/specs/fig-NN.prompt.txt`로 생성해 `paper/figures/incoming/`에 PNG를 넣는다. (c) 결정론적 벡터 경로(Graphviz)만으로 진행한다.
- **검토한 사실:** `paper/figures/image-route-receipt.json` — 자격증명 없음, 요청 미전송, 키 값은 읽지도 기록하지도 않았다. `dot` graphviz 14.1.5와 `tesseract` 5.5.2는 설치되어 있다.
- **기본값:** **(c)**. 기본값으로 즉시 진행한다. blocking=false.
- **근거:** (c)는 저장소 안에서 결정론적으로 재생성되고 clean-clone에서 바이트 동일하게 검증된다. 이는 이 프로젝트의 재현성 기준에 이미지 모델 경로보다 잘 맞는다. (a)나 (b)가 오면 같은 스펙에서 경로만 바꾸고 원장에 route를 기록한다.
- **되돌리는 조건:** 사용자가 (a) 또는 (b)를 선택하면 스펙 변경 없이 경로만 교체한다.
- **상태:** OPEN, 기본값으로 진행 중 (2026-09-03T05:11:47+09:00)

### Q-0006 갱신 (2026-09-03) — 답변 수령

- **답변:** (a). 25건 기입 완료. **라벨러는 사람이 아니라 supervisor 모델**이므로 논문·receipt 어디에서도 `human-anchored`로 쓰지 않고 `supervisor-model-anchored calibration set`(감독 모델 기준 교정 세트)으로만 부른다.
- 분포 satisfied 14 / not_satisfied 5 / unclear 6. **판정 가능 라벨 19건**, 요건 25건에 **6건 부족**.
- 2차 blind 일치도(세션이 두 파일에서 **직접 재계산**, 지시문 수치를 옮기지 않음): 전체 24/25, unclear 제외 18/18. 불일치 L022(satisfied vs unclear). 정지 조건 미해당.
- `supplement_ready: paper/experiments/calibration/label-form-supplement-001.json` — **8건**, 동일 층화(seed 20260903, >0.9:3 / 0.7-0.9:3 / <0.7:2), verdict·confidence 미포함. supervisor 기입 대기.
- 판정 채점은 여전히 **inadmissible**: 라벨 부족과 기준이 사람이 아니라는 두 이유 모두.


## Q-0009 — 하네스 대 하네스 비교 실험 arm 실행 여부 (harness-comparison arm)

- **질문:** 결정론적 검증기(테스트 통과, 점수)를 사용하는 하네스 대 하네스 비교 실험(`paper/research/harness-comparison-arm-design.md`)을 실제로 실행할 것인가?
- **대안:**
  - (a) 실행 승인: 최소 검출 가능 설계(80 에피소드, 예상 $14.60) 또는 예산 절반 스크리닝(40 에피소드, 예상 $7.30)을 사전등록 후 실행.
  - (b) **실행하지 않음 (기본값)**: 설계 및 비용 산정 문서만 유지하고 에피소드는 일체 실행하지 않음.
- **검토한 사실:**
  - 본 논문의 주 기여는 성능 우월성 주장이 아니라 계측 규율과 도구 반증 결과임.
  - 선행 연구[@primeagent2026]의 유사 관찰(하네스 차이가 실험 잡음에 비해 작음)이 이미 문헌에 존재함.
  - 언어모델 판정기를 쓰지 않아 판정 비용은 $0.00이나 에이전트 실행 토큰 비용($7.30~$14.60)과 GPU 시간이 소요됨.
- **기본값:** **(b) 실행하지 않음**. 기본값으로 즉시 진행하며, 에피소드 실행이나 외부 벤치마크 과제 다운로드를 일체 진행하지 않는다.
- **되돌리는 조건:** 사용자가 명시적으로 (a)를 선택할 경우, 사전등록을 먼저 동결한 후 Colab GPU 환경 승인을 거쳐 실행한다.
- **상태:** **APPROVED (a) — 사용자 2026-09-03 10:47 KST — n=40×3과제×3아암, 상한 $48.47** (2026-09-03T10:53:45)
- **승인 범위 (instruction-0014 §1):** B0 / B1 / B2 **3아암**, `study-b-preregistration.md` §4 과제군, §5 endpoint.
- **미승인 유지:** 절제 4아암(B2−G/−P/−R/−L), 시나리오 (b)·(c), Q-0007 별도 지출, MLE-bench Lite.
- **지출 상한 확정 (instruction-0014a):** 스크리닝 $48.47(360 에피소드), 드라이런 $2 별도. 모델 `anthropic/claude-haiku-4-5` 고정.
  승인 기록: `paper/research/q0009-approval.json`. 상한 도달 시 즉시 중단, 완료 에피소드만 보고.
- **봉인:** 0014a 수신 후에 한다. 그 전까지 미완 항목 폐쇄·드라이런·해커톤 산출물을 진행한다.

## Q-0010 — 철회 (instruction-0015c, 기록 대상 아님)
