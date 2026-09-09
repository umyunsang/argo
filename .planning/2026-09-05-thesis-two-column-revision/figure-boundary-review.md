# Figure publication-boundary review

- 완료 시각: `2026-09-05T11:15:02+09:00`
- 판정: **PASS — 새 SVG 3개의 텍스트 계약·XML·원본 해시·실측 수치·변경 문구 폭 검증에 한정.**
- 1단 편집·QMD·Typst·PDF·패키징은 root 소유이며 이 작업의 수정·검증 범위가 아니다.
- 원본 SVG 3개를 이번 작업에서 완독했다. `template-20260905`와 이전 `two-column-compact-20260905` 복사본은 수정하지 않았다.
- 최신 명시 제목 `Measurement checks`가 이전 `Stage-0 evaluation paths` 권고를 대체한다.
- 현재 사용자 지시와 실제 SVG를 직접 근거로 사용했다. 과거 메모리는 탐색 힌트일 뿐 현재 과학적 주장이나 출판 승인 근거로 사용하지 않았다.

## 이 작업의 완료 상태

| 단계 | 상태 |
|---|---|
| 원본 완독 및 변경 경계 확인 | completed |
| 새 복사본의 최소 텍스트 교체 | completed |
| 원본 해시·XML·수치·텍스트 폭 검증 | completed |
| 모든 치환과 근거 기록 후 중단 | completed |

공유 계획 파일은 수정하지 않았다. 이 검토서와 짝이 되는 JSON만 이 작업의 결과·진행·검증 기록이다.

## 생성 파일과 해시

| 새 SVG | 원본 SHA-256: 전후 동일 | 새 SVG SHA-256 | 치환 수 |
|---|---|---|---|
| `paper/figures/thesis-boundary-20260905/fig1-research-agent-architecture.svg` | `a5b6490ff6a156bf85da915896b97ce202824f6d518a5e9c9358ca90e67d6f2d` | `bfd3e705abb2a3491d4d1006019b9b8c98603e8657ee12a3f364b082707b4084` | 9 |
| `paper/figures/thesis-boundary-20260905/fig2-stage0-measurement-isolation.svg` | `56709ba4633669c8c239fc8761ffa5a7b22cce535686385e28489744698182fd` | `2c3ab9ab8de55e605c07fb37f041579607c82a6a6846ef5246e768742eaee6ac` | 2 |
| `paper/figures/thesis-boundary-20260905/fig3-evidence-dependency-contract.svg` | `4cdda40253c9e5b46baf96cab26da7205f8f34cb4f815622ffbc1f5c8d97047d` | `905627af37615b807496a67f7a0751dc2d5e79dbc5c562b3d1d1f0e00f5918a8` | 4 |

합계: SVG 3개, 텍스트 노드 치환 15회. 추가 기록은 `.planning/2026-09-05-thesis-two-column-revision/figure-boundary-review.md`와 `.planning/2026-09-05-thesis-two-column-revision/figure-boundary-checks.json` 두 파일뿐이다.

## 모든 치환과 변경 근거

### `fig-architecture` — Proposed agent architecture

| 원본 위치/표면 | 이전 텍스트 | 새 텍스트 | 변경 근거 |
|---|---|---|---|
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:2` / `title` | Proposed integrated research-agent architecture | Proposed agent architecture | 접근성 제목을 지정된 간결한 논문 제목으로 맞춘다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:3` / `desc` | Six proposed research stages connected to a typed provenance spine. Research refinement and harness refinement have separate lineages. The persistent execution substrate is a proposed architectural layer, not a completed ARGO runtime. | Six conceptual research stages linked by typed evidence records. Research refinement and workflow revision are separate, untested design elements. Execution support is an unvalidated conceptual layer, not an implementation claim. | 제품명과 계승 실행 기반의 설명을 제거한다. 전체를 미검증 개념 설계로 한정하며 구현 완료나 향후 제품 개발을 주장하지 않는다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:18` / `text` | Proposed research-agent architecture | Proposed agent architecture | 보이는 제목을 지정된 간결한 제목으로 바꾼다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:19` / `text` | Conceptual design; integrated efficacy not yet evaluated | Proposed, untested design; no efficacy evidence | 제안 전체의 미실증 상태와 효능 근거 부재를 동시에 명시한다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:68` / `text` | Harness refinement | Workflow revision | 제품 하네스 개선 대신 논문상의 작업 절차 수정이라는 방법 설계 범주로 한정한다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:69` / `text` | Revise tools and instructions | Compare workflow choices | 구현 도구와 지침의 개량 항목을 제거하고 방법상의 절차 선택 비교로 대체한다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:70` / `text` | Separate lineage; held-out validation | Separate, untested design record | 별도 수정 이력은 유지하되 held-out 검증이 완료되었거나 약속되었다는 인상을 제거한다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:72` / `text` | Persistent execution substrate; native implementation remains paused | Execution support (proposed; unvalidated) | 내부 구현 중단 상태와 운영 중인 기반의 암시를 제거하고 미검증 실행 지원 계층으로 바꾼다. |
| `paper/figures/template-20260905/fig1-research-agent-architecture.svg:73` / `text` | Daemon · persistent REPL · recovery · harness refinement · TUI | Conceptual layer; no implementation claim | 구체적인 구현 스택 목록을 통째로 제거한다. 이름만 가린 내부 구현 로드맵을 남기지 않는다. |

