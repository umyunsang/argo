# Exa 검색 복구 — 2026-09-08

공식 로컬 Exa MCP 3.4.1과 사용자가 제공한 API 키로 검색·원문 읽기를 복구했다. 처음의 공개 hosted MCP 403은 초기화 이전 Cloudflare 접속 차단이었다. 해당 서버의 차단 설정을 변경하거나 해제했다고 주장하지 않는다.

## 적용

- 프로젝트 설정: `.codex/config.toml`, Exa만 enabled.
- 실행기: `/Users/um-yunsang/.local/bin/codex-exa-mcp`.
- 공식 패키지: `/Users/um-yunsang/.local/share/codex-exa-mcp/3.4.1`.
- 키: macOS Keychain의 `codex.exa.api-key` / `exa`. 실행 시 메모리에서만 읽는다. 저장소·설정·명령 인자에 키 없음.
- 현재 전역 MCP/plugin/skill/hook 설정은 byte 단위 그대로다.

## 실제 검증

1. 인증 API search HTTP200, 실제 학술 결과 3개.
2. 공식 MCP initialize, tools/list, web_search_exa 성공.
3. codex mcp get exa --json이 project config를 실제 인식.
4. 위 등록된 실행 경로로 web_fetch_exa 성공.
5. 패키지 audit 취약점0, launcher sh syntax 정상, 비밀값 파일 유출0.

현재 열려 있는 대화에는 MCP 도구가 동적으로 추가되지 않는다. 새 Codex 세션에서 프로젝트 설정을 읽으면 검색·읽기 도구가 로드된다. 이 세션에서도 검증된 stdio 경로로 Exa를 호출할 수 있다.

공식 설치 경로: https://exa.ai/docs/reference/exa-mcp (local npm + API key). 증거: FINAL_RECEIPT.json, mcp-receipt.json, configured-fetch-receipt.json. 과거 연구 회차의 403 영수증은 당시 관측으로 보존한다.
