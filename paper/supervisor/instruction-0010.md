# Supervisor instruction #0010 — gpt-image-2 경로 개통, Q-0006 라벨 전달, Hugging Face 크레딧 회계

- 발신: Claude Code supervisor
- 시각: 2026-09-03 05:40 KST
- 대상: argo-paper-root
- 근거: status.md cycle 59(2026-09-03 05:11), `paper/figures/image-route-receipt.json`(route_available=false, Graphviz 기본 경로 진행 중), `paper/experiments/calibration/label-form.json`(25건 기입 완료), `paper/experiments/*receipt.json`의 judge 필드, 사용자 지시 2026-09-03 05:08 KST
- 선행 지시: instruction-0009(양식·한글 본문·그림 최대화)는 전부 유효하다. 이 지시는 0009의 §5(그림 생성 경로)와 §7(Q-0006)을 갱신하고 비용 회계 규칙을 추가한다.

## 0. 요약

1. gpt-image-2 자격 증명이 준비됐다. 그림 9종을 gpt-image-2로 다시 생성하고 Graphviz 렌더는 fallback 산출물로 보관한다.
2. Q-0006은 (a)로 답변됐다. 25건 라벨이 양식에 기입돼 있다. 라벨러는 사람이 아니라 supervisor 모델이다. 이 사실을 논문과 receipt에 그대로 쓴다.
3. Hugging Face 크레딧은 이 세션의 판정기 호출(`huggingface/Qwen3.6-27B`, `huggingface/GLM-5.3`)이 소비하고 있다. 모든 HF 호출을 cost-ledger에 USD로 기록하고 누적 상한을 둔다.

## 1. gpt-image-2 생성 경로 (instruction-0009 §5 갱신)

### 1.1 자격 증명 사용 규칙

- 키 파일: `~/.config/argo/openai-image.env` (내용은 `OPENAI_API_KEY=...` 한 줄, 권한 600). 사용자가 2026-09-03 05:08 KST에 등록을 지시했고 supervisor가 `GET /v1/models`로 검증했다. 사용 가능 모델: `gpt-image-2`(스냅샷 `gpt-image-2-2026-04-21`), 예비 `gpt-image-1.5`.
- 키는 **이미지 API를 호출하는 그 단일 셸 명령 안에서만** 읽는다. 예: `set -a; . ~/.config/argo/openai-image.env; set +a; python3 experiments/figures/render_image_api.py --figure fig-01`. 스크립트는 `os.environ["OPENAI_API_KEY"]`를 요청 헤더에만 쓴다.
- 금지: 키 값을 `echo`/`printenv`/`env`로 출력, 로그·receipt·JSON·커밋에 기록, 다른 파일로 복사, `.env`를 워크트리 안에 만들기, 세션 전역 환경에 export한 채 다른 명령 실행. receipt에는 `credential_source: "~/.config/argo/openai-image.env (value never read into records)"`만 적는다.
- `paper/figures/image-route-receipt.json`을 갱신한다: `route_available: true`, `models_endpoint_http_status`, 사용 모델 id, 확인 시각. `env_variable_names_present`는 이름만.

### 1.2 생성 절차 (0009 §5의 규칙 유지)

- 요청: `POST https://api.openai.com/v1/images/generations`, `model: gpt-image-2`, 크기 1536x1024(가로 블록도) 또는 1024x1024, 프롬프트는 `paper/figures/specs/fig-NN.prompt.txt` 그대로("IEEE-style academic technical block diagram, strictly black and white, clean vector line art, white background, … Labels exactly as written:" 형식). 파라미터 이름이 거부되면 API 오류 메시지의 허용 값에 맞춰 수정하고 그 오류 본문을 receipt에 남긴다. 추측으로 파라미터를 늘리지 않는다.
- 후처리: PNG → 벡터화(potrace 또는 vtracer) → OCR 라벨 게이트(tesseract, 스펙 라벨 일치율 ≥ 0.9, 최대 3회 재생성) → 통과본을 `paper/figures/rendered/fig-NN.image.svg`로 저장. 실패 시 현재 Graphviz 렌더(`fig-NN.svg`)를 그대로 채택하고 ledger의 `route`에 `vector_fallback_after_image_failure`와 실패 사유를 적는다.
- `figure-ledger.json`의 각 항목에 `route`(`gpt-image-2` | `graphviz` | fallback 사유), `output_path`, `output_sha256`, `ocr_label_match`, `image_request_id`, `usd`를 채운다. 9개 모두 `route != pending`이 될 때까지 form workstream이 우선이다.
- 비용: 이미지 호출마다 cost-ledger에 행을 추가한다(모델, 크기, 품질, 재생성 회차, USD). 이미지 누적 USD가 10을 넘으면 Q를 올리고 멈춘다.
- 논문 본문에는 그림 생성 도구를 "이미지 생성 모델"로만 적고 벤더·제품명은 쓰지 않는다(0009 §2·§9의 명칭 규칙). 그림 안 라벨은 영어, 캡션은 한글(`그림 n. 제목`).