### `fig-measurement` — Measurement checks

| 원본 위치/표면 | 이전 텍스트 | 새 텍스트 | 변경 근거 |
|---|---|---|---|
| `paper/figures/template-20260905/fig2-stage0-measurement-isolation.svg:2` / `title` | Stage 0 measurement checks and separate runtime isolation probe | Measurement checks | 접근성 제목을 최신 명시 지시로 맞춘다. Stage 0은 단계 명칭이며 실측값이 아니다. |
| `paper/figures/template-20260905/fig2-stage0-measurement-isolation.svg:17` / `text` | Stage 0: two distinct evidence paths | Measurement checks | 보이는 제목을 최신 명시 지시로 맞춘다. 두 경로의 분리와 실측값은 A/B 패널에 그대로 보존한다. |

### `fig-graph` — Evidence dependency graph

| 원본 위치/표면 | 이전 텍스트 | 새 텍스트 | 변경 근거 |
|---|---|---|---|
| `paper/figures/template-20260905/fig3-evidence-dependency-contract.svg:2` / `title` | Proposed typed evidence dependency and handoff contract | Evidence dependency graph | 접근성 제목을 간결하게 맞춘다. 유형 관계와 인계 명세는 본문 및 제안 표시로 보존한다. |
| `paper/figures/template-20260905/fig3-evidence-dependency-contract.svg:3` / `desc` | Sources with a hash and locator support or contradict claims. Decisions derive from claims, experiments derive from decisions, and artifacts derive from experiments. A source retraction triggers requires_recheck for the affected claim and dependent records; it does not automatically falsify them. Proposed contract for dependency tracking and re-evaluation. | Sources with a hash and locator support or contradict claims. Decisions derive from claims, experiments derive from decisions, and artifacts derive from experiments. A source retraction triggers requires_recheck for the affected claim and dependent records; it does not automatically falsify them. Proposed, untested contract for dependency tracking and re-evaluation. | 관계 방향과 재검토가 자동 거짓 판정이 아니라는 문장을 그대로 유지하며 명세의 미검증 상태만 명시한다. |
| `paper/figures/template-20260905/fig3-evidence-dependency-contract.svg:24` / `text` | Typed evidence dependency graph | Evidence dependency graph | 보이는 제목을 지정된 간결한 제목으로 바꾼다. typed 관계 명칭은 보존한다. |
| `paper/figures/template-20260905/fig3-evidence-dependency-contract.svg:25` / `text` | Proposed contract — dependency tracking and re-evaluation | Proposed, untested dependency and recheck contract | 그림 자체에서 의존성 및 재검토 명세가 제안이자 미검증 설계임을 명시한다. |

## 실측 및 의미 불변 조건