## 2. Q-0006 답변 전달 — 교정 라벨 25건

### 2.1 사실

- 사용자가 2026-09-03 05:08 KST에 "Q-0006 교정 라벨 25건 니가 직접진행해 승인할게"로 supervisor에게 기입을 위임했다. 05:17 KST에 `paper/experiments/calibration/label-form.json`의 25개 항목에 `answer`, `labeller`, `labelled_at`, `notes`를 기입했다. 상위 필드와 `_blinded_key`는 건드리지 않았다.
- 분포: satisfied 14 / not_satisfied 5 / unclear 6. unclear 항목: L004, L006, L014, L018, L020, L025.
- 라벨러: `supervisor-model: claude-fable-5-1 (Claude Code supervisor 세션, 사람 아님)`. 판정기(`huggingface/Qwen3.6-27B`, `huggingface/GLM-5.3`)·처치 모델(`anthropic/claude-haiku-4-5`)과 모델·제공자 계열이 다르다. supervisor는 `label-key.json`, 판정 verdict, confidence를 읽지 않았다(blind 유지).
- 2차 라벨러: 독립 서브에이전트(`claude-opus-5`, supervisor의 답을 보지 못함)가 25건 전부를 blind로 재라벨했다. 결과 파일 `paper/supervisor/label-second-pass.json`. 일치도: 25건 전체 24/25, unclear가 하나라도 있는 쌍 제외 18/18, 프로토콜 20% 중복(시드 20260903, L005, L008, L009, L015, L021) 5/5. 불일치: L022(supervisor satisfied / 2차 unclear). 파일 sha256 5247fb1c7ae84557…. 프로토콜 정지 조건(일치도 < 0.90)에 걸리지 않는다.

### 2.2 세션이 할 일

1. **명칭 정정.** 이 세트는 "human-anchored"가 아니다. 모든 receipt·decision record·논문 본문에서 "supervisor-model-anchored calibration set"(국문: "감독 모델 기준 교정 세트")로 적고, 라벨러가 사람이 아닌 모델이며 판정기·처치 모델과 다른 제공자 계열이라는 점, 사용자가 이를 승인했다는 점을 명시한다. 위협·한계 표에 "교정 기준이 사람이 아닌 모델"을 한 행으로 넣는다. `human-label-protocol.md`는 편집하지 말고, 새 문서 `paper/research/calibration-anchor-disclosure.md`에 차이를 적는다.
2. **수령 receipt.** `paper/experiments/calibration/labels-received-receipt.json`을 만든다: 새 `form_sha256`, 라벨 분포, 라벨러 문자열, 2차 라벨 파일 sha256과 일치도, blind 확인(라벨 기입 전후로 item 필드 집합이 동일, key 미노출).
3. **unclear 처리.** 프로토콜대로 unclear 6건은 교정 세트에서 제외하고 별도 집계한다. 무결 라벨은 19건이므로 25건 요건에 6건이 모자란다. 같은 층화 규칙(신뢰도 층 비율 유지, 파일럿 제외, 시드 기록)으로 **보충 항목 8건 이상**을 뽑아 `paper/experiments/calibration/label-form-supplement-001.json`(동일 스키마, 판정 verdict·confidence 미포함)을 만들고 questions.md의 Q-0006 아래에 `supplement_ready` 줄을 추가해 supervisor에게 알린다. supervisor가 같은 방식으로 기입한다.
4. **2차 일치도 판정.** 프로토콜의 정지 규칙(중복 일치도가 인증하려는 위험 수준보다 낮으면 정지)을 그대로 적용한다. 일치도는 unclear를 제외한 쌍과 포함한 쌍 두 가지로 보고한다. 정지 조건에 걸리면 판정 채점은 계속 inadmissible로 두고 그 사실을 status.md 첫 줄에 쓴다.
5. **선택적 평가기 실행.** 정지 조건에 걸리지 않으면, 라벨을 보지 않은 채 이미 기록된 판정 verdict·confidence(key)와 라벨을 결합해 오류율 상한(UCB) 기반 임계값을 계산한다. 25건 무결 라벨이 채워지기 전에는 "인증"이라는 단어를 쓰지 않고 예비 추정으로만 보고한다.
6. **재라벨 금지.** supervisor의 라벨을 수정하거나 재요청하지 않는다. 교정이 필요하면 프로토콜대로 사유와 함께 새 레코드를 추가한다.

## 3. Hugging Face 크레딧 회계

### 3.1 발견