- 측정 그림의 제목·접근성 제목 외 모든 문자열은 바이트 단위로 동일하다. A의 `16 tasks × 6 checks`, `3 valid + 3 corrupt / task`, `96 evaluator executions`, `48 valid / 48 corrupt`, `96 manifests rederived`, `6 mutations detected`, 증거 날짜를 그대로 보존했다.
- A는 채점기 fixture 검사이며 96회 통합 에이전트 실행이 아니다. B는 별도 격리 점검이고 `Probe; no model call`, `fully certified integrated tasks = 0`, `integrated runner uncertified`, `no efficacy result.`를 모두 그대로 보존했다.
- B의 별도 agent/scorer 컨테이너, 읽기 전용 oracle 및 입력, 고정 이미지, 직접 경로·심볼릭 링크·외부 및 루프백 네트워크 점검은 원래 측정 조건이므로 유지했다. 구현 도구의 도입 계획이나 제품 로드맵으로 재서술하지 않았다.
- **숫자 예외는 실측값이 아니라 단계 표기 2개뿐이다.** XML 제목과 보이는 제목의 `Stage 0`이 사용자 지정 `Measurement checks`로 바뀌면서 단계 명칭의 `0` 두 개가 사라졌다. 실측값 `0`을 포함한 모든 실측 수치와 날짜 및 구조의 1–6단계 번호는 바이트 단위로 동일하다.
- 그래프의 `supports`, `contradicts`, `derived_from` 방향, 역방향 의존 경로, 식별자·해시·판본 및 근거 보존은 그대로다. 접근성 설명의 `it does not automatically falsify them.`을 보존하여 재검토 요청을 자동 거짓 판정으로 바꾸지 않았다.
- 구조의 도구 개량·held-out 검증 표현과 구체적 구현 스택을 제거했다. 별도 미검증 방법 설계 기록 및 미검증 실행 지원 계층으로 한정했으며, 제품명만 가린 내부 개발 계획은 남기지 않았다.
- 새 세 SVG의 title/desc/visible text에서 제품·내부 상태·구현 스택 금칙어 검색 결과는 0건이다. 금칙어 정규식과 각 수치 포함 텍스트의 일치 기록은 JSON에 있다.

## 검증 범위와 텍스트 폭

- `xml.etree.ElementTree`로 원본/복사본을 파싱하고 SVG namespace와 루트를 확인했다. `/usr/bin/xmllint --nonet --noout`도 원본 3개 및 새 복사본 3개 모두 종료 코드 0, stderr 없음이다. XML well-formedness 확인이며 별도 SVG 스키마 적합성 인증은 아니다.
- 모든 element tag/attribute/tail, CSS, geometry, typography 및 변경 허용 텍스트 외 바이트를 보존했다. 역치환하면 원본 바이트가 정확히 복원되며 파일별 원본 SHA-256 전후가 일치한다.
- 아래 폭은 로컬 CoreText의 Arial/Arial Bold 및 기존 SVG font-size로 계산한 typographic advance이다. 변경 문구 전부가 원문보다 넓지 않고 기존 공간 안에 들어간다. 이미지 생성·네트워크 조회·PDF 렌더링은 실행하지 않았다.

| 그림/원본 줄 | 새 문구 | 이전 폭 | 새 폭 | 가용 폭 |
|---|---|---|---|---|
| `fig-architecture:18` | Proposed agent architecture | 397.364 | 298.3 | 940.0 |
| `fig-architecture:19` | Proposed, untested design; no efficacy evidence | 496.631 | 429.922 | 940.0 |
| `fig-architecture:68` | Workflow revision | 205.412 | 189.073 | 420.0 |
| `fig-architecture:69` | Compare workflow choices | 254.57 | 238.975 | 420.0 |
| `fig-architecture:70` | Separate, untested design record | 324.678 | 295.752 | 420.0 |
| `fig-architecture:72` | Execution support (proposed; unvalidated) | 621.445 | 375.791 | 922.0 |
| `fig-architecture:73` | Conceptual layer; no implementation claim | 570.205 | 376.855 | 922.0 |
| `fig-measurement:17` | Measurement checks | 378.974 | 222.557 | 940.0 |
| `fig-graph:24` | Evidence dependency graph | 365.138 | 298.311 | 940.0 |
| `fig-graph:25` | Proposed, untested dependency and recheck contract | 538.105 | 479.209 | 940.0 |

## 한계와 인계

- 이 작업은 원래 수치·과학적 주장을 재실험하거나 독립 재인증하지 않았다. A/B 계측 결과를 에이전트 효능·독창성·SOTA 결과로 승격하지 않았다.
- 최종 1단 PDF의 배치·폰트 대체·캡션 연결·전체 페이지 시각 검수는 이 작업에서 수행하지 않았다. root가 QMD를 통합하기 전까지 이 SVG는 최종 논문 승인본이 아니다.
- 초기 읽기 명령의 `git` 조회 1회는 zsh 변수 `path`가 PATH를 가려 실패했다. `/usr/bin/git`로 동일 범위만 재조회하여 해결했으며 어떤 설정 파일도 수정하지 않았다.
- QMD/Typst/원본 SVG/공유 계획/런타임/연구 원장 수정, 네트워크·원격 작업·이미지 생성·커밋·중첩 에이전트 실행은 하지 않았다.
- 지정한 5개 파일을 생성하고 검증한 뒤 **STOP**.