- 이 세션이 2026-09-02 13:12 KST부터 엔진의 `huggingface` 제공자(`router.huggingface.co/v1`, Inference Providers)로 판정기 호출을 보내고 있다. 모델·데이터셋 다운로드는 무료이고, 크레딧은 이 추론 호출이 소비한다.
- 호출 흐름(세션 기록 기준): 13:12 백엔드 프로브(`Qwen3.6-27B`, 이후 `GLM-5.3`, `DeepSeek-V4-Pro`) → 15:39 verified endpoint 192건 요소 판정(모델 판정 174) → 17:17 판정기 신뢰도 세트 78회 호출(Qwen + GLM) → cycle 55 span/full 비교 6회 → cycle 56 whole-artifact 48건 → 01:34 replay 24건 → 01:46 mid-band 50회(10×5). 이후 사이클의 판정도 같은 경로다.
- cost-ledger.md에는 처치 모델(anthropic) 비용만 USD로 있고 HF 판정기 비용 행이 없다.

### 3.2 규칙

1. **receipt 소급.** 위 호출 각각에 대해 HF 응답의 usage(입력·출력 토큰)와 제공자 단가로 USD를 추정해 cost-ledger.md에 "Hugging Face 판정기" 절을 만든다. 단가 출처(제공자 가격표 URL 또는 응답 헤더)를 적고, 불확실하면 보수적 상한값을 쓰고 가정임을 명시한다. 누적 HF USD를 status.md 헤더에 둔다.
2. **앞으로의 모든 HF 호출**은 receipt에 `provider: huggingface`, 호출 수, 토큰, USD를 남긴다. 
3. **상한.** 2026-09-02 13:12 이후 누적 HF 추정 USD가 10을 넘으면 새 HF 호출을 멈추고 Q를 올린다(6필드 형식, 기본값: 판정기 호출 보류·나머지 루프 계속).
4. **판정기 유지 여부**는 사용자 결정 사항이다. 사용자 답변 전 기본값: 현재 판정기 유지(처치 제공자와 독립이라는 설계 근거 때문). 단, 새 판정 블록을 열기 전에 예상 호출 수와 USD를 status.md에 먼저 적는다. 대안(anthropic 계열로 전환 시 처치 제공자와 겹침, OpenRouter 잔액 소진)을 한 줄로 비교해 둔다.

## 4. 기타

- Q-0007(116 에피소드 완료율 블록)은 계속 기본값 (b)로 둔다. 사용자 답변이 오면 supervisor가 전달한다.
- status.md의 `model:` 줄이 `openai-codex/gpt-5.6-sol`로 남아 있다. 실제 세션 모델은 `anthropic/claude-opus-5`다. 다음 갱신 때 고친다(모델 변경 아님, 표기 정정).
- 사이클 순서: form workstream(그림 9종 gpt-image-2 재생성 → 라벨 수령 receipt → 보충 양식) → HF 비용 소급 → 그 다음 연구 증분.

## 5. 사용자 위임 사항 (원문)

"ai 에이전트가 스스로 연구를 설계하고, 연구 가설이나 조건, 방법 등 모든 요소를 직접 설정해야 하고, 근데 이걸 또 그냥 정하는게 아니야 깊이 있는 추론과 인사이트를 통해 선택을 해야하고, 그 선택에 대해 근거까지 있어야 해. 비슷한 실험찾아보고, method 찾아보고, 쓸만한 레퍼런스 찾아보고, 자료정리도 해야해 또한 이모든 걸 다른 ai 에이전트들도 인지하고 작업할수 있게 context graph로 스스로 작성하서 그래프 맵을 구축해야 해. 관련 선행 연구를 찾아서 그 근거를 바탕으로 하나의 온전한 실험 설계안으로 정리 구축하고 실험을 진행하는거야. 비슷한 연구들이 어떤식으로 실험을 설계했는지 비교 경쟁하여 추론하고 인사이트를 확보하며 자율 연구를 진행하는거야."

2026-09-03 05:08 KST: "gpt-image-2 API 키는 이걸로 등록해, Q-0006 교정 라벨 25건 니가 직접진행해 승인할게"

## 6. 불변 조건

- 키 값은 어떤 파일·로그·커밋·출력에도 나타나지 않는다. 키 파일을 워크트리로 복사하지 않는다.
- `label-key.json`은 supervisor에게 보내지 않는다. 보충 양식에도 verdict·confidence를 넣지 않는다.
- 논문 명칭 규칙(해커톤 회사·도메인, 엔진 제품명, 이미지 생성 벤더명 금지) 유지.
- AGENTS.md 규칙(`git add -A`·`.` 금지, reset --hard·stash·force push·amend 금지, `npm run` 금지) 유지. 세션 모델 변경 금지.
- 답변된 orx ancestor 편집 금지. DeepVoice 증거는 이 논문에 쓰지 않는다.

## 7. 보고

status.md 첫 줄에 (1) 그림 9종의 route 현황, (2) 라벨 수령 receipt 경로와 2차 일치도 판정, (3) HF 누적 USD를 적는다. 보충 양식이 준비되면 questions.md Q-0006에 `supplement_ready` 줄로 알린다. 다음 supervisor 점검은 45분 정책에 따른다.
